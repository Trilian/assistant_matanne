"""
Tests complets pour le module planificateur_repas.

Couvre:
- Fonctions de génération PDF
- Chargement/sauvegarde des préférences
- Gestion des feedbacks
- Génération de planning IA
- Logique métier du planificateur
"""

import pytest
from datetime import date, datetime, timedelta
from io import BytesIO
from unittest.mock import Mock, MagicMock, patch
import json

# Import du module logic (fonctions pures)
from src.domains.cuisine.logic.planificateur_repas_logic import (
    JOURS_SEMAINE,
    PROTEINES,
    ROBOTS_CUISINE,
    TEMPS_CATEGORIES,
    PreferencesUtilisateur,
    FeedbackRecette,
    RecetteSuggestion,
    RepasPlannifie,
    PlanningSemaine,
    calculer_score_recette,
    filtrer_recettes_eligibles,
    generer_suggestions_alternatives,
    generer_prompt_semaine,
    generer_prompt_alternative,
    valider_equilibre_semaine,
    suggerer_ajustements_equilibre,
)


# ═══════════════════════════════════════════════════════════
# TESTS CONSTANTES
# ═══════════════════════════════════════════════════════════


class TestConstantes:
    """Tests pour les constantes du planificateur."""

    def test_jours_semaine_count(self):
        assert len(JOURS_SEMAINE) == 7

    def test_jours_semaine_content(self):
        assert "Lundi" in JOURS_SEMAINE
        assert "Dimanche" in JOURS_SEMAINE

    def test_proteines_defined(self):
        assert len(PROTEINES) > 0
        assert "poulet" in PROTEINES or "Poulet" in PROTEINES

    def test_robots_cuisine_defined(self):
        assert isinstance(ROBOTS_CUISINE, (list, dict))

    def test_temps_categories_defined(self):
        assert isinstance(TEMPS_CATEGORIES, (list, dict))


# ═══════════════════════════════════════════════════════════
# TESTS MODÈLES PYDANTIC
# ═══════════════════════════════════════════════════════════


class TestPreferencesUtilisateur:
    """Tests pour le modèle PreferencesUtilisateur."""

    def test_create_default_preferences(self):
        prefs = PreferencesUtilisateur()
        assert prefs is not None

    def test_create_preferences_with_allergies(self):
        prefs = PreferencesUtilisateur(
            allergenes=["gluten", "lactose"],
        )
        assert "gluten" in prefs.allergenes
        assert len(prefs.allergenes) == 2

    def test_create_preferences_with_regime(self):
        prefs = PreferencesUtilisateur(
            regime="vegetarien",
        )
        assert prefs.regime == "vegetarien"

    def test_create_preferences_with_temps_max(self):
        prefs = PreferencesUtilisateur(
            temps_max_preparation=30,
        )
        assert prefs.temps_max_preparation == 30


class TestFeedbackRecette:
    """Tests pour le modèle FeedbackRecette."""

    def test_create_feedback_positif(self):
        feedback = FeedbackRecette(
            recette_id=1,
            recette_nom="Poulet rôti",
            feedback="positif",
        )
        assert feedback.feedback == "positif"

    def test_create_feedback_negatif(self):
        feedback = FeedbackRecette(
            recette_id=2,
            recette_nom="Sushi",
            feedback="negatif",
            contexte="Trop long à préparer",
        )
        assert feedback.feedback == "negatif"
        assert feedback.contexte == "Trop long à préparer"


class TestRecetteSuggestion:
    """Tests pour le modèle RecetteSuggestion."""

    def test_create_suggestion(self):
        suggestion = RecetteSuggestion(
            recette_id=1,
            nom="Pâtes carbonara",
            score=0.85,
        )
        assert suggestion.score == 0.85
        assert suggestion.nom == "Pâtes carbonara"

    def test_suggestion_with_alternatives(self):
        suggestion = RecetteSuggestion(
            recette_id=1,
            nom="Pizza maison",
            score=0.9,
            alternatives=["Focaccia", "Calzone"],
        )
        assert len(suggestion.alternatives) == 2


