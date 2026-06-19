"""Harmonization decision model — explicit choices for reconciling
a candidate wiki with the local knowledge inventory.

Each decision option records what should happen when a candidate wiki
is accepted into (or rejected from) the local knowledge base.  No
automatic install or trust happens as part of choice creation — these
are *records* of explicit decisions.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import List


class DecisionKind(Enum):
    """Explicit harmonization choice for a candidate wiki."""

    INSTALL = "install"
    """Full install — all content and entry points are added locally."""

    SKIP = "skip"
    """Do nothing — the wiki is not added to the local knowledge base."""

    ROUTE_ONLY = "route-only"
    """Make the wiki findable/routable but do not install its content
    locally.  Agents can access it on-demand but it doesn't consume
    local space or appear in the combined inventory."""

    PREFER_LOCAL = "prefer-local"
    """Install the wiki but when scope conflicts arise, the local
    inventory's version shadows the wiki's version."""

    PREFER_WIKI = "prefer-wiki"
    """Install the wiki and when scope conflicts arise, the wiki's
    version shadows the local inventory's version."""

    KEEP_BOTH_WITH_BOUNDARIES = "keep-both-with-boundaries"
    """Install the wiki with explicit boundary markers so both the
    local and wiki versions coexist, each scoped to their declared
    territory."""


@dataclass
class HarmonizationChoice:
    """A single harmonization decision record.

    Captures what was decided, on what basis, and any supporting
    rationale or side effects.
    """

    candidate_id: str
    """Registry ID of the candidate wiki this decision applies to."""

    decision: DecisionKind
    """The chosen harmonization action."""

    rationale: str = ""
    """Human-readable explanation of why this decision was made."""

    applied_boundaries: List[str] = field(default_factory=list)
    """Specific scope boundary markers when decision is
    ``KEEP_BOTH_WITH_BOUNDARIES``.  Empty for other decisions."""


@dataclass
class HarmonizationResult:
    """The full outcome of a harmonization session.

    Contains the decision that was made, the fit analysis that informed
    it, and the list of available options from which the decision was
    drawn.
    """

    candidate_id: str
    """Registry ID of the candidate wiki."""

    decision: HarmonizationChoice
    """The chosen harmonization action."""

    available_options: List[DecisionKind] = field(default_factory=list)
    """All options that were available when the decision was made."""

    def describe(self) -> str:
        """Return a human-readable summary of this harmonization result.

        Suitable for CLI/UI display.
        """
        lines = [
            f"Candidate:  {self.candidate_id}",
            f"Decision:   {self.decision.decision.value}",
        ]
        if self.decision.rationale:
            lines.append(f"Rationale:  {self.decision.rationale}")
        if self.decision.applied_boundaries:
            lines.append("Boundaries:")
            for b in self.decision.applied_boundaries:
                lines.append(f"  - {b}")
        lines.append(f"Available:  {', '.join(o.value for o in self.available_options)}")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Decision helpers
# ---------------------------------------------------------------------------


def all_options() -> List[DecisionKind]:
    """Return every possible harmonization decision kind.

    Useful for UI/CLI that presents the full menu of choices.
    """
    return list(DecisionKind)


def make_install_decision(
    candidate_id: str, rationale: str = ""
) -> HarmonizationChoice:
    """Create an INSTALL decision."""
    return HarmonizationChoice(
        candidate_id=candidate_id,
        decision=DecisionKind.INSTALL,
        rationale=rationale or "Wiki is a good fit for local knowledge base.",
    )


def make_skip_decision(
    candidate_id: str, rationale: str = ""
) -> HarmonizationChoice:
    """Create a SKIP decision."""
    return HarmonizationChoice(
        candidate_id=candidate_id,
        decision=DecisionKind.SKIP,
        rationale=rationale or "Wiki overlaps substantially with local content.",
    )


def make_route_only_decision(
    candidate_id: str, rationale: str = ""
) -> HarmonizationChoice:
    """Create a ROUTE_ONLY decision."""
    return HarmonizationChoice(
        candidate_id=candidate_id,
        decision=DecisionKind.ROUTE_ONLY,
        rationale=rationale or "Wiki is useful as an on-demand reference.",
    )


def make_prefer_local_decision(
    candidate_id: str, rationale: str = ""
) -> HarmonizationChoice:
    """Create a PREFER_LOCAL decision."""
    return HarmonizationChoice(
        candidate_id=candidate_id,
        decision=DecisionKind.PREFER_LOCAL,
        rationale=rationale or "Local knowledge takes precedence in conflicts.",
    )


def make_prefer_wiki_decision(
    candidate_id: str, rationale: str = ""
) -> HarmonizationChoice:
    """Create a PREFER_WIKI decision."""
    return HarmonizationChoice(
        candidate_id=candidate_id,
        decision=DecisionKind.PREFER_WIKI,
        rationale=rationale or "Wiki knowledge takes precedence in conflicts.",
    )


def make_keep_both_decision(
    candidate_id: str,
    boundaries: List[str],
    rationale: str = "",
) -> HarmonizationChoice:
    """Create a KEEP_BOTH_WITH_BOUNDARIES decision."""
    return HarmonizationChoice(
        candidate_id=candidate_id,
        decision=DecisionKind.KEEP_BOTH_WITH_BOUNDARIES,
        rationale=rationale or "Both versions coexist with explicit scope boundaries.",
        applied_boundaries=boundaries,
    )