"""
Tests pour les helpers UI - Fonctions pures sans dépendances externes
Couverture cible: Fonctions helpers pures testables sans DB externe

Ces tests couvrent:
- Fonctions pures (formater_quantite, etc.)
- Fonctions de transformation de données
- Validation de formats
"""
import pytest
from unittest.mock import MagicMock, patch
from datetime import date, timedelta
import pandas as pd


# ═══════════════════════════════════════════════════════════
# FIXTURE MOCK STREAMLIT
# ═══════════════════════════════════════════════════════════

@pytest.fixture
def mock_streamlit():
    """Mock Streamlit pour éviter les erreurs d'import."""
    with patch.dict("sys.modules", {"streamlit": MagicMock()}):
        yield


# ═══════════════════════════════════════════════════════════
# TESTS HELPERS CUISINE UI - RECETTES
# ═══════════════════════════════════════════════════════════


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
# TESTS HELPERS INVENTAIRE UI
# ═══════════════════════════════════════════════════════════


class TestPrepareInventoryDataframe:
    """Tests pour _prepare_inventory_dataframe (inventaire.py)"""

    def test_prepare_empty_dataframe(self, mock_streamlit):
        """Dataframe vide si pas d'inventaire."""
        from src.domains.cuisine.ui.inventaire.helpers import _prepare_inventory_dataframe
        
        result = _prepare_inventory_dataframe([])
        
        assert len(result) == 0
        assert isinstance(result, pd.DataFrame)

    def test_prepare_dataframe_with_data(self, mock_streamlit):
        """Dataframe avec données."""
        from src.domains.cuisine.ui.inventaire.helpers import _prepare_inventory_dataframe
        
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

    def test_prepare_dataframe_colonnes(self, mock_streamlit):
        """Vérifier les colonnes du dataframe."""
        from src.domains.cuisine.ui.inventaire.helpers import _prepare_inventory_dataframe
        
        inventaire = [
            {
                "ingredient_nom": "Lait",
                "ingredient_categorie": "Produits laitiers",
                "quantite": 2.0,
                "unite": "L",
                "quantite_min": 1.0,
                "emplacement": "Frigo",
                "jours_avant_peremption": 5,
                "statut": "ok",
                "derniere_maj": date.today().isoformat()
            }
        ]
        
        result = _prepare_inventory_dataframe(inventaire)
        
        expected_columns = ["Article", "Catégorie", "Quantité", "Emplacement", "Statut"]
        for col in expected_columns:
            assert col in result.columns, f"Colonne '{col}' manquante"


class TestPrepareAlertDataframe:
    """Tests pour _prepare_alert_dataframe (inventaire.py)"""

    def test_prepare_alert_dataframe_empty(self, mock_streamlit):
        """Dataframe alertes vide."""
        from src.domains.cuisine.ui.inventaire.helpers import _prepare_alert_dataframe
        
        result = _prepare_alert_dataframe([])
        
        assert len(result) == 0
        assert isinstance(result, pd.DataFrame)

    def test_prepare_alert_dataframe_critique(self, mock_streamlit):
        """Dataframe alertes avec article critique."""
        from src.domains.cuisine.ui.inventaire.helpers import _prepare_alert_dataframe
        
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
        from src.domains.cuisine.ui.inventaire.helpers import _prepare_alert_dataframe
        
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

    def test_prepare_alert_dataframe_colonnes(self, mock_streamlit):
        """Vérifier les colonnes du dataframe alertes."""
        from src.domains.cuisine.ui.inventaire.helpers import _prepare_alert_dataframe
        
        articles = [
            {
                "ingredient_nom": "Beurre",
                "ingredient_categorie": "Produits laitiers",
                "quantite": 0.1,
                "unite": "kg",
                "quantite_min": 0.5,
                "emplacement": "Frigo",
                "jours_avant_peremption": None,
                "statut": "critique"
            }
        ]
        
        result = _prepare_alert_dataframe(articles)
        
        expected_columns = ["Article", "Catégorie", "Problème", "Quantité"]
        for col in expected_columns:
            assert col in result.columns, f"Colonne '{col}' manquante"


# ═══════════════════════════════════════════════════════════
# TESTS UTILITAIRES PLANNING UI - CALCULS PURS
# ═══════════════════════════════════════════════════════════


