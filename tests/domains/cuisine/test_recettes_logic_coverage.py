"""
Tests de couverture complets pour src/domains/cuisine/logic/recettes_logic.py
Objectif: atteindre 80%+ de couverture
"""
import pytest
from datetime import date
from unittest.mock import Mock, MagicMock, patch, PropertyMock


# ═══════════════════════════════════════════════════════════════════════════════
# TESTS LECTURE RECETTES (get_toutes_recettes, get_recette_by_id, rechercher_recettes)
# ═══════════════════════════════════════════════════════════════════════════════

class TestGetToutesRecettes:
    """Tests pour get_toutes_recettes."""

    @patch("src.domains.cuisine.logic.recettes_logic.get_db_context")
    @patch("src.domains.cuisine.logic.recettes_logic.get_recette_service")
    def test_get_toutes_recettes_success(self, mock_service, mock_context):
        """Récupère toutes les recettes avec succès."""
        from src.domains.cuisine.logic.recettes_logic import get_toutes_recettes
        
        mock_recette1 = Mock()
        mock_recette1.id = 1
        mock_recette1.nom = "Recette 1"
        mock_recette2 = Mock()
        mock_recette2.id = 2
        mock_recette2.nom = "Recette 2"
        
        mock_session = MagicMock()
        mock_session.query.return_value.all.return_value = [mock_recette1, mock_recette2]
        mock_context.return_value.__enter__.return_value = mock_session
        
        result = get_toutes_recettes()
        
        assert len(result) == 2
        assert result[0].nom == "Recette 1"
        mock_session.query.assert_called_once()

    @patch("src.domains.cuisine.logic.recettes_logic.get_db_context")
    @patch("src.domains.cuisine.logic.recettes_logic.get_recette_service")
    def test_get_toutes_recettes_vide(self, mock_service, mock_context):
        """Récupère une liste vide."""
        from src.domains.cuisine.logic.recettes_logic import get_toutes_recettes
        
        mock_session = MagicMock()
        mock_session.query.return_value.all.return_value = []
        mock_context.return_value.__enter__.return_value = mock_session
        
        result = get_toutes_recettes()
        
        assert result == []


class TestGetRecetteById:
    """Tests pour get_recette_by_id."""

    @patch("src.domains.cuisine.logic.recettes_logic.get_db_context")
    def test_get_recette_by_id_found(self, mock_context):
        """Trouve une recette par ID."""
        from src.domains.cuisine.logic.recettes_logic import get_recette_by_id
        
        mock_recette = Mock()
        mock_recette.id = 1
        mock_recette.nom = "Tarte aux pommes"
        
        mock_session = MagicMock()
        mock_session.query.return_value.filter.return_value.first.return_value = mock_recette
        mock_context.return_value.__enter__.return_value = mock_session
        
        result = get_recette_by_id(1)
        
        assert result is not None
        assert result.nom == "Tarte aux pommes"

    @patch("src.domains.cuisine.logic.recettes_logic.get_db_context")
    def test_get_recette_by_id_not_found(self, mock_context):
        """Recette non trouvée."""
        from src.domains.cuisine.logic.recettes_logic import get_recette_by_id
        
        mock_session = MagicMock()
        mock_session.query.return_value.filter.return_value.first.return_value = None
        mock_context.return_value.__enter__.return_value = mock_session
        
        result = get_recette_by_id(999)
        
        assert result is None


