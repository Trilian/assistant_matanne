"""
Tests pour src/services/courses/service.py

Tests du ServiceCourses:
- CRUD liste de courses
- Obtention liste avec filtres
- Suggestions IA depuis inventaire
- Gestion des modèles de courses
- Application des modèles
"""

from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy.orm import Session

from src.core.models import ArticleCourses, ArticleModele, Ingredient, ModeleCourses
from src.services.courses.service import (
    ServiceCourses,
    get_courses_service,
    obtenir_service_courses,
)
from src.services.courses.types import SuggestionCourses

# ═══════════════════════════════════════════════════════════
# FIXTURES
# ═══════════════════════════════════════════════════════════


@pytest.fixture
def mock_client_ia():
    """Mock du client IA."""
    client = MagicMock()
    client.appeler = MagicMock(return_value="[]")
    return client


@pytest.fixture
def service_courses(mock_client_ia):
    """Instance du service courses avec client IA mocké."""
    with patch("src.services.courses.service.obtenir_client_ia", return_value=mock_client_ia):
        service = ServiceCourses()
        return service


@pytest.fixture
def sample_ingredient(db: Session) -> Ingredient:
    """Crée un ingrédient de test."""
    ingredient = Ingredient(nom="Tomates", unite="kg", categorie="Fruits & Légumes")
    db.add(ingredient)
    db.commit()
    db.refresh(ingredient)
    return ingredient


@pytest.fixture
def sample_ingredient_2(db: Session) -> Ingredient:
    """Crée un second ingrédient de test."""
    ingredient = Ingredient(nom="Oeufs", unite="pièce", categorie="Crèmerie")
    db.add(ingredient)
    db.commit()
    db.refresh(ingredient)
    return ingredient


@pytest.fixture
def sample_liste_courses(db: Session) -> "ListeCourses":
    """Crée une liste de courses de test."""
    from src.core.models import ListeCourses

    liste = ListeCourses(nom="Liste Test", archivee=False)
    db.add(liste)
    db.commit()
    db.refresh(liste)
    return liste


@pytest.fixture
def sample_article_courses(
    db: Session, sample_ingredient: Ingredient, sample_liste_courses
) -> ArticleCourses:
    """Crée un article de courses de test."""
    article = ArticleCourses(
        liste_id=sample_liste_courses.id,
        ingredient_id=sample_ingredient.id,
        quantite_necessaire=2.0,
        priorite="haute",
        achete=False,
        rayon_magasin="Fruits & Légumes",
        notes="Bio si possible",
        suggere_par_ia=False,
    )
    db.add(article)
    db.commit()
    db.refresh(article)
    return article


@pytest.fixture
def sample_modele_courses(db: Session) -> ModeleCourses:
    """Crée un modèle de courses de test."""
    modele = ModeleCourses(
        nom="Modèle Petit-déjeuner", description="Articles pour le petit-déjeuner", actif=True
    )
    db.add(modele)
    db.commit()
    db.refresh(modele)
    return modele


@pytest.fixture
def sample_article_modele(
    db: Session, sample_modele_courses: ModeleCourses, sample_ingredient: Ingredient
) -> ArticleModele:
    """Crée un article de modèle de test."""
    article = ArticleModele(
        modele_id=sample_modele_courses.id,
        ingredient_id=sample_ingredient.id,
        nom_article="Tomates",
        quantite=1.5,
        unite="kg",
        rayon_magasin="Fruits & Légumes",
        priorite="haute",
        ordre=0,
    )
    db.add(article)
    db.commit()
    db.refresh(article)
    return article


# ═══════════════════════════════════════════════════════════
# TESTS CRÉATION SERVICE
# ═══════════════════════════════════════════════════════════


