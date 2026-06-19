"""Harmonization module.

Seam: represent explicit decision state — install, skip, route-only,
prefer-local, prefer-wiki, keep-both-with-boundaries — as visible choices,
not hidden side effects.

v1 adapter: local-only decisions tracked on the filesystem. No cloud sync.
"""

from iknow.harmonization.decisions import (
    DecisionKind,
    HarmonizationChoice,
    HarmonizationResult,
    all_options,
    make_install_decision,
    make_keep_both_decision,
    make_prefer_local_decision,
    make_prefer_wiki_decision,
    make_route_only_decision,
    make_skip_decision,
)

__all__ = [
    "DecisionKind",
    "HarmonizationChoice",
    "HarmonizationResult",
    "all_options",
    "make_install_decision",
    "make_keep_both_decision",
    "make_prefer_local_decision",
    "make_prefer_wiki_decision",
    "make_route_only_decision",
    "make_skip_decision",
]