"""Smoke tests for the Wiki Contract module seam.

The Wiki Contract module is importable and has the expected structure.
No product behavior is implemented yet — these tests verify the scaffold.
"""

import importlib


class TestContractsModule:
    """The ``iknow.contracts`` module exists and is importable."""

    def test_module_importable(self) -> None:
        mod = importlib.import_module("iknow.contracts")
        assert mod.__doc__ is not None
        assert "Wiki Contract" in mod.__doc__

    def test_all_modules_importable(self) -> None:
        """Every control-plane module is importable without errors."""
        modules = [
            "iknow",
            "iknow.cli",
            "iknow.contracts",
            "iknow.registry",
            "iknow.inventory",
            "iknow.fit",
            "iknow.harmonization",
            "iknow.compiler",
            "iknow.store",
            "iknow.serving",
            "iknow.validation",
        ]
        for name in modules:
            mod = importlib.import_module(name)
            assert mod is not None, f"{name} should import successfully"