"""Cookbook Registry interface.

Defines the protocol (duck-typed interface) for a cookbook registry
that lists available knowledge base wikis and fetches their full Wiki Contracts.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Protocol

from iknow.contracts.model import TrustState, WikiContract


@dataclass
class RegistryItem:
    """Lightweight listing metadata for a wiki in the registry.

    This is what callers receive when listing all wikis — enough to
    power a table/list-first UI or CLI without loading every contract.
    """

    id: str
    """Unique registry identifier for this wiki."""

    name: str
    """Human-readable wiki name."""

    description: str
    """Short description of what the wiki covers."""

    trust_state: TrustState
    """Trust ladder status (Community, Verified, Official)."""

    version: str
    """Semantic version string from the Wiki Contract."""


class CookbookRegistry(Protocol):
    """Duck-typed interface for a cookbook registry.

    Any concrete implementation — static, hosted, cached — must satisfy
    this protocol to be a valid registry adapter.
    """

    def list_wikis(self) -> List[RegistryItem]:
        """Return lightweight listing metadata for all wikis in the registry.

        This is the primary discovery path; callers use it to build
        browse/search/filter views.
        """
        ...

    def get_wiki(self, wiki_id: str) -> WikiContract:
        """Fetch the full Wiki Contract for a single wiki by its registry ID.

        Parameters
        ----------
        wiki_id:
            The registry ID of the wiki to fetch (e.g. ``"agent_workflow_setup"``).

        Returns
        -------
        WikiContract
            The fully validated contract for the requested wiki.

        Raises
        ------
        KeyError
            If ``wiki_id`` does not match any wiki in the registry.
        """
        ...