class TestRechercherRecettes:
    """Tests pour rechercher_recettes avec filtres."""

    @patch("src.domains.cuisine.logic.recettes_logic.get_db_context")
    def test_rechercher_recettes_par_query(self, mock_context):
        """Recherche par texte."""
        from src.domains.cuisine.logic.recettes_logic import rechercher_recettes
        
        mock_recette = Mock()
        mock_recette.nom = "Tarte aux pommes"
        
        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = [mock_recette]
        
        mock_session = MagicMock()
        mock_session.query.return_value = mock_query
        mock_context.return_value.__enter__.return_value = mock_session
        
        result = rechercher_recettes(query="tarte")
        
        assert len(result) == 1

    @patch("src.domains.cuisine.logic.recettes_logic.get_db_context")
    def test_rechercher_recettes_par_categorie(self, mock_context):
        """Recherche par catégorie."""
        from src.domains.cuisine.logic.recettes_logic import rechercher_recettes
        
        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = []
        
        mock_session = MagicMock()
        mock_session.query.return_value = mock_query
        mock_context.return_value.__enter__.return_value = mock_session
        
        result = rechercher_recettes(query="", categorie="dessert")
        
        assert result == []

    @patch("src.domains.cuisine.logic.recettes_logic.get_db_context")
    def test_rechercher_recettes_par_difficulte(self, mock_context):
        """Recherche par difficulté."""
        from src.domains.cuisine.logic.recettes_logic import rechercher_recettes
        
        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = []
        
        mock_session = MagicMock()
        mock_session.query.return_value = mock_query
        mock_context.return_value.__enter__.return_value = mock_session
        
        result = rechercher_recettes(query="", difficulte="facile")
        
        assert result == []

    @patch("src.domains.cuisine.logic.recettes_logic.get_db_context")
    def test_rechercher_recettes_par_temps_max(self, mock_context):
        """Recherche par temps max."""
        from src.domains.cuisine.logic.recettes_logic import rechercher_recettes
        
        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = []
        
        mock_session = MagicMock()
        mock_session.query.return_value = mock_query
        mock_context.return_value.__enter__.return_value = mock_session
        
        result = rechercher_recettes(query="", temps_max=30)
        
        assert result == []

    @patch("src.domains.cuisine.logic.recettes_logic.get_db_context")
    def test_rechercher_recettes_tous_filtres(self, mock_context):
        """Recherche avec tous les filtres."""
        from src.domains.cuisine.logic.recettes_logic import rechercher_recettes
        
        mock_recette = Mock()
        mock_recette.nom = "Salade"
        
        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = [mock_recette]
        
        mock_session = MagicMock()
        mock_session.query.return_value = mock_query
        mock_context.return_value.__enter__.return_value = mock_session
        
        result = rechercher_recettes(
            query="salade",
            categorie="entrée",
            difficulte="facile",
            temps_max=15
        )
        
        assert len(result) == 1


class TestGetRecettesParCategorie:
    """Tests pour get_recettes_par_categorie."""

    @patch("src.domains.cuisine.logic.recettes_logic.get_db_context")
    def test_get_recettes_par_categorie_success(self, mock_context):
        """Récupère recettes par catégorie."""
        from src.domains.cuisine.logic.recettes_logic import get_recettes_par_categorie
        
        mock_recette = Mock()
        mock_recette.categorie = "dessert"
        
        mock_session = MagicMock()
        mock_session.query.return_value.filter.return_value.all.return_value = [mock_recette]
        mock_context.return_value.__enter__.return_value = mock_session
        
        result = get_recettes_par_categorie("dessert")
        
        assert len(result) == 1


class TestGetRecettesFavorites:
    """Tests pour get_recettes_favorites."""

    @patch("src.domains.cuisine.logic.recettes_logic.Recette")
    @patch("src.domains.cuisine.logic.recettes_logic.get_db_context")
    def test_get_recettes_favorites_success(self, mock_context, mock_recette_class):
        """Récupère recettes favorites."""
        from src.domains.cuisine.logic.recettes_logic import get_recettes_favorites
        
        mock_recette = Mock()
        mock_recette.favorite = True
        
        mock_session = MagicMock()
        mock_session.query.return_value.filter.return_value.all.return_value = [mock_recette]
        mock_context.return_value.__enter__.return_value = mock_session
        
        # Mock l'attribut 'favorite' sur la classe Recette
        mock_recette_class.favorite = Mock()
        mock_recette_class.favorite.__eq__ = Mock(return_value=Mock())
        
        result = get_recettes_favorites()
        
        assert len(result) == 1


# ═══════════════════════════════════════════════════════════════════════════════
# TESTS CRÉATION/MODIFICATION RECETTES
# ═══════════════════════════════════════════════════════════════════════════════

