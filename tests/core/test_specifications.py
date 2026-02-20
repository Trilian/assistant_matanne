"""
Tests pour src/core/specifications.py et Repository v2 avec specs.
"""

import pytest
from sqlalchemy import Column, Integer, String, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker

from src.core.repository import Repository
from src.core.specifications import (
    Et,
    Non,
    Ou,
    Spec,
    Specification,
    contient,
    entre,
    limite,
    ordre_par,
    paginer,
    par_champ,
    par_champs,
)

# ═══════════════════════════════════════════════════════════
# FIXTURES — DB en mémoire
# ═══════════════════════════════════════════════════════════


class Base(DeclarativeBase):
    pass


class Produit(Base):
    __tablename__ = "produits"

    id: Mapped[int] = mapped_column(primary_key=True)
    nom: Mapped[str] = mapped_column(String(100))
    prix: Mapped[int] = mapped_column(Integer, default=0)
    categorie: Mapped[str] = mapped_column(String(50), default="")
    actif: Mapped[bool] = mapped_column(default=True)


@pytest.fixture
def db_session():
    """Session SQLite en mémoire avec données de test."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()

    # Données de test
    produits = [
        Produit(id=1, nom="Tarte aux pommes", prix=8, categorie="dessert", actif=True),
        Produit(id=2, nom="Soupe de légumes", prix=5, categorie="entrée", actif=True),
        Produit(id=3, nom="Tarte au citron", prix=10, categorie="dessert", actif=True),
        Produit(id=4, nom="Salade niçoise", prix=12, categorie="entrée", actif=False),
        Produit(id=5, nom="Gâteau chocolat", prix=15, categorie="dessert", actif=True),
    ]
    session.add_all(produits)
    session.commit()

    yield session
    session.close()


@pytest.fixture
def repo(db_session):
    """Repository Produit."""
    return Repository(db_session, Produit)


# ═══════════════════════════════════════════════════════════
# TESTS SPECIFICATIONS DE BASE
# ═══════════════════════════════════════════════════════════


class TestSpec:
    """Tests pour Spec (spécification lambda)."""

    def test_spec_par_champ(self, repo):
        """Test filtre par champ simple."""
        spec = par_champ("categorie", "dessert")
        result = repo.lister(spec=spec)
        assert len(result) == 3
        assert all(p.categorie == "dessert" for p in result)

    def test_spec_contient(self, repo):
        """Test recherche textuelle ILIKE."""
        spec = contient("nom", "tarte")
        result = repo.lister(spec=spec)
        assert len(result) == 2
        assert all("tarte" in p.nom.lower() for p in result)

    def test_spec_entre(self, repo):
        """Test filtre par intervalle."""
        spec = entre("prix", 5, 10)
        result = repo.lister(spec=spec)
        assert all(5 <= p.prix <= 10 for p in result)

    def test_spec_par_champs(self, repo):
        """Test filtre multi-champs."""
        spec = par_champs(categorie="dessert", actif=True)
        result = repo.lister(spec=spec)
        assert len(result) == 3
        assert all(p.categorie == "dessert" and p.actif for p in result)

    def test_spec_limite(self, repo):
        """Test limite."""
        spec = limite(2)
        result = repo.lister(spec=spec)
        assert len(result) == 2

    def test_spec_paginer(self, repo):
        """Test pagination."""
        spec = paginer(page=1, par_page=2)
        result = repo.lister(spec=spec)
        assert len(result) == 2

    def test_spec_ordre_par_asc(self, repo):
        """Test tri ascendant."""
        spec = ordre_par("prix")
        result = repo.lister(spec=spec)
        prix = [p.prix for p in result]
        assert prix == sorted(prix)

    def test_spec_ordre_par_desc(self, repo):
        """Test tri descendant."""
        spec = ordre_par("prix", descendant=True)
        result = repo.lister(spec=spec)
        prix = [p.prix for p in result]
        assert prix == sorted(prix, reverse=True)


# ═══════════════════════════════════════════════════════════
# TESTS COMPOSITION
# ═══════════════════════════════════════════════════════════


class TestComposition:
    """Tests pour la composition de spécifications."""

    def test_et_composition(self, repo):
        """Test composition ET."""
        spec = par_champ("categorie", "dessert") & par_champ("actif", True)
        result = repo.lister(spec=spec)
        assert len(result) == 3
        assert all(p.categorie == "dessert" and p.actif for p in result)

    def test_et_avec_limite(self, repo):
        """Test ET avec limite."""
        spec = par_champ("categorie", "dessert") & limite(1)
        result = repo.lister(spec=spec)
        assert len(result) == 1
        assert result[0].categorie == "dessert"

    def test_triple_composition(self, repo):
        """Test trois spécifications composées."""
        spec = par_champ("actif", True) & contient("nom", "tarte") & ordre_par("prix")
        result = repo.lister(spec=spec)
        assert len(result) == 2
        assert result[0].prix <= result[1].prix

    def test_spec_repr(self):
        """Test repr des spécifications."""
        spec = par_champ("actif", True) & contient("nom", "test")
        assert "&" in repr(spec)


# ═══════════════════════════════════════════════════════════
# TESTS REPOSITORY V2 — SPECS
# ═══════════════════════════════════════════════════════════


class TestRepositorySpec:
    """Tests pour Repository.lister(spec=) et compter(spec=)."""

    def test_lister_avec_spec(self, repo):
        """Test lister avec spécification."""
        spec = par_champ("categorie", "entrée")
        result = repo.lister(spec=spec)
        assert len(result) == 2

    def test_compter_avec_spec(self, repo):
        """Test compter avec spécification."""
        spec = par_champ("actif", True)
        count = repo.compter(spec=spec)
        assert count == 4

    def test_lister_spec_et_filtre_coexistent(self, repo):
        """Test spec + filtre classique (les deux appliqués)."""
        spec = par_champ("actif", True)
        result = repo.lister(spec=spec, filtre={"categorie": "dessert"})
        assert len(result) == 3

    def test_premier(self, repo):
        """Test premier()."""
        spec = par_champ("categorie", "dessert") & ordre_par("prix")
        result = repo.premier(spec=spec)
        assert result is not None
        assert result.categorie == "dessert"
        assert result.prix == 8  # Moins cher

    def test_premier_aucun_resultat(self, repo):
        """Test premier() quand rien ne correspond."""
        spec = par_champ("categorie", "inexistant")
        result = repo.premier(spec=spec)
        assert result is None

    def test_creer_en_masse(self, repo, db_session):
        """Test création en masse."""
        nouveaux = [Produit(nom=f"Produit {i}", prix=i, categorie="test") for i in range(10)]
        result = repo.creer_en_masse(nouveaux)
        assert len(result) == 10
        assert repo.compter(filtre={"categorie": "test"}) == 10

    def test_supprimer_par_spec(self, repo):
        """Test suppression par spécification."""
        count = repo.supprimer_par_spec(par_champ("actif", False))
        assert count == 1
        assert repo.compter(filtre={"actif": False}) == 0


# ═══════════════════════════════════════════════════════════
# TESTS UNIT OF WORK
# ═══════════════════════════════════════════════════════════


class TestUnitOfWork:
    """Tests pour UnitOfWork."""

    def test_uow_with_session(self, db_session):
        """Test UoW avec session existante."""
        from src.core.unit_of_work import UnitOfWork

        with UnitOfWork(session=db_session) as uow:
            repo = uow.repository(Produit)
            produits = repo.lister()
            assert len(produits) == 5

    def test_uow_commit_auto(self, db_session):
        """Test commit automatique en sortie de with."""
        from src.core.unit_of_work import UnitOfWork

        with UnitOfWork(session=db_session) as uow:
            repo = uow.repository(Produit)
            repo.creer(Produit(nom="Nouveau", prix=20, categorie="test"))

        # Vérifie que le commit a persisté
        count = db_session.query(Produit).filter(Produit.nom == "Nouveau").count()
        assert count == 1

    def test_uow_rollback_on_exception(self, db_session):
        """Test rollback automatique sur exception."""
        from src.core.unit_of_work import UnitOfWork

        initial_count = db_session.query(Produit).count()

        try:
            with UnitOfWork(session=db_session) as uow:
                repo = uow.repository(Produit)
                repo.creer(Produit(nom="Ghost", prix=99, categorie="test"))
                raise ValueError("Erreur simulée")
        except ValueError:
            pass

        # Le produit ne doit pas être persisté (rollback)
        assert db_session.query(Produit).count() == initial_count

    def test_uow_multiple_repositories(self, db_session):
        """Test accès à plusieurs repositories."""
        from src.core.unit_of_work import UnitOfWork

        with UnitOfWork(session=db_session) as uow:
            repo1 = uow.repository(Produit)
            repo2 = uow.repository(Produit)
            # Mêmes instances réutilisées
            assert repo1 is repo2

    def test_uow_session_property(self, db_session):
        """Test accès à la session."""
        from src.core.unit_of_work import UnitOfWork

        with UnitOfWork(session=db_session) as uow:
            assert uow.session is db_session

    def test_uow_session_sans_contexte(self):
        """Test erreur si session accédée hors contexte."""
        from src.core.unit_of_work import UnitOfWork

        uow = UnitOfWork()
        with pytest.raises(RuntimeError, match="non initialisé"):
            _ = uow.session

    def test_uow_flush(self, db_session):
        """Test flush explicite."""
        from src.core.unit_of_work import UnitOfWork

        with UnitOfWork(session=db_session) as uow:
            repo = uow.repository(Produit)
            produit = Produit(nom="Flush Test", prix=1, categorie="test")
            repo.creer(produit)
            uow.flush()
            assert produit.id is not None
