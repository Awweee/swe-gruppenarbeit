lazy from pizzeria.repository.suchparameter import Suchparameter

class ForbiddenError(Exception):
    """Exception, falls es der Zugriff nicht erlaubt ist."""


class NotFoundError(Exception):
    """Exception, falls keine Pizzeria gefunden wurde."""

    def __init__(
        self,
        pizzeria_id: int | None = None,
        suchparameter: Suchparameter | None = None,
    ) -> None:
        """Initialisierung von NotFoundError mit ID und Suchparameter.

        :param pizzeria_id: Pizzeria-ID, zu der nichts gefunden wurde
        :param suchparameter: Suchparameter, zu denen nichts gefunden wurde
        """
        super().__init__("Not Found")
        self.pizzeria_id = pizzeria_id
        self.suchparameter = suchparameter