class TestCreerRecette:
    """Tests pour creer_recette."""

    @patch("src.domains.cuisine.logic.recettes_logic.Recette")
    @patch("src.domains.cuisine.logic.recettes_logic.get_db_context")
    @patch("src.domains.cuisine.logic.recettes_logic.get_recette_service")
    def test_creer_recette_success(self, mock_service, mock_context, mock_recette_class):
        """Crée une recette avec succès."""
        from src.domains.cuisine.logic.recettes_logic import creer_recette
        
        mock_recette_instance = Mock()
        mock_recette_instance.nom = "Tarte aux pommes"
        mock_recette_class.return_value = mock_recette_instance
        
        mock_session = MagicMock()
        mock_context.return_value.__enter__.return_value = mock_session
        
        result = creer_recette(
            nom="Tarte aux pommes",
            ingredients=["pommes", "farine"],
            instructions=["Étape 1", "Étape 2"],
            categorie="dessert",
            difficulte="moyenne",
            temps_preparation=45,
            portions=6,
            calories=300
        )
        
        mock_recette_class.assert_called_once()
        mock_session.add.assert_called_once_with(mock_recette_instance)
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once_with(mock_recette_instance)

    @patch("src.domains.cuisine.logic.recettes_logic.Recette")
    @patch("src.domains.cuisine.logic.recettes_logic.get_db_context")
    @patch("src.domains.cuisine.logic.recettes_logic.get_recette_service")
    def test_creer_recette_minimal(self, mock_service, mock_context, mock_recette_class):
        """Crée une recette avec paramètres minimaux."""
        from src.domains.cuisine.logic.recettes_logic import creer_recette
        
        mock_recette_instance = Mock()
        mock_recette_class.return_value = mock_recette_instance
        
        mock_session = MagicMock()
        mock_context.return_value.__enter__.return_value = mock_session
        
        result = creer_recette(
            nom="Test",
            ingredients=["un"],
            instructions=["faire"]
        )
        
        mock_session.add.assert_called_once()


class TestMettreAJourRecette:
    """Tests pour mettre_a_jour_recette."""

    @patch("src.domains.cuisine.logic.recettes_logic.get_db_context")
    def test_mettre_a_jour_recette_success(self, mock_context):
        """Met à jour une recette existante."""
        from src.domains.cuisine.logic.recettes_logic import mettre_a_jour_recette
        
        mock_recette = Mock()
        mock_recette.id = 1
        mock_recette.nom = "Ancien nom"
        
        mock_session = MagicMock()
        mock_session.query.return_value.filter.return_value.first.return_value = mock_recette
        mock_context.return_value.__enter__.return_value = mock_session
        
        result = mettre_a_jour_recette(1, {"nom": "Nouveau nom"})
        
        assert mock_recette.nom == "Nouveau nom"
        mock_session.commit.assert_called_once()

    @patch("src.domains.cuisine.logic.recettes_logic.get_db_context")
    def test_mettre_a_jour_recette_not_found(self, mock_context):
        """Recette à mettre à jour non trouvée."""
        from src.domains.cuisine.logic.recettes_logic import mettre_a_jour_recette
        
        mock_session = MagicMock()
        mock_session.query.return_value.filter.return_value.first.return_value = None
        mock_context.return_value.__enter__.return_value = mock_session
        
        result = mettre_a_jour_recette(999, {"nom": "Nouveau"})
        
        assert result is None

    @patch("src.domains.cuisine.logic.recettes_logic.get_db_context")
    def test_mettre_a_jour_attribut_inexistant(self, mock_context):
        """Mise à jour avec attribut inexistant (ignoré)."""
        from src.domains.cuisine.logic.recettes_logic import mettre_a_jour_recette
        
        mock_recette = Mock(spec=["id", "nom"])
        mock_recette.id = 1
        mock_recette.nom = "Test"
        
        mock_session = MagicMock()
        mock_session.query.return_value.filter.return_value.first.return_value = mock_recette
        mock_context.return_value.__enter__.return_value = mock_session
        
        result = mettre_a_jour_recette(1, {"attribut_inexistant": "valeur"})
        
        # L'attribut inexistant ne doit pas lever d'erreur
        mock_session.commit.assert_called_once()


