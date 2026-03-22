"""
Tests unitaires pour les modèles batch_cooking.

Module: src.core.models.batch_cooking
"""

import pytest

from src.core.models.batch_cooking import (
    LocalisationStockageEnum,
    StatutEtapeEnum,
    StatutSessionEnum,
    TypeRobotEnum,
)


@pytest.mark.unit
class TestBatchCookingEnums:
    """Tests pour les enums du batch cooking."""

    def test_statut_session_valeurs(self):
        """StatutSessionEnum contient les 4 statuts attendus."""
        assert StatutSessionEnum.PLANIFIEE == "planifiee"
        assert StatutSessionEnum.EN_COURS == "en_cours"
        assert StatutSessionEnum.TERMINEE == "terminee"
        assert StatutSessionEnum.ANNULEE == "annulee"
        assert len(StatutSessionEnum) == 4

    def test_statut_etape_valeurs(self):
        """StatutEtapeEnum contient les 4 statuts attendus."""
        assert StatutEtapeEnum.A_FAIRE == "a_faire"
        assert StatutEtapeEnum.EN_COURS == "en_cours"
        assert StatutEtapeEnum.TERMINEE == "terminee"
        assert StatutEtapeEnum.PASSEE == "passee"
        assert len(StatutEtapeEnum) == 4

    def test_type_robot_valeurs(self):
        """TypeRobotEnum contient les 9 robots attendus."""
        assert TypeRobotEnum.COOKEO == "cookeo"
        assert TypeRobotEnum.MONSIEUR_CUISINE == "monsieur_cuisine"
        assert TypeRobotEnum.AIRFRYER == "airfryer"
        assert TypeRobotEnum.FOUR == "four"
        assert TypeRobotEnum.PLAQUES == "plaques"
        assert len(TypeRobotEnum) == 9

    def test_localisation_stockage_valeurs(self):
        """LocalisationStockageEnum contient les 3 localisations."""
        assert LocalisationStockageEnum.FRIGO == "frigo"
        assert LocalisationStockageEnum.CONGELATEUR == "congelateur"
        assert LocalisationStockageEnum.TEMPERATURE_AMBIANTE == "temperature_ambiante"
        assert len(LocalisationStockageEnum) == 3

    def test_enums_sont_des_str(self):
        """Les enums sont des StrEnum — utilisables comme str."""
        assert isinstance(StatutSessionEnum.PLANIFIEE, str)
        assert isinstance(TypeRobotEnum.COOKEO, str)
        assert f"statut: {StatutSessionEnum.EN_COURS}" == "statut: en_cours"
