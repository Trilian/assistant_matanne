"""
Tests pour les helpers UI - Fonctions pures et mocks DB
Couverture cible: Fonctions helpers sans dépendance Streamlit

Ces tests couvrent:
- Fonctions pures (formater_quantite, etc.)
- Fonctions avec DB (mocks)
- Styles CSS (validation structure)
"""
import pytest
from unittest.mock import MagicMock, patch, PropertyMock
from datetime import date, timedelta
import pandas as pd

# ═══════════════════════════════════════════════════════════
# TESTS HELPERS CUISINE UI
# ═══════════════════════════════════════════════════════════


@pytest.fixture
def mock_streamlit():
    """Mock Streamlit pour éviter les erreurs d'import."""
    with patch.dict("sys.modules", {"streamlit": MagicMock()}):
        yield


class TestFormaterQuantite:
    """Tests pour formater_quantite (recettes.py)"""

    def test_formater_entier(self, mock_streamlit):
        """Entier affiché sans décimale."""
        from src.domains.cuisine.ui.recettes import formater_quantite
        assert formater_quantite(2) == "2"
        assert formater_quantite(10) == "10"

    def test_formater_float_entier(self, mock_streamlit):
        """Float sans décimale affichée comme entier."""
        from src.domains.cuisine.ui.recettes import formater_quantite
        assert formater_quantite(2.0) == "2"
        assert formater_quantite(10.0) == "10"

    def test_formater_float_decimal(self, mock_streamlit):
        """Float avec décimale conservée."""
        from src.domains.cuisine.ui.recettes import formater_quantite
        assert formater_quantite(2.5) == "2.5"
        assert formater_quantite(0.25) == "0.25"

    def test_formater_string_numerique(self, mock_streamlit):
        """String numérique convertie."""
        from src.domains.cuisine.ui.recettes import formater_quantite
        assert formater_quantite("3") == "3"
        assert formater_quantite("3.0") == "3"
        assert formater_quantite("3.5") == "3.5"

    def test_formater_string_non_numerique(self, mock_streamlit):
        """String non numérique retournée telle quelle."""
        from src.domains.cuisine.ui.recettes import formater_quantite
        assert formater_quantite("quelques") == "quelques"
        assert formater_quantite("au goût") == "au goût"


# ═══════════════════════════════════════════════════════════
# TESTS HELPERS HUB FAMILLE
# ═══════════════════════════════════════════════════════════


class TestCalculerAgeJules:
    """Tests pour calculer_age_jules (hub_famille.py)"""

    @patch("src.domains.famille.ui.hub_famille.get_db_context")
    def test_calcul_age_basique(self, mock_db_context, mock_streamlit):
        """Calcule l'âge en mois depuis date de naissance."""
        from src.domains.famille.ui.hub_famille import calculer_age_jules
        
        # Mock du ChildProfile
        mock_child = MagicMock()
        mock_child.date_of_birth = date.today() - timedelta(days=580)  # ~19 mois
        mock_child.name = "Jules"
        mock_child.actif = True
        
        mock_db = MagicMock()
        mock_db.query().filter_by().first.return_value = mock_child
        mock_db_context.return_value.__enter__.return_value = mock_db
        
        result = calculer_age_jules()
        
        assert "mois" in result
        assert result["mois"] == 19
        assert "texte" in result

    @patch("src.domains.famille.ui.hub_famille.get_db_context")
    def test_calcul_age_sans_profil(self, mock_db_context, mock_streamlit):
        """Retourne valeur par défaut si pas de profil."""
        from src.domains.famille.ui.hub_famille import calculer_age_jules
        
        mock_db = MagicMock()
        mock_db.query().filter_by().first.return_value = None
        mock_db_context.return_value.__enter__.return_value = mock_db
        
        result = calculer_age_jules()
        
        assert result["mois"] == 19  # Valeur par défaut
        assert result["texte"] == "19 mois"


class TestUserStreak:
    """Tests pour get_user_streak (hub_famille.py)"""

    @patch("src.domains.famille.ui.hub_famille.get_db_context")
    def test_streak_zero_sans_user(self, mock_db_context, mock_streamlit):
        """Streak = 0 si utilisateur introuvable."""
        from src.domains.famille.ui.hub_famille import get_user_streak
        
        mock_db = MagicMock()
        mock_db.query().filter_by().first.return_value = None
        mock_db_context.return_value.__enter__.return_value = mock_db
        
        result = get_user_streak("unknown")
        assert result == 0

    @patch("src.domains.famille.ui.hub_famille.get_db_context")
    def test_streak_zero_sans_summaries(self, mock_db_context, mock_streamlit):
        """Streak = 0 sans résumés quotidiens."""
        from src.domains.famille.ui.hub_famille import get_user_streak
        
        mock_user = MagicMock()
        mock_user.id = 1
        mock_user.objectif_pas_quotidien = 10000
        
        mock_db = MagicMock()
        mock_db.query().filter_by().first.return_value = mock_user
        mock_db.query().filter().order_by().all.return_value = []
        mock_db_context.return_value.__enter__.return_value = mock_db
        
        result = get_user_streak("test_user")
        assert result == 0


