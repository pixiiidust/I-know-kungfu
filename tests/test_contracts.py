"""Tests for Wiki Contract parsing and validation.

Covers:
- Valid contract loading through the public interface
- Contract field exposure (identity, scope, non-scope, provenance, etc.)
- Missing required metadata (validation without crashing)
- Inferred metadata represented distinctly from source-declared metadata
- All three trust states (Community, Verified, Official)
- Serving entry points
"""

import os

from iknow.contracts import load, load_from_dict, validate
from iknow.contracts.model import (
    InferredField,
    ServingEntryPoint,
    TrustState,
    WikiContract,
)

_FIXTURES = os.path.join(os.path.dirname(__file__), "fixtures")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _fixture_path(name: str) -> str:
    return os.path.join(_FIXTURES, name)


# ---------------------------------------------------------------------------
# Valid contract
# ---------------------------------------------------------------------------

class TestValidContract:
    """A well-formed Wiki Contract fixture loads and exposes all fields."""

    def test_load_from_file(self) -> None:
        contract = load(_fixture_path("valid_contract.json"))
        assert isinstance(contract, WikiContract)

    def test_identity_fields(self) -> None:
        contract = load(_fixture_path("valid_contract.json"))
        assert contract.name == "Pixi Package Manager Wiki"
        assert "Pixi package manager" in contract.description
        assert contract.version == "1.0.0"

    def test_scope_fields(self) -> None:
        contract = load(_fixture_path("valid_contract.json"))
        assert "package management" in contract.scope
        assert "conda" in contract.scope

    def test_non_scope_fields(self) -> None:
        contract = load(_fixture_path("valid_contract.json"))
        assert "npm internals" in contract.non_scope
        assert "pip internals" in contract.non_scope

    def test_provenance_freshness_license(self) -> None:
        contract = load(_fixture_path("valid_contract.json"))
        assert contract.provenance == "https://pixi.sh/latest/"
        assert contract.freshness == "2025-01-15"
        assert contract.license == "BSD-3-Clause"

    def test_trust_state(self) -> None:
        contract = load(_fixture_path("valid_contract.json"))
        assert contract.trust_state == TrustState.OFFICIAL

    def test_serving_entry_points(self) -> None:
        contract = load(_fixture_path("valid_contract.json"))
        expected = {
            ServingEntryPoint.MCP,
            ServingEntryPoint.LLMS_TXT,
            ServingEntryPoint.MARKDOWN,
            ServingEntryPoint.INDEX_JSON,
        }
        assert set(contract.entry_points) == expected

    def test_validation_state_is_valid(self) -> None:
        contract = load(_fixture_path("valid_contract.json"))
        assert contract.validation_state == "valid"
        assert contract.warnings == []

    def test_no_inferred_fields_on_explicit_contract(self) -> None:
        contract = load(_fixture_path("valid_contract.json"))
        assert contract.inferred_metadata == {}


# ---------------------------------------------------------------------------
# Missing required metadata
# ---------------------------------------------------------------------------

class TestMissingFields:
    """A contract with missing required fields is loaded and reports warnings."""

    def test_loads_without_crashing(self) -> None:
        contract = load(_fixture_path("missing_fields_contract.json"))
        assert isinstance(contract, WikiContract)

    def test_validation_state_is_invalid(self) -> None:
        contract = load(_fixture_path("missing_fields_contract.json"))
        assert contract.validation_state == "invalid"

    def test_warnings_list_missing_fields(self) -> None:
        contract = load(_fixture_path("missing_fields_contract.json"))
        assert len(contract.warnings) > 0

    def test_warning_for_description(self) -> None:
        contract = load(_fixture_path("missing_fields_contract.json"))
        assert any("description" in w for w in contract.warnings)

    def test_warning_for_provenance(self) -> None:
        contract = load(_fixture_path("missing_fields_contract.json"))
        assert any("provenance" in w for w in contract.warnings)

    def test_warning_for_freshness(self) -> None:
        contract = load(_fixture_path("missing_fields_contract.json"))
        assert any("freshness" in w for w in contract.warnings)

    def test_warning_for_license(self) -> None:
        contract = load(_fixture_path("missing_fields_contract.json"))
        assert any("license" in w for w in contract.warnings)

    def test_warning_for_non_scope(self) -> None:
        contract = load(_fixture_path("missing_fields_contract.json"))
        assert any("non_scope" in w for w in contract.warnings)

    def test_no_warning_for_scope(self) -> None:
        """scope *is* provided in the fixture, so no warning for it."""
        contract = load(_fixture_path("missing_fields_contract.json"))
        scope_warnings = [w for w in contract.warnings if w.strip() == "Missing required field: scope"]
        assert len(scope_warnings) == 0

    def test_entry_points_warning_when_empty(self) -> None:
        contract = load(_fixture_path("missing_fields_contract.json"))
        assert any("entry points" in w for w in contract.warnings)


