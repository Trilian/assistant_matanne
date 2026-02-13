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
        mock_purchase = MagicMock()
        mock_purchase.achete = False

        mock_db = MagicMock()
        mock_db.query.return_value.filter_by.return_value.all.return_value = [mock_purchase]

        with patch("src.modules.famille.achats_famille.utils.obtenir_contexte_db") as mock_ctx:
            mock_ctx.return_value.__enter__ = MagicMock(return_value=mock_db)
            mock_ctx.return_value.__exit__ = MagicMock(return_value=False)

            from src.modules.famille.achats_famille.utils import get_all_purchases

            result = get_all_purchases()

            assert result == [mock_purchase]
            mock_db.query.return_value.filter_by.assert_called_with(achete=False)

    def test_retourne_liste_achats_achetes(self):
        """Récupère les achats déjà achetés"""
        mock_purchase = MagicMock()
        mock_purchase.achete = True

        mock_db = MagicMock()
        mock_db.query.return_value.filter_by.return_value.all.return_value = [mock_purchase]

        with patch("src.modules.famille.achats_famille.utils.obtenir_contexte_db") as mock_ctx:
            mock_ctx.return_value.__enter__ = MagicMock(return_value=mock_db)
            mock_ctx.return_value.__exit__ = MagicMock(return_value=False)

            from src.modules.famille.achats_famille.utils import get_all_purchases

            result = get_all_purchases(achete=True)

            mock_db.query.return_value.filter_by.assert_called_with(achete=True)

    def test_retourne_liste_vide_sur_exception(self):
        """Retourne une liste vide en cas d'erreur"""
        with patch("src.modules.famille.achats_famille.utils.obtenir_contexte_db") as mock_ctx:
            mock_ctx.side_effect = Exception("DB error")

            from src.modules.famille.achats_famille.utils import get_all_purchases

            result = get_all_purchases()

            assert result == []


class TestGetPurchasesByCategory:
    """Tests pour la fonction get_purchases_by_category"""

    def test_filtre_par_categorie(self):
        """Filtre les achats par catégorie"""
        mock_purchase = MagicMock()
        mock_purchase.categorie = "jules_vetements"

        mock_db = MagicMock()
        mock_query = mock_db.query.return_value
        mock_filter = mock_query.filter.return_value
        mock_filter.order_by.return_value.all.return_value = [mock_purchase]

        with patch("src.modules.famille.achats_famille.utils.obtenir_contexte_db") as mock_ctx:
            mock_ctx.return_value.__enter__ = MagicMock(return_value=mock_db)
            mock_ctx.return_value.__exit__ = MagicMock(return_value=False)

            from src.modules.famille.achats_famille.utils import get_purchases_by_category

            result = get_purchases_by_category("jules_vetements")

            assert len(result) == 1

    def test_retourne_liste_vide_sur_exception(self):
        """Retourne une liste vide en cas d'erreur"""
        with patch("src.modules.famille.achats_famille.utils.obtenir_contexte_db") as mock_ctx:
            mock_ctx.side_effect = Exception("DB error")

            from src.modules.famille.achats_famille.utils import get_purchases_by_category

            result = get_purchases_by_category("jules_vetements")

            assert result == []


class TestGetPurchasesByGroupe:
    """Tests pour la fonction get_purchases_by_groupe"""

    def test_filtre_par_groupe_jules(self):
        """Filtre les achats par groupe jules"""
        mock_purchase = MagicMock()

        mock_db = MagicMock()
        mock_query = mock_db.query.return_value
        mock_filter = mock_query.filter.return_value
        mock_filter.order_by.return_value.all.return_value = [mock_purchase]

        with patch("src.modules.famille.achats_famille.utils.obtenir_contexte_db") as mock_ctx:
            mock_ctx.return_value.__enter__ = MagicMock(return_value=mock_db)
            mock_ctx.return_value.__exit__ = MagicMock(return_value=False)

            from src.modules.famille.achats_famille.utils import get_purchases_by_groupe

            result = get_purchases_by_groupe("jules")

            assert len(result) == 1

    def test_filtre_par_groupe_nous(self):
        """Filtre les achats par groupe nous"""
        mock_db = MagicMock()
        mock_query = mock_db.query.return_value
        mock_filter = mock_query.filter.return_value
        mock_filter.order_by.return_value.all.return_value = []

        with patch("src.modules.famille.achats_famille.utils.obtenir_contexte_db") as mock_ctx:
            mock_ctx.return_value.__enter__ = MagicMock(return_value=mock_db)
            mock_ctx.return_value.__exit__ = MagicMock(return_value=False)

            from src.modules.famille.achats_famille.utils import get_purchases_by_groupe

            result = get_purchases_by_groupe("nous")

            assert result == []

    def test_retourne_liste_vide_sur_exception(self):
        """Retourne une liste vide en cas d'erreur"""
        with patch("src.modules.famille.achats_famille.utils.obtenir_contexte_db") as mock_ctx:
            mock_ctx.side_effect = Exception("DB error")

            from src.modules.famille.achats_famille.utils import get_purchases_by_groupe

            result = get_purchases_by_groupe("jules")

            assert result == []