class TestCountFunctions:
    """Tests pour les fonctions de comptage."""

    @patch("src.domains.famille.ui.hub_famille.get_db_context")
    def test_count_pending_purchases_zero(self, mock_db_context, mock_streamlit):
        """Compte achats en attente."""
        from src.domains.famille.ui.hub_famille import count_pending_purchases
        
        mock_db = MagicMock()
        mock_db.query().filter_by().count.return_value = 0
        mock_db_context.return_value.__enter__.return_value = mock_db
        
        result = count_pending_purchases()
        assert result == 0

    @patch("src.domains.famille.ui.hub_famille.get_db_context")
    def test_count_pending_purchases_some(self, mock_db_context, mock_streamlit):
        """Compte achats en attente > 0."""
        from src.domains.famille.ui.hub_famille import count_pending_purchases
        
        mock_db = MagicMock()
        mock_db.query().filter_by().count.return_value = 5
        mock_db_context.return_value.__enter__.return_value = mock_db
        
        result = count_pending_purchases()
        assert result == 5

    @patch("src.domains.famille.ui.hub_famille.get_db_context")
    def test_count_urgent_purchases(self, mock_db_context, mock_streamlit):
        """Compte achats urgents."""
        from src.domains.famille.ui.hub_famille import count_urgent_purchases
        
        mock_db = MagicMock()
        mock_db.query().filter().count.return_value = 2
        mock_db_context.return_value.__enter__.return_value = mock_db
        
        result = count_urgent_purchases()
        assert result == 2


# ═══════════════════════════════════════════════════════════
# TESTS CSS STYLES
# ═══════════════════════════════════════════════════════════


class TestCSSStyles:
    """Tests pour les constantes CSS."""

    def test_card_styles_defined(self, mock_streamlit):
        """CARD_STYLES contient du CSS valide."""
        from src.domains.famille.ui.hub_famille import CARD_STYLES
        
        assert "<style>" in CARD_STYLES
        assert "</style>" in CARD_STYLES
        assert ".family-card" in CARD_STYLES

    def test_card_styles_classes(self, mock_streamlit):
        """Classes CSS pour les cards définies."""
        from src.domains.famille.ui.hub_famille import CARD_STYLES
        
        assert ".family-card.jules" in CARD_STYLES
        assert ".family-card.weekend" in CARD_STYLES
        assert ".family-card.anne" in CARD_STYLES
        assert ".family-card.mathieu" in CARD_STYLES


# ═══════════════════════════════════════════════════════════
# TESTS HELPERS PLANNING UI
# ═══════════════════════════════════════════════════════════


class TestChargerDonneesSemaine:
    """Tests pour charger_donnees_semaine (calendrier_unifie.py)"""

    @patch("src.domains.planning.ui.calendrier_unifie.obtenir_contexte_db")
    def test_charger_donnees_structure(self, mock_db_context, mock_streamlit):
        """Retourne la structure de données attendue."""
        from src.domains.planning.ui.calendrier_unifie import charger_donnees_semaine
        
        mock_db = MagicMock()
        mock_db.query().filter().first.return_value = None
        mock_db.query().filter().all.return_value = []
        mock_db_context.return_value.__enter__.return_value = mock_db
        
        result = charger_donnees_semaine(date.today())
        
        assert "repas" in result
        assert "sessions_batch" in result
        assert "activites" in result
        assert "events" in result
        assert isinstance(result["repas"], list)
    
    @patch("src.domains.planning.ui.calendrier_unifie.obtenir_contexte_db")
    def test_charger_donnees_avec_erreur(self, mock_db_context, mock_streamlit):
        """Gère les erreurs sans crash."""
        from src.domains.planning.ui.calendrier_unifie import charger_donnees_semaine
        
        mock_db_context.return_value.__enter__.side_effect = Exception("DB Error")
        
        # Ne doit pas lever d'exception
        result = charger_donnees_semaine(date.today())
        
        assert isinstance(result, dict)


# ═══════════════════════════════════════════════════════════
# TESTS HELPERS INVENTAIRE UI
# ═══════════════════════════════════════════════════════════


