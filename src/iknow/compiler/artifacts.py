"""Artifact writer for the Draft Wiki Compiler.

Writes compiled draft artifacts to ``./.kungfu/drafts/<wiki-id>/``.

Expected artifacts:
- ``kb.json``          — Knowledge base metadata (Wiki Contract view)
- ``index.json``       — Table of contents / document index
- ``llms.txt``          — LLM-friendly file listing
- ``sources.json``     — Source manifest (included + excluded + provenance)
- ``warnings.json``    — Compilation warnings
- ``review.md``        — Human-readable review notes
- ``raw/``             — Raw Markdown files mirrored from sources
"""

from __future__ import annotations

import json
import os
import shutil
from typing import Any, Dict, List

from iknow.compiler.manifest import SourceManifest


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def write_artifacts(
    manifest: SourceManifest,
    draft_dir: str,
) -> List[str]:
    """Write all draft artifacts under *draft_dir*.

    Parameters
    ----------
    manifest:
        Source manifest produced by ``build_manifest()``.
    draft_dir:
        Output directory path (e.g. ``.kungfu/drafts/<wiki-id>/``).

    Returns
    -------
    List[str]
        Relative paths of all written files (for verification / reporting).
    """
    written: List[str] = []

    # Ensure output directory exists
    os.makedirs(draft_dir, exist_ok=True)

    # Gather document metadata from included files
    docs = _build_document_list(manifest)

    # 1. kb.json — knowledge base metadata
    kb = _build_kb_json(manifest)
    written.append(_write_json(draft_dir, "kb.json", kb))

    # 2. index.json — document index
    index = _build_index_json(manifest, docs)
    written.append(_write_json(draft_dir, "index.json", index))

    # 3. sources.json — full manifest with provenance. This is written before
    # llms.txt so the routing summary is derived after source review data exists.
    sources = _build_sources_json(manifest)
    written.append(_write_json(draft_dir, "sources.json", sources))

    # 4. llms.txt — plain-text file listing for LLM consumption
    written.append(_write_text(draft_dir, "llms.txt", _build_llms_txt(manifest, docs)))

    # 5. warnings.json — compilation warnings
    warnings_data = _build_warnings_json(manifest, docs)
    written.append(_write_json(draft_dir, "warnings.json", warnings_data))

    # 6. review.md — human-readable review notes
    written.append(_write_text(draft_dir, "review.md", _build_review_md(manifest, docs)))

    # 7. raw/ — mirror of included Markdown sources
    raw_dir = os.path.join(draft_dir, "raw")
    written.extend(_mirror_sources(manifest, raw_dir))

    return written


# ---------------------------------------------------------------------------
# Artifact builders
# ---------------------------------------------------------------------------


def _build_document_list(manifest: SourceManifest) -> List[Dict[str, Any]]:
    """Build a simple document list from included files."""
    docs: List[Dict[str, str]] = []
    for entry in manifest.included:
        # Read first line as title hint
        title = _guess_title(entry.abspath) or _stem_title(entry.relpath)
        docs.append(
            {
                "path": entry.relpath,
                "title": title,
                "size_bytes": _file_size(entry.abspath),
            }
        )
    return docs


def _build_kb_json(manifest: SourceManifest) -> Dict[str, Any]:
    """Knowledge base metadata JSON."""
    return {
        "wiki_id": manifest.wiki_id,
        "name": manifest.wiki_name,
        "description": manifest.description,
        "version": manifest.version,
        "scope": manifest.scope,
        "non_scope": manifest.non_scope,
        "license": manifest.license,
        "maintainer": manifest.maintainer,
        "provenance": manifest.provenance,
        "freshness": manifest.freshness,
        "trust_state": manifest.trust_state,
        "publication": manifest.publication,
        "entry_points": manifest.entry_points,
        "total_documents": len(manifest.included),
        "total_excluded": len(manifest.excluded),
        "metadata_warnings": manifest.metadata_warnings,
    }


def _build_index_json(
    manifest: SourceManifest, docs: List[Dict[str, str]]
) -> Dict[str, Any]:
    """Document index JSON (table of contents)."""
    return {
        "wiki_id": manifest.wiki_id,
        "wiki_name": manifest.wiki_name,
        "total_documents": len(docs),
        "documents": docs,
    }


