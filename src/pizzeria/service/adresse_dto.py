from dataclasses import dataclass

import strawberry

from pizzeria.entity.adresse import Adresse


@dataclass(eq=False, slots=True, kw_only=True)
@strawberry.type(name="Adresse")
class AdresseDTO:
    """DTO-Klasse für die Adresse, insbesondere ohne Decorators für SQLAlchemy."""

    plz: str
    ort: str
    strasse: str
    hausnummer: str


    @classmethod
    def from_adresse(cls, adresse: Adresse | None) -> AdresseDTO:
        """Initialisierung von AdresseDTO durch ein Entity-Objekt von Adresse.

        :param adresse: Adresse-Objekt mit Decorators für SQLAlchemy
        :return: AdresseDTO-Objekt mit Daten aus dem Adresse-Objekt
        :rtype: AdresseDTO
        :raises AdresseRequiredError: falls adresse None ist
        """

        return cls(
            plz=adresse.plz,
            ort=adresse.ort,
            strasse=adresse.strasse,
            hausnummer=adresse.hausnummer,
        )
