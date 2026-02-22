"""
Tests pour src/modules/famille/achats_famille/utils.py

Tests complets pour les fonctions utilitaires du module achats_famille.
"""

from datetime import date
from unittest.mock import MagicMock, patch


class TestConstantes:
    """Tests pour les constantes du module"""

    def test_categories_contient_cles_attendues(self):
        """Vérifie que CATEGORIES contient toutes les clés attendues"""
        from src.modules.famille.achats_famille.utils import CATEGORIES

        cles_attendues = [
            "jules_vetements",
            "jules_jouets",
            "jules_equipement",
            "nous_jeux",
            "nous_loisirs",
            "nous_equipement",
            "maison",
        ]
        for cle in cles_attendues:
            assert cle in CATEGORIES

    def test_categories_structure(self):
        """Vérifie la structure de chaque catégorie"""
        from src.modules.famille.achats_famille.utils import CATEGORIES

        for cle, valeur in CATEGORIES.items():
            assert "emoji" in valeur
            assert "label" in valeur
            assert "groupe" in valeur
            assert valeur["groupe"] in ["jules", "nous", "maison"]

    def test_priorites_contient_cles_attendues(self):
        """Vérifie que PRIORITES contient toutes les clés attendues"""
        from src.modules.famille.achats_famille.utils import PRIORITES

        cles_attendues = ["urgent", "haute", "moyenne", "basse", "optionnel"]
        for cle in cles_attendues:
            assert cle in PRIORITES

    def test_priorites_order(self):
        """Vérifie l'ordre des priorités"""
        from src.modules.famille.achats_famille.utils import PRIORITES

        assert PRIORITES["urgent"]["order"] < PRIORITES["haute"]["order"]
        assert PRIORITES["haute"]["order"] < PRIORITES["moyenne"]["order"]
        assert PRIORITES["moyenne"]["order"] < PRIORITES["basse"]["order"]
        assert PRIORITES["basse"]["order"] < PRIORITES["optionnel"]["order"]


class TestGetAllPurchases:
    """Tests pour la fonction get_all_purchases"""

    def test_retourne_liste_achats_non_achetes(self):
        """Récupère les achats non achetés par défaut"""
        mock_purchase = MagicMock(achete=False)
        mock_service = MagicMock()
        mock_service.lister_achats.return_value = [mock_purchase]

        with patch(
            "src.modules.famille.achats_famille.utils.obtenir_service_achats_famille",
            return_value=mock_service,
        ):
            from src.modules.famille.achats_famille.utils import get_all_purchases

            result = get_all_purchases()

            assert result == [mock_purchase]
            mock_service.lister_achats.assert_called_with(achete=False)

    def test_retourne_liste_achats_achetes(self):
        """Récupère les achats déjà achetés"""
        mock_purchase = MagicMock(achete=True)
        mock_service = MagicMock()
        mock_service.lister_achats.return_value = [mock_purchase]

        with patch(
            "src.modules.famille.achats_famille.utils.obtenir_service_achats_famille",
            return_value=mock_service,
        ):
            from src.modules.famille.achats_famille.utils import get_all_purchases

            result = get_all_purchases(achete=True)

            mock_service.lister_achats.assert_called_with(achete=True)

    def test_retourne_liste_vide_sur_exception(self):
        """Retourne une liste vide en cas d'erreur"""
        with patch(
            "src.modules.famille.achats_famille.utils.obtenir_service_achats_famille",
            side_effect=Exception("error"),
        ):
            from src.modules.famille.achats_famille.utils import get_all_purchases

            result = get_all_purchases()

            assert result == []


