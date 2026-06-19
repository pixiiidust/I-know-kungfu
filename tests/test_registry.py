"""Tests for the Static Cookbook Registry adapter.

Covers:
- list_wikis returns at least three realistic wikis
- Each registry item has expected fields (id, name, description, trust, version)
- get_wiki returns a valid WikiContract for each known ID
- get_wiki raises KeyError for missing IDs
- Trust states are preserved (Community, Verified, Official)
- Registry items expose enough data for a table/list-first UI or CLI listing
"""

from typing import List

import pytest

from iknow.contracts.model import TrustState, WikiContract
from iknow.registry import RegistryItem, StaticCookbookRegistry


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def registry() -> StaticCookbookRegistry:
    return StaticCookbookRegistry()


# ---------------------------------------------------------------------------
# list_wikis
# ---------------------------------------------------------------------------

class TestListWikis:
    """Listing wikis returns lightweight metadata for all entries."""

    def test_returns_at_least_three_wikis(self, registry: StaticCookbookRegistry) -> None:
        wikis = registry.list_wikis()
        assert len(wikis) >= 3

    def test_all_items_are_registry_items(self, registry: StaticCookbookRegistry) -> None:
        wikis = registry.list_wikis()
        for item in wikis:
            assert isinstance(item, RegistryItem)

    def test_each_item_has_id(self, registry: StaticCookbookRegistry) -> None:
        wikis = registry.list_wikis()
        for item in wikis:
            assert isinstance(item.id, str)
            assert len(item.id) > 0

    def test_each_item_has_name(self, registry: StaticCookbookRegistry) -> None:
        wikis = registry.list_wikis()
        for item in wikis:
            assert isinstance(item.name, str)
            assert len(item.name) > 0

    def test_each_item_has_description(self, registry: StaticCookbookRegistry) -> None:
        wikis = registry.list_wikis()
        for item in wikis:
            assert isinstance(item.description, str)
            assert len(item.description) > 0

    def test_each_item_has_trust_state(self, registry: StaticCookbookRegistry) -> None:
        wikis = registry.list_wikis()
        for item in wikis:
            assert isinstance(item.trust_state, TrustState)

    def test_each_item_has_version(self, registry: StaticCookbookRegistry) -> None:
        wikis = registry.list_wikis()
        for item in wikis:
            assert isinstance(item.version, str)
            assert len(item.version) > 0

    def test_contains_agent_workflow_setup(self, registry: StaticCookbookRegistry) -> None:
        wikis = registry.list_wikis()
        ids = {w.id for w in wikis}
        assert "agent_workflow_setup" in ids

    def test_contains_terminal_setup(self, registry: StaticCookbookRegistry) -> None:
        wikis = registry.list_wikis()
        ids = {w.id for w in wikis}
        assert "terminal_setup" in ids

    def test_contains_mcp_basics(self, registry: StaticCookbookRegistry) -> None:
        wikis = registry.list_wikis()
        ids = {w.id for w in wikis}
        assert "mcp_basics" in ids


# ---------------------------------------------------------------------------
# get_wiki — known IDs
# ---------------------------------------------------------------------------

class TestGetWikiKnown:
    """Fetching a known wiki by ID returns its full WikiContract."""

    def test_agent_workflow_setup(self, registry: StaticCookbookRegistry) -> None:
        contract = registry.get_wiki("agent_workflow_setup")
        assert isinstance(contract, WikiContract)
        assert contract.name == "Agent Workflow Setup Wiki"

    def test_terminal_setup(self, registry: StaticCookbookRegistry) -> None:
        contract = registry.get_wiki("terminal_setup")
        assert isinstance(contract, WikiContract)
        assert contract.name == "Terminal Setup Wiki"

    def test_mcp_basics(self, registry: StaticCookbookRegistry) -> None:
        contract = registry.get_wiki("mcp_basics")
        assert isinstance(contract, WikiContract)
        assert contract.name == "MCP Basics Wiki"

    def test_contract_has_scope(self, registry: StaticCookbookRegistry) -> None:
        contract = registry.get_wiki("agent_workflow_setup")
        assert isinstance(contract.scope, list)
        assert len(contract.scope) > 0

    def test_contract_has_non_scope(self, registry: StaticCookbookRegistry) -> None:
        contract = registry.get_wiki("agent_workflow_setup")
        assert isinstance(contract.non_scope, list)

    def test_contract_has_provenance(self, registry: StaticCookbookRegistry) -> None:
        contract = registry.get_wiki("agent_workflow_setup")
        assert isinstance(contract.provenance, str)
        assert len(contract.provenance) > 0

    def test_contract_has_freshness(self, registry: StaticCookbookRegistry) -> None:
        contract = registry.get_wiki("agent_workflow_setup")
        assert isinstance(contract.freshness, str)
        assert len(contract.freshness) > 0

    def test_contract_has_license(self, registry: StaticCookbookRegistry) -> None:
        contract = registry.get_wiki("agent_workflow_setup")
        assert isinstance(contract.license, str)
        assert len(contract.license) > 0

    def test_contract_has_entry_points(self, registry: StaticCookbookRegistry) -> None:
        contract = registry.get_wiki("agent_workflow_setup")
        assert isinstance(contract.entry_points, list)
        assert len(contract.entry_points) > 0

    def test_contract_is_validated(self, registry: StaticCookbookRegistry) -> None:
        contract = registry.get_wiki("agent_workflow_setup")
        assert contract.validation_state == "valid"
        assert contract.warnings == []


