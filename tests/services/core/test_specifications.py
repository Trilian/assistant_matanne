"""Tests pour le package Specifications — Filtres composables."""

from datetime import date, timedelta
from unittest.mock import MagicMock, patch

import pytest

from src.services.core.specifications.base import (
    AndSpecification,
    FalseSpecification,
    NotSpecification,
    OrSpecification,
    Specification,
    TrueSpecification,
    combine_and,
    combine_or,
    filter_by_spec,
)

# ═══════════════════════════════════════════════════════════
# FIXTURES ET MOCKS
# ═══════════════════════════════════════════════════════════


class MockEntity:
    """Entité mock pour les tests."""

    def __init__(self, value: int, name: str = "test"):
        self.value = value
        self.name = name


class ValueGreaterThanSpec(Specification[MockEntity]):
    """Spec de test: value > threshold."""

    def __init__(self, threshold: int):
        self.threshold = threshold

    def is_satisfied_by(self, entity: MockEntity) -> bool:
        return entity.value > self.threshold

    def to_query(self, query):
        return query  # Mock


class NameStartsWithSpec(Specification[MockEntity]):
    """Spec de test: name commence par prefix."""

    def __init__(self, prefix: str):
        self.prefix = prefix

    def is_satisfied_by(self, entity: MockEntity) -> bool:
        return entity.name.startswith(self.prefix)

    def to_query(self, query):
        return query  # Mock


# ═══════════════════════════════════════════════════════════
# TESTS SPECIFICATIONS DE BASE
# ═══════════════════════════════════════════════════════════


class TestSpecificationBase:
    """Tests des spécifications de base."""

    def test_simple_spec_satisfied(self):
        """Spec simple satisfaite."""
        spec = ValueGreaterThanSpec(5)
        entity = MockEntity(value=10)

        assert spec.is_satisfied_by(entity) is True

    def test_simple_spec_not_satisfied(self):
        """Spec simple non satisfaite."""
        spec = ValueGreaterThanSpec(5)
        entity = MockEntity(value=3)

        assert spec.is_satisfied_by(entity) is False


class TestAndSpecification:
    """Tests de la composition AND."""

    def test_and_both_satisfied(self):
        """AND: les deux specs satisfaites."""
        spec = ValueGreaterThanSpec(5) & NameStartsWithSpec("t")
        entity = MockEntity(value=10, name="test")

        assert spec.is_satisfied_by(entity) is True

    def test_and_one_not_satisfied(self):
        """AND: une spec non satisfaite."""
        spec = ValueGreaterThanSpec(5) & NameStartsWithSpec("x")
        entity = MockEntity(value=10, name="test")

        assert spec.is_satisfied_by(entity) is False

    def test_and_none_satisfied(self):
        """AND: aucune spec satisfaite."""
        spec = ValueGreaterThanSpec(100) & NameStartsWithSpec("x")
        entity = MockEntity(value=10, name="test")

        assert spec.is_satisfied_by(entity) is False

    def test_and_repr(self):
        """AND: représentation lisible."""
        spec = ValueGreaterThanSpec(5) & NameStartsWithSpec("t")
        repr_str = repr(spec)

        assert "AND" in repr_str


class TestOrSpecification:
    """Tests de la composition OR."""

    def test_or_both_satisfied(self):
        """OR: les deux specs satisfaites."""
        spec = ValueGreaterThanSpec(5) | NameStartsWithSpec("t")
        entity = MockEntity(value=10, name="test")

        assert spec.is_satisfied_by(entity) is True

    def test_or_one_satisfied(self):
        """OR: une spec satisfaite."""
        spec = ValueGreaterThanSpec(100) | NameStartsWithSpec("t")
        entity = MockEntity(value=10, name="test")

        assert spec.is_satisfied_by(entity) is True

    def test_or_none_satisfied(self):
        """OR: aucune spec satisfaite."""
        spec = ValueGreaterThanSpec(100) | NameStartsWithSpec("x")
        entity = MockEntity(value=10, name="test")

        assert spec.is_satisfied_by(entity) is False


