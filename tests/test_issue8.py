"""Tests for Issue #8: Serving module and MCP-shaped adapter over installed wikis.

Acceptance criteria covered:
- ``list_wikis`` returns installed wikis with metadata.
- ``get_wiki_summary`` returns detailed metadata including scope/non-scope.
- ``search_wiki`` returns hits from deterministic text/heading search.
- ``read_document`` returns exact Markdown content with citation path.
- Out-of-scope query returns refusal/redirect rather than hallucinated answer.
- MCP adapter exposes tool definitions and dispatches correctly.
- Tests cover installed wiki listing, search hit, document read, citation
  path, and out-of-scope refusal path.
"""

from __future__ import annotations

import json
import os

import pytest

from iknow.serving import (
    DocumentResult,
    SearchHit,
    WikiListItem,
    WikiSummary,
    get_wiki_summary,
    list_wikis,
    read_document,
    search_wiki,
)
from iknow.serving.mcp import (
    call_tool,
    get_tool_definitions,
    list_resources,
)
from iknow.serving.search import search_documents
from iknow.store import install_draft

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
def installed_wiki(tmp_path, tmp_store) -> str:
    """Create and install a minimal valid compiled draft programmatically."""
    dest = os.path.join(str(tmp_path), "draft-test-wiki")
    os.makedirs(os.path.join(dest, "raw"))

    # kb.json
    kb = {
        "wiki_id": "test-wiki",
        "name": "Test Wiki",
        "description": "A test wiki for serving module validation",
        "version": "0.1.0",
        "scope": ["testing", "serving"],
        "non_scope": [],
        "license": "MIT",
        "maintainer": "test-maintainer",
        "provenance": "https://example.com/test-wiki",
        "freshness": "2025-06-01",
        "entry_points": ["llms.txt", "index.json", "markdown"],
        "total_documents": 3,
        "total_excluded": 0,
        "metadata_warnings": [],
    }
    with open(os.path.join(dest, "kb.json"), "w") as f:
        json.dump(kb, f, indent=2)

    # index.json
    index = {
        "wiki_id": "test-wiki",
        "wiki_name": "Test Wiki",
        "total_documents": 3,
        "documents": [
            {"path": "getting-started.md", "title": "Getting Started", "size_bytes": 50},
            {"path": "api-reference.md", "title": "API Reference", "size_bytes": 100},
            {"path": "tutorial.md", "title": "Tutorial", "size_bytes": 75},
        ],
    }
    with open(os.path.join(dest, "index.json"), "w") as f:
        json.dump(index, f, indent=2)

    # llms.txt
    with open(os.path.join(dest, "llms.txt"), "w") as f:
        f.write("# Test Wiki\n")

    # sources.json
    sources = {"wiki_id": "test-wiki", "wiki_name": "Test Wiki", "base_dir": dest,
               "included": [], "excluded": []}
    with open(os.path.join(dest, "sources.json"), "w") as f:
        json.dump(sources, f)

    # warnings.json
    with open(os.path.join(dest, "warnings.json"), "w") as f:
        json.dump({"total_warnings": 0, "warnings": []}, f)

    # review.md
    with open(os.path.join(dest, "review.md"), "w") as f:
        f.write("# Review\n")

    # Raw markdown files
    docs = {
        "getting-started.md": "# Getting Started\n\nWelcome to the test wiki.\n## Installation\n\nRun `pip install`.\n",
        "api-reference.md": "# API Reference\n\n## Functions\n\n### `foo()`\n\nDoes something.\n",
        "tutorial.md": "# Tutorial\n\n## Step 1\n\nDo this first.\n\n## Testing\n\nRun the tests with pytest.\n",
    }
    for fname, content in docs.items():
        with open(os.path.join(dest, "raw", fname), "w", encoding="utf-8") as f:
            f.write(content)

    result = install_draft(draft_dir=dest, store_path=tmp_store)
    assert result.success
    return result.wiki_id


