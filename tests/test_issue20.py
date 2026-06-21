"""Issue #20 — derive LocalKnowledgeInventory from Graphify graph data."""

from __future__ import annotations

import copy
import json
import os

from iknow.contracts.model import ServingEntryPoint, TrustState
from iknow.inventory import inventory_from_graphify_graph, load_graphify_inventory
from iknow.inventory.model import LocalKnowledgeInventory

ROOT = os.path.dirname(os.path.dirname(__file__))
GRAPH_FIXTURE = os.path.join(
    ROOT,
    "tests",
    "fixtures",
    "graphify",
    "context_fit_graph.json",
)
EMPTY_GRAPH_FIXTURE = os.path.join(
    ROOT,
    "tests",
    "fixtures",
    "graphify",
    "empty_graph.json",
)


def load_fixture(path: str = GRAPH_FIXTURE) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


class TestIssue20GraphifyInventoryAdapter:
    def test_graph_nodes_map_to_local_knowledge_inventory_items(self) -> None:
        inventory = load_graphify_inventory(GRAPH_FIXTURE)

        assert isinstance(inventory, LocalKnowledgeInventory)
        assert inventory.name == "Graphify-derived Local Inventory"
        assert inventory.items
        assert "Knowledge Pack Routing" in inventory.combined_scope
        assert "MCP Server Development" in inventory.combined_scope
        assert "AI-native Product Framing" in inventory.combined_scope

    def test_adapter_groups_topics_by_graph_community(self) -> None:
        inventory = load_graphify_inventory(GRAPH_FIXTURE)
        ids = {item.id for item in inventory.items}

        assert "graphify_community_1" in ids
        assert "graphify_community_2" in ids
        assert "graphify_community_3" in ids
        for item in inventory.items:
            assert item.name.startswith("Graphify community ")
            assert item.entry_points == [ServingEntryPoint.MARKDOWN]
            assert item.trust_state is TrustState.COMMUNITY
            assert "Evidence only" in item.description

    def test_adapter_filters_noise_file_nodes_and_duplicates(self) -> None:
        inventory = load_graphify_inventory(GRAPH_FIXTURE)
        scope = inventory.combined_scope

        assert "Knowledge Pack Routing" in scope
        assert scope.count("Knowledge Pack Routing") == 1
        assert "compare.py" not in scope
        assert "Path" not in scope
        assert "typing" not in scope
        assert "No Source Concept" in scope  # allowed concept evidence, not builtin noise

    def test_adapter_preserves_local_safe_source_evidence_in_description(self) -> None:
        inventory = load_graphify_inventory(GRAPH_FIXTURE)
        description = "\n".join(item.description for item in inventory.items)

        assert "docs/agent-workflows/wiki/concepts/knowledge-pack-routing.md" in description
        assert "edge_confidence=" in description
        assert "max_degree=" in description
        assert not any(secret in description for secret in ["/root/", "/home/", "/Users/", ":\\"])

    def test_adapter_redacts_absolute_source_paths_when_present(self) -> None:
        graph = load_fixture()
        graph = copy.deepcopy(graph)
        graph["nodes"].append(
            {
                "id": "private:absolute",
                "label": "Private Absolute Source",
                "source_file": "/home/jamie/project/docs/private-source.md",
                "source_location": "L1",
                "file_type": "document",
                "community": 5,
            }
        )

        inventory = inventory_from_graphify_graph(graph)
        description = "\n".join(item.description for item in inventory.items)

        assert "Private Absolute Source" in inventory.combined_scope
        assert "docs/private-source.md" in description
        assert "/home/jamie" not in description

    def test_empty_graph_derives_empty_inventory_without_error(self) -> None:
        inventory = load_graphify_inventory(EMPTY_GRAPH_FIXTURE)

        assert inventory.name == "Graphify-derived Local Inventory"
        assert inventory.items == []
        assert inventory.combined_scope == []

    def test_graph_signals_remain_evidence_not_trust_or_install_authority(self) -> None:
        inventory = load_graphify_inventory(GRAPH_FIXTURE)

        assert inventory.items
        for item in inventory.items:
            assert item.trust_state is TrustState.COMMUNITY
            assert item.entry_points == [ServingEntryPoint.MARKDOWN]
            assert "not a trust, provenance, freshness, or install claim" in item.description
            assert item.non_scope == []