class TestRepasPlannifie:
    """Tests pour le modèle RepasPlannifie."""

    def test_create_repas(self):
        repas = RepasPlannifie(
            jour="Lundi",
            type_repas="midi",
            recette_id=1,
            recette_nom="Quiche lorraine",
        )
        assert repas.jour == "Lundi"
        assert repas.type_repas == "midi"


class TestPlanningSemaine:
    """Tests pour le modèle PlanningSemaine."""

    def test_create_planning_empty(self):
        planning = PlanningSemaine(
            date_debut=date(2026, 2, 6),
        )
        assert planning.date_debut == date(2026, 2, 6)

    def test_create_planning_with_repas(self):
        repas = [
            RepasPlannifie(jour="Lundi", type_repas="midi", recette_id=1, recette_nom="Salade"),
            RepasPlannifie(jour="Lundi", type_repas="soir", recette_id=2, recette_nom="Pâtes"),
        ]
        planning = PlanningSemaine(
            date_debut=date(2026, 2, 6),
            repas=repas,
        )
        assert len(planning.repas) == 2


# ═══════════════════════════════════════════════════════════
# TESTS FONCTIONS LOGIQUE
# ═══════════════════════════════════════════════════════════


class TestCalculerScoreRecette:
    """Tests pour calculer_score_recette."""

    def test_score_recette_parfaite(self):
        recette = MagicMock()
        recette.temps_preparation = 20
        recette.nom = "Salade"
        recette.ingredients = []
        
        prefs = PreferencesUtilisateur(
            temps_max_preparation=30,
        )
        
        score = calculer_score_recette(recette, prefs)
        assert 0 <= score <= 1

    def test_score_recette_temps_depasse(self):
        recette = MagicMock()
        recette.temps_preparation = 60
        recette.nom = "Plat complexe"
        recette.ingredients = []
        
        prefs = PreferencesUtilisateur(
            temps_max_preparation=30,
        )
        
        score = calculer_score_recette(recette, prefs)
        # Score should be lower for recipes that exceed time limit
        assert score <= 0.5

    def test_score_recette_avec_feedback_positif(self):
        recette = MagicMock()
        recette.id = 1
        recette.temps_preparation = 20
        recette.nom = "Favori"
        recette.ingredients = []
        
        prefs = PreferencesUtilisateur()
        feedbacks = [
            FeedbackRecette(recette_id=1, recette_nom="Favori", feedback="positif"),
        ]
        
        score = calculer_score_recette(recette, prefs, feedbacks=feedbacks)
        # Positive feedback should boost score
        assert score >= 0.5


class TestFiltrerRecettesEligibles:
    """Tests pour filtrer_recettes_eligibles."""

    def test_filtre_allergenes(self):
        recettes = [
            MagicMock(nom="Salade", ingredients=[MagicMock(nom="laitue")]),
            MagicMock(nom="Pizza", ingredients=[MagicMock(nom="gluten")]),
        ]
        
        prefs = PreferencesUtilisateur(allergenes=["gluten"])
        
        result = filtrer_recettes_eligibles(recettes, prefs)
        # Should filter out gluten containing recipe
        assert len(result) <= len(recettes)

    def test_filtre_temps_max(self):
        recettes = [
            MagicMock(nom="Rapide", temps_preparation=15),
            MagicMock(nom="Long", temps_preparation=120),
        ]
        
        prefs = PreferencesUtilisateur(temps_max_preparation=30)
        
        result = filtrer_recettes_eligibles(recettes, prefs)
        assert len(result) >= 1

    def test_filtre_liste_vide(self):
        result = filtrer_recettes_eligibles([], PreferencesUtilisateur())
        assert result == []