class TestServiceCoursesCreation:
    """Tests de création du service."""

    def test_creation_service(self, mock_client_ia):
        """Test création du service."""
        with patch("src.services.courses.service.obtenir_client_ia", return_value=mock_client_ia):
            service = ServiceCourses()
            assert service is not None
            assert service.model == ArticleCourses
            assert service.cache_ttl == 1800

    def test_factory_obtenir_service_courses(self, mock_client_ia):
        """Test factory function retourne instance."""
        with patch("src.services.courses.service.obtenir_client_ia", return_value=mock_client_ia):
            with patch("src.services.courses.service._service_courses", None):
                service = obtenir_service_courses()
                assert service is not None
                assert isinstance(service, ServiceCourses)

    def test_factory_singleton(self, mock_client_ia):
        """Test factory retourne même instance."""
        with patch("src.services.courses.service.obtenir_client_ia", return_value=mock_client_ia):
            with patch("src.services.courses.service._service_courses", None):
                service1 = obtenir_service_courses()
                service2 = obtenir_service_courses()
                assert service1 is service2

    def test_alias_get_courses_service(self, mock_client_ia):
        """Test alias anglais."""
        with patch("src.services.courses.service.obtenir_client_ia", return_value=mock_client_ia):
            with patch("src.services.courses.service._service_courses", None):
                service = get_courses_service()
                assert isinstance(service, ServiceCourses)


# ═══════════════════════════════════════════════════════════
# TESTS OBTENIR LISTE COURSES
# ═══════════════════════════════════════════════════════════


class TestObtenirlListeCourses:
    """Tests pour obtenir_liste_courses."""

    def test_liste_vide(self, service_courses, patch_db_context):
        """Test récupération liste vide."""
        result = service_courses.obtenir_liste_courses()
        assert result == []

    def test_liste_avec_articles(
        self, service_courses, patch_db_context, sample_article_courses, sample_ingredient
    ):
        """Test récupération liste avec articles."""
        result = service_courses.obtenir_liste_courses()
        assert len(result) == 1
        assert result[0]["ingredient_nom"] == "Tomates"
        assert result[0]["quantite_necessaire"] == 2.0
        assert result[0]["priorite"] == "haute"
        assert result[0]["achete"] is False

    def test_liste_exclut_achetes_par_defaut(
        self,
        db: Session,
        service_courses,
        patch_db_context,
        sample_ingredient,
        sample_liste_courses,
    ):
        """Test que les articles achetés sont exclus par défaut."""
        # Créer un article acheté
        article_achete = ArticleCourses(
            liste_id=sample_liste_courses.id,
            ingredient_id=sample_ingredient.id,
            quantite_necessaire=1.0,
            priorite="moyenne",
            achete=True,
            rayon_magasin="Test",
        )
        db.add(article_achete)
        db.commit()

        result = service_courses.obtenir_liste_courses(achetes=False)
        assert len(result) == 0

    def test_liste_inclut_achetes(
        self,
        db: Session,
        service_courses,
        patch_db_context,
        sample_ingredient,
        sample_liste_courses,
    ):
        """Test inclusion des articles achetés."""
        # Créer un article acheté
        article = ArticleCourses(
            liste_id=sample_liste_courses.id,
            ingredient_id=sample_ingredient.id,
            quantite_necessaire=1.0,
            priorite="moyenne",
            achete=True,
            rayon_magasin="Test",
        )
        db.add(article)
        db.commit()

        result = service_courses.obtenir_liste_courses(achetes=True)
        assert len(result) == 1
        assert result[0]["achete"] is True

    def test_filtre_priorite_haute(
        self,
        db: Session,
        service_courses,
        patch_db_context,
        sample_ingredient,
        sample_ingredient_2,
        sample_liste_courses,
    ):
        """Test filtre par priorité haute."""
        # Créer articles avec différentes priorités
        article_haute = ArticleCourses(
            liste_id=sample_liste_courses.id,
            ingredient_id=sample_ingredient.id,
            quantite_necessaire=1.0,
            priorite="haute",
            achete=False,
            rayon_magasin="Test",
        )
        article_moyenne = ArticleCourses(
            liste_id=sample_liste_courses.id,
            ingredient_id=sample_ingredient_2.id,
            quantite_necessaire=1.0,
            priorite="moyenne",
            achete=False,
            rayon_magasin="Test",
        )
        db.add_all([article_haute, article_moyenne])
        db.commit()

        result = service_courses.obtenir_liste_courses(priorite="haute")
        assert len(result) == 1
        assert result[0]["priorite"] == "haute"

    def test_filtre_priorite_moyenne(
        self,
        db: Session,
        service_courses,
        patch_db_context,
        sample_ingredient,
        sample_ingredient_2,
        sample_liste_courses,
    ):
        """Test filtre par priorité moyenne."""
        article_haute = ArticleCourses(
            liste_id=sample_liste_courses.id,
            ingredient_id=sample_ingredient.id,
            quantite_necessaire=1.0,
            priorite="haute",
            achete=False,
            rayon_magasin="Test",
        )
        article_moyenne = ArticleCourses(
            liste_id=sample_liste_courses.id,
            ingredient_id=sample_ingredient_2.id,
            quantite_necessaire=1.0,
            priorite="moyenne",
            achete=False,
            rayon_magasin="Test",
        )
        db.add_all([article_haute, article_moyenne])
        db.commit()

        result = service_courses.obtenir_liste_courses(priorite="moyenne")
        assert len(result) == 1
        assert result[0]["priorite"] == "moyenne"

    def test_alias_get_liste_courses(self, service_courses, patch_db_context):
        """Test alias get_liste_courses."""
        result = service_courses.get_liste_courses()
        assert result == []

    def test_structure_dict_retour(
        self, service_courses, patch_db_context, sample_article_courses, sample_ingredient
    ):
        """Test structure du dictionnaire retourné."""
        result = service_courses.obtenir_liste_courses()
        assert len(result) == 1

        article = result[0]
        expected_keys = [
            "id",
            "ingredient_id",
            "ingredient_nom",
            "quantite_necessaire",
            "unite",
            "priorite",
            "achete",
            "rayon_magasin",
            "magasin_cible",
            "notes",
            "suggere_par_ia",
        ]
        for key in expected_keys:
            assert key in article, f"Clé manquante: {key}"


