"""Exceptions in der Geschäftslogik."""

from pizzeria.repository.pizzeria_suchparameter import PizzeriaSuchparameter

__all__ = [
    "AdresseRequiredError",
    "NotFoundError",
]


class NotFoundError(Exception):
    """Exception, falls keine Pizzeria gefunden wurde."""

    def __init__(
        self,
        pizzeria_id: int | None = None,
        suchparameter: PizzeriaSuchparameter | None = None,
    ) -> None:
        """Initialisierung von NotFoundError.

        :param pizzeria_id: Pizzeria-ID, zu der nichts gefunden wurde
        :param suchparameter: Suchparameter, zu denen nichts gefunden wurde
        """
        super().__init__("Not Found")
        self.pizzeria_id = pizzeria_id
        self.suchparameter = suchparameter


class AdresseRequiredError(RuntimeError):
    """Exception, falls eine Adresse None ist."""

    def __init__(self) -> None:
        """Initialisierung von AdresseRequiredError."""
        super().__init__("Ungueltiger Zustand: Adresse ist None")
