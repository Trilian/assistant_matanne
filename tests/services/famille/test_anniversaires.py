"""
Tests pour src/services/famille/anniversaires.py — ServiceAnniversaires.

Couvre:
- CRUD anniversaires
- Prochains anniversaires avec compte à rebours
- Historique cadeaux
- Propriétés calculées (age, jours_restants)
- Factory singleton
"""

from __future__ import annotations

from datetime import date, timedelta

import pytest
from sqlalchemy.orm import Session

from src.core.models import AnniversaireFamille
from src.services.famille.anniversaires import ServiceAnniversaires, obtenir_service_anniversaires


# ═══════════════════════════════════════════════════════════
# FIXTURES
# ═══════════════════════════════════════════════════════════


@pytest.fixture
def service():
    return ServiceAnniversaires()


@pytest.fixture
def anniversaire_proche(db: Session) -> AnniversaireFamille:
    """Anniversaire dans 7 jours."""
    aujourd_hui = date.today()
    anniv_date = aujourd_hui + timedelta(days=7)
    a = AnniversaireFamille(
        nom_personne="Mamie Françoise",
        date_naissance=anniv_date.replace(year=1955),
        relation="grand_parent",
        rappel_jours_avant=[7, 1, 0],
        actif=True,
    )
    db.add(a)
    db.commit()
    db.refresh(a)
    return a


@pytest.fixture
def anniversaire_lointain(db: Session) -> AnniversaireFamille:
    """Anniversaire dans 180 jours."""
    aujourd_hui = date.today()
    anniv_date = aujourd_hui + timedelta(days=180)
    a = AnniversaireFamille(
        nom_personne="Oncle Bernard",
        date_naissance=anniv_date.replace(year=1970),
        relation="oncle",
        actif=True,
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
        s = obtenir_service_anniversaires()
        assert isinstance(s, ServiceAnniversaires)


# ═══════════════════════════════════════════════════════════
# LECTURE
# ═══════════════════════════════════════════════════════════


class TestLecture:
    def test_obtenir_anniversaires_vide(self, service, db: Session):
        # DB de test propre
        items = service.obtenir_anniversaires(db=db)
        assert isinstance(items, list)

    def test_obtenir_anniversaires_avec_donnees(
        self, service, anniversaire_proche: AnniversaireFamille, db: Session
    ):
        items = service.obtenir_anniversaires(db=db)
        assert any(a.id == anniversaire_proche.id for a in items)

    def test_lister_anniversaires_alias(
        self, service, anniversaire_proche: AnniversaireFamille, db: Session
    ):
        """lister_anniversaires est un alias de obtenir_anniversaires."""
        items = service.lister_anniversaires(db=db)
        assert any(a.id == anniversaire_proche.id for a in items)

    def test_obtenir_prochains_dans_delai(
        self, service, anniversaire_proche: AnniversaireFamille, db: Session
    ):
        items = service.obtenir_prochains(jours=30, db=db)
        assert any(a["id"] == anniversaire_proche.id for a in items)

    def test_obtenir_prochains_hors_delai(
        self, service, anniversaire_lointain: AnniversaireFamille, db: Session
    ):
        items = service.obtenir_prochains(jours=30, db=db)
        assert not any(a["id"] == anniversaire_lointain.id for a in items)

    def test_lister_prochains_alias(
        self, service, anniversaire_proche: AnniversaireFamille, db: Session
    ):
        """lister_prochains est un alias de obtenir_prochains."""
        items = service.lister_prochains(limite=30, db=db)
        assert any(a["id"] == anniversaire_proche.id for a in items)

    def test_prochains_trie_par_jours_restants(
        self,
        service,
        anniversaire_proche: AnniversaireFamille,
        anniversaire_lointain: AnniversaireFamille,
        db: Session,
    ):
        items = service.obtenir_prochains(jours=365, db=db)
        jours = [a["jours_restants"] for a in items]
        assert jours == sorted(jours)

    def test_prochains_contient_champs_attendus(
        self, service, anniversaire_proche: AnniversaireFamille, db: Session
    ):
        items = service.obtenir_prochains(jours=30, db=db)
        assert items
        item = items[0]
        assert "id" in item
        assert "nom" in item
        assert "jours_restants" in item
        assert "age" in item
        assert item["jours_restants"] >= 0


# ═══════════════════════════════════════════════════════════
# ÉCRITURE
# ═══════════════════════════════════════════════════════════


class TestEcriture:
    def test_ajouter_anniversaire(self, service, db: Session):
        data = {
            "nom_personne": "Test Dupont",
            "date_naissance": date(1985, 3, 15),
            "relation": "ami",
        }
        a = service.ajouter_anniversaire(data, db=db)
        assert a is not None
        assert a.nom_personne == "Test Dupont"
        assert a.relation == "ami"

    def test_modifier_anniversaire(
        self, service, anniversaire_proche: AnniversaireFamille, db: Session
    ):
        ok = service.modifier_anniversaire(
            anniversaire_proche.id, {"idees_cadeaux": "Livre, fleurs"}, db=db
        )
        assert ok is True
        db.refresh(anniversaire_proche)
        assert anniversaire_proche.idees_cadeaux == "Livre, fleurs"

    def test_modifier_anniversaire_inexistant(self, service, db: Session):
        ok = service.modifier_anniversaire(99999, {"notes": "x"}, db=db)
        assert ok is False

    def test_supprimer_anniversaire(
        self, service, anniversaire_proche: AnniversaireFamille, db: Session
    ):
        anniv_id = anniversaire_proche.id
        ok = service.supprimer_anniversaire(anniv_id, db=db)
        assert ok is True
        reste = db.query(AnniversaireFamille).filter(AnniversaireFamille.id == anniv_id).first()
        assert reste is None

    def test_ajouter_cadeau_historique(
        self, service, anniversaire_proche: AnniversaireFamille, db: Session
    ):
        ok = service.ajouter_cadeau(
            anniversaire_proche.id, annee=2025, cadeau="Livre de recettes", db=db
        )
        assert ok is True
        db.refresh(anniversaire_proche)
        historique = anniversaire_proche.historique_cadeaux or []
        assert any(h.get("cadeau") == "Livre de recettes" for h in historique)

    def test_ajouter_cadeau_anniversaire_inexistant(self, service, db: Session):
        ok = service.ajouter_cadeau(99999, annee=2025, cadeau="Cadeau", db=db)
        assert ok is False


# ═══════════════════════════════════════════════════════════
# PROPRIÉTÉS CALCULÉES (modèle)
# ═══════════════════════════════════════════════════════════


class TestProprietes:
    def test_age_calcule(self, db: Session):
        """L'âge doit correspondre aux années révolues."""
        aujourd_hui = date.today()
        naissance_il_y_a_30_ans = aujourd_hui.replace(year=aujourd_hui.year - 30)
        a = AnniversaireFamille(
            nom_personne="Test Age",
            date_naissance=naissance_il_y_a_30_ans,
            relation="ami",
        )
        db.add(a)
        db.commit()
        db.refresh(a)
        # L'âge doit être 29 ou 30 selon si l'anniversaire est passé cette année
        assert a.age in (29, 30)

    def test_jours_restants_positif_ou_zero(
        self, anniversaire_proche: AnniversaireFamille
    ):
        """jours_restants doit être >= 0."""
        assert anniversaire_proche.jours_restants is not None
        assert anniversaire_proche.jours_restants >= 0