def _build_llms_txt(
    manifest: SourceManifest, docs: List[Dict[str, str]]
) -> str:
    """LLM-friendly plaintext file listing."""
    lines: List[str] = [
        f"# {manifest.wiki_name}",
        f"Wiki ID: {manifest.wiki_id}",
        f"Total documents: {len(docs)}",
        "",
        "## Documents",
        "",
    ]
    for doc in docs:
        lines.append(f"- {doc['title']} ({doc['path']})")
    lines.append("")
    return "\n".join(lines)


def _build_sources_json(manifest: SourceManifest) -> Dict[str, Any]:
    """Full source manifest with provenance."""
    return {
        "wiki_id": manifest.wiki_id,
        "wiki_name": manifest.wiki_name,
        "base_dir": manifest.base_dir,
        "metadata_provenance": {
            "source": "iknow.yaml",
            "warnings": manifest.metadata_warnings,
        },
        "included": [
            {
                "relpath": e.relpath,
                "abspath": e.abspath,
                "reason": e.reason or "matched include patterns",
            }
            for e in manifest.included
        ],
        "excluded": [
            {
                "relpath": e.relpath,
                "abspath": e.abspath,
                "reason": e.reason,
            }
            for e in manifest.excluded
        ],
    }


def _build_warnings_json(
    manifest: SourceManifest, docs: List[Dict[str, str]]
) -> Dict[str, Any]:
    """Compilation warnings."""
    warnings: List[str] = list(manifest.metadata_warnings)
    if not docs:
        warnings.append("No documents were included in the compilation")
    return {
        "wiki_id": manifest.wiki_id,
        "wiki_name": manifest.wiki_name,
        "total_warnings": len(warnings),
        "warnings": warnings,
    }


def _build_review_md(
    manifest: SourceManifest, docs: List[Dict[str, str]]
) -> str:
    """Human-readable review notes."""
    lines: List[str] = [
        f"# Review: {manifest.wiki_name}",
        f"**Wiki ID:** {manifest.wiki_id}",
        f"**Base directory:** `{manifest.base_dir}`",
        "",
        "## Summary",
        "",
        f"- **Included documents:** {len(manifest.included)}",
        f"- **Excluded files:** {len(manifest.excluded)}",
        f"- **Total considered:** {manifest.total_files}",
        "",
    ]

    if manifest.metadata_warnings:
        lines.extend(
            [
                "## Metadata Warnings",
                "",
            ]
            + [f"- ⚠️  {w}" for w in manifest.metadata_warnings]
            + [""]
        )

    if docs:
        lines.extend(
            [
                "## Included Documents",
                "",
            ]
            + [f"- [{d['title']}](raw/{d['path']}) — `{d['path']}`" for d in docs]
            + [""]
        )

    if manifest.excluded:
        lines.extend(
            [
                "## Excluded Files",
                "",
            ]
            + [f"- `{e.relpath}` — {e.reason}" for e in manifest.excluded]
            + [""]
        )

    lines.append("---\n*Generated by I-know-kungfu Draft Wiki Compiler*\n")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _write_json(base_dir: str, filename: str, data: Any) -> str:
    """Write *data* as pretty-printed JSON under *base_dir*."""
    path = os.path.join(base_dir, filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    return filename


def _write_text(base_dir: str, filename: str, text: str) -> str:
    """Write plain text under *base_dir*."""
    path = os.path.join(base_dir, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    return filename


def _mirror_sources(manifest: SourceManifest, raw_dir: str) -> List[str]:
    """Copy included Markdown files into *raw_dir*, preserving directory structure.

    Returns relative paths of written files.
    """
    written: List[str] = []
    for entry in manifest.included:
        dest = os.path.join(raw_dir, entry.relpath)
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        try:
            shutil.copy2(entry.abspath, dest)
            written.append(os.path.join("raw", entry.relpath))
        except OSError:
            pass  # Skip files we can't copy
    return written


def _guess_title(abspath: str) -> str:
    """Try to extract a title from the first ``# `` heading in a Markdown file."""
    try:
        with open(abspath, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith("# ") and not line.startswith("##"):
                    return line[2:].strip()
    except (OSError, UnicodeDecodeError):
        pass
    return ""


def _stem_title(relpath: str) -> str:
    """Derive a title from the filename stem."""
    base = os.path.basename(relpath)
    name, _ = os.path.splitext(base)
    # Replace hyphens/underscores with spaces and title-case
    return name.replace("-", " ").replace("_", " ").strip().title()


def _file_size(abspath: str) -> int:
    """Return file size in bytes (0 on error)."""
    try:
        return os.path.getsize(abspath)
    except OSError:
        return 0