# ---------------------------------------------------------------------------
# Inferred metadata
# ---------------------------------------------------------------------------

class TestInferredMetadata:
    """Inferred metadata is represented distinctly from source-declared."""

    def test_loads(self) -> None:
        contract = load(_fixture_path("inferred_contract.json"))
        assert isinstance(contract, WikiContract)

    def test_inferred_fields_populated(self) -> None:
        contract = load(_fixture_path("inferred_contract.json"))
        assert "description" in contract.inferred_metadata
        assert "license" in contract.inferred_metadata

    def test_inferred_field_values(self) -> None:
        contract = load(_fixture_path("inferred_contract.json"))
        desc = contract.inferred_metadata["description"]
        assert isinstance(desc, InferredField)
        assert desc.inferred is True
        assert contract.description in desc.value

    def test_non_inferred_field_not_in_metadata(self) -> None:
        contract = load(_fixture_path("inferred_contract.json"))
        # 'name' and 'version' are not in _inferred
        assert "name" not in contract.inferred_metadata
        assert "version" not in contract.inferred_metadata

    def test_source_declared_fields_still_accessible_directly(self) -> None:
        contract = load(_fixture_path("inferred_contract.json"))
        assert contract.description != ""  # still has a value
        assert contract.license == "MIT"

    def test_validation_passes(self) -> None:
        contract = load(_fixture_path("inferred_contract.json"))
        assert contract.validation_state == "valid"


# ---------------------------------------------------------------------------
# Trust states
# ---------------------------------------------------------------------------

class TestTrustStates:
    """All three trust states are accepted and preserved."""

    def test_community(self) -> None:
        contract = load_from_dict({
            "name": "C",
            "description": "d",
            "version": "1",
            "scope": ["a"],
            "non_scope": ["b"],
            "provenance": "https://x",
            "freshness": "2025-01",
            "license": "MIT",
            "trust_state": "Community",
            "entry_points": ["mcp"],
        })
        assert contract.trust_state == TrustState.COMMUNITY

    def test_verified(self) -> None:
        contract = load_from_dict({
            "name": "C",
            "description": "d",
            "version": "1",
            "scope": ["a"],
            "non_scope": ["b"],
            "provenance": "https://x",
            "freshness": "2025-01",
            "license": "MIT",
            "trust_state": "Verified",
            "entry_points": ["mcp"],
        })
        assert contract.trust_state == TrustState.VERIFIED

    def test_official(self) -> None:
        contract = load_from_dict({
            "name": "C",
            "description": "d",
            "version": "1",
            "scope": ["a"],
            "non_scope": ["b"],
            "provenance": "https://x",
            "freshness": "2025-01",
            "license": "MIT",
            "trust_state": "Official",
            "entry_points": ["mcp"],
        })
        assert contract.trust_state == TrustState.OFFICIAL

    def test_case_insensitive_community(self) -> None:
        contract = load_from_dict({
            "name": "C",
            "description": "d",
            "version": "1",
            "scope": ["a"],
            "non_scope": ["b"],
            "provenance": "https://x",
            "freshness": "2025-01",
            "license": "MIT",
            "trust_state": "community",
            "entry_points": ["mcp"],
        })
        assert contract.trust_state == TrustState.COMMUNITY

    def test_unrecognised_falls_back_to_community(self) -> None:
        contract = load_from_dict({
            "name": "C",
            "description": "d",
            "version": "1",
            "scope": ["a"],
            "non_scope": ["b"],
            "provenance": "https://x",
            "freshness": "2025-01",
            "license": "MIT",
            "trust_state": "UnknownState",
            "entry_points": ["mcp"],
        })
        # Falls back to Community per loader default
        assert contract.trust_state == TrustState.COMMUNITY


