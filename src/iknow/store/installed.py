"""Install and manage globally installed wikis.

Seam: ``install_draft()`` copies a compiled draft wiki into the installed
wiki store (default ``~/.iknow/installed/<wiki-id>/``).  The store path is
overridable via env var or direct argument injection.

The installed store is the bridge between source-local drafts (under
``.kungfu/drafts/``) and the agent-available global registry.  No network,
auth, or hosted backend access is required — all operations are local
filesystem copy via stdlib ``shutil``.
"""

from __future__ import annotations

import json
import os
import shutil
from dataclasses import dataclass, field
from typing import Any, List

from iknow.store.paths import (
    get_installed_store_path,
    installed_wiki_path,
    is_valid_draft,
)


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------


@dataclass
class InstallResult:
    """Outcome of an install operation."""

    success: bool
    wiki_id: str
    installed_path: str
    errors: List[str] = field(default_factory=list)


@dataclass
class InstalledWiki:
    """Metadata about a wiki that has been installed in the store."""

    wiki_id: str
    name: str
    description: str
    version: str
    installed_at: str  # filesystem path
    has_raw: bool = False
    total_documents: int = 0

    @classmethod
    def from_store_dir(cls, wiki_dir: str) -> "InstalledWiki | None":
        """Load metadata from an installed wiki directory.

        Reads ``kb.json`` to populate the record.  Returns ``None`` if the
        directory doesn't look like a valid installed wiki.
        """
        kb_path = os.path.join(wiki_dir, "kb.json")
        if not os.path.isfile(kb_path):
            return None

        try:
            with open(kb_path, "r", encoding="utf-8") as f:
                kb = json.load(f)
        except (OSError, json.JSONDecodeError):
            return None

        wiki_id = kb.get("wiki_id", os.path.basename(wiki_dir))
        raw_dir = os.path.join(wiki_dir, "raw")

        return cls(
            wiki_id=wiki_id,
            name=kb.get("name", kb.get("wiki_name", "")),
            description=kb.get("description", ""),
            version=kb.get("version", ""),
            installed_at=wiki_dir,
            has_raw=os.path.isdir(raw_dir),
            total_documents=kb.get("total_documents", 0),
        )


# ---------------------------------------------------------------------------
# Install
# ---------------------------------------------------------------------------


def install_draft(
    draft_dir: str,
    wiki_id: str | None = None,
    store_path: str | None = None,
) -> InstallResult:
    """Install a compiled draft wiki into the global installed wiki store.

    Parameters
    ----------
    draft_dir:
        Path to the compiled draft directory (e.g.
        ``.kungfu/drafts/<wiki-id>/``).
    wiki_id:
        Identifier for the wiki.  Defaults to the basename of *draft_dir* or
        the value from ``kb.json``.
    store_path:
        Override the installed store root.  Defaults to
        ``get_installed_store_path()``.

    Returns
    -------
    InstallResult
        Outcome with ``success`` flag, ``wiki_id``, ``installed_path``, and
        any ``errors``.
    """
    # Validate the draft directory
    valid, issues = is_valid_draft(draft_dir)
    if not valid:
        return InstallResult(
            success=False,
            wiki_id=wiki_id or os.path.basename(draft_dir),
            installed_path="",
            errors=issues,
        )

    # Determine the wiki ID (guaranteed non-None after this block)
    resolved_id: str
    if wiki_id is not None:
        resolved_id = wiki_id
    else:
        # Try to read from kb.json
        kb_path = os.path.join(draft_dir, "kb.json")
        try:
            with open(kb_path, "r", encoding="utf-8") as f:
                kb = json.load(f)
            resolved_id = kb.get("wiki_id") or os.path.basename(draft_dir)
        except (OSError, json.JSONDecodeError):
            resolved_id = os.path.basename(draft_dir)

    # Resolve the install destination
    dest = installed_wiki_path(resolved_id, store_path)

    # Remove existing installation if present (clean install)
    if os.path.isdir(dest):
        try:
            shutil.rmtree(dest)
        except OSError as exc:
            return InstallResult(
                success=False,
                wiki_id=resolved_id,
                installed_path=dest,
                errors=[f"Failed to remove existing installation: {exc}"],
            )

    # Copy the entire draft directory to the installed store
    try:
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        shutil.copytree(draft_dir, dest, symlinks=False)
    except OSError as exc:
        return InstallResult(
            success=False,
            wiki_id=resolved_id,
            installed_path=dest,
            errors=[f"Failed to install wiki: {exc}"],
        )

    # Patch kb.json so its wiki_id matches the install target (if different
    # from the draft's original).  The directory name IS the canonical
    # installed wiki_id.
    kb_path = os.path.join(dest, "kb.json")
    try:
        with open(kb_path, "r", encoding="utf-8") as f:
            kb = json.load(f)
        if kb.get("wiki_id") != resolved_id:
            kb["wiki_id"] = resolved_id
            with open(kb_path, "w", encoding="utf-8") as f:
                json.dump(kb, f, indent=2, ensure_ascii=False)
    except (OSError, json.JSONDecodeError):
        pass  # Non-fatal — kb.json already validated during is_valid_draft

    return InstallResult(
        success=True,
        wiki_id=resolved_id,
        installed_path=dest,
    )


