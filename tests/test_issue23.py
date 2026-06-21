"""Issue #23 — bounded-context crossing warnings from graph structure."""

from __future__ import annotations

import json
import os

from iknow.contracts.model import ServingEntryPoint, TrustState, WikiContract
from iknow.fit import compute_fit
from iknow.fit.result import RouteRecommendation
from iknow.inventory import inventory_from_graphify_graph, load_graphify_inventory

ROOT = os.path.dirname(os.path.dirname(__file__))
GRAPH_FIXTURE = os.path.join(
    ROOT,
    "tests",
    "fixtures",
    "graphify",
    "context_fit_graph.json",
)


def contract(scope: list[str]) -> WikiContract:
    return WikiContract(
        name="Candidate Wiki",
        description="Candidate used for Context Fit tests.",
        version="1.0.0",
        scope=scope,
        non_scope=[],
        provenance="synthetic",
        freshness="2026-06-21",
        license="MIT",
        trust_state=TrustState.VERIFIED,
        entry_points=[ServingEntryPoint.MARKDOWN],
    )


def graph(nodes: list[dict], links: list[dict] | None = None) -> dict:
    return {
        "directed": True,
        "multigraph": False,
        "graph": {"name": "test graph"},
        "nodes": nodes,
        "links": links or [],
    }


class TestIssue23BoundedContextWarnings:
    def test_clear_cross_boundary_candidate_warns_and_routes_with_care(self) -> None:
        inventory = load_graphify_inventory(GRAPH_FIXTURE)
        result = compute_fit(
            contract(["Knowledge Pack Routing", "Product Case Studies"]),
            inventory,
        )
        fit = result.fit

        assert any("spans multiple local graph contexts" in w for w in fit.boundary_warnings)
        assert "graphify_community_1" in "\n".join(fit.boundary_warnings)
        assert "graphify_community_3" in "\n".join(fit.boundary_warnings)
        assert fit.recommendation is RouteRecommendation.ROUTE_WITH_CARE

    def test_single_community_graph_degrades_without_boundary_warning(self) -> None:
        inventory = inventory_from_graphify_graph(
            graph(
                [
                    {
                        "id": "a",
                        "label": "Knowledge Pack Routing",
                        "source_file": "docs/a.md",
                        "community": 1,
                    },
                    {
                        "id": "b",
                        "label": "Runtime Memory Knowledge Routing",
                        "source_file": "docs/b.md",
                        "community": 1,
                    },
                ]
            )
        )
        fit = compute_fit(
            contract(["Knowledge Pack Routing", "Runtime Memory Knowledge Routing"]),
            inventory,
        ).fit

        assert not any("spans multiple local graph contexts" in w for w in fit.boundary_warnings)
        assert fit.recommendation is RouteRecommendation.RECOMMENDED_INSTALL

    def test_graph_without_community_metadata_degrades_gracefully(self) -> None:
        inventory = inventory_from_graphify_graph(
            graph(
                [
                    {"id": "a", "label": "Knowledge Pack Routing", "source_file": "docs/a.md"},
                    {"id": "b", "label": "Product Case Studies", "source_file": "docs/b.md"},
                ]
            )
        )
        fit = compute_fit(
            contract(["Knowledge Pack Routing", "Product Case Studies"]),
            inventory,
        ).fit

        assert not any("spans multiple local graph contexts" in w for w in fit.boundary_warnings)
        assert fit.recommendation is RouteRecommendation.RECOMMENDED_INSTALL

    def test_utility_and_noise_nodes_do_not_create_false_boundary_warnings(self) -> None:
        inventory = load_graphify_inventory(GRAPH_FIXTURE)
        fit = compute_fit(
            contract(["Knowledge Pack Routing", "Path", "compare.py"]),
            inventory,
        ).fit

        assert not any("spans multiple local graph contexts" in w for w in fit.boundary_warnings)
        assert "Path" in fit.gap_topics
        assert "compare.py" in fit.gap_topics

    def test_weak_bridge_across_two_graph_contexts_warns_without_erasing_gap(self) -> None:
        inventory = load_graphify_inventory(GRAPH_FIXTURE)
        fit = compute_fit(
            contract(["Knowledge Pack Routing", "MCP protocol concepts"]),
            inventory,
        ).fit

        assert "MCP protocol concepts" in fit.graph_evidence_topics
        assert "MCP protocol concepts" in fit.gap_topics
        assert any("spans multiple local graph contexts" in w for w in fit.boundary_warnings)
        assert fit.recommendation is RouteRecommendation.ROUTE_WITH_CARE

    def test_noisy_cross_community_edge_alone_does_not_warn_without_candidate_match(self) -> None:
        with open(GRAPH_FIXTURE, "r", encoding="utf-8") as f:
            data = json.load(f)
        inventory = inventory_from_graphify_graph(data)
        fit = compute_fit(contract(["Knowledge Pack Routing"]), inventory).fit

        assert not any("spans multiple local graph contexts" in w for w in fit.boundary_warnings)
        assert fit.recommendation is RouteRecommendation.RECOMMENDED_INSTALL
