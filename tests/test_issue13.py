"""Tests for Issue #13: Package a second real wiki to exercise trust and fit differences.

Acceptance criteria covered:
- A second real Wiki Contract/package is generated from existing source material.
- The second package has distinct scope, non-scope, provenance, freshness,
  and route/trust posture from the first package (agent-workflows).
- Cookbook registry/listing output can show both packages with meaningful differences.
- Context fit output can distinguish overlap, gaps, boundary warnings,
  and route recommendation for both packages.
- The second package has at least one cited in-scope query and one
  out-of-scope refusal.
- Existing tests still pass.
"""

from __future__ import annotations

import json
import os
import shutil

import pytest

from iknow.compiler.config import CompilerConfig, parse_config
from iknow.compiler.manifest import SourceManifest, build_manifest
from iknow.compiler.artifacts import write_artifacts
from iknow.compiler.compile import compile_draft
from iknow.serving import search_wiki
from iknow.store import install_draft

# ---------------------------------------------------------------------------
# Paths — both packages
# ---------------------------------------------------------------------------

FIXTURE_DIR_AW = os.path.join(
    os.path.dirname(__file__), "fixtures", "phase2", "agent-workflows"
)
YAML_PATH_AW = os.path.join(FIXTURE_DIR_AW, "iknow.yaml")

FIXTURE_DIR_PS = os.path.join(
    os.path.dirname(__file__), "fixtures", "phase2", "ai-native-product-surfaces"
)
YAML_PATH_PS = os.path.join(FIXTURE_DIR_PS, "iknow.yaml")


# ===========================================================================
# Config — second iknow.yaml parses correctly
# ===========================================================================


class TestSecondRealConfigParsing:
    """A second real iknow.yaml (Wiki Contract) exists and parses correctly."""

    def test_config_file_exists(self) -> None:
        assert os.path.isfile(YAML_PATH_PS), (
            f"Expected iknow.yaml at {YAML_PATH_PS}"
        )

    def test_parse_success(self) -> None:
        config = parse_config(YAML_PATH_PS)
        assert config.wiki_id == "ai-native-product-surfaces"
        assert config.name == "AI-Native Product Surfaces"
        assert "AI-native" in config.description
        assert "product" in config.description.lower()

    def test_scope_and_non_scope(self) -> None:
        config = parse_config(YAML_PATH_PS)
        assert any("AI-native" in s for s in config.scope)
        assert any("PM case studies" in s for s in config.scope)
        assert any(
            "Generic product management" in s for s in config.non_scope
        )

    def test_freshness_present(self) -> None:
        config = parse_config(YAML_PATH_PS)
        assert config.freshness, "freshness must be set"
        assert "2026" in config.freshness

    def test_maintainer_present(self) -> None:
        config = parse_config(YAML_PATH_PS)
        assert config.maintainer, "maintainer must be set"

    def test_trust_state_present(self) -> None:
        config = parse_config(YAML_PATH_PS)
        assert config.trust_state, "trust_state must be set"
        # Must be different from first package's "draft"
        assert config.trust_state != "draft", (
            "Second package should use a different trust posture"
        )

    def test_publication_present(self) -> None:
        config = parse_config(YAML_PATH_PS)
        assert config.publication, "publication must be set"
        # Must be different from first package's "private"
        assert config.publication != "private", (
            "Second package should use a different publication posture"
        )

    def test_license_present(self) -> None:
        config = parse_config(YAML_PATH_PS)
        assert config.license, "license must be set"

    def test_entry_points_present(self) -> None:
        config = parse_config(YAML_PATH_PS)
        assert len(config.entry_points) >= 3
        assert "llms.txt" in config.entry_points
        assert "index.json" in config.entry_points


# ===========================================================================
# Artifacts — compiled output structure for second package
# ===========================================================================


