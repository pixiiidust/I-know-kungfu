"""Compilation pipeline for the Draft Wiki Compiler.

Orchestrates:
1. Parse ``iknow.yaml``
2. Build source manifest
3. Write draft artifacts
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import List

from iknow.compiler.config import CompilerConfig, parse_config
from iknow.compiler.manifest import SourceManifest, build_manifest
from iknow.compiler.artifacts import write_artifacts


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------


@dataclass
class CompileResult:
    """Outcome of a draft compilation."""

    success: bool
    wiki_id: str
    draft_dir: str
    manifest: SourceManifest | None = None
    artifacts: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def compile_draft(
    config_path: str,
    base_dir: str | None = None,
    output_dir: str | None = None,
) -> CompileResult:
    """Compile a private draft wiki from ``iknow.yaml`` and Markdown sources.

    Parameters
    ----------
    config_path:
        Path to ``iknow.yaml``.
    base_dir:
        Base directory for resolving relative source paths.
        Defaults to the directory containing ``config_path``.
    output_dir:
        Override output directory.  Defaults to
        ``<base_dir>/.kungfu/drafts/<wiki-id>/``.

    Returns
    -------
    CompileResult
        Outcome — check ``success`` and ``errors``.
    """
    # Resolve base dir
    if base_dir is None:
        base_dir = os.path.dirname(os.path.abspath(config_path))

    base_dir = os.path.abspath(base_dir)

    # 1. Parse config
    config = parse_config(config_path)

    if not config.sources and not config.warnings:
        return CompileResult(
            success=False,
            wiki_id="unknown",
            draft_dir="",
            errors=["Configuration has no sources and no metadata to compile"],
        )

    # 2. Build manifest
    manifest = build_manifest(config, base_dir)

    # 3. Determine draft output directory
    wiki_id = config.wiki_id or "unnamed"
    if output_dir is None:
        draft_dir = os.path.join(base_dir, ".kungfu", "drafts", wiki_id)
    else:
        draft_dir = os.path.abspath(output_dir)

    # 4. Write artifacts
    try:
        artifacts = write_artifacts(manifest, draft_dir)
    except OSError as exc:
        return CompileResult(
            success=False,
            wiki_id=wiki_id,
            draft_dir=draft_dir,
            manifest=manifest,
            errors=[f"Failed to write artifacts: {exc}"],
        )

    # 5. Collect any errors (warnings are non-blocking)
    errors: List[str] = []
    if not manifest.included:
        errors.append("No documents were included — check sources and include/exclude patterns")

    return CompileResult(
        success=not errors,
        wiki_id=wiki_id,
        draft_dir=draft_dir,
        manifest=manifest,
        artifacts=artifacts,
        errors=errors,
    )