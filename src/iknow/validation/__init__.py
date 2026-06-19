"""Validation module.

Seam: contract, provenance, and entry-point checks. Endpoint-ready — local
adapters now, hosted listing/recommendation/eval checks later.

v1 adapter: local-only static checks (contract validity, source provenance,
entry-point completeness). No hosted backend.

Public API
----------
- ``check_listing_eligibility`` — gate for cookbook registry listing.
- ``check_recommendation_eligibility`` — gate for agent recommendation.
- ``validate_wiki`` — combined local validation output for future endpoints.
- ``GateResult`` — outcome of a single gate check.
- ``ValidationOutput`` — combined listing + recommendation result.
"""

from iknow.validation.gates import (
    check_listing_eligibility,
    check_recommendation_eligibility,
)
from iknow.validation.results import GateResult, ValidationOutput


def validate_wiki(contract, wiki_dir=None) -> ValidationOutput:
    """Run both local eligibility gates and return one endpoint-ready result."""
    listing = check_listing_eligibility(contract, wiki_dir)
    recommendation = check_recommendation_eligibility(contract, wiki_dir)
    return ValidationOutput(
        wiki_id=contract.name,
        listing=listing,
        recommendation=recommendation,
    )


__all__ = [
    "check_listing_eligibility",
    "check_recommendation_eligibility",
    "validate_wiki",
    "GateResult",
    "ValidationOutput",
]