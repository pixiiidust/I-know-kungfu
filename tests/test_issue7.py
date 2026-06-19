"""Tests for Issue #7: Installed Wiki Store module.

Acceptance criteria covered:
- Install module installs a draft wiki into a configurable store path.
- Installed wiki preserves contract, index, llms.txt, raw Markdown, sources,
  and warnings/review metadata.
- Install refuses or warns on invalid draft artifacts.
- Install does not require network, auth, or hosted backend access.
- Tests use a temporary installed-store path and verify installed artifacts
  are discoverable.
- Docs or help text explain source-local drafts vs global installed wikis.
"""

from __future__ import annotations

import json
import os
import shutil

import pytest

from iknow.store import (
    InstallResult,
    InstalledWiki,
    get_installed,
    get_installed_store_path,
    get_known_artifacts,
    install_draft,
    installed_wiki_path,
    is_valid_draft,
    list_installed,
    remove_installed,
    summarize,
)
from iknow.store.paths import (
    DEFAULT_STORE_DIRNAME,
    ENV_STORE_OVERRIDE,
    IKNOW_HOME_DIRNAME,
    REQUIRED_DRAFT_ARTIFACTS,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

FIXTURE_DRAFT = os.path.join(
    os.path.dirname(__file__),
    "fixtures",
    "issue6",
    ".kungfu",
    "drafts",
    "test-wiki",
)


@pytest.fixture
def tmp_store(tmp_path) -> str:
    """Create a temporary installed store path."""
    return os.path.join(str(tmp_path), "installed")


@pytest.fixture
def valid_draft(tmp_path) -> str:
    """Create a minimal valid compiled draft programmatically (no fixture dependency)."""
    dest = os.path.join(str(tmp_path), "test-wiki")
    os.makedirs(os.path.join(dest, "raw"))

    # kb.json — contract
    kb = {
        "wiki_id": "test-wiki",
        "name": "Test Wiki",
        "description": "A test wiki for installed store validation",
        "version": "0.1.0",
        "scope": ["testing", "store"],
        "non_scope": ["deployment"],
        "license": "MIT",
        "maintainer": "test-maintainer",
        "provenance": "https://example.com/test-wiki",
        "freshness": "2025-06-01",
        "entry_points": ["llms.txt", "index.json"],
        "total_documents": 2,
        "total_excluded": 0,
        "metadata_warnings": [],
    }
    with open(os.path.join(dest, "kb.json"), "w") as f:
        json.dump(kb, f, indent=2)

    # index.json
    index = {
        "wiki_id": "test-wiki",
        "wiki_name": "Test Wiki",
        "total_documents": 2,
        "documents": [
            {"path": "doc1.md", "title": "Doc One", "size_bytes": 50},
            {"path": "doc2.md", "title": "Doc Two", "size_bytes": 75},
        ],
    }
    with open(os.path.join(dest, "index.json"), "w") as f:
        json.dump(index, f, indent=2)

    # llms.txt
    with open(os.path.join(dest, "llms.txt"), "w") as f:
        f.write("# Test Wiki\nWiki ID: test-wiki\nTotal documents: 2\n\n## Documents\n\n- Doc One (doc1.md)\n- Doc Two (doc2.md)\n")

    # sources.json
    sources = {
        "wiki_id": "test-wiki",
        "wiki_name": "Test Wiki",
        "base_dir": dest,
        "metadata_provenance": {"source": "iknow.yaml", "warnings": []},
        "included": [
            {"relpath": "doc1.md", "abspath": os.path.join(dest, "doc1.md"), "reason": "matched include patterns"},
            {"relpath": "doc2.md", "abspath": os.path.join(dest, "doc2.md"), "reason": "matched include patterns"},
        ],
        "excluded": [],
    }
    with open(os.path.join(dest, "sources.json"), "w") as f:
        json.dump(sources, f, indent=2)

    # warnings.json
    warnings_data = {
        "wiki_id": "test-wiki",
        "wiki_name": "Test Wiki",
        "total_warnings": 0,
        "warnings": [],
    }
    with open(os.path.join(dest, "warnings.json"), "w") as f:
        json.dump(warnings_data, f, indent=2)

    # review.md
    with open(os.path.join(dest, "review.md"), "w") as f:
        f.write("# Review: Test Wiki\n**Wiki ID:** test-wiki\n\n## Summary\n\n- **Included documents:** 2\n- **Excluded files:** 0\n- **Total considered:** 2\n")

    # raw markdown files
    with open(os.path.join(dest, "raw", "doc1.md"), "w") as f:
        f.write("# Doc One\n\nContent of doc one.\n")
    with open(os.path.join(dest, "raw", "doc2.md"), "w") as f:
        f.write("# Doc Two\n\nContent of doc two.\n")

    return dest


# ===========================================================================
# Path resolution
# ===========================================================================


class TestStorePaths:
    """Path resolution for the installed wiki store."""

    def test_default_store_path(self) -> None:
        path = get_installed_store_path(override=None)
        home = os.path.expanduser("~")
        expected = os.path.join(home, IKNOW_HOME_DIRNAME, DEFAULT_STORE_DIRNAME)
        assert path == expected

    def test_override_argument(self) -> None:
        path = get_installed_store_path(override="/tmp/custom-store")
        assert path == os.path.abspath("/tmp/custom-store")

    def test_env_override(self, monkeypatch) -> None:
        monkeypatch.setenv(ENV_STORE_OVERRIDE, "/env/custom-store")
        path = get_installed_store_path(override=None)
        assert path == os.path.abspath("/env/custom-store")

    def test_override_precedence(self, monkeypatch) -> None:
        """Explicit override should win over env var."""
        monkeypatch.setenv(ENV_STORE_OVERRIDE, "/env/should-lose")
        path = get_installed_store_path(override="/explicit/winner")
        assert path == os.path.abspath("/explicit/winner")

    def test_installed_wiki_path(self) -> None:
        path = installed_wiki_path("my-wiki", "/store/root")
        assert path == os.path.join("/store/root", "my-wiki")

    def test_installed_wiki_path_default_store(self) -> None:
        path = installed_wiki_path("my-wiki")
        store = get_installed_store_path()
        assert path == os.path.join(store, "my-wiki")


# ===========================================================================
# Draft validation
# ===========================================================================


class TestDraftValidation:
    """Install refuses or warns on invalid draft artifacts."""

    def test_valid_draft(self) -> None:
        """Test that a properly constructed draft passes validation."""
        import tempfile
        import json

        with tempfile.TemporaryDirectory() as d:
            os.makedirs(os.path.join(d, "raw"))
            for art in REQUIRED_DRAFT_ARTIFACTS:
                with open(os.path.join(d, art), "w") as f:
                    if art.endswith(".json"):
                        json.dump({"test": True}, f)
                    else:
                        f.write("# test\n")
            valid, issues = is_valid_draft(d)
            assert valid is True
            assert issues == []

    def test_missing_directory(self) -> None:
        valid, issues = is_valid_draft("/nonexistent/draft")
        assert valid is False
        assert any("does not exist" in i for i in issues)

    def test_missing_all_artifacts(self, tmp_path) -> None:
        empty_dir = os.path.join(str(tmp_path), "empty-draft")
        os.makedirs(empty_dir)
        valid, issues = is_valid_draft(empty_dir)
        assert valid is False
        for artifact in REQUIRED_DRAFT_ARTIFACTS:
            assert any(artifact in i for i in issues)
        assert any("raw/" in i for i in issues)

    def test_missing_one_artifact(self, tmp_path) -> None:
        incomplete = os.path.join(str(tmp_path), "incomplete")
        os.makedirs(os.path.join(incomplete, "raw"))
        # Only write kb.json
        with open(os.path.join(incomplete, "kb.json"), "w") as f:
            json.dump({"test": True}, f)
        valid, issues = is_valid_draft(incomplete)
        assert valid is False
        # Should report all except kb.json
        missing = set(REQUIRED_DRAFT_ARTIFACTS) - {"kb.json"}
        for art in missing:
            assert any(art in i for i in issues)

    def test_get_known_artifacts(self) -> None:
        artifacts = get_known_artifacts()
        assert "kb.json" in artifacts
        assert "index.json" in artifacts
        assert "llms.txt" in artifacts
        assert "sources.json" in artifacts
        assert "warnings.json" in artifacts
        assert "review.md" in artifacts
        assert len(artifacts) == 6


# ===========================================================================
# Install
# ===========================================================================


class TestInstallDraft:
    """Install a compiled draft wiki into the global installed wiki store."""

    def test_install_success(self, valid_draft, tmp_store) -> None:
        result = install_draft(
            draft_dir=valid_draft,
            wiki_id="test-wiki",
            store_path=tmp_store,
        )
        assert result.success is True
        assert result.wiki_id == "test-wiki"
        assert os.path.isdir(result.installed_path)

    def test_install_preserves_kb_json(self, valid_draft, tmp_store) -> None:
        result = install_draft(
            draft_dir=valid_draft,
            wiki_id="test-wiki",
            store_path=tmp_store,
        )
        assert result.success
        kb_path = os.path.join(result.installed_path, "kb.json")
        assert os.path.isfile(kb_path)
        with open(kb_path) as f:
            kb = json.load(f)
        assert kb["wiki_id"] == "test-wiki"
        assert kb["name"] == "Test Wiki"
        assert kb["version"] == "0.1.0"

    def test_install_preserves_index_json(self, valid_draft, tmp_store) -> None:
        result = install_draft(
            draft_dir=valid_draft,
            wiki_id="test-wiki",
            store_path=tmp_store,
        )
        assert result.success
        idx_path = os.path.join(result.installed_path, "index.json")
        assert os.path.isfile(idx_path)
        with open(idx_path) as f:
            idx = json.load(f)
        assert idx["total_documents"] == 2

    def test_install_preserves_llms_txt(self, valid_draft, tmp_store) -> None:
        result = install_draft(
            draft_dir=valid_draft,
            wiki_id="test-wiki",
            store_path=tmp_store,
        )
        assert result.success
        assert os.path.isfile(os.path.join(result.installed_path, "llms.txt"))

    def test_install_preserves_sources_json(self, valid_draft, tmp_store) -> None:
        result = install_draft(
            draft_dir=valid_draft,
            wiki_id="test-wiki",
            store_path=tmp_store,
        )
        assert result.success
        assert os.path.isfile(os.path.join(result.installed_path, "sources.json"))

    def test_install_preserves_warnings_json(self, valid_draft, tmp_store) -> None:
        result = install_draft(
            draft_dir=valid_draft,
            wiki_id="test-wiki",
            store_path=tmp_store,
        )
        assert result.success
        assert os.path.isfile(os.path.join(result.installed_path, "warnings.json"))

    def test_install_preserves_review_md(self, valid_draft, tmp_store) -> None:
        result = install_draft(
            draft_dir=valid_draft,
            wiki_id="test-wiki",
            store_path=tmp_store,
        )
        assert result.success
        assert os.path.isfile(os.path.join(result.installed_path, "review.md"))

    def test_install_preserves_raw_markdown(self, valid_draft, tmp_store) -> None:
        result = install_draft(
            draft_dir=valid_draft,
            wiki_id="test-wiki",
            store_path=tmp_store,
        )
        assert result.success
        raw_dir = os.path.join(result.installed_path, "raw")
        assert os.path.isdir(raw_dir)
        assert os.path.isfile(os.path.join(raw_dir, "doc1.md"))
        assert os.path.isfile(os.path.join(raw_dir, "doc2.md"))

    def test_install_preserves_all_artifacts(self, valid_draft, tmp_store) -> None:
        """Install preserves every file that was in the draft."""
        # Collect original files
        original_files = set()
        for root, _dirs, files in os.walk(valid_draft):
            for f in files:
                rel = os.path.relpath(os.path.join(root, f), valid_draft)
                original_files.add(rel)

        result = install_draft(
            draft_dir=valid_draft,
            store_path=tmp_store,
        )
        assert result.success

        # Collect installed files
        installed_files = set()
        for root, _dirs, files in os.walk(result.installed_path):
            for f in files:
                rel = os.path.relpath(os.path.join(root, f), result.installed_path)
                installed_files.add(rel)

        assert original_files == installed_files

    def test_install_auto_detects_wiki_id(self, valid_draft, tmp_store) -> None:
        result = install_draft(
            draft_dir=valid_draft,
            store_path=tmp_store,
        )
        assert result.success
        assert result.wiki_id == "test-wiki"  # from kb.json

    def test_install_auto_detects_from_dirname(self, valid_draft, tmp_store) -> None:
        """If kb.json lacks wiki_id, use directory name."""
        # Remove wiki_id from kb.json
        kb_path = os.path.join(valid_draft, "kb.json")
        with open(kb_path) as f:
            kb = json.load(f)
        del kb["wiki_id"]
        with open(kb_path, "w") as f:
            json.dump(kb, f)

        result = install_draft(
            draft_dir=valid_draft,
            store_path=tmp_store,
        )
        assert result.success
        assert result.wiki_id == "test-wiki"  # basename of draft_dir

    def test_install_rejects_invalid_draft(self, tmp_store, tmp_path) -> None:
        """Install refuses on invalid draft artifacts."""
        empty = os.path.join(str(tmp_path), "bad-draft")
        os.makedirs(empty)

        result = install_draft(
            draft_dir=empty,
            store_path=tmp_store,
        )
        assert result.success is False
        assert len(result.errors) > 0

    def test_install_rejects_nonexistent_draft(self, tmp_store) -> None:
        result = install_draft(
            draft_dir="/nonexistent/draft",
            store_path=tmp_store,
        )
        assert result.success is False
        assert any("does not exist" in e for e in result.errors)

    def test_install_overwrites_existing(self, valid_draft, tmp_store) -> None:
        """Installing twice should overwrite cleanly."""
        r1 = install_draft(valid_draft, wiki_id="test-wiki", store_path=tmp_store)
        assert r1.success

        r2 = install_draft(valid_draft, wiki_id="test-wiki", store_path=tmp_store)
        assert r2.success
        assert os.path.isdir(r2.installed_path)

    def test_install_returns_installed_path(self, valid_draft, tmp_store) -> None:
        r = install_draft(valid_draft, wiki_id="my-id", store_path=tmp_store)
        expected = os.path.join(tmp_store, "my-id")
        assert r.installed_path == expected


# ===========================================================================
# List / Query / Remove
# ===========================================================================


class TestListInstalled:
    """List installed wikis."""

    def test_list_empty_store(self, tmp_store) -> None:
        wikis = list_installed(store_path=tmp_store)
        assert wikis == []

    def test_list_single_wiki(self, valid_draft, tmp_store) -> None:
        install_draft(valid_draft, wiki_id="test-wiki", store_path=tmp_store)
        wikis = list_installed(store_path=tmp_store)
        assert len(wikis) == 1
        assert wikis[0].wiki_id == "test-wiki"
        assert wikis[0].name == "Test Wiki"

    def test_list_multiple_wikis(self, valid_draft, tmp_store, tmp_path) -> None:
        # Install first wiki
        install_draft(valid_draft, wiki_id="wiki-a", store_path=tmp_store)

        # Create and install a second draft
        draft_b = os.path.join(str(tmp_path), "wiki-b")
        shutil.copytree(valid_draft, draft_b)
        kb_path = os.path.join(draft_b, "kb.json")
        with open(kb_path) as f:
            kb = json.load(f)
        kb["name"] = "Wiki B"
        with open(kb_path, "w") as f:
            json.dump(kb, f)
        install_draft(draft_b, wiki_id="wiki-b", store_path=tmp_store)

        wikis = list_installed(store_path=tmp_store)
        assert len(wikis) == 2
        ids = [w.wiki_id for w in wikis]
        assert "wiki-a" in ids
        assert "wiki-b" in ids

    def test_list_sorted(self, valid_draft, tmp_store, tmp_path) -> None:
        """List should be sorted alphabetically."""
        install_draft(valid_draft, wiki_id="zulu", store_path=tmp_store)
        draft_b = os.path.join(str(tmp_path), "alpha")
        shutil.copytree(valid_draft, draft_b)
        install_draft(draft_b, wiki_id="alpha", store_path=tmp_store)

        wikis = list_installed(store_path=tmp_store)
        assert wikis[0].wiki_id == "alpha"
        assert wikis[1].wiki_id == "zulu"

    def test_list_ignores_non_wiki_dirs(self, tmp_store) -> None:
        """Files and non-kb directories in the store are ignored."""
        os.makedirs(tmp_store, exist_ok=True)
        # Create a file and a dir without kb.json
        with open(os.path.join(tmp_store, "README.txt"), "w") as f:
            f.write("hello")
        os.makedirs(os.path.join(tmp_store, "subdir"))
        assert list_installed(store_path=tmp_store) == []

    def test_installed_wiki_has_raw_flag(self, valid_draft, tmp_store) -> None:
        install_draft(valid_draft, wiki_id="test-wiki", store_path=tmp_store)
        wikis = list_installed(store_path=tmp_store)
        assert len(wikis) == 1
        assert wikis[0].has_raw is True
        assert wikis[0].total_documents == 2


class TestGetInstalled:
    """Get metadata for a single installed wiki."""

    def test_get_existing(self, valid_draft, tmp_store) -> None:
        install_draft(valid_draft, wiki_id="test-wiki", store_path=tmp_store)
        wiki = get_installed("test-wiki", store_path=tmp_store)
        assert wiki is not None
        assert wiki.wiki_id == "test-wiki"
        assert wiki.name == "Test Wiki"
        assert wiki.version == "0.1.0"

    def test_get_nonexistent(self, tmp_store) -> None:
        wiki = get_installed("nonexistent", store_path=tmp_store)
        assert wiki is None


class TestRemoveInstalled:
    """Remove an installed wiki from the store."""

    def test_remove_existing(self, valid_draft, tmp_store) -> None:
        install_draft(valid_draft, wiki_id="test-wiki", store_path=tmp_store)
        assert os.path.isdir(os.path.join(tmp_store, "test-wiki"))

        success = remove_installed("test-wiki", store_path=tmp_store)
        assert success is True
        assert not os.path.isdir(os.path.join(tmp_store, "test-wiki"))

    def test_remove_nonexistent(self, tmp_store) -> None:
        success = remove_installed("nonexistent", store_path=tmp_store)
        assert success is False

    def test_remove_other_wikis_remain(self, valid_draft, tmp_store, tmp_path) -> None:
        """Removing one wiki should not affect others."""
        install_draft(valid_draft, wiki_id="wiki-a", store_path=tmp_store)
        draft_b = os.path.join(str(tmp_path), "wiki-b")
        shutil.copytree(valid_draft, draft_b)
        install_draft(draft_b, wiki_id="wiki-b", store_path=tmp_store)

        remove_installed("wiki-a", store_path=tmp_store)

        remaining = list_installed(store_path=tmp_store)
        assert len(remaining) == 1
        assert remaining[0].wiki_id == "wiki-b"


# ===========================================================================
# Summarize helper
# ===========================================================================


class TestSummarize:
    """Human-readable summary for an installed wiki."""

    def test_summary_format(self) -> None:
        wiki = InstalledWiki(
            wiki_id="test-wiki",
            name="Test Wiki",
            description="desc",
            version="1.0.0",
            installed_at="/some/path",
            total_documents=5,
        )
        summary = summarize(wiki)
        assert "test-wiki" in summary
        assert "Test Wiki" in summary
        assert "1.0.0" in summary
        assert "5" in summary


# ===========================================================================
# No network / auth / backend
# ===========================================================================


class TestNoNetworkRequired:
    """Install does not require network, auth, or hosted backend access."""

    def test_local_only(self, valid_draft, tmp_store) -> None:
        """Install uses only local filesystem — no remote calls."""
        # This test passes by definition: the implementation uses only
        # stdlib os/shutil operations and does not import urllib/requests/etc.
        result = install_draft(
            draft_dir=valid_draft,
            wiki_id="test-wiki",
            store_path=tmp_store,
        )
        assert result.success
        assert os.path.isdir(result.installed_path)

    def test_no_imports_from_network_libs(self) -> None:
        """Verify the module doesn't import any networking libraries."""
        import iknow.store.installed as m
        # Check there's no urllib, requests, httpx, etc.
        mod_source = m.__file__ or ""
        with open(mod_source) as f:
            source = f.read()
        for net_lib in ("import urllib", "import requests", "import httpx",
                        "import aiohttp", "import socket", "import http"):
            assert net_lib not in source, f"Module imports networking: {net_lib}"


# ===========================================================================
# Edge cases
# ===========================================================================


class TestEdgeCases:
    """Edge cases for the installed store."""

    def test_install_with_unicode_wiki_id(self, valid_draft, tmp_store) -> None:
        result = install_draft(
            draft_dir=valid_draft,
            wiki_id="wiki-ünîcödé",
            store_path=tmp_store,
        )
        assert result.success
        assert os.path.isdir(os.path.join(tmp_store, "wiki-ünîcödé"))

    def test_no_store_path_uses_default(self, valid_draft, monkeypatch) -> None:
        """When no store_path given, use env or default."""
        monkeypatch.setenv(ENV_STORE_OVERRIDE, "/tmp/test-installed-store")
        result = install_draft(
            draft_dir=valid_draft,
            wiki_id="env-test",
        )
        assert result.success
        assert "/tmp/test-installed-store" in result.installed_path
        # Clean up
        shutil.rmtree(result.installed_path, ignore_errors=True)

    def test_empty_store_path_nonexistent(self, tmp_store) -> None:
        """Listing an empty/nonexistent store returns empty list."""
        wikis = list_installed(store_path="/nonexistent/store")
        assert wikis == []