class TestSecondRealArtifacts:
    """Compiled output includes all expected artifacts."""

    @pytest.fixture
    def config(self) -> CompilerConfig:
        return parse_config(YAML_PATH_PS)

    @pytest.fixture
    def manifest(self, config) -> SourceManifest:
        return build_manifest(config, FIXTURE_DIR_PS)

    @pytest.fixture
    def draft_dir(self, tmp_path) -> str:
        d = os.path.join(str(tmp_path), ".kungfu", "drafts", "ai-native-product-surfaces")
        os.makedirs(d, exist_ok=True)
        return d

    def test_kb_json_has_trust_and_publication(self, manifest, draft_dir) -> None:
        write_artifacts(manifest, draft_dir)
        with open(os.path.join(draft_dir, "kb.json")) as f:
            kb = json.load(f)
        assert "trust_state" in kb
        assert "publication" in kb
        assert kb["trust_state"] in ("draft", "verified", "community", "official")
        assert kb["publication"] in ("private", "public", "restricted")

    def test_kb_json_has_scope_and_non_scope(self, manifest, draft_dir) -> None:
        write_artifacts(manifest, draft_dir)
        with open(os.path.join(draft_dir, "kb.json")) as f:
            kb = json.load(f)
        assert len(kb["scope"]) >= 3
        assert len(kb["non_scope"]) >= 1

    def test_kb_json_has_freshness_maintainer_license(self, manifest, draft_dir) -> None:
        write_artifacts(manifest, draft_dir)
        with open(os.path.join(draft_dir, "kb.json")) as f:
            kb = json.load(f)
        assert kb["freshness"]
        assert kb["maintainer"]
        assert kb["license"]

    def test_kb_json_has_entry_points(self, manifest, draft_dir) -> None:
        write_artifacts(manifest, draft_dir)
        with open(os.path.join(draft_dir, "kb.json")) as f:
            kb = json.load(f)
        assert len(kb["entry_points"]) >= 1

    def test_raw_dir_has_mirrored_sources(self, manifest, draft_dir) -> None:
        write_artifacts(manifest, draft_dir)
        raw_dir = os.path.join(draft_dir, "raw")
        assert os.path.isfile(
            os.path.join(raw_dir, "README.md")
        ), "Missing README.md in raw"
        assert os.path.isfile(
            os.path.join(
                raw_dir, "wiki", "concepts", "ai-native-problem-framing-framework.md"
            )
        ), "Missing ai-native-problem-framing-framework.md in raw"
        assert os.path.isfile(
            os.path.join(
                raw_dir, "wiki", "entities", "planned-program-intel.md"
            )
        ), "Missing planned-program-intel.md in raw"

    def test_llms_txt_has_documents_listed(self, manifest, draft_dir) -> None:
        write_artifacts(manifest, draft_dir)
        with open(os.path.join(draft_dir, "llms.txt")) as f:
            content = f.read()
        assert "AI-Native Problem Framing Framework" in content
        assert "Planned Program Intel" in content

    def test_review_md_exists(self, manifest, draft_dir) -> None:
        write_artifacts(manifest, draft_dir)
        assert os.path.isfile(os.path.join(draft_dir, "review.md"))

    def test_warnings_json_exists(self, manifest, draft_dir) -> None:
        write_artifacts(manifest, draft_dir)
        assert os.path.isfile(os.path.join(draft_dir, "warnings.json"))

    def test_sources_json_has_provenance(self, manifest, draft_dir) -> None:
        write_artifacts(manifest, draft_dir)
        with open(os.path.join(draft_dir, "sources.json")) as f:
            sources = json.load(f)
        assert "metadata_provenance" in sources
        assert len(sources["included"]) >= 3


# ===========================================================================
# Distinctiveness — both packages have meaningful differences
# ===========================================================================


