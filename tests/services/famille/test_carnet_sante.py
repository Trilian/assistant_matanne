"""Tests du référentiel vaccinal famille aligné avec la configuration Jules."""

from __future__ import annotations

import json

from src.services.famille.carnet_sante import DATA_DIR, ServiceCarnetSante


def test_calendrier_vaccinal_limite_aux_rappels_a_partir_de_6_ans() -> None:
    service = ServiceCarnetSante()

    vaccins = service._charger_calendrier_vaccinal()

    assert vaccins
    assert all(vaccin.get("doses") for vaccin in vaccins)
    assert all(
        int(dose.get("age_mois", 0)) >= 72
        for vaccin in vaccins
        for dose in vaccin.get("doses", [])
    )


def test_fichier_reference_documente_le_filtre_jules() -> None:
    chemin = DATA_DIR / "reference" / "calendrier_vaccinal_fr.json"

    with open(chemin, encoding="utf-8") as handle:
        data = json.load(handle)

    assert "6 ans" in data["meta"]["description"]
    assert all(
        int(dose.get("age_mois", 0)) >= 72
        for vaccin in data.get("vaccins", [])
        for dose in vaccin.get("doses", [])
    )