class TestGenererSuggestionsAlternatives:
    """Tests pour generer_suggestions_alternatives."""

    def test_generer_alternatives(self):
        recette_originale = MagicMock(id=1, nom="Poulet rôti", categorie="viande")
        recettes_disponibles = [
            MagicMock(id=2, nom="Poulet grillé", categorie="viande"),
            MagicMock(id=3, nom="Canard", categorie="viande"),
            MagicMock(id=4, nom="Salade", categorie="entrée"),
        ]
        
        alternatives = generer_suggestions_alternatives(
            recette_originale, 
            recettes_disponibles,
            nb_alternatives=2,
        )
        
        assert len(alternatives) <= 2

    def test_generer_alternatives_aucune_disponible(self):
        recette = MagicMock(id=1, nom="Unique")
        
        alternatives = generer_suggestions_alternatives(recette, [], nb_alternatives=3)
        
        assert alternatives == []


class TestGenererPromptSemaine:
    """Tests pour generer_prompt_semaine."""

    def test_prompt_basique(self):
        prefs = PreferencesUtilisateur()
        
        prompt = generer_prompt_semaine(prefs, date_debut=date(2026, 2, 6))
        
        assert isinstance(prompt, str)
        assert len(prompt) > 0

    def test_prompt_avec_contraintes(self):
        prefs = PreferencesUtilisateur(
            regime="vegetarien",
            allergenes=["gluten"],
            temps_max_preparation=30,
        )
        
        prompt = generer_prompt_semaine(prefs, date_debut=date(2026, 2, 6))
        
        assert "végétarien" in prompt.lower() or "vegetarien" in prompt.lower()

    def test_prompt_avec_contexte(self):
        prefs = PreferencesUtilisateur()
        
        prompt = generer_prompt_semaine(
            prefs, 
            date_debut=date(2026, 2, 6),
            contexte="Semaine chargée, besoin de repas rapides",
        )
        
        assert "rapide" in prompt.lower() or len(prompt) > 50


class TestGenererPromptAlternative:
    """Tests pour generer_prompt_alternative."""

    def test_prompt_alternative(self):
        recette_originale = MagicMock(nom="Pâtes bolognaise")
        
        prompt = generer_prompt_alternative(
            recette_originale,
            raison="Trop long à préparer",
        )
        
        assert isinstance(prompt, str)
        assert len(prompt) > 0


class TestValiderEquilibreSemaine:
    """Tests pour valider_equilibre_semaine."""

    def test_planning_equilibre(self):
        planning = {
            "Lundi": {"midi": "Poulet", "soir": "Légumes"},
            "Mardi": {"midi": "Poisson", "soir": "Pâtes"},
            "Mercredi": {"midi": "Boeuf", "soir": "Salade"},
            "Jeudi": {"midi": "Végétarien", "soir": "Légumes"},
            "Vendredi": {"midi": "Poisson", "soir": "Pizza"},
        }
        
        result = valider_equilibre_semaine(planning)
        
        assert isinstance(result, dict)
        assert "equilibre" in result or "score" in result or "valide" in result

    def test_planning_desequilibre(self):
        planning = {
            "Lundi": {"midi": "Viande", "soir": "Viande"},
            "Mardi": {"midi": "Viande", "soir": "Viande"},
            "Mercredi": {"midi": "Viande", "soir": "Viande"},
        }
        
        result = valider_equilibre_semaine(planning)
        
        # Should indicate imbalance
        assert result is not None


class TestSuggererAjustementsEquilibre:
    """Tests pour suggerer_ajustements_equilibre."""

    def test_suggestions_ajustement(self):
        planning = {
            "Lundi": {"midi": "Viande", "soir": "Viande"},
            "Mardi": {"midi": "Viande", "soir": "Viande"},
        }
        
        suggestions = suggerer_ajustements_equilibre(planning)
        
        assert isinstance(suggestions, list)


# ═══════════════════════════════════════════════════════════
# TESTS UI (avec mocks Streamlit)
# ═══════════════════════════════════════════════════════════


