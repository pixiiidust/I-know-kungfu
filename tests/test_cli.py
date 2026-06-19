"""Smoke tests for the iknow CLI entrypoint.

Covers:
- --help and --version flags
- cookbook list / inspect
- fit
- compile
- install
- serve list / search / read
"""

import json
import os
import shutil
import subprocess
import sys

import pytest

from iknow.cli import build_parser, main
from iknow.compiler import compile_draft
from iknow.store import get_installed_store_path


# ===========================================================================
# Fixtures
# ===========================================================================

FIXTURE_DIR = os.path.join(os.path.dirname(__file__), "fixtures", "issue6")
YAML_PATH = os.path.join(FIXTURE_DIR, "iknow.yaml")


# ===========================================================================
# Help & version
# ===========================================================================


class TestCliHelp:
    """The CLI entrypoint can print help and version without errors."""

    def test_help_flag_prints_and_exits_ok(self, capsys) -> None:
        try:
            main(["--help"])
        except SystemExit as exc:
            assert exc.code == 0, f"--help should exit 0, got {exc.code}"
        captured = capsys.readouterr()
        assert "usage: iknow" in captured.out

    def test_version_flag_prints_and_exits_ok(self, capsys) -> None:
        try:
            main(["--version"])
        except SystemExit as exc:
            assert exc.code == 0, f"--version should exit 0, got {exc.code}"
        captured = capsys.readouterr()
        assert "iknow 0.1.0" in captured.out

    def test_no_args_prints_help_and_exits_ok(self, capsys) -> None:
        rc = main([])
        assert rc == 0
        captured = capsys.readouterr()
        assert "usage: iknow" in captured.out

    def test_python_module_entrypoint_prints_version(self) -> None:
        result = subprocess.run(
            [sys.executable, "-m", "iknow", "--version"],
            check=True,
            capture_output=True,
            text=True,
        )
        assert result.stdout.strip() == "iknow 0.1.0"

    def test_parser_builds_without_error(self) -> None:
        parser = build_parser()
        assert parser.prog == "iknow"
        assert parser.description is not None


# ===========================================================================
# cookbook list
# ===========================================================================


class TestCookbookList:
    """``cookbook list`` lists registry wikis."""

    def test_list_prints_three_wikis(self, capsys) -> None:
        rc = main(["cookbook", "list"])
        assert rc == 0
        captured = capsys.readouterr()
        assert "agent_workflow_setup" in captured.out
        assert "terminal_setup" in captured.out
        assert "mcp_basics" in captured.out
        assert "Wiki ID" in captured.out  # header

    def test_list_shows_trust_states(self, capsys) -> None:
        rc = main(["cookbook", "list"])
        assert rc == 0
        captured = capsys.readouterr()
        assert "Verified" in captured.out
        assert "Official" in captured.out
        assert "Community" in captured.out


# ===========================================================================
# cookbook inspect
# ===========================================================================


class TestCookbookInspect:
    """``cookbook inspect <wiki-id>`` shows contract details."""

    def test_inspect_known_wiki(self, capsys) -> None:
        rc = main(["cookbook", "inspect", "agent_workflow_setup"])
        assert rc == 0
        captured = capsys.readouterr()
        assert "Agent Workflow Setup Wiki" in captured.out
        assert "Scope:" in captured.out
        assert "Non-scope" in captured.out
        assert "agent workflow design" in captured.out
        assert "Entry points" in captured.out

    def test_inspect_unknown_wiki_returns_error(self, capsys) -> None:
        rc = main(["cookbook", "inspect", "nonexistent"])
        assert rc == 1
        captured = capsys.readouterr()
        assert "not found" in captured.err


# ===========================================================================
# fit
# ===========================================================================


class TestFit:
    """``fit <wiki-id>`` checks context fit against default inventory."""

    def test_fit_known_wiki_returns_recommendation(self, capsys) -> None:
        rc = main(["fit", "agent_workflow_setup"])
        assert rc == 0
        captured = capsys.readouterr()
        # The agent workflow wiki has topics not in the default inventory
        assert "Recommendation:" in captured.out
        assert "Merge risk:" in captured.out
        assert "Gap:" in captured.out
        assert "Harmonization options:" in captured.out

    def test_fit_unknown_wiki_returns_error(self, capsys) -> None:
        rc = main(["fit", "nonexistent"])
        assert rc == 1
        captured = capsys.readouterr()
        assert "not found" in captured.err


# ===========================================================================
# compile
# ===========================================================================


class TestCompileCli:
    """``compile --config iknow.yaml`` compiles a draft."""

    def test_compile_success(self, capsys) -> None:
        rc = main(["compile", "--config", YAML_PATH])
        assert rc == 0
        captured = capsys.readouterr()
        assert "Compiled" in captured.out
        assert "test-wiki" in captured.out
        assert ".kungfu/drafts/test-wiki" in captured.out
        # Clean up
        draft_dir = os.path.join(FIXTURE_DIR, ".kungfu")
        if os.path.isdir(draft_dir):
            shutil.rmtree(draft_dir)

    def test_compile_missing_config(self, capsys) -> None:
        rc = main(["compile", "--config", "/nonexistent/iknow.yaml"])
        assert rc == 1
        captured = capsys.readouterr()
        assert "not found" in captured.err


