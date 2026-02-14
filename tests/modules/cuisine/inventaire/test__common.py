"""
Tests pour src/modules/cuisine/inventaire/_common.py

Tests complets pour vérifier les imports et exports du module _common.
"""


class TestCommonImports:
    """Tests pour les imports du module _common"""

    def test_import_module(self):
        """Vérifie que le module s'importe correctement"""
        from src.modules.cuisine.inventaire import _common

        assert _common is not None

    def test_all_exports_defined(self):
        """Vérifie que __all__ est défini"""
        from src.modules.cuisine.inventaire._common import __all__

        assert isinstance(__all__, list)
        assert len(__all__) > 0

    def test_export_logger(self):
        """Vérifie l'export du logger"""
        from src.modules.cuisine.inventaire._common import logger

        assert logger is not None

    def test_export_streamlit(self):
        """Vérifie l'export de streamlit"""
        from src.modules.cuisine.inventaire._common import st

        assert st is not None

    def test_export_pandas(self):
        """Vérifie l'export de pandas"""
        from src.modules.cuisine.inventaire._common import pd

        assert pd is not None

    def test_export_date_types(self):
        """Vérifie l'export des types date"""
        from src.modules.cuisine.inventaire._common import date, timedelta

        assert date is not None
        assert timedelta is not None

    def test_export_any_type(self):
        """Vérifie l'export du type Any"""
        from src.modules.cuisine.inventaire._common import Any

        assert Any is not None


class TestCommonServices:
    """Tests pour les services exportés"""

    def test_export_inventaire_service(self):
        """Vérifie l'export du service inventaire"""
        from src.modules.cuisine.inventaire._common import get_inventaire_service

        assert callable(get_inventaire_service)

    def test_export_predictions_service(self):
        """Vérifie l'export du service prédictions"""
        from src.modules.cuisine.inventaire._common import obtenir_service_predictions

        assert callable(obtenir_service_predictions)

    def test_export_erreur_validation(self):
        """Vérifie l'export de ErreurValidation"""
        from src.modules.cuisine.inventaire._common import ErreurValidation

        assert ErreurValidation is not None
        # Vérifie que c'est une exception
        assert issubclass(ErreurValidation, Exception)


class TestCommonLogicFunctions:
    """Tests pour les fonctions logiques exportées"""

    def test_export_emplacements(self):
        """Vérifie l'export des EMPLACEMENTS"""
        from src.modules.cuisine.inventaire._common import EMPLACEMENTS

        assert isinstance(EMPLACEMENTS, list | tuple | dict)

    def test_export_categories(self):
        """Vérifie l'export des CATEGORIES"""
        from src.modules.cuisine.inventaire._common import CATEGORIES

        assert isinstance(CATEGORIES, list | tuple | dict)

    def test_export_status_config(self):
        """Vérifie l'export de STATUS_CONFIG"""
        from src.modules.cuisine.inventaire._common import STATUS_CONFIG

        assert isinstance(STATUS_CONFIG, dict)

    def test_export_calculer_status_stock(self):
        """Vérifie l'export de calculer_status_stock"""
        from src.modules.cuisine.inventaire._common import calculer_status_stock

        assert callable(calculer_status_stock)

    def test_export_calculer_status_peremption(self):
        """Vérifie l'export de calculer_status_peremption"""
        from src.modules.cuisine.inventaire._common import calculer_status_peremption

        assert callable(calculer_status_peremption)

    def test_export_calculer_alertes(self):
        """Vérifie l'export de calculer_alertes"""
        from src.modules.cuisine.inventaire._common import calculer_alertes

        assert callable(calculer_alertes)

    def test_export_calculer_statistiques_inventaire(self):
        """Vérifie l'export de calculer_statistiques_inventaire"""
        from src.modules.cuisine.inventaire._common import calculer_statistiques_inventaire

        assert callable(calculer_statistiques_inventaire)

    def test_export_valider_article_inventaire(self):
        """Vérifie l'export de valider_article_inventaire"""
        from src.modules.cuisine.inventaire._common import valider_article_inventaire

        assert callable(valider_article_inventaire)

    def test_export_formater_article_inventaire(self):
        """Vérifie l'export de formater_article_inventaire"""
        from src.modules.cuisine.inventaire._common import formater_article_inventaire

        assert callable(formater_article_inventaire)

    def test_export_trier_par_urgence(self):
        """Vérifie l'export de trier_par_urgence"""
        from src.modules.cuisine.inventaire._common import trier_par_urgence

        assert callable(trier_par_urgence)

    def test_export_filtrer_par_status(self):
        """Vérifie l'export de filtrer_par_status"""
        from src.modules.cuisine.inventaire._common import filtrer_par_status

        assert callable(filtrer_par_status)

    def test_export_filtrer_par_categorie(self):
        """Vérifie l'export de filtrer_par_categorie"""
        from src.modules.cuisine.inventaire._common import filtrer_par_categorie

        assert callable(filtrer_par_categorie)

    def test_export_filtrer_par_emplacement(self):
        """Vérifie l'export de filtrer_par_emplacement"""
        from src.modules.cuisine.inventaire._common import filtrer_par_emplacement

        assert callable(filtrer_par_emplacement)

    def test_export_grouper_par_categorie(self):
        """Vérifie l'export de grouper_par_categorie"""
        from src.modules.cuisine.inventaire._common import grouper_par_categorie

        assert callable(grouper_par_categorie)


class TestCommonAllExports:
    """Tests pour vérifier que tous les exports __all__ sont accessibles"""

    def test_all_exports_importable(self):
        """Vérifie que tous les éléments de __all__ sont importables"""
        from src.modules.cuisine.inventaire import _common

        for name in _common.__all__:
            assert hasattr(_common, name), f"{name} not found in module"
            obj = getattr(_common, name)
            assert obj is not None, f"{name} is None"

    def test_exports_count(self):
        """Vérifie le nombre d'exports"""
        from src.modules.cuisine.inventaire._common import __all__

        # Au moins 15 exports attendus
        assert len(__all__) >= 15


class TestCommonModuleStructure:
    """Tests pour la structure du module"""

    def test_module_docstring(self):
        """Vérifie que le module a une docstring"""
        from src.modules.cuisine.inventaire import _common

        assert _common.__doc__ is not None

    def test_logging_configured(self):
        """Vérifie que logging est importé"""
        from src.modules.cuisine.inventaire._common import logging

        assert logging is not None