# ═══════════════════════════════════════════════════════════
# TESTS SUGGESTIONS IA
# ═══════════════════════════════════════════════════════════


class TestSuggestionsIA:
    """Tests pour generer_suggestions_ia_depuis_inventaire."""

    def test_suggestions_inventaire_vide(self, service_courses, patch_db_context):
        """Test suggestions avec inventaire vide."""
        with patch("src.services.inventaire.get_inventaire_service") as mock_get_inv:
            mock_inv = MagicMock()
            mock_inv.get_inventaire_complet.return_value = []
            mock_get_inv.return_value = mock_inv

            result = service_courses.generer_suggestions_ia_depuis_inventaire()
            assert result == []

    def test_suggestions_service_inventaire_indisponible(self, service_courses, patch_db_context):
        """Test suggestions quand service inventaire indisponible."""
        with patch("src.services.inventaire.get_inventaire_service") as mock_get_inv:
            mock_get_inv.return_value = None

            result = service_courses.generer_suggestions_ia_depuis_inventaire()
            assert result == []

    def test_suggestions_avec_inventaire(self, service_courses, patch_db_context, mock_client_ia):
        """Test suggestions avec inventaire contenant des articles."""
        mock_inventaire = [
            {"nom": "Tomates", "quantite": 1, "unite": "kg"},
            {"nom": "Lait", "quantite": 0.5, "unite": "L"},
        ]

        mock_suggestions = [
            SuggestionCourses(
                nom="Lait", quantite=1.0, unite="L", priorite="haute", rayon="Crèmerie"
            ),
        ]

        with patch("src.services.inventaire.get_inventaire_service") as mock_get_inv:
            mock_inv = MagicMock()
            mock_inv.get_inventaire_complet.return_value = mock_inventaire
            mock_inv.build_inventory_summary.return_value = "Inventaire: Tomates, Lait"
            mock_get_inv.return_value = mock_inv

            with patch.object(
                service_courses, "call_with_list_parsing_sync", return_value=mock_suggestions
            ):
                result = service_courses.generer_suggestions_ia_depuis_inventaire()
                assert len(result) == 1
                assert result[0].nom == "Lait"

    def test_suggestions_erreur_parsing(self, service_courses, patch_db_context):
        """Test gestion erreur de parsing."""
        mock_inventaire = [{"nom": "Test", "quantite": 1}]

        with patch("src.services.inventaire.get_inventaire_service") as mock_get_inv:
            mock_inv = MagicMock()
            mock_inv.get_inventaire_complet.return_value = mock_inventaire
            mock_inv.build_inventory_summary.return_value = "Test"
            mock_get_inv.return_value = mock_inv

            with patch.object(
                service_courses,
                "call_with_list_parsing_sync",
                side_effect=KeyError("champ manquant"),
            ):
                result = service_courses.generer_suggestions_ia_depuis_inventaire()
                assert result == []

    def test_suggestions_erreur_generique(self, service_courses, patch_db_context):
        """Test gestion erreur générique."""
        mock_inventaire = [{"nom": "Test", "quantite": 1}]

        with patch("src.services.inventaire.get_inventaire_service") as mock_get_inv:
            mock_inv = MagicMock()
            mock_inv.get_inventaire_complet.return_value = mock_inventaire
            mock_inv.build_inventory_summary.return_value = "Test"
            mock_get_inv.return_value = mock_inv

            with patch.object(
                service_courses, "call_with_list_parsing_sync", side_effect=Exception("Erreur test")
            ):
                result = service_courses.generer_suggestions_ia_depuis_inventaire()
                assert result == []


