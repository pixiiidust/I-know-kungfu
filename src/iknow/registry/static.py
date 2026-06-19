"""Static Cookbook Registry adapter.

Loads a fixed set of Wiki Contracts from JSON fixture files bundled
with the package.  No backend, no network, no database — pure Ponytail
local/static operation.

Prototype wikis registered here:
  - Agent Workflow Setup Wiki  (Verified)
  - Terminal Setup Wiki        (Official)
  - MCP Basics Wiki            (Community)
"""

from __future__ import annotations

import json
import os
from typing import List, Tuple

from iknow.contracts.loader import load_from_dict
from iknow.contracts.model import WikiContract

from iknow.registry.interface import CookbookRegistry, RegistryItem

# ---------------------------------------------------------------------------
# Internal registry data: list of (id, filename) pairs
# ---------------------------------------------------------------------------
_FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures")

_REGISTRY: List[Tuple[str, str]] = [
    ("agent_workflow_setup", "agent_workflow_setup_wiki.json"),
    ("terminal_setup", "terminal_setup_wiki.json"),
    ("mcp_basics", "mcp_basics_wiki.json"),
]


def _load_fixture(filename: str) -> dict:
    """Read a single JSON fixture file and return the raw dict."""
    path = os.path.join(_FIXTURES_DIR, filename)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _build_registry_items() -> List[Tuple[str, WikiContract]]:
    """Load all fixtures and return a list of (id, WikiContract) pairs."""
    result: List[Tuple[str, WikiContract]] = []
    for wiki_id, filename in _REGISTRY:
        data = _load_fixture(filename)
        contract = load_from_dict(data)
        result.append((wiki_id, contract))
    return result


# ---------------------------------------------------------------------------
# Lazy-loaded cache (loaded once on first access)
# ---------------------------------------------------------------------------
_cache: List[Tuple[str, WikiContract]] | None = None


def _get_cached() -> List[Tuple[str, WikiContract]]:
    global _cache
    if _cache is None:
        _cache = _build_registry_items()
    return _cache


# ---------------------------------------------------------------------------
# Public static registry implementation
# ---------------------------------------------------------------------------

class StaticCookbookRegistry:
    """A static, fixture-backed Cookbook registry.

    Satisfies the ``CookbookRegistry`` protocol.
    """

    def list_wikis(self) -> List[RegistryItem]:
        """Return lightweight listing metadata for all registered wikis."""
        items: List[RegistryItem] = []
        for wiki_id, contract in _get_cached():
            items.append(
                RegistryItem(
                    id=wiki_id,
                    name=contract.name,
                    description=contract.description,
                    trust_state=contract.trust_state,
                    version=contract.version,
                )
            )
        return items

    def get_wiki(self, wiki_id: str) -> WikiContract:
        """Fetch the full Wiki Contract for a wiki by its registry ID.

        Parameters
        ----------
        wiki_id:
            The registry identifier (e.g. ``"agent_workflow_setup"``).

        Returns
        -------
        WikiContract
            The fully validated contract.

        Raises
        ------
        KeyError
            If no wiki with the given ID exists in the registry.
        """
        for wid, contract in _get_cached():
            if wid == wiki_id:
                return contract
        raise KeyError(f"Wiki not found in registry: {wiki_id!r}")


# ---------------------------------------------------------------------------
# Convenience singleton
# ---------------------------------------------------------------------------
registry = StaticCookbookRegistry()