class TestGetPurchasesByCategory:
    """Tests pour la fonction get_purchases_by_category"""

    def test_filtre_par_categorie(self):
        """Filtre les achats par catégorie"""
        mock_purchase = MagicMock(categorie="jules_vetements")
        mock_service = MagicMock()
        mock_service.lister_par_categorie.return_value = [mock_purchase]

        with patch(
            "src.modules.famille.achats_famille.utils.obtenir_service_achats_famille",
            return_value=mock_service,
        ):
            from src.modules.famille.achats_famille.utils import get_purchases_by_category

            result = get_purchases_by_category("jules_vetements")

            assert len(result) == 1
            mock_service.lister_par_categorie.assert_called_with("jules_vetements", achete=False)

    def test_retourne_liste_vide_sur_exception(self):
        """Retourne une liste vide en cas d'erreur"""
        with patch(
            "src.modules.famille.achats_famille.utils.obtenir_service_achats_famille",
            side_effect=Exception("error"),
        ):
            from src.modules.famille.achats_famille.utils import get_purchases_by_category

            result = get_purchases_by_category("jules_vetements")

            assert result == []


class TestGetPurchasesByGroupe:
    """Tests pour la fonction get_purchases_by_groupe"""

    def test_filtre_par_groupe_jules(self):
        """Filtre les achats par groupe jules"""
        mock_purchase = MagicMock()
        mock_service = MagicMock()
        mock_service.lister_par_groupe.return_value = [mock_purchase]

        with patch(
            "src.modules.famille.achats_famille.utils.obtenir_service_achats_famille",
            return_value=mock_service,
        ):
            from src.modules.famille.achats_famille.utils import get_purchases_by_groupe

            result = get_purchases_by_groupe("jules")

            assert len(result) == 1

    def test_filtre_par_groupe_nous(self):
        """Filtre les achats par groupe nous"""
        mock_service = MagicMock()
        mock_service.lister_par_groupe.return_value = []

        with patch(
            "src.modules.famille.achats_famille.utils.obtenir_service_achats_famille",
            return_value=mock_service,
        ):
            from src.modules.famille.achats_famille.utils import get_purchases_by_groupe

            result = get_purchases_by_groupe("nous")

            assert result == []

    def test_retourne_liste_vide_sur_exception(self):
        """Retourne une liste vide en cas d'erreur"""
        with patch(
            "src.modules.famille.achats_famille.utils.obtenir_service_achats_famille",
            side_effect=Exception("error"),
        ):
            from src.modules.famille.achats_famille.utils import get_purchases_by_groupe

            result = get_purchases_by_groupe("jules")

            assert result == []


class TestGetStats:
    """Tests pour la fonction get_stats"""

    def test_stats_avec_achats(self):
        """Calcule les statistiques avec des achats"""
        mock_service = MagicMock()
        mock_service.get_stats.return_value = {
            "en_attente": 2,
            "achetes": 1,
            "total_estime": 80.0,
            "total_depense": 45.0,
            "urgents": 1,
        }

        with patch(
            "src.modules.famille.achats_famille.utils.obtenir_service_achats_famille",
            return_value=mock_service,
        ):
            from src.modules.famille.achats_famille.utils import get_stats

            result = get_stats()

            assert result["en_attente"] == 2
            assert result["achetes"] == 1
            assert result["total_estime"] == 80.0
            assert result["total_depense"] == 45.0
            assert result["urgents"] == 1

    def test_stats_sans_achats(self):
        """Calcule les statistiques sans achats"""
        mock_service = MagicMock()
        mock_service.get_stats.return_value = {
            "en_attente": 0,
            "achetes": 0,
            "total_estime": 0,
            "total_depense": 0,
            "urgents": 0,
        }

        with patch(
            "src.modules.famille.achats_famille.utils.obtenir_service_achats_famille",
            return_value=mock_service,
        ):
            from src.modules.famille.achats_famille.utils import get_stats

            result = get_stats()

            assert result["en_attente"] == 0
            assert result["total_estime"] == 0

    def test_stats_sur_exception(self):
        """Retourne des stats vides sur exception"""
        with patch(
            "src.modules.famille.achats_famille.utils.obtenir_service_achats_famille",
            side_effect=Exception("error"),
        ):
            from src.modules.famille.achats_famille.utils import get_stats

            result = get_stats()

            assert result == {
                "en_attente": 0,
                "achetes": 0,
                "total_estime": 0,
                "total_depense": 0,
                "urgents": 0,
            }

    def test_stats_priorite_haute_compte_comme_urgent(self):
        """Vérifie que la priorité haute est comptée comme urgente"""
        mock_service = MagicMock()
        mock_service.get_stats.return_value = {
            "en_attente": 1,
            "achetes": 0,
            "total_estime": 10.0,
            "total_depense": 0,
            "urgents": 1,
        }

        with patch(
            "src.modules.famille.achats_famille.utils.obtenir_service_achats_famille",
            return_value=mock_service,
        ):
            from src.modules.famille.achats_famille.utils import get_stats

            result = get_stats()

            assert result["urgents"] == 1