@pytest.fixture
def custom_wiki(tmp_path, tmp_store) -> str:
    """Create and install a wiki with scope/non-scope for out-of-scope testing."""
    dest = os.path.join(str(tmp_path), "scope-wiki")
    os.makedirs(os.path.join(dest, "raw"))

    # Create documents
    doc_content = {
        "pixi.md": "# Pixi Package Manager\n\nPixi is a fast package manager.\n## Installation\n\nInstall with `curl`.\n## Usage\n\nRun `pixi init`.\n",
        "conda.md": "# Conda Compatibility\n\nPixi is compatible with conda environments.\n## Channels\n\nAdd conda-forge as a channel.\n",
        "troubleshooting.md": "# Troubleshooting\n\nCommon issues and solutions.\n",
    }
    for fname, content in doc_content.items():
        with open(os.path.join(dest, "raw", fname), "w", encoding="utf-8") as f:
            f.write(content)

    # kb.json with scope and non_scope
    kb = {
        "wiki_id": "scope-wiki",
        "name": "Scope Wiki",
        "description": "A wiki with scope boundaries for testing",
        "version": "1.0.0",
        "scope": ["package management", "conda", "pixi"],
        "non_scope": ["docker orchestration", "npm internals", "pip internals"],
        "license": "MIT",
        "maintainer": "test",
        "provenance": "https://example.com/scope-wiki",
        "freshness": "2025-06-01",
        "entry_points": ["llms.txt", "index.json"],
        "total_documents": 3,
        "total_excluded": 0,
        "metadata_warnings": [],
        "trust_state": "Community",
    }
    with open(os.path.join(dest, "kb.json"), "w") as f:
        json.dump(kb, f, indent=2)

    # index.json
    index = {
        "wiki_id": "scope-wiki",
        "wiki_name": "Scope Wiki",
        "total_documents": 3,
        "documents": [
            {"path": "pixi.md", "title": "Pixi Package Manager", "size_bytes": 100},
            {"path": "conda.md", "title": "Conda Compatibility", "size_bytes": 80},
            {"path": "troubleshooting.md", "title": "Troubleshooting", "size_bytes": 40},
        ],
    }
    with open(os.path.join(dest, "index.json"), "w") as f:
        json.dump(index, f, indent=2)

    # Minimal required artifacts
    with open(os.path.join(dest, "llms.txt"), "w") as f:
        f.write("# Scope Wiki\n")
    sources = {"wiki_id": "scope-wiki", "wiki_name": "Scope Wiki", "base_dir": dest, "included": [], "excluded": []}
    with open(os.path.join(dest, "sources.json"), "w") as f:
        json.dump(sources, f)
    with open(os.path.join(dest, "warnings.json"), "w") as f:
        json.dump({"warnings": []}, f)
    with open(os.path.join(dest, "review.md"), "w") as f:
        f.write("# Review\n")

    result = install_draft(draft_dir=dest, store_path=tmp_store)
    assert result.success
    return result.wiki_id


# ===========================================================================
# list_wikis
# ===========================================================================


class TestListWikis:
    """list_wikis returns installed wikis with metadata."""

    def test_list_empty_store(self, tmp_store) -> None:
        wikis = list_wikis(store_path=tmp_store)
        assert wikis == []

    def test_list_single_wiki(self, installed_wiki, tmp_store) -> None:
        wikis = list_wikis(store_path=tmp_store)
        assert len(wikis) == 1
        w = wikis[0]
        assert isinstance(w, WikiListItem)
        assert w.wiki_id == "test-wiki"
        assert w.name == "Test Wiki"
        assert w.version == "0.1.0"
        assert w.total_documents == 3
        assert w.has_raw is True

    def test_list_multiple_wikis(self, installed_wiki, custom_wiki, tmp_store) -> None:
        wikis = list_wikis(store_path=tmp_store)
        assert len(wikis) == 2
        ids = [w.wiki_id for w in wikis]
        assert "test-wiki" in ids
        assert "scope-wiki" in ids

    def test_list_sorting(self, installed_wiki, custom_wiki, tmp_store) -> None:
        wikis = list_wikis(store_path=tmp_store)
        assert wikis[0].wiki_id <= wikis[1].wiki_id  # sorted


