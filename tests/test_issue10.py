"""Tests for Issue #10: Local validation gates for listing and recommendation eligibility.

Acceptance criteria covered:
- Validation can check a Wiki Contract and draft/installed wiki artifacts locally.
- Listing Eligibility requires minimum scope, non-scope, provenance,
  license/maintainer metadata, serving entry points, and valid artifacts.
- Recommendation Eligibility is separate and can fail even when listing passes.
- Validation output distinguishes warnings from blockers.
- Verified/Official behaviour remains local metadata only; no ownership-claim
  workflow is built.
- Tests prove one wiki can be listable but not recommendable.
"""

from __future__ import annotations

import json
import os

import pytest

from iknow.contracts.model import ServingEntryPoint, TrustState, WikiContract
from iknow.validation import (
    GateResult,
    ValidationOutput,
    check_listing_eligibility,
    check_recommendation_eligibility,
    validate_wiki,
)


# ===========================================================================
# Fixtures
# ===========================================================================


def _make_contract(
    *,
    name: str = "test-wiki",
    description: str = "A test wiki",
    version: str = "1.0.0",
    scope: list[str] | None = None,
    non_scope: list[str] | None = None,
    provenance: str = "https://example.com/test-wiki",
    freshness: str = "2025-06-01",
    license: str = "MIT",
    trust_state: TrustState = TrustState.COMMUNITY,
    entry_points: list[ServingEntryPoint] | None = None,
    warnings: list[str] | None = None,
    validation_state: str = "valid",
) -> WikiContract:
    """Build a WikiContract with sensible defaults."""
    return WikiContract(
        name=name,
        description=description,
        version=version,
        scope=scope if scope is not None else ["testing"],
        non_scope=non_scope if non_scope is not None else ["other-topic"],
        provenance=provenance,
        freshness=freshness,
        license=license,
        trust_state=trust_state,
        entry_points=entry_points if entry_points is not None else [ServingEntryPoint.MCP],
        validation_state=validation_state,
        warnings=warnings or [],
    )


@pytest.fixture
def valid_contract() -> WikiContract:
    """A fully valid community wiki contract."""
    return _make_contract(
        name="valid-wiki",
        trust_state=TrustState.COMMUNITY,
    )


@pytest.fixture
def verified_contract() -> WikiContract:
    """A verified wiki contract — eligible for recommendation."""
    return _make_contract(
        name="verified-wiki",
        trust_state=TrustState.VERIFIED,
        entry_points=[ServingEntryPoint.MCP, ServingEntryPoint.LLMS_TXT],
    )


@pytest.fixture
def official_contract() -> WikiContract:
    """An official wiki contract — top-tier recommendation."""
    return _make_contract(
        name="official-wiki",
        trust_state=TrustState.OFFICIAL,
        entry_points=[
            ServingEntryPoint.MCP,
            ServingEntryPoint.LLMS_TXT,
            ServingEntryPoint.MARKDOWN,
        ],
    )


@pytest.fixture
def wiki_dir(tmp_path) -> str:
    """Create a minimal valid wiki directory with all artifacts."""
    dest = os.path.join(str(tmp_path), "test-wiki-on-disk")
    os.makedirs(os.path.join(dest, "raw"))

    # kb.json with maintainer
    kb = {
        "wiki_id": "test-wiki-on-disk",
        "name": "Test Wiki on Disk",
        "description": "A wiki with all required artifacts",
        "version": "1.0.0",
        "scope": ["testing"],
        "non_scope": ["other-topic"],
        "license": "MIT",
        "maintainer": "test-maintainer",
        "provenance": "https://example.com/test-wiki",
        "freshness": "2025-06-01",
        "entry_points": ["mcp", "llms.txt"],
        "total_documents": 1,
        "total_excluded": 0,
        "metadata_warnings": [],
    }
    with open(os.path.join(dest, "kb.json"), "w") as f:
        json.dump(kb, f, indent=2)

    # index.json
    index = {
        "wiki_id": "test-wiki-on-disk",
        "wiki_name": "Test Wiki on Disk",
        "total_documents": 1,
        "documents": [{"path": "doc.md", "title": "Doc", "size_bytes": 50}],
    }
    with open(os.path.join(dest, "index.json"), "w") as f:
        json.dump(index, f)

    # llms.txt
    with open(os.path.join(dest, "llms.txt"), "w") as f:
        f.write("# Test Wiki\n")

    # sources.json
    with open(os.path.join(dest, "sources.json"), "w") as f:
        json.dump({"wiki_id": "test-wiki-on-disk", "included": [], "excluded": []}, f)

    # warnings.json
    with open(os.path.join(dest, "warnings.json"), "w") as f:
        json.dump({"warnings": []}, f)

    # review.md
    with open(os.path.join(dest, "review.md"), "w") as f:
        f.write("# Review\n")

    # Raw file
    with open(os.path.join(dest, "raw", "doc.md"), "w") as f:
        f.write("# Doc\n")

    return dest


