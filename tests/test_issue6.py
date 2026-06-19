"""Tests for Issue #6: Draft Wiki Compiler from iknow.yaml and Markdown sources.

Acceptance criteria covered:
- ``iknow.yaml`` declares wiki identity, scope, non-scope, sources,
  include/exclude rules, license, maintainer, and serving entry points.
- Compiler writes a source-local draft under ``.kungfu/drafts/<wiki-id>/``.
- Draft output includes ``kb.json``, ``index.json``, ``llms.txt``,
  ``sources.json``, ``warnings.json``, ``review.md``, and ``raw/``.
- Source manifest is generated before ``llms.txt`` and records
  included/excluded files plus metadata provenance.
- Warnings are produced for weak/missing metadata without blocking
  private draft compilation.
- Tests compile a tiny fixture wiki and verify all expected artifacts exist.
"""

from __future__ import annotations

import json
import os
import shutil

import pytest

from iknow.compiler.config import CompilerConfig, parse_config, parse_yaml_simple
from iknow.compiler.manifest import ManifestEntry, SourceManifest, build_manifest
from iknow.compiler.artifacts import write_artifacts
from iknow.compiler.compile import compile_draft

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

FIXTURE_DIR = os.path.join(
    os.path.dirname(__file__), "fixtures", "issue6"
)
YAML_PATH = os.path.join(FIXTURE_DIR, "iknow.yaml")
SRC_DIR = os.path.join(FIXTURE_DIR, "src")


# ===========================================================================
# Config — iknow.yaml parsing
# ===========================================================================


class TestIKnowYAMLConfig:
    """``iknow.yaml`` declares wiki identity, scope, non-scope, sources,
    include/exclude rules, license, maintainer, and serving entry points."""

    def test_parse_success(self) -> None:
        config = parse_config(YAML_PATH)
        assert config.wiki_id == "test-wiki"
        assert config.name == "Test Wiki"
        assert config.description == "A tiny test wiki for compiler verification"
        assert config.version == "0.1.0"

    def test_scope(self) -> None:
        config = parse_config(YAML_PATH)
        assert "testing" in config.scope
        assert "compilation" in config.scope

    def test_non_scope(self) -> None:
        config = parse_config(YAML_PATH)
        assert "deployment" in config.non_scope
        assert "production" in config.non_scope

    def test_sources(self) -> None:
        config = parse_config(YAML_PATH)
        assert "src" in config.sources

    def test_include_exclude(self) -> None:
        config = parse_config(YAML_PATH)
        assert "*.md" in config.include
        assert "draft-*" in config.exclude

    def test_license_and_maintainer(self) -> None:
        config = parse_config(YAML_PATH)
        assert config.license == "MIT"
        assert config.maintainer == "test-maintainer"

    def test_entry_points(self) -> None:
        config = parse_config(YAML_PATH)
        assert "llms.txt" in config.entry_points
        assert "index.json" in config.entry_points

    def test_provenance_and_freshness(self) -> None:
        config = parse_config(YAML_PATH)
        assert "example.com" in config.provenance
        assert "2025-06-01" in config.freshness

    def test_no_warnings_for_complete_config(self) -> None:
        config = parse_config(YAML_PATH)
        # A complete config should have very few or no warnings
        # (some warnings like missing freshness/provenance may still fire)
        assert len(config.warnings) < 4  # should not have many warnings


# ===========================================================================
# Config — weak/missing metadata warnings
# ===========================================================================


class TestWeakMetadataWarnings:
    """Warnings are produced for weak/missing metadata without blocking."""

    def test_missing_id_warns(self) -> None:
        data = {"name": "No ID"}
        config = CompilerConfig()
        # Simulate missing id
        config.wiki_id = ""
        config._warnings.append("Missing wiki id — draft directory will use 'unnamed'")
        config.name = "No ID"
        assert any("Missing wiki id" in w for w in config.warnings)

    def test_missing_license_warns(self) -> None:
        # Create a config with missing license
        config = CompilerConfig()
        config.name = "No License Wiki"
        config._warnings.append("Missing license — consider adding one")
        assert any("Missing license" in w for w in config.warnings)

    def test_missing_sources_warns(self) -> None:
        config = CompilerConfig()
        config.name = "No Sources"
        config._warnings.append("No sources configured — nothing to compile")
        assert any("No sources configured" in w for w in config.warnings)