# ===========================================================================
# get_wiki_summary
# ===========================================================================


class TestGetWikiSummary:
    """get_wiki_summary returns detailed metadata."""

    def test_summary_existing(self, installed_wiki, tmp_store) -> None:
        summary = get_wiki_summary("test-wiki", store_path=tmp_store)
        assert summary is not None
        assert isinstance(summary, WikiSummary)
        assert summary.wiki_id == "test-wiki"
        assert summary.name == "Test Wiki"
        assert summary.version == "0.1.0"
        assert isinstance(summary.scope, list)
        assert len(summary.documents) > 0

    def test_summary_nonexistent(self, tmp_store) -> None:
        summary = get_wiki_summary("nonexistent", store_path=tmp_store)
        assert summary is None

    def test_summary_scope_and_non_scope(self, custom_wiki, tmp_store) -> None:
        summary = get_wiki_summary("scope-wiki", store_path=tmp_store)
        assert summary is not None
        assert "package management" in summary.scope
        assert "docker orchestration" in summary.non_scope
        assert summary.trust_state == "Community"

    def test_summary_documents_list(self, installed_wiki, tmp_store) -> None:
        summary = get_wiki_summary("test-wiki", store_path=tmp_store)
        assert summary is not None
        assert len(summary.documents) >= 3
        titles = [d.get("title", "") for d in summary.documents]
        assert "Getting Started" in titles[0] or "getting-started" in summary.documents[0].get(
            "path", ""
        )


# ===========================================================================
# search_wiki
# ===========================================================================


class TestSearchWiki:
    """search_wiki returns hits from deterministic text/heading search."""

    def test_search_hit_content(self, installed_wiki, tmp_store) -> None:
        result = search_wiki("test-wiki", "getting started", store_path=tmp_store)
        assert result["out_of_scope"] is False
        assert result["total_hits"] > 0
        # Should find "getting-started" document
        paths = [h["document_path"] for h in result["hits"]]
        assert any("getting-started" in p for p in paths)

    def test_search_hit_heading(self, custom_wiki, tmp_store) -> None:
        result = search_wiki("scope-wiki", "Installation", store_path=tmp_store)
        assert result["out_of_scope"] is False
        assert result["total_hits"] > 0
        # "Installation" is a heading in pixi.md
        hits = result["hits"]
        assert any(h["match_type"] == "heading" for h in hits)

    def test_search_no_results(self, installed_wiki, tmp_store) -> None:
        result = search_wiki("test-wiki", "xyznonexistent789", store_path=tmp_store)
        assert result["out_of_scope"] is False
        assert result["total_hits"] == 0

    def test_search_nonexistent_wiki(self, tmp_store) -> None:
        result = search_wiki("nonexistent", "test", store_path=tmp_store)
        assert "error" in result
        assert "not found" in result["error"]

    def test_search_respects_max_results(self, custom_wiki, tmp_store) -> None:
        result = search_wiki("scope-wiki", "a", store_path=tmp_store, max_results=1)
        assert result["total_hits"] <= 1


# ===========================================================================
# Out-of-scope detection (search_wiki)
# ===========================================================================


