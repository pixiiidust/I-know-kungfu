"""CLI entrypoint for the iknow control plane.

Subcommands
-----------
cookbook list
    List all knowledge base wikis available in the static Cookbook registry.
cookbook inspect <wiki-id>
    Show the full Wiki Contract for a registry wiki.
fit <wiki-id> [--inventory {default|json-path}]
    Check context fit between a registry wiki and the local knowledge inventory.
compile --config <iknow.yaml>
    Compile a private draft wiki from configuration and local Markdown sources.
install <wiki-id> [--draft-dir PATH]
    Install a compiled draft wiki from .kungfu/drafts/<wiki-id>/ into the store.
list
    List all installed wikis.
remove <wiki-id>
    Remove an installed wiki from the store.
serve list
    List installed wikis with detailed metadata.
serve search <wiki-id> <query>
    Search within an installed wiki (with out-of-scope detection).
serve read <wiki-id> <doc-path>
    Read a specific document from an installed wiki.

Environment variables
---------------------
IKNOW_INSTALLED_STORE
    Override the installed wiki store path (default: ~/.iknow/installed/).
"""

from __future__ import annotations

import argparse
import json
import os
import sys

from iknow import __version__
from iknow.compiler import compile_draft
from iknow.fit import compute_fit
from iknow.inventory import get_inventory
from iknow.registry import registry
from iknow.serving import list_wikis, read_document, search_wiki
from iknow.store import (
    get_installed_store_path,
    install_draft,
    list_installed,
    remove_installed,
    summarize,
)

# ---------------------------------------------------------------------------
# Argument builder
# ---------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="iknow",
        description="I-know-kungfu — grow your knowledge base with proven wikis.",
        epilog=(
            "See https://github.com/pixiiidust/I-know-kungfu for documentation.\n"
            "\n"
            "Variant C flow:\n"
            "  cookbook list                     find a wiki\n"
            "  cookbook inspect <wiki-id>        inspect scope & entry points\n"
            "  fit <wiki-id>                     check local fit\n"
            "  compile --config iknow.yaml       compile a local draft\n"
            "  install <wiki-id>                 install the draft\n"
            "  serve search <wiki-id> <query>    inspect proof / refusal"
        ),
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # --- cookbook list ------------------------------------------------------
    cookbook_parser = subparsers.add_parser(
        "cookbook",
        help="List and inspect Cookbook registry wikis.",
    )
    cookbook_sub = cookbook_parser.add_subparsers(
        dest="cookbook_action", help="cookbook subcommand"
    )
    cookbook_list = cookbook_sub.add_parser(
        "list",
        help="List all wikis in the Cookbook registry.",
    )
    cookbook_inspect = cookbook_sub.add_parser(
        "inspect",
        help="Show the full Wiki Contract for a registry wiki.",
    )
    cookbook_inspect.add_argument(
        "wiki_id",
        help="Registry wiki identifier (e.g. agent_workflow_setup).",
    )

    # --- fit -----------------------------------------------------------------
    fit_parser = subparsers.add_parser(
        "fit",
        help="Check context fit between a registry wiki and local inventory.",
    )
    fit_parser.add_argument(
        "wiki_id",
        help="Registry wiki identifier to check fit for.",
    )
    fit_parser.add_argument(
        "--inventory",
        default="default",
        help=(
            "Inventory source: 'default' for bundled fixture, "
            "or a path to a JSON inventory file."
        ),
    )

    # --- compile -------------------------------------------------------------
    compile_parser = subparsers.add_parser(
        "compile",
        help="Compile a private draft wiki from iknow.yaml and Markdown sources.",
    )
    compile_parser.add_argument(
        "--config",
        default="iknow.yaml",
        help="Path to iknow.yaml (default: iknow.yaml in current directory).",
    )
    compile_parser.add_argument(
        "--output-dir",
        default=None,
        help="Override the draft output directory.",
    )

    # --- install -------------------------------------------------------------
    install_parser = subparsers.add_parser(
        "install",
        help="Install a compiled draft wiki into the global store.",
    )
    install_parser.add_argument(
        "wiki_id",
        help="Wiki identifier. Looks for draft at .kungfu/drafts/<wiki-id>/ by default.",
    )
    install_parser.add_argument(
        "--draft-dir",
        default=None,
        help="Explicit path to the compiled draft directory.",
    )
    install_parser.add_argument(
        "--store-path",
        default=None,
        help="Override the installed store path.",
    )

    # --- list (installed) ----------------------------------------------------
    list_parser = subparsers.add_parser(
        "list",
        help="List all installed wikis.",
    )
    list_parser.add_argument(
        "--store-path",
        default=None,
        help="Override the installed store path.",
    )

    # --- remove --------------------------------------------------------------
    remove_parser = subparsers.add_parser(
        "remove",
        help="Remove an installed wiki from the global store.",
    )
    remove_parser.add_argument(
        "wiki_id",
        help="Wiki identifier to remove.",
    )
    remove_parser.add_argument(
        "--store-path",
        default=None,
        help="Override the installed store path.",
    )

    # --- serve ---------------------------------------------------------------
    serve_parser = subparsers.add_parser(
        "serve",
        help="Query installed wikis: list, search, or read documents.",
    )
    serve_sub = serve_parser.add_subparsers(
        dest="serve_action", help="serve subcommand"
    )

    serve_list = serve_sub.add_parser(
        "list",
        help="List all installed wikis with detailed metadata.",
    )
    serve_list.add_argument(
        "--store-path",
        default=None,
        help="Override the installed store path.",
    )

    serve_search = serve_sub.add_parser(
        "search",
        help="Search within an installed wiki (detects out-of-scope queries).",
    )
    serve_search.add_argument(
        "wiki_id",
        help="Installed wiki identifier.",
    )
    serve_search.add_argument(
        "query",
        help="Search query string.",
    )
    serve_search.add_argument(
        "--store-path",
        default=None,
        help="Override the installed store path.",
    )
    serve_search.add_argument(
        "--max-results",
        type=int,
        default=10,
        help="Maximum number of search hits (default: 10).",
    )

    serve_read = serve_sub.add_parser(
        "read",
        help="Read a specific document from an installed wiki.",
    )
    serve_read.add_argument(
        "wiki_id",
        help="Installed wiki identifier.",
    )
    serve_read.add_argument(
        "doc_path",
        help="Relative document path (e.g. getting-started.md).",
    )
    serve_read.add_argument(
        "--store-path",
        default=None,
        help="Override the installed store path.",
    )

    return parser


