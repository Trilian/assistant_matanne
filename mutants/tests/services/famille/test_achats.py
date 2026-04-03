"""
Tests pour src/services/famille/achats.py — ServiceAchatsFamille.

Couvre:
- Listage (global, par catégorie, par personne, à revendre)
- Création et marquage acheté / vendu
- Statistiques et urgents
- Filtres a_revendre
- Factory singleton
"""

from __future__ import annotations

from datetime import date

import pytest
from sqlalchemy.orm import Session

from src.core.models import AchatFamille
from src.services.famille.achats import ServiceAchatsFamille, obtenir_service_achats_famille


# ═══════════════════════════════════════════════════════════
# FIXTURES
# ═══════════════════════════════════════════════════════════


@pytest.fixture
def service():
    return ServiceAchatsFamille()


@pytest.fixture
def achat_vetements(db: Session) -> AchatFamille:
    a = AchatFamille(
        nom="Pull chaud",
        categorie="jules_vetements",
        priorite="haute",
        prix_estime=25.0,
        pour_qui="jules",
        achete=False,
        a_revendre=False,
    )
    db.add(a)
    db.commit()
    db.refresh(a)
    return a


@pytest.fixture
def achat_achete(db: Session) -> AchatFamille:
    a = AchatFamille(
        nom="Livre Kirikou",
        categorie="livres",
        priorite="moyenne",
        prix_estime=12.0,
        prix_reel=11.5,
        pour_qui="jules",
        achete=True,
        a_revendre=True,
        date_achat=date.today(),
    )
    db.add(a)
    db.commit()
    db.refresh(a)
    return a


@pytest.fixture
def achat_urgent(db: Session) -> AchatFamille:
    a = AchatFamille(
        nom="Chaussures hiver",
        categorie="chaussures",
        priorite="urgent",
        prix_estime=45.0,
        pour_qui="jules",
        achete=False,
        a_revendre=False,
    )
    db.add(a)
    db.commit()
    db.refresh(a)
    return a


# ═══════════════════════════════════════════════════════════
# FACTORY
# ═══════════════════════════════════════════════════════════


class TestFactory:
    def test_retourne_instance_service(self):
        s = obtenir_service_achats_famille()
        assert isinstance(s, ServiceAchatsFamille)


# ═══════════════════════════════════════════════════════════
# LECTURE
# ═══════════════════════════════════════════════════════════


class TestLecture:
    def test_lister_achats_en_attente(self, service, achat_vetements: AchatFamille, db: Session):
        items = service.lister_achats(achete=False, db=db)
        assert any(a.id == achat_vetements.id for a in items)

    def test_lister_achats_achetes(self, service, achat_achete: AchatFamille, db: Session):
        items = service.lister_achats(achete=True, db=db)
        assert any(a.id == achat_achete.id for a in items)

    def test_lister_par_categorie(self, service, achat_vetements: AchatFamille, db: Session):
        items = service.lister_par_categorie("jules_vetements", achete=False, db=db)
        assert all(a.categorie == "jules_vetements" for a in items)
        assert any(a.id == achat_vetements.id for a in items)

    def test_lister_par_categorie_vide_si_mauvaise_categorie(self, service, db: Session):
        items = service.lister_par_categorie("categorie_inexistante", db=db)
        assert items == []

    def test_lister_par_personne(self, service, achat_vetements: AchatFamille, db: Session):
        items = service.lister_par_personne(pour_qui="jules", db=db)
        assert all(a.pour_qui == "jules" for a in items)
        assert any(a.id == achat_vetements.id for a in items)

    def test_lister_a_revendre(self, service, achat_achete: AchatFamille, db: Session):
        items = service.lister_a_revendre(db=db)
        assert any(a.id == achat_achete.id for a in items)
        assert all(a.a_revendre for a in items)

    def test_get_stats_retourne_structure_attendue(
        self, service, achat_vetements: AchatFamille, achat_achete: AchatFamille, db: Session
    ):
        stats = service.get_stats(db=db)
        assert "en_attente" in stats
        assert "achetes" in stats
        assert "total_estime" in stats
        assert "total_depense" in stats
        assert "urgents" in stats
        assert stats["en_attente"] >= 1
        assert stats["achetes"] >= 1

    def test_get_urgents(self, service, achat_urgent: AchatFamille, db: Session):
        items = service.get_urgents(limit=10, db=db)
        assert any(a.id == achat_urgent.id for a in items)
        assert all(a.priorite in ("urgent", "haute") for a in items)


# ═══════════════════════════════════════════════════════════
# ÉCRITURE
# ═══════════════════════════════════════════════════════════


class TestEcriture:
    def test_ajouter_achat_basique(self, service, db: Session):
        achat = service.ajouter_achat(
            nom="Livre de cuisine",
            categorie="livres",
            prix_estime=20.0,
            db=db,
        )
        assert achat is not None
        assert achat.nom == "Livre de cuisine"
        assert achat.achete is False
        assert achat.prix_estime == 20.0

    def test_ajouter_achat_avec_pour_qui(self, service, db: Session):
        achat = service.ajouter_achat(
            nom="Doudou souris",
            categorie="jules_jouets",
            pour_qui="jules",
            db=db,
        )
        assert achat is not None
        assert achat.pour_qui == "jules"

    def test_ajouter_achat_avec_revente(self, service, db: Session):
        achat = service.ajouter_achat(
            nom="Manteau hiver",
            categorie="jules_vetements",
            a_revendre=True,
            prix_revente_estime=10.0,
            db=db,
        )
        assert achat is not None
        assert achat.a_revendre is True
        assert achat.prix_revente_estime == 10.0

    def test_marquer_achete_sans_prix(self, service, achat_vetements: AchatFamille, db: Session):
        ok = service.marquer_achete(achat_vetements.id, db=db)
        assert ok is True
        db.refresh(achat_vetements)
        assert achat_vetements.achete is True
        assert achat_vetements.date_achat == date.today()

    def test_marquer_achete_avec_prix_reel(self, service, achat_vetements: AchatFamille, db: Session):
        ok = service.marquer_achete(achat_vetements.id, prix_reel=30.0, db=db)
        assert ok is True
        db.refresh(achat_vetements)
        assert achat_vetements.prix_reel == 30.0

    def test_marquer_achete_id_inexistant_retourne_false(self, service, db: Session):
        ok = service.marquer_achete(99999, db=db)
        assert not ok

    def test_marquer_vendu(self, service, achat_achete: AchatFamille, db: Session):
        ok = service.marquer_vendu(achat_achete.id, db=db)
        assert ok is True
        db.refresh(achat_achete)
        assert achat_achete.vendu_le is not None

    def test_marquer_vendu_id_inexistant_retourne_false(self, service, db: Session):
        ok = service.marquer_vendu(99999, db=db)
        assert not ok