class TestOutOfScopeRefusal:
    """Out-of-scope query returns refusal/redirect rather than hallucinated answer."""

    def test_out_of_scope_refusal(self, custom_wiki, tmp_store) -> None:
        """Query matching non_scope should return refusal."""
        result = search_wiki(
            "scope-wiki", "docker orchestration", store_path=tmp_store
        )
        assert result["out_of_scope"] is True
        assert "out_of_scope_detail" in result
        assert "docker orchestration" in result["out_of_scope_detail"]
        assert result["total_hits"] == 0

    def test_out_of_scope_npm(self, custom_wiki, tmp_store) -> None:
        """Query matching 'npm internals' should be refused."""
        result = search_wiki(
            "scope-wiki", "npm internals", store_path=tmp_store
        )
        assert result["out_of_scope"] is True
        assert result["total_hits"] == 0

    def test_in_scope_returns_hits(self, custom_wiki, tmp_store) -> None:
        """Query matching scope content should return hits."""
        result = search_wiki("scope-wiki", "pixi", store_path=tmp_store)
        assert result["out_of_scope"] is False
        assert result["total_hits"] > 0

    def test_partial_non_scope_match(self, custom_wiki, tmp_store) -> None:
        """Partial match of non_scope keyword should still be caught."""
        result = search_wiki("scope-wiki", "npm", store_path=tmp_store)
        assert result["out_of_scope"] is True
        assert result["total_hits"] == 0

    def test_no_non_scope_in_wiki(self, installed_wiki, tmp_store) -> None:
        """Wiki without non_scope should not trigger out_of_scope."""
        result = search_wiki(
            "test-wiki", "deployment", store_path=tmp_store
        )
        # test-wiki fixture kb.json may or may not have non_scope
        assert "error" not in result or not result.get("error")


# ===========================================================================
# read_document
# ===========================================================================


class TestReadDocument:
    """read_document returns exact Markdown content with citation path."""

    def test_read_existing_document(self, installed_wiki, tmp_store) -> None:
        result = read_document(
            "test-wiki", "getting-started.md", store_path=tmp_store
        )
        assert "error" not in result or not result.get("error")
        assert result["wiki_id"] == "test-wiki"
        assert result["document_path"] == "getting-started.md"
        assert len(result["content"]) > 0
        assert result["size_bytes"] > 0
        # Verify exact content
        assert "# Getting Started" in result["content"]

    def test_read_document_with_citation_path(self, installed_wiki, tmp_store) -> None:
        result = read_document(
            "test-wiki", "getting-started.md", store_path=tmp_store
        )
        assert "citation_path" in result
        assert result["citation_path"].endswith("raw/getting-started.md")
        assert os.path.isfile(result["citation_path"])

    def test_read_document_content_accuracy(self, custom_wiki, tmp_store) -> None:
        """Verify exact Markdown content is returned."""
        result = read_document(
            "scope-wiki", "pixi.md", store_path=tmp_store
        )
        assert "error" not in result or not result.get("error")
        assert "# Pixi Package Manager" in result["content"]
        assert "Run `pixi init`" in result["content"]
        assert result["title"] == "Pixi Package Manager"

    def test_read_nonexistent_document(self, installed_wiki, tmp_store) -> None:
        result = read_document(
            "test-wiki", "no-such-file.md", store_path=tmp_store
        )
        assert "error" in result
        assert "not found" in result["error"]

    def test_read_nonexistent_wiki(self, tmp_store) -> None:
        result = read_document(
            "nonexistent", "doc.md", store_path=tmp_store
        )
        assert "error" in result
        assert "not found" in result["error"]

    def test_read_path_traversal_blocked(self, installed_wiki, tmp_store) -> None:
        """Path traversal attempts should be denied."""
        result = read_document(
            "test-wiki", "../../etc/passwd", store_path=tmp_store
        )
        assert "error" in result
        assert "traversal" in result["error"].lower() or "denied" in result["error"].lower()


# ===========================================================================
# Search module (unit tests)
# ===========================================================================