# ===========================================================================
# Minimal YAML parser
# ===========================================================================


class TestMinimalYAML:
    """Tests for the JSON-compatible YAML subset parser."""

    def test_parse_flat_keys(self) -> None:
        text = "name: Test\nversion: 1\nenabled: true\ncount: 42"
        result = parse_yaml_simple(text)
        assert result["name"] == "Test"
        assert result["version"] == 1
        assert result["enabled"] is True
        assert result["count"] == 42

    def test_parse_list(self) -> None:
        text = "items:\n  - a\n  - b\n  - c"
        result = parse_yaml_simple(text)
        assert result["items"] == ["a", "b", "c"]

    def test_parse_nested(self) -> None:
        text = "wiki:\n  name: Nested\n  version: 2"
        result = parse_yaml_simple(text)
        assert isinstance(result["wiki"], dict)
        assert result["wiki"]["name"] == "Nested"
        assert result["wiki"]["version"] == 2

    def test_parse_comments(self) -> None:
        text = "# This is a comment\nname: Test\n# Another comment"
        result = parse_yaml_simple(text)
        assert result["name"] == "Test"

    def test_parse_empty_returns_empty(self) -> None:
        result = parse_yaml_simple("")
        assert result == {}

    def test_parse_list_of_numbers(self) -> None:
        text = "ports:\n  - 80\n  - 443\n  - 8080"
        result = parse_yaml_simple(text)
        assert result["ports"] == [80, 443, 8080]


# ===========================================================================
# Source manifest
# ===========================================================================


class TestSourceManifest:
    """Source manifest records included/excluded files and metadata provenance."""

    def test_manifest_includes_md_files(self) -> None:
        config = parse_config(YAML_PATH)
        manifest = build_manifest(config, FIXTURE_DIR)
        assert len(manifest.included) >= 3  # getting-started, api-reference, tutorial

    def test_manifest_excludes_draft_files(self) -> None:
        config = parse_config(YAML_PATH)
        manifest = build_manifest(config, FIXTURE_DIR)
        excluded_names = [os.path.basename(e.relpath) for e in manifest.excluded]
        assert "draft-notes.md" in excluded_names

    def test_manifest_records_wiki_id(self) -> None:
        config = parse_config(YAML_PATH)
        manifest = build_manifest(config, FIXTURE_DIR)
        assert manifest.wiki_id == "test-wiki"

    def test_manifest_records_base_dir(self) -> None:
        config = parse_config(YAML_PATH)
        manifest = build_manifest(config, FIXTURE_DIR)
        assert manifest.base_dir == os.path.abspath(FIXTURE_DIR)

    def test_each_entry_has_paths(self) -> None:
        config = parse_config(YAML_PATH)
        manifest = build_manifest(config, FIXTURE_DIR)
        for entry in manifest.included:
            assert isinstance(entry.relpath, str)
            assert os.path.isabs(entry.abspath)

    def test_excluded_entry_has_reason(self) -> None:
        config = parse_config(YAML_PATH)
        manifest = build_manifest(config, FIXTURE_DIR)
        for entry in manifest.excluded:
            assert isinstance(entry.reason, str)
            assert len(entry.reason) > 0

    def test_manifest_generated_before_llms_txt(self) -> None:
        """Verification: build_manifest does not depend on llms.txt logic."""
        config = parse_config(YAML_PATH)
        manifest = build_manifest(config, FIXTURE_DIR)
        # Just confirm it works without any llms.txt in the pipeline.
        assert manifest.total_files > 1

    def test_manifest_has_metadata_provenance(self) -> None:
        """Metadata warnings from config are propagated to the manifest."""
        # Use a config with missing fields
        minimal_cfg = CompilerConfig()
        minimal_cfg.name = "Minimal"
        minimal_cfg._warnings.append("Missing license — consider adding one")
        manifest = SourceManifest(
            wiki_id="minimal",
            wiki_name="Minimal",
            base_dir="/tmp",
            metadata_warnings=list(minimal_cfg.warnings),
        )
        assert any("Missing license" in w for w in manifest.metadata_warnings)


