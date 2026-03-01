"""
Singleton pattern utilities for server components.

Provides a unified base class for singleton instances.
"""

from __future__ import annotations

from typing import Any, ClassVar


class Singleton:
    """
    Base class for singleton instances.

    Uses class variables to store the single instance and ensures
    only one instance exists throughout the application lifecycle.
    """

    _instance: ClassVar[Singleton | None] = None

    def __new__(cls) -> Singleton:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        """Subclasses should override if they need initialization logic."""
        pass
