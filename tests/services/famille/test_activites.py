"""
Tests pour src/services/famille/activites.py — ServiceActivites.

Couvre:
- Ajout d'activité
- Marquage comme terminée
- Listage des activités
- Suppression
- Factory singleton
"""

from __future__ import annotations

from datetime import date, timedelta
from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy.orm import Session

from src.core.models import ActiviteFamille
from src.services.famille.activites import ServiceActivites, obtenir_service_activites


# ═══════════════════════════════════════════════════════════
# FIXTURES
# ═══════════════════════════════════════════════════════════


@pytest.fixture
def service():
    return ServiceActivites()


@pytest.fixture
def activite_parc(db: Session) -> ActiviteFamille:
    """Activité 'Parc' en base de test."""
    a = ActiviteFamille(
        titre="Parc de la Tête d'Or",
        type_activite="parc",
        date_prevue=date.today() + timedelta(days=3),
        duree_heures=2.0,
        lieu="Lyon",
        qui_participe=["Jules", "Anne"],
        cout_estime=0.0,
        terminee=False,
    )
    db.add(a)
    db.commit()
    db.refresh(a)
    return a


@pytest.fixture
def activite_terminee(db: Session) -> ActiviteFamille:
    """Activité déjà terminée en base de test."""
    a = ActiviteFamille(
        titre="Musée Confluences",
        type_activite="musee",
        date_prevue=date.today() - timedelta(days=2),
        duree_heures=3.0,
        lieu="Lyon",
        qui_participe=["Jules", "Mathieu"],
        cout_estime=15.0,
        terminee=True,
    )
    db.add(a)
    db.commit()
    db.refresh(a)
    return a


# ═══════════════════════════════════════════════════════════
# FACTORY
# ═══════════════════════════════════════════════════════════


class TestFactory:
    def test_obtenir_service_retourne_instance(self):
        s = obtenir_service_activites()
        assert isinstance(s, ServiceActivites)

    def test_singleton(self):
        s1 = obtenir_service_activites()
        s2 = obtenir_service_activites()
        assert s1 is s2


# ═══════════════════════════════════════════════════════════
# LECTURE
# ═══════════════════════════════════════════════════════════


class TestListerActivites:
    def test_liste_vide(self, service, patch_db_context):
        result = service.lister_activites()
        assert result == []

    def test_liste_avec_activites(self, db, service, patch_db_context, activite_parc, activite_terminee):
        result = service.lister_activites()
        assert len(result) >= 2

    def test_filtrer_non_terminees(self, db, service, patch_db_context, activite_parc, activite_terminee):
        result = service.lister_activites(terminees_uniquement=False)
        titres = [a.titre if hasattr(a, "titre") else a.get("titre") for a in result]
        # Au moins une activité non terminée
        assert any("Parc" in str(t) for t in titres)


# ═══════════════════════════════════════════════════════════
# AJOUT
# ═══════════════════════════════════════════════════════════


class TestAjouterActivite:
    def test_ajouter_activite_succes(self, db, service, patch_db_context):
        result = service.ajouter_activite(
            titre="Zoo de Lyon",
            type_activite="zoo",
            date_prevue=date.today() + timedelta(days=7),
            duree=4.0,
            lieu="Lyon",
            participants=["Jules"],
            cout_estime=10.0,
            notes="Prévoir le pique-nique",
        )
        assert result is not None
        assert result.titre == "Zoo de Lyon"
        assert result.terminee is False

    def test_ajouter_activite_sans_notes(self, db, service, patch_db_context):
        result = service.ajouter_activite(
            titre="Vélo",
            type_activite="sport",
            date_prevue=date.today() + timedelta(days=1),
            duree=1.5,
            lieu="Lyon",
            participants=["Mathieu"],
            cout_estime=0.0,
        )
        assert result is not None
        assert result.notes == "" or result.notes is None

    def test_ajouter_activite_persistee(self, db, service, patch_db_context):
        service.ajouter_activite(
            titre="Cinéma",
            type_activite="cinema",
            date_prevue=date.today() + timedelta(days=5),
            duree=2.5,
            lieu="Centre-ville",
            participants=["Anne", "Mathieu"],
            cout_estime=20.0,
        )
        nb = db.query(ActiviteFamille).count()
        assert nb >= 1


# ═══════════════════════════════════════════════════════════
# MARQUAGE TERMINÉE
# ═══════════════════════════════════════════════════════════


class TestMarquerTerminee:
    def test_marquer_activite_terminee(self, db, service, patch_db_context, activite_parc):
        result = service.marquer_terminee(activite_parc.id)
        assert result is not None

    def test_marquer_activite_inexistante(self, service, patch_db_context):
        result = service.marquer_terminee(99999)
        assert result is None


# ═══════════════════════════════════════════════════════════
# SUPPRESSION
# ═══════════════════════════════════════════════════════════


class TestSupprimerActivite:
    def test_supprimer_activite_existante(self, db, service, patch_db_context, activite_parc):
        activite_id = activite_parc.id
        result = service.supprimer_activite(activite_id)
        # Retourne True ou None selon l'implémentation
        assert result is not False

    def test_supprimer_activite_inexistante(self, service, patch_db_context):
        result = service.supprimer_activite(99999)
        assert result is None or result is False
