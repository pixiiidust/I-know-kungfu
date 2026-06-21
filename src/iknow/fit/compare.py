"""Context Fit comparison logic.

Compares a candidate Wiki Contract against a Local Knowledge Inventory
and returns a structured FitResult with overlap, gaps, boundary warnings,
conflict warnings, merge risk, and route recommendation.

Ponytail v1: deterministic heuristic-only comparison. No ML, no vector
search, no real scanning, no mutation, no install.
"""

from __future__ import annotations

from typing import List

from iknow.contracts.model import WikiContract
from iknow.inventory.model import LocalKnowledgeInventory
from iknow.fit.result import FitResult, FitComparison, RouteRecommendation


def compute_fit(
    candidate: WikiContract,
    inventory: LocalKnowledgeInventory,
    candidate_id: str = "unknown",
) -> FitComparison:
    """Compare a candidate Wiki Contract against a local inventory.

    Parameters
    ----------
    candidate:
        The Wiki Contract to evaluate.
    inventory:
        The local knowledge inventory to compare against.
    candidate_id:
        Optional registry ID for the candidate (used in the response).

    Returns
    -------
    FitComparison
        A complete comparison with overlap, gaps, warnings, risk,
        and a route recommendation.
    """
    candidate_scope = [s.strip() for s in candidate.scope]
    candidate_non_scope = [ns.strip() for ns in candidate.non_scope]
    inventory_scope_set = {_normalize(s) for s in inventory.combined_scope}
    inventory_non_scope_set = {_normalize(ns) for ns in inventory.combined_non_scope}
    evidence_by_topic = _inventory_evidence_by_topic(inventory)

    # -- Overlap ------------------------------------------------------------
    overlapping: List[str] = []
    graph_evidence: List[str] = []
    evidence_sources: List[str] = []
    gaps: List[str] = []

    for topic in candidate_scope:
        norm = _normalize(topic)
        if norm in inventory_scope_set:
            overlapping.append(topic)
            evidence_sources.extend(evidence_by_topic.get(norm, []))
        else:
            gaps.append(topic)
            related_sources = _related_graph_evidence_sources(topic, evidence_by_topic)
            if related_sources:
                graph_evidence.append(topic)
                evidence_sources.extend(related_sources)

    # -- Boundary / conflict warnings ---------------------------------------
    boundary_warnings: List[str] = []
    conflict_warnings: List[str] = []

    # Candidate scope items that the inventory explicitly excludes
    for topic in candidate_scope:
        norm = _normalize(topic)
        if norm in inventory_non_scope_set:
            boundary_warnings.append(
                f'Candidate covers "{topic}" but your local inventory '
                f"explicitly excludes it."
            )

    # Candidate non-scope items that the inventory includes (reverse boundary)
    for topic in candidate_non_scope:
        norm = _normalize(topic)
        if norm in inventory_scope_set:
            boundary_warnings.append(
                f'Candidate explicitly excludes "{topic}" which is '
                f"in your local inventory's scope."
            )

    # -- Merge risk ---------------------------------------------------------
    total = len(candidate.scope)
    gap_percentage = len(gaps) / total if total > 0 else 0.0

    if gap_percentage > 0.7:
        merge_risk = "high"
    elif gap_percentage > 0.3:
        merge_risk = "medium"
    else:
        merge_risk = "low"

    # Bump risk for boundary warnings
    if boundary_warnings:
        if merge_risk == "low":
            merge_risk = "medium"
        elif merge_risk == "medium":
            merge_risk = "high"

    # -- Route recommendation -----------------------------------------------
    recommendation = _recommend_route(
        gap_percentage=gap_percentage,
        overlapping=overlapping,
        boundary_warnings=boundary_warnings,
        conflict_warnings=conflict_warnings,
        trust_state=candidate.trust_state,
    )

    fit = FitResult(
        overlapping_topics=overlapping,
        graph_evidence_topics=graph_evidence,
        evidence_sources=_dedupe(evidence_sources),
        gap_topics=gaps,
        boundary_warnings=boundary_warnings,
        conflict_warnings=conflict_warnings,
        merge_risk=merge_risk,
        gap_percentage=round(gap_percentage, 2),
        recommendation=recommendation,
    )

    return FitComparison(
        candidate_id=candidate_id,
        candidate_name=candidate.name,
        inventory_name=inventory.name,
        fit=fit,
    )