# ---------------------------------------------------------------------------
# Serving entry points
# ---------------------------------------------------------------------------

class TestServingEntryPoints:
    """Serving entry points are parsed correctly."""

    def test_all_entry_points(self) -> None:
        contract = load_from_dict({
            "name": "C",
            "description": "d",
            "version": "1",
            "scope": ["a"],
            "non_scope": ["b"],
            "provenance": "https://x",
            "freshness": "2025-01",
            "license": "MIT",
            "trust_state": "Community",
            "entry_points": ["mcp", "llms.txt", "markdown", "index.json"],
        })
        assert ServingEntryPoint.MCP in contract.entry_points
        assert ServingEntryPoint.LLMS_TXT in contract.entry_points
        assert ServingEntryPoint.MARKDOWN in contract.entry_points
        assert ServingEntryPoint.INDEX_JSON in contract.entry_points

    def test_case_insensitive_entry_point(self) -> None:
        contract = load_from_dict({
            "name": "C",
            "description": "d",
            "version": "1",
            "scope": ["a"],
            "non_scope": ["b"],
            "provenance": "https://x",
            "freshness": "2025-01",
            "license": "MIT",
            "trust_state": "Community",
            "entry_points": ["MCP", "LLMS.TXT"],
        })
        assert ServingEntryPoint.MCP in contract.entry_points
        assert ServingEntryPoint.LLMS_TXT in contract.entry_points

    def test_unknown_entry_point_skipped(self) -> None:
        contract = load_from_dict({
            "name": "C",
            "description": "d",
            "version": "1",
            "scope": ["a"],
            "non_scope": ["b"],
            "provenance": "https://x",
            "freshness": "2025-01",
            "license": "MIT",
            "trust_state": "Community",
            "entry_points": ["mcp", "unknown_protocol"],
        })
        assert ServingEntryPoint.MCP in contract.entry_points
        assert len(contract.entry_points) == 1


# ---------------------------------------------------------------------------
# Public interface (smoke)
# ---------------------------------------------------------------------------

class TestPublicInterface:
    """The module's public interface exposes expected names."""

    def test_module_exports_load(self) -> None:
        from iknow.contracts import load as _load
        assert callable(_load)

    def test_module_exports_validate(self) -> None:
        from iknow.contracts import validate as _validate
        assert callable(_validate)

    def test_module_exports_model_classes(self) -> None:
        from iknow.contracts import WikiContract, InferredField, TrustState
        assert WikiContract is not None
        assert InferredField is not None
        assert TrustState is not None

    def test_load_from_dict_accessible(self) -> None:
        from iknow.contracts import load_from_dict
        assert callable(load_from_dict)


# ---------------------------------------------------------------------------
# Explicit validate() call on pre-built contract
# ---------------------------------------------------------------------------

class TestExplicitValidate:
    """Calling validate() directly on a contract works."""

    def test_validate_valid_contract(self) -> None:
        contract = WikiContract(
            name="Test",
            description="A test wiki",
            version="1",
            scope=["topic"],
            non_scope=["other"],
            provenance="https://example.com",
            freshness="2025-01",
            license="MIT",
            trust_state=TrustState.COMMUNITY,
            entry_points=[ServingEntryPoint.MCP],
        )
        validate(contract)
        assert contract.validation_state == "valid"
        assert contract.warnings == []

    def test_validate_invalid_contract(self) -> None:
        contract = WikiContract(
            name="",
            description="",
            version="",
            scope=[],
            non_scope=[],
            provenance="",
            freshness="",
            license="",
            trust_state=TrustState.COMMUNITY,
            entry_points=[],
        )
        validate(contract)
        assert contract.validation_state == "invalid"
        assert len(contract.warnings) > 0