class TestPrepareDataframe:
    """Tests pour les fonctions de préparation de dataframes."""

    def test_prepare_inventory_dataframe_empty(self, mock_streamlit):
        """Dataframe vide si liste vide."""
        from src.domains.cuisine.ui.inventaire import _prepare_inventory_dataframe
        
        result = _prepare_inventory_dataframe([])
        
        assert len(result) == 0
        assert isinstance(result, pd.DataFrame)

    def test_prepare_inventory_dataframe_with_data(self, mock_streamlit):
        """Dataframe avec données."""
        from src.domains.cuisine.ui.inventaire import _prepare_inventory_dataframe
        
        inventaire = [
            {
                "ingredient_nom": "Tomates",
                "ingredient_categorie": "Légumes",
                "quantite": 5.0,
                "unite": "kg",
                "quantite_min": 2.0,
                "emplacement": "Frigo",
                "jours_avant_peremption": 7,
                "statut": "ok",
                "derniere_maj": date.today().isoformat()
            }
        ]
        
        result = _prepare_inventory_dataframe(inventaire)
        
        assert len(result) == 1
        assert "Article" in result.columns

    def test_prepare_alert_dataframe_empty(self, mock_streamlit):
        """Dataframe alertes vide."""
        from src.domains.cuisine.ui.inventaire import _prepare_alert_dataframe
        
        result = _prepare_alert_dataframe([])
        
        assert len(result) == 0
        assert isinstance(result, pd.DataFrame)

    def test_prepare_alert_dataframe_critique(self, mock_streamlit):
        """Dataframe alertes avec article critique."""
        from src.domains.cuisine.ui.inventaire import _prepare_alert_dataframe
        
        articles = [
            {
                "ingredient_nom": "Lait",
                "ingredient_categorie": "Produits laitiers",
                "quantite": 0.5,
                "unite": "L",
                "quantite_min": 2.0,
                "emplacement": "Frigo",
                "jours_avant_peremption": None,
                "statut": "critique"
            }
        ]
        
        result = _prepare_alert_dataframe(articles)
        
        assert len(result) == 1
        assert "Article" in result.columns
        assert "Problème" in result.columns

    def test_prepare_alert_dataframe_peremption(self, mock_streamlit):
        """Dataframe alertes avec péremption proche."""
        from src.domains.cuisine.ui.inventaire import _prepare_alert_dataframe
        
        articles = [
            {
                "ingredient_nom": "Yaourt",
                "ingredient_categorie": "Produits laitiers",
                "quantite": 4.0,
                "unite": "pièces",
                "quantite_min": 2.0,
                "emplacement": "Frigo",
                "jours_avant_peremption": 2,
                "statut": "peremption_proche"
            }
        ]
        
        result = _prepare_alert_dataframe(articles)
        
        assert len(result) == 1
        # Problème doit mentionner les jours
        assert "2 jours" in result.iloc[0]["Problème"]


# ═══════════════════════════════════════════════════════════
# TESTS HELPERS WEEKEND ACTIVITIES
# ═══════════════════════════════════════════════════════════


class TestCountWeekendActivities:
    """Tests pour count_weekend_activities (hub_famille.py)"""

    @patch("src.domains.famille.ui.hub_famille.get_db_context")
    def test_count_zero(self, mock_db_context, mock_streamlit):
        """Aucune activité planifiée."""
        from src.domains.famille.ui.hub_famille import count_weekend_activities
        
        mock_db = MagicMock()
        mock_db.query().filter().count.return_value = 0
        mock_db_context.return_value.__enter__.return_value = mock_db
        
        result = count_weekend_activities()
        assert result == 0

    @patch("src.domains.famille.ui.hub_famille.get_db_context")
    def test_count_some(self, mock_db_context, mock_streamlit):
        """Plusieurs activités planifiées."""
        from src.domains.famille.ui.hub_famille import count_weekend_activities
        
        mock_db = MagicMock()
        mock_db.query().filter().count.return_value = 3
        mock_db_context.return_value.__enter__.return_value = mock_db
        
        result = count_weekend_activities()
        assert result == 3


class TestGetUserGarminConnected:
    """Tests pour get_user_garmin_connected (hub_famille.py)"""

    @patch("src.domains.famille.ui.hub_famille.get_db_context")
    def test_garmin_connected(self, mock_db_context, mock_streamlit):
        """Utilisateur avec Garmin connecté."""
        from src.domains.famille.ui.hub_famille import get_user_garmin_connected
        
        mock_user = MagicMock()
        mock_user.garmin_connected = True
        
        mock_db = MagicMock()
        mock_db.query().filter_by().first.return_value = mock_user
        mock_db_context.return_value.__enter__.return_value = mock_db
        
        result = get_user_garmin_connected("test_user")
        assert result is True

    @patch("src.domains.famille.ui.hub_famille.get_db_context")
    def test_garmin_not_connected(self, mock_db_context, mock_streamlit):
        """Utilisateur sans Garmin connecté."""
        from src.domains.famille.ui.hub_famille import get_user_garmin_connected
        
        mock_user = MagicMock()
        mock_user.garmin_connected = False
        
        mock_db = MagicMock()
        mock_db.query().filter_by().first.return_value = mock_user
        mock_db_context.return_value.__enter__.return_value = mock_db
        
        result = get_user_garmin_connected("test_user")
        assert result is False

    @patch("src.domains.famille.ui.hub_famille.get_db_context")
    def test_garmin_user_not_found(self, mock_db_context, mock_streamlit):
        """Utilisateur introuvable."""
        from src.domains.famille.ui.hub_famille import get_user_garmin_connected
        
        mock_db = MagicMock()
        mock_db.query().filter_by().first.return_value = None
        mock_db_context.return_value.__enter__.return_value = mock_db
        
        result = get_user_garmin_connected("unknown")
        assert result is False
