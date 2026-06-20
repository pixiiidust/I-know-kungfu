"""Issue #16 — real-data end-to-end Cookbook demo walkthrough.

Verifies the Phase 2 demo runs against the packaged wiki fixtures and proves:
inspect -> fit -> install/route -> serve/search/read -> cited answer -> refusal.
"""

from __future__ import annotations

import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(__file__))
SCRIPT = os.path.join(ROOT, "scripts", "phase2_real_data_demo.py")
DOC = os.path.join(ROOT, "docs", "demo", "phase2-real-data-cookbook.md")
README = os.path.join(ROOT, "README.md")


class TestIssue16RealDataDemo:
    def test_phase2_real_data_demo_script_runs_locally(self) -> None:
        result = subprocess.run(
            [sys.executable, SCRIPT],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
            timeout=60,
        )

        assert result.returncode == 0, result.stdout + result.stderr
        out = result.stdout
        assert "Phase 2 real-data Cookbook productization demo" in out
        assert "Local-first: no auth, no upload, no hosted backend, no network dependency." in out
        assert "Package:      agent-workflows" in out
        assert "Trust:        draft" in out
        assert "Recommendation:" in out
        assert "Exported 2 wiki(s)" in out
        assert "Installed wiki 'agent-workflows'" in out
        assert "Total hits:" in out
        assert "CITED ANSWER" in out
        assert "Citation:" in out
        assert "OUT-OF-SCOPE REFUSAL" in out
        assert "Phase 2 real-data demo completed successfully." in out

    def test_demo_documentation_points_to_single_command(self) -> None:
        with open(DOC, "r", encoding="utf-8") as f:
            doc = f.read()
        assert "python scripts/phase2_real_data_demo.py" in doc
        assert "tests/fixtures/phase2/" in doc
        assert "no auth" in doc
        assert "no hosted backend" in doc
        assert "no network" in doc
        assert "CITED ANSWER" in doc
        assert "OUT-OF-SCOPE REFUSAL" in doc

    def test_readme_links_real_data_path_without_replacing_existing_demo(self) -> None:
        with open(README, "r", encoding="utf-8") as f:
            readme = f.read()
        assert "python scripts/demo.py" in readme
        assert "python scripts/phase2_real_data_demo.py" in readme
        assert "docs/demo/phase2-real-data-cookbook.md" in readme