def _normalize(value: str) -> str:
    """Normalize a topic for comparison without mutating source objects."""
    return value.lower().strip()


def _tokens(value: str) -> set[str]:
    """Return comparison tokens, keeping only useful domain terms."""
    stopwords = {
        "and", "or", "the", "a", "an", "to", "of", "for", "with", "in", "on",
        "patterns", "pattern", "concepts", "concept", "definitions", "definition",
    }
    return {
        token
        for token in _normalize(value).replace(".", " ").replace("-", " ").split()
        if len(token) > 2 and token not in stopwords
    }


def _inventory_evidence_by_topic(inventory: LocalKnowledgeInventory) -> dict[str, list[str]]:
    """Map normalized inventory topic → local-safe evidence source paths."""
    evidence: dict[str, list[str]] = {}
    for item in inventory.items:
        for topic in item.scope:
            norm = _normalize(topic)
            sources = item.evidence_sources.get(topic, [])
            evidence.setdefault(norm, [])
            evidence[norm].extend(sources)
    return {topic: _dedupe(sources) for topic, sources in evidence.items()}


def _related_graph_evidence_sources(
    candidate_topic: str,
    evidence_by_topic: dict[str, list[str]],
) -> list[str]:
    """Find weak related Graphify/local evidence without turning it into overlap."""
    candidate_tokens = _tokens(candidate_topic)
    if not candidate_tokens:
        return []
    sources: list[str] = []
    for inventory_topic, inventory_sources in evidence_by_topic.items():
        inventory_tokens = _tokens(inventory_topic)
        if candidate_tokens & inventory_tokens:
            sources.extend(inventory_sources)
    return _dedupe(sources)


def _dedupe(values: List[str]) -> List[str]:
    seen: set[str] = set()
    result: List[str] = []
    for value in values:
        if value and value not in seen:
            seen.add(value)
            result.append(value)
    return result


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _recommend_route(
    gap_percentage: float,
    overlapping: List[str],
    boundary_warnings: List[str],
    conflict_warnings: List[str],
    trust_state: object,
) -> RouteRecommendation:
    """Heuristic route recommendation based on fit metrics.

    The recommendation is purely heuristic and deterministic for
    given inputs.  No automatic install or trust occurs here.
    """
    from iknow.contracts.model import TrustState

    # Hard conflict → skip
    if conflict_warnings:
        return RouteRecommendation.SKIP

    # High gap with boundary warnings → findable only
    if gap_percentage > 0.7 and boundary_warnings:
        return RouteRecommendation.FINDABLE_ONLY

    # High gap → at least findable
    if gap_percentage > 0.7:
        return RouteRecommendation.FINDABLE_ONLY

    # Moderate gap → route with care
    if gap_percentage > 0.3:
        if boundary_warnings:
            return RouteRecommendation.ROUTE_WITH_CARE
        # If trust is high, still route-with-care might be fine
        return RouteRecommendation.ROUTE_WITH_CARE

    # Low gap — good overlap
    if gap_percentage <= 0.3:
        if boundary_warnings:
            return RouteRecommendation.ROUTE_WITH_CARE
        # Great fit — recommend install
        if overlapping and isinstance(trust_state, TrustState):
            if trust_state in (TrustState.VERIFIED, TrustState.OFFICIAL):
                return RouteRecommendation.RECOMMENDED_INSTALL
        return RouteRecommendation.RECOMMENDED_INSTALL

    return RouteRecommendation.FINDABLE_ONLY