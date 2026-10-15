"""Filter für die Pizzeriasuche."""

from dataclasses import dataclass

__all__ = ["PizzeriaSuchparameter"]


@dataclass(frozen=True, slots=True, kw_only=True)
class PizzeriaSuchparameter:
    """Suchparameter für die Pizzeriasuche."""

    name: str | None = None
    """Teil des Namens als Suchparameter."""

    def is_empty(self) -> bool:
        """Prüft, ob kein Suchparameter gesetzt ist."""
        return self.name is None