# ===========================================================================
# Listing eligibility — contract-only checks
# ===========================================================================


class TestListingContractOnly:
    """Listing eligibility checks when only the contract is provided."""

    def test_valid_contract_passes_listing(self, valid_contract) -> None:
        result = check_listing_eligibility(valid_contract)
        assert result.passed is True
        assert len(result.blockers) == 0

    def test_passing_result_has_no_blockers(self, valid_contract) -> None:
        result = check_listing_eligibility(valid_contract)
        assert result.wiki_id == "valid-wiki"
        assert result.passed is True

    def test_listing_fails_without_scope(self, valid_contract) -> None:
        valid_contract.scope = []
        result = check_listing_eligibility(valid_contract)
        assert result.passed is False
        assert any("scope" in b.lower() for b in result.blockers)

    def test_listing_fails_without_non_scope(self, valid_contract) -> None:
        valid_contract.non_scope = []
        result = check_listing_eligibility(valid_contract)
        assert result.passed is False
        assert any("non-scope" in b.lower() for b in result.blockers)

    def test_listing_fails_without_provenance(self, valid_contract) -> None:
        valid_contract.provenance = ""
        result = check_listing_eligibility(valid_contract)
        assert result.passed is False
        assert any("provenance" in b.lower() for b in result.blockers)

    def test_listing_fails_without_license(self, valid_contract) -> None:
        valid_contract.license = ""
        result = check_listing_eligibility(valid_contract)
        assert result.passed is False
        assert any("license" in b.lower() for b in result.blockers)

    def test_listing_fails_without_entry_points(self, valid_contract) -> None:
        valid_contract.entry_points = []
        result = check_listing_eligibility(valid_contract)
        assert result.passed is False
        assert any("entry points" in b.lower() for b in result.blockers)

    def test_single_scope_triggers_warning_not_blocker(self) -> None:
        contract = _make_contract(scope=["only-one"], non_scope=["other"])
        result = check_listing_eligibility(contract)
        assert result.passed is True  # one scope is still valid
        assert any("only one" in w.lower() for w in result.warnings)

    def test_single_entry_point_triggers_warning(self) -> None:
        contract = _make_contract(entry_points=[ServingEntryPoint.MCP])
        result = check_listing_eligibility(contract)
        assert result.passed is True
        assert any("only one" in w.lower() for w in result.warnings)

    def test_generic_license_triggers_warning(self) -> None:
        contract = _make_contract(license="MIT")
        result = check_listing_eligibility(contract)
        assert result.passed is True
        # MIT is in the known generic set
        assert any("generic" in w.lower() for w in result.warnings)

    def test_weak_provenance_triggers_warning(self) -> None:
        contract = _make_contract(provenance="local-file.txt")
        result = check_listing_eligibility(contract)
        assert result.passed is True  # still passes — provenance is non-empty
        assert any("does not look like a URL" in w for w in result.warnings)


# ===========================================================================
# Listing eligibility — with on-disk artifacts
# ===========================================================================


