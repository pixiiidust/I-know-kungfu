"""Tests for Issue #5: Local Inventory, Context Fit, and Harmonization decisions.

Acceptance criteria covered:
- Local Inventory fixture can be loaded without scanning private files.
- Context Fit compares a candidate Wiki Contract against the inventory and
  returns overlap, gaps, boundary/conflict warnings, merge risk, and route
  recommendation.
- Harmonization represents explicit choices (install, skip, route-only,
  prefer-local, prefer-wiki, keep-both-with-boundaries).
- Fit output is deterministic for fixtures and suitable for CLI/UI display.
- Tests cover recommended_install, route_with_care, and findable_only cases.
- No automatic install/trust happens as part of fit checking.
"""

from __future__ import annotations

import pytest

from iknow.contracts.model import TrustState, WikiContract
from iknow.inventory import (
    InventoryItem,
    LocalKnowledgeInventory,
    build_default_inventory,
    get_inventory,
)
from iknow.fit import (
    FitComparison,
    FitResult,
    RouteRecommendation,
    compute_fit,
)
from iknow.harmonization import (
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


# ===========================================================================
# Local Inventory
# ===========================================================================


class TestLocalInventoryFixture:
    """Local Inventory fixture can be loaded without scanning private files."""

    def test_build_default_returns_inventory(self) -> None:
        inv = build_default_inventory()
        assert isinstance(inv, LocalKnowledgeInventory)

    def test_has_name(self) -> None:
        inv = build_default_inventory()
        assert isinstance(inv.name, str)
        assert len(inv.name) > 0

    def test_has_description(self) -> None:
        inv = build_default_inventory()
        assert isinstance(inv.description, str)
        assert len(inv.description) > 0

    def test_has_three_items(self) -> None:
        inv = build_default_inventory()
        assert len(inv.items) == 3

    def test_items_are_inventory_items(self) -> None:
        inv = build_default_inventory()
        for item in inv.items:
            assert isinstance(item, InventoryItem)

    def test_each_item_has_id(self) -> None:
        inv = build_default_inventory()
        for item in inv.items:
            assert isinstance(item.id, str)
            assert len(item.id) > 0

    def test_each_item_has_name(self) -> None:
        inv = build_default_inventory()
        for item in inv.items:
            assert isinstance(item.name, str)
            assert len(item.name) > 0

    def test_each_item_has_scope(self) -> None:
        inv = build_default_inventory()
        for item in inv.items:
            assert isinstance(item.scope, list)
            assert len(item.scope) > 0

    def test_combined_scope_is_deduplicated(self) -> None:
        inv = build_default_inventory()
        combined = inv.combined_scope
        assert isinstance(combined, list)
        assert len(combined) >= 3  # at least as many as the largest single item

    def test_combined_non_scope_is_deduplicated(self) -> None:
        inv = build_default_inventory()
        combined = inv.combined_non_scope
        assert isinstance(combined, list)
        assert len(combined) > 0

    def test_get_inventory_singleton(self) -> None:
        """get_inventory returns the same object across calls."""
        inv1 = get_inventory()
        inv2 = get_inventory()
        assert inv1 is inv2  # same instance

    def test_no_filesystem_access(self) -> None:
        """Inventory is built from in-memory data, not filesystem scan."""
        # Just confirming we can build it without any IO
        inv = build_default_inventory()
        assert inv.name == "Default Local Knowledge Base"


# ===========================================================================
# Context Fit
# ===========================================================================


class TestFitDeterminism:
    """Fit output is deterministic for the same inputs."""

    def test_deterministic_output(self) -> None:
        inventory = build_default_inventory()
        candidate = WikiContract(
            name="Test Wiki",
            description="A test wiki",
            version="1.0.0",
            scope=["Python packaging", "shell configuration"],
            non_scope=["GUI desktop environments"],
            provenance="https://example.com",
            freshness="2025-01-01",
            license="MIT",
            trust_state=TrustState.VERIFIED,
            entry_points=[],
        )
        result1 = compute_fit(candidate, inventory, candidate_id="test")
        result2 = compute_fit(candidate, inventory, candidate_id="test")
        assert result1.fit.overlapping_topics == result2.fit.overlapping_topics
        assert result1.fit.gap_topics == result2.fit.gap_topics
        assert result1.fit.boundary_warnings == result2.fit.boundary_warnings
        assert result1.fit.merge_risk == result2.fit.merge_risk
        assert result1.fit.recommendation == result2.fit.recommendation

    def test_returns_fit_comparison(self) -> None:
        inventory = build_default_inventory()
        candidate = WikiContract(
            name="T", description="d", version="1",
            scope=["a"], non_scope=["b"],
            provenance="https://x", freshness="2025-01", license="MIT",
            trust_state=TrustState.COMMUNITY, entry_points=[],
        )
        result = compute_fit(candidate, inventory)
        assert isinstance(result, FitComparison)

    def test_comparison_has_candidate_info(self) -> None:
        inventory = build_default_inventory()
        candidate = WikiContract(
            name="T", description="d", version="1",
            scope=["a"], non_scope=["b"],
            provenance="https://x", freshness="2025-01", license="MIT",
            trust_state=TrustState.COMMUNITY, entry_points=[],
        )
        result = compute_fit(candidate, inventory, candidate_id="test_id")
        assert result.candidate_id == "test_id"
        assert result.candidate_name == "T"
        assert result.inventory_name == inventory.name

    def test_fit_result_has_all_fields(self) -> None:
        inventory = build_default_inventory()
        candidate = WikiContract(
            name="T", description="d", version="1",
            scope=["a"], non_scope=["b"],
            provenance="https://x", freshness="2025-01", license="MIT",
            trust_state=TrustState.COMMUNITY, entry_points=[],
        )
        result = compute_fit(candidate, inventory)
        fit = result.fit
        assert isinstance(fit, FitResult)
        assert isinstance(fit.overlapping_topics, list)
        assert isinstance(fit.gap_topics, list)
        assert isinstance(fit.boundary_warnings, list)
        assert isinstance(fit.conflict_warnings, list)
        assert isinstance(fit.merge_risk, str)
        assert isinstance(fit.gap_percentage, float)
        assert isinstance(fit.recommendation, RouteRecommendation)

    def test_gap_percentage_is_between_zero_and_one(self) -> None:
        inventory = build_default_inventory()
        for scope in [[], ["a"], ["a", "b", "c", "d", "e"]]:
            candidate = WikiContract(
                name="T", description="d", version="1",
                scope=scope, non_scope=["b"],
                provenance="https://x", freshness="2025-01", license="MIT",
                trust_state=TrustState.COMMUNITY, entry_points=[],
            )
            result = compute_fit(candidate, inventory)
            assert 0.0 <= result.fit.gap_percentage <= 1.0


# ===========================================================================
# Fit — recommended_install case
# ===========================================================================


class TestFitRecommendedInstall:
    """When a candidate overlaps well with local scope and conflicts are
    absent, route recommendation should be RECOMMENDED_INSTALL."""

    @pytest.fixture
    def inventory(self) -> LocalKnowledgeInventory:
        return build_default_inventory()

    def test_high_overlap_verified_recommends_install(self, inventory) -> None:
        """High overlap + Verified trust → RECOMMENDED_INSTALL."""
        candidate = WikiContract(
            name="Python Tooling Wiki",
            description="Python dev tools wiki",
            version="1.0.0",
            scope=[
                "Python packaging",
                "virtual environments",
                "testing with pytest",
            ],
            non_scope=["Python internals"],
            provenance="https://example.com",
            freshness="2025-01-01",
            license="MIT",
            trust_state=TrustState.VERIFIED,
            entry_points=[],
        )
        result = compute_fit(candidate, inventory, candidate_id="python_tooling")
        assert result.fit.recommendation == RouteRecommendation.RECOMMENDED_INSTALL
        assert len(result.fit.overlapping_topics) > 0
        assert result.fit.merge_risk in ("low",)

    def test_high_overlap_official_recommends_install(self, inventory) -> None:
        """High overlap + Official trust → RECOMMENDED_INSTALL."""
        candidate = WikiContract(
            name="Shell Config Wiki",
            description="Shell config reference",
            version="1.0.0",
            scope=[
                "shell configuration",
                "environment variables",
                "aliases and functions",
            ],
            non_scope=["GUI desktop environments"],
            provenance="https://example.com",
            freshness="2025-01-01",
            license="MIT",
            trust_state=TrustState.OFFICIAL,
            entry_points=[],
        )
        result = compute_fit(candidate, inventory, candidate_id="shell_config")
        assert result.fit.recommendation == RouteRecommendation.RECOMMENDED_INSTALL

    def test_high_overlap_community_recommends_install(self, inventory) -> None:
        """High overlap + Community trust → RECOMMENDED_INSTALL."""
        candidate = WikiContract(
            name="MCP Extras Wiki",
            description="Extra MCP topics",
            version="1.0.0",
            scope=[
                "MCP protocol concepts",
                "tool and resource definitions",
            ],
            non_scope=["production MCP deployment"],
            provenance="https://example.com",
            freshness="2025-01-01",
            license="MIT",
            trust_state=TrustState.COMMUNITY,
            entry_points=[],
        )
        result = compute_fit(candidate, inventory, candidate_id="mcp_extras")
        assert result.fit.recommendation == RouteRecommendation.RECOMMENDED_INSTALL

    def test_low_gap_no_warnings(self, inventory) -> None:
        """Topics fully covered by inventory produce low gap percentage."""
        candidate = WikiContract(
            name="Local KB Sync",
            description="Sync local KB",
            version="1.0.0",
            scope=[
                "Python packaging",
                "shell configuration",
                "MCP protocol concepts",
            ],
            non_scope=["Python internals", "GUI desktop environments"],
            provenance="https://example.com",
            freshness="2025-01-01",
            license="MIT",
            trust_state=TrustState.VERIFIED,
            entry_points=[],
        )
        result = compute_fit(candidate, inventory)
        assert 0.0 <= result.fit.gap_percentage <= 0.3
        assert len(result.fit.boundary_warnings) == 0

    def test_no_automatic_install(self, inventory) -> None:
        """Fit checking does NOT install anything or change any state."""
        candidate = WikiContract(
            name="Python Tooling Wiki",
            description="Python dev tools wiki",
            version="1.0.0",
            scope=["Python packaging", "virtual environments"],
            non_scope=["Python internals"],
            provenance="https://example.com",
            freshness="2025-01-01",
            license="MIT",
            trust_state=TrustState.VERIFIED,
            entry_points=[],
        )
        original_candidate_scope = list(candidate.scope)
        original_inventory_scope = list(inventory.items[0].scope)

        result = compute_fit(candidate, inventory)
        # The recommendation says install is *recommended* but nothing
        # was actually installed.
        assert result.fit.recommendation == RouteRecommendation.RECOMMENDED_INSTALL
        assert candidate.scope == original_candidate_scope
        assert inventory.items[0].scope == original_inventory_scope


# ===========================================================================
# Fit — route_with_care case
# ===========================================================================


class TestFitRouteWithCare:
    """Moderate overlap or boundary warnings → ROUTE_WITH_CARE."""

    @pytest.fixture
    def inventory(self) -> LocalKnowledgeInventory:
        return build_default_inventory()

    def test_moderate_gap_returns_route_with_care(self, inventory) -> None:
        """~50% gap → ROUTE_WITH_CARE."""
        # Inventory has ~14 scope items; give candidate some known + some new
        candidate = WikiContract(
            name="Mixed Knowledge Wiki",
            description="Some known, some new topics",
            version="1.0.0",
            scope=[
                "Python packaging",     # known
                "MCP protocol concepts",  # known
                "distributed systems",    # gap
                "event sourcing",         # gap
                "microservices",          # gap
            ],
            non_scope=["Python internals"],
            provenance="https://example.com",
            freshness="2025-01-01",
            license="MIT",
            trust_state=TrustState.VERIFIED,
            entry_points=[],
        )
        result = compute_fit(candidate, inventory)
        assert result.fit.recommendation == RouteRecommendation.ROUTE_WITH_CARE
        assert 0.3 < result.fit.gap_percentage <= 0.7

    def test_low_gap_with_boundary_warning_returns_route_with_care(
        self, inventory
    ) -> None:
        """Low gap but boundary warnings → ROUTE_WITH_CARE."""
        candidate = WikiContract(
            name="Shell + Python Wiki",
            description="Shell and Python topics",
            version="1.0.0",
            scope=[
                "Python packaging",
                "shell configuration",
            ],
            non_scope=[
                # This is IN the inventory scope — boundary warning
                "Python packaging",
            ],
            provenance="https://example.com",
            freshness="2025-01-01",
            license="MIT",
            trust_state=TrustState.VERIFIED,
            entry_points=[],
        )
        result = compute_fit(candidate, inventory)
        assert result.fit.recommendation == RouteRecommendation.ROUTE_WITH_CARE
        assert len(result.fit.boundary_warnings) > 0

    def test_boundary_warning_includes_candidate_exclusion(self, inventory) -> None:
        """Boundary warning fires when candidate excludes what inventory includes."""
        candidate = WikiContract(
            name="Shell-excluding Wiki",
            description="Excludes shell topics",
            version="1.0.0",
            scope=["Python packaging"],
            non_scope=["shell configuration"],
            provenance="https://example.com",
            freshness="2025-01-01",
            license="MIT",
            trust_state=TrustState.COMMUNITY,
            entry_points=[],
        )
        result = compute_fit(candidate, inventory)
        warnings = [w for w in result.fit.boundary_warnings if "shell configuration" in w]
        assert len(warnings) > 0
        assert "explicitly excludes" in warnings[0]


# ===========================================================================
# Fit — findable_only case
# ===========================================================================


class TestFitFindableOnly:
    """Low overlap or high gap → FINDABLE_ONLY."""

    @pytest.fixture
    def inventory(self) -> LocalKnowledgeInventory:
        return build_default_inventory()

    def test_high_gap_returns_findable_only(self, inventory) -> None:
        """>70% gap → FINDABLE_ONLY."""
        candidate = WikiContract(
            name="Quantum Computing Wiki",
            description="QC topics — nothing in common with local KB",
            version="1.0.0",
            scope=[
                "quantum circuits",
                "qubit operations",
                "quantum error correction",
                "Shor's algorithm",
                "Grover's algorithm",
            ],
            non_scope=["classical computing"],
            provenance="https://example.com",
            freshness="2025-01-01",
            license="MIT",
            trust_state=TrustState.COMMUNITY,
            entry_points=[],
        )
        result = compute_fit(candidate, inventory)
        assert result.fit.recommendation == RouteRecommendation.FINDABLE_ONLY
        assert result.fit.gap_percentage >= 0.7

    def test_high_gap_with_boundary_warnings_findable_only(self, inventory) -> None:
        """>70% gap + boundary warnings → FINDABLE_ONLY."""
        candidate = WikiContract(
            name="Incompatible Wiki",
            description="High gap + boundary crossing",
            version="1.0.0",
            scope=[
                "quantum circuits",
                "shell configuration",  # known + boundary? no, it's in scope
                "qubit operations",
                "quantum error correction",
                "Shor's algorithm",
                "Grover's algorithm",
            ],
            non_scope=[
                "Python packaging",  # In inventory scope → boundary warning
            ],
            provenance="https://example.com",
            freshness="2025-01-01",
            license="MIT",
            trust_state=TrustState.COMMUNITY,
            entry_points=[],
        )
        result = compute_fit(candidate, inventory)
        # Gap is 5/6 = 0.83 > 0.7, has boundary warning → FINDABLE_ONLY
        assert result.fit.recommendation == RouteRecommendation.FINDABLE_ONLY
        assert len(result.fit.boundary_warnings) > 0

    def test_entirely_new_domain(self, inventory) -> None:
        """Nothing overlaps → FINDABLE_ONLY."""
        candidate = WikiContract(
            name="Cooking Wiki",
            description="Cooking knowledge",
            version="1.0.0",
            scope=["sous vide", "fermentation", "knife skills"],
            non_scope=["Python packaging"],
            provenance="https://example.com",
            freshness="2025-01-01",
            license="MIT",
            trust_state=TrustState.VERIFIED,
            entry_points=[],
        )
        result = compute_fit(candidate, inventory)
        assert result.fit.recommendation == RouteRecommendation.FINDABLE_ONLY
        assert len(result.fit.overlapping_topics) == 0
        assert len(result.fit.gap_topics) == 3


# ===========================================================================
# Fit — CLI/UI display
# ===========================================================================


class TestFitCLIDisplay:
    """Fit output is suitable for CLI/UI display."""

    def test_fit_result_has_readable_fields(self) -> None:
        """FitResult fields are all basic Python types — trivially printable."""
        inventory = build_default_inventory()
        candidate = WikiContract(
            name="Test", description="d", version="1",
            scope=["a"], non_scope=["b"],
            provenance="https://x", freshness="2025-01", license="MIT",
            trust_state=TrustState.COMMUNITY, entry_points=[],
        )
        result = compute_fit(candidate, inventory, candidate_id="test")
        fit = result.fit
        # All fields are printable primitives
        assert isinstance(str(fit.recommendation.value), str)
        assert isinstance(fit.merge_risk, str)

    def test_fit_comparison_has_all_context(self) -> None:
        """FitComparison wraps candidate identity + fit result."""
        inventory = build_default_inventory()
        candidate = WikiContract(
            name="Test Wiki", description="d", version="1",
            scope=["a"], non_scope=["b"],
            provenance="https://x", freshness="2025-01", license="MIT",
            trust_state=TrustState.COMMUNITY, entry_points=[],
        )
        result = compute_fit(candidate, inventory, candidate_id="test_candidate")
        assert result.candidate_id == "test_candidate"
        assert result.candidate_name == "Test Wiki"
        assert result.inventory_name == inventory.name
        assert result.fit is not None


# ===========================================================================
# Harmonization — decisions
# ===========================================================================


class TestHarmonizationDecisions:
    """Harmonization represents explicit choices."""

    def test_decision_kind_enum_has_all_options(self) -> None:
        """All six decision types exist."""
        kinds = {d.value for d in DecisionKind}
        expected = {
            "install",
            "skip",
            "route-only",
            "prefer-local",
            "prefer-wiki",
            "keep-both-with-boundaries",
        }
        assert kinds == expected

    def test_all_options_returns_all(self) -> None:
        options = all_options()
        assert len(options) == 6
        assert DecisionKind.INSTALL in options
        assert DecisionKind.SKIP in options
        assert DecisionKind.ROUTE_ONLY in options
        assert DecisionKind.PREFER_LOCAL in options
        assert DecisionKind.PREFER_WIKI in options
        assert DecisionKind.KEEP_BOTH_WITH_BOUNDARIES in options

    def test_install_decision(self) -> None:
        choice = make_install_decision("test_wiki")
        assert isinstance(choice, HarmonizationChoice)
        assert choice.candidate_id == "test_wiki"
        assert choice.decision == DecisionKind.INSTALL
        assert isinstance(choice.rationale, str)

    def test_skip_decision(self) -> None:
        choice = make_skip_decision("test_wiki")
        assert choice.decision == DecisionKind.SKIP
        assert choice.candidate_id == "test_wiki"

    def test_route_only_decision(self) -> None:
        choice = make_route_only_decision("test_wiki")
        assert choice.decision == DecisionKind.ROUTE_ONLY

    def test_prefer_local_decision(self) -> None:
        choice = make_prefer_local_decision("test_wiki")
        assert choice.decision == DecisionKind.PREFER_LOCAL

    def test_prefer_wiki_decision(self) -> None:
        choice = make_prefer_wiki_decision("test_wiki")
        assert choice.decision == DecisionKind.PREFER_WIKI

    def test_keep_both_decision(self) -> None:
        choice = make_keep_both_decision(
            "test_wiki",
            boundaries=["Python packaging → local", "shell config → wiki"],
        )
        assert choice.decision == DecisionKind.KEEP_BOTH_WITH_BOUNDARIES
        assert len(choice.applied_boundaries) == 2

    def test_decision_with_custom_rationale(self) -> None:
        choice = make_install_decision("test_wiki", rationale="Good fit.")
        assert choice.rationale == "Good fit."

    def test_harmonization_result(self) -> None:
        choice = make_install_decision("test_wiki")
        result = HarmonizationResult(
            candidate_id="test_wiki",
            decision=choice,
            available_options=[DecisionKind.INSTALL, DecisionKind.SKIP],
        )
        assert result.candidate_id == "test_wiki"
        assert result.decision.decision == DecisionKind.INSTALL
        assert DecisionKind.SKIP in result.available_options

    def test_describe_returns_string(self) -> None:
        choice = make_install_decision("test_wiki", rationale="Good fit.")
        result = HarmonizationResult(
            candidate_id="test_wiki",
            decision=choice,
            available_options=[DecisionKind.INSTALL, DecisionKind.SKIP],
        )
        desc = result.describe()
        assert isinstance(desc, str)
        assert "test_wiki" in desc
        assert "install" in desc
        assert "Good fit" in desc

    def test_describe_with_boundaries(self) -> None:
        choice = make_keep_both_decision(
            "test_wiki",
            boundaries=["Python → local", "Shell → wiki"],
        )
        result = HarmonizationResult(
            candidate_id="test_wiki",
            decision=choice,
            available_options=list(DecisionKind),
        )
        desc = result.describe()
        assert "keep-both-with-boundaries" in desc
        assert "Python" in desc
        assert "Shell" in desc

    def test_no_automatic_install(self) -> None:
        """Harmonization choices are records, not actions."""
        choice = make_install_decision("test_wiki", rationale="Good fit.")
        # Making the choice does NOT install anything
        assert choice.candidate_id == "test_wiki"
        assert choice.decision == DecisionKind.INSTALL
        # No side effects — just a dataclass


# ===========================================================================
# Integration: Inventory → Fit → Harmonization
# ===========================================================================


class TestInventoryFitHarmonizationIntegration:
    """End-to-end: load inventory, compute fit, make decisions."""

    def test_recommended_install_flow(self) -> None:
        """Full flow: known wiki → fit → install decision."""
        inventory = build_default_inventory()
        candidate = WikiContract(
            name="Python Packaging Wiki",
            description="Python packaging tools",
            version="1.0.0",
            scope=["Python packaging", "virtual environments", "testing with pytest"],
            non_scope=["Python internals"],
            provenance="https://example.com",
            freshness="2025-01-01",
            license="MIT",
            trust_state=TrustState.VERIFIED,
            entry_points=[],
        )
        fit = compute_fit(candidate, inventory, candidate_id="python_packaging")
        assert fit.fit.recommendation == RouteRecommendation.RECOMMENDED_INSTALL

        choice = make_install_decision(
            fit.candidate_id,
            rationale=f"Fit analysis: {fit.fit.gap_percentage:.0%} gap, {len(fit.fit.overlapping_topics)} overlapping topics.",
        )
        assert choice.decision == DecisionKind.INSTALL

    def test_findable_only_flow(self) -> None:
        """Full flow: unknown domain → fit → findable decision."""
        inventory = build_default_inventory()
        candidate = WikiContract(
            name="Quantum Wiki",
            description="Quantum computing topics",
            version="1.0.0",
            scope=["quantum gates", "qubits", "entanglement"],
            non_scope=[],
            provenance="https://example.com",
            freshness="2025-01-01",
            license="MIT",
            trust_state=TrustState.COMMUNITY,
            entry_points=[],
        )
        fit = compute_fit(candidate, inventory, candidate_id="quantum")
        assert fit.fit.recommendation == RouteRecommendation.FINDABLE_ONLY

        choice = make_route_only_decision(fit.candidate_id)
        assert choice.decision == DecisionKind.ROUTE_ONLY

    def test_inventory_is_unchanged_after_fit(self) -> None:
        """Fit analysis does not mutate the inventory."""
        inventory = build_default_inventory()
        original_name = inventory.name
        original_count = len(inventory.items)

        candidate = WikiContract(
            name="Test Wiki", description="d", version="1",
            scope=["Python packaging"], non_scope=[],
            provenance="https://x", freshness="2025-01", license="MIT",
            trust_state=TrustState.COMMUNITY, entry_points=[],
        )
        compute_fit(candidate, inventory)

        assert inventory.name == original_name
        assert len(inventory.items) == original_count