# ---------------------------------------------------------------------------
# Command handlers
# ---------------------------------------------------------------------------


def _cmd_cookbook(args: argparse.Namespace) -> int:
    """Handle ``cookbook list`` and ``cookbook inspect``."""
    action = getattr(args, "cookbook_action", None)

    if action == "list":
        items = registry.list_wikis()
        if not items:
            print("Cookbook registry is empty.")
            return 0
        print(f"{'Wiki ID':24s}  {'Name':32s}  {'Trust':12s}  Version")
        print("-" * 80)
        for item in items:
            print(
                f"{item.id:24s}  {item.name:32s}  "
                f"{item.trust_state.value:12s}  v{item.version}"
            )
        return 0

    elif action == "inspect":
        try:
            contract = registry.get_wiki(args.wiki_id)
        except KeyError:
            print(f"Wiki not found in registry: {args.wiki_id!r}", file=sys.stderr)
            return 1

        print(f"Name:          {contract.name}")
        print(f"Description:   {contract.description}")
        print(f"Version:       {contract.version}")
        print(f"Trust state:   {contract.trust_state.value}")
        print(f"Provenance:    {contract.provenance}")
        print(f"Freshness:     {contract.freshness}")
        print(f"License:       {contract.license}")
        print(f"Validation:    {contract.validation_state}")
        print()
        print("Scope:")
        for topic in contract.scope:
            print(f"  - {topic}")
        print()
        print("Non-scope (out of scope):")
        for topic in contract.non_scope:
            print(f"  - {topic}")
        print()
        print("Entry points:")
        for ep in contract.entry_points:
            print(f"  - {ep.value}")
        if contract.warnings:
            print()
            print("Warnings:")
            for w in contract.warnings:
                print(f"  - {w}")
        return 0

    else:
        print("Usage: iknow cookbook {list|inspect}", file=sys.stderr)
        return 1


