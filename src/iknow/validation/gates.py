"""Local validation gates for listing and recommendation eligibility.

These gates inspect a ``WikiContract`` and, optionally, the on-disk draft or
installed wiki artifacts to determine whether a wiki qualifies for:

- **Listing** in a cookbook registry (browse/search surface).
- **Recommendation** to an agent as a high-quality knowledge base.

Each gate returns a ``GateResult`` that distinguishes **blockers** (must-fix
issues that fail the gate) from **warnings** (advisory issues that do not
block passage).

Listing eligibility  (``check_listing_eligibility``)
    - Minimum scope + non-scope
    - Provenance, license & maintainer metadata
    - At least one serving entry point
    - Valid draft/installed artifacts (if a ``wiki_dir`` is provided)

Recommendation eligibility  (``check_recommendation_eligibility``)
    - All listing requirements (delegated)
    - Stricter trust-state requirement (Verified or Official)
    - Up-to-date freshness
    - No warnings at all (clean bill of health)

All checks are **local-only**.  No hosted registry, no auth/ownership claims,
no marketplace review, no eval runner.
"""

from __future__ import annotations

import json
import os
from typing import List, Optional

from iknow.contracts.model import TrustState, WikiContract
from iknow.store.paths import REQUIRED_DRAFT_ARTIFACTS
from iknow.validation.results import GateResult


# ---------------------------------------------------------------------------
# Listing eligibility gate
# ---------------------------------------------------------------------------


def check_listing_eligibility(
    contract: WikiContract,
    wiki_dir: str | None = None,
) -> GateResult:
    """Check whether *contract* qualifies for listing in a registry.

    Parameters
    ----------
    contract:
        The Wiki Contract to validate.
    wiki_dir:
        Optional path to a draft or installed wiki directory on disk.  When
        provided, artifact existence and maintainer metadata are checked.

    Returns
    -------
    GateResult
        ``passed=True`` when there are no blockers.  Warnings are advisory.
    """
    result = GateResult(wiki_id=contract.name, passed=True)

    _check_scope(contract, result)
    _check_non_scope(contract, result)
    _check_provenance(contract, result)
    _check_license(contract, result)
    _check_entry_points(contract, result)

    if wiki_dir is not None:
        _check_maintainer(wiki_dir, result)
        _check_artifacts(wiki_dir, result)

    result.passed = len(result.blockers) == 0
    return result


# ---------------------------------------------------------------------------
# Recommendation eligibility gate
# ---------------------------------------------------------------------------


def check_recommendation_eligibility(
    contract: WikiContract,
    wiki_dir: str | None = None,
) -> GateResult:
    """Check whether *contract* qualifies for recommendation.

    Recommendation is **stricter** than listing.  A wiki may be listable but
    *not* recommendable (e.g. ``Community`` trust, stale freshness, or
    unresolved warnings).

    Parameters
    ----------
    contract:
        The Wiki Contract to validate.
    wiki_dir:
        Optional path to a draft or installed wiki directory on disk.

    Returns
    -------
    GateResult
        ``passed=True`` only when all recommendation criteria are met.
    """
    result = GateResult(wiki_id=contract.name, passed=True)

    # All listing requirements must also be met.
    listing = check_listing_eligibility(contract, wiki_dir)
    result.merge(listing)

    # Recommendation-specific checks
    _check_trust_state(contract, result)
    _check_freshness(contract, result)
    _check_clean_warnings(contract, result)

    result.passed = len(result.blockers) == 0
    return result


# ---------------------------------------------------------------------------
# Individual check helpers
# ---------------------------------------------------------------------------


def _check_scope(contract: WikiContract, result: GateResult) -> None:
    """Scope must have at least one entry."""
    if not contract.scope:
        result.blockers.append("No scope defined — at least one scope entry is required")
    elif len(contract.scope) == 1:
        result.warnings.append(
            f"Scope has only one entry ('{contract.scope[0]}') — consider adding more"
        )


def _check_non_scope(contract: WikiContract, result: GateResult) -> None:
    """Non-scope must have at least one entry."""
    if not contract.non_scope:
        result.blockers.append("No non-scope defined — at least one non-scope entry is required")


def _check_provenance(contract: WikiContract, result: GateResult) -> None:
    """Provenance URL must be non-empty."""
    if not contract.provenance:
        result.blockers.append("No provenance URL — provenance is required for listing")
    elif not _looks_like_url(contract.provenance):
        result.warnings.append(
            f"Provenance '{contract.provenance}' does not look like a URL"
        )


def _check_license(contract: WikiContract, result: GateResult) -> None:
    """License must be non-empty."""
    if not contract.license:
        result.blockers.append("No license defined — license is required for listing")
    else:
        _check_license_quality(contract.license, result)