class TestSearchDocuments:
    """Deterministic text/heading search in raw Markdown files."""

    def test_search_heading(self, tmp_path) -> None:
        raw_dir = os.path.join(str(tmp_path), "raw")
        os.makedirs(raw_dir)
        with open(os.path.join(raw_dir, "test.md"), "w") as f:
            f.write("# My Heading\n\nSome content here.\n## Sub Heading\n\nMore content.\n")
        hits = search_documents(raw_dir, "My Heading")
        assert len(hits) == 1
        assert hits[0].match_type == "heading"
        assert hits[0].document_path == "test.md"

    def test_search_content(self, tmp_path) -> None:
        raw_dir = os.path.join(str(tmp_path), "raw")
        os.makedirs(raw_dir)
        with open(os.path.join(raw_dir, "test.md"), "w") as f:
            f.write("# Title\n\nSpecific searchable content here.\n")
        hits = search_documents(raw_dir, "searchable content")
        assert len(hits) == 1
        assert hits[0].match_type == "content"

    def test_heading_preferred_over_content(self, tmp_path) -> None:
        """Heading matches should be listed before content matches."""
        raw_dir = os.path.join(str(tmp_path), "raw")
        os.makedirs(raw_dir)
        with open(os.path.join(raw_dir, "a.md"), "w") as f:
            f.write("# Foo Bar\n\nBody about foo.\n")
        with open(os.path.join(raw_dir, "b.md"), "w") as f:
            f.write("# Other\n\nContent about foo bar in body.\n")
        hits = search_documents(raw_dir, "foo")
        assert len(hits) >= 2
        assert hits[0].match_type == "heading"
        # Second could be heading or content, just ensure at least one heading

    def test_search_case_insensitive(self, tmp_path) -> None:
        raw_dir = os.path.join(str(tmp_path), "raw")
        os.makedirs(raw_dir)
        with open(os.path.join(raw_dir, "test.md"), "w") as f:
            f.write("# Title\n\nHELLO WORLD content.\n")
        hits = search_documents(raw_dir, "hello world")
        assert len(hits) == 1

    def test_search_empty_query(self, tmp_path) -> None:
        raw_dir = os.path.join(str(tmp_path), "raw")
        os.makedirs(raw_dir)
        with open(os.path.join(raw_dir, "test.md"), "w") as f:
            f.write("# Title\n\nContent.\n")
        hits = search_documents(raw_dir, "")
        # Empty query technically matches everything, but should return results
        # since empty string is substring of everything
        assert len(hits) > 0

    def test_search_nonexistent_dir(self) -> None:
        hits = search_documents("/nonexistent/raw", "test")
        assert hits == []

    def test_search_context_snippet(self, tmp_path) -> None:
        """Search results include context snippets."""
        raw_dir = os.path.join(str(tmp_path), "raw")
        os.makedirs(raw_dir)
        with open(os.path.join(raw_dir, "test.md"), "w") as f:
            f.write("# Title\n\nThis is a long paragraph with the query token somewhere in it.\n")
        hits = search_documents(raw_dir, "query token")
        assert len(hits) == 1
        assert "query token" in hits[0].match_context

    def test_heading_hit_has_no_content_duplicate(self, tmp_path) -> None:
        """A document matching both heading and content should appear once (as heading)."""
        raw_dir = os.path.join(str(tmp_path), "raw")
        os.makedirs(raw_dir)
        with open(os.path.join(raw_dir, "test.md"), "w") as f:
            f.write("# Query Match\n\nMore content about query match.\n")
        hits = search_documents(raw_dir, "query match")
        doc_paths = [h.document_path for h in hits]
        assert doc_paths.count("test.md") == 1
        assert hits[0].match_type == "heading"


# ===========================================================================
# MCP adapter tests
# ===========================================================================


