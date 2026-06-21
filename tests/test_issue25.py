"""Issue #25 — Cookbook UI renders Graphify-backed fit fields."""

from __future__ import annotations

import json
import os
import re
import subprocess
import tempfile

ROOT = os.path.dirname(os.path.dirname(__file__))
INDEX_HTML = os.path.join(ROOT, "prototype", "cookbook-serving", "index.html")
REGISTRY_JSON = os.path.join(ROOT, "prototype", "cookbook-serving", "data", "cookbook-registry.json")


def read(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def registry() -> dict:
    with open(REGISTRY_JSON, "r", encoding="utf-8") as f:
        return json.load(f)


class TestIssue25GraphifyFitUiData:
    def test_registry_contains_graphify_context_fit_fields(self) -> None:
        data = registry()
        assert data["wikis"]
        for wiki in data["wikis"]:
            fit = wiki.get("context_fit")
            assert fit, f"{wiki['id']} missing context_fit"
            for field in [
                "evidence_label",
                "source",
                "recommendation",
                "merge_risk",
                "exact_overlap",
                "graph_evidence_overlap",
                "gaps",
                "boundary_warnings",
                "evidence_sources",
                "trust_boundary",
            ]:
                assert field in fit, f"{wiki['id']} missing context_fit.{field}"
            assert "Synthetic/demo Graphify-backed" in fit["evidence_label"]
            assert "Graphify evidence supports local fit only" in fit["trust_boundary"]

    def test_registry_has_boundary_risk_and_empty_safe_shapes(self) -> None:
        data = registry()
        fits = [wiki["context_fit"] for wiki in data["wikis"]]

        assert any(fit["boundary_warnings"] for fit in fits)
        assert any(fit["exact_overlap"] for fit in fits)
        assert any(fit["graph_evidence_overlap"] for fit in fits)
        assert any(fit["gaps"] for fit in fits)

    def test_index_renders_graphify_fit_panel_fields_and_empty_state(self) -> None:
        html = read(INDEX_HTML)

        assert "contextFit" in html
        assert "fitTerms" in html
        assert "Exact overlap" in html
        assert "Graph evidence" in html
        assert "Boundary warnings" in html
        assert "Evidence sources" in html
        assert "No local graph evidence" in html
        assert "Graphify evidence does not prove official status" in html
        assert "Wiki Contract fields still govern trust and install decisions" in html
        assert "Graphify evidence supports local fit only; Wiki Contract fields still govern trust" in read(REGISTRY_JSON)

    def test_ui_copy_does_not_claim_graphify_proves_trust(self) -> None:
        html = read(INDEX_HTML)
        forbidden = [
            "Graphify proves trust",
            "Graphify proves provenance",
            "Graphify proves freshness",
            "Graphify proves official",
        ]
        for phrase in forbidden:
            assert phrase not in html

    def test_inline_script_is_valid_javascript(self) -> None:
        html = read(INDEX_HTML)
        match = re.search(r"<script>(.*)</script>", html, re.DOTALL)
        assert match, "inline script not found"
        with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as f:
            f.write(match.group(1))
            script_path = f.name
        try:
            result = subprocess.run(
                ["node", "--check", script_path],
                capture_output=True,
                text=True,
            )
            assert result.returncode == 0, result.stderr
        finally:
            os.unlink(script_path)
