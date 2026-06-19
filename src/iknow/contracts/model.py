"""Data models for Wiki Contract parsing and validation.

A Wiki Contract is the explicit agreement a knowledge base wiki exposes
to humans and agents: identity, scope, non-scope, provenance, freshness,
license, trust state, available entry points, and validation state.
"""

from __future__ import annotations

import enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional


class TrustState(enum.Enum):
    """Trust ladder for a knowledge base wiki."""

    COMMUNITY = "Community"
    VERIFIED = "Verified"
    OFFICIAL = "Official"

    @classmethod
    def _missing_(cls, value: object) -> Optional["TrustState"]:
        """Case-insensitive lookup; returns None for unrecognised values."""
        if isinstance(value, str):
            for member in cls:
                if member.value.lower() == value.lower():
                    return member
        return None


class ServingEntryPoint(enum.Enum):
    """Supported ways an agent can consume a knowledge base wiki."""

    MCP = "mcp"
    LLMS_TXT = "llms.txt"
    MARKDOWN = "markdown"
    INDEX_JSON = "index.json"

    @classmethod
    def _missing_(cls, value: object) -> Optional["ServingEntryPoint"]:
        """Case-insensitive lookup."""
        if isinstance(value, str):
            for member in cls:
                if member.value.lower() == value.lower():
                    return member
        return None


@dataclass
class InferredField:
    """A field whose value was inferred rather than declared in source metadata.

    ``inferred`` is True when the value was derived (e.g. from filenames,
    heuristics, or later enrichment) rather than present in the original
    source metadata.
    """

    value: str
    inferred: bool = False


@dataclass
class WikiContract:
    """Represents a parsed and validated Wiki Contract.

    Exposes all contract fields through simple attributes.  Validation
    results live in ``validation_state`` and ``warnings`` so callers can
    inspect contract health without parsing raw files.
    """

    # -- Identity -----------------------------------------------------------
    name: str
    description: str
    version: str

    # -- Scope --------------------------------------------------------------
    scope: List[str]
    non_scope: List[str]

    # -- Provenance & lifecycle ---------------------------------------------
    provenance: str
    freshness: str
    license: str

    # -- Trust --------------------------------------------------------------
    trust_state: TrustState

    # -- Serving ------------------------------------------------------------
    entry_points: List[ServingEntryPoint]

    # -- Inferred metadata --------------------------------------------------
    # Maps field-name → InferredField so callers can tell which values were
    # source-declared vs. derived.
    inferred_metadata: Dict[str, InferredField] = field(default_factory=dict)

    # -- Validation state ---------------------------------------------------
    validation_state: str = "unknown"  # "valid", "invalid", or "unknown"
    warnings: List[str] = field(default_factory=list)