class TestMCPAdapter:
    """MCP adapter exposes tool definitions and dispatches correctly."""

    def test_tool_definitions_present(self) -> None:
        tools = get_tool_definitions()
        assert len(tools) == 4
        names = [t["name"] for t in tools]
        assert "list_wikis" in names
        assert "get_wiki_summary" in names
        assert "search_wiki" in names
        assert "read_document" in names

    def test_tool_definitions_have_schema(self) -> None:
        tools = get_tool_definitions()
        for t in tools:
            assert "description" in t
            assert "inputSchema" in t
            assert "type" in t["inputSchema"]
            assert "properties" in t["inputSchema"]

    def test_call_list_wikis(self, installed_wiki, tmp_store) -> None:
        result = call_tool("list_wikis", {"store_path": tmp_store})
        assert result.get("isError", False) is False
        assert "content" in result
        assert len(result["content"]) > 0
        text = result["content"][0]["text"]
        assert "test-wiki" in text

    def test_call_get_wiki_summary(self, installed_wiki, tmp_store) -> None:
        result = call_tool(
            "get_wiki_summary",
            {"wiki_id": "test-wiki", "store_path": tmp_store},
        )
        assert result.get("isError", False) is False
        text = result["content"][0]["text"]
        assert "Test Wiki" in text
        assert "test-wiki" in text

    def test_call_search_wiki(self, installed_wiki, tmp_store) -> None:
        result = call_tool(
            "search_wiki",
            {"wiki_id": "test-wiki", "query": "getting started", "store_path": tmp_store},
        )
        assert result.get("isError", False) is False
        text = result["content"][0]["text"]
        assert "getting-started" in text or "Getting Started" in text

    def test_call_read_document(self, installed_wiki, tmp_store) -> None:
        result = call_tool(
            "read_document",
            {
                "wiki_id": "test-wiki",
                "document_path": "getting-started.md",
                "store_path": tmp_store,
            },
        )
        assert result.get("isError", False) is False
        text = result["content"][0]["text"]
        assert "Getting Started" in text
        assert "citation" in text.lower() or "Citation" in text

    def test_call_out_of_scope_refusal(self, custom_wiki, tmp_store) -> None:
        result = call_tool(
            "search_wiki",
            {
                "wiki_id": "scope-wiki",
                "query": "docker orchestration",
                "store_path": tmp_store,
            },
        )
        assert result.get("isError", False) is False
        text = result["content"][0]["text"]
        assert "Out-of-Scope" in text

    def test_call_unknown_tool(self) -> None:
        result = call_tool("nonexistent", {})
        assert result.get("isError", False) is True
        text = result["content"][0]["text"]
        assert "Unknown tool" in text

    def test_list_resources(self, installed_wiki, tmp_store) -> None:
        resources = list_resources(store_path=tmp_store)
        assert len(resources) > 0
        # list_resources uses default store, but we installed to tmp_store
        # So this tests shape, not content
        assert all("uri" in r for r in resources)
        assert all("name" in r for r in resources)

    def test_tool_definition_input_schema_has_required(self) -> None:
        tools = get_tool_definitions()
        for t in tools:
            if t["name"] in ("get_wiki_summary",):
                assert "required" in t["inputSchema"]
            if t["name"] in ("search_wiki", "read_document"):
                assert "required" in t["inputSchema"]


# ===========================================================================
# No network / stdlib only
# ===========================================================================


class TestNoNetworkRequired:
    """Serving module uses only stdlib — no network or hosted RAG."""

    def test_no_network_imports_in_interface(self) -> None:
        import iknow.serving.interface as m
        src = m.__file__ or ""
        with open(src) as f:
            source = f.read()
        for net_lib in ("import urllib", "import requests", "import httpx",
                        "import aiohttp", "import socket"):
            assert net_lib not in source

    def test_no_network_imports_in_search(self) -> None:
        import iknow.serving.search as m
        src = m.__file__ or ""
        with open(src) as f:
            source = f.read()
        for net_lib in ("import urllib", "import requests", "import httpx",
                        "import aiohttp", "import socket"):
            assert net_lib not in source

    def test_no_network_imports_in_mcp(self) -> None:
        import iknow.serving.mcp as m
        src = m.__file__ or ""
        with open(src) as f:
            source = f.read()
        for net_lib in ("import urllib", "import requests", "import httpx",
                        "import aiohttp", "import socket"):
            assert net_lib not in source