class TestBothPackagesDistinct:
    """Both compiled packages must have distinct scope, non-scope,
    provenance, freshness, trust_state, and publication.
    """

    @pytest.fixture
    def aw_kb(self, tmp_path) -> dict:
        d = os.path.join(str(tmp_path), "aw")
        os.makedirs(d, exist_ok=True)
        manifest = build_manifest(parse_config(YAML_PATH_AW), FIXTURE_DIR_AW)
        write_artifacts(manifest, d)
        with open(os.path.join(d, "kb.json")) as f:
            return json.load(f)

    @pytest.fixture
    def ps_kb(self, tmp_path) -> dict:
        d = os.path.join(str(tmp_path), "ps")
        os.makedirs(d, exist_ok=True)
        manifest = build_manifest(parse_config(YAML_PATH_PS), FIXTURE_DIR_PS)
        write_artifacts(manifest, d)
        with open(os.path.join(d, "kb.json")) as f:
            return json.load(f)

    def test_distinct_wiki_ids(self, aw_kb, ps_kb) -> None:
        assert aw_kb["wiki_id"] != ps_kb["wiki_id"]

    def test_distinct_names(self, aw_kb, ps_kb) -> None:
        assert aw_kb["name"] != ps_kb["name"]

    def test_distinct_scope(self, aw_kb, ps_kb) -> None:
        """Scope items should have no exact overlap (different domains)."""
        aw_scope_set = set(s.lower() for s in aw_kb["scope"])
        ps_scope_set = set(s.lower() for s in ps_kb["scope"])
        # At least one scope item should differ (they are different domains)
        assert len(aw_scope_set - ps_scope_set) >= 1
        assert len(ps_scope_set - aw_scope_set) >= 1

    def test_distinct_non_scope(self, aw_kb, ps_kb) -> None:
        """Non-scope items should differ meaningfully."""
        aw_ns_set = set(s.lower() for s in aw_kb["non_scope"])
        ps_ns_set = set(s.lower() for s in ps_kb["non_scope"])
        # At least one non-scope item differs
        assert len(aw_ns_set - ps_ns_set) >= 1 or len(ps_ns_set - aw_ns_set) >= 1

    def test_distinct_provenance(self, aw_kb, ps_kb) -> None:
        assert aw_kb["provenance"] != ps_kb["provenance"]

    def test_distinct_trust_state(self, aw_kb, ps_kb) -> None:
        assert aw_kb["trust_state"] != ps_kb["trust_state"], (
            "Trust state should differ between packages"
        )

    def test_distinct_publication(self, aw_kb, ps_kb) -> None:
        assert aw_kb["publication"] != ps_kb["publication"], (
            "Publication posture should differ between packages"
        )

    def test_distinct_description(self, aw_kb, ps_kb) -> None:
        assert aw_kb["description"] != ps_kb["description"]


# ===========================================================================
# Context Fit — both packages produce distinct fit output
# ===========================================================================