class TestGetStats:
    """Tests pour la fonction get_stats"""

    def test_stats_avec_achats(self):
        """Calcule les statistiques avec des achats"""
        # Achats en attente
        mock_en_attente_1 = MagicMock()
        mock_en_attente_1.prix_estime = 50.0
        mock_en_attente_1.priorite = "urgent"

        mock_en_attente_2 = MagicMock()
        mock_en_attente_2.prix_estime = 30.0
        mock_en_attente_2.priorite = "basse"

        # Achats effectués
        mock_achete = MagicMock()
        mock_achete.prix_reel = 45.0
        mock_achete.prix_estime = 50.0

        mock_db = MagicMock()

        def filter_by_side_effect(achete):
            mock_result = MagicMock()
            if achete:
                mock_result.all.return_value = [mock_achete]
            else:
                mock_result.all.return_value = [mock_en_attente_1, mock_en_attente_2]
            return mock_result

        mock_db.query.return_value.filter_by.side_effect = filter_by_side_effect

        with patch("src.modules.famille.achats_famille.utils.obtenir_contexte_db") as mock_ctx:
            mock_ctx.return_value.__enter__ = MagicMock(return_value=mock_db)
            mock_ctx.return_value.__exit__ = MagicMock(return_value=False)

            from src.modules.famille.achats_famille.utils import get_stats

            result = get_stats()

            assert result["en_attente"] == 2
            assert result["achetes"] == 1
            assert result["total_estime"] == 80.0
            assert result["total_depense"] == 45.0
            assert result["urgents"] == 1

    def test_stats_sans_achats(self):
        """Calcule les statistiques sans achats"""
        mock_db = MagicMock()
        mock_db.query.return_value.filter_by.return_value.all.return_value = []

        with patch("src.modules.famille.achats_famille.utils.obtenir_contexte_db") as mock_ctx:
            mock_ctx.return_value.__enter__ = MagicMock(return_value=mock_db)
            mock_ctx.return_value.__exit__ = MagicMock(return_value=False)

            from src.modules.famille.achats_famille.utils import get_stats

            result = get_stats()

            assert result["en_attente"] == 0
            assert result["total_estime"] == 0

    def test_stats_sur_exception(self):
        """Retourne des stats vides sur exception"""
        with patch("src.modules.famille.achats_famille.utils.obtenir_contexte_db") as mock_ctx:
            mock_ctx.side_effect = Exception("DB error")

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
        mock_urgent = MagicMock()
        mock_urgent.prix_estime = 10.0
        mock_urgent.priorite = "haute"

        mock_db = MagicMock()

        def filter_by_side_effect(achete):
            mock_result = MagicMock()
            if not achete:
                mock_result.all.return_value = [mock_urgent]
            else:
                mock_result.all.return_value = []
            return mock_result

        mock_db.query.return_value.filter_by.side_effect = filter_by_side_effect

        with patch("src.modules.famille.achats_famille.utils.obtenir_contexte_db") as mock_ctx:
            mock_ctx.return_value.__enter__ = MagicMock(return_value=mock_db)
            mock_ctx.return_value.__exit__ = MagicMock(return_value=False)

            from src.modules.famille.achats_famille.utils import get_stats

            result = get_stats()

            assert result["urgents"] == 1


