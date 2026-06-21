"""Data models for the Local Knowledge Inventory.

A Local Knowledge Inventory describes what the user already knows locally —
what topics are covered, how they're served, and the trust posture of
the local knowledge base.  It is the "what do I already have?" counterpart
to a Wiki Contract's "what does this wiki offer?".
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from iknow.contracts.model import ServingEntryPoint, TrustState


@dataclass
class InventoryItem:
    """A single entry in the local knowledge inventory.

    Each item represents one area of knowledge the user has already
    installed or curated locally.
    """

    id: str
    """Unique identifier for this inventory item."""

    name: str
    """Human-readable name for this knowledge area."""

    description: str
    """Short description of what this area covers."""

    scope: List[str]
    """Specific topics covered within this area."""

    non_scope: List[str]
    """Adjacent topics explicitly out of scope."""

    entry_points: List[ServingEntryPoint]
    """How this area is served locally (MCP, markdown, etc.)."""

    trust_state: TrustState
    """Trust posture of the local knowledge for this area."""

    evidence_sources: Dict[str, List[str]] = field(default_factory=dict)
    """Optional topic → local source paths evidence map.

    Adapters such as Graphify can populate this so Context Fit can show why a
    topic was considered local evidence without treating the evidence as trust,
    provenance, freshness, or install authority.
    """


@dataclass
class LocalKnowledgeInventory:
    """The complete local knowledge inventory describing what the user has.

    This is a first-class object that the Context Fit module compares
    against a candidate Wiki Contract to determine overlap, gaps, and
    boundary warnings.

    ``items`` holds multiple knowledge areas; for simple comparisons
    the combined scope/non_scope across all items is used as the
    "known territory".
    """

    name: str
    """Human-readable name for this inventory (e.g. 'My Local KB')."""

    description: str
    """High-level description of the local knowledge base."""

    items: List[InventoryItem] = field(default_factory=list)

    # ------------------------------------------------------------------
    # Convenience accessors
    # ------------------------------------------------------------------

    @property
    def combined_scope(self) -> List[str]:
        """All scope items across all inventory entries, deduplicated."""
        seen: set[str] = set()
        result: list[str] = []
        for item in self.items:
            for s in item.scope:
                if s not in seen:
                    seen.add(s)
                    result.append(s)
        return result

    @property
    def combined_non_scope(self) -> List[str]:
        """All non-scope items across all inventory entries, deduplicated."""
        seen: set[str] = set()
        result: list[str] = []
        for item in self.items:
            for ns in item.non_scope:
                if ns not in seen:
                    seen.add(ns)
                    result.append(ns)
        return result