# ═══════════════════════════════════════════════════════════
# TESTS MODÈLES COURSES
# ═══════════════════════════════════════════════════════════


class TestModelesGestion:
    """Tests pour la gestion des modèles."""

    def test_obtenir_modeles_vide(self, service_courses, patch_db_context):
        """Test récupération modèles vides."""
        result = service_courses.obtenir_modeles()
        assert result == []

    def test_obtenir_modeles_avec_contenu(
        self, service_courses, patch_db_context, sample_modele_courses, sample_article_modele
    ):
        """Test récupération modèles avec articles."""
        result = service_courses.obtenir_modeles()
        assert len(result) == 1
        assert result[0]["nom"] == "Modèle Petit-déjeuner"
        assert result[0]["description"] == "Articles pour le petit-déjeuner"
        assert len(result[0]["articles"]) == 1

    def test_obtenir_modeles_filtre_utilisateur(
        self, db: Session, service_courses, patch_db_context
    ):
        """Test filtre par utilisateur_id."""
        modele1 = ModeleCourses(nom="Modèle User1", utilisateur_id="user1", actif=True)
        modele2 = ModeleCourses(nom="Modèle User2", utilisateur_id="user2", actif=True)
        db.add_all([modele1, modele2])
        db.commit()

        result = service_courses.obtenir_modeles(utilisateur_id="user1")
        assert len(result) == 1
        assert result[0]["nom"] == "Modèle User1"

    def test_obtenir_modeles_exclut_inactifs(self, db: Session, service_courses, patch_db_context):
        """Test exclusion modèles inactifs."""
        modele_actif = ModeleCourses(nom="Actif", actif=True)
        modele_inactif = ModeleCourses(nom="Inactif", actif=False)
        db.add_all([modele_actif, modele_inactif])
        db.commit()

        result = service_courses.obtenir_modeles()
        assert len(result) == 1
        assert result[0]["nom"] == "Actif"

    def test_alias_get_modeles(self, service_courses, patch_db_context):
        """Test alias get_modeles."""
        result = service_courses.get_modeles()
        assert result == []

    def test_creer_modele_simple(self, db: Session, service_courses, patch_db_context):
        """Test création modèle simple."""
        articles = [
            {"nom": "Article1", "quantite": 1.0, "unite": "pièce"},
            {"nom": "Article2", "quantite": 2.0, "unite": "kg"},
        ]

        modele_id = service_courses.creer_modele(
            nom="Nouveau modèle", articles=articles, description="Description test"
        )

        assert modele_id is not None
        assert modele_id > 0

        # Vérifier en DB
        modele = db.query(ModeleCourses).filter_by(id=modele_id).first()
        assert modele is not None
        assert modele.nom == "Nouveau modèle"
        assert len(modele.articles) == 2

    def test_creer_modele_avec_ingredient_id(
        self, db: Session, service_courses, patch_db_context, sample_ingredient
    ):
        """Test création modèle avec ingredient_id."""
        articles = [
            {"ingredient_id": sample_ingredient.id, "nom": "Tomates", "quantite": 1.5},
        ]

        modele_id = service_courses.creer_modele(nom="Avec Ingredient", articles=articles)

        modele = db.query(ModeleCourses).filter_by(id=modele_id).first()
        assert modele.articles[0].ingredient_id == sample_ingredient.id

    def test_creer_modele_avec_utilisateur(self, db: Session, service_courses, patch_db_context):
        """Test création modèle avec utilisateur_id."""
        modele_id = service_courses.creer_modele(
            nom="Modèle personnel",
            articles=[{"nom": "Test", "quantite": 1}],
            utilisateur_id="user123",
        )

        modele = db.query(ModeleCourses).filter_by(id=modele_id).first()
        assert modele.utilisateur_id == "user123"

    def test_alias_create_modele(self, service_courses, patch_db_context):
        """Test alias create_modele."""
        modele_id = service_courses.create_modele(
            nom="Alias test", articles=[{"nom": "X", "quantite": 1}]
        )
        assert modele_id > 0

    def test_supprimer_modele_existant(
        self, service_courses, patch_db_context, sample_modele_courses
    ):
        """Test suppression modèle existant."""
        result = service_courses.supprimer_modele(sample_modele_courses.id)
        assert result is True

    def test_supprimer_modele_inexistant(self, service_courses, patch_db_context):
        """Test suppression modèle inexistant."""
        result = service_courses.supprimer_modele(99999)
        assert result is False

    def test_alias_delete_modele(self, service_courses, patch_db_context, sample_modele_courses):
        """Test alias delete_modele."""
        result = service_courses.delete_modele(sample_modele_courses.id)
        assert result is True


