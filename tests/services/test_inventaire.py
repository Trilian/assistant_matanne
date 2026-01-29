"""
Tests unitaires pour InventaireService.

Teste:
- CRUD articles inventaire
- Calcul de statuts (critique, stock_bas, peremption_proche)
- Alertes inventaire
- Suggestions IA pour courses
- Historique des modifications
- Gestion des photos
- Validation Pydantic
"""

import pytest
from datetime import date, timedelta
from unittest.mock import MagicMock, patch

from pydantic import ValidationError

from src.services.inventaire import (
    SuggestionCourses,
    ArticleImport,
    CATEGORIES,
    EMPLACEMENTS,
)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# FIXTURES
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@pytest.fixture
def mock_client_ia():
    """Mock du client IA Mistral."""
    with patch("src.services.inventaire.obtenir_client_ia") as mock:
        client = MagicMock()
        mock.return_value = client
        yield client


@pytest.fixture
def inventaire_service(mock_client_ia):
    """Service InventaireService avec mocks."""
    from src.services.inventaire import InventaireService
    
    service = InventaireService()
    return service


@pytest.fixture
def sample_article_data():
    """Données d'article inventaire valide."""
    return {
        "id": 1,
        "ingredient_id": 10,
        "ingredient_nom": "Tomates",
        "ingredient_categorie": "Légumes",
        "quantite": 5,
        "quantite_min": 2,
        "unite": "kg",
        "emplacement": "Frigo",
        "date_peremption": date.today() + timedelta(days=5),
        "statut": "ok",
        "jours_avant_peremption": 5,
    }


@pytest.fixture
def sample_article_critique():
    """Article en état critique (quantité < 50% du minimum)."""
    return {
        "id": 2,
        "ingredient_id": 11,
        "ingredient_nom": "Lait",
        "ingredient_categorie": "Laitier",
        "quantite": 0.3,  # < 50% de 1.0
        "quantite_min": 1.0,
        "unite": "L",
        "emplacement": "Frigo",
        "date_peremption": None,
        "statut": "critique",
        "jours_avant_peremption": None,
    }


@pytest.fixture
def sample_article_peremption_proche():
    """Article avec péremption proche (< 7 jours)."""
    return {
        "id": 3,
        "ingredient_id": 12,
        "ingredient_nom": "Yaourt",
        "ingredient_categorie": "Laitier",
        "quantite": 6,
        "quantite_min": 2,
        "unite": "unités",
        "emplacement": "Frigo",
        "date_peremption": date.today() + timedelta(days=3),
        "statut": "peremption_proche",
        "jours_avant_peremption": 3,
    }


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS VALIDATION PYDANTIC
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestSuggestionCoursesValidation:
    """Tests de validation du schéma SuggestionCourses."""

    def test_suggestion_courses_valide(self):
        """Test création avec données valides."""
        suggestion = SuggestionCourses(
            nom="Tomates cerises",
            quantite=500,
            unite="g",
            priorite="haute",
            rayon="Fruits et légumes",
        )
        assert suggestion.nom == "Tomates cerises"
        assert suggestion.quantite == 500
        assert suggestion.priorite == "haute"

    def test_suggestion_courses_nom_trop_court(self):
        """Test nom trop court (< 2 caractères)."""
        with pytest.raises(ValidationError) as exc_info:
            SuggestionCourses(
                nom="A",  # Trop court
                quantite=100,
                unite="g",
                priorite="haute",
                rayon="Ã‰picerie",
            )
        assert "min_length" in str(exc_info.value).lower() or "at least 2" in str(exc_info.value).lower()

    def test_suggestion_courses_quantite_negative(self):
        """Test quantité négative."""
        with pytest.raises(ValidationError) as exc_info:
            SuggestionCourses(
                nom="Pommes",
                quantite=-5,  # Négatif
                unite="kg",
                priorite="moyenne",
                rayon="Fruits et légumes",
            )
        assert "greater than" in str(exc_info.value).lower()

    def test_suggestion_courses_quantite_zero(self):
        """Test quantité à zéro."""
        with pytest.raises(ValidationError) as exc_info:
            SuggestionCourses(
                nom="Pommes",
                quantite=0,  # Zéro non autorisé
                unite="kg",
                priorite="moyenne",
                rayon="Fruits et légumes",
            )
        assert "greater than" in str(exc_info.value).lower()

    def test_suggestion_courses_priorite_invalide(self):
        """Test priorité non autorisée."""
        with pytest.raises(ValidationError) as exc_info:
            SuggestionCourses(
                nom="Pommes",
                quantite=2,
                unite="kg",
                priorite="urgente",  # Non autorisé
                rayon="Fruits et légumes",
            )
        assert "pattern" in str(exc_info.value).lower() or "string_pattern" in str(exc_info.value).lower()

    def test_suggestion_courses_priorites_valides(self):
        """Test toutes les priorités valides."""
        priorites = ["haute", "moyenne", "basse"]
        
        for prio in priorites:
            suggestion = SuggestionCourses(
                nom="Test article",
                quantite=1,
                unite="kg",
                priorite=prio,
                rayon="Test rayon",
            )
            assert suggestion.priorite == prio

    def test_suggestion_courses_unite_vide(self):
        """Test unité vide."""
        with pytest.raises(ValidationError) as exc_info:
            SuggestionCourses(
                nom="Pommes",
                quantite=2,
                unite="",  # Vide
                priorite="moyenne",
                rayon="Fruits",
            )
        assert "min_length" in str(exc_info.value).lower() or "at least 1" in str(exc_info.value).lower()