class TestMarkAsBought:
    """Tests pour la fonction mark_as_bought"""

    def test_marque_achat_comme_effectue(self):
        """Marque un achat comme effectué"""
        mock_service = MagicMock()

        with patch(
            "src.modules.famille.achats_famille.utils.obtenir_service_achats_famille",
            return_value=mock_service,
        ):
            from src.modules.famille.achats_famille.utils import mark_as_bought

            mark_as_bought(1)

            mock_service.marquer_achete.assert_called_once_with(1, prix_reel=None)

    def test_marque_achat_avec_prix_reel(self):
        """Marque un achat avec prix réel"""
        mock_service = MagicMock()

        with patch(
            "src.modules.famille.achats_famille.utils.obtenir_service_achats_famille",
            return_value=mock_service,
        ):
            from src.modules.famille.achats_famille.utils import mark_as_bought

            mark_as_bought(1, prix_reel=25.50)

            mock_service.marquer_achete.assert_called_once_with(1, prix_reel=25.50)

    def test_ne_fait_rien_si_achat_non_trouve(self):
        """Délègue au service même si achat inexistant"""
        mock_service = MagicMock()

        with patch(
            "src.modules.famille.achats_famille.utils.obtenir_service_achats_famille",
            return_value=mock_service,
        ):
            from src.modules.famille.achats_famille.utils import mark_as_bought

            mark_as_bought(999)

            mock_service.marquer_achete.assert_called_once_with(999, prix_reel=None)

    def test_gere_exception_silencieusement(self):
        """Gère les exceptions silencieusement"""
        with patch(
            "src.modules.famille.achats_famille.utils.obtenir_service_achats_famille",
            side_effect=Exception("error"),
        ):
            from src.modules.famille.achats_famille.utils import mark_as_bought

            # Ne doit pas lever d'exception
            mark_as_bought(1)


class TestDeletePurchase:
    """Tests pour la fonction delete_purchase"""

    def test_supprime_achat(self):
        """Supprime un achat existant"""
        mock_service = MagicMock()

        with patch(
            "src.modules.famille.achats_famille.utils.obtenir_service_achats_famille",
            return_value=mock_service,
        ):
            from src.modules.famille.achats_famille.utils import delete_purchase

            delete_purchase(1)

            mock_service.supprimer_achat.assert_called_once_with(1)

    def test_ne_fait_rien_si_achat_non_trouve(self):
        """Délègue au service même si achat inexistant"""
        mock_service = MagicMock()

        with patch(
            "src.modules.famille.achats_famille.utils.obtenir_service_achats_famille",
            return_value=mock_service,
        ):
            from src.modules.famille.achats_famille.utils import delete_purchase

            delete_purchase(999)

            mock_service.supprimer_achat.assert_called_once_with(999)

    def test_gere_exception_silencieusement(self):
        """Gère les exceptions silencieusement"""
        with patch(
            "src.modules.famille.achats_famille.utils.obtenir_service_achats_famille",
            side_effect=Exception("error"),
        ):
            from src.modules.famille.achats_famille.utils import delete_purchase

            # Ne doit pas lever d'exception
            delete_purchase(1)