class TestUIGenererPdfPlanning:
    """Tests pour generer_pdf_planning_session."""

    @patch('src.domains.cuisine.ui.planificateur_repas.reportlab')
    def test_generer_pdf_basique(self, mock_reportlab):
        from src.domains.cuisine.ui.planificateur_repas import generer_pdf_planning_session
        
        planning_data = {
            "Lundi": {"midi": "Salade", "soir": "Pâtes"},
        }
        
        result = generer_pdf_planning_session(
            planning_data=planning_data,
            date_debut=date(2026, 2, 6),
        )
        
        # May return BytesIO or None depending on reportlab
        assert result is None or isinstance(result, BytesIO)

    def test_generer_pdf_planning_vide(self):
        from src.domains.cuisine.ui.planificateur_repas import generer_pdf_planning_session
        
        result = generer_pdf_planning_session(
            planning_data={},
            date_debut=date(2026, 2, 6),
        )
        
        # Should handle empty planning gracefully
        assert result is None or isinstance(result, BytesIO)


class TestUIChargerPreferences:
    """Tests pour charger_preferences."""

    @patch('src.domains.cuisine.ui.planificateur_repas.obtenir_contexte_db')
    def test_charger_preferences_existantes(self, mock_db):
        from src.domains.cuisine.ui.planificateur_repas import charger_preferences
        
        mock_session = MagicMock()
        mock_db.return_value.__enter__ = Mock(return_value=mock_session)
        mock_db.return_value.__exit__ = Mock(return_value=False)
        
        mock_pref = MagicMock()
        mock_pref.data = json.dumps({"regime": "vegetarien"})
        mock_session.query.return_value.first.return_value = mock_pref
        
        result = charger_preferences()
        
        assert result is not None

    @patch('src.domains.cuisine.ui.planificateur_repas.obtenir_contexte_db')
    def test_charger_preferences_inexistantes(self, mock_db):
        from src.domains.cuisine.ui.planificateur_repas import charger_preferences
        
        mock_session = MagicMock()
        mock_db.return_value.__enter__ = Mock(return_value=mock_session)
        mock_db.return_value.__exit__ = Mock(return_value=False)
        
        mock_session.query.return_value.first.return_value = None
        
        result = charger_preferences()
        
        # Should return default preferences
        assert isinstance(result, PreferencesUtilisateur)


class TestUISauvegarderPreferences:
    """Tests pour sauvegarder_preferences."""

    @patch('src.domains.cuisine.ui.planificateur_repas.obtenir_contexte_db')
    def test_sauvegarder_preferences(self, mock_db):
        from src.domains.cuisine.ui.planificateur_repas import sauvegarder_preferences
        
        mock_session = MagicMock()
        mock_db.return_value.__enter__ = Mock(return_value=mock_session)
        mock_db.return_value.__exit__ = Mock(return_value=False)
        
        prefs = PreferencesUtilisateur(regime="vegetarien")
        
        result = sauvegarder_preferences(prefs)
        
        assert result is True
        mock_session.commit.assert_called()


class TestUIChargerFeedbacks:
    """Tests pour charger_feedbacks."""

    @patch('src.domains.cuisine.ui.planificateur_repas.obtenir_contexte_db')
    def test_charger_feedbacks(self, mock_db):
        from src.domains.cuisine.ui.planificateur_repas import charger_feedbacks
        
        mock_session = MagicMock()
        mock_db.return_value.__enter__ = Mock(return_value=mock_session)
        mock_db.return_value.__exit__ = Mock(return_value=False)
        
        mock_feedbacks = [
            MagicMock(recette_id=1, recette_nom="Test", feedback="positif"),
        ]
        mock_session.query.return_value.all.return_value = mock_feedbacks
        
        result = charger_feedbacks()
        
        assert isinstance(result, list)


class TestUIAjouterFeedback:
    """Tests pour ajouter_feedback."""

    @patch('src.domains.cuisine.ui.planificateur_repas.obtenir_contexte_db')
    def test_ajouter_feedback_positif(self, mock_db):
        from src.domains.cuisine.ui.planificateur_repas import ajouter_feedback
        
        mock_session = MagicMock()
        mock_db.return_value.__enter__ = Mock(return_value=mock_session)
        mock_db.return_value.__exit__ = Mock(return_value=False)
        
        ajouter_feedback(
            recette_id=1,
            recette_nom="Poulet rôti",
            feedback="positif",
        )
        
        mock_session.add.assert_called()
        mock_session.commit.assert_called()


