from __future__ import annotations

from datetime import date
from unittest.mock import MagicMock, patch

from src.services.core.events import EvenementDomaine
from src.services.famille.budget import BudgetService, CategorieDepense


def test_on_achat_achete_cree_depense_depuis_prix_reel():
    with patch("src.services.famille.budget.service.obtenir_bus"):
        service = BudgetService()

    service.ajouter_depense = MagicMock()
    event = EvenementDomaine(
        type="achats.achete",
        data={
            "nom": "Pull Jules",
            "categorie": "jules_vetements",
            "prix_reel": 34.9,
        },
        source="tests",
    )

    service._on_achat_achete(event)

    service.ajouter_depense.assert_called_once()
    depense = service.ajouter_depense.call_args.args[0]
    assert depense.montant == 34.9
    assert depense.categorie == CategorieDepense.VETEMENTS
    assert depense.description == "Achat validé: Pull Jules"
    assert depense.date == date.today()


def test_on_achat_achete_utilise_prix_estime_si_prix_reel_absent():
    with patch("src.services.famille.budget.service.obtenir_bus"):
        service = BudgetService()

    service.ajouter_depense = MagicMock()
    event = EvenementDomaine(
        type="achats.achete",
        data={
            "nom": "Jeu éducatif",
            "categorie": "jouets_jules",
            "prix_estime": "19.5",
        },
        source="tests",
    )

    service._on_achat_achete(event)

    service.ajouter_depense.assert_called_once()
    depense = service.ajouter_depense.call_args.args[0]
    assert depense.montant == 19.5
    assert depense.categorie == CategorieDepense.ENFANT


def test_on_achat_achete_ignore_montant_invalide_ou_negatif():
    with patch("src.services.famille.budget.service.obtenir_bus"):
        service = BudgetService()

    service.ajouter_depense = MagicMock()

    service._on_achat_achete(
        EvenementDomaine(
            type="achats.achete",
            data={"prix_reel": "abc", "categorie": "jules_vetements"},
            source="tests",
        )
    )
    service._on_achat_achete(
        EvenementDomaine(
            type="achats.achete",
            data={"prix_reel": -1, "categorie": "jules_vetements"},
            source="tests",
        )
    )
    service._on_achat_achete(
        EvenementDomaine(
            type="achats.achete",
            data={"prix_estime": 0, "categorie": "jules_vetements"},
            source="tests",
        )
    )

    service.ajouter_depense.assert_not_called()