def _cmd_fit(args: argparse.Namespace) -> int:
    """Handle ``fit <wiki-id>`` — compare registry wiki vs local inventory."""
    # Load inventory
    if args.inventory == "default":
        inventory = get_inventory()
    else:
        try:
            with open(args.inventory, "r", encoding="utf-8") as f:
                data = json.load(f)
            from iknow.inventory import LocalKnowledgeInventory

            inventory = LocalKnowledgeInventory(
                name=data.get("name", "Custom Inventory"),
                description=data.get("description", ""),
            )
        except (OSError, json.JSONDecodeError) as exc:
            print(
                f"Failed to load inventory from {args.inventory!r}: {exc}",
                file=sys.stderr,
            )
            return 1

    # Fetch contract from registry
    try:
        contract = registry.get_wiki(args.wiki_id)
    except KeyError:
        print(f"Wiki not found in registry: {args.wiki_id!r}", file=sys.stderr)
        return 1

    # Compute fit
    result = compute_fit(contract, inventory, candidate_id=args.wiki_id)
    fit = result.fit

    print(f"Candidate:     {result.candidate_name} ({result.candidate_id})")
    print(f"Inventory:     {result.inventory_name}")
    print(f"Recommendation: {fit.recommendation.value}")
    print(f"Merge risk:    {fit.merge_risk}")
    print(f"Gap:           {fit.gap_percentage:.0%} of scope topics are new")
    print()
    print(f"Overlap ({len(fit.overlapping_topics)} topics):")
    for topic in fit.overlapping_topics:
        print(f"  ✓ {topic}")
    print()
    print(f"Gaps ({len(fit.gap_topics)} topics):")
    for topic in fit.gap_topics:
        print(f"  ✗ {topic}")

    if fit.boundary_warnings:
        print()
        print("Boundary warnings:")
        for w in fit.boundary_warnings:
            print(f"  ⚠ {w}")

    if fit.conflict_warnings:
        print()
        print("Conflict warnings:")
        for w in fit.conflict_warnings:
            print(f"  ✗ {w}")

    # Show harmonization options aligned with recommendation
    print()
    print("Harmonization options:")
    from iknow.harmonization import all_options

    for opt in all_options():
        marker = "→" if fit.recommendation.name.lower().startswith(
            opt.value.replace("-", "_")
        ) else " "
        print(f"  {marker} {opt.value}")

    return 0


def _cmd_compile(args: argparse.Namespace) -> int:
    """Handle ``compile --config <iknow.yaml>``."""
    config_path = args.config
    if not os.path.isfile(config_path):
        print(f"Configuration file not found: {config_path}", file=sys.stderr)
        return 1

    result = compile_draft(
        config_path=config_path,
        output_dir=args.output_dir,
    )

    if result.success:
        print(f"Compiled wiki '{result.wiki_id}' → {result.draft_dir}/")
        print(f"  Artifacts: {len(result.artifacts)} files written")
        if result.manifest and result.manifest.metadata_warnings:
            print(f"  Warnings: {len(result.manifest.metadata_warnings)}")
            for w in result.manifest.metadata_warnings:
                print(f"    ⚠ {w}")
        return 0
    else:
        print(f"Failed to compile wiki '{result.wiki_id}':", file=sys.stderr)
        for err in result.errors:
            print(f"  - {err}", file=sys.stderr)
        return 1


def _cmd_install(args: argparse.Namespace) -> int:
    """Handle ``install <wiki-id>`` — install a compiled draft."""
    # Resolve draft directory
    if args.draft_dir:
        draft_dir = args.draft_dir
    else:
        draft_dir = os.path.join(".kungfu", "drafts", args.wiki_id)

    if not os.path.isdir(draft_dir):
        print(
            f"Draft directory not found: {draft_dir}",
            file=sys.stderr,
        )
        print(
            "  First compile the wiki with: iknow compile --config iknow.yaml",
            file=sys.stderr,
        )
        return 1

    result = install_draft(
        draft_dir=draft_dir,
        wiki_id=args.wiki_id,
        store_path=args.store_path,
    )

    if result.success:
        print(f"Installed wiki '{result.wiki_id}' → {result.installed_path}")
        return 0
    else:
        print(f"Failed to install wiki '{result.wiki_id}':", file=sys.stderr)
        for err in result.errors:
            print(f"  - {err}", file=sys.stderr)
        return 1