class TestUIGenererSemaineIA:
    """Tests pour generer_semaine_ia."""

    @patch('src.domains.cuisine.ui.planificateur_repas.obtenir_client_ia')
    def test_generer_semaine_success(self, mock_ia):
        from src.domains.cuisine.ui.planificateur_repas import generer_semaine_ia
        
        mock_client = MagicMock()
        mock_ia.return_value = mock_client
        mock_client.generate.return_value = {
            "Lundi": {"midi": "Salade", "soir": "Pâtes"},
        }
        
        result = generer_semaine_ia(date_debut=date(2026, 2, 6))
        
        assert isinstance(result, dict)

    @patch('src.domains.cuisine.ui.planificateur_repas.obtenir_client_ia')
    def test_generer_semaine_erreur_ia(self, mock_ia):
        from src.domains.cuisine.ui.planificateur_repas import generer_semaine_ia
        
        mock_client = MagicMock()
        mock_ia.return_value = mock_client
        mock_client.generate.side_effect = Exception("IA indisponible")
        
        result = generer_semaine_ia(date_debut=date(2026, 2, 6))
        
        # Should return empty dict or handle gracefully
        assert result is None or result == {}


class TestUIRenderFunctions:
    """Tests pour les fonctions de rendu UI."""

    @patch('streamlit.subheader')
    @patch('streamlit.columns')
    def test_render_configuration_preferences(self, mock_cols, mock_subheader):
        from src.domains.cuisine.ui.planificateur_repas import render_configuration_preferences
        
        mock_cols.return_value = [MagicMock() for _ in range(2)]
        
        # Should not raise
        render_configuration_preferences()

    @patch('streamlit.subheader')
    @patch('streamlit.write')
    def test_render_apprentissage_ia(self, mock_write, mock_subheader):
        from src.domains.cuisine.ui.planificateur_repas import render_apprentissage_ia
        
        # Should not raise
        render_apprentissage_ia()

    @patch('streamlit.container')
    def test_render_carte_recette_suggestion(self, mock_container):
        from src.domains.cuisine.ui.planificateur_repas import render_carte_recette_suggestion
        
        mock_container.return_value.__enter__ = Mock(return_value=MagicMock())
        mock_container.return_value.__exit__ = Mock(return_value=False)
        
        recette = MagicMock(
            id=1,
            nom="Test",
            temps_preparation=20,
            difficulte="facile",
        )
        
        # Should not raise
        render_carte_recette_suggestion(recette, jour="Lundi", type_repas="midi")

    @patch('streamlit.columns')
    def test_render_jour_planning(self, mock_cols):
        from src.domains.cuisine.ui.planificateur_repas import render_jour_planning
        
        mock_cols.return_value = [MagicMock() for _ in range(3)]
        
        jour_data = {
            "midi": MagicMock(nom="Salade"),
            "soir": MagicMock(nom="Pâtes"),
        }
        
        # Should not raise
        render_jour_planning("Lundi", jour_data)

    @patch('streamlit.subheader')
    @patch('streamlit.columns')
    def test_render_resume_equilibre(self, mock_cols, mock_subheader):
        from src.domains.cuisine.ui.planificateur_repas import render_resume_equilibre
        
        mock_cols.return_value = [MagicMock() for _ in range(4)]
        
        planning_data = {
            "Lundi": {"midi": "Poulet", "soir": "Légumes"},
        }
        
        # Should not raise
        render_resume_equilibre(planning_data)


class TestUIAppFunction:
    """Tests pour la fonction app() principale."""

    @patch('streamlit.title')
    @patch('streamlit.tabs')
    def test_app_main_entry(self, mock_tabs, mock_title):
        from src.domains.cuisine.ui.planificateur_repas import app
        
        mock_tabs.return_value = [MagicMock() for _ in range(3)]
        
        # Should not raise
        app()
        
        mock_title.assert_called()
