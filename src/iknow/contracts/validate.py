"""Validation for Wiki Contract objects.

Checks required fields and populates ``validation_state`` and ``warnings``
on the provided ``WikiContract``.

All validation functions mutate the contract in-place — they live in a
separate module so callers can choose to skip validation or add custom
rules without touching the loader.
"""

from __future__ import annotations

from typing import List

from iknow.contracts.model import WikiContract

# Fields that must be non-empty for a contract to be considered valid.
_REQUIRED_TEXT_FIELDS = [
    "name",
    "description",
    "provenance",
    "freshness",
    "license",
]

_REQUIRED_LIST_FIELDS = [
    "scope",
    "non_scope",
]


def validate(contract: WikiContract) -> None:
    """Run all built-in validation rules against *contract*.

    Results are stored in-place on ``contract.validation_state`` and
    ``contract.warnings``.  Never raises — callers can inspect the
    contract safely even for malformed data.
    """
    warnings: List[str] = []

    _check_required_text(contract, warnings)
    _check_required_lists(contract, warnings)
    _check_entry_points(contract, warnings)

    if warnings:
        contract.validation_state = "invalid"
    else:
        contract.validation_state = "valid"
    contract.warnings = warnings


# ---------------------------------------------------------------------------
# Individual checks
# ---------------------------------------------------------------------------

def _check_required_text(contract: WikiContract, warnings: List[str]) -> None:
    for field_name in _REQUIRED_TEXT_FIELDS:
        value = getattr(contract, field_name, None)
        if not value or (isinstance(value, str) and value.strip() == ""):
            warnings.append(f"Missing required field: {field_name}")


def _check_required_lists(contract: WikiContract, warnings: List[str]) -> None:
    for field_name in _REQUIRED_LIST_FIELDS:
        value = getattr(contract, field_name, None)
        if not value or (isinstance(value, list) and len(value) == 0):
            warnings.append(f"Missing required field: {field_name}")


def _check_entry_points(contract: WikiContract, warnings: List[str]) -> None:
    if not contract.entry_points:
        warnings.append("No serving entry points defined")