class TestContextFitDistinction:
    """Context fit output can distinguish overlap, gaps, boundary warnings,
    and route recommendation for both packages.
    """

    @pytest.fixture
    def aw_contract(self, tmp_path) -> dict:
        """Return compiled kb.json dict for agent-workflows."""
        d = os.path.join(str(tmp_path), "aw-fit")
        os.makedirs(d, exist_ok=True)
        manifest = build_manifest(parse_config(YAML_PATH_AW), FIXTURE_DIR_AW)
        write_artifacts(manifest, d)
        with open(os.path.join(d, "kb.json")) as f:
            return json.load(f)

    @pytest.fixture
    def ps_contract(self, tmp_path) -> dict:
        """Return compiled kb.json dict for ai-native-product-surfaces."""
        d = os.path.join(str(tmp_path), "ps-fit")
        os.makedirs(d, exist_ok=True)
        manifest = build_manifest(parse_config(YAML_PATH_PS), FIXTURE_DIR_PS)
        write_artifacts(manifest, d)
        with open(os.path.join(d, "kb.json")) as f:
            return json.load(f)

    def _build_inventory(self, contract: dict, name: str = "Test Inventory"):
        """Build a minimal LocalKnowledgeInventory-like dict from contract."""
        from iknow.contracts.model import TrustState, WikiContract
        from iknow.inventory.model import InventoryItem, LocalKnowledgeInventory

        trust = TrustState._missing_(contract.get("trust_state", "")) or TrustState.COMMUNITY

        item = InventoryItem(
            id=contract["wiki_id"],
            name=contract["name"],
            description=contract.get("description", ""),
            scope=contract.get("scope", []),
            non_scope=contract.get("non_scope", []),
            entry_points=[],
            trust_state=trust,
        )
        return LocalKnowledgeInventory(
            name=name,
            description=f"Inventory for {name}",
            items=[item],
        )

    def _build_contract(self, contract: dict) -> WikiContract:
        """Build a WikiContract from compiled kb.json dict."""
        from iknow.contracts.model import TrustState, WikiContract

        trust = TrustState._missing_(contract.get("trust_state", "")) or TrustState.COMMUNITY
        return WikiContract(
            name=contract["name"],
            description=contract.get("description", ""),
            version=contract.get("version", ""),
            scope=contract.get("scope", []),
            non_scope=contract.get("non_scope", []),
            provenance=contract.get("provenance", ""),
            freshness=contract.get("freshness", ""),
            license=contract.get("license", ""),
            trust_state=trust,
            entry_points=[],
        )

    def test_fit_agent_workflows_vs_inventory(self, aw_contract) -> None:
        """Fit for agent-workflows against its own inventory should
        show low/no gaps and route recommendation.
        """
        from iknow.fit import compute_fit

        contract = self._build_contract(aw_contract)
        inventory = self._build_inventory(aw_contract)
        result = compute_fit(contract, inventory, candidate_id="agent-workflows")

        assert result.candidate_id == "agent-workflows"
        assert result.fit is not None
        # When comparing against itself, all scope topics overlap
        # (gap percentage should be 0.0)
        assert result.fit.gap_percentage == 0.0

    def test_fit_product_surfaces_vs_inventory(self, ps_contract) -> None:
        """Fit for product-surfaces against its own inventory should
        also show no gaps.
        """
        from iknow.fit import compute_fit

        contract = self._build_contract(ps_contract)
        inventory = self._build_inventory(ps_contract)
        result = compute_fit(contract, inventory, candidate_id="ai-native-product-surfaces")

        assert result.candidate_id == "ai-native-product-surfaces"
        assert result.fit.gap_percentage == 0.0  # same-inventory

    def test_fit_cross_domain(self, aw_contract, ps_contract) -> None:
        """Comparing one package's contract against the other package's
        inventory should reveal gaps and produce a different route
        recommendation.
        """
        from iknow.fit import compute_fit

        # Agent-workflows contract vs product-surfaces inventory
        aw_contract_obj = self._build_contract(aw_contract)
        ps_inventory = self._build_inventory(ps_contract, name="Product Surfaces Inventory")
        aw_vs_ps = compute_fit(
            aw_contract_obj, ps_inventory, candidate_id="agent-workflows"
        )

        # Product-surfaces contract vs agent-workflows inventory
        ps_contract_obj = self._build_contract(ps_contract)
        aw_inventory = self._build_inventory(aw_contract, name="Agent Workflows Inventory")
        ps_vs_aw = compute_fit(
            ps_contract_obj, aw_inventory, candidate_id="ai-native-product-surfaces"
        )

        # Both should have some gaps (different domains)
        assert aw_vs_ps.fit.gap_percentage > 0
        assert ps_vs_aw.fit.gap_percentage > 0

        # Gap percentages may differ (symmetric or not depending on scope sizes)
        assert aw_vs_ps.fit.recommendation is not None
        assert ps_vs_aw.fit.recommendation is not None

        # Cross-domain comparison should have boundary warnings (non-scope overlap detection)
        # or at least some gaps indicating different territories
        assert len(aw_vs_ps.fit.gap_topics) > 0
        assert len(ps_vs_aw.fit.gap_topics) > 0


# ===========================================================================
# Listing/Registry — can show both packages meaningfully
# ===========================================================================


