"""Local Knowledge Inventory module.

Seam: produce a Local Knowledge Inventory describing the user's existing
knowledge base (overview, scope, entry points, trust posture).

v1 adapter: optional filesystem scan with manual fallback. No vector DB,
no cloud sync.
"""

from iknow.inventory.graphify import (
    inventory_from_graphify_graph,
    load_graphify_inventory,
)
from iknow.inventory.model import InventoryItem, LocalKnowledgeInventory
from iknow.inventory.static import build_default_inventory, get_inventory

__all__ = [
    "InventoryItem",
    "LocalKnowledgeInventory",
    "build_default_inventory",
    "get_inventory",
    "inventory_from_graphify_graph",
    "load_graphify_inventory",
]
