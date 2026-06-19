"""Wiki Contract module.

Seam: expose and validate a Wiki Contract while hiding whether it came from
``iknow.yaml``, a filesystem scan, static registry data, or later hosted
endpoints.

v1 adapter: local-only, reads from static files or YAML on disk.
No hosted registry, auth, or cloud dependency.
"""

from iknow.contracts.loader import load, load_from_dict
from iknow.contracts.model import (
    InferredField,
    ServingEntryPoint,
    TrustState,
    WikiContract,
)
from iknow.contracts.validate import validate

__all__ = [
    "load",
    "load_from_dict",
    "validate",
    "WikiContract",
    "InferredField",
    "ServingEntryPoint",
    "TrustState",
]