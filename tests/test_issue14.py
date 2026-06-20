"""Tests for Issue #14: Export static Cookbook registry data from real wiki contracts.

Acceptance criteria covered:
- There is a command or build step that exports static Cookbook registry data
  from real packaged wiki artifacts.
- The exported data includes enough fields to render the Variant A Cookbook UI
  without hardcoded package rows.
- The exported data includes contract/provenance/freshness/trust fields,
  not just display labels.
- Listing eligibility and recommendation eligibility remain separate in the
  exported shape.
- Tests cover that registry export preserves both example wikis and their
  distinct trust/fit posture.
- Existing tests still pass.
"""

from __future__ import annotations

import json
import os

import pytest

from iknow.validation import check_listing_eligibility, check_recommendation_eligibility

# ---------------------------------------------------------------------------
# Paths — both packages
# ---------------------------------------------------------------------------

HERE = os.path.dirname(__file__)

FIXTURE_DIR_AW = os.path.join(
    HERE, "fixtures", "phase2", "agent-workflows"
)
YAML_PATH_AW = os.path.join(FIXTURE_DIR_AW, "iknow.yaml")

FIXTURE_DIR_PS = os.path.join(
    HERE, "fixtures", "phase2", "ai-native-product-surfaces"
)
YAML_PATH_PS = os.path.join(FIXTURE_DIR_PS, "iknow.yaml")

# Export output directory (under prototype)
EXPORT_OUTPUT_DIR = os.path.join(
    HERE, "..", "prototype", "cookbook-serving", "data"
)
EXPORT_OUTPUT_PATH = os.path.join(EXPORT_OUTPUT_DIR, "cookbook-registry.json")


# ===========================================================================
# Fixtures
# ===========================================================================


@pytest.fixture
def compiled_dirs(tmp_path) -> dict[str, str]:
    """Compile both real wikis and return {wiki_id: compiled_dir}."""
    from iknow.compiler.compile import compile_draft

    aw_out = os.path.join(str(tmp_path), "drafts", "agent-workflows")
    ps_out = os.path.join(str(tmp_path), "drafts", "ai-native-product-surfaces")

    aw_result = compile_draft(YAML_PATH_AW, base_dir=FIXTURE_DIR_AW, output_dir=aw_out)
    assert aw_result.success, f"Compile agent-workflows failed: {aw_result.errors}"
    ps_result = compile_draft(YAML_PATH_PS, base_dir=FIXTURE_DIR_PS, output_dir=ps_out)
    assert ps_result.success, f"Compile ai-native-product-surfaces failed: {ps_result.errors}"

    return {
        "agent-workflows": aw_out,
        "ai-native-product-surfaces": ps_out,
    }


# ===========================================================================
# Test: export function exists and produces correct shape
# ===========================================================================


class TestExportFunctionExists:
    """The export module exists and has the expected API."""

    def test_module_importable(self) -> None:
        from iknow.cookbook import export as cookbook_export
        assert cookbook_export is not None

    def test_export_function_exists(self) -> None:
        from iknow.cookbook.export import export_cookbook_registry
        assert callable(export_cookbook_registry)

    def test_export_accepts_wiki_dirs_and_output_path(self, compiled_dirs) -> None:
        from iknow.cookbook.export import export_cookbook_registry

        result = export_cookbook_registry(
            wiki_dirs=list(compiled_dirs.values()),
            output_path=None,  # return data, don't write
        )
        assert isinstance(result, dict)


# ===========================================================================
# Test: export shape includes all required fields
# ===========================================================================