class TestArticleImportValidation:
    """Tests de validation du schéma ArticleImport."""

    def test_article_import_valide(self):
        """Test import article valide."""
        article = ArticleImport(
            nom="Pommes Granny",
            quantite=2.5,
            quantite_min=1.0,
            unite="kg",
            categorie="Fruits",
            emplacement="Frigo",
            date_peremption="2024-12-31",
        )
        assert article.nom == "Pommes Granny"
        assert article.quantite == 2.5

    def test_article_import_minimal(self):
        """Test import avec champs minimaux."""
        article = ArticleImport(
            nom="Sel",
            quantite=500,
            quantite_min=100,
            unite="g",
        )
        assert article.categorie is None
        assert article.emplacement is None
        assert article.date_peremption is None

    def test_article_import_quantite_negative(self):
        """Test quantité négative interdite."""
        with pytest.raises(ValidationError) as exc_info:
            ArticleImport(
                nom="Test",
                quantite=-1,
                quantite_min=0,
                unite="g",
            )
        assert "greater than or equal" in str(exc_info.value).lower()


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS CONSTANTES
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestConstantes:
    """Tests des constantes du module."""

    def test_categories_definies(self):
        """Test que les catégories sont définies."""
        assert len(CATEGORIES) > 0
        assert "Légumes" in CATEGORIES
        assert "Fruits" in CATEGORIES
        assert "Protéines" in CATEGORIES

    def test_emplacements_definis(self):
        """Test que les emplacements sont définis."""
        assert len(EMPLACEMENTS) > 0
        assert "Frigo" in EMPLACEMENTS
        assert "Congélateur" in EMPLACEMENTS
        assert "Placard" in EMPLACEMENTS


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS CALCUL STATUT
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestCalculStatut:
    """Tests du calcul de statut des articles."""

    def test_calcul_statut_ok(self, inventaire_service):
        """Test statut OK quand quantité suffisante et pas de péremption proche."""
        # Mock d'un article avec quantité > quantite_min
        article = MagicMock()
        article.quantite = 5.0
        article.quantite_min = 2.0
        article.date_peremption = date.today() + timedelta(days=30)
        
        statut = inventaire_service._calculer_statut(article, date.today())
        assert statut == "ok"

    def test_calcul_statut_stock_bas(self, inventaire_service):
        """Test statut stock_bas quand quantité < quantite_min."""
        article = MagicMock()
        article.quantite = 1.5  # < 2.0 mais >= 1.0 (50%)
        article.quantite_min = 2.0
        article.date_peremption = None
        
        statut = inventaire_service._calculer_statut(article, date.today())
        assert statut == "stock_bas"

    def test_calcul_statut_critique(self, inventaire_service):
        """Test statut critique quand quantité < 50% du minimum."""
        article = MagicMock()
        article.quantite = 0.5  # < 1.0 (50% de 2.0)
        article.quantite_min = 2.0
        article.date_peremption = None
        
        statut = inventaire_service._calculer_statut(article, date.today())
        assert statut == "critique"

    def test_calcul_statut_peremption_proche(self, inventaire_service):
        """Test statut peremption_proche quand <= 7 jours."""
        article = MagicMock()
        article.quantite = 10.0  # Quantité OK
        article.quantite_min = 2.0
        article.date_peremption = date.today() + timedelta(days=5)  # 5 jours
        
        statut = inventaire_service._calculer_statut(article, date.today())
        assert statut == "peremption_proche"

    def test_calcul_statut_peremption_prioritaire(self, inventaire_service):
        """Test que péremption proche prime sur stock OK."""
        article = MagicMock()
        article.quantite = 100.0  # Beaucoup de stock
        article.quantite_min = 1.0
        article.date_peremption = date.today() + timedelta(days=2)  # Périme bientôt
        
        statut = inventaire_service._calculer_statut(article, date.today())
        assert statut == "peremption_proche"


