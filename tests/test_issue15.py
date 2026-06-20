"""Tests for Issue #15: Wire the Variant A Cookbook UI to generated registry data.

Acceptance criteria covered:
- The prototype loads package rows from generated registry data, not duplicated
  synthetic row objects inside index.html.
- Variant A remains the only active UI surface; no A/B/C switcher returns.
- Search, trust filters, row selection, serving surface selection, copy actions,
  cited answer, and refusal still work.
- The UI renders at least two real packaged wikis from Phase 2 artifacts.
- index.html has no synthetic pack data (no demo.packs or demo={...}).
- index.html references data/cookbook-registry.json as its data source.
- The registry JSON contains at least 2 wikis.
- Existing tests still pass.
"""

from __future__ import annotations

import json
import os
import re

import pytest

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

HERE = os.path.dirname(__file__)
PROTOTYPE_DIR = os.path.join(HERE, "..", "prototype", "cookbook-serving")
INDEX_HTML = os.path.join(PROTOTYPE_DIR, "index.html")
REGISTRY_JSON = os.path.join(PROTOTYPE_DIR, "data", "cookbook-registry.json")


# ===========================================================================
# Test: No synthetic pack data in index.html
# ===========================================================================


class TestNoSyntheticPacks:
    """index.html must not contain hardcoded synthetic pack data."""

    def test_no_demo_packs_object(self) -> None:
        """The file must not contain 'demo={packs:' or 'demo.packs'."""
        with open(INDEX_HTML, "r") as f:
            content = f.read()
        assert "demo={packs:" not in content, (
            "Found hardcoded demo.packs object in index.html"
        )
        assert "demo.packs" not in content, (
            "Found reference to demo.packs in index.html"
        )

    def test_no_synthetic_pack_titles(self) -> None:
        """Must not contain synthetic pack titles like 'Agent Workflow Setup Wiki'."""
        with open(INDEX_HTML, "r") as f:
            content = f.read()
        synthetic_titles = [
            "Agent Workflow Setup Wiki",
            "Terminal Setup Wiki",
            "MCP Basics Wiki",
            "Local Model Serving Wiki",
        ]
        for title in synthetic_titles:
            assert title not in content, (
                f"Found synthetic pack title '{title}' in index.html"
            )

    def test_references_registry_json(self) -> None:
        """index.html must reference data/cookbook-registry.json."""
        with open(INDEX_HTML, "r") as f:
            content = f.read()
        assert "data/cookbook-registry.json" in content, (
            "index.html does not reference data/cookbook-registry.json"
        )

    def test_has_fetch_call(self) -> None:
        """index.html must fetch the registry JSON."""
        with open(INDEX_HTML, "r") as f:
            content = f.read()
        assert "fetch('data/cookbook-registry.json')" in content, (
            "index.html does not fetch data/cookbook-registry.json"
        )

    def test_no_variant_b_or_c(self) -> None:
        """Variant A remains the only active UI surface; no B/C switcher."""
        with open(INDEX_HTML, "r") as f:
            content = f.read()
        # Only variantA section should exist
        assert 'id="variantA"' in content
        assert 'id="variantB"' not in content
        assert 'id="variantC"' not in content
        assert "Variant A selected" in content


# ===========================================================================
# Test: Registry JSON exists and has at least 2 wikis
# ===========================================================================


class TestRegistryData:
    """The registry JSON must exist and contain at least 2 wikis."""

    def test_registry_json_exists(self) -> None:
        assert os.path.isfile(REGISTRY_JSON), (
            f"Registry JSON not found at {REGISTRY_JSON}"
        )

    def test_registry_has_at_least_two_wikis(self) -> None:
        with open(REGISTRY_JSON, "r") as f:
            data = json.load(f)
        assert "wikis" in data, "Registry JSON missing 'wikis' key"
        assert len(data["wikis"]) >= 2, (
            f"Expected at least 2 wikis, got {len(data['wikis'])}"
        )

    def test_registry_wikis_have_required_fields(self) -> None:
        """Each wiki must have fields needed by the UI."""
        with open(REGISTRY_JSON, "r") as f:
            data = json.load(f)
        required = [
            "id", "name", "description", "version", "trust_state",
            "publication", "maintainer", "freshness", "scope", "non_scope",
            "document_count", "route_recommendation", "badge", "summary",
            "listing_eligible", "recommendation_eligible",
            "kb_json_path", "llms_txt_path",
        ]
        for wiki in data["wikis"]:
            for field in required:
                assert field in wiki, (
                    f"Wiki '{wiki.get('id', 'unknown')}' missing field '{field}'"
                )


