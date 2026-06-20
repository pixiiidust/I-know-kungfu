"""Export static Cookbook registry data from real packaged wiki artifacts.

This module compiles or reads already-compiled wiki packages and produces
a JSON export of the Cookbook registry that can be consumed by the
Variant A Cookbook UI without hardcoded package rows.

Usage::

    from iknow.cookbook.export import export_cookbook_registry

    result = export_cookbook_registry(
        wiki_dirs=["/path/to/compiled/wiki1", "/path/to/compiled/wiki2"],
        output_path="prototype/cookbook-serving/data/cookbook-registry.json",
    )
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from iknow.contracts.loader import load_from_dict
from iknow.contracts.model import TrustState
from iknow.validation.gates import check_listing_eligibility, check_recommendation_eligibility


# ---------------------------------------------------------------------------
# Derivation helpers for UI display fields
# ---------------------------------------------------------------------------


def _derive_route_recommendation(trust_state: str, publication: str) -> str:
    """Derive a simple route recommendation from trust state and publication.

    draft/private   → "local-draft"   (inspect-only, run locally)
    community/restricted → "review-before-install"
    community/public     → "review-before-install"
    verified/*     → "recommended"
    official/*     → "recommended"
    """
    ts = trust_state.strip().lower() if trust_state else ""
    pub = publication.strip().lower() if publication else ""

    if ts in ("verified", "official"):
        return "recommended"
    if ts == "community":
        return "review-before-install"
    if ts == "draft" and pub == "private":
        return "local-draft"
    if ts == "draft":
        return "local-draft"
    return "inspect-only"


def _derive_badge(trust_state: str, publication: str) -> str:
    """Derive a short badge label for Variant A UI display."""
    ts = trust_state.strip().lower() if trust_state else ""
    pub = publication.strip().lower() if publication else ""

    if ts == "official":
        return "Official"
    if ts == "verified":
        return "Verified"
    if ts == "community":
        suffix = " (Restricted)" if pub == "restricted" else ""
        return f"Community{suffix}"
    if ts == "draft":
        return "Draft"
    return ts.title() if trust_state else "Unknown"


def _derive_summary(description: str, max_chars: int = 120) -> str:
    """Derive a short display summary from the full description."""
    if not description:
        return ""
    if len(description) <= max_chars:
        return description
    return description[:max_chars].rsplit(" ", 1)[0] + "..."


# ---------------------------------------------------------------------------
# Core export logic
# ---------------------------------------------------------------------------


def _read_kb_json(wiki_dir: str) -> Optional[Dict[str, Any]]:
    """Read kb.json from a compiled wiki directory."""
    path = os.path.join(wiki_dir, "kb.json")
    if not os.path.isfile(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _read_index_json(wiki_dir: str) -> Optional[Dict[str, Any]]:
    """Read index.json from a compiled wiki directory."""
    path = os.path.join(wiki_dir, "index.json")
    if not os.path.isfile(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _build_contract_from_kb(kb: dict):
    """Build a WikiContract from a kb.json dict for eligibility checks."""
    trust_raw = kb.get("trust_state", "")
    trust_state = TrustState._missing_(trust_raw) if isinstance(trust_raw, str) else TrustState.COMMUNITY
    if trust_state is None:
        trust_state = TrustState.COMMUNITY

    from iknow.contracts.model import ServingEntryPoint, WikiContract

    entry_points_raw = kb.get("entry_points", [])
    entry_points = []
    if isinstance(entry_points_raw, list):
        for ep_raw in entry_points_raw:
            ep = ServingEntryPoint._missing_(ep_raw)
            if ep is not None:
                entry_points.append(ep)

    return WikiContract(
        name=kb.get("name", ""),
        description=kb.get("description", ""),
        version=kb.get("version", ""),
        scope=kb.get("scope", []),
        non_scope=kb.get("non_scope", []),
        provenance=kb.get("provenance", ""),
        freshness=kb.get("freshness", ""),
        license=kb.get("license", ""),
        trust_state=trust_state,
        entry_points=entry_points,
    )


def _empty_entry(wiki_id: str) -> Dict[str, Any]:
    """Return an empty/minimal wiki entry when kb.json is missing."""
    return {
        "id": wiki_id,
        "name": wiki_id,
        "description": "",
        "version": "",
        "trust_state": "",
        "publication": "",
        "maintainer": "",
        "license": "",
        "provenance": "",
        "freshness": "",
        "scope": [],
        "non_scope": [],
        "entry_points": [],
        "document_count": 0,
        "kb_json_path": "",
        "index_json_path": "",
        "llms_txt_path": "",
        "listing_eligible": False,
        "listing_blockers": ["kb.json not found"],
        "listing_warnings": [],
        "recommendation_eligible": False,
        "recommendation_blockers": ["kb.json not found"],
        "recommendation_warnings": [],
        "route_recommendation": "inspect-only",
        "badge": "Unknown",
        "summary": "",
    }


def _export_one_wiki(wiki_id: str, wiki_dir: str) -> Dict[str, Any]:
    """Build the export entry for a single compiled wiki directory.

    Parameters
    ----------
    wiki_id:
        The wiki identifier (used as the registry ID).
    wiki_dir:
        Path to the compiled wiki directory (containing kb.json, index.json, etc.).

    Returns
    -------
    dict
        A single wiki entry in the registry export format.
    """
    kb = _read_kb_json(wiki_dir)
    index = _read_index_json(wiki_dir)

    if kb is None:
        return _empty_entry(wiki_id)

    # Use wiki_id from kb.json if available, falling back to the directory name
    effective_id = kb.get("wiki_id", wiki_id)

    # Build stable package-relative artifact paths for static consumers.
    # The exported registry may be generated from temporary compiled dirs, so
    # do not leak absolute build-machine paths into the checked-in JSON.
    kb_json_path = f"packages/{effective_id}/kb.json"
    index_json_path = f"packages/{effective_id}/index.json"
    llms_txt_path = f"packages/{effective_id}/llms.txt"

    # Get document count from index.json
    document_count = 0
    if index and "total_documents" in index:
        document_count = index["total_documents"]
    elif kb.get("total_documents"):
        document_count = kb.get("total_documents", 0)

    # Build contract for eligibility checks
    contract = _build_contract_from_kb(kb)

    # Run eligibility gates
    listing_result = check_listing_eligibility(contract, wiki_dir=wiki_dir)
    recommendation_result = check_recommendation_eligibility(contract, wiki_dir=wiki_dir)

    # Get trust/publication as strings
    trust_state = str(kb.get("trust_state", ""))
    publication = str(kb.get("publication", ""))

    # Derive UI display fields
    route = _derive_route_recommendation(trust_state, publication)
    badge = _derive_badge(trust_state, publication)
    summary = _derive_summary(kb.get("description", ""))

    return {
        "id": effective_id,
        "name": kb.get("name", wiki_id),
        "description": kb.get("description", ""),
        "version": kb.get("version", ""),
        "trust_state": trust_state,
        "publication": publication,
        "maintainer": kb.get("maintainer", ""),
        "license": kb.get("license", ""),
        "provenance": kb.get("provenance", ""),
        "freshness": kb.get("freshness", ""),
        "scope": kb.get("scope", []),
        "non_scope": kb.get("non_scope", []),
        "entry_points": kb.get("entry_points", []),
        "document_count": document_count,
        "kb_json_path": kb_json_path,
        "index_json_path": index_json_path,
        "llms_txt_path": llms_txt_path,
        "listing_eligible": listing_result.passed,
        "listing_blockers": list(listing_result.blockers),
        "listing_warnings": list(listing_result.warnings),
        "recommendation_eligible": recommendation_result.passed,
        "recommendation_blockers": list(recommendation_result.blockers),
        "recommendation_warnings": list(recommendation_result.warnings),
        "route_recommendation": route,
        "badge": badge,
        "summary": summary,
    }


def export_cookbook_registry(
    wiki_dirs: List[str],
    output_path: Optional[str] = None,
) -> Dict[str, Any]:
    """Export static Cookbook registry data from compiled wiki directories.

    Parameters
    ----------
    wiki_dirs:
        List of paths to compiled wiki directories.  Each directory should
        contain at least ``kb.json`` and ``index.json``.
    output_path:
        If provided, the result is written to this JSON file.
        If ``None``, the result dict is returned without writing.

    Returns
    -------
    dict
        The exported registry data with version, export timestamp, and wikis
        list.  Each wiki entry contains display, contract, provenance,
        freshness, trust, eligibility, and route fields.

        Structure::

            {
                "version": 1,
                "exported_at": "2026-06-20T12:00:00Z",
                "wikis": [
                    {  # one per compiled wiki
                        "id": ...,
                        "name": ...,
                        "description": ...,
                        "version": ...,
                        "trust_state": ...,
                        "publication": ...,
                        "maintainer": ...,
                        "license": ...,
                        "provenance": ...,
                        "freshness": ...,
                        "scope": [...],
                        "non_scope": [...],
                        "entry_points": [...],
                        "document_count": ...,
                        "kb_json_path": ...,
                        "index_json_path": ...,
                        "llms_txt_path": ...,
                        "listing_eligible": true/false,
                        "listing_blockers": [...],
                        "listing_warnings": [...],
                        "recommendation_eligible": true/false,
                        "recommendation_blockers": [...],
                        "recommendation_warnings": [...],
                        "route_recommendation": "...",
                        "badge": "...",
                        "summary": "...",
                    },
                ],
            }
    """
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    wikis: List[Dict[str, Any]] = []
    for wiki_dir in wiki_dirs:
        # Derive wiki ID from directory name (last component)
        wiki_id = os.path.basename(os.path.normpath(wiki_dir))
        entry = _export_one_wiki(wiki_id, wiki_dir)
        wikis.append(entry)

    result: Dict[str, Any] = {
        "version": 1,
        "exported_at": now,
        "wikis": wikis,
    }

    if output_path is not None:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

    return result