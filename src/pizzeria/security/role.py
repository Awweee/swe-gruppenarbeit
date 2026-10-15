from enum import StrEnum


class Role(StrEnum):
    """Enum für Rollen."""

    ADMIN = "ADMIN"
    """Rolle für die Administration."""

    PIZZERIA = "PIZZERIA"
    """Rolle für Pizzerien."""