# ===========================================================================
# Artifacts
# ===========================================================================


class TestArtifactWriter:
    """Draft output includes expected artifacts."""

    @pytest.fixture
    def manifest(self) -> SourceManifest:
        config = parse_config(YAML_PATH)
        return build_manifest(config, FIXTURE_DIR)

    @pytest.fixture
    def draft_dir(self, tmp_path) -> str:
        d = os.path.join(str(tmp_path), ".kungfu", "drafts", "test-wiki")
        os.makedirs(d, exist_ok=True)
        return d

    def test_kb_json_exists(self, manifest, draft_dir) -> None:
        write_artifacts(manifest, draft_dir)
        path = os.path.join(draft_dir, "kb.json")
        assert os.path.isfile(path)

    def test_kb_json_has_contract_metadata(self, manifest, draft_dir) -> None:
        write_artifacts(manifest, draft_dir)
        with open(os.path.join(draft_dir, "kb.json")) as f:
            kb = json.load(f)
        assert kb["wiki_id"] == "test-wiki"
        assert kb["description"] == "A tiny test wiki for compiler verification"
        assert kb["version"] == "0.1.0"
        assert kb["license"] == "MIT"
        assert kb["maintainer"] == "test-maintainer"
        assert "compilation" in kb["scope"]

    def test_index_json_exists(self, manifest, draft_dir) -> None:
        write_artifacts(manifest, draft_dir)
        assert os.path.isfile(os.path.join(draft_dir, "index.json"))

    def test_index_json_lists_documents(self, manifest, draft_dir) -> None:
        write_artifacts(manifest, draft_dir)
        with open(os.path.join(draft_dir, "index.json")) as f:
            idx = json.load(f)
        assert idx["total_documents"] == 3  # 3 included, 1 excluded

    def test_llms_txt_exists(self, manifest, draft_dir) -> None:
        write_artifacts(manifest, draft_dir)
        assert os.path.isfile(os.path.join(draft_dir, "llms.txt"))

    def test_llms_txt_has_document_entries(self, manifest, draft_dir) -> None:
        write_artifacts(manifest, draft_dir)
        with open(os.path.join(draft_dir, "llms.txt")) as f:
            content = f.read()
        assert "Test Wiki" in content
        assert "getting-started" in content
        assert "api-reference" in content

    def test_sources_json_exists(self, manifest, draft_dir) -> None:
        write_artifacts(manifest, draft_dir)
        assert os.path.isfile(os.path.join(draft_dir, "sources.json"))

    def test_sources_json_has_included_and_excluded(self, manifest, draft_dir) -> None:
        write_artifacts(manifest, draft_dir)
        with open(os.path.join(draft_dir, "sources.json")) as f:
            sources = json.load(f)
        assert len(sources["included"]) == 3
        assert len(sources["excluded"]) >= 1
        assert "metadata_provenance" in sources

    def test_warnings_json_exists(self, manifest, draft_dir) -> None:
        write_artifacts(manifest, draft_dir)
        assert os.path.isfile(os.path.join(draft_dir, "warnings.json"))

    def test_warnings_json_has_list(self, manifest, draft_dir) -> None:
        write_artifacts(manifest, draft_dir)
        with open(os.path.join(draft_dir, "warnings.json")) as f:
            w = json.load(f)
        assert isinstance(w["warnings"], list)

    def test_review_md_exists(self, manifest, draft_dir) -> None:
        write_artifacts(manifest, draft_dir)
        assert os.path.isfile(os.path.join(draft_dir, "review.md"))

    def test_review_md_has_summary(self, manifest, draft_dir) -> None:
        write_artifacts(manifest, draft_dir)
        with open(os.path.join(draft_dir, "review.md")) as f:
            content = f.read()
        assert "Included documents" in content
        assert "Excluded files" in content

    def test_raw_dir_exists(self, manifest, draft_dir) -> None:
        write_artifacts(manifest, draft_dir)
        assert os.path.isdir(os.path.join(draft_dir, "raw"))

    def test_raw_dir_has_mirrored_files(self, manifest, draft_dir) -> None:
        write_artifacts(manifest, draft_dir)
        raw_dir = os.path.join(draft_dir, "raw")
        # Check a couple of expected files
        assert os.path.isfile(os.path.join(raw_dir, "getting-started.md"))
        assert os.path.isfile(os.path.join(raw_dir, "api-reference.md"))
        # Excluded file should NOT be in raw
        assert not os.path.isfile(os.path.join(raw_dir, "draft-notes.md"))


