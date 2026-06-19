"""Path resolution for the Installed Wiki Store.

Seam: resolves the global installed-wiki directory from well-known locations
with support for env/config overrides so tests never write to a real home
directory.

Canonical paths
---------------
- Default store: ``~/.iknow/installed/``
- Installed wiki: ``<store-path>/<wiki-id>/``
- Override via: ``IKNOW_INSTALLED_STORE`` environment variable or direct
  argument injection.
"""

from __future__ import annotations

import os

# ---------------------------------------------------------------------------
# Default path constants
# ---------------------------------------------------------------------------

DEFAULT_STORE_DIRNAME = "installed"
IKNOW_HOME_DIRNAME = ".iknow"
ENV_STORE_OVERRIDE = "IKNOW_INSTALLED_STORE"
REQUIRED_DRAFT_ARTIFACTS = (
    "kb.json",
    "index.json",
    "llms.txt",
    "sources.json",
    "warnings.json",
    "review.md",
)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def get_installed_store_path(override: str | None = None) -> str:
    """Return the absolute path to the installed wiki store.

    Resolution order:
    1. ``override`` argument (if provided).
    2. ``IKNOW_INSTALLED_STORE`` environment variable (if set).
    3. ``~/.iknow/installed/`` (default).

    Returns an absolute, normalised path.
    """
    raw = override or os.environ.get(ENV_STORE_OVERRIDE)
    if raw:
        return os.path.abspath(raw)

    home = os.path.expanduser("~")
    return os.path.join(home, IKNOW_HOME_DIRNAME, DEFAULT_STORE_DIRNAME)


def installed_wiki_path(wiki_id: str, store_path: str | None = None) -> str:
    """Return the path for an installed wiki within the store.

    Parameters
    ----------
    wiki_id:
        Unique identifier for the wiki.
    store_path:
        Store root. Defaults to ``get_installed_store_path()``.

    Returns
    -------
    str
        Absolute path to ``<store_path>/<wiki_id>/``.
    """
    if store_path is None:
        store_path = get_installed_store_path()
    return os.path.join(store_path, wiki_id)


def is_valid_draft(draft_dir: str) -> tuple[bool, list[str]]:
    """Check whether *draft_dir* contains a valid compiled draft wiki.

    A valid draft must have all required artifacts present as files (not
    directories).

    Parameters
    ----------
    draft_dir:
        Path to the draft wiki directory (e.g. ``.kungfu/drafts/<wiki-id>/``).

    Returns
    -------
    (bool, list[str])
        ``(True, [])`` if valid; ``(False, reasons)`` otherwise with a list
        of human-readable issues.
    """
    issues: list[str] = []

    if not os.path.isdir(draft_dir):
        issues.append(f"Draft directory does not exist: {draft_dir}")
        return False, issues

    for artifact in REQUIRED_DRAFT_ARTIFACTS:
        path = os.path.join(draft_dir, artifact)
        if not os.path.isfile(path):
            issues.append(f"Missing required artifact: {artifact}")

    raw_dir = os.path.join(draft_dir, "raw")
    if not os.path.isdir(raw_dir):
        issues.append("Missing required directory: raw/")

    return (len(issues) == 0, issues)


def get_known_artifacts() -> tuple[str, ...]:
    """Return the tuple of required artifact filenames.

    Useful for test assertions and documentation.
    """
    return REQUIRED_DRAFT_ARTIFACTS