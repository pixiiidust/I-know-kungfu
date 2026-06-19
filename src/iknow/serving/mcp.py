"""MCP-shaped adapter over installed wiki serving functions.

Seam: exposes ``list_wikis``, ``get_wiki_summary``, ``search_wiki``, and
``read_document`` as a tool-like facade compatible with an MCP tool/resource
interface.  Uses only stdlib — no MCP SDK dependency.  The adapter wraps
the interface layer and returns JSON-serialisable dicts suitable for
serialisation as MCP tool results.

Out-of-scope: queries that match ``non_scope`` metadata return refusal/
redirect metadata rather than hallucinated answers.
"""

from __future__ import annotations

from typing import Any, Dict, List

from iknow.serving.interface import (
    get_wiki_summary,
    list_wikis,
    read_document,
    search_wiki,
)


# ---------------------------------------------------------------------------
# Tool definitions (MCP-shaped metadata)
# ---------------------------------------------------------------------------

TOOL_DEFINITIONS = [
    {
        "name": "list_wikis",
        "description": (
            "List all installed knowledge base wikis with summary metadata "
            "(name, version, description, document count)."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "store_path": {
                    "type": "string",
                    "description": "Override the installed store root path",
                }
            },
        },
    },
    {
        "name": "get_wiki_summary",
        "description": (
            "Return detailed metadata for a single installed wiki, "
            "including scope, non-scope, provenance, license, and full "
            "document listing."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "wiki_id": {
                    "type": "string",
                    "description": "Wiki identifier (directory name in the store)",
                },
                "store_path": {
                    "type": "string",
                    "description": "Override the installed store root path",
                },
            },
            "required": ["wiki_id"],
        },
    },
    {
        "name": "search_wiki",
        "description": (
            "Search inside one installed wiki using deterministic text/heading "
            "matching. Out-of-scope queries are detected and return a refusal/"
            "redirect response instead of hallucinated answers."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "wiki_id": {
                    "type": "string",
                    "description": "Wiki identifier",
                },
                "query": {
                    "type": "string",
                    "description": "Search query string",
                },
                "store_path": {
                    "type": "string",
                    "description": "Override the installed store root path",
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum search results (default 20)",
                    "default": 20,
                },
            },
            "required": ["wiki_id", "query"],
        },
    },
    {
        "name": "read_document",
        "description": (
            "Read the exact Markdown content of a wiki document, returning "
            "the full text, title, size, and a citation filesystem path. "
            "Suitable for citation and attribution."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "wiki_id": {
                    "type": "string",
                    "description": "Wiki identifier",
                },
                "document_path": {
                    "type": "string",
                    "description": (
                        "Relative path to the document within the wiki's "
                        "raw/ directory (e.g. 'getting-started.md')"
                    ),
                },
                "store_path": {
                    "type": "string",
                    "description": "Override the installed store root path",
                },
            },
            "required": ["wiki_id", "document_path"],
        },
    },
]


# ---------------------------------------------------------------------------
# Adapter functions (MCP-shaped tool call dispatchers)
# ---------------------------------------------------------------------------


def list_resources(store_path: str | None = None) -> List[Dict[str, Any]]:
    """Resource-style listing: returns installed wikis as resource URIs.

    Each resource URI is ``wiki://<wiki_id>/`` with metadata as the
    resource description.
    """
    wikis = list_wikis(store_path=store_path)
    resources = []
    for w in wikis:
        resources.append(
            {
                "uri": f"wiki://{w.wiki_id}/",
                "name": w.name,
                "description": w.description,
                "mimeType": "text/markdown",
            }
        )
    return resources


# ---------------------------------------------------------------------------
# Tool dispatcher
# ---------------------------------------------------------------------------


_TOOL_HANDLERS: Dict[str, Any] = {
    "list_wikis": lambda args: {
        "content": [
            {
                "type": "text",
                "text": "\n".join(
                    _format_wiki_line(w) for w in list_wikis(**args)
                ),
            }
        ],
    },
    "get_wiki_summary": lambda args: {
        "content": [
            {
                "type": "text",
                "text": _format_wiki_summary(
                    get_wiki_summary(**args)
                ),
            }
        ],
    },
    "search_wiki": lambda args: {
        "content": [
            {
                "type": "text",
                "text": _format_search_results(
                    search_wiki(**args)
                ),
            }
        ],
    },
    "read_document": lambda args: {
        "content": [
            {
                "type": "text",
                "text": _format_document(
                    read_document(**args)
                ),
            }
        ],
    },
}


