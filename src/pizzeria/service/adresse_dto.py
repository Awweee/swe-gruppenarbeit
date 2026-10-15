"""DTO-Klasse für die Adresse, insbesondere ohne Decorators für SQLAlchemy."""

from dataclasses import dataclass
from typing import Self

from pizzeria.entity.adresse import Adresse
from pizzeria.service.exceptions import AdresseRequiredError

__all__ = ["AdresseDTO"]


@dataclass(eq=False, slots=True, kw_only=True)
class AdresseDTO:
    """DTO-Klasse für Adressdaten."""

    plz: str
    """Postleitzahl."""

    ort: str
    """Ort."""

    @classmethod
    def from_adresse(cls, adresse: Adresse | None) -> Self:
        """Initialisierung von AdresseDTO durch ein Entity-Objekt.

        :param adresse: Adresse-Objekt von SQLAlchemy
        :return: AdresseDTO mit den Adressdaten
        :rtype: AdresseDTO
        :raises AdresseRequiredError: Falls die Adresse None ist
        """
        if adresse is None:
            raise AdresseRequiredError

        return cls(
            plz=adresse.plz,
            ort=adresse.ort,
        )
