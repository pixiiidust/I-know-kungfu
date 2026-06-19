"""Deterministic text/heading search over installed wiki raw Markdown files.

Seam: ``search_documents()`` implements substring match on content and
headings across ``*.md`` files in a ``raw/`` directory.  No vector DB,
no hosted RAG, no network — pure stdlib.
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class SearchHit:
    """A single search result."""

    document_path: str
    match_context: str
    match_type: str  # "heading" or "content"
    title: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "document_path": self.document_path,
            "match_context": self.match_context,
            "match_type": self.match_type,
            "title": self.title,
        }


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


_HEADING_RE = re.compile(r"^(#{1,6})\s+(.+)$", re.MULTILINE)


def _extract_headings(content: str) -> List[str]:
    """Return all heading texts from a Markdown document."""
    return [m.group(2).strip() for m in _HEADING_RE.finditer(content)]


def _extract_context(
    content: str,
    query: str,
    window_chars: int = 120,
) -> str:
    """Extract a snippet of text surrounding the first match of *query*."""
    q_lower = query.lower()
    idx = content.lower().find(q_lower)
    if idx < 0:
        return ""

    start = max(0, idx - window_chars // 2)
    end = min(len(content), idx + len(query) + window_chars // 2)

    snippet = content[start:end]
    # Try to break at line boundaries for readability
    if start > 0:
        # Find previous newline or space
        nl = snippet.find("\n")
        if 0 < nl < 40:
            snippet = snippet[nl + 1 :]
    if end < len(content):
        nl = snippet.rfind("\n")
        if nl > len(snippet) - 40:
            snippet = snippet[:nl]

    return snippet.strip()


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def search_documents(
    raw_dir: str,
    query: str,
    max_results: int = 20,
) -> List[SearchHit]:
    """Search Markdown files in *raw_dir* for *query*.

    Matches are determined by substring matching (case-insensitive) on
    both headings and body content.  Heading matches are preferred and
    listed first.

    Parameters
    ----------
    raw_dir:
        Path to the ``raw/`` directory of an installed wiki.
    query:
        Search string (case-insensitive substring match).
    max_results:
        Maximum number of hits to return (default 20).

    Returns
    -------
    List[SearchHit]
        Search results sorted by relevance (heading matches first, then
        content matches).
    """
    if not os.path.isdir(raw_dir):
        return []

    q_lower = query.lower()
    heading_hits: List[SearchHit] = []
    content_hits: List[SearchHit] = []

    for root, _dirs, files in os.walk(raw_dir):
        for entry in sorted(files):
            if not entry.endswith(".md"):
                continue
            filepath = os.path.join(root, entry)
            if not os.path.isfile(filepath):
                continue
            relpath = os.path.relpath(filepath, raw_dir)

            try:
                with open(filepath, "r", encoding="utf-8", errors="replace") as f:
                    content = f.read()
            except OSError:
                continue

            # Check headings first (preferred)
            headings = _extract_headings(content)
            for heading in headings:
                if q_lower in heading.lower():
                    context = _extract_context(content, query)
                    heading_hits.append(
                        SearchHit(
                            document_path=relpath,
                            match_context=context or heading,
                            match_type="heading",
                        )
                    )
                    break  # One heading hit per document

            # Check body content
            if q_lower in content.lower():
                # Skip if we already got a heading hit for this doc
                if any(h.document_path == relpath for h in heading_hits):
                    continue
                context = _extract_context(content, query)
                content_hits.append(
                    SearchHit(
                        document_path=relpath,
                        match_context=context,
                        match_type="content",
                    )
                )

            if len(heading_hits) + len(content_hits) >= max_results:
                break
        if len(heading_hits) + len(content_hits) >= max_results:
            break

    # Heading hits first, then content hits
    combined = heading_hits + content_hits
    return combined[:max_results]