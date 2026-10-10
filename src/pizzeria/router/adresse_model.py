"""Pydantic-Model für die Adresse einer Pizzeria."""

from typing import Annotated

from pydantic import BaseModel, ConfigDict, StringConstraints

from pizzeria.entity import Adresse

__all__ = ["AdresseModel"]


class AdresseModel(BaseModel):
    """Pydantic-Model für die Adresse einer Pizzeria."""

    strasse: Annotated[str, StringConstraints(min_length=1, max_length=128)]
    """Straße."""

    hausnummer: Annotated[str, StringConstraints(min_length=1, max_length=16)]
    """Hausnummer."""

    plz: Annotated[str, StringConstraints(pattern=r"^[0-9]{5}$")]
    """Fünfstellige Postleitzahl."""

    ort: Annotated[str, StringConstraints(min_length=1, max_length=64)]
    """Ort."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "strasse": "Kaiserstraße",
                "hausnummer": "12a",
                "plz": "76133",
                "ort": "Karlsruhe",
            },
        },
        strict=True,
        extra="forbid",
        frozen=True,
    )

    def to_adresse(self) -> Adresse:
        """Konvertierung in ein Adresse-Objekt für SQLAlchemy.

        :return: Adresse-Objekt für SQLAlchemy
        :rtype: Adresse
        """
        return Adresse(
            strasse=self.strasse,
            hausnummer=self.hausnummer,
            plz=self.plz,
            ort=self.ort,
        )
