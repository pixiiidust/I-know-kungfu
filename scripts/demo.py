#!/usr/bin/env python3
"""
End-to-end Demo: Variant C CLI Flow
====================================

This script exercises the complete I-know-kungfu CLI pipeline
without any network access, using only bundled fixtures.

Usage:
    python scripts/demo.py

This demonstrates the Variant C flow:
  find wiki → check fit → choose entry point → harmonize → inspect proof/refusal
"""

from __future__ import annotations

import os
import shutil
import sys
import tempfile

# Ensure the package is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from iknow.cli import main

FIXTURE_DIR = os.path.join(os.path.dirname(__file__), "..", "tests", "fixtures", "issue6")
YAML_PATH = os.path.join(FIXTURE_DIR, "iknow.yaml")


def run(argv: list[str]) -> tuple[int, str, str]:
    """Run a CLI command and return (exit_code, stdout, stderr)."""
    from io import StringIO

    old_out, old_err = sys.stdout, sys.stderr
    sys.stdout = StringIO()
    sys.stderr = StringIO()
    try:
        rc = main(argv)
    except SystemExit as exc:
        rc = int(exc.code) if exc.code is not None else 0
    out = sys.stdout.getvalue()
    err = sys.stderr.getvalue()
    sys.stdout.close()
    sys.stderr.close()
    sys.stdout, sys.stderr = old_out, old_err
    return rc, out, err


def main_demo() -> int:
    store = tempfile.mkdtemp(prefix="iknow_demo_")
    os.environ["IKNOW_INSTALLED_STORE"] = store

    # Draft output path (known from compile step)
    draft_dir = os.path.join(FIXTURE_DIR, ".kungfu", "drafts", "test-wiki")

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
         ["install", "test-wiki",
          "--draft-dir", draft_dir,
          "--store-path", store]),
        ("6. List installed wikis",
         ["list", "--store-path", store]),
        ("7. Serve — search inside the installed wiki (in-scope)",
         ["serve", "search", "test-wiki", "testing", "--store-path", store]),
        ("8. Serve — search inside the installed wiki (out-of-scope → refusal)",
         ["serve", "search", "test-wiki", "deployment", "--store-path", store]),
        ("9. Serve — read a document with citation path",
         ["serve", "read", "test-wiki", "getting-started.md", "--store-path", store]),
    ]

    failed = False
    for label, argv in steps:
        print(f"\n{'=' * 72}")
        print(f"  {label}")
        print(f"  $ iknow {' '.join(argv)}")
        print(f"{'=' * 72}")
        rc, out, err = run(argv)
        print(out, end="")
        if err:
            print(f"[stderr] {err}", end="")
        if rc == 0:
            print(f"\n  → OK (exit {rc})")
        else:
            print(f"\n  → FAIL (exit {rc})")
            failed = True

    # Cleanup
    if os.environ.get("IKNOW_INSTALLED_STORE") == store:
        del os.environ["IKNOW_INSTALLED_STORE"]
    if os.path.isdir(store):
        shutil.rmtree(store)
    if os.path.isdir(draft_dir):
        shutil.rmtree(os.path.dirname(os.path.dirname(draft_dir)))  # .kungfu/

    print(f"\n{'=' * 72}")
    if failed:
        print("  Demo completed with ERRORS.")
        return 1
    else:
        print("  Demo completed successfully!")
        return 0


if __name__ == "__main__":
    sys.exit(main_demo())