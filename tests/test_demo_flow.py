"""End-to-end demo flow test for Issue #9 — Variant C.

Exercises the complete pipeline without network access:
  1. cookbook list         — find wikis
  2. cookbook inspect      — inspect scope & entry points
  3. fit                   — check local fit
  4. compile               — compile a private draft
  5. install               — install the draft
  6. serve search          — in-scope search (proof)
  7. serve search          — out-of-scope search (refusal)
  8. serve read            — read a document with citation path

All data comes from bundled fixtures — no network, no hosted backend.
"""

from __future__ import annotations

import os
import shutil
import sys

import pytest

from iknow.cli import main
from iknow.store import get_installed_store_path

# ---------------------------------------------------------------------------
# Path to the issue6 fixture (compiler test fixture with iknow.yaml + sources)
# ---------------------------------------------------------------------------
FIXTURE_DIR = os.path.join(os.path.dirname(__file__), "fixtures", "issue6")
YAML_PATH = os.path.join(FIXTURE_DIR, "iknow.yaml")


# ===========================================================================
# Variant C — full demo flow
# ===========================================================================


class TestVariantCDemoFlow:
    """Complete Variant C demo: find → fit → compile → install → serve.

    This preserves the order:
      Find wiki → Check fit → Choose entry point → Harmonize → Inspect proof/refusal.
    """

    @pytest.fixture(autouse=True)
    def _setup(self, tmp_path) -> None:
        """Set up a clean environment for the demo flow."""
        self.store_path = str(tmp_path / "installed")
        os.environ["IKNOW_INSTALLED_STORE"] = self.store_path
        # The compile step writes to FIXTURE_DIR/.kungfu/drafts/test-wiki/
        self.draft_dir = os.path.join(FIXTURE_DIR, ".kungfu", "drafts", "test-wiki")
        yield
        if "IKNOW_INSTALLED_STORE" in os.environ:
            del os.environ["IKNOW_INSTALLED_STORE"]
        if os.path.isdir(self.draft_dir):
            shutil.rmtree(self.draft_dir)
        if os.path.isdir(self.store_path):
            shutil.rmtree(self.store_path)

    # ---- Step 1: Find wiki ------------------------------------------------

    def test_step_01_cookbook_list(self, capsys) -> None:
        """``cookbook list`` — discover available wikis."""
        rc = main(["cookbook", "list"])
        assert rc == 0
        out = capsys.readouterr().out
        # Should see all three fixture wikis
        assert "agent_workflow_setup" in out
        assert "terminal_setup" in out
        assert "mcp_basics" in out
        # Should see trust states
        assert "Verified" in out
        assert "Official" in out
        assert "Community" in out

    # ---- Step 2: Inspect scope & entry points -----------------------------

    def test_step_02_cookbook_inspect(self, capsys) -> None:
        """``cookbook inspect agent_workflow_setup`` — inspect a wiki's contract."""
        rc = main(["cookbook", "inspect", "agent_workflow_setup"])
        assert rc == 0
        out = capsys.readouterr().out
        # Identity
        assert "Agent Workflow Setup Wiki" in out
        assert "1.0.0" in out
        # Scope
        assert "agent workflow design" in out
        assert "task delegation patterns" in out
        # Non-scope
        assert "model training" in out
        assert "RLHF fine-tuning" in out
        # Entry points
        assert "mcp" in out
        assert "llms.txt" in out
        assert "markdown" in out

    # ---- Step 3: Check local fit ------------------------------------------

    def test_step_03_fit_check(self, capsys) -> None:
        """``fit agent_workflow_setup`` — compare against default inventory."""
        rc = main(["fit", "agent_workflow_setup"])
        assert rc == 0
        out = capsys.readouterr().out
        # Should show a recommendation (the agent workflow wiki has new topics)
        assert "Recommendation:" in out
        assert "Merge risk:" in out
        assert "Gap:" in out
        # Should show harmonization options
        assert "Harmonization options:" in out
        assert "install" in out
        assert "skip" in out

    # ---- Step 3b: Check fit for out-of-scope ref-useful wiki (terminal_setup)

    def test_step_03b_fit_terminal_setup(self, capsys) -> None:
        """``fit terminal_setup`` — terminal wiki overlaps with inventory."""
        rc = main(["fit", "terminal_setup"])
        assert rc == 0
        out = capsys.readouterr().out
        assert "Recommendation:" in out
        assert "Harmonization options:" in out

    # ---- Step 3c: Check fit for mcp_basics (community wiki) ---------------

    def test_step_03c_fit_mcp_basics(self, capsys) -> None:
        """``fit mcp_basics`` — MCP wiki overlaps with inventory."""
        rc = main(["fit", "mcp_basics"])
        assert rc == 0
        out = capsys.readouterr().out
        assert "Recommendation:" in out

    # ---- Step 4: Compile a private draft ----------------------------------

    def test_step_04_compile(self, capsys) -> None:
        """``compile --config <iknow.yaml>`` — compile the test fixture wiki."""
        rc = main(["compile", "--config", YAML_PATH])
        assert rc == 0
        out = capsys.readouterr().out
        assert "Compiled wiki 'test-wiki'" in out
        assert ".kungfu/drafts/test-wiki" in out

    # ---- Step 5: Install the draft ----------------------------------------

    def test_step_05_install(self, capsys) -> None:
        """``install test-wiki`` — install compiled draft into the store."""
        # First compile
        rc = main(["compile", "--config", YAML_PATH])
        assert rc == 0
        capsys.readouterr()  # discard compile output

        # Now install
        rc = main([
            "install", "test-wiki",
            "--draft-dir", self.draft_dir,
            "--store-path", self.store_path,
        ])
        assert rc == 0
        out = capsys.readouterr().out
        assert "Installed wiki 'test-wiki'" in out

    # ---- Step 6: List installed wikis -------------------------------------

    def test_step_06_list_installed(self, capsys) -> None:
        """``list`` — show installed wikis."""
        # Compile + install
        main(["compile", "--config", YAML_PATH])
        capsys.readouterr()
        main([
            "install", "test-wiki",
            "--draft-dir", self.draft_dir,
            "--store-path", self.store_path,
        ])
        capsys.readouterr()

        rc = main(["list", "--store-path", self.store_path])
        assert rc == 0
        out = capsys.readouterr().out
        assert "test-wiki" in out
        assert "Test Wiki" in out

    # ---- Step 7: Serve — search in-scope (proof) --------------------------

    def test_step_07_serve_search_in_scope(self, capsys) -> None:
        """``serve search test-wiki testing`` — find in-scope content."""
        # Compile + install
        main(["compile", "--config", YAML_PATH])
        capsys.readouterr()
        main([
            "install", "test-wiki",
            "--draft-dir", self.draft_dir,
            "--store-path", self.store_path,
        ])
        capsys.readouterr()

        rc = main([
            "serve", "search", "test-wiki", "testing",
            "--store-path", self.store_path,
        ])
        assert rc == 0
        out = capsys.readouterr().out
        assert "Search results" in out
        assert "getting-started.md" in out
        assert "OUT-OF-SCOPE REFUSAL" not in out

    # ---- Step 8: Serve — search out-of-scope (refusal) --------------------

    def test_step_08_serve_search_out_of_scope(self, capsys) -> None:
        """``serve search test-wiki deployment`` — out-of-scope refusal."""
        # Compile + install
        main(["compile", "--config", YAML_PATH])
        capsys.readouterr()
        main([
            "install", "test-wiki",
            "--draft-dir", self.draft_dir,
            "--store-path", self.store_path,
        ])
        capsys.readouterr()

        rc = main([
            "serve", "search", "test-wiki", "deployment",
            "--store-path", self.store_path,
        ])
        assert rc == 0
        out = capsys.readouterr().out
        # "deployment" is in the non_scope list → should trigger refusal
        assert "OUT-OF-SCOPE REFUSAL" in out
        assert "explicitly listed as out of scope" in out
        assert "route this query" in out

    # ---- Step 9: Serve — read document with citation path -----------------

    def test_step_09_serve_read_document(self, capsys) -> None:
        """``serve read test-wiki getting-started.md`` — read with citation."""
        # Compile + install
        main(["compile", "--config", YAML_PATH])
        capsys.readouterr()
        main([
            "install", "test-wiki",
            "--draft-dir", self.draft_dir,
            "--store-path", self.store_path,
        ])
        capsys.readouterr()

        rc = main([
            "serve", "read", "test-wiki", "getting-started.md",
            "--store-path", self.store_path,
        ])
        assert rc == 0
        out = capsys.readouterr().out
        assert "Document:" in out
        assert "Path:" in out
        assert "Size:" in out

    # ---- Step 10: Serve — list installed (verify persistence) -------------

    def test_step_10_serve_list(self, capsys) -> None:
        """``serve list`` — detailed listing of installed wikis."""
        # Compile + install
        main(["compile", "--config", YAML_PATH])
        capsys.readouterr()
        main([
            "install", "test-wiki",
            "--draft-dir", self.draft_dir,
            "--store-path", self.store_path,
        ])
        capsys.readouterr()

        rc = main(["serve", "list", "--store-path", self.store_path])
        assert rc == 0
        out = capsys.readouterr().out
        assert "test-wiki" in out
        assert "Test Wiki" in out
        assert "✓" in out  # raw flag present