# ---------------------------------------------------------------------------
# Formatting helpers
# ---------------------------------------------------------------------------


def _format_wiki_line(item: Any) -> str:
    """Format a wiki list item as a human-readable line."""
    return (
        f"{item.wiki_id:24s}  {item.name:30s}  "
        f"v{item.version:8s}  {item.total_documents} docs"
    )


def _format_wiki_summary(summary: Any | None) -> str:
    """Format a wiki summary as human-readable text."""
    if summary is None:
        return "Wiki not found."
    lines = [
        f"# {summary.name}",
        f"**Wiki ID:** {summary.wiki_id}",
        f"**Version:** {summary.version}",
        f"**Description:** {summary.description}",
        f"**License:** {summary.license}",
        f"**Provenance:** {summary.provenance}",
        f"**Freshness:** {summary.freshness}",
        f"**Trust State:** {summary.trust_state}",
        f"**Total Documents:** {summary.total_documents}",
        f"**Installed At:** {summary.installed_at}",
        "",
        "**Scope:**",
    ]
    for s in summary.scope:
        lines.append(f"- {s}")
    if summary.non_scope:
        lines.append("")
        lines.append("**Non-Scope:**")
        for ns in summary.non_scope:
            lines.append(f"- {ns}")
    lines.append("")
    lines.append("**Documents:**")
    for doc in summary.documents:
        lines.append(f"- {doc.get('title', '')} ({doc.get('path', '')})")
    return "\n".join(lines)


def _format_search_results(result: Dict[str, Any]) -> str:
    """Format search results as human-readable text."""
    if result.get("out_of_scope"):
        return (
            "🚫 Out-of-Scope Query\n\n"
            f"{result.get('out_of_scope_detail', '')}"
        )
    if result.get("error"):
        return f"Error: {result['error']}"
    if not result.get("hits"):
        return f"No results found for '{result.get('query', '')}' in wiki '{result.get('wiki_id', '')}'."

    lines = [
        f"Search results for '{result['query']}' in '{result['wiki_id']}'",
        f"Total hits: {result['total_hits']}",
        "",
    ]
    for i, hit in enumerate(result["hits"], 1):
        marker = "📑" if hit["match_type"] == "heading" else "📄"
        lines.append(f"{marker} {i}. **{hit.get('title', hit['document_path'])}**")
        lines.append(f"   File: {hit['document_path']}")
        lines.append(f"   Match: {hit['match_type']}")
        if hit["match_context"]:
            lines.append(f"   Context: \"{hit['match_context'][:100]}...\"")
        lines.append("")
    return "\n".join(lines)


def _format_document(doc_result: Dict[str, Any]) -> str:
    """Format a document read result as human-readable text."""
    if doc_result.get("error"):
        return f"Error: {doc_result['error']}"
    lines = [
        f"# {doc_result.get('title', doc_result.get('document_path', ''))}",
        f"**Wiki:** {doc_result.get('wiki_id', '')}",
        f"**Path:** {doc_result.get('document_path', '')}",
        f"**Size:** {doc_result.get('size_bytes', 0)} bytes",
        f"**Citation Path:** {doc_result.get('citation_path', '')}",
        "",
        "---",
        "",
        doc_result.get("content", ""),
    ]
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def get_tool_definitions() -> List[Dict[str, Any]]:
    """Return the list of tool definitions for MCP discovery.

    Each definition includes ``name``, ``description``, and
    ``inputSchema``.
    """
    return TOOL_DEFINITIONS


def call_tool(name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Dispatch a tool call by name with the given arguments.

    Parameters
    ----------
    name:
        Tool name (one of 'list_wikis', 'get_wiki_summary', 'search_wiki',
        'read_document').
    arguments:
        Keyword arguments for the underlying function.

    Returns
    -------
    Dict
        An MCP-shaped response dict with a ``content`` list (each item has
        ``type`` and ``text`` keys).
    """
    handler = _TOOL_HANDLERS.get(name)
    if handler is None:
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"Unknown tool: {name}. "
                    f"Available tools: {', '.join(_TOOL_HANDLERS)}",
                }
            ],
            "isError": True,
        }

    try:
        return handler(arguments)
    except Exception as exc:
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"Error executing tool '{name}': {exc}",
                }
            ],
            "isError": True,
        }