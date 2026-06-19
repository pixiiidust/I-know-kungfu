"""Source manifest generation for the Draft Wiki Compiler.

The source manifest is generated *before* ``llms.txt`` routing and records
every file that was considered for inclusion, whether it was included or
excluded, plus metadata provenance notes.

This module uses only the ``os`` and ``pathlib`` modules from the stdlib —
no external dependencies.
"""

from __future__ import annotations

import fnmatch
import os
from dataclasses import dataclass, field
from typing import Dict, List


from iknow.compiler.config import CompilerConfig


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------


@dataclass
class ManifestEntry:
    """A single file entry in the source manifest."""

    relpath: str
    abspath: str
    included: bool
    reason: str = ""  # Why it was included or excluded


@dataclass
class SourceManifest:
    """Complete record of source files considered during compilation."""

    wiki_id: str
    wiki_name: str
    base_dir: str
    description: str = ""
    version: str = ""
    scope: List[str] = field(default_factory=list)
    non_scope: List[str] = field(default_factory=list)
    license: str = ""
    maintainer: str = ""
    provenance: str = ""
    freshness: str = ""
    entry_points: List[str] = field(default_factory=list)
    included: List[ManifestEntry] = field(default_factory=list)
    excluded: List[ManifestEntry] = field(default_factory=list)
    metadata_warnings: List[str] = field(default_factory=list)

    @property
    def total_files(self) -> int:
        return len(self.included) + len(self.excluded)


# ---------------------------------------------------------------------------
# Core logic
# ---------------------------------------------------------------------------


def _should_include(
    relpath: str,
    include_patterns: List[str],
    exclude_patterns: List[str],
) -> tuple[bool, str]:
    """Determine whether *relpath* should be included.

    Returns ``(included, reason)``.
    """
    # Default: exclude if no include patterns match
    matched_include = False
    if not include_patterns:
        matched_include = True  # No patterns means include all
    else:
        for pat in include_patterns:
            if fnmatch.fnmatch(relpath, pat) or fnmatch.fnmatch(
                os.path.basename(relpath), pat
            ):
                matched_include = True
                break

    if not matched_include:
        return False, "Does not match any include pattern"

    # Check exclude patterns
    for pat in exclude_patterns:
        if fnmatch.fnmatch(relpath, pat) or fnmatch.fnmatch(
            os.path.basename(relpath), pat
        ):
            return False, f"Excluded by pattern: {pat}"

    return True, ""


def _find_markdown_files(base_dir: str) -> List[str]:
    """Recursively find all ``.md`` files under *base_dir*.

    Returns relative paths.
    """
    result: List[str] = []
    resolved = os.path.abspath(base_dir)
    if not os.path.isdir(resolved):
        return result

    for root, _dirs, files in os.walk(resolved):
        for fname in files:
            if fname.endswith(".md"):
                abspath = os.path.join(root, fname)
                relpath = os.path.relpath(abspath, resolved)
                result.append(relpath)

    result.sort()
    return result


def build_manifest(
    config: CompilerConfig,
    base_dir: str,
) -> SourceManifest:
    """Build a ``SourceManifest`` from the compiler config.

    Parameters
    ----------
    config:
        Parsed ``iknow.yaml`` configuration.
    base_dir:
        Directory to resolve relative source paths against.

    Returns
    -------
    SourceManifest
        Complete manifest of considered files.
    """
    assert isinstance(config, CompilerConfig)

    manifest = SourceManifest(
        wiki_id=config.wiki_id or "unnamed",
        wiki_name=config.name or "Unnamed Wiki",
        base_dir=os.path.abspath(base_dir),
        description=config.description,
        version=config.version,
        scope=list(config.scope),
        non_scope=list(config.non_scope),
        license=config.license,
        maintainer=config.maintainer,
        provenance=config.provenance,
        freshness=config.freshness,
        entry_points=list(config.entry_points),
        metadata_warnings=list(config.warnings),
    )

    include_patterns = config.include if config.include else ["*.md"]
    exclude_patterns = config.exclude if config.exclude else []

    # Collect files from all source directories
    all_files: Dict[str, str] = {}  # relpath -> abspath
    for src in config.sources:
        src_dir = src
        if not os.path.isabs(src_dir):
            src_dir = os.path.join(base_dir, src_dir)
        files = _find_markdown_files(src_dir)
        for relpath in files:
            abspath = os.path.join(src_dir, relpath)
            # Keep first occurrence if same relpath appears in multiple sources
            if relpath not in all_files:
                all_files[relpath] = abspath

    # Also scan the base directory itself for any markdown files if no
    # explicit sources are configured (fallback).
    if not config.sources:
        files = _find_markdown_files(base_dir)
        for relpath in files:
            abspath = os.path.join(base_dir, relpath)
            if relpath not in all_files:
                all_files[relpath] = abspath

    # Classify each file
    for relpath, abspath in sorted(all_files.items()):
        included, reason = _should_include(relpath, include_patterns, exclude_patterns)
        entry = ManifestEntry(
            relpath=relpath,
            abspath=abspath,
            included=included,
            reason=reason,
        )
        if included:
            manifest.included.append(entry)
        else:
            manifest.excluded.append(entry)

    return manifest