# ===========================================================================
# Demo script — runnable as ``python -m tests.test_demo_flow``
# ===========================================================================


def run_demo(store_path: str | None = None) -> int:
    """Run the full demo and print output to stdout.

    Returns 0 on success, 1 on failure.
    """
    import tempfile

    store = store_path or tempfile.mkdtemp(prefix="iknow_demo_")
    prev = os.environ.get("IKNOW_INSTALLED_STORE")
    os.environ["IKNOW_INSTALLED_STORE"] = store

    steps = [
        ("1. Cookbook — list available wikis",
         ["cookbook", "list"]),
        ("2. Cookbook — inspect Agent Workflow Setup Wiki",
         ["cookbook", "inspect", "agent_workflow_setup"]),
        ("3. Fit check — compare Agent Workflow Wiki vs local inventory",
         ["fit", "agent_workflow_setup"]),
        ("4. Compile — create a private draft from iknow.yaml",
         ["compile", "--config", YAML_PATH]),
        ("5. Install — install the compiled draft into the global store",
         ["install", "test-wiki"]),
        ("6. List installed wikis",
         ["list"]),
        ("7. Serve — search inside the installed wiki (in-scope query)",
         ["serve", "search", "test-wiki", "testing"]),
        ("8. Serve — search inside the installed wiki (out-of-scope query → refusal)",
         ["serve", "search", "test-wiki", "deployment"]),
        ("9. Serve — read a document with citation path",
         ["serve", "read", "test-wiki", "getting-started.md"]),
    ]

    failed = False
    for label, argv in steps:
        print(f"\n{'=' * 72}")
        print(f"  {label}")
        print(f"  $ iknow {' '.join(argv)}")
        print(f"{'=' * 72}")
        try:
            # Capture output and print it
            from io import StringIO
            old_out, old_err = sys.stdout, sys.stderr
            sys.stdout = StringIO()
            sys.stderr = StringIO()
            rc = main(argv)
            out = sys.stdout.getvalue()
            err = sys.stderr.getvalue()
            sys.stdout.close()
            sys.stderr.close()
            sys.stdout, sys.stderr = old_out, old_err
            print(out, end="")
            if err:
                print(f"[stderr] {err}", end="")
            if rc == 0:
                print(f"  → OK (exit {rc})")
            else:
                print(f"  → FAIL (exit {rc})")
                failed = True
        except Exception as exc:
            print(f"  → ERROR: {exc}")
            failed = True

    # Restore env
    if prev is not None:
        os.environ["IKNOW_INSTALLED_STORE"] = prev
    else:
        del os.environ["IKNOW_INSTALLED_STORE"]

    # Cleanup draft dir
    draft_dir = os.path.join(FIXTURE_DIR, ".kungfu")
    if os.path.isdir(draft_dir):
        shutil.rmtree(draft_dir)

    print(f"\n{'=' * 72}")
    if failed:
        print("  Demo completed with ERRORS.")
        return 1
    else:
        print("  Demo completed successfully!")
        return 0


if __name__ == "__main__":
    sys.exit(run_demo())