def _cmd_list(args: argparse.Namespace) -> int:
    """Handle ``list`` — list installed wikis."""
    wikis = list_installed(store_path=args.store_path)
    if not wikis:
        store = args.store_path or get_installed_store_path()
        print(f"No wikis installed in: {store}")
        return 0
    print(f"{'Wiki ID':24s}  {'Name':30s}  {'Version':10s}  Documents")
    print("-" * 72)
    for wiki in wikis:
        print(summarize(wiki))
    return 0


def _cmd_remove(args: argparse.Namespace) -> int:
    """Handle ``remove <wiki-id>``."""
    success = remove_installed(
        wiki_id=args.wiki_id,
        store_path=args.store_path,
    )
    if success:
        print(f"Removed wiki '{args.wiki_id}'")
        return 0
    else:
        print(
            f"Wiki '{args.wiki_id}' not found or could not be removed",
            file=sys.stderr,
        )
        return 1


def _cmd_serve(args: argparse.Namespace) -> int:
    """Handle ``serve {list|search|read}``."""
    action = getattr(args, "serve_action", None)
    store_path = getattr(args, "store_path", None)

    if action == "list":
        items = list_wikis(store_path=store_path)
        if not items:
            store = args.store_path or get_installed_store_path()
            print(f"No wikis installed in: {store}")
            return 0
        print(f"{'Wiki ID':24s}  {'Name':32s}  {'Version':10s}  Docs  Raw")
        print("-" * 78)
        for item in items:
            raw_flag = "✓" if item.has_raw else "✗"
            print(
                f"{item.wiki_id:24s}  {item.name:32s}  "
                f"v{item.version:7s}  {item.total_documents:4d}  {raw_flag}"
            )
        return 0

    elif action == "search":
        result = search_wiki(
            wiki_id=args.wiki_id,
            query=args.query,
            store_path=store_path,
            max_results=args.max_results,
        )
        error = result.get("error")
        if error:
            print(f"Error: {error}", file=sys.stderr)
            return 1

        if result.get("out_of_scope"):
            print("═" * 60)
            print("OUT-OF-SCOPE REFUSAL")
            print("═" * 60)
            print()
            print(result.get("out_of_scope_detail", "Query is out of scope."))
            print()
            print("Suggested action: route this query to a different knowledge base.")
            return 0

        hits = result.get("hits", [])
        if not hits:
            print(f"No results found for query: {args.query!r}")
            return 0

        print(f"Search results for '{args.query}' in wiki '{args.wiki_id}':")
        print(f"  Total hits: {result.get('total_hits', len(hits))}")
        print()
        for i, hit in enumerate(hits, start=1):
            print(f"  [{i}] {hit.get('title', 'Untitled')}")
            print(f"      Path: {hit.get('document_path', '?')}")
            snippet = hit.get("snippet", "")
            if snippet:
                print(f"      Snippet: {snippet[:120]}...")
            print()
        return 0

    elif action == "read":
        result = read_document(
            wiki_id=args.wiki_id,
            document_path=args.doc_path,
            store_path=store_path,
        )
        error = result.get("error")
        if error:
            print(f"Error: {error}", file=sys.stderr)
            return 1

        print(f"Document: {result.get('title', 'Untitled')}")
        print(f"Path:     {result.get('citation_path', '?')}")
        print(f"Size:     {result.get('size_bytes', 0)} bytes")
        print()
        print(result.get("content", ""))
        return 0

    else:
        print("Usage: iknow serve {list|search|read}", file=sys.stderr)
        return 1


# ---------------------------------------------------------------------------
# Main dispatch
# ---------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    command = args.command

    if command == "cookbook":
        return _cmd_cookbook(args)
    elif command == "fit":
        return _cmd_fit(args)
    elif command == "compile":
        return _cmd_compile(args)
    elif command == "install":
        return _cmd_install(args)
    elif command == "list":
        return _cmd_list(args)
    elif command == "remove":
        return _cmd_remove(args)
    elif command == "serve":
        return _cmd_serve(args)
    else:
        parser.print_help()
        return 0


if __name__ == "__main__":
    sys.exit(main())