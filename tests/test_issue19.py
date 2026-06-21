"""Issue #19 — synthetic Graphify graph fixture for Context Fit."""

from __future__ import annotations

import json
import os
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(__file__))
GRAPH_FIXTURE_DIR = os.path.join(ROOT, "tests", "fixtures", "graphify")
GRAPH_FIXTURE = os.path.join(GRAPH_FIXTURE_DIR, "context_fit_graph.json")
EMPTY_GRAPH_FIXTURE = os.path.join(GRAPH_FIXTURE_DIR, "empty_graph.json")
DANGLING_LINK_FIXTURE = os.path.join(GRAPH_FIXTURE_DIR, "dangling_link_graph.json")

NOISE_LABELS = {"Path", "typing", "str", "Any"}


def load_graph(path: str = GRAPH_FIXTURE) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


class TestIssue19GraphifyFixture:
    def test_synthetic_graph_fixture_exists_and_uses_graphify_shape(self) -> None:
        graph = load_graph()

        assert graph["directed"] is True
        assert isinstance(graph["nodes"], list)
        assert isinstance(graph["links"], list)
        assert graph["graph"]["purpose"].startswith("Deterministic local graph evidence")

    def test_fixture_has_fit_relevant_concepts_and_communities(self) -> None:
        graph = load_graph()
        labels = {node.get("label") for node in graph["nodes"]}
        communities = {node.get("community") for node in graph["nodes"]}

        assert "Knowledge Pack Routing" in labels
        assert "MCP Server Development" in labels
        assert "llms.txt entrypoints" in labels
        assert "AI-native Product Framing" in labels
        assert "Product Case Studies" in labels
        assert {1, 2, 3}.issubset(communities)

    def test_fixture_can_exercise_overlap_gap_and_boundary_risk(self) -> None:
        graph = load_graph()
        labels = {node.get("label") for node in graph["nodes"]}
        cross_community_edges = []
        community_by_id = {node["id"]: node.get("community") for node in graph["nodes"]}

        for edge in graph["links"]:
            source_community = community_by_id.get(edge["source"])
            target_community = community_by_id.get(edge["target"])
            if source_community != target_community:
                cross_community_edges.append(edge)

        # Candidate exact/graph overlap can match these local graph topics.
        assert "Knowledge Pack Routing" in labels
        assert "MCP Server Development" in labels

        # Candidate non-scope or poor-fit examples can be tested against this topic.
        assert "Product Case Studies" in labels

        # Boundary-risk demos need at least one ambiguous cross-context bridge.
        assert any(
            edge["confidence"] == "AMBIGUOUS"
            and edge["relation"] in {"cross_context_entrypoint", "cross_context_overlap"}
            for edge in cross_community_edges
        )

    def test_fixture_contains_documented_edge_case_nodes_for_adapter_tests(self) -> None:
        graph = load_graph()
        nodes = graph["nodes"]
        labels = [node.get("label") for node in nodes]
        label_counts = Counter(label for label in labels if label)

        assert any("label" not in node for node in nodes), "missing-label node not represented"
        assert any(node.get("source_file") == "" for node in nodes), "missing-source node not represented"
        assert any(label in NOISE_LABELS for label in labels), "noise/builtin labels not represented"
        assert label_counts["Knowledge Pack Routing"] > 1, "duplicate concept not represented"

    def test_fixture_avoids_private_absolute_paths(self) -> None:
        graph = load_graph()
        source_files = [node.get("source_file", "") for node in graph["nodes"]]

        assert source_files
        for source_file in source_files:
            assert not source_file.startswith("/"), source_file
            assert ":\\" not in source_file, source_file
            assert "/home/" not in source_file, source_file
            assert "/Users/" not in source_file, source_file
            assert "/root/" not in source_file, source_file

    def test_empty_graph_fixture_covers_no_local_evidence_case(self) -> None:
        graph = load_graph(EMPTY_GRAPH_FIXTURE)

        assert graph["directed"] is True
        assert graph["nodes"] == []
        assert graph["links"] == []
        assert "empty" in graph["graph"]["purpose"]

    def test_dangling_link_fixture_covers_missing_node_references(self) -> None:
        graph = load_graph(DANGLING_LINK_FIXTURE)
        node_ids = {node["id"] for node in graph["nodes"]}
        dangling_edges = [
            edge
            for edge in graph["links"]
            if edge["source"] not in node_ids or edge["target"] not in node_ids
        ]

        assert dangling_edges
        assert dangling_edges[0]["target"] == "missing:node"