class TestListingWithArtifacts:
    """Listing eligibility checks with a wiki directory on disk."""

    def test_valid_wiki_dir_passes_listing(
        self, valid_contract: WikiContract, wiki_dir: str
    ) -> None:
        result = check_listing_eligibility(valid_contract, wiki_dir=wiki_dir)
        assert result.passed is True
        assert len(result.blockers) == 0

    def test_maintainer_read_from_kb_json(self, wiki_dir: str) -> None:
        contract = _make_contract(name="on-disk-wiki")
        result = check_listing_eligibility(contract, wiki_dir=wiki_dir)
        assert result.passed is True
        # Maintainer check should pass since kb.json has one

    def test_missing_kb_json_is_blocker(self, wiki_dir: str) -> None:
        os.remove(os.path.join(wiki_dir, "kb.json"))
        contract = _make_contract(name="missing-kb")
        result = check_listing_eligibility(contract, wiki_dir=wiki_dir)
        assert result.passed is False
        assert any("kb.json" in b for b in result.blockers)

    def test_missing_raw_dir_is_blocker(self, wiki_dir: str) -> None:
        import shutil
        shutil.rmtree(os.path.join(wiki_dir, "raw"))
        contract = _make_contract(name="no-raw")
        result = check_listing_eligibility(contract, wiki_dir=wiki_dir)
        assert result.passed is False
        assert any("raw" in b.lower() for b in result.blockers)

    def test_missing_llms_txt_is_blocker(self, wiki_dir: str) -> None:
        os.remove(os.path.join(wiki_dir, "llms.txt"))
        contract = _make_contract(name="no-llms")
        result = check_listing_eligibility(contract, wiki_dir=wiki_dir)
        assert result.passed is False
        assert any("llms.txt" in b for b in result.blockers)

    def test_nonexistent_wiki_dir_is_blocker(self, valid_contract) -> None:
        result = check_listing_eligibility(
            valid_contract, wiki_dir="/tmp/__nonexistent_wiki_dir__test_abc_xyz__"
        )
        assert result.passed is False

    def test_invalid_kb_json_is_blocker(self, wiki_dir: str) -> None:
        with open(os.path.join(wiki_dir, "kb.json"), "w") as f:
            f.write("not valid json{")
        contract = _make_contract(name="bad-kb")
        result = check_listing_eligibility(contract, wiki_dir=wiki_dir)
        assert result.passed is False
        assert any("not valid JSON" in b for b in result.blockers)


# ===========================================================================
# Recommendation eligibility
# ===========================================================================


class TestRecommendationEligibility:
    """Recommendation eligibility checks — stricter than listing."""

    def test_community_wiki_is_listable_but_not_recommendable(
        self, valid_contract: WikiContract
    ) -> None:
        """Community trust: listable, but NOT recommendable."""
        listing = check_listing_eligibility(valid_contract)
        recommendation = check_recommendation_eligibility(valid_contract)

        assert listing.passed is True
        assert recommendation.passed is False
        assert any("Community" in b for b in recommendation.blockers)

    def test_verified_wiki_can_be_recommendable(
        self, verified_contract: WikiContract
    ) -> None:
        result = check_recommendation_eligibility(verified_contract)
        assert result.passed is True

    def test_official_wiki_can_be_recommendable(
        self, official_contract: WikiContract
    ) -> None:
        result = check_recommendation_eligibility(official_contract)
        assert result.passed is True

    def test_recommendation_fails_without_freshness(
        self, verified_contract: WikiContract
    ) -> None:
        verified_contract.freshness = ""
        result = check_recommendation_eligibility(verified_contract)
        assert result.passed is False
        assert any("freshness" in b.lower() for b in result.blockers)

    def test_recommendation_fails_with_contract_warnings(
        self, verified_contract: WikiContract
    ) -> None:
        verified_contract.warnings = ["Missing recommended field: description"]
        verified_contract.validation_state = "invalid"
        result = check_recommendation_eligibility(verified_contract)
        assert result.passed is False
        assert any("warning" in b.lower() for b in result.blockers)

    def test_recommendation_passes_with_verified_trust_and_full_metadata(
        self, verified_contract: WikiContract, wiki_dir: str
    ) -> None:
        result = check_recommendation_eligibility(verified_contract, wiki_dir=wiki_dir)
        assert result.passed is True
        assert len(result.blockers) == 0

    def test_recommendation_shows_listing_blockers_too(
        self, verified_contract: WikiContract
    ) -> None:
        """Recommendation should include listing blockers in its result."""
        verified_contract.scope = []
        result = check_recommendation_eligibility(verified_contract)
        assert result.passed is False
        assert any("scope" in b.lower() for b in result.blockers)


# ===========================================================================
# Warning vs. Blocker distinction
# ===========================================================================