# ===========================================================================
# install & list (installed) & remove
# ===========================================================================


class TestInstallListRemove:
    """``install <wiki-id>``, ``list``, and ``remove``."""

    @pytest.fixture(autouse=True)
    def _setup_compile(self, tmp_path) -> None:
        """Compile the test wiki into a temp location so we can install it."""
        self.tmp_store = str(tmp_path / "store")
        os.environ["IKNOW_INSTALLED_STORE"] = self.tmp_store

        # Compile the fixture wiki
        result = compile_draft(YAML_PATH, base_dir=FIXTURE_DIR)
        assert result.success
        self.draft_dir = result.draft_dir

        yield

        # Cleanup
        if "IKNOW_INSTALLED_STORE" in os.environ:
            del os.environ["IKNOW_INSTALLED_STORE"]
        if os.path.isdir(self.draft_dir):
            shutil.rmtree(self.draft_dir)

    def test_install_success(self, capsys) -> None:
        rc = main(["install", "test-wiki", "--draft-dir", self.draft_dir,
                    "--store-path", self.tmp_store])
        assert rc == 0
        captured = capsys.readouterr()
        assert "Installed" in captured.out
        assert "test-wiki" in captured.out

    def test_list_installed(self, capsys) -> None:
        # Install first
        main(["install", "test-wiki", "--draft-dir", self.draft_dir,
              "--store-path", self.tmp_store])
        rc = main(["list", "--store-path", self.tmp_store])
        assert rc == 0
        captured = capsys.readouterr()
        assert "test-wiki" in captured.out

    def test_install_no_draft(self, capsys) -> None:
        rc = main(["install", "nonexistent", "--store-path", self.tmp_store])
        assert rc == 1
        captured = capsys.readouterr()
        assert "not found" in captured.err


# ===========================================================================
# serve
# ===========================================================================


class TestServe:
    """``serve {list|search|read}`` over installed wikis."""

    @pytest.fixture(autouse=True)
    def _setup_install(self, tmp_path) -> None:
        self.tmp_store = str(tmp_path / "store")
        os.environ["IKNOW_INSTALLED_STORE"] = self.tmp_store

        # Compile and install
        result = compile_draft(YAML_PATH, base_dir=FIXTURE_DIR)
        assert result.success
        self.draft_dir = result.draft_dir

        from iknow.store import install_draft
        install_result = install_draft(
            draft_dir=self.draft_dir,
            wiki_id="test-wiki",
            store_path=self.tmp_store,
        )
        assert install_result.success

        yield

        if "IKNOW_INSTALLED_STORE" in os.environ:
            del os.environ["IKNOW_INSTALLED_STORE"]
        if os.path.isdir(self.draft_dir):
            shutil.rmtree(self.draft_dir)
        store_path = get_installed_store_path(override=self.tmp_store)
        if os.path.isdir(store_path):
            shutil.rmtree(store_path)

    def test_serve_list(self, capsys) -> None:
        rc = main(["serve", "list", "--store-path", self.tmp_store])
        assert rc == 0
        captured = capsys.readouterr()
        assert "test-wiki" in captured.out
        assert "Test Wiki" in captured.out

    def test_serve_search_in_scope(self, capsys) -> None:
        rc = main(["serve", "search", "test-wiki", "testing",
                    "--store-path", self.tmp_store])
        assert rc == 0
        captured = capsys.readouterr()
        assert "Search results" in captured.out
        assert "getting-started.md" in captured.out

    def test_serve_search_out_of_scope(self, capsys) -> None:
        """Search for something listed in non_scope should trigger refusal."""
        rc = main(["serve", "search", "test-wiki", "deployment",
                    "--store-path", self.tmp_store])
        assert rc == 0
        captured = capsys.readouterr()
        assert "OUT-OF-SCOPE REFUSAL" in captured.out

    def test_serve_read_document(self, capsys) -> None:
        rc = main(["serve", "read", "test-wiki", "getting-started.md",
                    "--store-path", self.tmp_store])
        assert rc == 0
        captured = capsys.readouterr()
        assert "Document:" in captured.out
        assert "Size:" in captured.out


# ===========================================================================
# Unknown command
# ===========================================================================


class TestUnknownCommand:
    """Unknown subcommands exit with error code 2 (argparse)."""

    def test_unknown_command(self, capsys) -> None:
        try:
            main(["bogus"])
        except SystemExit as exc:
            assert exc.code == 2
        captured = capsys.readouterr()
        assert "invalid choice" in captured.err
