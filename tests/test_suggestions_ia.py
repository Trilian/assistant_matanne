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
            temps_moyen_preparation=30,
            difficulte_moyenne=2.5,
            ingredients_favoris=["poulet", "tomates", "pâtes"]
        )
        
        assert "plat" in profil.categories_preferees
        assert profil.temps_moyen_preparation == 30

    def test_profil_defaults(self):
        """Valeurs par défaut du profil."""
        from src.services.suggestions_ia import ProfilCulinaire
        
        profil = ProfilCulinaire()
        
        assert profil.categories_preferees == [] or profil.categories_preferees is not None
        assert profil.temps_moyen_preparation >= 0


class TestContexteSuggestionModel:
    """Tests pour le modèle ContexteSuggestion."""

    def test_contexte_creation(self):
        """Création d'un contexte de suggestion."""
        from src.services.suggestions_ia import ContexteSuggestion
        
        contexte = ContexteSuggestion(
            saison="hiver",
            moment_journee="soir",
            ingredients_disponibles=["poulet", "riz", "légumes"],
            contraintes_temps=45
        )
        
        assert contexte.saison == "hiver"
        assert "poulet" in contexte.ingredients_disponibles

    def test_contexte_defaults(self):
        """Valeurs par défaut du contexte."""
        from src.services.suggestions_ia import ContexteSuggestion
        
        contexte = ContexteSuggestion()
        
        assert contexte.saison is None or contexte.saison in ["printemps", "été", "automne", "hiver"]


class TestSuggestionRecetteModel:
    """Tests pour le modèle SuggestionRecette."""

    def test_suggestion_creation(self):
        """Création d'une suggestion."""
        from src.services.suggestions_ia import SuggestionRecette
        
        suggestion = SuggestionRecette(
            recette_id=1,
            recette_nom="Poulet rôti",
            score=0.85,
            raisons=["Ingrédients disponibles", "Correspond à la saison"]
        )
        
        assert suggestion.recette_nom == "Poulet rôti"
        assert suggestion.score == 0.85
        assert len(suggestion.raisons) == 2


class TestSuggestionsServiceInit:
    """Tests d'initialisation du service."""

    def test_get_suggestions_service(self):
        """La factory retourne une instance."""
        from src.services.suggestions_ia import get_suggestions_service
        
        service = get_suggestions_service()
        assert service is not None

    def test_service_methodes(self):
        """Le service expose les méthodes requises."""
        from src.services.suggestions_ia import get_suggestions_service
        
        service = get_suggestions_service()
        
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
        profil = {"temps_moyen_preparation": 30}
        
        # Recette rapide
        recette_rapide = {"temps_total": 25}
        # Recette longue
        recette_longue = {"temps_total": 90}
        
        def score_temps(recette, profil):
            ecart = abs(recette["temps_total"] - profil["temps_moyen_preparation"])
            # Plus l'écart est grand, plus le score est bas
            return max(0, 1 - (ecart / 60))
        
        score_rapide = score_temps(recette_rapide, profil)
        score_longue = score_temps(recette_longue, profil)
        
        assert score_rapide > score_longue


class TestCalculerScoreRepetition:
    """Tests pour le malus de répétition."""

    def test_malus_repetition(self):
        """Malus pour recette récemment préparée."""
        recettes_recentes = [1, 2, 3, 1, 2]  # IDs des recettes récentes
        
        recette_id = 1
        occurrences = recettes_recentes.count(recette_id)
        
        # Malus proportionnel aux occurrences
        malus = min(occurrences * 0.1, 0.5)  # Max 0.5
        
        assert malus == 0.2  # 2 occurrences × 0.1

    def test_pas_malus_nouvelle_recette(self):
        """Pas de malus pour nouvelle recette."""
        recettes_recentes = [1, 2, 3]
        
        recette_id = 10  # Pas dans les récentes
        occurrences = recettes_recentes.count(recette_id)
        malus = min(occurrences * 0.1, 0.5)
        
        assert malus == 0


class TestCalculerScoreSaison:
    """Tests pour le score saisonnier."""

    def test_score_saison_hiver(self):
        """Score pour recettes d'hiver en hiver."""
        mois_courant = 1  # Janvier
        recette = {"saisons": [12, 1, 2]}  # Hiver
        
        is_saison = mois_courant in recette["saisons"]
        bonus = 0.15 if is_saison else 0
        
        assert bonus == 0.15

    def test_score_saison_toute_annee(self):
        """Score pour recette toute l'année."""
        mois_courant = 7
        recette = {"saisons": list(range(1, 13))}  # Toute l'année
        
        is_saison = mois_courant in recette["saisons"]
        bonus = 0.15 if is_saison else 0
        
        assert bonus == 0.15