class TestListingBothPackages:
    """Registry/listing output can show both packages with meaningful differences."""

    def test_listing_both_by_compile(self, tmp_path) -> None:
        """We can compile both and enumerate them via their kb.json
        metadata — verifying that both packages are clearly distinct
        in listing-level metadata without requiring full #14 static export.
        """
        # Compile both into separate directories
        aw_dir = os.path.join(str(tmp_path), "store", "agent-workflows")
        ps_dir = os.path.join(str(tmp_path), "store", "ai-native-product-surfaces")

        aw_result = compile_draft(YAML_PATH_AW, base_dir=FIXTURE_DIR_AW,
                                  output_dir=aw_dir)
        ps_result = compile_draft(YAML_PATH_PS, base_dir=FIXTURE_DIR_PS,
                                  output_dir=ps_dir)

        assert aw_result.success is True
        assert ps_result.success is True

        # Load both kb.jsons
        with open(os.path.join(aw_dir, "kb.json")) as f:
            aw_kb = json.load(f)
        with open(os.path.join(ps_dir, "kb.json")) as f:
            ps_kb = json.load(f)

        # Construct a minimal listing dict (like a registry would produce)
        listing = [
            {"id": aw_kb["wiki_id"], "name": aw_kb["name"],
             "trust_state": aw_kb.get("trust_state", "")},
            {"id": ps_kb["wiki_id"], "name": ps_kb["name"],
             "trust_state": ps_kb.get("trust_state", "")},
        ]

        assert len(listing) == 2
        ids = {item["id"] for item in listing}
        assert "agent-workflows" in ids
        assert "ai-native-product-surfaces" in ids

        # Names must differ
        names = {item["name"] for item in listing}
        assert len(names) == 2

        # Trust states must differ (raw strings from kb.json)
        trust_raw = {item["trust_state"] for item in listing}
        assert len(trust_raw) == 2

    def test_installed_listing_shows_both(self, tmp_path) -> None:
        """After installing both drafts, the store's list_installed
        returns both wikis.
        """
        store = os.path.join(str(tmp_path), "installed-store")

        # Compile both
        aw_result = compile_draft(YAML_PATH_AW, base_dir=FIXTURE_DIR_AW)
        ps_result = compile_draft(YAML_PATH_PS, base_dir=FIXTURE_DIR_PS)
        assert aw_result.success is True
        assert ps_result.success is True

        # Install both
        install_aw = install_draft(aw_result.draft_dir, "agent-workflows", store_path=store)
        install_ps = install_draft(ps_result.draft_dir, "ai-native-product-surfaces", store_path=store)
        assert install_aw.success is True
        assert install_ps.success is True

        from iknow.serving import list_wikis
        wikis = list_wikis(store_path=store)
        assert len(wikis) >= 2
        ids = {w.wiki_id for w in wikis}
        assert "agent-workflows" in ids
        assert "ai-native-product-surfaces" in ids

        # Verify summaries show distinct metadata
        from iknow.serving import get_wiki_summary
        aw_summary = get_wiki_summary("agent-workflows", store_path=store)
        ps_summary = get_wiki_summary("ai-native-product-surfaces", store_path=store)
        assert aw_summary is not None
        assert ps_summary is not None
        assert aw_summary.name != ps_summary.name
        assert aw_summary.trust_state != ps_summary.trust_state
        assert aw_summary.freshness != ps_summary.freshness


# ===========================================================================
# Query scope — in-scope and out-of-scope for second package
# ===========================================================================


