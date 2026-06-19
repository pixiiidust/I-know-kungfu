"""Load a Wiki Contract from a JSON fixture on disk.

Usage::

    from iknow.contracts.loader import load

    contract = load("path/to/contract.json")
    print(contract.name, contract.validation_state)
"""

from __future__ import annotations

import json
from typing import Dict, List

from iknow.contracts.model import (
    InferredField,
    ServingEntryPoint,
    TrustState,
    WikiContract,
)
from iknow.contracts.validate import validate


def load(path: str) -> WikiContract:
    """Parse a Wiki Contract from a JSON fixture file.

    Parameters
    ----------
    path:
        Filesystem path to a JSON file containing the contract fields.

    Returns
    -------
    WikiContract
        A fully populated contract object with validation already run
        (``validation_state`` and ``warnings`` reflect the result).
    """
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return load_from_dict(data)


def load_from_dict(data: dict) -> WikiContract:
    """Parse a Wiki Contract from an already-deserialised Python dict.

    This is the primary construction path; ``load()`` delegates here after
    reading the file.
    """
    # -- Identity -----------------------------------------------------------
    name = _str(data, "name", "")
    description = _str(data, "description", "")
    version = _str(data, "version", "")

    # -- Scope --------------------------------------------------------------
    scope = _str_list(data, "scope")
    non_scope = _str_list(data, "non_scope")

    # -- Provenance & lifecycle ---------------------------------------------
    provenance = _str(data, "provenance", "")
    freshness = _str(data, "freshness", "")
    license = _str(data, "license", "")

    # -- Trust --------------------------------------------------------------
    trust_state = _parse_trust(data)

    # -- Serving ------------------------------------------------------------
    entry_points = _parse_entry_points(data)

    # -- Inferred metadata --------------------------------------------------
    inferred_metadata = _parse_inferred(data)

    contract = WikiContract(
        name=name,
        description=description,
        version=version,
        scope=scope,
        non_scope=non_scope,
        provenance=provenance,
        freshness=freshness,
        license=license,
        trust_state=trust_state,
        entry_points=entry_points,
        inferred_metadata=inferred_metadata,
    )

    # Run validation and attach results.
    validate(contract)
    return contract


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _str(data: dict, key: str, default: str) -> str:
    val = data.get(key, default)
    if isinstance(val, str):
        return val
    return default


def _str_list(data: dict, key: str) -> List[str]:
    raw = data.get(key, [])
    if isinstance(raw, list):
        return [str(item) for item in raw if isinstance(item, str)]
    return []


def _parse_trust(data: dict) -> TrustState:
    raw = data.get("trust_state", "")
    if isinstance(raw, str) and raw:
        ts = TrustState._missing_(raw)
        if ts is not None:
            return ts
    return TrustState.COMMUNITY


def _parse_entry_points(data: dict) -> List[ServingEntryPoint]:
    raw = data.get("entry_points", [])
    if not isinstance(raw, list):
        return []
    result: List[ServingEntryPoint] = []
    for item in raw:
        if isinstance(item, str):
            ep = ServingEntryPoint._missing_(item)
            if ep is not None:
                result.append(ep)
    return result


def _parse_inferred(data: dict) -> Dict[str, InferredField]:
    """Extract inferred-metadata hints from the raw dict.

    The fixture may include a top-level key ``_inferred`` mapping
    field names to boolean (True = value was derived, not source-declared).

    For every field named in ``_inferred``, we create an ``InferredField``
    wrapper around the actual value present in the same ``data`` dict.
    """
    raw = data.get("_inferred", {})
    if not isinstance(raw, dict):
        return {}

    result: Dict[str, InferredField] = {}
    for field_name, is_inferred in raw.items():
        if not isinstance(is_inferred, bool):
            continue
        # Pull the actual value for this field from the main data dict.
        actual_value = data.get(field_name)
        if actual_value is None:
            continue
        # Convert lists and other types to a display-friendly string.
        if isinstance(actual_value, list):
            display = ", ".join(str(v) for v in actual_value)
        else:
            display = str(actual_value)
        result[field_name] = InferredField(value=display, inferred=is_inferred)
    return result