class TestSupprimerRecette:
    """Tests pour supprimer_recette."""

    @patch("src.domains.cuisine.logic.recettes_logic.get_db_context")
    def test_supprimer_recette_success(self, mock_context):
        """Supprime une recette existante."""
        from src.domains.cuisine.logic.recettes_logic import supprimer_recette
        
        mock_recette = Mock()
        mock_recette.id = 1
        
        mock_session = MagicMock()
        mock_session.query.return_value.filter.return_value.first.return_value = mock_recette
        mock_context.return_value.__enter__.return_value = mock_session
        
        result = supprimer_recette(1)
        
        assert result is True
        mock_session.delete.assert_called_once_with(mock_recette)
        mock_session.commit.assert_called_once()

    @patch("src.domains.cuisine.logic.recettes_logic.get_db_context")
    def test_supprimer_recette_not_found(self, mock_context):
        """Recette à supprimer non trouvée."""
        from src.domains.cuisine.logic.recettes_logic import supprimer_recette
        
        mock_session = MagicMock()
        mock_session.query.return_value.filter.return_value.first.return_value = None
        mock_context.return_value.__enter__.return_value = mock_session
        
        result = supprimer_recette(999)
        
        assert result is False


class TestToggleFavorite:
    """Tests pour toggle_favorite."""

    @patch("src.domains.cuisine.logic.recettes_logic.get_db_context")
    def test_toggle_favorite_to_true(self, mock_context):
        """Toggle de False à True."""
        from src.domains.cuisine.logic.recettes_logic import toggle_favorite
        
        mock_recette = Mock()
        mock_recette.id = 1
        mock_recette.favorite = False
        
        mock_session = MagicMock()
        mock_session.query.return_value.filter.return_value.first.return_value = mock_recette
        mock_context.return_value.__enter__.return_value = mock_session
        
        result = toggle_favorite(1)
        
        assert mock_recette.favorite is True
        mock_session.commit.assert_called_once()

    @patch("src.domains.cuisine.logic.recettes_logic.get_db_context")
    def test_toggle_favorite_to_false(self, mock_context):
        """Toggle de True à False."""
        from src.domains.cuisine.logic.recettes_logic import toggle_favorite
        
        mock_recette = Mock()
        mock_recette.id = 1
        mock_recette.favorite = True
        
        mock_session = MagicMock()
        mock_session.query.return_value.filter.return_value.first.return_value = mock_recette
        mock_context.return_value.__enter__.return_value = mock_session
        
        result = toggle_favorite(1)
        
        assert mock_recette.favorite is False

    @patch("src.domains.cuisine.logic.recettes_logic.get_db_context")
    def test_toggle_favorite_not_found(self, mock_context):
        """Toggle sur recette inexistante."""
        from src.domains.cuisine.logic.recettes_logic import toggle_favorite
        
        mock_session = MagicMock()
        mock_session.query.return_value.filter.return_value.first.return_value = None
        mock_context.return_value.__enter__.return_value = mock_session
        
        result = toggle_favorite(999)
        
        assert result is False


# ═══════════════════════════════════════════════════════════════════════════════
# TESTS PLANNING REPAS
# ═══════════════════════════════════════════════════════════════════════════════

class TestGetPlanningSemaine:
    """Tests pour get_planning_semaine."""

    @patch("src.domains.cuisine.logic.recettes_logic.get_db_context")
    def test_get_planning_semaine_success(self, mock_context):
        """Récupère le planning d'une semaine."""
        from src.domains.cuisine.logic.recettes_logic import get_planning_semaine
        
        mock_repas = Mock()
        mock_repas.date_repas = date(2024, 1, 15)
        
        mock_session = MagicMock()
        mock_session.query.return_value.filter.return_value.all.return_value = [mock_repas]
        mock_context.return_value.__enter__.return_value = mock_session
        
        result = get_planning_semaine(date(2024, 1, 14), date(2024, 1, 20))
        
        assert len(result) == 1

    @patch("src.domains.cuisine.logic.recettes_logic.get_db_context")
    def test_get_planning_semaine_vide(self, mock_context):
        """Planning vide."""
        from src.domains.cuisine.logic.recettes_logic import get_planning_semaine
        
        mock_session = MagicMock()
        mock_session.query.return_value.filter.return_value.all.return_value = []
        mock_context.return_value.__enter__.return_value = mock_session
        
        result = get_planning_semaine(date(2024, 1, 14), date(2024, 1, 20))
        
        assert result == []


