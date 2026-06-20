#!/usr/bin/env python3
"""Phase 2 real-data Cookbook walkthrough.

Runs the local-first product path against the Phase 2 packaged wiki fixtures:
inspect -> fit check -> install/route -> serve/search/read -> cited answer -> refusal.

Usage:
    python scripts/phase2_real_data_demo.py
"""

from __future__ import annotations

import contextlib
import io
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

from iknow.cli import main as iknow_main  # noqa: E402
from iknow.contracts.loader import load_from_dict  # noqa: E402
from iknow.fit import compute_fit  # noqa: E402
from iknow.inventory import get_inventory  # noqa: E402
from iknow.serving import read_document, search_wiki  # noqa: E402

PHASE2_FIXTURES = ROOT / "tests" / "fixtures" / "phase2"
PACKAGES = {
    "agent-workflows": PHASE2_FIXTURES / "agent-workflows" / "iknow.yaml",
    "ai-native-product-surfaces": PHASE2_FIXTURES / "ai-native-product-surfaces" / "iknow.yaml",
}


def run_cli(argv: list[str]) -> tuple[int, str, str]:
    """Run an iknow CLI command in-process and capture stdout/stderr."""
    old_out, old_err = sys.stdout, sys.stderr
    stdout, stderr = io.StringIO(), io.StringIO()
    sys.stdout, sys.stderr = stdout, stderr
    try:
        try:
            rc = iknow_main(argv)
        except SystemExit as exc:
            rc = int(exc.code or 0)
        return rc, stdout.getvalue(), stderr.getvalue()
    finally:
        sys.stdout, sys.stderr = old_out, old_err


def step(title: str) -> None:
    print("\n" + "=" * 78)
    print(title)
    print("=" * 78)


def show_command(argv: list[str]) -> tuple[int, str, str]:
    print("$ iknow " + " ".join(argv))
    rc, out, err = run_cli(argv)
    if out:
        print(out, end="")
    if err:
        print("[stderr] " + err, end="")
    print(f"→ exit {rc}")
    return rc, out, err


