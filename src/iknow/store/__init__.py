"""Installed Wiki Store module.

Seam: register installed wikis so they become agent-available. Separates
draft wiki state from globally installed state.

v1 adapter: local filesystem (``~/.iknow/``). No hosted registry backend.
"""

from iknow.store.installed import (
    InstallResult,
    InstalledWiki,
    get_installed,
    install_draft,
    list_installed,
    remove_installed,
    summarize,
)
from iknow.store.paths import (
    get_installed_store_path,
    installed_wiki_path,
    is_valid_draft,
    get_known_artifacts,
)

__all__ = [
    "InstallResult",
    "InstalledWiki",
    "get_installed",
    "get_installed_store_path",
    "get_known_artifacts",
    "install_draft",
    "installed_wiki_path",
    "is_valid_draft",
    "list_installed",
    "remove_installed",
    "summarize",
]
