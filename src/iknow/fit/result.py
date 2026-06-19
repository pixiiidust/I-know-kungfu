"""Data models for Context Fit results.

A Context Fit describes the relationship between a candidate Wiki Contract
and the local knowledge inventory: what overlaps, what's new, what might
conflict, and what recommended action to take.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import List


class RouteRecommendation(Enum):
    """Recommended action based on fit analysis.

    Values are ordered from most to least recommended.
    """

    RECOMMENDED_INSTALL = "recommended_install"
    """High overlap, acceptable gaps, no hard conflicts — install is safe."""

    ROUTE_WITH_CARE = "route_with_care"
    """Moderate overlap or some boundary warnings — route to content but
    flag areas of caution during interaction."""

    FINDABLE_ONLY = "findable_only"
    """Low overlap or significant uncertainty — make wiki findable/known
    but do not auto-route or install.  User can opt in explicitly."""

    SKIP = "skip"
    """Substantial overlap or conflicts — no action recommended."""


@dataclass
class FitResult:
    """The complete output of a Context Fit comparison.

    Contains everything needed for a CLI/UI display: overlap, gaps,
    boundary/conflict warnings, merge risk assessment, and a route
    recommendation.  All fields are deterministic for given inputs.
    """

    # -- Overlap / gaps -----------------------------------------------------

    overlapping_topics: List[str] = field(default_factory=list)
    """Scope items present in both the candidate wiki and the inventory."""

    gap_topics: List[str] = field(default_factory=list)
    """Scope items in the candidate wiki that are NOT in the inventory."""

    # -- Boundary / conflict ------------------------------------------------

    boundary_warnings: List[str] = field(default_factory=list)
    """Human-readable warnings about scope/non-scope boundary crossings.

    E.g. 'candidate covers "shell configuration" which your local inventory
    explicitly excludes' or 'candidate explicitly excludes "Python packaging"
    which is in your local scope'.
    """

    conflict_warnings: List[str] = field(default_factory=list)
    """Hard conflicts where both sides claim the same topic but differ
    significantly in approach or trust posture."""

    # -- Merge risk ---------------------------------------------------------

    merge_risk: str = "unknown"
    """Qualitative assessment: ``"low"``, ``"medium"``, or ``"high"``.

    Based on gap percentage and boundary warnings.
    """

    gap_percentage: float = 0.0
    """Ratio of gap topics to total candidate scope (0.0 – 1.0).

    0.0 = every candidate scope topic is already known locally.
    1.0 = nothing in the candidate scope is known locally.
    """

    # -- Recommendation -----------------------------------------------------

    recommendation: RouteRecommendation = RouteRecommendation.FINDABLE_ONLY
    """The recommended action based on fit analysis."""


@dataclass
class FitComparison:
    """Top-level container for a full fit comparison.

    Wraps the candidate wiki identity alongside the fit analysis so
    callers have everything in one object.
    """

    candidate_id: str
    """Registry ID of the candidate wiki that was analysed."""

    candidate_name: str
    """Name of the candidate wiki."""

    inventory_name: str
    """Name of the local inventory used for the comparison."""

    fit: FitResult
    """The detailed fit analysis result."""