def _check_license_quality(license_val: str, result: GateResult) -> None:
    """Warn about vague or non-standard license values."""
    known_generic = {"mit", "apache", "bsd", "other", "proprietary", "unknown"}
    if license_val.strip().lower() in known_generic:
        result.warnings.append(
            f"License '{license_val}' is generic — consider using a SPDX identifier"
        )


def _check_maintainer(
    wiki_dir: str,
    result: GateResult,
) -> None:
    """Maintainer metadata must be present in ``kb.json`` under *wiki_dir*.

    The ``WikiContract`` model does not have a dedicated ``maintainer`` field;
    maintainer comes from the on-disk ``kb.json`` artifact.
    """
    maintainer = _read_maintainer(wiki_dir)

    if not maintainer:
        result.blockers.append(
            "No maintainer defined in kb.json — maintainer is required for listing"
        )
    elif maintainer.strip().lower() in ("unknown", "n/a", "todo", ""):
        result.blockers.append(
            f"Maintainer '{maintainer}' is not a valid identifier"
        )


def _check_entry_points(contract: WikiContract, result: GateResult) -> None:
    """At least one serving entry point must be defined."""
    if not contract.entry_points:
        result.blockers.append(
            "No serving entry points defined — at least one is required for listing"
        )
    elif len(contract.entry_points) < 2:
        result.warnings.append(
            f"Only one serving entry point ('{contract.entry_points[0].value}') "
            "— consider adding more for broader agent compatibility"
        )


def _check_artifacts(wiki_dir: str, result: GateResult) -> None:
    """Verify that all required draft artifacts exist on disk.

    Uses the same artifact list as ``iknow.store.paths.is_valid_draft()``.
    """
    if not os.path.isdir(wiki_dir):
        result.blockers.append(f"Wiki directory does not exist: {wiki_dir}")
        return

    for artifact in REQUIRED_DRAFT_ARTIFACTS:
        path = os.path.join(wiki_dir, artifact)
        if not os.path.isfile(path):
            result.blockers.append(f"Missing required artifact: {artifact}")

    raw_dir = os.path.join(wiki_dir, "raw")
    if not os.path.isdir(raw_dir):
        result.blockers.append("Missing required directory: raw/")

    # Check that kb.json is valid JSON with required fields
    kb_path = os.path.join(wiki_dir, "kb.json")
    if os.path.isfile(kb_path):
        try:
            with open(kb_path, "r", encoding="utf-8") as f:
                kb = json.load(f)
            if not isinstance(kb, dict):
                result.blockers.append("kb.json is not a valid JSON object")
            else:
                # Warn if metadata_warnings are present in kb.json
                meta_warnings = kb.get("metadata_warnings", [])
                if meta_warnings:
                    for w in meta_warnings:
                        result.warnings.append(f"kb.json metadata warning: {w}")
        except (json.JSONDecodeError, OSError) as exc:
            result.blockers.append(f"kb.json is not valid JSON: {exc}")


def _check_trust_state(contract: WikiContract, result: GateResult) -> None:
    """Recommendation requires Verified or Official trust state."""
    if contract.trust_state not in (TrustState.VERIFIED, TrustState.OFFICIAL):
        result.blockers.append(
            f"Trust state is '{contract.trust_state.value}' — "
            "recommendation requires 'Verified' or 'Official'"
        )


def _check_freshness(contract: WikiContract, result: GateResult) -> None:
    """Recommendation requires a freshness date to be set."""
    if not contract.freshness:
        result.blockers.append("No freshness date — freshness is required for recommendation")
    else:
        # Check that freshness looks like a date (loose check)
        cleaned = contract.freshness.strip()
        if len(cleaned) < 8:  # too short for YYYY-MM-DD or YYYY-MM
            result.warnings.append(
                f"Freshness '{contract.freshness}' does not look like a valid date"
            )


def _check_clean_warnings(contract: WikiContract, result: GateResult) -> None:
    """Recommendation requires no unresolved contract warnings."""
    if contract.validation_state == "invalid" or contract.warnings:
        for w in contract.warnings:
            result.blockers.append(f"Contract warning unresolved: {w}")


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _read_maintainer(wiki_dir: str | None) -> str | None:
    """Read the ``maintainer`` field from ``kb.json`` under *wiki_dir*."""
    if wiki_dir is None:
        return None
    kb_path = os.path.join(wiki_dir, "kb.json")
    if not os.path.isfile(kb_path):
        return None
    try:
        with open(kb_path, "r", encoding="utf-8") as f:
            kb = json.load(f)
        raw = kb.get("maintainer")
        if raw and isinstance(raw, str):
            return raw.strip()
    except (OSError, json.JSONDecodeError):
        pass
    return None


def _looks_like_url(value: str) -> bool:
    """Heuristic: does *value* look like a URL?"""
    return value.startswith(("http://", "https://", "ftp://", "git+"))