# ---------------------------------------------------------------------------
# get_wiki — missing ID
# ---------------------------------------------------------------------------

class TestGetWikiMissing:
    """Fetching an unknown wiki ID raises KeyError."""

    def test_unknown_id_raises_key_error(self, registry: StaticCookbookRegistry) -> None:
        with pytest.raises(KeyError):
            registry.get_wiki("nonexistent_wiki")

    def test_empty_string_raises_key_error(self, registry: StaticCookbookRegistry) -> None:
        with pytest.raises(KeyError):
            registry.get_wiki("")

    def test_wrong_case_raises_key_error(self, registry: StaticCookbookRegistry) -> None:
        with pytest.raises(KeyError):
            registry.get_wiki("AGENT_WORKFLOW_SETUP")

    def test_error_message_includes_id(self, registry: StaticCookbookRegistry) -> None:
        with pytest.raises(KeyError) as exc_info:
            registry.get_wiki("bogus")
        assert "bogus" in str(exc_info.value)


# ---------------------------------------------------------------------------
# Trust-state preservation
# ---------------------------------------------------------------------------

class TestTrustStatePreservation:
    """Each wiki's trust state is preserved correctly through the registry."""

    def test_agent_workflow_setup_is_verified(self, registry: StaticCookbookRegistry) -> None:
        contract = registry.get_wiki("agent_workflow_setup")
        assert contract.trust_state == TrustState.VERIFIED

    def test_terminal_setup_is_official(self, registry: StaticCookbookRegistry) -> None:
        contract = registry.get_wiki("terminal_setup")
        assert contract.trust_state == TrustState.OFFICIAL

    def test_mcp_basics_is_community(self, registry: StaticCookbookRegistry) -> None:
        contract = registry.get_wiki("mcp_basics")
        assert contract.trust_state == TrustState.COMMUNITY

    def test_trust_state_in_listing(self, registry: StaticCookbookRegistry) -> None:
        wikis = registry.list_wikis()
        states = {w.id: w.trust_state for w in wikis}
        assert states["agent_workflow_setup"] == TrustState.VERIFIED
        assert states["terminal_setup"] == TrustState.OFFICIAL
        assert states["mcp_basics"] == TrustState.COMMUNITY


# ---------------------------------------------------------------------------
# CLI/UI listing compatibility
# ---------------------------------------------------------------------------

class TestListingCompatibility:
    """Registry items expose enough data for a table/list-first UI or CLI."""

    def test_listing_has_all_ids(self, registry: StaticCookbookRegistry) -> None:
        """A CLI could build an id: name lookup table from the listing."""
        wikis = registry.list_wikis()
        lookup = {w.id: w.name for w in wikis}
        assert len(lookup) == len(wikis)  # no duplicate IDs

    def test_listing_fields_cover_display_needs(self, registry: StaticCookbookRegistry) -> None:
        """The four display fields (name, description, trust, version) are present."""
        wikis = registry.list_wikis()
        for w in wikis:
            # All fields are non-empty strings (trust_state is an enum, but we check it)
            assert all([
                isinstance(w.name, str) and len(w.name) > 0,
                isinstance(w.description, str) and len(w.description) > 0,
                isinstance(w.trust_state, TrustState),
                isinstance(w.version, str) and len(w.version) > 0,
            ])

    def test_listing_matches_contract_names(self, registry: StaticCookbookRegistry) -> None:
        """Listing names match the full contract names."""
        wikis = registry.list_wikis()
        for w in wikis:
            contract = registry.get_wiki(w.id)
            assert w.name == contract.name