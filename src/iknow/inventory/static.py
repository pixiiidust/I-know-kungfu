"""Static fixture-backed Local Knowledge Inventory.

Produces a deterministic inventory without scanning private files.
This is the v1 Ponytail adapter — pure fixture data, no filesystem
scanning, no mutation, no cloud.
"""

from __future__ import annotations

from iknow.contracts.model import ServingEntryPoint, TrustState
from iknow.inventory.model import InventoryItem, LocalKnowledgeInventory


def build_default_inventory() -> LocalKnowledgeInventory:
    """Build and return the bundled default Local Knowledge Inventory.

    The default inventory represents a typical local development knowledge
    base with Python tooling, shell configuration, and basic MCP concepts.
    No filesystem scanning or private file access occurs.

    Returns
    -------
    LocalKnowledgeInventory
        A fully populated inventory with three knowledge areas.
    """
    items = [
        InventoryItem(
            id="python_dev",
            name="Python Development",
            description="Local Python environment, packaging, and tooling knowledge.",
            scope=[
                "Python packaging",
                "virtual environments",
                "pip and setuptools",
                "testing with pytest",
                "code formatting",
            ],
            non_scope=[
                "Python internals",
                "CPython implementation details",
                "alternative Python runtimes",
            ],
            entry_points=[ServingEntryPoint.MARKDOWN, ServingEntryPoint.MCP],
            trust_state=TrustState.VERIFIED,
        ),
        InventoryItem(
            id="shell_config",
            name="Shell Configuration",
            description="Terminal setup, shell aliases, and environment management.",
            scope=[
                "shell configuration",
                "environment variables",
                "aliases and functions",
                "terminal emulators",
            ],
            non_scope=[
                "GUI desktop environments",
                "window managers",
            ],
            entry_points=[ServingEntryPoint.MARKDOWN],
            trust_state=TrustState.OFFICIAL,
        ),
        InventoryItem(
            id="mcp_tools",
            name="MCP Tools",
            description="Basic Model Context Protocol understanding and local tooling.",
            scope=[
                "MCP protocol concepts",
                "tool and resource definitions",
                "MCP server development",
            ],
            non_scope=[
                "production MCP deployment",
                "authentication and authorization",
            ],
            entry_points=[ServingEntryPoint.MCP, ServingEntryPoint.LLMS_TXT],
            trust_state=TrustState.COMMUNITY,
        ),
    ]

    return LocalKnowledgeInventory(
        name="Default Local Knowledge Base",
        description=(
            "Local development knowledge covering Python tooling, "
            "shell configuration, and MCP basics."
        ),
        items=items,
    )


# Convenience singleton — same as calling build_default_inventory().
_default_inventory: LocalKnowledgeInventory | None = None


def get_inventory() -> LocalKnowledgeInventory:
    """Return the shared default inventory singleton.

    Lazily initialised on first call.
    """
    global _default_inventory
    if _default_inventory is None:
        _default_inventory = build_default_inventory()
    return _default_inventory