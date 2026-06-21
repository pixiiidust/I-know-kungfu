"""Issue #21 — Graphify graph input seam for ``iknow fit``."""

from __future__ import annotations

import os

from iknow import cli
from iknow.cli import build_parser, main
import iknow.inventory.graphify as graphify_adapter

ROOT = os.path.dirname(os.path.dirname(__file__))
GRAPH_FIXTURE = os.path.join(
    ROOT,
    "tests",
    "fixtures",
    "graphify",
    "context_fit_graph.json",
)


class TestIssue21GraphifyFitInputSeam:
    def test_parser_exposes_inventory_graph_flag(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            ["fit", "mcp_basics", "--inventory-graph", "graphify-out/graph.json"]
        )

        assert args.command == "fit"
        assert args.inventory_graph == "graphify-out/graph.json"
        assert args.inventory == "default"

    def test_fit_can_load_graphify_graph_inventory(self, capsys) -> None:
        rc = main(["fit", "mcp_basics", "--inventory-graph", GRAPH_FIXTURE])

        assert rc == 0
        captured = capsys.readouterr()
        assert "Inventory:     Graphify-derived Local Inventory" in captured.out
        assert "✓ MCP server development" in captured.out
        assert "Recommendation:" in captured.out

    def test_default_inventory_behavior_still_works(self, capsys) -> None:
        rc = main(["fit", "mcp_basics"])

        assert rc == 0
        captured = capsys.readouterr()
        assert "Inventory:     Default Local Knowledge Base" in captured.out
        assert "Recommendation:" in captured.out

    def test_missing_graph_file_fails_clearly(self, capsys) -> None:
        rc = main(["fit", "mcp_basics", "--inventory-graph", "/tmp/does-not-exist-iknow.json"])

        assert rc == 1
        captured = capsys.readouterr()
        assert "Failed to load Graphify inventory graph" in captured.err
        assert "does-not-exist-iknow.json" in captured.err

    def test_invalid_json_graph_fails_clearly(self, tmp_path, capsys) -> None:
        bad_graph = tmp_path / "bad-graph.json"
        bad_graph.write_text("{not-json", encoding="utf-8")

        rc = main(["fit", "mcp_basics", "--inventory-graph", str(bad_graph)])

        assert rc == 1
        captured = capsys.readouterr()
        assert "Failed to load Graphify inventory graph" in captured.err

    def test_unsupported_graph_schema_fails_clearly(self, tmp_path, capsys) -> None:
        bad_graph = tmp_path / "not-graphify.json"
        bad_graph.write_text('{"items": []}', encoding="utf-8")

        rc = main(["fit", "mcp_basics", "--inventory-graph", str(bad_graph)])

        assert rc == 1
        captured = capsys.readouterr()
        assert "Unsupported Graphify graph schema" in captured.err
        assert "missing 'nodes' list" in captured.err

    def test_oversized_graph_fails_clearly(self, monkeypatch, capsys) -> None:
        monkeypatch.setattr(graphify_adapter, "MAX_GRAPH_BYTES", 1)

        rc = main(["fit", "mcp_basics", "--inventory-graph", GRAPH_FIXTURE])

        assert rc == 1
        captured = capsys.readouterr()
        assert "Graphify graph is too large" in captured.err

    def test_inventory_and_inventory_graph_are_mutually_exclusive(self, tmp_path, capsys) -> None:
        custom_inventory = tmp_path / "inventory.json"
        custom_inventory.write_text('{"name": "custom", "description": "custom"}', encoding="utf-8")

        rc = main(
            [
                "fit",
                "mcp_basics",
                "--inventory",
                str(custom_inventory),
                "--inventory-graph",
                GRAPH_FIXTURE,
            ]
        )

        assert rc == 1
        captured = capsys.readouterr()
        assert "use either --inventory or --inventory-graph" in captured.err

    def test_graph_input_seam_is_read_only(self, tmp_path, monkeypatch, capsys) -> None:
        monkeypatch.chdir(tmp_path)
        rc = main(["fit", "mcp_basics", "--inventory-graph", GRAPH_FIXTURE])

        assert rc == 0
        assert not (tmp_path / "graphify-out").exists()
        assert not (tmp_path / ".kungfu").exists()
        captured = capsys.readouterr()
        assert "Graphify-derived Local Inventory" in captured.out