class TestNotSpecification:
    """Tests de la négation NOT."""

    def test_not_inverts_true(self):
        """NOT: inverse True en False."""
        spec = ~ValueGreaterThanSpec(5)
        entity = MockEntity(value=10)

        assert spec.is_satisfied_by(entity) is False

    def test_not_inverts_false(self):
        """NOT: inverse False en True."""
        spec = ~ValueGreaterThanSpec(100)
        entity = MockEntity(value=10)

        assert spec.is_satisfied_by(entity) is True


class TestUtilitySpecifications:
    """Tests des specs utilitaires."""

    def test_true_spec_always_true(self):
        """TrueSpecification toujours True."""
        spec = TrueSpecification()
        entity = MockEntity(value=0)

        assert spec.is_satisfied_by(entity) is True

    def test_false_spec_always_false(self):
        """FalseSpecification toujours False."""
        spec = FalseSpecification()
        entity = MockEntity(value=100)

        assert spec.is_satisfied_by(entity) is False


# ═══════════════════════════════════════════════════════════
# TESTS HELPERS
# ═══════════════════════════════════════════════════════════


class TestCombineHelpers:
    """Tests des helpers combine_and et combine_or."""

    def test_combine_and_empty(self):
        """combine_and sans args retourne TrueSpec."""
        spec = combine_and()
        entity = MockEntity(value=0)

        assert spec.is_satisfied_by(entity) is True

    def test_combine_and_multiple(self):
        """combine_and avec plusieurs specs."""
        spec = combine_and(
            ValueGreaterThanSpec(5),
            ValueGreaterThanSpec(8),
            NameStartsWithSpec("t"),
        )
        entity = MockEntity(value=10, name="test")

        assert spec.is_satisfied_by(entity) is True

    def test_combine_or_empty(self):
        """combine_or sans args retourne FalseSpec."""
        spec = combine_or()
        entity = MockEntity(value=100)

        assert spec.is_satisfied_by(entity) is False

    def test_combine_or_multiple(self):
        """combine_or avec plusieurs specs."""
        spec = combine_or(
            ValueGreaterThanSpec(100),  # False
            NameStartsWithSpec("x"),  # False
            NameStartsWithSpec("t"),  # True
        )
        entity = MockEntity(value=10, name="test")

        assert spec.is_satisfied_by(entity) is True


class TestFilterBySpec:
    """Tests du helper filter_by_spec."""

    def test_filter_items(self):
        """Filtre une liste avec une spec."""
        items = [
            MockEntity(value=3),
            MockEntity(value=7),
            MockEntity(value=12),
            MockEntity(value=2),
        ]
        spec = ValueGreaterThanSpec(5)

        result = filter_by_spec(items, spec)

        assert len(result) == 2
        assert all(e.value > 5 for e in result)

    def test_filter_empty_list(self):
        """Filtre une liste vide."""
        result = filter_by_spec([], ValueGreaterThanSpec(5))
        assert result == []

    def test_filter_no_match(self):
        """Filtre sans correspondance."""
        items = [MockEntity(value=1), MockEntity(value=2)]
        result = filter_by_spec(items, ValueGreaterThanSpec(100))
        assert result == []


# ═══════════════════════════════════════════════════════════
# TESTS SPECS RECETTES (avec mocks)
# ═══════════════════════════════════════════════════════════