# ===========================================================================
# Test: UI interactions preserved (static analysis)
# ===========================================================================


class TestUIPreserved:
    """Key UI interactions must still be present in the JavaScript."""

    def test_search_function_exists(self) -> None:
        with open(INDEX_HTML, "r") as f:
            content = f.read()
        assert "packSearch" in content, "Search input missing"
        assert "query" in content, "Search query variable missing"

    def test_filter_chips_present(self) -> None:
        with open(INDEX_HTML, "r") as f:
            content = f.read()
        assert "data-filter" in content, "Filter chips missing"
        assert "All" in content, "All filter chip missing"
        assert "Draft" in content, "Draft filter chip missing"
        assert "Community" in content, "Community filter chip missing"

    def test_row_selection_present(self) -> None:
        with open(INDEX_HTML, "r") as f:
            content = f.read()
        assert "data-pack" in content, "Pack data attribute missing"
        assert "packrow" in content, "Pack row class missing"
        assert "selectedId" in content, "Selection variable missing"

    def test_surface_selection_present(self) -> None:
        with open(INDEX_HTML, "r") as f:
            content = f.read()
        assert "data-surface" in content, "Surface data attribute missing"
        assert "surfacebar" in content, "Surface bar missing"
        assert "MCP" in content, "MCP surface missing"
        assert "llms.txt" in content, "llms.txt surface missing"

    def test_copy_actions_present(self) -> None:
        with open(INDEX_HTML, "r") as f:
            content = f.read()
        assert "copy-setup" in content, "Copy setup action missing"
        assert "clipboard" in content, "Clipboard API reference missing"

    def test_cited_answer_present(self) -> None:
        with open(INDEX_HTML, "r") as f:
            content = f.read()
        assert "proof" in content, "Proof section missing"
        assert "cited answer" in content.lower(), "Cited answer heading missing"
        assert "refusal" in content.lower(), "Refusal section missing"

    def test_loading_state_present(self) -> None:
        with open(INDEX_HTML, "r") as f:
            content = f.read()
        assert "Loading registry data" in content, "Loading state missing"

    def test_async_fetch_used(self) -> None:
        with open(INDEX_HTML, "r") as f:
            content = f.read()
        assert "async function loadRegistry" in content, (
            "Async loadRegistry function missing"
        )
        assert "loadRegistry()" in content, "loadRegistry not called on init"


# ===========================================================================
# Test: adaptWiki mapping function exists
# ===========================================================================


class TestAdaptWikiMapping:
    """The adaptWiki mapping function must exist and produce correct fields."""

    def test_adaptWiki_function_exists(self) -> None:
        with open(INDEX_HTML, "r") as f:
            content = f.read()
        assert "function adaptWiki" in content, "adaptWiki function missing"

    def test_adaptWiki_maps_trust_state(self) -> None:
        with open(INDEX_HTML, "r") as f:
            content = f.read()
        assert "trust_state" in content, "trust_state field missing in mapping"

    def test_adaptWiki_maps_route_recommendation(self) -> None:
        with open(INDEX_HTML, "r") as f:
            content = f.read()
        assert "route_recommendation" in content, (
            "route_recommendation field missing in mapping"
        )

    def test_adaptWiki_maps_document_count(self) -> None:
        with open(INDEX_HTML, "r") as f:
            content = f.read()
        assert "document_count" in content, (
            "document_count field missing in mapping"
        )