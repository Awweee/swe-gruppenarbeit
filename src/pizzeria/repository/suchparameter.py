from dataclasses import dataclass

__all__ = ["Suchparameter"]

@dataclass
class Suchparameter:
   name: str | None
   email: str | None
   def is_empty(self) -> bool:
        """Prüft, ob alle Suchparameter None sind."""
        return self.name is None and self.email is None
