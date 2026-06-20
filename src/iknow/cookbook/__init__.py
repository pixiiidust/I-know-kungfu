"""Cookbook Registry module.

Seam: discover and export knowledge base wikis from the cookbook.

v1 adapter: local/static export from compiled wiki directories.
No hosted backend, no network, no database — pure local operation.
"""

from iknow.cookbook.export import export_cookbook_registry

__all__ = [
    "export_cookbook_registry",
]