class TestMarkAsBought:
    """Tests pour la fonction mark_as_bought"""

    def test_marque_achat_comme_effectue(self):
        """Marque un achat comme effectué"""
        mock_purchase = MagicMock()
        mock_purchase.achete = False

        mock_db = MagicMock()
        mock_db.get.return_value = mock_purchase

        with patch("src.modules.famille.achats_famille.utils.obtenir_contexte_db") as mock_ctx:
            mock_ctx.return_value.__enter__ = MagicMock(return_value=mock_db)
            mock_ctx.return_value.__exit__ = MagicMock(return_value=False)

            from src.modules.famille.achats_famille.utils import mark_as_bought

            mark_as_bought(1)

            assert mock_purchase.achete is True
            assert mock_purchase.date_achat == date.today()
            mock_db.commit.assert_called_once()

    def test_marque_achat_avec_prix_reel(self):
        """Marque un achat avec prix réel"""
        mock_purchase = MagicMock()
        mock_purchase.prix_reel = None

        mock_db = MagicMock()
        mock_db.get.return_value = mock_purchase

        with patch("src.modules.famille.achats_famille.utils.obtenir_contexte_db") as mock_ctx:
            mock_ctx.return_value.__enter__ = MagicMock(return_value=mock_db)
            mock_ctx.return_value.__exit__ = MagicMock(return_value=False)

            from src.modules.famille.achats_famille.utils import mark_as_bought

            mark_as_bought(1, prix_reel=25.50)

            assert mock_purchase.prix_reel == 25.50

    def test_ne_fait_rien_si_achat_non_trouve(self):
        """Ne fait rien si l'achat n'existe pas"""
        mock_db = MagicMock()
        mock_db.get.return_value = None

        with patch("src.modules.famille.achats_famille.utils.obtenir_contexte_db") as mock_ctx:
            mock_ctx.return_value.__enter__ = MagicMock(return_value=mock_db)
            mock_ctx.return_value.__exit__ = MagicMock(return_value=False)

            from src.modules.famille.achats_famille.utils import mark_as_bought

            mark_as_bought(999)

            mock_db.commit.assert_not_called()

    def test_gere_exception_silencieusement(self):
        """Gère les exceptions silencieusement"""
        with patch("src.modules.famille.achats_famille.utils.obtenir_contexte_db") as mock_ctx:
            mock_ctx.side_effect = Exception("DB error")

            from src.modules.famille.achats_famille.utils import mark_as_bought

            # Ne doit pas lever d'exception
            mark_as_bought(1)


class TestDeletePurchase:
    """Tests pour la fonction delete_purchase"""

    def test_supprime_achat(self):
        """Supprime un achat existant"""
        mock_purchase = MagicMock()

        mock_db = MagicMock()
        mock_db.get.return_value = mock_purchase

        with patch("src.modules.famille.achats_famille.utils.obtenir_contexte_db") as mock_ctx:
            mock_ctx.return_value.__enter__ = MagicMock(return_value=mock_db)
            mock_ctx.return_value.__exit__ = MagicMock(return_value=False)

            from src.modules.famille.achats_famille.utils import delete_purchase

            delete_purchase(1)

            mock_db.delete.assert_called_once_with(mock_purchase)
            mock_db.commit.assert_called_once()

    def test_ne_fait_rien_si_achat_non_trouve(self):
        """Ne fait rien si l'achat n'existe pas"""
        mock_db = MagicMock()
        mock_db.get.return_value = None

        with patch("src.modules.famille.achats_famille.utils.obtenir_contexte_db") as mock_ctx:
            mock_ctx.return_value.__enter__ = MagicMock(return_value=mock_db)
            mock_ctx.return_value.__exit__ = MagicMock(return_value=False)

            from src.modules.famille.achats_famille.utils import delete_purchase

            delete_purchase(999)

            mock_db.delete.assert_not_called()

    def test_gere_exception_silencieusement(self):
        """Gère les exceptions silencieusement"""
        with patch("src.modules.famille.achats_famille.utils.obtenir_contexte_db") as mock_ctx:
            mock_ctx.side_effect = Exception("DB error")

            from src.modules.famille.achats_famille.utils import delete_purchase

            # Ne doit pas lever d'exception
            delete_purchase(1)