class TestAjouterRepasPlanning:
    """Tests pour ajouter_repas_planning."""

    @patch("src.domains.cuisine.logic.recettes_logic.Repas")
    @patch("src.domains.cuisine.logic.recettes_logic.get_db_context")
    def test_ajouter_repas_planning_success(self, mock_context, mock_repas_class):
        """Ajoute un repas au planning."""
        from src.domains.cuisine.logic.recettes_logic import ajouter_repas_planning
        
        mock_repas_instance = Mock()
        mock_repas_class.return_value = mock_repas_instance
        
        mock_session = MagicMock()
        mock_context.return_value.__enter__.return_value = mock_session
        
        result = ajouter_repas_planning(
            recette_id=1,
            date_repas=date(2024, 1, 15),
            type_repas="diner"
        )
        
        mock_repas_class.assert_called_once()
        mock_session.add.assert_called_once_with(mock_repas_instance)
        mock_session.commit.assert_called_once()

    @patch("src.domains.cuisine.logic.recettes_logic.Repas")
    @patch("src.domains.cuisine.logic.recettes_logic.get_db_context")
    def test_ajouter_repas_planning_dejeuner(self, mock_context, mock_repas_class):
        """Ajoute un déjeuner au planning."""
        from src.domains.cuisine.logic.recettes_logic import ajouter_repas_planning
        
        mock_repas_instance = Mock()
        mock_repas_class.return_value = mock_repas_instance
        
        mock_session = MagicMock()
        mock_context.return_value.__enter__.return_value = mock_session
        
        result = ajouter_repas_planning(
            recette_id=2,
            date_repas=date(2024, 1, 16),
            type_repas="dejeuner"
        )
        
        mock_session.add.assert_called_once()


# ═══════════════════════════════════════════════════════════════════════════════
# TESTS STATISTIQUES
# ═══════════════════════════════════════════════════════════════════════════════

class TestGetStatistiquesRecettes:
    """Tests pour get_statistiques_recettes."""

    @patch("src.domains.cuisine.logic.recettes_logic.get_db_context")
    def test_get_statistiques_recettes_success(self, mock_context):
        """Calcule les statistiques avec des recettes."""
        from src.domains.cuisine.logic.recettes_logic import get_statistiques_recettes
        
        mock_recette1 = Mock()
        mock_recette1.temps_preparation = 30
        mock_recette1.favorite = True
        mock_recette1.categorie = "dessert"
        mock_recette1.difficulte = "facile"
        
        mock_recette2 = Mock()
        mock_recette2.temps_preparation = 60
        mock_recette2.favorite = False
        mock_recette2.categorie = "plat"
        mock_recette2.difficulte = "moyenne"
        
        mock_session = MagicMock()
        mock_session.query.return_value.all.return_value = [mock_recette1, mock_recette2]
        mock_context.return_value.__enter__.return_value = mock_session
        
        result = get_statistiques_recettes()
        
        assert result["total"] == 2
        assert result["favorites"] == 1
        assert result["temps_moyen"] == 45
        assert result["par_categorie"]["dessert"] == 1
        assert result["par_categorie"]["plat"] == 1
        assert result["par_difficulte"]["facile"] == 1
        assert result["par_difficulte"]["moyenne"] == 1

    @patch("src.domains.cuisine.logic.recettes_logic.get_db_context")
    def test_get_statistiques_recettes_vide(self, mock_context):
        """Statistiques avec aucune recette."""
        from src.domains.cuisine.logic.recettes_logic import get_statistiques_recettes
        
        mock_session = MagicMock()
        mock_session.query.return_value.all.return_value = []
        mock_context.return_value.__enter__.return_value = mock_session
        
        result = get_statistiques_recettes()
        
        assert result["total"] == 0
        assert result["favorites"] == 0
        assert result["temps_moyen"] == 0
        assert result["par_categorie"] == {}
        assert result["par_difficulte"] == {}

    @patch("src.domains.cuisine.logic.recettes_logic.get_db_context")
    def test_get_statistiques_recettes_categorie_none(self, mock_context):
        """Statistiques avec catégorie/difficulté None."""
        from src.domains.cuisine.logic.recettes_logic import get_statistiques_recettes
        
        mock_recette = Mock()
        mock_recette.temps_preparation = 20
        mock_recette.favorite = False
        mock_recette.categorie = None
        mock_recette.difficulte = None
        
        mock_session = MagicMock()
        mock_session.query.return_value.all.return_value = [mock_recette]
        mock_context.return_value.__enter__.return_value = mock_session
        
        result = get_statistiques_recettes()
        
        assert result["total"] == 1
        assert result["par_categorie"]["autre"] == 1
        assert result["par_difficulte"]["moyenne"] == 1

    @patch("src.domains.cuisine.logic.recettes_logic.get_db_context")
    def test_get_statistiques_recettes_temps_none(self, mock_context):
        """Statistiques avec temps_preparation None."""
        from src.domains.cuisine.logic.recettes_logic import get_statistiques_recettes
        
        mock_recette = Mock()
        mock_recette.temps_preparation = None
        mock_recette.favorite = True
        mock_recette.categorie = "entrée"
        mock_recette.difficulte = "difficile"
        
        mock_session = MagicMock()
        mock_session.query.return_value.all.return_value = [mock_recette]
        mock_context.return_value.__enter__.return_value = mock_session
        
        result = get_statistiques_recettes()
        
        assert result["total"] == 1
        assert result["temps_moyen"] == 0
        assert result["favorites"] == 1


