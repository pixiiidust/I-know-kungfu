"""Issue #17 — Phase 2 boundaries and deferred backend docs."""

from __future__ import annotations

import os

ROOT = os.path.dirname(os.path.dirname(__file__))
PHASE2_DOC = os.path.join(ROOT, "docs", "roadmap", "phase2-real-data-productization.md")
PRD = os.path.join(ROOT, "docs", "PRD.md")
NOTES = os.path.join(ROOT, "prototype", "cookbook-serving", "NOTES.md")
README = os.path.join(ROOT, "README.md")


def read(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


class TestIssue17Phase2Boundaries:
    def test_phase2_doc_names_goal_proofs_deferred_work_and_issues(self) -> None:
        doc = read(PHASE2_DOC)
        assert "Real-data Cookbook productization" in doc
        assert "local/static productization" in doc
        assert "Phase 2 proves" in doc
        assert "Two real example knowledge base wikis" in doc
        assert "Generated static Cookbook registry data" in doc
        assert "Variant A" in doc
        assert "Deferred until a later phase" in doc
        for deferred in [
            "hosted marketplace backend",
            "publisher accounts or auth",
            "public uploads",
            "payments or monetization",
            "vector database retrieval or hosted RAG",
            "cloud MCP hosting",
        ]:
            assert deferred in doc
        for issue in ["#11", "#12", "#13", "#14", "#15", "#16", "#17"]:
            assert issue in doc

    def test_variant_a_is_recorded_and_variant_c_is_historical(self) -> None:
        prd = read(PRD)
        notes = read(NOTES)
        assert "Variant A is now the chosen UI surface for Phase 2" in prd
        assert "Variant C was the historical smell-test direction" in prd
        assert "continue from Variant A as the chosen surface" in notes
        assert "Older Variant C references are historical" in notes
        assert "restore the A/B/C switcher" in notes

    def test_readme_links_boundary_without_removing_existing_docs(self) -> None:
        readme = read(README)
        assert "docs/roadmap/phase2-real-data-productization.md" in readme
        assert "docs/PRD.md" in readme
        assert "prototype/cookbook-serving/NOTES.md" in readme
