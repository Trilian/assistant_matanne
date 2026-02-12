"""
Tests pour planificateur_repas_logic.py - Fonctions pures du planificateur
"""

import pytest
from datetime import date, timedelta
from dataclasses import dataclass
from typing import Optional, List

from src.modules.cuisine.planificateur_repas.utils import (
    RecetteSuggestion,
    RepasPlannifie,
    PlanningSemaine,
    calculer_score_recette,
    filtrer_recettes_eligibles,
    JOURS_SEMAINE,
    TYPES_REPAS,
    PROTEINES,
    EQUILIBRE_DEFAUT,
    TEMPS_CATEGORIES,
    ROBOTS_CUISINE,
)
from src.modules.cuisine.schemas import PreferencesUtilisateur, FeedbackRecette


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# Tests Constantes
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestConstantes:
    """Tests des constantes du module."""

    def test_jours_semaine(self):
        """Vérifie les jours de la semaine."""
        assert len(JOURS_SEMAINE) == 7
        assert JOURS_SEMAINE[0] == "Lundi"
        assert JOURS_SEMAINE[6] == "Dimanche"

    def test_types_repas(self):
        """Vérifie les types de repas."""
        assert "déjeuner" in TYPES_REPAS
        assert "dîner" in TYPES_REPAS
        assert "goûter" in TYPES_REPAS

    def test_proteines_structure(self):
        """Vérifie la structure des protéines."""
        assert "poulet" in PROTEINES
        assert "poisson" in PROTEINES
        assert "tofu" in PROTEINES
        for prot, info in PROTEINES.items():
            assert "label" in info
            assert "emoji" in info
            assert "categorie" in info

    def test_equilibre_defaut(self):
        """Vérifie l'équilibre par défaut."""
        assert "poisson" in EQUILIBRE_DEFAUT
        assert "viande_rouge" in EQUILIBRE_DEFAUT
        assert "vegetarien" in EQUILIBRE_DEFAUT

    def test_temps_categories(self):
        """Vérifie les catégories de temps."""
        assert "express" in TEMPS_CATEGORIES
        assert "normal" in TEMPS_CATEGORIES
        assert "long" in TEMPS_CATEGORIES
        for cat, info in TEMPS_CATEGORIES.items():
            assert "max_minutes" in info
            assert "label" in info


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# Tests RecetteSuggestion Dataclass
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestRecetteSuggestion:
    """Tests pour la dataclass RecetteSuggestion."""

    def test_creation_basique(self):
        """Crée une suggestion basique."""
        suggestion = RecetteSuggestion(
            id=1,
            nom="Poulet rôti",
            description="Poulet rôti aux herbes",
            temps_preparation=15,
            temps_cuisson=60,
            portions=4,
            difficulte="facile"
        )
        assert suggestion.nom == "Poulet rôti"
        assert suggestion.temps_preparation == 15

    def test_temps_total(self):
        """Vérifie le calcul du temps total."""
        suggestion = RecetteSuggestion(
            id=1,
            nom="Test",
            description="Test",
            temps_preparation=20,
            temps_cuisson=30,
            portions=4,
            difficulte="facile"
        )
        assert suggestion.temps_total == 50

    def test_emoji_difficulte(self):
        """Vérifie les emojis de difficulté."""
        facile = RecetteSuggestion(
            id=1, nom="T", description="T",
            temps_preparation=10, temps_cuisson=10,
            portions=2, difficulte="facile"
        )
        assert facile.emoji_difficulte == "ðŸŸ¢"

        moyen = RecetteSuggestion(
            id=2, nom="T", description="T",
            temps_preparation=10, temps_cuisson=10,
            portions=2, difficulte="moyen"
        )
        assert moyen.emoji_difficulte == "ðŸŸ¡"

        difficile = RecetteSuggestion(
            id=3, nom="T", description="T",
            temps_preparation=10, temps_cuisson=10,
            portions=2, difficulte="difficile"
        )
        assert difficile.emoji_difficulte == "ðŸ”´"

    def test_valeurs_defaut(self):
        """Vérifie les valeurs par défaut."""
        suggestion = RecetteSuggestion(
            id=1, nom="Test", description="Test",
            temps_preparation=10, temps_cuisson=10,
            portions=2, difficulte="facile"
        )
        assert suggestion.compatible_batch is False
        assert suggestion.compatible_jules is True
        assert suggestion.est_vegetarien is False
        assert suggestion.score_match == 0.0
        assert suggestion.ingredients_en_stock == []
        assert suggestion.ingredients_manquants == []


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# Tests RepasPlannifie Dataclass
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestRepasPlannifie:
    """Tests pour la dataclass RepasPlannifie."""

    def test_creation_vide(self):
        """Crée un repas vide."""
        repas = RepasPlannifie(
            jour=date.today(),
            type_repas="déjeuner"
        )
        assert repas.est_vide is True
        assert repas.recette is None

    def test_creation_avec_recette(self):
        """Crée un repas avec recette."""
        suggestion = RecetteSuggestion(
            id=1, nom="Test", description="Test",
            temps_preparation=10, temps_cuisson=10,
            portions=2, difficulte="facile"
        )
        repas = RepasPlannifie(
            jour=date.today(),
            type_repas="dîner",
            recette=suggestion
        )
        assert repas.est_vide is False
        assert repas.recette.nom == "Test"

    def test_jour_nom(self):
        """Vérifie le nom du jour."""
        # Lundi
        lundi = date(2024, 1, 1)  # Un lundi
        repas = RepasPlannifie(jour=lundi, type_repas="déjeuner")
        assert repas.jour_nom == "Lundi"


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# Tests PlanningSemaine Dataclass
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestPlanningSemaine:
    """Tests pour la dataclass PlanningSemaine."""

    def test_creation_vide(self):
        """Crée un planning vide."""
        planning = PlanningSemaine(
            date_debut=date.today(),
            date_fin=date.today() + timedelta(days=6)
        )
        assert planning.nb_repas_planifies == 0
        assert planning.nb_repas_total == 0

    def test_nb_repas_planifies(self):
        """Compte les repas planifiés."""
        suggestion = RecetteSuggestion(
            id=1, nom="Test", description="Test",
            temps_preparation=10, temps_cuisson=10,
            portions=2, difficulte="facile"
        )
        planning = PlanningSemaine(
            date_debut=date.today(),
            date_fin=date.today() + timedelta(days=6),
            repas=[
                RepasPlannifie(jour=date.today(), type_repas="déjeuner", recette=suggestion),
                RepasPlannifie(jour=date.today(), type_repas="dîner"),  # Vide
            ]
        )
        assert planning.nb_repas_total == 2
        assert planning.nb_repas_planifies == 1

    def test_get_repas_jour(self):
        """Récupère les repas d'un jour."""
        aujourd_hui = date.today()
        demain = date.today() + timedelta(days=1)
        planning = PlanningSemaine(
            date_debut=aujourd_hui,
            date_fin=demain,
            repas=[
                RepasPlannifie(jour=aujourd_hui, type_repas="déjeuner"),
                RepasPlannifie(jour=aujourd_hui, type_repas="dîner"),
                RepasPlannifie(jour=demain, type_repas="déjeuner"),
            ]
        )
        repas_aujourdhui = planning.get_repas_jour(aujourd_hui)
        assert len(repas_aujourdhui) == 2

    def test_get_equilibre(self):
        """Calcule l'équilibre des protéines."""
        planning = PlanningSemaine(
            date_debut=date.today(),
            date_fin=date.today() + timedelta(days=6),
            repas=[
                RepasPlannifie(
                    jour=date.today(),
                    type_repas="déjeuner",
                    recette=RecetteSuggestion(
                        id=1, nom="Poisson", description="Test",
                        temps_preparation=10, temps_cuisson=10,
                        portions=2, difficulte="facile",
                        categorie_proteine="poisson"
                    )
                ),
            ]
        )
        equilibre = planning.get_equilibre()
        assert equilibre["poisson"] == 1


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# Tests Calcul Score Recette
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestCalculerScoreRecette:
    """Tests pour calculer_score_recette."""

    @pytest.fixture
    def preferences_defaut(self):
        """Préférences par défaut pour les tests."""
        return PreferencesUtilisateur()

    @pytest.fixture
    def recette_simple(self):
        """Recette simple pour les tests."""
        @dataclass
        class RecetteSimple:
            id: int = 1
            nom: str = "Poulet grillé"
            type_proteine: str = "poulet"
            temps_preparation: int = 15
            temps_cuisson: int = 30
            compatible_bebe: bool = True
            compatible_batch: bool = False
            ingredients: list = None
        return RecetteSimple()

    def test_score_base(self, preferences_defaut, recette_simple):
        """Le score de base est 50."""
        score, raison = calculer_score_recette(
            recette=recette_simple,
            preferences=preferences_defaut,
            feedbacks=[],
            equilibre_actuel={},
            stock_disponible=[]
        )
        assert 40 <= score <= 60  # Autour du score de base

    def test_exclusion_aliment(self, recette_simple):
        """Une exclusion donne un score de 0."""
        prefs = PreferencesUtilisateur(aliments_exclus=["poulet"])
        score, raison = calculer_score_recette(
            recette=recette_simple,
            preferences=prefs,
            feedbacks=[],
            equilibre_actuel={},
            stock_disponible=[]
        )
        assert score == 0.0
        assert "exclu" in raison.lower()

    def test_bonus_favori(self, recette_simple):
        """Un favori augmente le score."""
        prefs_sans = PreferencesUtilisateur()
        prefs_avec = PreferencesUtilisateur(aliments_favoris=["poulet"])
        
        score_sans, _ = calculer_score_recette(
            recette=recette_simple,
            preferences=prefs_sans,
            feedbacks=[],
            equilibre_actuel={},
            stock_disponible=[]
        )
        score_avec, _ = calculer_score_recette(
            recette=recette_simple,
            preferences=prefs_avec,
            feedbacks=[],
            equilibre_actuel={},
            stock_disponible=[]
        )
        assert score_avec > score_sans

    def test_feedback_positif(self, preferences_defaut, recette_simple):
        """Un feedback positif augmente le score."""
        feedback_like = FeedbackRecette(recette_id=1, recette_nom="Poulet grillé", feedback="like")
        
        score_sans, _ = calculer_score_recette(
            recette=recette_simple,
            preferences=preferences_defaut,
            feedbacks=[],
            equilibre_actuel={},
            stock_disponible=[]
        )
        score_avec, raison = calculer_score_recette(
            recette=recette_simple,
            preferences=preferences_defaut,
            feedbacks=[feedback_like],
            equilibre_actuel={},
            stock_disponible=[]
        )
        assert score_avec > score_sans

    def test_feedback_negatif(self, preferences_defaut, recette_simple):
        """Un feedback négatif diminue le score."""
        feedback_dislike = FeedbackRecette(recette_id=1, recette_nom="Poulet grillé", feedback="dislike")
        
        score_sans, _ = calculer_score_recette(
            recette=recette_simple,
            preferences=preferences_defaut,
            feedbacks=[],
            equilibre_actuel={},
            stock_disponible=[]
        )
        score_avec, raison = calculer_score_recette(
            recette=recette_simple,
            preferences=preferences_defaut,
            feedbacks=[feedback_dislike],
            equilibre_actuel={},
            stock_disponible=[]
        )
        assert score_avec < score_sans

    def test_recette_dict(self, preferences_defaut):
        """Fonctionne avec un dict au lieu d'un objet."""
        recette_dict = {
            "id": 1,
            "nom": "Salade légumes",
        }
        score, raison = calculer_score_recette(
            recette=recette_dict,
            preferences=preferences_defaut,
            feedbacks=[],
            equilibre_actuel={},
            stock_disponible=[]
        )
        assert 0 <= score <= 100


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# Tests Filtrer Recettes Ã‰ligibles
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestFiltrerRecettesEligibles:
    """Tests pour filtrer_recettes_eligibles."""

    def test_filtre_exclusions(self):
        """Exclut les recettes avec aliments exclus."""
        @dataclass
        class Recette:
            nom: str
        
        recettes = [
            Recette(nom="Poulet rôti"),
            Recette(nom="Salade verte"),
            Recette(nom="Poulet grillé"),
        ]
        prefs = PreferencesUtilisateur(aliments_exclus=["poulet"])
        
        eligibles = filtrer_recettes_eligibles(recettes, prefs)
        assert len(eligibles) == 1
        assert eligibles[0].nom == "Salade verte"

    def test_pas_exclusion(self):
        """Retourne toutes si pas d'exclusion."""
        @dataclass
        class Recette:
            nom: str
        
        recettes = [
            Recette(nom="Poulet rôti"),
            Recette(nom="Salade verte"),
        ]
        prefs = PreferencesUtilisateur()
        
        eligibles = filtrer_recettes_eligibles(recettes, prefs)
        assert len(eligibles) == 2

    def test_liste_vide(self):
        """Retourne liste vide si entrée vide."""
        prefs = PreferencesUtilisateur()
        eligibles = filtrer_recettes_eligibles([], prefs)
        assert len(eligibles) == 0

    def test_toutes_exclues(self):
        """Retourne vide si toutes exclues."""
        @dataclass
        class Recette:
            nom: str
        
        recettes = [
            Recette(nom="Poulet rôti"),
            Recette(nom="Poulet grillé"),
        ]
        prefs = PreferencesUtilisateur(aliments_exclus=["poulet"])
        
        eligibles = filtrer_recettes_eligibles(recettes, prefs)
        assert len(eligibles) == 0

    def test_filtre_type_repas(self):
        """Filtre par type de repas si spécifié."""
        @dataclass
        class Recette:
            nom: str
            type_repas: Optional[str] = None
        
        recettes = [
            Recette(nom="Croissant", type_repas="petit_déjeuner"),
            Recette(nom="Steak", type_repas="déjeuner,dîner"),
            Recette(nom="Salade", type_repas=None),  # Pas de type spécifié
        ]
        prefs = PreferencesUtilisateur()
        
        eligibles = filtrer_recettes_eligibles(recettes, prefs, type_repas="déjeuner")
        # Le croissant ne devrait pas être dans la liste pour le déjeuner
        noms = [r.nom for r in eligibles]
        assert "Croissant" not in noms
        assert "Steak" in noms