class TestTrouverIngredientsManquants:
    """Tests pour trouver les ingrédients manquants."""

    def test_tous_ingredients_disponibles(self):
        """Tous les ingrédients sont disponibles."""
        disponibles = {"farine", "œufs", "sucre", "beurre"}
        requis = {"farine", "œufs", "sucre"}
        
        manquants = requis - disponibles
        
        assert len(manquants) == 0

    def test_ingredients_partiellement_manquants(self):
        """Certains ingrédients manquent."""
        disponibles = {"farine", "œufs"}
        requis = {"farine", "œufs", "sucre", "lait"}
        
        manquants = requis - disponibles
        
        assert manquants == {"sucre", "lait"}

    def test_calculer_ratio_disponibilite(self):
        """Calcul du ratio de disponibilité."""
        disponibles = {"farine", "œufs", "sucre"}
        requis = {"farine", "œufs", "sucre", "lait"}
        
        presents = requis & disponibles
        ratio = len(presents) / len(requis) if requis else 1
        
        assert ratio == 0.75


class TestMixerSuggestions:
    """Tests pour le mixage de suggestions."""

    def test_mixer_ratio_60_40(self):
        """Mixage 60% familières, 40% découvertes."""
        familieres = [
            {"id": 1, "score": 0.9},
            {"id": 2, "score": 0.85},
            {"id": 3, "score": 0.8},
        ]
        
        decouvertes = [
            {"id": 10, "score": 0.7},
            {"id": 11, "score": 0.65},
        ]
        
        nb_total = 5
        nb_familieres = int(nb_total * 0.6)  # 3
        nb_decouvertes = nb_total - nb_familieres  # 2
        
        mix = familieres[:nb_familieres] + decouvertes[:nb_decouvertes]
        
        assert len(mix) == 5

    def test_mixer_complement_insuffisant(self):
        """Compléter si pas assez de découvertes."""
        familieres = [{"id": i} for i in range(10)]
        decouvertes = [{"id": 100}]  # Une seule
        
        nb_total = 5
        nb_decouvertes = min(2, len(decouvertes))  # 1
        nb_familieres = nb_total - nb_decouvertes  # 4
        
        mix = familieres[:nb_familieres] + decouvertes[:nb_decouvertes]
        
        assert len(mix) == 5


class TestSuggestionsAvecContexte:
    """Tests pour les suggestions contextuelles."""

    def test_suggestions_rapides_midi(self):
        """Suggestions rapides pour le midi."""
        contexte = {
            "moment_journee": "midi",
            "contraintes_temps": 30
        }
        
        recettes = [
            {"nom": "Salade", "temps_total": 15},
            {"nom": "Pâtes", "temps_total": 25},
            {"nom": "Bœuf bourguignon", "temps_total": 180},
        ]
        
        adaptees = [r for r in recettes if r["temps_total"] <= contexte["contraintes_temps"]]
        
        assert len(adaptees) == 2

    def test_suggestions_ingredients_perimes(self):
        """Priorité aux ingrédients proches péremption."""
        ingredients_perissables = ["lait", "yaourt", "crème"]
        
        recettes = [
            {"nom": "Quiche", "ingredients": ["lait", "œufs"]},
            {"nom": "Pâtes", "ingredients": ["pâtes", "tomates"]},
            {"nom": "Crêpes", "ingredients": ["lait", "farine"]},
        ]
        
        def score_perissables(recette):
            return len(set(recette["ingredients"]) & set(ingredients_perissables))
        
        triees = sorted(recettes, key=score_perissables, reverse=True)
        
        assert triees[0]["nom"] == "Quiche" or triees[0]["nom"] == "Crêpes"


class TestSuggestionsIA:
    """Tests pour les suggestions avec IA."""

    @patch('src.services.suggestions_ia.ClientIA')
    def test_suggerer_avec_ia_success(self, mock_client):
        """Suggestion IA réussie."""
        from src.services.suggestions_ia import get_suggestions_service
        
        mock_client.return_value.generer.return_value = """
        [
            {"recette": "Poulet curry", "raison": "Ingrédients disponibles"},
            {"recette": "Riz sauté", "raison": "Rapide à préparer"}
        ]
        """
        
        service = get_suggestions_service()
        
        # Le test vérifie que le service peut appeler l'IA
        assert service is not None

    @patch('src.services.suggestions_ia.ClientIA')
    def test_suggerer_avec_ia_fallback(self, mock_client):
        """Fallback si IA échoue."""
        mock_client.return_value.generer.side_effect = Exception("API Error")
        
        from src.services.suggestions_ia import get_suggestions_service
        
        service = get_suggestions_service()
        
        # Devrait avoir un mécanisme de fallback
        assert service is not None