class TestWarningVsBlocker:
    """Validation output distinguishes warnings from blockers."""

    def test_passing_result_has_no_blockers(self, valid_contract) -> None:
        result = check_listing_eligibility(valid_contract)
        assert result.passed is True
        assert len(result.blockers) == 0

    def test_passing_result_can_have_warnings(self) -> None:
        """A wiki with thin metadata may pass listing with warnings."""
        contract = _make_contract(
            scope=["thin"],
            non_scope=["other"],
            provenance="https://example.com",
            license="MIT",
        )
        result = check_listing_eligibility(contract)
        assert result.passed is True
        assert len(result.warnings) > 0  # single scope, generic license etc.

    def test_warnings_and_blockers_are_separate_lists(self) -> None:
        contract = _make_contract(
            scope=[],
            non_scope=[],
            provenance="",
            license="MIT",
            entry_points=[ServingEntryPoint.MCP],
        )
        result = check_listing_eligibility(contract)
        assert not result.passed
        # Should have blockers for scope, non-scope, provenance
        assert len(result.blockers) >= 3
        # Warnings may also be present for generic license or single entry point
        assert isinstance(result.warnings, list)

    def test_warnings_do_not_cause_failure(self) -> None:
        """Warnings are advisory only — they don't flip ``passed`` to False."""
        contract = _make_contract(
            scope=["only-one"],
            non_scope=["other-topic"],
            provenance="local.txt",
            license="MIT",
            entry_points=[ServingEntryPoint.MCP],
        )
        result = check_listing_eligibility(contract)
        # All required fields present (scope/has 1, non-scope present, provenance present,
        # license present, entry points present) — passes despite warnings
        assert result.passed is True
        assert len(result.warnings) >= 1


# ===========================================================================
# ValidationOutput composite
# ===========================================================================


class TestValidationOutput:
    """Composite output with both listing and recommendation gates."""

    def test_community_wiki_composite(self, valid_contract: WikiContract) -> None:
        listing = check_listing_eligibility(valid_contract)
        recommendation = check_recommendation_eligibility(valid_contract)
        output = ValidationOutput(
            wiki_id=valid_contract.name,
            listing=listing,
            recommendation=recommendation,
        )

        assert output.listable is True
        assert output.recommendable is False
        assert output.wiki_id == "valid-wiki"

    def test_verified_wiki_composite(
        self, verified_contract: WikiContract
    ) -> None:
        listing = check_listing_eligibility(verified_contract)
        recommendation = check_recommendation_eligibility(verified_contract)
        output = ValidationOutput(
            wiki_id=verified_contract.name,
            listing=listing,
            recommendation=recommendation,
        )

        assert output.listable is True
        assert output.recommendable is True

    def test_to_dict_serialisation(self, valid_contract: WikiContract) -> None:
        listing = check_listing_eligibility(valid_contract)
        recommendation = check_recommendation_eligibility(valid_contract)
        output = ValidationOutput(
            wiki_id=valid_contract.name,
            listing=listing,
            recommendation=recommendation,
        )

        d = output.to_dict()
        assert d["wiki_id"] == "valid-wiki"
        assert d["listable"] is True
        assert d["recommendable"] is False
        assert "listing" in d
        assert "recommendation" in d
        assert d["recommendation"]["passed"] is False
        # Blockers should list Community trust issue
        assert any("Community" in b for b in d["recommendation"]["blockers"])


    def test_validate_wiki_runs_both_gates(self, valid_contract: WikiContract) -> None:
        output = validate_wiki(valid_contract)

        assert isinstance(output, ValidationOutput)
        assert output.listable is True
        assert output.recommendable is False
        assert any("Community" in b for b in output.recommendation.blockers)


# ===========================================================================
# GateResult utility methods
# ===========================================================================


class TestGateResultUtilities:
    """GateResult convenience methods."""

    def test_total_issues(self) -> None:
        result = GateResult(
            wiki_id="test",
            passed=False,
            blockers=["b1", "b2"],
            warnings=["w1"],
        )
        assert result.total_issues == 3

    def test_merge(self) -> None:
        a = GateResult(wiki_id="w", passed=True)
        b = GateResult(
            wiki_id="w", passed=False, blockers=["x"], warnings=["y"]
        )
        merged = a.merge(b)
        assert merged.blockers == ["x"]
        assert merged.warnings == ["y"]
        assert merged.passed is False  # False because b failed

    def test_to_dict(self) -> None:
        result = GateResult(
            wiki_id="w",
            passed=False,
            blockers=["blocker"],
            warnings=["warning"],
        )
        d = result.to_dict()
        assert d["wiki_id"] == "w"
        assert d["passed"] is False
        assert "blocker" in d["blockers"]
        assert "warning" in d["warnings"]


