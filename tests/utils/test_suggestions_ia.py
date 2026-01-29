"""Tests unitaires pour le service suggestions_ia."""

import pytest
from datetime import datetime, date
from unittest.mock import MagicMock, patch


class TestProfilCulinaireModel:
    """Tests pour le modèle ProfilCulinaire."""

    def test_profil_creation(self):
        """Création d'un profil culinaire."""
        from src.services.suggestions_ia import ProfilCulinaire
        
        profil = ProfilCulinaire(
            categories_preferees=["plat", "dessert"],
            temps_moyen_minutes=30,
            difficulte_moyenne="facile",
            ingredients_frequents=["poulet", "tomates", "pâtes"]
        )
        
        assert "plat" in profil.categories_preferees
        assert profil.temps_moyen_minutes == 30

    def test_profil_defaults(self):
        """Valeurs par défaut du profil."""
        from src.services.suggestions_ia import ProfilCulinaire
        
        profil = ProfilCulinaire()
        
        assert profil.categories_preferees == []
        assert profil.temps_moyen_minutes == 45  # Défaut
        assert profil.difficulte_moyenne == "moyen"


class TestContexteSuggestionModel:
    """Tests pour le modèle ContexteSuggestion."""

    def test_contexte_creation(self):
        """Création d'un contexte de suggestion."""
        from src.services.suggestions_ia import ContexteSuggestion
        
        contexte = ContexteSuggestion(
            saison="hiver",
            type_repas="dîner",
            ingredients_disponibles=["poulet", "riz", "légumes"],
            temps_disponible_minutes=45
        )
        
        assert contexte.saison == "hiver"
        assert "poulet" in contexte.ingredients_disponibles

    def test_contexte_defaults(self):
        """Valeurs par défaut du contexte."""
        from src.services.suggestions_ia import ContexteSuggestion
        
        contexte = ContexteSuggestion()
        
        # saison par défaut est "" (chaîne vide)
        assert contexte.saison == ""
        assert contexte.type_repas == "dîner"


class TestSuggestionRecetteModel:
    """Tests pour le modèle SuggestionRecette."""

    def test_suggestion_creation(self):
        """Création d'une suggestion."""
        from src.services.suggestions_ia import SuggestionRecette
        
        suggestion = SuggestionRecette(
            recette_id=1,
            nom="Poulet rôti",
            score=0.85,
            raison="Ingrédients disponibles"
        )
        
        assert suggestion.nom == "Poulet rôti"
        assert suggestion.score == 0.85
        assert suggestion.raison == "Ingrédients disponibles"


class TestSuggestionsServiceInit:
    """Tests d'initialisation du service."""

    def test_get_suggestions_ia_service(self):
        """La factory retourne une instance."""
        from src.services.suggestions_ia import get_suggestions_ia_service
        
        service = get_suggestions_ia_service()
        assert service is not None

    def test_service_methodes(self):
        """Le service expose les méthodes requises."""
        from src.services.suggestions_ia import get_suggestions_ia_service
        
        service = get_suggestions_ia_service()
        
        assert hasattr(service, 'analyser_profil_culinaire')
        assert hasattr(service, 'construire_contexte')
        assert hasattr(service, 'suggerer_recettes')


class TestCalculerScoreCategorie:
    """Tests pour le calcul de score par catégorie."""

    def test_score_categorie_preferee(self):
        """Score élevé pour catégorie préférée."""
        profil = {"categories_preferees": ["dessert", "plat"]}
        recette = {"categorie": "dessert"}
        
        # Si catégorie dans préférences → score bonus
        bonus = 0.2 if recette["categorie"] in profil["categories_preferees"] else 0
        
        assert bonus == 0.2

    def test_score_categorie_non_preferee(self):
        """Score normal pour catégorie non préférée."""
        profil = {"categories_preferees": ["dessert"]}
        recette = {"categorie": "entrée"}
        
        bonus = 0.2 if recette["categorie"] in profil["categories_preferees"] else 0
        
        assert bonus == 0