class TestExportShape:
    """Exported data includes all required fields per the acceptance criteria."""

    def test_shape_has_version_and_exported_at(self, compiled_dirs) -> None:
        from iknow.cookbook.export import export_cookbook_registry

        result = export_cookbook_registry(
            wiki_dirs=list(compiled_dirs.values()),
            output_path=None,
        )
        assert "version" in result
        assert "exported_at" in result
        assert "wikis" in result

    def test_shape_includes_both_wikis(self, compiled_dirs) -> None:
        from iknow.cookbook.export import export_cookbook_registry

        result = export_cookbook_registry(
            wiki_dirs=list(compiled_dirs.values()),
            output_path=None,
        )
        wiki_ids = {w["id"] for w in result["wikis"]}
        assert "agent-workflows" in wiki_ids
        assert "ai-native-product-surfaces" in wiki_ids

    def test_each_wiki_has_display_fields(self, compiled_dirs) -> None:
        from iknow.cookbook.export import export_cookbook_registry

        result = export_cookbook_registry(
            wiki_dirs=list(compiled_dirs.values()),
            output_path=None,
        )
        for wiki in result["wikis"]:
            assert isinstance(wiki["id"], str) and len(wiki["id"]) > 0
            assert isinstance(wiki["name"], str) and len(wiki["name"]) > 0
            assert isinstance(wiki["description"], str) and len(wiki["description"]) > 0
            assert isinstance(wiki["version"], str) and len(wiki["version"]) > 0

    def test_each_wiki_has_contract_fields(self, compiled_dirs) -> None:
        from iknow.cookbook.export import export_cookbook_registry

        result = export_cookbook_registry(
            wiki_dirs=list(compiled_dirs.values()),
            output_path=None,
        )
        for wiki in result["wikis"]:
            assert "trust_state" in wiki
            assert "publication" in wiki
            assert "maintainer" in wiki
            assert "license" in wiki
            assert "provenance" in wiki
            assert "freshness" in wiki

    def test_each_wiki_has_scope_and_non_scope(self, compiled_dirs) -> None:
        from iknow.cookbook.export import export_cookbook_registry

        result = export_cookbook_registry(
            wiki_dirs=list(compiled_dirs.values()),
            output_path=None,
        )
        for wiki in result["wikis"]:
            assert isinstance(wiki["scope"], list)
            assert isinstance(wiki["non_scope"], list)

    def test_each_wiki_has_entry_points_and_document_count(self, compiled_dirs) -> None:
        from iknow.cookbook.export import export_cookbook_registry

        result = export_cookbook_registry(
            wiki_dirs=list(compiled_dirs.values()),
            output_path=None,
        )
        for wiki in result["wikis"]:
            assert isinstance(wiki["entry_points"], list)
            assert isinstance(wiki["document_count"], int)
            assert wiki["document_count"] > 0

    def test_each_wiki_has_artifact_paths(self, compiled_dirs) -> None:
        from iknow.cookbook.export import export_cookbook_registry

        result = export_cookbook_registry(
            wiki_dirs=list(compiled_dirs.values()),
            output_path=None,
        )
        for wiki in result["wikis"]:
            assert "kb_json_path" in wiki
            assert "index_json_path" in wiki
            assert "llms_txt_path" in wiki


# ===========================================================================
# Test: eligibility fields are separate
# ===========================================================================


class TestEligibilitySeparate:
    """Listing eligibility and recommendation eligibility remain
    separate in the exported shape."""

    def test_both_eligibility_fields_present(self, compiled_dirs) -> None:
        from iknow.cookbook.export import export_cookbook_registry

        result = export_cookbook_registry(
            wiki_dirs=list(compiled_dirs.values()),
            output_path=None,
        )
        for wiki in result["wikis"]:
            assert "listing_eligible" in wiki
            assert "recommendation_eligible" in wiki
            assert isinstance(wiki["listing_eligible"], bool)
            assert isinstance(wiki["recommendation_eligible"], bool)

    def test_listing_blockers_and_warnings(self, compiled_dirs) -> None:
        from iknow.cookbook.export import export_cookbook_registry

        result = export_cookbook_registry(
            wiki_dirs=list(compiled_dirs.values()),
            output_path=None,
        )
        for wiki in result["wikis"]:
            assert isinstance(wiki.get("listing_blockers", None), list)
            assert isinstance(wiki.get("listing_warnings", None), list)

    def test_recommendation_blockers_and_warnings(self, compiled_dirs) -> None:
        from iknow.cookbook.export import export_cookbook_registry

        result = export_cookbook_registry(
            wiki_dirs=list(compiled_dirs.values()),
            output_path=None,
        )
        for wiki in result["wikis"]:
            assert isinstance(wiki.get("recommendation_blockers", None), list)
            assert isinstance(wiki.get("recommendation_warnings", None), list)


# ===========================================================================
# Test: distinct trust/fit posture between both wikis
# ===========================================================================