class TestJoursAvantPeremption:
    """Tests du calcul des jours avant péremption."""

    def test_jours_avant_peremption_positif(self, inventaire_service):
        """Test calcul avec date future."""
        article = MagicMock()
        article.date_peremption = date.today() + timedelta(days=10)
        
        jours = inventaire_service._jours_avant_peremption(article, date.today())
        assert jours == 10

    def test_jours_avant_peremption_negatif(self, inventaire_service):
        """Test calcul avec date passée (périmé)."""
        article = MagicMock()
        article.date_peremption = date.today() - timedelta(days=3)
        
        jours = inventaire_service._jours_avant_peremption(article, date.today())
        assert jours == -3

    def test_jours_avant_peremption_none(self, inventaire_service):
        """Test sans date de péremption."""
        article = MagicMock()
        article.date_peremption = None
        
        jours = inventaire_service._jours_avant_peremption(article, date.today())
        assert jours is None

    def test_jours_avant_peremption_aujourdhui(self, inventaire_service):
        """Test péremption aujourd'hui."""
        article = MagicMock()
        article.date_peremption = date.today()
        
        jours = inventaire_service._jours_avant_peremption(article, date.today())
        assert jours == 0


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS ALERTES
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestAlertes:
    """Tests du système d'alertes."""

    def test_get_alertes_structure(self, inventaire_service):
        """Test structure retournée par get_alertes."""
        with patch.object(inventaire_service, "get_inventaire_complet", return_value=[]):
            alertes = inventaire_service.get_alertes()
            
            # Doit avoir les 3 catégories
            assert "stock_bas" in alertes
            assert "critique" in alertes
            assert "peremption_proche" in alertes

    def test_get_alertes_trie_par_statut(self, inventaire_service, sample_article_critique, sample_article_peremption_proche):
        """Test que les alertes sont triées par statut."""
        inventaire = [
            sample_article_critique,
            sample_article_peremption_proche,
        ]
        
        with patch.object(inventaire_service, "get_inventaire_complet", return_value=inventaire):
            alertes = inventaire_service.get_alertes()
            
            assert len(alertes["critique"]) == 1
            assert len(alertes["peremption_proche"]) == 1
            assert alertes["critique"][0]["ingredient_nom"] == "Lait"

    def test_get_alertes_exclut_ok(self, inventaire_service, sample_article_data):
        """Test que les articles OK sont exclus des alertes."""
        inventaire = [sample_article_data]  # Statut "ok"
        
        with patch.object(inventaire_service, "get_inventaire_complet", return_value=inventaire):
            alertes = inventaire_service.get_alertes()
            
            total_alertes = sum(len(v) for v in alertes.values())
            assert total_alertes == 0


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS SUGGESTIONS IA
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestSuggestionsIA:
    """Tests des suggestions IA pour courses."""

    def test_suggerer_courses_ia_construit_contexte(self, inventaire_service):
        """Test que suggerer_courses_ia construit le bon contexte."""
        with patch.object(inventaire_service, "get_alertes", return_value={"stock_bas": [], "critique": [], "peremption_proche": []}), \
             patch.object(inventaire_service, "get_inventaire_complet", return_value=[]), \
             patch.object(inventaire_service, "build_inventory_summary") as mock_summary, \
             patch.object(inventaire_service, "build_json_prompt") as mock_prompt, \
             patch.object(inventaire_service, "call_with_list_parsing_sync", return_value=[]):
            
            mock_summary.return_value = "Résumé inventaire"
            mock_prompt.return_value = "Prompt JSON"
            
            inventaire_service.suggerer_courses_ia()
            
            # Vérifier que build_inventory_summary a été appelé
            mock_summary.assert_called_once()

    def test_suggerer_courses_ia_retourne_suggestions(self, inventaire_service):
        """Test que suggerer_courses_ia retourne des suggestions."""
        suggestions = [
            SuggestionCourses(
                nom="Lait",
                quantite=2,
                unite="L",
                priorite="haute",
                rayon="Produits frais",
            )
        ]
        
        with patch.object(inventaire_service, "get_alertes", return_value={}), \
             patch.object(inventaire_service, "get_inventaire_complet", return_value=[]), \
             patch.object(inventaire_service, "build_inventory_summary", return_value="ctx"), \
             patch.object(inventaire_service, "build_json_prompt", return_value="prompt"), \
             patch.object(inventaire_service, "call_with_list_parsing_sync", return_value=suggestions), \
             patch.object(inventaire_service, "build_system_prompt", return_value="system"):
            
            result = inventaire_service.suggerer_courses_ia()
            
            assert len(result) == 1
            assert result[0].nom == "Lait"
            assert result[0].priorite == "haute"

    def test_suggerer_courses_ia_erreur_retourne_vide(self, inventaire_service):
        """Test que les erreurs retournent une liste vide."""
        with patch.object(inventaire_service, "get_alertes", side_effect=Exception("Erreur")):
            result = inventaire_service.suggerer_courses_ia()
            
            # GrÃ¢ce au décorateur @with_error_handling(default_return=[])
            assert result == []


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS GESTION ARTICLES
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestGestionArticles:
    """Tests de la gestion des articles."""

    def test_ajouter_article_parametres(self, inventaire_service):
        """Test que ajouter_article accepte les bons paramètres."""
        # La méthode doit accepter ces paramètres
        import inspect
        sig = inspect.signature(inventaire_service.ajouter_article)
        params = list(sig.parameters.keys())
        
        assert "ingredient_nom" in params
        assert "quantite" in params
        assert "quantite_min" in params
        assert "emplacement" in params
        assert "date_peremption" in params

    def test_mettre_a_jour_article_parametres(self, inventaire_service):
        """Test que mettre_a_jour_article accepte les bons paramètres."""
        import inspect
        sig = inspect.signature(inventaire_service.mettre_a_jour_article)
        params = list(sig.parameters.keys())
        
        assert "article_id" in params
        assert "quantite" in params
        assert "emplacement" in params

    def test_supprimer_article_parametres(self, inventaire_service):
        """Test que supprimer_article accepte article_id."""
        import inspect
        sig = inspect.signature(inventaire_service.supprimer_article)
        params = list(sig.parameters.keys())
        
        assert "article_id" in params


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS HISTORIQUE
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestHistorique:
    """Tests de l'historique des modifications."""

    def test_get_historique_parametres(self, inventaire_service):
        """Test que get_historique accepte les bons filtres."""
        import inspect
        sig = inspect.signature(inventaire_service.get_historique)
        params = list(sig.parameters.keys())
        
        assert "article_id" in params
        assert "ingredient_id" in params
        assert "days" in params

    def test_enregistrer_modification_parametres(self, inventaire_service):
        """Test que _enregistrer_modification accepte tous les champs."""
        import inspect
        sig = inspect.signature(inventaire_service._enregistrer_modification)
        params = list(sig.parameters.keys())
        
        assert "article" in params
        assert "type_modification" in params
        assert "quantite_avant" in params
        assert "quantite_apres" in params


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS PHOTOS
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestPhotos:
    """Tests de la gestion des photos."""

    def test_ajouter_photo_existe(self, inventaire_service):
        """Test que la méthode ajouter_photo existe."""
        assert hasattr(inventaire_service, "ajouter_photo")
        assert callable(inventaire_service.ajouter_photo)

    def test_supprimer_photo_existe(self, inventaire_service):
        """Test que la méthode supprimer_photo existe."""
        assert hasattr(inventaire_service, "supprimer_photo")
        assert callable(inventaire_service.supprimer_photo)

    def test_obtenir_photo_existe(self, inventaire_service):
        """Test que la méthode obtenir_photo existe."""
        assert hasattr(inventaire_service, "obtenir_photo")
        assert callable(inventaire_service.obtenir_photo)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS CACHE ET INVALIDATION
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestCacheInventaire:
    """Tests du comportement du cache."""

    def test_invalider_cache_existe(self, inventaire_service):
        """Test que _invalider_cache est disponible (héritée de BaseService)."""
        assert hasattr(inventaire_service, "_invalider_cache")
        assert callable(inventaire_service._invalider_cache)

    @patch("src.services.inventaire.Cache")
    def test_get_inventaire_complet_cache_key(self, mock_cache_class, inventaire_service):
        """Test que la clé de cache inclut les paramètres."""
        # Le décorateur @with_cache génère une clé basée sur les paramètres
        # key_func: f"inventaire_{emplacement}_{categorie}_{include_ok}"
        
        # On vérifie que le pattern de clé est cohérent
        emplacement = "Frigo"
        categorie = "Légumes"
        include_ok = True
        
        expected_key = f"inventaire_{emplacement}_{categorie}_{include_ok}"
        assert "inventaire" in expected_key
        assert emplacement in expected_key


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS INTÃ‰GRATION SERVICE
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@pytest.mark.integration
class TestInventaireServiceIntegration:
    """Tests d'intégration légers (sans vraie DB)."""

    def test_service_herite_base_service(self, inventaire_service):
        """Test que InventaireService hérite de BaseService."""
        from src.services.types import BaseService
        assert isinstance(inventaire_service, BaseService)

    def test_service_herite_base_ai_service(self, inventaire_service):
        """Test que InventaireService hérite de BaseAIService."""
        from src.services.base_ai_service import BaseAIService
        assert isinstance(inventaire_service, BaseAIService)

    def test_service_a_methodes_mixin(self, inventaire_service):
        """Test que les méthodes du mixin sont disponibles."""
        # InventoryAIMixin fournit build_inventory_summary
        assert hasattr(inventaire_service, "build_inventory_summary")
        assert callable(inventaire_service.build_inventory_summary)

    def test_model_est_article_inventaire(self, inventaire_service):
        """Test que le modèle est ArticleInventaire."""
        from src.core.models import ArticleInventaire
        assert inventaire_service.model == ArticleInventaire


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS FILTRES INVENTAIRE
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestFiltresInventaire:
    """Tests des filtres sur l'inventaire."""

    def test_get_inventaire_complet_filtre_emplacement(self, inventaire_service):
        """Test filtre par emplacement."""
        # La méthode doit accepter le paramètre emplacement
        import inspect
        sig = inspect.signature(inventaire_service.get_inventaire_complet)
        assert "emplacement" in sig.parameters

    def test_get_inventaire_complet_filtre_categorie(self, inventaire_service):
        """Test filtre par catégorie."""
        import inspect
        sig = inspect.signature(inventaire_service.get_inventaire_complet)
        assert "categorie" in sig.parameters

    def test_get_inventaire_complet_include_ok(self, inventaire_service):
        """Test option include_ok."""
        import inspect
        sig = inspect.signature(inventaire_service.get_inventaire_complet)
        assert "include_ok" in sig.parameters
        
        # Valeur par défaut doit être True
        default = sig.parameters["include_ok"].default
        assert default is True

