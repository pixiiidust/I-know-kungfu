"""Graphify-backed Local Knowledge Inventory adapter.

This adapter treats Graphify output as read-only local evidence for Context Fit.
It does not assign trust, install anything, call Graphify, start servers, or make
network requests.
"""

from __future__ import annotations

import json
import os
import re
from collections import Counter, defaultdict
from pathlib import PurePosixPath
from typing import Any

from iknow.contracts.model import ServingEntryPoint, TrustState
from iknow.inventory.model import InventoryItem, LocalKnowledgeInventory

_BUILTIN_NOISE_LABELS = {
    "any",
    "bool",
    "bytes",
    "callable",
    "dict",
    "enum",
    "false",
    "float",
    "int",
    "list",
    "literal",
    "none",
    "object",
    "optional",
    "path",
    "str",
    "true",
    "tuple",
    "typing",
    "union",
}

_GENERATED_PATH_PARTS = {
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    "__pycache__",
    "build",
    "dist",
    "node_modules",
    "site-packages",
}

_FILE_LABEL_RE = re.compile(r"^[\w.-]+\.[A-Za-z0-9]+$")
MAX_GRAPH_BYTES = 10 * 1024 * 1024


def load_graphify_inventory(path: str) -> LocalKnowledgeInventory:
    """Load a Graphify ``graph.json`` file and derive local inventory evidence.

    Raises clear standard exceptions for CLI callers to render:
    ``FileNotFoundError`` for missing files, ``ValueError`` for oversized or
    unsupported schema, and ``json.JSONDecodeError`` for invalid JSON.
    """
    if not os.path.isfile(path):
        raise FileNotFoundError(path)
    size = os.path.getsize(path)
    if size > MAX_GRAPH_BYTES:
        raise ValueError(
            f"Graphify graph is too large ({size} bytes; max {MAX_GRAPH_BYTES} bytes)"
        )
    with open(path, "r", encoding="utf-8") as f:
        graph = json.load(f)
    _validate_graphify_graph_shape(graph)
    return inventory_from_graphify_graph(graph)


def _validate_graphify_graph_shape(graph: object) -> None:
    if not isinstance(graph, dict):
        raise ValueError("Unsupported Graphify graph schema: root must be a JSON object")
    if "nodes" not in graph:
        raise ValueError("Unsupported Graphify graph schema: missing 'nodes' list")
    if "links" not in graph and "edges" not in graph:
        raise ValueError("Unsupported Graphify graph schema: missing 'links' or 'edges' list")
    if not isinstance(graph.get("nodes"), list):
        raise ValueError("Unsupported Graphify graph schema: 'nodes' must be a list")
    edge_value = graph.get("links", graph.get("edges"))
    if not isinstance(edge_value, list):
        raise ValueError("Unsupported Graphify graph schema: edges must be a list")


def inventory_from_graphify_graph(graph: dict[str, Any]) -> LocalKnowledgeInventory:
    """Derive a LocalKnowledgeInventory from Graphify-style graph data.

    Expected input is the node-link JSON shape Graphify writes: ``nodes`` plus
    either ``links`` or ``edges``. Invalid or sparse graph records degrade to an
    empty inventory rather than raising, because this adapter is advisory fit
    evidence only.
    """
    raw_nodes = graph.get("nodes", [])
    raw_edges = graph.get("links", graph.get("edges", []))
    nodes = [node for node in raw_nodes if isinstance(node, dict)]
    edges = [edge for edge in raw_edges if isinstance(edge, dict)]

    degree_by_id = _degree_by_id(edges)
    confidence_counts = Counter(
        str(edge.get("confidence", "UNKNOWN")) for edge in edges if edge.get("confidence")
    )

    topics_by_community: dict[int, list[tuple[str, str, int]]] = defaultdict(list)
    seen_labels: set[str] = set()

    for node in nodes:
        label = str(node.get("label") or "").strip()
        source_file = _safe_source_path(str(node.get("source_file") or ""))
        if not _is_scope_candidate(label, source_file):
            continue

        normalized_label = _normalize_label(label)
        if normalized_label in seen_labels:
            continue
        seen_labels.add(normalized_label)

        community = _coerce_community(node.get("community"))
        degree = degree_by_id.get(str(node.get("id") or ""), 0)
        topics_by_community[community].append((label, source_file, degree))

    items = [
        _inventory_item_for_community(community, topics, confidence_counts)
        for community, topics in sorted(topics_by_community.items())
        if topics
    ]

    return LocalKnowledgeInventory(
        name="Graphify-derived Local Inventory",
        description=(
            "Local knowledge inventory derived from Graphify graph evidence. "
            "Use as fit evidence only; trust, provenance, freshness, and install "
            "decisions still come from Wiki Contracts."
        ),
        items=items,
    )