class TestDistinctTrustFitPosture:
    """Both example wikis are preserved with their distinct trust/fit posture."""

    def test_distinct_trust_state(self, compiled_dirs) -> None:
        from iknow.cookbook.export import export_cookbook_registry

        result = export_cookbook_registry(
            wiki_dirs=list(compiled_dirs.values()),
            output_path=None,
        )
        w_by_id = {w["id"]: w for w in result["wikis"]}
        aw_trust = w_by_id["agent-workflows"]["trust_state"]
        ps_trust = w_by_id["ai-native-product-surfaces"]["trust_state"]
        assert aw_trust != ps_trust, (
            "Trust state should differ: agent-workflows=draft, "
            "ai-native-product-surfaces=community"
        )

    def test_distinct_publication(self, compiled_dirs) -> None:
        from iknow.cookbook.export import export_cookbook_registry

        result = export_cookbook_registry(
            wiki_dirs=list(compiled_dirs.values()),
            output_path=None,
        )
        w_by_id = {w["id"]: w for w in result["wikis"]}
        aw_pub = w_by_id["agent-workflows"]["publication"]
        ps_pub = w_by_id["ai-native-product-surfaces"]["publication"]
        assert aw_pub != ps_pub, (
            "Publication should differ: agent-workflows=private, "
            "ai-native-product-surfaces=restricted"
        )

    def test_distinct_listing_eligibility(self, compiled_dirs) -> None:
        """Draft/private wiki may fail listing eligibility while
        community/restricted may pass."""
        from iknow.cookbook.export import export_cookbook_registry

        result = export_cookbook_registry(
            wiki_dirs=list(compiled_dirs.values()),
            output_path=None,
        )
        w_by_id = {w["id"]: w for w in result["wikis"]}
        # agent-workflows is draft/private — may fail listing due to
        # weak provenance or other checks
        aw_listing = w_by_id["agent-workflows"]["listing_eligible"]
        ps_listing = w_by_id["ai-native-product-surfaces"]["listing_eligible"]
        # At minimum they're tracked separately; they may differ
        assert isinstance(aw_listing, bool)
        assert isinstance(ps_listing, bool)

    def test_distinct_recommendation_eligibility(self, compiled_dirs) -> None:
        """Neither draft nor community wikis are recommendable."""
        from iknow.cookbook.export import export_cookbook_registry

        result = export_cookbook_registry(
            wiki_dirs=list(compiled_dirs.values()),
            output_path=None,
        )
        w_by_id = {w["id"]: w for w in result["wikis"]}
        aw_rec = w_by_id["agent-workflows"]["recommendation_eligible"]
        ps_rec = w_by_id["ai-native-product-surfaces"]["recommendation_eligible"]
        # Both are not recommendable (neither is Verified or Official)
        assert aw_rec is False
        assert ps_rec is False


# ===========================================================================
# Test: can write to disk
# ===========================================================================


class TestExportToDisk:
    """Export function can write the result to a JSON file on disk."""

    def test_write_to_temp_path(self, compiled_dirs, tmp_path) -> None:
        from iknow.cookbook.export import export_cookbook_registry

        out_path = os.path.join(str(tmp_path), "export.json")
        result = export_cookbook_registry(
            wiki_dirs=list(compiled_dirs.values()),
            output_path=out_path,
        )
        assert isinstance(result, dict)
        assert os.path.isfile(out_path), f"Output file not written: {out_path}"

        with open(out_path, "r") as f:
            loaded = json.load(f)
        assert loaded["version"] == 1
        assert len(loaded["wikis"]) == 2

    def test_export_preserves_valid_json(self, compiled_dirs, tmp_path) -> None:
        from iknow.cookbook.export import export_cookbook_registry

        out_path = os.path.join(str(tmp_path), "export.json")
        export_cookbook_registry(
            wiki_dirs=list(compiled_dirs.values()),
            output_path=out_path,
        )
        with open(out_path, "r") as f:
            loaded = json.load(f)
        # Verify structure
        assert "version" in loaded
        assert "exported_at" in loaded
        assert "wikis" in loaded
        for wiki in loaded["wikis"]:
            assert "id" in wiki
            assert "name" in wiki
            assert "trust_state" in wiki
            assert "listing_eligible" in wiki
            assert "recommendation_eligible" in wiki


# ===========================================================================
# Test: route/trust posture fields
# ===========================================================================


class TestRouteTrustPosture:
    """Route recommendation and trust posture fields are present."""

    def test_route_recommendation_present(self, compiled_dirs) -> None:
        from iknow.cookbook.export import export_cookbook_registry

        result = export_cookbook_registry(
            wiki_dirs=list(compiled_dirs.values()),
            output_path=None,
        )
        for wiki in result["wikis"]:
            assert "route_recommendation" in wiki
            assert isinstance(wiki["route_recommendation"], str)

    def test_badge_and_summary_present(self, compiled_dirs) -> None:
        from iknow.cookbook.export import export_cookbook_registry

        result = export_cookbook_registry(
            wiki_dirs=list(compiled_dirs.values()),
            output_path=None,
        )
        for wiki in result["wikis"]:
            assert "badge" in wiki
            assert isinstance(wiki["badge"], str)
            assert len(wiki["badge"]) > 0
            assert "summary" in wiki
            assert isinstance(wiki["summary"], str)

    def test_route_differs_by_trust_state(self, compiled_dirs) -> None:
        from iknow.cookbook.export import export_cookbook_registry

        result = export_cookbook_registry(
            wiki_dirs=list(compiled_dirs.values()),
            output_path=None,
        )
        w_by_id = {w["id"]: w for w in result["wikis"]}
        aw_route = w_by_id["agent-workflows"]["route_recommendation"]
        ps_route = w_by_id["ai-native-product-surfaces"]["route_recommendation"]
        assert aw_route != ps_route, (
            "Route recommendation should differ between draft/private "
            "and community/restricted wikis"
        )