# ═══════════════════════════════════════════════════════════
# TESTS APPLIQUER MODÈLES
# ═══════════════════════════════════════════════════════════


class TestAppliquerModele:
    """Tests pour appliquer_modele."""

    def test_appliquer_modele_inexistant(self, service_courses, patch_db_context):
        """Test application modèle inexistant."""
        result = service_courses.appliquer_modele(99999)
        assert result == []

    def test_appliquer_modele_avec_ingredient(
        self,
        db: Session,
        service_courses,
        patch_db_context,
        sample_modele_courses,
        sample_article_modele,
    ):
        """Test application modèle avec ingrédient existant."""
        # Le mock de BaseService.create doit être configuré
        with patch.object(service_courses, "create", return_value=1) as mock_create:
            result = service_courses.appliquer_modele(sample_modele_courses.id)
            assert len(result) == 1
            mock_create.assert_called_once()

    def test_appliquer_modele_cree_ingredient_si_absent(
        self, db: Session, service_courses, patch_db_context
    ):
        """Test création ingrédient si non trouvé."""
        # Créer modèle avec article sans ingredient_id
        modele = ModeleCourses(nom="Test", actif=True)
        db.add(modele)
        db.flush()

        article = ArticleModele(
            modele_id=modele.id,
            nom_article="Nouvel ingredient",
            quantite=1.0,
            unite="kg",
            rayon_magasin="Test",
            priorite="moyenne",
            ordre=0,
        )
        db.add(article)
        db.commit()

        with patch.object(service_courses, "create", return_value=100):
            result = service_courses.appliquer_modele(modele.id)
            assert len(result) == 1

            # Vérifier que l'ingrédient a été créé
            ingredient = db.query(Ingredient).filter_by(nom="Nouvel ingredient").first()
            assert ingredient is not None