class TestRecetteSpecifications:
    """Tests des specifications de recettes."""

    def test_recette_rapide_spec(self):
        """RecetteRapideSpec: temps total < max."""
        from src.services.core.specifications.recettes import RecetteRapideSpec

        # Mock recette
        recette = MagicMock()
        recette.temps_preparation = 15
        recette.temps_cuisson = 10

        spec = RecetteRapideSpec(temps_max=30)
        assert spec.is_satisfied_by(recette) is True

        spec2 = RecetteRapideSpec(temps_max=20)
        assert spec2.is_satisfied_by(recette) is False

    def test_recette_par_type_spec(self):
        """RecetteParTypeSpec: type_repas correspondant."""
        from src.services.core.specifications.recettes import RecetteParTypeSpec

        recette = MagicMock()
        recette.type_repas = "dîner"

        spec = RecetteParTypeSpec(type_repas="dîner")
        assert spec.is_satisfied_by(recette) is True

        spec2 = RecetteParTypeSpec(type_repas="déjeuner")
        assert spec2.is_satisfied_by(recette) is False

    def test_recette_compatible_bebe_spec(self):
        """RecetteCompatibleBebeSpec: compatible_bebe True."""
        from src.services.core.specifications.recettes import RecetteCompatibleBebeSpec

        recette_bebe = MagicMock()
        recette_bebe.compatible_bebe = True

        recette_adulte = MagicMock()
        recette_adulte.compatible_bebe = False

        spec = RecetteCompatibleBebeSpec(compatible=True)
        assert spec.is_satisfied_by(recette_bebe) is True
        assert spec.is_satisfied_by(recette_adulte) is False


# ═══════════════════════════════════════════════════════════
# TESTS SPECS INVENTAIRE (avec mocks)
# ═══════════════════════════════════════════════════════════


class TestInventaireSpecifications:
    """Tests des specifications d'inventaire."""

    def test_article_stock_bas(self):
        """ArticleStockBas: quantité <= quantité_min."""
        from src.services.core.specifications.inventaire import ArticleStockBas

        article_bas = MagicMock()
        article_bas.quantite = 2
        article_bas.quantite_min = 5

        article_ok = MagicMock()
        article_ok.quantite = 10
        article_ok.quantite_min = 5

        spec = ArticleStockBas()
        assert spec.is_satisfied_by(article_bas) is True
        assert spec.is_satisfied_by(article_ok) is False

    def test_article_peremption_proche(self):
        """ArticlePeremptionProcheSpec: date < aujourd'hui + jours."""
        from src.services.core.specifications.inventaire import ArticlePeremptionProcheSpec

        article_proche = MagicMock()
        article_proche.date_peremption = date.today() + timedelta(days=3)

        article_loin = MagicMock()
        article_loin.date_peremption = date.today() + timedelta(days=30)

        spec = ArticlePeremptionProcheSpec(jours_avant=7)
        assert spec.is_satisfied_by(article_proche) is True
        assert spec.is_satisfied_by(article_loin) is False

    def test_article_par_emplacement(self):
        """ArticleParEmplacementSpec: emplacement correspondant."""
        from src.services.core.specifications.inventaire import ArticleParEmplacementSpec

        article_frigo = MagicMock()
        article_frigo.emplacement = "Frigo"

        article_placard = MagicMock()
        article_placard.emplacement = "Placard"

        spec = ArticleParEmplacementSpec(emplacement="Frigo")
        assert spec.is_satisfied_by(article_frigo) is True
        assert spec.is_satisfied_by(article_placard) is False


# ═══════════════════════════════════════════════════════════
# TESTS COMPOSITION COMPLEXE
# ═══════════════════════════════════════════════════════════


class TestComplexComposition:
    """Tests de compositions complexes."""

    def test_three_level_composition(self):
        """Composition à 3 niveaux: (A & B) | C."""
        a = ValueGreaterThanSpec(5)
        b = NameStartsWithSpec("t")
        c = ValueGreaterThanSpec(100)

        spec = (a & b) | c

        # A & B satisfait
        e1 = MockEntity(value=10, name="test")
        assert spec.is_satisfied_by(e1) is True

        # C satisfait
        e2 = MockEntity(value=150, name="xxx")
        assert spec.is_satisfied_by(e2) is True

        # Aucun satisfait
        e3 = MockEntity(value=3, name="xxx")
        assert spec.is_satisfied_by(e3) is False

    def test_not_combined_with_and(self):
        """NOT combiné avec AND: A & ~B."""
        a = ValueGreaterThanSpec(5)
        b = NameStartsWithSpec("x")

        spec = a & ~b  # value > 5 AND NOT name.startswith("x")

        e1 = MockEntity(value=10, name="test")  # True
        assert spec.is_satisfied_by(e1) is True

        e2 = MockEntity(value=10, name="xxx")  # False (name starts with x)
        assert spec.is_satisfied_by(e2) is False
