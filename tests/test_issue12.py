"""Tests for Issue #12: Package the first real knowledge base wiki.

Acceptance criteria covered:
- A real ``iknow.yaml`` (Wiki Contract) exists for the first example wiki.
- Compiled output includes ``kb.json``, ``index.json``, ``llms.txt``,
  raw Markdown mirror, source/provenance metadata, and review/warning output.
- ``kb.json`` declares scope, non-scope, freshness, maintainer, trust state,
  license/publication posture, and serving entry points.
- At least one in-scope query can be answered with an exact source citation
  from this package (e.g. "What is Knowledge Pack Routing?").
- At least one out-of-scope query refuses or redirects instead of answering
  from the wrong wiki (e.g. "Describe a product case study").
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
# Paths
# ---------------------------------------------------------------------------

FIXTURE_DIR = os.path.join(
    os.path.dirname(__file__), "fixtures", "phase2", "agent-workflows"
)
YAML_PATH = os.path.join(FIXTURE_DIR, "iknow.yaml")


# ===========================================================================
# Config — iknow.yaml parses correctly for the real wiki
# ===========================================================================


class TestRealConfigParsing:
    """A real iknow.yaml (Wiki Contract) exists and parses correctly."""

    def test_config_file_exists(self) -> None:
        assert os.path.isfile(YAML_PATH), (
            f"Expected iknow.yaml at {YAML_PATH}"
        )

    def test_parse_success(self) -> None:
        config = parse_config(YAML_PATH)
        assert config.wiki_id == "agent-workflows"
        assert config.name == "Agent Workflows"
        assert "Knowledge Pack Routing" in config.description or "Knowledge Pack Routing" in " ".join(config.scope)
        assert "Pixoid" in config.description

    def test_scope_and_non_scope(self) -> None:
        config = parse_config(YAML_PATH)
        assert any("Knowledge Pack Routing" in s for s in config.scope)
        assert any("Product case studies" in s for s in config.non_scope)

    def test_freshness_present(self) -> None:
        config = parse_config(YAML_PATH)
        # Must declare freshness date
        assert config.freshness, "freshness must be set"
        assert "2026" in config.freshness

    def test_maintainer_present(self) -> None:
        config = parse_config(YAML_PATH)
        assert config.maintainer, "maintainer must be set"

    def test_trust_state_present(self) -> None:
        config = parse_config(YAML_PATH)
        assert config.trust_state, "trust_state must be set"

    def test_publication_present(self) -> None:
        config = parse_config(YAML_PATH)
        assert config.publication, "publication must be set"

    def test_license_present(self) -> None:
        config = parse_config(YAML_PATH)
        assert config.license, "license must be set"

    def test_entry_points_present(self) -> None:
        config = parse_config(YAML_PATH)
        assert len(config.entry_points) >= 3
        assert "llms.txt" in config.entry_points
        assert "index.json" in config.entry_points


# ===========================================================================
# Artifacts — compiled output structure
# ===========================================================================


class TestRealArtifacts:
    """Compiled output includes all expected artifacts."""

    @pytest.fixture
    def config(self) -> "CompilerConfig":
        return parse_config(YAML_PATH)

    @pytest.fixture
    def manifest(self, config) -> "SourceManifest":
        return build_manifest(config, FIXTURE_DIR)

    @pytest.fixture
    def draft_dir(self, tmp_path) -> str:
        d = os.path.join(str(tmp_path), ".kungfu", "drafts", "agent-workflows")
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
                raw_dir, "wiki", "concepts", "knowledge-pack-routing.md"
            )
        ), "Missing knowledge-pack-routing.md in raw"
        assert os.path.isfile(
            os.path.join(
                raw_dir, "wiki", "concepts", "peer-profiles-vs-child-processes.md"
            )
        ), "Missing peer-profiles-vs-child-processes.md in raw"

    def test_llms_txt_has_documents_listed(self, manifest, draft_dir) -> None:
        write_artifacts(manifest, draft_dir)
        with open(os.path.join(draft_dir, "llms.txt")) as f:
            content = f.read()
        assert "Knowledge Pack Routing" in content
        assert "Peer Profiles" in content

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
# Search / Query — in-scope and out-of-scope
# ===========================================================================


class TestQueryScope:
    """At least one in-scope query can be answered with citation.
    At least one out-of-scope query refuses or redirects.
    """

    @pytest.fixture
    def draft_dir(self, tmp_path) -> str:
        d = os.path.join(str(tmp_path), ".kungfu", "drafts", "agent-workflows")
        os.makedirs(d, exist_ok=True)
        config = parse_config(YAML_PATH)
        manifest = build_manifest(config, FIXTURE_DIR)
        write_artifacts(manifest, d)
        return d

    def test_in_scope_knowledge_pack_routing(self, draft_dir) -> None:
        """Knowledge Pack Routing is in scope — the raw source should
        contain a clear explanation we can cite."""
        kpr_path = os.path.join(
            draft_dir, "raw", "wiki", "concepts", "knowledge-pack-routing.md"
        )
        assert os.path.isfile(kpr_path)
        with open(kpr_path) as f:
            content = f.read()
        # Verify the content is real, not lorem ipsum
        assert "Knowledge Pack Routing" in content
        assert "markdown-first pattern" in content
        assert "scope, freshness, source paths" in content
        # Exact citation verification
        assert "Jamie" in content

    def test_in_scope_peer_profiles_vs_child_processes(self, draft_dir) -> None:
        pp_path = os.path.join(
            draft_dir, "raw", "wiki", "concepts", "peer-profiles-vs-child-processes.md"
        )
        assert os.path.isfile(pp_path)
        with open(pp_path) as f:
            content = f.read()
        assert "peer Hermes profiles" in content.lower() or "peer profiles" in content.lower()
        assert "child process" in content.lower()

    def test_out_of_scope_product_case_study_refuses(self, draft_dir) -> None:
        """Product case studies are not covered — the compiled
        wiki metadata should show 'case studies' in non_scope."""
        with open(os.path.join(draft_dir, "kb.json")) as f:
            kb = json.load(f)
        non_scope_text = " ".join(kb["non_scope"]).lower()
        assert "case stud" in non_scope_text

    def test_out_of_scope_ai_infrastructure_refuses(self, draft_dir) -> None:
        """Low-level local AI infrastructure is not covered."""
        with open(os.path.join(draft_dir, "kb.json")) as f:
            kb = json.load(f)
        non_scope_text = " ".join(kb["non_scope"]).lower()
        assert "infrastructure" in non_scope_text

    def test_installed_wiki_search_returns_citation(self, tmp_path) -> None:
        """Installed package can answer an in-scope query with source path."""
        result = compile_draft(YAML_PATH, base_dir=FIXTURE_DIR)
        assert result.success is True
        store = os.path.join(str(tmp_path), "installed")
        install = install_draft(result.draft_dir, "agent-workflows", store_path=store)
        assert install.success is True

        search = search_wiki("agent-workflows", "Knowledge Pack Routing", store_path=store)

        assert search["out_of_scope"] is False
        assert search["total_hits"] > 0
        assert any(
            hit["document_path"] == "wiki/concepts/knowledge-pack-routing.md"
            for hit in search["hits"]
        )

    def test_installed_wiki_search_refuses_out_of_scope_query(self, tmp_path) -> None:
        """Installed package refuses a query matching declared non-scope."""
        result = compile_draft(YAML_PATH, base_dir=FIXTURE_DIR)
        assert result.success is True
        store = os.path.join(str(tmp_path), "installed")
        install = install_draft(result.draft_dir, "agent-workflows", store_path=store)
        assert install.success is True

        search = search_wiki("agent-workflows", "product case study", store_path=store)

        assert search["out_of_scope"] is True
        assert "different knowledge base" in search["out_of_scope_detail"]
        assert search["total_hits"] == 0


# ===========================================================================
# Compile pipeline — end-to-end
# ===========================================================================


class TestRealCompilePipeline:
    """End-to-end: parse real config → build manifest → write artifacts."""

    def test_compile_success(self) -> None:
        result = compile_draft(YAML_PATH, base_dir=FIXTURE_DIR)
        assert result.success is True
        assert result.wiki_id == "agent-workflows"
        expected = {"kb.json", "index.json", "llms.txt", "sources.json",
                     "warnings.json", "review.md"}
        actual = set(result.artifacts)
        assert expected.issubset(actual), f"Missing: {expected - actual}"
        assert any(a.startswith("raw/") for a in result.artifacts)
        # Clean up
        if os.path.isdir(result.draft_dir):
            shutil.rmtree(result.draft_dir)

    def test_compile_produces_raw_directory(self) -> None:
        result = compile_draft(YAML_PATH, base_dir=FIXTURE_DIR)
        raw_dir = os.path.join(result.draft_dir, "raw")
        assert os.path.isdir(raw_dir)
        assert len(os.listdir(raw_dir)) > 0
        # Clean up
        if os.path.isdir(result.draft_dir):
            shutil.rmtree(result.draft_dir)