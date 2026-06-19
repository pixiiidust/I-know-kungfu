"""Context Fit module.

Seam: compare a candidate Wiki Contract against a Local Knowledge Inventory.
Returns overlap, gaps, boundary/conflict warnings, merge risk, and a route
recommendation.

v1 adapter: local-only heuristic analysis. No cloud or vector DB.
"""

from iknow.fit.compare import compute_fit
from iknow.fit.result import (
    FitComparison,
    FitResult,
    RouteRecommendation,
)

__all__ = [
    "compute_fit",
    "FitComparison",
    "FitResult",
    "RouteRecommendation",
]