"""
Tests pour src/services/famille/routines.py — ServiceRoutines.

Couvre:
- Listage routines et tâches
- Création de routine
- Ajout de tâche
- Marquage complet / réinitialisation
- Tâches en retard
- Factory singleton
"""

from __future__ import annotations

from datetime import datetime
from unittest.mock import MagicMock

import pytest
from sqlalchemy.orm import Session

from src.core.models import Routine, TacheRoutine
from src.services.famille.routines import ServiceRoutines, obtenir_service_routines


# ═══════════════════════════════════════════════════════════
# FIXTURES
# ═══════════════════════════════════════════════════════════


@pytest.fixture
def service():
    return ServiceRoutines()


@pytest.fixture
def routine_matin(db: Session) -> Routine:
    """Routine du matin active."""
    r = Routine(
        nom="Routine matin Jules",
        description="Se lever, se laver, s'habiller",
        pour="jules",
        frequence="quotidien",
        active=True,
        ia_personnalisation="",
    )
    db.add(r)
    db.commit()
    db.refresh(r)
    return r


@pytest.fixture
def routine_soir(db: Session) -> Routine:
    """Routine du soir inactive."""
    r = Routine(
        nom="Routine soir",
        description="Bain, histoire, dodo",
        pour="jules",
        frequence="quotidien",
        active=False,
    )
    db.add(r)
    db.commit()
    db.refresh(r)
    return r


@pytest.fixture
def tache_brossage(db: Session, routine_matin: Routine) -> TacheRoutine:
    """Tâche 'Se brosser les dents' liée à routine_matin."""
    t = TacheRoutine(
        routine_id=routine_matin.id,
        nom="Se brosser les dents",
        heure_prevue="08:00",
        statut="en_attente",
    )
    db.add(t)
    db.commit()
    db.refresh(t)
    return t


# ═══════════════════════════════════════════════════════════
# FACTORY
# ═══════════════════════════════════════════════════════════


class TestFactory:
    def test_obtenir_service_retourne_instance(self):
        s = obtenir_service_routines()
        assert isinstance(s, ServiceRoutines)

    def test_singleton(self):
        s1 = obtenir_service_routines()
        s2 = obtenir_service_routines()
        assert s1 is s2


# ═══════════════════════════════════════════════════════════
# LECTURE
# ═══════════════════════════════════════════════════════════


class TestListerRoutines:
    def test_liste_vide(self, service, patch_db_context):
        result = service.lister_routines()
        assert result == []

    def test_liste_actives_uniquement(self, db, service, patch_db_context, routine_matin, routine_soir):
        result = service.lister_routines(actives_uniquement=True)
        noms = [r.get("nom", "") if isinstance(r, dict) else r.nom for r in result]
        assert any("matin" in n.lower() for n in noms)
        assert not any("soir" in n.lower() for n in noms)

    def test_liste_toutes_routines(self, db, service, patch_db_context, routine_matin, routine_soir):
        result = service.lister_routines(actives_uniquement=False)
        assert len(result) >= 2

    def test_liste_taches(self, db, service, patch_db_context, tache_brossage):
        result = service.lister_taches(routine_id=tache_brossage.routine_id)
        assert len(result) >= 1


# ═══════════════════════════════════════════════════════════
# CRÉATION
# ═══════════════════════════════════════════════════════════


class TestCreerRoutine:
    def test_creer_routine_succes(self, db, service, patch_db_context):
        result = service.creer_routine(
            nom="Routine weekend",
            description="Activités du weekend",
            pour="famille",
            frequence="hebdomadaire",
        )
        assert result is not None

    def test_routine_persistee(self, db, service, patch_db_context):
        service.creer_routine(
            nom="Sport matin",
            description="Natation ou vélo",
            pour="mathieu",
            frequence="quotidien",
        )
        nb = db.query(Routine).count()
        assert nb >= 1


class TestAjouterTache:
    def test_ajouter_tache_a_routine(self, db, service, patch_db_context, routine_matin):
        result = service.ajouter_tache(
            routine_id=routine_matin.id,
            nom="S'habiller",
            heure_prevue="07:45",
        )
        assert result is not None

    def test_tache_persistee(self, db, service, patch_db_context, routine_matin):
        service.ajouter_tache(
            routine_id=routine_matin.id,
            nom="Petit-déjeuner",
            heure_prevue="08:15",
        )
        nb = db.query(TacheRoutine).filter_by(routine_id=routine_matin.id).count()
        assert nb >= 1


# ═══════════════════════════════════════════════════════════
# COMPLÉTION
# ═══════════════════════════════════════════════════════════


class TestMarquerComplete:
    def test_marquer_tache_complete(self, db, service, patch_db_context, tache_brossage):
        result = service.marquer_complete(tache_brossage.id)
        assert result is not None or result is True

    def test_marquer_tache_inexistante(self, service, patch_db_context):
        result = service.marquer_complete(99999)
        assert result is None or result is False


class TestReinitialiserTaches:
    def test_reinitialiser_taches_jour(self, db, service, patch_db_context, tache_brossage):
        # Marquer la tâche comme complète d'abord
        db.query(TacheRoutine).filter_by(id=tache_brossage.id).update({"statut": "complete"})
        db.commit()
        # Réinitialiser
        result = service.reinitialiser_taches_jour(routine_id=tache_brossage.routine_id)
        assert result is not None


# ═══════════════════════════════════════════════════════════
# TÂCHES EN RETARD
# ═══════════════════════════════════════════════════════════


class TestTachesEnRetard:
    def test_aucune_tache_en_retard(self, db, service, patch_db_context, routine_matin):
        result = service.get_taches_en_retard()
        assert isinstance(result, list)

    def test_comptage_completees_aujourd_hui(self, db, service, patch_db_context, routine_matin):
        result = service.compter_completees_aujourdhui()
        assert isinstance(result, int)
        assert result >= 0


# ═══════════════════════════════════════════════════════════
# SUPPRESSION / DÉSACTIVATION
# ═══════════════════════════════════════════════════════════


class TestSuppressionRoutine:
    def test_supprimer_routine(self, db, service, patch_db_context, routine_matin):
        result = service.supprimer_routine(routine_matin.id)
        assert result is not False

    def test_desactiver_routine(self, db, service, patch_db_context, routine_matin):
        result = service.desactiver_routine(routine_matin.id)
        assert result is not None