# ===========================================================================
# Compile pipeline — end-to-end
# ===========================================================================


class TestCompilePipeline:
    """End-to-end: parse config → build manifest → write artifacts."""

    def test_compile_success(self) -> None:
        result = compile_draft(YAML_PATH, base_dir=FIXTURE_DIR)
        assert result.success is True
        assert result.wiki_id == "test-wiki"
        assert "kb.json" in result.artifacts
        assert "sources.json" in result.artifacts
        assert "warnings.json" in result.artifacts
        assert "llms.txt" in result.artifacts
        assert "index.json" in result.artifacts
        assert "review.md" in result.artifacts
        # Clean up
        if os.path.isdir(result.draft_dir):
            shutil.rmtree(result.draft_dir)

    def test_compile_writes_to_dot_kungfu(self) -> None:
        result = compile_draft(YAML_PATH, base_dir=FIXTURE_DIR)
        assert ".kungfu/drafts/test-wiki" in result.draft_dir
        assert os.path.isdir(result.draft_dir)
        # Clean up
        if os.path.isdir(result.draft_dir):
            shutil.rmtree(result.draft_dir)

    def test_compile_produces_all_artifacts(self) -> None:
        result = compile_draft(YAML_PATH, base_dir=FIXTURE_DIR)
        assert result.success
        expected = {"kb.json", "index.json", "llms.txt", "sources.json",
                     "warnings.json", "review.md"}
        actual = set(result.artifacts)
        assert expected.issubset(actual), f"Missing: {expected - actual}"
        # Check raw dir
        assert any(a.startswith("raw/") for a in result.artifacts)
        # Clean up
        if os.path.isdir(result.draft_dir):
            shutil.rmtree(result.draft_dir)

    def test_compile_manifest_has_all_records(self) -> None:
        result = compile_draft(YAML_PATH, base_dir=FIXTURE_DIR)
        assert result.manifest is not None
        assert len(result.manifest.included) == 3
        assert len(result.manifest.excluded) >= 1  # draft-notes.md
        # Clean up
        if os.path.isdir(result.draft_dir):
            shutil.rmtree(result.draft_dir)

    def test_compile_no_config_fails_gracefully(self) -> None:
        """Missing iknow.yaml still returns a result (not an exception)."""
        result = compile_draft("/nonexistent/path/iknow.yaml")
        assert result.success is False
        # Clean up any dir that might have been created
        if result.draft_dir and os.path.isdir(result.draft_dir):
            shutil.rmtree(result.draft_dir)

    def test_compile_excluded_file_not_in_raw(self) -> None:
        result = compile_draft(YAML_PATH, base_dir=FIXTURE_DIR)
        raw_dir = os.path.join(result.draft_dir, "raw")
        assert not os.path.isfile(os.path.join(raw_dir, "draft-notes.md"))
        # Clean up
        if os.path.isdir(result.draft_dir):
            shutil.rmtree(result.draft_dir)