# ---------------------------------------------------------------------------
# Query
# ---------------------------------------------------------------------------


def list_installed(
    store_path: str | None = None,
) -> List[InstalledWiki]:
    """List all wikis currently installed in the store.

    Parameters
    ----------
    store_path:
        Override the store root.  Defaults to ``get_installed_store_path()``.

    Returns
    -------
    List[InstalledWiki]
        Sorted list of installed wiki metadata records.
    """
    if store_path is None:
        store_path = get_installed_store_path()

    if not os.path.isdir(store_path):
        return []

    wikis: List[InstalledWiki] = []
    for entry in sorted(os.listdir(store_path)):
        wiki_dir = os.path.join(store_path, entry)
        if not os.path.isdir(wiki_dir):
            continue
        meta = InstalledWiki.from_store_dir(wiki_dir)
        if meta is not None:
            wikis.append(meta)

    return wikis


def get_installed(
    wiki_id: str,
    store_path: str | None = None,
) -> InstalledWiki | None:
    """Get metadata for a single installed wiki.

    Parameters
    ----------
    wiki_id:
        Wiki identifier (directory name within the store).
    store_path:
        Override the store root.  Defaults to ``get_installed_store_path()``.

    Returns
    -------
    InstalledWiki | None
        Metadata record, or ``None`` if not found.
    """
    dest = installed_wiki_path(wiki_id, store_path)
    if not os.path.isdir(dest):
        return None
    return InstalledWiki.from_store_dir(dest)


# ---------------------------------------------------------------------------
# Removal
# ---------------------------------------------------------------------------


def remove_installed(
    wiki_id: str,
    store_path: str | None = None,
) -> bool:
    """Remove an installed wiki from the store.

    Parameters
    ----------
    wiki_id:
        Wiki identifier to remove.
    store_path:
        Override the store root.  Defaults to ``get_installed_store_path()``.

    Returns
    -------
    bool
        ``True`` if successfully removed; ``False`` if not found or on error.
    """
    dest = installed_wiki_path(wiki_id, store_path)
    if not os.path.isdir(dest):
        return False
    try:
        shutil.rmtree(dest)
        return True
    except OSError:
        return False


# ---------------------------------------------------------------------------
# CLI helper
# ---------------------------------------------------------------------------


def summarize(installed: InstalledWiki) -> str:
    """Return a human-readable summary line for an installed wiki."""
    return (
        f"{installed.wiki_id:24s}  {installed.name:30s}  "
        f"v{installed.version:8s}  {installed.total_documents} docs"
    )