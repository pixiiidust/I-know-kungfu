"""Parse ``iknow.yaml`` configuration for the Draft Wiki Compiler.

Provides a minimal YAML-like parser that handles the JSON-compatible subset
needed for wiki configuration.  No external dependencies (no PyYAML).

Supported syntax:
- Key-value pairs (``key: value``)
- Strings, integers, booleans, and ``null``
- Nested dicts via indentation (2 or 4 spaces)
- Lists via ``- item`` under a key
- Comments (``# ...``)

Unsupported:
- Flow-style YAML (``{a: b}``, ``[1, 2]``)
- Multi-line strings (``|``, ``>``)
- Anchors, aliases, tags, or complex types.
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


# ---------------------------------------------------------------------------
# Configuration model
# ---------------------------------------------------------------------------


@dataclass
class CompilerConfig:
    """Deserialised contents of a wiki's ``iknow.yaml``."""

    # Identity
    wiki_id: str = ""
    name: str = ""
    description: str = ""
    version: str = ""

    # Scope
    scope: List[str] = field(default_factory=list)
    non_scope: List[str] = field(default_factory=list)

    # Sources & filtering
    sources: List[str] = field(default_factory=list)
    include: List[str] = field(default_factory=lambda: ["*.md"])
    exclude: List[str] = field(default_factory=list)

    # Provenance
    license: str = ""
    maintainer: str = ""
    provenance: str = ""
    freshness: str = ""

    # Serving entry points
    entry_points: List[str] = field(default_factory=lambda: ["llms.txt", "index.json", "markdown"])

    # Internal: warnings collected during parsing
    _warnings: List[str] = field(default_factory=list)

    @property
    def warnings(self) -> List[str]:
        return list(self._warnings)


# ---------------------------------------------------------------------------
# Minimal YAML-compatible parser
# ---------------------------------------------------------------------------

_KEY_VALUE_RE = re.compile(r"^(\s*)([\w_-]+)\s*:\s*(.*?)$")
_LIST_ITEM_RE = re.compile(r"^(\s*)-\s+(.*)$")
_EMPTY_OR_COMMENT_RE = re.compile(r"^\s*(#.*)?$")


def _coerce_scalar(raw: str) -> Any:
    """Coerce a string scalar to bool / int / str as appropriate."""
    v = raw.strip()
    if v == "":
        return ""
    if v.lower() in ("true", "yes", "on"):
        return True
    if v.lower() in ("false", "no", "off"):
        return False
    if v.lower() in ("null", "none", "~"):
        return None
    try:
        return int(v)
    except ValueError:
        pass
    if len(v) >= 2 and v[0] == v[-1] and v[0] in ('"', "'"):
        return v[1:-1]
    return v


def parse_yaml_simple(text: str) -> dict:
    """Parse a YAML-like string into a nested Python dict.

    Algorithm:
    1. Tokenize each line into (indent, kind, data).
    2. Walk tokens to build the tree.

    A "pending" key (key with no value) is resolved by looking at the next
    block of lines at deeper indent.  If they are list items, the key's value
    is a list.  If they are key-value pairs, the key's value is a nested dict.
    """
    # --- Pass 1: tokenize ---
    tokens: list[tuple[int, str, Any]] = []

    for line in text.split("\n"):
        if _EMPTY_OR_COMMENT_RE.match(line):
            continue
        kv = _KEY_VALUE_RE.match(line)
        if kv:
            indent = len(kv.group(1))
            key = kv.group(2)
            raw_val = kv.group(3).strip()
            if raw_val == "":
                tokens.append((indent, "key_empty", key))
            else:
                tokens.append((indent, "key_val", (key, _coerce_scalar(raw_val))))
            continue
        li = _LIST_ITEM_RE.match(line)
        if li:
            indent = len(li.group(1))
            tokens.append((indent, "list_item", _coerce_scalar(li.group(2))))
            continue

    # --- Pass 2: build tree ---
    root: dict = {}
    # Stack of (indent, dict) — tracks the current nesting path
    indent_stack: list[tuple[int, dict]] = [(0, root)]
    # Track keys that were defined with "key:" (empty value) but whose
    # value hasn't been resolved yet. Maps indent → key_name.
    pending: dict[int, str] = {}
    # Track lists being built. Maps indent → [values].
    lists: dict[int, list] = {}
    # Track which pending key a list belongs to. Maps indent → key_name.
    list_owner: dict[int, str] = {}

    i = 0
    while i < len(tokens):
        indent, kind, data = tokens[i]

        if kind == "key_empty":
            key = data

            # Close any lists at this or deeper indent
            _flush_lists(lists, list_owner, indent_stack, indent)

            # Pop stack to this indent level
            while indent_stack and indent_stack[-1][0] >= indent:
                indent_stack.pop()

            parent = indent_stack[-1][1] if indent_stack else root

            # Look ahead to see what follows — if the next tokens at deeper
            # indent are list items, this key is a list; if key-value pairs,
            # it's a nested dict.
            next_kind = _peek_kind(tokens, i + 1, indent)

            if next_kind == "list":
                # This key is a list — set empty list placeholder
                parent[key] = []
                # Track that subsequent list items at deeper indent belong here
                list_owner[indent + 2] = key
                pending[indent] = key
                lists[indent + 2] = []
                indent_stack.append((indent, parent))
            elif next_kind == "dict":
                # This key is a nested dict
                new_dict: dict = {}
                parent[key] = new_dict
                pending[indent] = key
                indent_stack.append((indent, new_dict))
            else:
                # Nothing follows — empty list
                parent[key] = []

            i += 1

        elif kind == "key_val":
            key, value = data

            # Close any lists at this or deeper indent
            _flush_lists(lists, list_owner, indent_stack, indent)

            # Pop stack to this indent level
            while indent_stack and indent_stack[-1][0] >= indent:
                indent_stack.pop()

            parent = indent_stack[-1][1] if indent_stack else root
            parent[key] = value

            # Remove this key from pending if present
            pending.pop(indent, None)

            i += 1

        elif kind == "list_item":
            value = data

            # Find which pending key this list belongs to
            # Look for a pending key at a shallower indent
            owner_key = None
            for pi in sorted(pending.keys(), reverse=True):
                if pi < indent:
                    owner_key = pending[pi]
                    break

            if owner_key is None:
                i += 1
                continue  # orphan list item

            # Start or continue the list bucket
            if indent not in lists:
                lists[indent] = []
            lists[indent].append(value)

            i += 1

    # Final flush of any remaining lists
    _flush_lists(lists, list_owner, indent_stack, 0)

    return root