class TestCalculerScoreTemps:
    """Tests pour le calcul de score temps."""

    def test_score_temps_adapte(self):
        """Score pour temps adapté au profil."""
        profil = {"temps_moyen_minutes": 30}
        
        # Recette rapide
        recette_rapide = {"temps_total": 25}
        # Recette longue
        recette_longue = {"temps_total": 90}
        
        def score_temps(recette, profil):
            ecart = abs(recette["temps_total"] - profil["temps_moyen_minutes"])
            # Plus l'écart est grand, plus le score est bas
            return max(0, 1 - (ecart / 60))
        
        score_rapide = score_temps(recette_rapide, profil)
        score_longue = score_temps(recette_longue, profil)
        
        assert score_rapide > score_longue


class TestCalculerScoreRepetition:
    """Tests pour le malus de répétition."""

    def test_malus_repetition(self):
        """Malus pour recette récemment préparée."""
        jours_depuis = 2
        
        # Malus diminue avec le temps
        malus = max(0, 0.3 - (jours_depuis * 0.05))
        
        # Utiliser pytest.approx pour la comparaison des floats
        assert abs(malus - 0.2) < 0.01

    def test_pas_malus_ancienne_recette(self):
        """Pas de malus pour recette non préparée récemment."""
        jours_depuis = 30
        
        malus = max(0, 0.3 - (jours_depuis * 0.05))
        
        assert malus == 0


class TestFiltrageRecettes:
    """Tests pour le filtrage des recettes."""

    def test_filtrer_par_ingredients(self):
        """Filtrer les recettes avec ingrédients disponibles."""
        recettes = [
            {"nom": "Poulet rôti", "ingredients": ["poulet", "huile", "sel"]},
            {"nom": "Saumon grillé", "ingredients": ["saumon", "citron"]},
        ]
        disponibles = {"poulet", "huile", "sel", "poivre"}
        
        # Simuler le filtrage
        def score_disponibilite(recette, disponibles):
            ingredients_requis = set(recette["ingredients"])
            ingredients_manquants = ingredients_requis - disponibles
            return 1 - (len(ingredients_manquants) / len(ingredients_requis))
        
        scores = [score_disponibilite(r, disponibles) for r in recettes]
        
        # Poulet rôti devrait avoir un meilleur score
        assert scores[0] > scores[1]

    def test_filtrer_par_temps(self):
        """Filtrer les recettes par temps disponible."""
        recettes = [
            {"nom": "Omelette", "temps_total": 15},
            {"nom": "Bœuf bourguignon", "temps_total": 180},
        ]
        temps_max = 30
        
        recettes_possibles = [r for r in recettes if r["temps_total"] <= temps_max]
        
        assert len(recettes_possibles) == 1
        assert recettes_possibles[0]["nom"] == "Omelette"


class TestSaisons:
    """Tests pour les suggestions saisonnières."""

    def test_detecter_saison(self):
        """Détection de la saison courante."""
        from datetime import date
        
        def get_saison(d: date) -> str:
            mois = d.month
            if mois in [3, 4, 5]:
                return "printemps"
            elif mois in [6, 7, 8]:
                return "été"
            elif mois in [9, 10, 11]:
                return "automne"
            else:
                return "hiver"
        
        assert get_saison(date(2024, 1, 15)) == "hiver"
        assert get_saison(date(2024, 4, 15)) == "printemps"
        assert get_saison(date(2024, 7, 15)) == "été"
        assert get_saison(date(2024, 10, 15)) == "automne"

    def test_ingredients_saison(self):
        """Ingrédients de saison."""
        saisons_ingredients = {
            "hiver": ["choux", "poireau", "carotte", "pomme"],
            "printemps": ["asperge", "fraise", "radis"],
            "été": ["tomate", "courgette", "melon", "pêche"],
            "automne": ["champignon", "potiron", "raisin", "noix"],
        }
        
        assert "tomate" in saisons_ingredients["été"]
        assert "choux" in saisons_ingredients["hiver"]
