"""CLI entrypoint for the iknow control plane."""

import argparse
import sys

from iknow import __version__


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="iknow",
        description="I-know-kungfu — grow your knowledge base with proven wikis.",
        epilog="See https://github.com/pixiiidust/I-know-kungfu for documentation.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    # No subcommands yet — just help/version for the scaffold
    if not any(vars(args).values()):
        parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())