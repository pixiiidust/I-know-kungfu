"""Core serving functions for installed wikis.

Seam: ``list_wikis()``, ``get_wiki_summary()``, ``search_wiki()``, and
``read_document()`` expose read-only behaviour over locally installed wikis
using only stdlib and the installed store from ``iknow.store``.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import Any, Dict, List

from iknow.serving.search import SearchHit, search_documents
from iknow.store import InstalledWiki, get_installed, list_installed


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------


@dataclass
class WikiListItem:
    """Summary data for one wiki in a list response."""

    wiki_id: str
    name: str
    version: str
    description: str
    total_documents: int
    has_raw: bool
    installed_at: str


@dataclass
class WikiSummary:
    """Detailed metadata about an installed wiki, including contract info."""

    wiki_id: str
    name: str
    description: str
    version: str
    scope: List[str]
    non_scope: List[str]
    provenance: str
    freshness: str
    license: str
    trust_state: str
    total_documents: int
    installed_at: str
    documents: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class DocumentResult:
    """Content and metadata for a single wiki document."""

    wiki_id: str
    document_path: str
    title: str
    content: str
    size_bytes: int


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _load_index(wiki_dir: str) -> Dict[str, Any]:
    """Load and return the index.json for an installed wiki."""
    idx_path = os.path.join(wiki_dir, "index.json")
    if not os.path.isfile(idx_path):
        return {"documents": []}
    try:
        with open(idx_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return {"documents": []}


def _load_kb_json(wiki_dir: str) -> Dict[str, Any]:
    """Load and return kb.json for an installed wiki."""
    kb_path = os.path.join(wiki_dir, "kb.json")
    if not os.path.isfile(kb_path):
        return {}
    try:
        with open(kb_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return {}


def _find_doc_title(doc_path: str, index_docs: List[Dict[str, Any]]) -> str:
    """Look up the display title for a document path from index.json."""
    rel = doc_path
    if rel.startswith("raw/"):
        rel = rel[4:]
    for entry in index_docs:
        index_path = entry.get("path", "")
        if index_path == rel or index_path == doc_path:
            return entry.get("title", rel)
    # Fallback: derive title from filename
    base = os.path.splitext(os.path.basename(doc_path))[0]
    return base.replace("-", " ").replace("_", " ").title()


def _is_out_of_scope(query: str, kb: Dict[str, Any]) -> bool:
    """Check whether *query* appears to be out of scope for this wiki.

    Uses the ``non_scope`` list from kb.json and simple substring matching.
    Returns ``True`` when the query matches any non_scope keyword or phrase.
    """
    non_scope: List[str] = kb.get("non_scope", [])
    if not non_scope:
        return False
    q_lower = query.lower()
    for keyword in non_scope:
        kw_lower = keyword.lower()
        # Check if the query contains the non_scope keyword OR the keyword contains the query
        if kw_lower in q_lower or q_lower in kw_lower:
            return True
    return False


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def list_wikis(store_path: str | None = None) -> List[WikiListItem]:
    """List all installed wikis with summary metadata.

    Parameters
    ----------
    store_path:
        Override the installed store root.  Defaults to
        ``get_installed_store_path()``.

    Returns
    -------
    List[WikiListItem]
        Sorted list of installed wikis.
    """
    installed = list_installed(store_path=store_path)
    return [
        WikiListItem(
            wiki_id=w.wiki_id,
            name=w.name,
            version=w.version,
            description=w.description,
            total_documents=w.total_documents,
            has_raw=w.has_raw,
            installed_at=w.installed_at,
        )
        for w in installed
    ]


def get_wiki_summary(
    wiki_id: str, store_path: str | None = None
) -> WikiSummary | None:
    """Return detailed summary for a single installed wiki.

    Includes scope, non-scope, provenance, and document listing from
    ``index.json``.

    Parameters
    ----------
    wiki_id:
        Wiki identifier (directory name within the store).
    store_path:
        Override the installed store root.

    Returns
    -------
    WikiSummary | None
        Detailed metadata, or ``None`` if the wiki is not installed.
    """
    installed: InstalledWiki | None = get_installed(wiki_id, store_path=store_path)
    if installed is None:
        return None

    wiki_dir = installed.installed_at
    kb = _load_kb_json(wiki_dir)
    index = _load_index(wiki_dir)

    return WikiSummary(
        wiki_id=installed.wiki_id,
        name=installed.name,
        description=installed.description,
        version=installed.version,
        scope=kb.get("scope", []),
        non_scope=kb.get("non_scope", []),
        provenance=kb.get("provenance", ""),
        freshness=kb.get("freshness", ""),
        license=kb.get("license", ""),
        trust_state=kb.get("trust_state", "Unknown"),
        total_documents=installed.total_documents,
        installed_at=installed.installed_at,
        documents=index.get("documents", []),
    )


def search_wiki(
    wiki_id: str,
    query: str,
    store_path: str | None = None,
    max_results: int = 20,
) -> Dict[str, Any]:
    """Search inside one installed wiki.

    Uses deterministic text/heading search — no vector DB required.
    Detects out-of-scope queries against ``kb.json``'s ``non_scope`` list.

    Parameters
    ----------
    wiki_id:
        Wiki identifier.
    query:
        Search query string.
    store_path:
        Override the installed store root.
    max_results:
        Maximum number of search hits to return (default 20).

    Returns
    -------
    Dict
        JSON-serialisable result dict with keys:
        - ``wiki_id`` (str)
        - ``query`` (str)
        - ``out_of_scope`` (bool) — ``True`` if query matches non_scope
        - ``out_of_scope_detail`` (str, optional) — explanation when
          out_of_scope is True
        - ``hits`` (List[SearchHit])
        - ``total_hits`` (int)
    """
    installed: InstalledWiki | None = get_installed(wiki_id, store_path=store_path)
    if installed is None:
        return {
            "wiki_id": wiki_id,
            "query": query,
            "out_of_scope": False,
            "hits": [],
            "total_hits": 0,
            "error": f"Wiki '{wiki_id}' not found",
        }

    wiki_dir = installed.installed_at
    kb = _load_kb_json(wiki_dir)
    index = _load_index(wiki_dir)
    index_docs = index.get("documents", [])

    # Out-of-scope detection
    if _is_out_of_scope(query, kb):
        return {
            "wiki_id": wiki_id,
            "query": query,
            "out_of_scope": True,
            "out_of_scope_detail": (
                f"The query '{query}' matches topics explicitly listed as "
                f"out of scope for wiki '{installed.name}'. "
                f"Non-scope topics: {kb.get('non_scope', [])}. "
                "Please consult a different knowledge base for this topic."
            ),
            "hits": [],
            "total_hits": 0,
        }

    # Perform search
    raw_dir = os.path.join(wiki_dir, "raw")
    hits = search_documents(raw_dir, query, max_results=max_results)

    # Attach titles from index
    for hit in hits:
        if not hit.title:
            hit.title = _find_doc_title(hit.document_path, index_docs)

    return {
        "wiki_id": wiki_id,
        "query": query,
        "out_of_scope": False,
        "hits": [h.to_dict() for h in hits],
        "total_hits": len(hits),
    }


def read_document(
    wiki_id: str,
    document_path: str,
    store_path: str | None = None,
) -> Dict[str, Any]:
    """Read the exact Markdown content of a wiki document.

    Parameters
    ----------
    wiki_id:
        Wiki identifier.
    document_path:
        Relative path to the document within the wiki's ``raw/`` directory
        (e.g. ``doc1.md`` or ``getting-started.md``).
    store_path:
        Override the installed store root.

    Returns
    -------
    Dict
        JSON-serialisable result dict with keys:
        - ``wiki_id`` (str)
        - ``document_path`` (str) — canonical path within the wiki
        - ``title`` (str)
        - ``content`` (str) — exact Markdown content
        - ``size_bytes`` (int)
        - ``citation_path`` (str) — full filesystem path suitable for citation
        - ``error`` (str, optional) — present only on failure
    """
    installed: InstalledWiki | None = get_installed(wiki_id, store_path=store_path)
    if installed is None:
        return {
            "wiki_id": wiki_id,
            "document_path": document_path,
            "content": "",
            "size_bytes": 0,
            "citation_path": "",
            "title": "",
            "error": f"Wiki '{wiki_id}' not found",
        }

    wiki_dir = installed.installed_at
    raw_dir = os.path.join(wiki_dir, "raw")

    # Normalise path: if it already starts with raw/, strip it
    clean_path = document_path
    if clean_path.startswith("raw/"):
        clean_path = clean_path[4:]

    raw_root = os.path.normpath(raw_dir)
    abs_path = os.path.normpath(os.path.join(raw_root, clean_path))

    # Safety: ensure the resolved path is within the raw directory
    if os.path.commonpath([raw_root, abs_path]) != raw_root:
        return {
            "wiki_id": wiki_id,
            "document_path": document_path,
            "content": "",
            "size_bytes": 0,
            "citation_path": "",
            "title": "",
            "error": "Path traversal denied",
        }

    if not os.path.isfile(abs_path):
        return {
            "wiki_id": wiki_id,
            "document_path": document_path,
            "content": "",
            "size_bytes": 0,
            "citation_path": abs_path,
            "title": "",
            "error": f"Document not found: {document_path}",
        }

    try:
        with open(abs_path, "r", encoding="utf-8") as f:
            content = f.read()
    except OSError as exc:
        return {
            "wiki_id": wiki_id,
            "document_path": document_path,
            "content": "",
            "size_bytes": 0,
            "citation_path": abs_path,
            "title": "",
            "error": f"Failed to read document: {exc}",
        }

    index = _load_index(wiki_dir)
    title = _find_doc_title(clean_path, index.get("documents", []))
    size_bytes = os.path.getsize(abs_path)

    return {
        "wiki_id": wiki_id,
        "document_path": clean_path,
        "title": title,
        "content": content,
        "size_bytes": size_bytes,
        "citation_path": abs_path,
    }