def _peek_kind(tokens: list, start: int, current_indent: int) -> str:
    """Look ahead from *start* to determine if the next block is list or dict.

    Returns "list" if the first token at deeper indent is a list_item,
    "dict" if it's a key_empty/key_val, or "none".
    """
    for j in range(start, len(tokens)):
        ti, tk, _ = tokens[j]
        if ti <= current_indent:
            # Back to same or shallower indent — end of block
            break
        if tk == "list_item":
            return "list"
        if tk in ("key_empty", "key_val"):
            return "dict"
    return "none"


def _flush_lists(
    lists: dict,
    list_owner: dict,
    indent_stack: list,
    up_to_indent: int,
) -> None:
    """Write accumulated lists into their owner dicts.

    Any list accumulated at *indent* >= *up_to_indent* is flushed.
    """
    for li in sorted(lists.keys(), reverse=True):
        if li >= up_to_indent:
            owner_key = list_owner.get(li)
            if owner_key:
                # Find the parent dict for this list — it's the dict at
                # indent (li - 2) in the stack
                for stack_indent, stack_dict in reversed(indent_stack):
                    if stack_indent < li:
                        stack_dict[owner_key] = lists[li]
                        break
            lists.pop(li, None)
            list_owner.pop(li, None)


# ---------------------------------------------------------------------------
# Public API: parse_config
# ---------------------------------------------------------------------------


def parse_config(path: str) -> CompilerConfig:
    """Parse an ``iknow.yaml`` file and return a ``CompilerConfig``.

    Parameters
    ----------
    path:
        Filesystem path to ``iknow.yaml``.

    Returns
    -------
    CompilerConfig
        Populated configuration; warnings are available via
        ``config.warnings``.
    """
    config = CompilerConfig()
    if not os.path.isfile(path):
        config._warnings.append(f"Configuration file not found: {path}")
        return config

    with open(path, "r", encoding="utf-8") as f:
        text = f.read()

    if not text.strip():
        config._warnings.append("Configuration file is empty")
        return config

    try:
        raw = parse_yaml_simple(text)
    except Exception as exc:
        config._warnings.append(f"Failed to parse {path}: {exc}")
        return config

    # Walk the raw dict to populate the config dataclass.
    # Support both flat key layout and nested under a "wiki" key.
    data: dict = raw
    if "wiki" in raw and isinstance(raw["wiki"], dict):
        data = raw["wiki"]

    # Identity
    config.wiki_id = _str_or(data, "id", "")
    config.name = _str_or(data, "name", "")
    config.description = _str_or(data, "description", "")
    config.version = _str_or(data, "version", "")

    # Scope
    config.scope = _str_list(data, "scope")
    config.non_scope = _str_list(data, "non_scope")

    # Sources
    config.sources = _str_list(data, "sources")
    config.include = _str_list(data, "include") or ["*.md"]
    config.exclude = _str_list(data, "exclude")

    # Provenance
    config.license = _str_or(data, "license", "")
    config.maintainer = _str_or(data, "maintainer", "")
    config.provenance = _str_or(data, "provenance", config.provenance)
    config.freshness = _str_or(data, "freshness", config.freshness)

    # Entry points
    config.entry_points = _str_list(data, "entry_points") or ["llms.txt", "index.json", "markdown"]

    # Collect warnings for weak/missing metadata
    if not config.wiki_id:
        config._warnings.append("Missing wiki id — draft directory will use 'unnamed'")
    if not config.name:
        config._warnings.append("Missing wiki name")
    if not config.description:
        config._warnings.append("Missing wiki description — review will note this")
    if not config.license:
        config._warnings.append("Missing license — consider adding one")
    if not config.maintainer:
        config._warnings.append("Missing maintainer — consider adding one")
    if not config.provenance:
        config._warnings.append("Missing provenance — draft is purely local")
    if not config.freshness:
        config._warnings.append("Missing freshness date")
    if not config.sources:
        config._warnings.append("No sources configured — nothing to compile")

    return config


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _str_or(data: dict, key: str, default: str) -> str:
    val = data.get(key, default)
    if not isinstance(val, str):
        return str(val) if val is not None else default
    return val


def _str_list(data: dict, key: str) -> List[str]:
    raw = data.get(key, [])
    if isinstance(raw, list):
        return [str(item) for item in raw if item is not None]
    return []