def load_kb(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def first_hit_path(search_result: dict) -> str:
    hits = search_result.get("hits", [])
    if not hits:
        raise RuntimeError("Expected at least one search hit in real-data demo")
    return str(hits[0]["document_path"])


def main() -> int:
    print("Phase 2 real-data Cookbook productization demo")
    print("Local-first: no auth, no upload, no hosted backend, no network dependency.")

    temp_root = Path(tempfile.mkdtemp(prefix="iknow_phase2_demo_"))
    previous_store = os.environ.get("IKNOW_INSTALLED_STORE")
    os.environ["IKNOW_INSTALLED_STORE"] = str(temp_root / "installed")

    failed = False
    try:
        draft_dirs: dict[str, Path] = {}

        step("1. Compile real Phase 2 packaged wikis")
        for wiki_id, config in PACKAGES.items():
            out_dir = temp_root / "drafts" / wiki_id
            rc, _, _ = show_command([
                "compile",
                "--config",
                str(config),
                "--output-dir",
                str(out_dir),
            ])
            failed = failed or rc != 0
            draft_dirs[wiki_id] = out_dir

        step("2. Inspect real package contract")
        kb = load_kb(draft_dirs["agent-workflows"] / "kb.json")
        contract = load_from_dict(kb)
        print("Package:      agent-workflows")
        print(f"Name:         {contract.name}")
        print(f"Trust:        {kb.get('trust_state', contract.trust_state.value)}")
        print(f"Freshness:    {contract.freshness}")
        print(f"Entry points: {', '.join(kb.get('entry_points', []))}")
        print("Scope sample:")
        for topic in contract.scope[:4]:
            print(f"  - {topic}")
        print("Non-scope sample:")
        for topic in contract.non_scope[:2]:
            print(f"  - {topic}")

        step("3. Fit check against local inventory")
        fit_result = compute_fit(contract, get_inventory(), candidate_id="agent-workflows")
        fit = fit_result.fit
        print(f"Candidate:      {fit_result.candidate_name} ({fit_result.candidate_id})")
        print(f"Inventory:      {fit_result.inventory_name}")
        print(f"Recommendation: {fit.recommendation.value}")
        print(f"Merge risk:     {fit.merge_risk}")
        print(f"Gap:            {fit.gap_percentage:.0%} of scope topics are new")
        print("Route decision: install locally, then serve bounded search/read/cite/refuse.")

        step("4. Export generated static Cookbook registry")
        registry_out = temp_root / "cookbook-registry.json"
        export_args = ["cookbook", "export", "--output", str(registry_out)]
        for draft_dir in draft_dirs.values():
            export_args.extend(["--package", str(draft_dir)])
        rc, _, _ = show_command(export_args)
        failed = failed or rc != 0

        step("5. Install/route agent-workflows into a temp local store")
        rc, _, _ = show_command([
            "install",
            "agent-workflows",
            "--draft-dir",
            str(draft_dirs["agent-workflows"]),
            "--store-path",
            os.environ["IKNOW_INSTALLED_STORE"],
        ])
        failed = failed or rc != 0
        rc, _, _ = show_command(["serve", "list", "--store-path", os.environ["IKNOW_INSTALLED_STORE"]])
        failed = failed or rc != 0

        step("6. Serve/search/read: cited answer from installed real package")
        query = "Knowledge Pack Routing"
        search_result = search_wiki(
            "agent-workflows",
            query,
            store_path=os.environ["IKNOW_INSTALLED_STORE"],
            max_results=3,
        )
        print(f"$ iknow serve search agent-workflows {query!r}")
        print(f"Total hits: {search_result.get('total_hits', 0)}")
        if search_result.get("out_of_scope"):
            print(search_result["out_of_scope_detail"])
            failed = True
        else:
            for i, hit in enumerate(search_result.get("hits", []), start=1):
                print(f"  [{i}] {hit['title']} — {hit['document_path']}")
                print(f"      {hit.get('snippet', '')[:160]}")

        doc_path = first_hit_path(search_result)
        read_result = read_document(
            "agent-workflows",
            doc_path,
            store_path=os.environ["IKNOW_INSTALLED_STORE"],
        )
        if read_result.get("error"):
            print("Read error:", read_result["error"])
            failed = True
        else:
            print("\nCITED ANSWER")
            print(
                "Knowledge Pack Routing keeps agents on bounded, source-backed "
                "entrypoints instead of wandering broad notes or web search."
            )
            print(f"Citation: {read_result['citation_path']}")
            print(f"Source title: {read_result['title']}")

        step("7. Refuse out-of-scope using the same installed package")
        refusal_query = "Product case studies"
        refusal = search_wiki(
            "agent-workflows",
            refusal_query,
            store_path=os.environ["IKNOW_INSTALLED_STORE"],
            max_results=3,
        )
        print(f"$ iknow serve search agent-workflows {refusal_query!r}")
        if refusal.get("out_of_scope"):
            print("OUT-OF-SCOPE REFUSAL")
            print(refusal["out_of_scope_detail"])
        else:
            print("Expected refusal, but query was not marked out of scope.")
            failed = True

        step("Result")
        if failed:
            print("Phase 2 real-data demo completed with errors.")
            return 1
        print("Phase 2 real-data demo completed successfully.")
        print(f"Temp store used: {os.environ['IKNOW_INSTALLED_STORE']}")
        print("All artifacts stayed local and temporary.")
        return 0
    finally:
        if previous_store is None:
            os.environ.pop("IKNOW_INSTALLED_STORE", None)
        else:
            os.environ["IKNOW_INSTALLED_STORE"] = previous_store
        with contextlib.suppress(OSError):
            shutil.rmtree(temp_root)


if __name__ == "__main__":
    raise SystemExit(main())