class TestCalculsDatesPures:
    """Tests pour les calculs de dates pures (sans DB)."""
    
    def test_calcul_jour_semaine(self):
        """Test calcul du jour de la semaine."""
        # Lundi = 0, Dimanche = 6
        d = date(2025, 2, 3)  # Un lundi
        assert d.weekday() == 0
        
        d2 = date(2025, 2, 8)  # Un samedi
        assert d2.weekday() == 5

    def test_calcul_debut_semaine(self):
        """Test calcul du début de semaine."""
        d = date(2025, 2, 5)  # Mercredi
        debut_semaine = d - timedelta(days=d.weekday())
        
        assert debut_semaine == date(2025, 2, 3)  # Lundi
        assert debut_semaine.weekday() == 0

    def test_calcul_fin_semaine(self):
        """Test calcul de la fin de semaine."""
        d = date(2025, 2, 5)  # Mercredi
        debut_semaine = d - timedelta(days=d.weekday())
        fin_semaine = debut_semaine + timedelta(days=6)
        
        assert fin_semaine == date(2025, 2, 9)  # Dimanche
        assert fin_semaine.weekday() == 6


# ═══════════════════════════════════════════════════════════
# TESTS FORMATS ET VALIDATION
# ═══════════════════════════════════════════════════════════


class TestFormatsUI:
    """Tests pour les formats d'affichage UI."""
    
    def test_format_date_francais(self):
        """Test formatage de date en français."""
        d = date(2025, 2, 3)
        jours_fr = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
        
        jour_nom = jours_fr[d.weekday()]
        assert jour_nom == "Lundi"
        
        format_fr = f"{jour_nom} {d.day:02d}/{d.month:02d}"
        assert format_fr == "Lundi 03/02"

    def test_format_heure(self):
        """Test formatage d'heure."""
        from datetime import time
        
        t = time(14, 30)
        format_heure = f"{t.hour:02d}:{t.minute:02d}"
        assert format_heure == "14:30"

    def test_format_duree_minutes(self):
        """Test formatage de durée en minutes."""
        duree_minutes = 90
        heures = duree_minutes // 60
        minutes = duree_minutes % 60
        
        if heures > 0 and minutes > 0:
            format_duree = f"{heures}h{minutes:02d}"
        elif heures > 0:
            format_duree = f"{heures}h"
        else:
            format_duree = f"{minutes}min"
        
        assert format_duree == "1h30"

    def test_format_duree_heures_seules(self):
        """Test formatage durée heures seules."""
        duree_minutes = 120
        heures = duree_minutes // 60
        minutes = duree_minutes % 60
        
        if heures > 0 and minutes > 0:
            format_duree = f"{heures}h{minutes:02d}"
        elif heures > 0:
            format_duree = f"{heures}h"
        else:
            format_duree = f"{minutes}min"
        
        assert format_duree == "2h"

    def test_format_duree_minutes_seules(self):
        """Test formatage durée minutes seules."""
        duree_minutes = 45
        heures = duree_minutes // 60
        minutes = duree_minutes % 60
        
        if heures > 0 and minutes > 0:
            format_duree = f"{heures}h{minutes:02d}"
        elif heures > 0:
            format_duree = f"{heures}h"
        else:
            format_duree = f"{minutes}min"
        
        assert format_duree == "45min"


class TestValidationQuantites:
    """Tests pour la validation des quantités."""
    
    def test_quantite_valide_entier(self):
        """Quantité entière valide."""
        def valider_quantite(q):
            try:
                val = float(q)
                return val > 0
            except (ValueError, TypeError):
                return False
        
        assert valider_quantite(5) is True
        assert valider_quantite(0) is False
        assert valider_quantite(-1) is False

    def test_quantite_valide_float(self):
        """Quantité float valide."""
        def valider_quantite(q):
            try:
                val = float(q)
                return val > 0
            except (ValueError, TypeError):
                return False
        
        assert valider_quantite(2.5) is True
        assert valider_quantite(0.1) is True

    def test_quantite_invalide_string(self):
        """Quantité string invalide."""
        def valider_quantite(q):
            try:
                val = float(q)
                return val > 0
            except (ValueError, TypeError):
                return False
        
        assert valider_quantite("abc") is False
        assert valider_quantite("") is False
        assert valider_quantite(None) is False

    def test_quantite_string_numerique(self):
        """String numérique valide."""
        def valider_quantite(q):
            try:
                val = float(q)
                return val > 0
            except (ValueError, TypeError):
                return False
        
        assert valider_quantite("3") is True
        assert valider_quantite("2.5") is True