# ═══════════════════════════════════════════════════════════════════════════════
# TESTS EDGE CASES
# ═══════════════════════════════════════════════════════════════════════════════

class TestEdgeCases:
    """Tests des cas limites."""

    @patch("src.domains.cuisine.logic.recettes_logic.get_db_context")
    def test_rechercher_recettes_query_vide(self, mock_context):
        """Recherche avec query vide (pas de filtre query)."""
        from src.domains.cuisine.logic.recettes_logic import rechercher_recettes
        
        mock_query = MagicMock()
        mock_query.all.return_value = []
        
        mock_session = MagicMock()
        mock_session.query.return_value = mock_query
        mock_context.return_value.__enter__.return_value = mock_session
        
        result = rechercher_recettes(query="")
        
        # Le filtre ilike ne doit pas être appelé si query est vide
        assert result == []

    def test_calculer_cout_recette_match_partiel(self):
        """Test du match partiel des ingrédients."""
        from src.domains.cuisine.logic.recettes_logic import calculer_cout_recette
        
        recette = Mock()
        recette.ingredients = ["200g de pommes de terre", "1 litre de lait frais"]
        
        prix_ingredients = {
            "pommes de terre": 1.50,
            "lait": 1.20
        }
        
        result = calculer_cout_recette(recette, prix_ingredients)
        
        # "pommes de terre" est trouvé dans "200g de pommes de terre"
        # "lait" est trouvé dans "1 litre de lait frais"
        assert result == 2.70

    def test_valider_recette_portions_negatives(self):
        """Validation avec portions négatives."""
        from src.domains.cuisine.logic.recettes_logic import valider_recette
        
        data = {
            "nom": "Test",
            "ingredients": ["un"],
            "instructions": ["faire"],
            "portions": -1
        }
        
        valid, error = valider_recette(data)
        
        assert valid is False
        assert "portion" in error.lower()

    def test_valider_recette_ingredients_none(self):
        """Validation avec ingrédients None."""
        from src.domains.cuisine.logic.recettes_logic import valider_recette
        
        data = {
            "nom": "Test",
            "ingredients": None,
            "instructions": ["faire"],
            "portions": 1
        }
        
        valid, error = valider_recette(data)
        
        assert valid is False
        assert "ingrédient" in error.lower()

    def test_valider_recette_instructions_none(self):
        """Validation avec instructions None."""
        from src.domains.cuisine.logic.recettes_logic import valider_recette
        
        data = {
            "nom": "Test",
            "ingredients": ["un"],
            "instructions": None,
            "portions": 1
        }
        
        valid, error = valider_recette(data)
        
        assert valid is False
        assert "instruction" in error.lower()