def _degree_by_id(edges: list[dict[str, Any]]) -> dict[str, int]:
    degree: Counter[str] = Counter()
    for edge in edges:
        source = edge.get("source")
        target = edge.get("target")
        if source:
            degree[str(source)] += 1
        if target:
            degree[str(target)] += 1
    return dict(degree)


def _inventory_item_for_community(
    community: int,
    topics: list[tuple[str, str, int]],
    confidence_counts: Counter[str],
) -> InventoryItem:
    sorted_topics = sorted(topics, key=lambda row: (-row[2], row[0].lower()))
    scope = [label for label, _source, _degree in sorted_topics]
    sources = sorted({source for _label, source, _degree in sorted_topics if source})
    max_degree = max((degree for _label, _source, degree in sorted_topics), default=0)
    confidence_summary = ", ".join(
        f"{name}={count}" for name, count in sorted(confidence_counts.items())
    ) or "none"
    source_summary = ", ".join(sources[:4]) if sources else "no source_file evidence"
    if len(sources) > 4:
        source_summary += f", +{len(sources) - 4} more"

    return InventoryItem(
        id=f"graphify_community_{community}",
        name=f"Graphify community {community}",
        description=(
            "Derived from Graphify graph evidence; "
            f"topics={len(scope)}, max_degree={max_degree}, "
            f"edge_confidence=({confidence_summary}), sources=({source_summary}). "
            "Evidence only — not a trust, provenance, freshness, or install claim."
        ),
        scope=scope,
        non_scope=[],
        entry_points=[ServingEntryPoint.MARKDOWN],
        trust_state=TrustState.COMMUNITY,
        evidence_sources={
            label: [source] if source else []
            for label, source, _degree in sorted_topics
        },
    )


def _is_scope_candidate(label: str, source_file: str) -> bool:
    if not label:
        return False
    normalized = _normalize_label(label)
    if normalized in _BUILTIN_NOISE_LABELS:
        return False
    if _FILE_LABEL_RE.match(label):
        return False
    if source_file:
        basename = os.path.basename(source_file)
        if label == basename:
            return False
        parts = set(source_file.split("/"))
        if parts & _GENERATED_PATH_PARTS:
            return False
    return True


def _normalize_label(label: str) -> str:
    return " ".join(label.lower().strip().split())


def _coerce_community(value: object) -> int:
    try:
        return int(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return 0


def _safe_source_path(source_file: str) -> str:
    """Return a local-safe, relative source path for evidence summaries."""
    source = source_file.replace("\\", "/").strip()
    if not source:
        return ""

    drive_match = re.match(r"^[A-Za-z]:/(.*)$", source)
    if drive_match:
        source = drive_match.group(1)

    # Drop leading slash and user/machine-specific prefixes. Keep the useful tail.
    source = source.lstrip("/")
    parts = [part for part in PurePosixPath(source).parts if part not in {"", "/"}]
    private_roots = {"home", "Users", "root"}
    for index, part in enumerate(parts):
        if part in private_roots and index + 2 < len(parts):
            parts = parts[index + 2 :]
            break

    return "/".join(parts)
