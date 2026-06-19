"""Serving module.

Seam: expose installed wikis to agent harnesses — list, summarize, search,
read. The first serving adapter is MCP; ``llms.txt``, raw Markdown, and
``index.json`` remain supported entry points.

v1 adapter: MCP served locally. No cloud MCP hosting.
"""

from iknow.serving.interface import (
    DocumentResult,
    SearchHit,
    WikiListItem,
    WikiSummary,
    get_wiki_summary,
    list_wikis,
    read_document,
    search_wiki,
)

__all__ = [
    "WikiListItem",
    "WikiSummary",
    "SearchHit",
    "DocumentResult",
    "list_wikis",
    "get_wiki_summary",
    "search_wiki",
    "read_document",
]