"""Issue #24 — Graphify-backed fit demo data and walkthrough."""

from __future__ import annotations

import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(__file__))
DEMO_SCRIPT = os.path.join(ROOT, "scripts", "graphify_fit_demo.py")
WALKTHROUGH = os.path.join(ROOT, "docs", "demo", "graphify-backed-context-fit.md")
GRAPH_FIXTURE = os.path.join(ROOT, "tests", "fixtures", "graphify", "context_fit_graph.json")


def read(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


class TestIssue24GraphifyFitDemo:
    def test_demo_script_and_walkthrough_exist(self) -> None:
        assert os.path.isfile(DEMO_SCRIPT)
        assert os.path.isfile(WALKTHROUGH)
        assert os.path.isfile(GRAPH_FIXTURE)

    def test_demo_runs_locally_with_checked_in_synthetic_data(self) -> None:
        result = subprocess.run(
            [sys.executable, DEMO_SCRIPT],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )

        assert "Graphify-backed Context Fit demo" in result.stdout
        assert "tests/fixtures/graphify/context_fit_graph.json" in result.stdout
        assert "Graphify-backed fit demo completed successfully" in result.stdout

    def test_demo_output_shows_good_poor_and_boundary_risk_fits(self) -> None:
        result = subprocess.run(
            [sys.executable, DEMO_SCRIPT],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        out = result.stdout

        assert "GOOD FIT" in out
        assert "Recommendation: recommended_install" in out
        assert "POOR FIT" in out
        assert "Recommendation: findable_only" in out
        assert "BOUNDARY-RISK FIT" in out
        assert "Recommendation: route_with_care" in out
        assert "spans multiple local graph contexts" in out

    def test_demo_labels_synthetic_evidence_and_does_not_claim_trust(self) -> None:
        result = subprocess.run(
            [sys.executable, DEMO_SCRIPT],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        out = result.stdout

        assert "checked-in synthetic data" in out
        assert "synthetic local Graphify graph fixture" in out
        assert "does not prove trust" in out
        assert "no Graphify runtime" in out

    def test_walkthrough_documents_local_path_and_boundaries(self) -> None:
        doc = read(WALKTHROUGH)

        assert "checked-in synthetic Graphify graph" in doc
        assert "Graphify-derived LocalKnowledgeInventory" in doc
        assert "GOOD FIT" in doc
        assert "POOR FIT" in doc
        assert "BOUNDARY-RISK FIT" in doc
        assert "does **not** run Graphify" in doc
        assert "does **not** answer" in doc
        assert "trustworthy, or safe to install" in doc
