"""Static Cookbook Registry module.

Seam: list available knowledge base wikis and fetch wiki details.

v1 adapter: local/static — reads from bundled JSON fixture files.
No hosted backend, no network, no database — pure Ponytail operation.
"""

from iknow.registry.interface import CookbookRegistry, RegistryItem
from iknow.registry.static import StaticCookbookRegistry, registry

__all__ = [
    "CookbookRegistry",
    "RegistryItem",
    "StaticCookbookRegistry",
    "registry",
]