# ===========================================================================
# Edge cases
# ===========================================================================


class TestEdgeCases:
    """Edge cases for both gates."""

    def test_empty_contract_fails_listing(self) -> None:
        contract = _make_contract(
            scope=[],
            non_scope=[],
            provenance="",
            license="",
            entry_points=[],
        )
        result = check_listing_eligibility(contract)
        assert result.passed is False

    def test_maintainer_unknown_is_blocker(self, wiki_dir: str) -> None:
        """If maintainer in kb.json is 'unknown', it should be a blocker."""
        kb_path = os.path.join(wiki_dir, "kb.json")
        with open(kb_path, "r") as f:
            kb = json.load(f)
        kb["maintainer"] = "unknown"
        with open(kb_path, "w") as f:
            json.dump(kb, f)

        contract = _make_contract(name="unknown-maintainer")
        result = check_listing_eligibility(contract, wiki_dir=wiki_dir)
        assert result.passed is False

    def test_single_scope_with_no_warnings_for_multiple(self) -> None:
        """Scope with exactly one entry should warn, not block."""
        contract = _make_contract(scope=["single-scope"], non_scope=["other"])
        result = check_listing_eligibility(contract)
        assert result.passed is True
        assert any("only one" in w.lower() for w in result.warnings)

    def test_verified_with_weak_freshness_date(self) -> None:
        """A freshness that's too short should warn on recommendation."""
        contract = _make_contract(
            trust_state=TrustState.VERIFIED,
            freshness="2025",
        )
        result = check_recommendation_eligibility(contract)
        assert result.passed is True  # freshness is present, passes
        # Short date triggers a warning (not a blocker)
        assert any("freshness" in w.lower() for w in result.warnings)

    def test_contract_name_in_result(self) -> None:
        contract = _make_contract(name="my-cool-wiki")
        result = check_listing_eligibility(contract)
        assert result.wiki_id == "my-cool-wiki"

    def test_gate_result_immutable_by_default(self) -> None:
        """GateResult fields are mutable lists but should not affect other instances."""
        r1 = GateResult(wiki_id="a", passed=True)
        r2 = GateResult(wiki_id="b", passed=True)
        r1.warnings.append("test")
        assert len(r2.warnings) == 0  # separate list objects


# ===========================================================================
# Verified/Official local metadata only
# ===========================================================================


class TestVerifiedOfficialLocalOnly:
    """Verified/Official behaviour remains local metadata only.

    No ownership-claim workflow is built — trust state is read as-is
    from the contract metadata without any remote verification, auth, or
    claim-based promotion.  These tests verify that the gates respect
    whatever trust state the contract declares locally.
    """

    def test_trust_state_read_from_contract(self) -> None:
        """The gates rely purely on the contract's local trust_state field."""
        community = _make_contract(trust_state=TrustState.COMMUNITY)
        verified = _make_contract(trust_state=TrustState.VERIFIED)
        official = _make_contract(trust_state=TrustState.OFFICIAL)

        # Listing: all pass regardless of trust state
        assert check_listing_eligibility(community).passed is True
        assert check_listing_eligibility(verified).passed is True
        assert check_listing_eligibility(official).passed is True

        # Recommendation: only Verified/Official pass
        assert check_recommendation_eligibility(community).passed is False
        assert check_recommendation_eligibility(verified).passed is True
        assert check_recommendation_eligibility(official).passed is True

    def test_no_ownership_claim_workflow(self) -> None:
        """No external auth, no claim-based promotion exists in gates."""
        contract = _make_contract(trust_state=TrustState.COMMUNITY)
        # Setting a Verfied/Official state locally promotes it without any
        # external verification — that's exactly the "local metadata only"
        # contract. There's no claim/promote endpoint in the validation
        # module at all.
        contract.trust_state = TrustState.VERIFIED
        result = check_recommendation_eligibility(contract)
        assert result.passed is True  # purely based on local metadata
        # There is no claim workflow, no auth check, no provenance
        # verification — just the local trust_state value.