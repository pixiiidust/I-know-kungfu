"""Smoke tests for the iknow CLI entrypoint."""

import subprocess
import sys

from iknow.cli import build_parser, main


class TestCliHelp:
    """The CLI entrypoint can print help and version without errors."""

    def test_help_flag_prints_and_exits_ok(self, capsys) -> None:
        """``iknow --help`` exits 0 and prints usage."""
        try:
            main(["--help"])
        except SystemExit as exc:
            assert exc.code == 0, f"--help should exit 0, got {exc.code}"
        captured = capsys.readouterr()
        assert "usage: iknow" in captured.out

    def test_version_flag_prints_and_exits_ok(self, capsys) -> None:
        """``iknow --version`` exits 0 and prints version string."""
        try:
            main(["--version"])
        except SystemExit as exc:
            assert exc.code == 0, f"--version should exit 0, got {exc.code}"
        captured = capsys.readouterr()
        assert "iknow 0.1.0" in captured.out

    def test_no_args_prints_help_and_exits_ok(self, capsys) -> None:
        """``iknow`` with no args prints help and exits 0."""
        rc = main([])
        assert rc == 0
        captured = capsys.readouterr()
        assert "usage: iknow" in captured.out

    def test_python_module_entrypoint_prints_version(self) -> None:
        """``python -m iknow --version`` works from the source tree."""
        result = subprocess.run(
            [sys.executable, "-m", "iknow", "--version"],
            check=True,
            capture_output=True,
            text=True,
        )
        assert result.stdout.strip() == "iknow 0.1.0"

    def test_parser_builds_without_error(self) -> None:
        """The argument parser can be constructed without errors."""
        parser = build_parser()
        assert parser.prog == "iknow"
        assert parser.description is not None
