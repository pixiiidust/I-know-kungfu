"""CLI entrypoint for the iknow control plane.

Subcommands
-----------
install <draft_dir> [--wiki-id WIKI_ID]
    Install a compiled draft wiki into the global store.
list
    List all installed wikis.
remove <wiki-id>
    Remove an installed wiki from the store.

Environment variables
---------------------
IKNOW_INSTALLED_STORE
    Override the installed wiki store path (default: ~/.iknow/installed/).
"""

from __future__ import annotations

import argparse
import sys

from iknow import __version__
from iknow.store import (
    get_installed,
    get_installed_store_path,
    install_draft,
    list_installed,
    remove_installed,
    summarize,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="iknow",
        description="I-know-kungfu — grow your knowledge base with proven wikis.",
        epilog=(
            "See https://github.com/pixiiidust/I-know-kungfu for documentation.\n"
            "\n"
            "Wiki lifecycle:\n"
            "  Source-local drafts   ./.kungfu/drafts/<wiki-id>/  (compiled from iknow.yaml)\n"
            "  Global installed      ~/.iknow/installed/<wiki-id>/  (agent-available)\n"
            "\n"
            "Use 'iknow install <draft-dir>' to make a local draft agent-available."
        ),
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # --- install ---
    install_parser = subparsers.add_parser(
        "install",
        help="Install a compiled draft wiki into the global store.",
    )
    install_parser.add_argument(
        "draft_dir",
        help="Path to the compiled draft directory (e.g. .kungfu/drafts/<wiki-id>/).",
    )
    install_parser.add_argument(
        "--wiki-id",
        default=None,
        help="Override the wiki identifier (default: from kb.json or directory name).",
    )
    install_parser.add_argument(
        "--store-path",
        default=None,
        help="Override the installed store path (default: from IKNOW_INSTALLED_STORE or ~/.iknow/installed/).",
    )

    # --- list ---
    list_parser = subparsers.add_parser(
        "list",
        help="List all installed wikis.",
    )
    list_parser.add_argument(
        "--store-path",
        default=None,
        help="Override the installed store path.",
    )

    # --- remove ---
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

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "install":
        result = install_draft(
            draft_dir=args.draft_dir,
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

    elif args.command == "list":
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

    elif args.command == "remove":
        success = remove_installed(
            wiki_id=args.wiki_id,
            store_path=args.store_path,
        )
        if success:
            print(f"Removed wiki '{args.wiki_id}'")
            return 0
        else:
            print(f"Wiki '{args.wiki_id}' not found or could not be removed", file=sys.stderr)
            return 1

    else:
        parser.print_help()
        return 0


if __name__ == "__main__":
    sys.exit(main())