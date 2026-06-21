#!/usr/bin/env python3
"""Graphify-backed Context Fit deterministic demo.

Shows the local path:
synthetic Graphify graph -> derived inventory -> candidate wiki fit ->
overlap/gaps/boundary warnings/evidence sources/recommendation.

Usage:
    python scripts/graphify_fit_demo.py
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

from iknow.contracts.model import ServingEntryPoint, TrustState, WikiContract  # noqa: E402
from iknow.fit import compute_fit  # noqa: E402
from iknow.inventory import load_graphify_inventory  # noqa: E402

GRAPH_FIXTURE = ROOT / "tests" / "fixtures" / "graphify" / "context_fit_graph.json"


def candidate(name: str, scope: list[str], non_scope: list[str] | None = None) -> WikiContract:
    return WikiContract(
        name=name,
        description=f"Synthetic demo candidate: {name}.",
        version="1.0.0",
        scope=scope,
        non_scope=non_scope or [],
        provenance="synthetic-demo",
        freshness="2026-06-21",
        license="MIT",
        trust_state=TrustState.VERIFIED,
        entry_points=[ServingEntryPoint.MARKDOWN],
    )


def print_fit(label: str, contract: WikiContract) -> None:
    inventory = load_graphify_inventory(str(GRAPH_FIXTURE))
    result = compute_fit(contract, inventory, candidate_id=label)
    fit = result.fit

    print("\n" + "=" * 78)
    print(f"{label}: {contract.name}")
    print("=" * 78)
    print("Evidence source: synthetic local Graphify graph fixture")
    print("Trust note: Graphify evidence is local fit evidence only; it does not prove trust.")
    print(f"Inventory:      {result.inventory_name}")
    print(f"Recommendation: {fit.recommendation.value}")
    print(f"Merge risk:     {fit.merge_risk}")
    print(f"Gap:            {fit.gap_percentage:.0%} of candidate scope remains non-exact")

    print("Exact overlap:")
    for topic in fit.overlapping_topics or ["None"]:
        print(f"  - {topic}")

    print("Graph evidence overlap:")
    for topic in fit.graph_evidence_topics or ["None"]:
        print(f"  - {topic}")

    print("Gaps:")
    for topic in fit.gap_topics or ["None"]:
        print(f"  - {topic}")

    print("Boundary warnings:")
    for warning in fit.boundary_warnings or ["None"]:
        print(f"  - {warning}")

    print("Evidence sources:")
    for source in fit.evidence_sources[:6] or ["None"]:
        print(f"  - {source}")


def main() -> int:
    print("Graphify-backed Context Fit demo")
    print("Local-only: checked-in synthetic data, no private files, no Graphify runtime.")
    print(f"Graph fixture: {GRAPH_FIXTURE.relative_to(ROOT)}")

    scenarios = [
        (
            "GOOD FIT",
            candidate("MCP Serving Fit", ["MCP Server Development"]),
        ),
        (
            "POOR FIT",
            candidate("Rust Compiler Internals", ["Rust compiler internals"]),
        ),
        (
            "BOUNDARY-RISK FIT",
            candidate(
                "Cross-context Cookbook Candidate",
                ["Knowledge Pack Routing", "Product Case Studies"],
            ),
        ),
    ]
    for label, contract in scenarios:
        print_fit(label, contract)

    print("\nResult: Graphify-backed fit demo completed successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
