"""Issue #26 — Graphify adapter boundary docs."""

from __future__ import annotations

import os

ROOT = os.path.dirname(os.path.dirname(__file__))
ADR = os.path.join(ROOT, "docs", "adr", "0002-graphify-context-fit-adapter.md")
README = os.path.join(ROOT, "README.md")


def read(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


class TestIssue26GraphifyBoundaryDocs:
    def test_adr_exists_and_defines_allowed_role(self) -> None:
        doc = read(ADR)

        assert "Graphify is an optional Context Fit evidence adapter" in doc
        assert "optional read-only local inventory / Context Fit evidence adapter" in doc
        assert "Graphify-derived LocalKnowledgeInventory" in doc
        assert "exact overlap" in doc
        assert "bounded-context warnings" in doc

    def test_adr_rejects_out_of_scope_graphify_adoption(self) -> None:
        doc = read(ADR)
        for rejected in [
            "Graphify install hooks",
            "committed `graphify-out/` artifacts",
            "Graphify MCP server dependency",
            "Graphify HTTP server dependency",
            "Graphify-generated wiki as the canonical serving layer",
            "Graphify as trust/provenance/freshness authority",
            "Graphify as install authority",
            "required dependency for basic `iknow` usage",
        ]:
            assert rejected in doc

    def test_adr_documents_private_data_handling_and_redaction(self) -> None:
        doc = read(ADR)

        assert "Private data handling" in doc
        assert "avoid absolute path leakage" in doc
        assert "/home/<user>/" in doc
        assert "/Users/<user>/" in doc
        assert "/root/" in doc
        assert "do not commit real private `graphify-out/` output" in doc
        assert "synthetic fixtures" in doc

    def test_adr_names_future_upgrade_paths_without_implementing_them(self) -> None:
        doc = read(ADR)

        assert "Future upgrade paths, not implemented now" in doc
        assert "Graphify `graph.json` adapter v2" in doc
        assert "Graphify MCP adapter" in doc
        assert "Graphify-generated wiki adapter" in doc
        assert "not current scope" in doc

    def test_readme_links_boundary_decision(self) -> None:
        readme = read(README)

        assert "docs/adr/0002-graphify-context-fit-adapter.md" in readme
        assert "Graphify adapter boundary decision" in readme