class TestSecondQueryScope:
    """At least one in-scope query can be answered with citation.
    At least one out-of-scope query refuses or redirects.
    """

    @pytest.fixture
    def draft_dir(self, tmp_path) -> str:
        d = os.path.join(str(tmp_path), ".kungfu", "drafts", "ai-native-product-surfaces")
        os.makedirs(d, exist_ok=True)
        config = parse_config(YAML_PATH_PS)
        manifest = build_manifest(config, FIXTURE_DIR_PS)
        write_artifacts(manifest, d)
        return d

    def test_in_scope_ai_native_problem_framing(self, draft_dir) -> None:
        """AI-Native Problem Framing is in scope — the raw source should
        contain a clear explanation we can cite.
        """
        framing_path = os.path.join(
            draft_dir, "raw", "wiki", "concepts", "ai-native-problem-framing-framework.md"
        )
        assert os.path.isfile(framing_path)
        with open(framing_path) as f:
            content = f.read()
        # Verify the content is real, not lorem ipsum
        assert "AI-Native Problem Framing Framework" in content
        assert "Environment" in content
        assert "Actions" in content
        assert "Goal" in content
        assert "Constraints" in content
        # Exact citation verification
        assert "product" in content.lower()

    def test_in_scope_planned_program_intel(self, draft_dir) -> None:
        """Planned Program Intel is in scope."""
        ppi_path = os.path.join(
            draft_dir, "raw", "wiki", "entities", "planned-program-intel.md"
        )
        assert os.path.isfile(ppi_path)
        with open(ppi_path) as f:
            content = f.read()
        assert "Planned Program Intel" in content
        assert "decision-routing" in content
        assert "institutional-memory" in content

    def test_out_of_scope_local_model_infrastructure_refuses(self, draft_dir) -> None:
        """Local model infrastructure (without product relevance)
        is not covered — the compiled wiki metadata should show
        this in non_scope.
        """
        with open(os.path.join(draft_dir, "kb.json")) as f:
            kb = json.load(f)
        non_scope_text = " ".join(kb["non_scope"]).lower()
        assert "infrastructure" in non_scope_text
        assert "product" in non_scope_text  # 'generic product management' check

    def test_out_of_scope_generic_pm_refuses(self, draft_dir) -> None:
        """Generic product management notes without AI-native surfaces
        are out of scope.
        """
        with open(os.path.join(draft_dir, "kb.json")) as f:
            kb = json.load(f)
        non_scope_text = " ".join(kb["non_scope"]).lower()
        assert "generic" in non_scope_text

    def test_installed_wiki_search_returns_citation(self, tmp_path) -> None:
        """Installed package can answer an in-scope query with source path."""
        result = compile_draft(YAML_PATH_PS, base_dir=FIXTURE_DIR_PS)
        assert result.success is True
        store = os.path.join(str(tmp_path), "installed-ps")
        install = install_draft(result.draft_dir, "ai-native-product-surfaces", store_path=store)
        assert install.success is True

        search = search_wiki(
            "ai-native-product-surfaces", "AI-native problem framing", store_path=store
        )

        assert search["out_of_scope"] is False
        assert search["total_hits"] > 0
        assert any(
            hit["document_path"] == "wiki/concepts/ai-native-problem-framing-framework.md"
            for hit in search["hits"]
        )

    def test_installed_wiki_search_refuses_out_of_scope_query(self, tmp_path) -> None:
        """Installed package refuses a query matching declared non-scope."""
        result = compile_draft(YAML_PATH_PS, base_dir=FIXTURE_DIR_PS)
        assert result.success is True
        store = os.path.join(str(tmp_path), "installed-ps-oos")
        install = install_draft(result.draft_dir, "ai-native-product-surfaces", store_path=store)
        assert install.success is True

        search = search_wiki(
            "ai-native-product-surfaces",
            "generic product management notes",
            store_path=store,
        )

        assert search["out_of_scope"] is True
        assert "different knowledge base" in search["out_of_scope_detail"]
        assert search["total_hits"] == 0

    def test_installed_wiki_search_refuses_local_infrastructure(self, tmp_path) -> None:
        """Another non-scope query: local model infrastructure."""
        result = compile_draft(YAML_PATH_PS, base_dir=FIXTURE_DIR_PS)
        assert result.success is True
        store = os.path.join(str(tmp_path), "installed-ps-oos2")
        install = install_draft(result.draft_dir, "ai-native-product-surfaces", store_path=store)
        assert install.success is True

        search = search_wiki(
            "ai-native-product-surfaces",
            "local model infrastructure",
            store_path=store,
        )

        assert search["out_of_scope"] is True
        assert search["total_hits"] == 0


# ===========================================================================
# Compile pipeline — end-to-end for second package
# ===========================================================================


class TestSecondCompilePipeline:
    """End-to-end: parse real config → build manifest → write artifacts."""

    def test_compile_success(self) -> None:
        result = compile_draft(YAML_PATH_PS, base_dir=FIXTURE_DIR_PS)
        assert result.success is True
        assert result.wiki_id == "ai-native-product-surfaces"
        expected = {"kb.json", "index.json", "llms.txt", "sources.json",
                     "warnings.json", "review.md"}
        actual = set(result.artifacts)
        assert expected.issubset(actual), f"Missing: {expected - actual}"
        assert any(a.startswith("raw/") for a in result.artifacts)
        # Clean up
        if os.path.isdir(result.draft_dir):
            shutil.rmtree(result.draft_dir)

    def test_compile_produces_raw_directory(self) -> None:
        result = compile_draft(YAML_PATH_PS, base_dir=FIXTURE_DIR_PS)
        raw_dir = os.path.join(result.draft_dir, "raw")
        assert os.path.isdir(raw_dir)
        assert len(os.listdir(raw_dir)) > 0
        # Clean up
        if os.path.isdir(result.draft_dir):
            shutil.rmtree(result.draft_dir)
