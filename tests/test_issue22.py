"""Issue #22 — separate exact overlap from graph-evidence overlap."""

from __future__ import annotations

import os

from iknow.contracts.model import ServingEntryPoint, TrustState, WikiContract
from iknow.fit import compute_fit
from iknow.fit.result import RouteRecommendation
from iknow.inventory import load_graphify_inventory
from iknow.inventory.model import InventoryItem, LocalKnowledgeInventory
from iknow.cli import main

ROOT = os.path.dirname(os.path.dirname(__file__))
GRAPH_FIXTURE = os.path.join(
    ROOT,
    "tests",
    "fixtures",
    "graphify",
    "context_fit_graph.json",
)


def contract(scope: list[str], non_scope: list[str] | None = None) -> WikiContract:
    return WikiContract(
        name="Candidate Wiki",
        description="Candidate used for Context Fit tests.",
        version="1.0.0",
        scope=scope,
        non_scope=non_scope or [],
        provenance="synthetic",
        freshness="2026-06-21",
        license="MIT",
        trust_state=TrustState.VERIFIED,
        entry_points=[ServingEntryPoint.MARKDOWN],
    )


def inventory(scope: list[str], non_scope: list[str] | None = None) -> LocalKnowledgeInventory:
    return LocalKnowledgeInventory(
        name="Test Inventory",
        description="Synthetic inventory.",
        items=[
            InventoryItem(
                id="local",
                name="Local",
                description="Local evidence.",
                scope=scope,
                non_scope=non_scope or [],
                entry_points=[ServingEntryPoint.MARKDOWN],
                trust_state=TrustState.COMMUNITY,
                evidence_sources={topic: [f"docs/{topic.lower().replace(' ', '-')}.md"] for topic in scope},
            )
        ],
    )


class TestIssue22ExactVsGraphEvidence:
    def test_exact_match_is_overlap_with_evidence_source(self) -> None:
        result = compute_fit(
            contract(["MCP Server Development"]),
            inventory(["MCP Server Development"]),
        )
        fit = result.fit

        assert fit.overlapping_topics == ["MCP Server Development"]
        assert fit.graph_evidence_topics == []
        assert fit.gap_topics == []
        assert fit.evidence_sources == ["docs/mcp-server-development.md"]
        assert fit.recommendation is RouteRecommendation.RECOMMENDED_INSTALL

    def test_weak_graph_evidence_remains_a_gap(self) -> None:
        result = compute_fit(
            contract(["MCP protocol concepts"]),
            inventory(["MCP Server Development"]),
        )
        fit = result.fit

        assert fit.overlapping_topics == []
        assert fit.graph_evidence_topics == ["MCP protocol concepts"]
        assert fit.gap_topics == ["MCP protocol concepts"]
        assert fit.gap_percentage == 1.0
        assert fit.recommendation is RouteRecommendation.FINDABLE_ONLY

    def test_no_evidence_is_gap_without_graph_evidence(self) -> None:
        result = compute_fit(
            contract(["Rust compiler internals"]),
            inventory(["MCP Server Development"]),
        )
        fit = result.fit

        assert fit.overlapping_topics == []
        assert fit.graph_evidence_topics == []
        assert fit.gap_topics == ["Rust compiler internals"]
        assert fit.evidence_sources == []

    def test_candidate_non_scope_still_dominates_boundary_warnings(self) -> None:
        result = compute_fit(
            contract(["MCP Server Development"], non_scope=["Product Case Studies"]),
            inventory(["MCP Server Development", "Product Case Studies"]),
        )
        fit = result.fit

        assert fit.overlapping_topics == ["MCP Server Development"]
        assert fit.graph_evidence_topics == []
        assert any("Product Case Studies" in warning for warning in fit.boundary_warnings)
        assert fit.recommendation is RouteRecommendation.ROUTE_WITH_CARE

    def test_graphify_fixture_fit_separates_exact_from_related_evidence(self) -> None:
        graph_inventory = load_graphify_inventory(GRAPH_FIXTURE)
        result = compute_fit(
            contract(["MCP Server Development", "MCP protocol concepts", "Unknown Topic"]),
            graph_inventory,
        )
        fit = result.fit

        assert fit.overlapping_topics == ["MCP Server Development"]
        assert "MCP protocol concepts" in fit.graph_evidence_topics
        assert "MCP protocol concepts" in fit.gap_topics
        assert "Unknown Topic" in fit.gap_topics
        assert any(source.endswith("mcp-server-development.md") for source in fit.evidence_sources)

    def test_cli_displays_exact_overlap_graph_evidence_gaps_and_sources(self, capsys) -> None:
        rc = main(["fit", "mcp_basics", "--inventory-graph", GRAPH_FIXTURE])

        assert rc == 0
        captured = capsys.readouterr()
        assert "Overlap (1 exact topics):" in captured.out
        assert "✓ MCP server development" in captured.out
        assert "Graph evidence" in captured.out
        assert "~ MCP protocol concepts" in captured.out
        assert "Evidence sources:" in captured.out
        assert "Gaps" in captured.out
