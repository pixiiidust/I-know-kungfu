"""Validation result types for listing and recommendation eligibility gates.

Defines the data classes that carry gate check outcomes, distinguishing
between warnings (informational) and blockers (fail the gate).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


# ---------------------------------------------------------------------------
# GateResult
# ---------------------------------------------------------------------------


@dataclass
class GateResult:
    """Outcome of a single validation gate (listing or recommendation).

    ``passed`` is ``True`` only when there are zero **blockers**.
    Warnings may be present even on a passing result — they are advisory
    and do not block eligibility.

    Attributes
    ----------
    wiki_id:
        Identifier of the wiki that was checked.
    passed:
        ``True`` iff the gate has no blockers.
    blockers:
        Issues that prevent this gate from passing (e.g. missing required
        metadata, missing artifacts).
    warnings:
        Advisory issues that do *not* block the gate (e.g. weak provenance,
        low trust, missing maintainer).
    """

    wiki_id: str
    passed: bool
    blockers: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    # ------------------------------------------------------------------
    # Convenience
    # ------------------------------------------------------------------

    @property
    def total_issues(self) -> int:
        """Total number of issues (blockers + warnings)."""
        return len(self.blockers) + len(self.warnings)

    def merge(self, other: GateResult) -> GateResult:
        """Merge another ``GateResult`` into this one (mutating).

        Blockers and warnings are appended; ``passed`` is ``True`` only if
        *both* results passed.
        """
        self.blockers.extend(other.blockers)
        self.warnings.extend(other.warnings)
        self.passed = self.passed and other.passed
        return self

    def to_dict(self) -> dict:
        """Serialise to a plain dict (useful for CLI / JSON output)."""
        return {
            "wiki_id": self.wiki_id,
            "passed": self.passed,
            "blockers": list(self.blockers),
            "warnings": list(self.warnings),
        }


# ---------------------------------------------------------------------------
# Composite result
# ---------------------------------------------------------------------------


@dataclass
class ValidationOutput:
    """Combined output of both listing and recommendation gates.

    This is the top-level result consumers interact with.  Each gate has
    its own ``GateResult`` so callers can inspect individual outcomes.
    """

    wiki_id: str
    listing: GateResult
    recommendation: GateResult

    @property
    def listable(self) -> bool:
        """Shortcut: is this wiki listable?"""
        return self.listing.passed

    @property
    def recommendable(self) -> bool:
        """Shortcut: is this wiki recommendable?"""
        return self.recommendation.passed

    def to_dict(self) -> dict:
        """Serialise to a plain dict."""
        return {
            "wiki_id": self.wiki_id,
            "listable": self.listable,
            "recommendable": self.recommendable,
            "listing": self.listing.to_dict(),
            "recommendation": self.recommendation.to_dict(),
        }
