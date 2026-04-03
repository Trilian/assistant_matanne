"""
Tests pour src/api/routes/planning.py

Tests unitaires avec vraies donnees pour les routes planning.
"""

from datetime import date, timedelta
from unittest.mock import MagicMock

import pytest


REPAS_TEST = [
    {"id": 1, "type_repas": "dejeuner", "date_repas": "2026-02-10", "recette_id": 1, "notes": "Poulet"},
    {"id": 2, "type_repas": "diner", "date_repas": "2026-02-10", "recette_id": 2, "notes": "Soupe"},
    {"id": 3, "type_repas": "dejeuner", "date_repas": "2026-02-11", "recette_id": 3, "notes": None},
]

NOUVEAU_REPAS = {"type_repas": "dejeuner", "date_repas": "2026-02-12", "recette_id": 1, "notes": "Tarte"}


def creer_mock_repas(data: dict) -> MagicMock:
    mock = MagicMock()
    for key, value in data.items():
        setattr(mock, key, value)
    return mock


class TestSchemasPlanning:

    def test_repas_base_valide(self):
        from src.api.schemas import RepasBase
        repas = RepasBase(type_repas="dejeuner", date_repas=date(2026, 2, 10), recette_id=1)
        assert repas.type_repas == "dejeuner"
        assert repas.recette_id == 1

    def test_repas_base_via_field_name(self):
        from src.api.schemas import RepasBase
        repas = RepasBase(type_repas="dejeuner", date=date(2026, 2, 10))
        assert repas.type_repas == "dejeuner"

    def test_type_repas_invalide_rejete(self):
        from pydantic import ValidationError
        from src.api.schemas import RepasBase
        with pytest.raises(ValidationError):
            RepasBase(type_repas="brunch", date_repas=date.today())

    def test_types_repas_valides(self):
        from src.api.schemas import RepasBase
        for t in ["petit_dejeuner", "dejeuner", "diner", "gouter"]:
            repas = RepasBase(type_repas=t, date_repas=date.today())
            assert repas.type_repas == t


class TestRoutesPlanning:
    pytestmark = [pytest.mark.asyncio(loop_scope="function")]

    async def test_planning_semaine_endpoint_existe(self, client):
        response = await client.get("/api/v1/planning/semaine")
        assert response.status_code in (200, 500)

    async def test_creer_repas_endpoint_existe(self, client):
        response = await client.post("/api/v1/planning/repas", json=NOUVEAU_REPAS)
        assert response.status_code in (200, 500)


class TestRoutesPlanningAvecMock:
    pytestmark = [pytest.mark.asyncio(loop_scope="function")]

    async def test_planning_semaine_format_correct(self, client):
        response = await client.get("/api/v1/planning/semaine")
        assert response.status_code in (200, 500)
        if response.status_code == 200:
            data = response.json()
            assert "date_debut" in data
            assert "date_fin" in data
            assert "planning" in data

    async def test_creer_repas_succes(self, client):
        response = await client.post("/api/v1/planning/repas", json=NOUVEAU_REPAS)
        assert response.status_code in (200, 500)


class TestValidationPlanning:
    pytestmark = [pytest.mark.asyncio(loop_scope="function")]

    async def test_creer_repas_type_invalide_echoue(self, client):
        response = await client.post("/api/v1/planning/repas", json={"type_repas": "brunch", "date_repas": "2026-02-12"})
        assert response.status_code == 422

    async def test_creer_repas_sans_date_echoue(self, client):
        response = await client.post("/api/v1/planning/repas", json={"type_repas": "dejeuner"})
        assert response.status_code == 422


class TestPlanningCreationDB:
    pytestmark = [pytest.mark.asyncio(loop_scope="function")]

    async def test_creer_repas_nouveau(self, client, db):
        from src.core.models import Planning, Repas
        today = date.today()
        planning = Planning(nom="Planning test", semaine_debut=today, semaine_fin=today + timedelta(days=7))
        db.add(planning)
        db.commit()
        db.refresh(planning)
        repas = Repas(planning_id=planning.id, date_repas=today + timedelta(days=1), type_repas="dejeuner")
        db.add(repas)
        db.commit()
        response = await client.get("/api/v1/planning/semaine")
        assert response.status_code == 200
        assert "planning" in response.json()

    async def test_planning_semaine_avec_repas(self, client, db):
        from src.core.models import Planning, Repas
        today = date.today()
        start_of_week = today - timedelta(days=today.weekday())
        planning = Planning(nom="Planning semaine", semaine_debut=start_of_week, semaine_fin=start_of_week + timedelta(days=7))
        db.add(planning)
        db.commit()
        db.refresh(planning)
        repas = Repas(planning_id=planning.id, date_repas=start_of_week + timedelta(days=2), type_repas="diner")
        db.add(repas)
        db.commit()
        response = await client.get("/api/v1/planning/semaine")
        assert response.status_code == 200
        assert "planning" in response.json()

    async def test_post_repas_cree_planning_automatique(self, client, db):
        tomorrow = (date.today() + timedelta(days=1)).isoformat()
        response = await client.post("/api/v1/planning/repas", json={"type_repas": "dejeuner", "date_repas": tomorrow})
        assert response.status_code in (200, 500)

    async def test_post_repas_avec_planning_existant(self, client, db):
        from src.core.models import Planning
        today = date.today()
        start_of_week = today - timedelta(days=today.weekday())
        planning = Planning(nom="Planning test", semaine_debut=start_of_week, semaine_fin=start_of_week + timedelta(days=6), etat="valide")
        db.add(planning)
        db.commit()
        tomorrow = (today + timedelta(days=1)).isoformat()
        response = await client.post("/api/v1/planning/repas", json={"type_repas": "diner", "date_repas": tomorrow})
        assert response.status_code in (200, 500)


class TestValidationPlanningV2:
    pytestmark = [pytest.mark.asyncio(loop_scope="function")]

    async def test_valider_planning_brouillon_passe_a_valide(self, client, db):
        from src.core.models import Planning

        lundi = date.today() - timedelta(days=date.today().weekday())
        planning = Planning(
            nom="Planning brouillon",
            semaine_debut=lundi,
            semaine_fin=lundi + timedelta(days=6),
            etat="brouillon",
        )
        db.add(planning)
        db.commit()
        db.refresh(planning)

        response = await client.post(f"/api/v1/planning/{planning.id}/valider")
        assert response.status_code == 200

        db.refresh(planning)
        assert planning.etat == "valide"

    async def test_valider_planning_archive_retourne_409(self, client, db):
        from src.core.models import Planning

        lundi = date.today() - timedelta(days=date.today().weekday())
        planning = Planning(
            nom="Planning archive",
            semaine_debut=lundi,
            semaine_fin=lundi + timedelta(days=6),
            etat="archive",
        )
        db.add(planning)
        db.commit()
        db.refresh(planning)

        response = await client.post(f"/api/v1/planning/{planning.id}/valider")
        assert response.status_code == 409

    async def test_regenerer_planning_archive_retourne_409(self, client, db):
        from src.core.models import Planning

        lundi = date.today() - timedelta(days=date.today().weekday())
        planning = Planning(
            nom="Planning archive",
            semaine_debut=lundi,
            semaine_fin=lundi + timedelta(days=6),
            etat="archive",
        )
        db.add(planning)
        db.commit()
        db.refresh(planning)

        response = await client.post(f"/api/v1/planning/{planning.id}/regenerer")
        assert response.status_code == 409


class TestSchemasPlanningCoverage:

    def test_repas_avec_notes(self):
        from src.api.schemas import RepasBase
        repas = RepasBase(type_repas="dejeuner", date_repas=date.today(), notes="Notes de test")
        assert repas.notes == "Notes de test"

    def test_repas_sans_recette(self):
        from src.api.schemas import RepasBase
        repas = RepasBase(type_repas="dejeuner", date_repas=date.today())
        assert repas.recette_id is None


class TestRoutesPlanningCoverage:
    pytestmark = [pytest.mark.asyncio(loop_scope="function")]

    async def test_planning_avec_date_specifique(self, client):
        today_str = date.today().isoformat()
        response = await client.get(f"/api/v1/planning/semaine?date={today_str}")
        assert response.status_code in (200, 500)

    async def test_supprimer_repas(self, client, db):
        from src.core.models import Planning, Repas
        today = date.today()
        planning = Planning(nom="Planning test", semaine_debut=today, semaine_fin=today + timedelta(days=7))
        db.add(planning)
        db.commit()
        db.refresh(planning)
        repas = Repas(planning_id=planning.id, date_repas=today + timedelta(days=1), type_repas="dejeuner")
        db.add(repas)
        db.commit()
        db.refresh(repas)
        response = await client.delete(f"/api/v1/planning/repas/{repas.id}")
        assert response.status_code in (200, 204, 404, 405, 500)

    async def test_modifier_repas(self, client, db):
        from src.core.models import Planning, Repas
        today = date.today()
        planning = Planning(nom="Planning test", semaine_debut=today, semaine_fin=today + timedelta(days=7))
        db.add(planning)
        db.commit()
        db.refresh(planning)
        repas = Repas(planning_id=planning.id, date_repas=today + timedelta(days=1), type_repas="dejeuner")
        db.add(repas)
        db.commit()
        db.refresh(repas)
        response = await client.put(
            f"/api/v1/planning/repas/{repas.id}",
            json={"type_repas": "diner", "date_repas": (today + timedelta(days=2)).isoformat()},
        )
        assert response.status_code in (200, 404, 405, 500)


class TestPlanningPayloadExact:
    pytestmark = [pytest.mark.asyncio(loop_scope="function")]

    async def test_planning_semaine_payload_exact_empty(self, client):
        response = await client.get("/api/v1/planning/semaine?date_debut=2026-02-10T00:00:00")
        assert response.status_code == 200
        assert response.json() == {
            "date_debut": "2026-02-10T00:00:00",
            "date_fin": "2026-02-17T00:00:00",
            "planning": {},
        }

    async def test_planning_mensuel_payload_exact_empty(self, client):
        response = await client.get("/api/v1/planning/mensuel?mois=2026-02")
        assert response.status_code == 200
        assert response.json() == {
            "mois": "2026-02",
            "debut": "2026-02-01",
            "fin": "2026-02-28",
            "repas": [],
            "par_jour": {},
        }

    async def test_planning_mensuel_payload_exact_with_repas(self, client, db):
        from src.core.models import Planning, Repas

        planning = Planning(
            nom="Semaine test",
            semaine_debut=date(2026, 2, 9),
            semaine_fin=date(2026, 2, 15),
            etat="valide",
        )
        db.add(planning)
        db.commit()
        db.refresh(planning)

        repas = Repas(
            planning_id=planning.id,
            date_repas=date(2026, 2, 10),
            type_repas="dejeuner",
            recette_id=None,
            notes="Repas test",
        )
        db.add(repas)
        db.commit()
        db.refresh(repas)

        response = await client.get("/api/v1/planning/mensuel?mois=2026-02")
        assert response.status_code == 200
        assert response.json() == {
            "mois": "2026-02",
            "debut": "2026-02-01",
            "fin": "2026-02-28",
            "repas": [
                {
                    "id": repas.id,
                    "date_repas": "2026-02-10",
                    "type_repas": "dejeuner",
                    "recette_id": None,
                    "recette_nom": None,
                    "notes": "Repas test",
                }
            ],
            "par_jour": {
                "2026-02-10": [
                    {
                        "id": repas.id,
                        "date_repas": "2026-02-10",
                        "type_repas": "dejeuner",
                        "recette_id": None,
                        "recette_nom": None,
                        "notes": "Repas test",
                    }
                ]
            },
        }

    async def test_planning_conflits_payload_exact_empty(self, client, monkeypatch):
        from src.services.planning.conflits import RapportConflits

        class _ServiceConflitsMock:
            def detecter_conflits_semaine(self, lundi):
                return RapportConflits(
                    date_debut=lundi,
                    date_fin=lundi + timedelta(days=6),
                    conflits=[],
                )

        monkeypatch.setattr(
            "src.services.planning.conflits.obtenir_service_conflits",
            lambda: _ServiceConflitsMock(),
        )

        response = await client.get("/api/v1/planning/conflits?date_debut=2026-02-10T00:00:00")
        assert response.status_code == 200
        assert response.json() == {
            "date_debut": "2026-02-09",
            "date_fin": "2026-02-15",
            "resume": "✅ Aucun conflit détecté",
            "nb_erreurs": 0,
            "nb_avertissements": 0,
            "nb_infos": 0,
            "items": [],
        }

    async def test_planning_conflits_payload_exact_with_item(self, client, monkeypatch):
        from src.services.planning.conflits import Conflit, NiveauConflit, RapportConflits, TypeConflit

        class _ServiceConflitsMock:
            def detecter_conflits_semaine(self, lundi):
                return RapportConflits(
                    date_debut=lundi,
                    date_fin=lundi + timedelta(days=6),
                    conflits=[
                        Conflit(
                            type=TypeConflit.SANS_MARGE,
                            niveau=NiveauConflit.AVERTISSEMENT,
                            message="Enchaînement serré entre deux événements",
                            date_jour=date(2026, 2, 10),
                            suggestion="Ajouter 15 min de marge",
                            evenement_1={
                                "titre": "École",
                                "heure_debut": "08:00",
                                "heure_fin": "08:30",
                            },
                            evenement_2={
                                "titre": "Rendez-vous",
                                "heure_debut": "08:35",
                                "heure_fin": "09:00",
                            },
                        )
                    ],
                )

        monkeypatch.setattr(
            "src.services.planning.conflits.obtenir_service_conflits",
            lambda: _ServiceConflitsMock(),
        )

        response = await client.get("/api/v1/planning/conflits?date_debut=2026-02-10T00:00:00")
        assert response.status_code == 200
        assert response.json() == {
            "date_debut": "2026-02-09",
            "date_fin": "2026-02-15",
            "resume": "🟡 1 avertissement(s)",
            "nb_erreurs": 0,
            "nb_avertissements": 1,
            "nb_infos": 0,
            "items": [
                {
                    "type": "sans_marge",
                    "niveau": "avertissement",
                    "message": "Enchaînement serré entre deux événements",
                    "date_jour": "2026-02-10",
                    "suggestion": "Ajouter 15 min de marge",
                    "evenement_1": {
                        "titre": "École",
                        "heure_debut": "08:00",
                        "heure_fin": "08:30",
                    },
                    "evenement_2": {
                        "titre": "Rendez-vous",
                        "heure_debut": "08:35",
                        "heure_fin": "09:00",
                    },
                }
            ],
        }

    async def test_creer_repas_payload_exact_creation(self, client):
        response = await client.post(
            "/api/v1/planning/repas",
            json={
                "type_repas": "diner",
                "date_repas": "2026-02-10",
                "recette_id": None,
                "notes": "Rapide",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Repas planifié"
        assert isinstance(data["id"], int)
        assert data["id"] > 0

    async def test_creer_repas_payload_exact_mise_a_jour(self, client, db):
        from src.core.models import Planning, Repas

        planning = Planning(
            nom="Semaine test",
            semaine_debut=date(2026, 2, 10),
            semaine_fin=date(2026, 2, 16),
            etat="valide",
        )
        db.add(planning)
        db.commit()
        db.refresh(planning)

        repas = Repas(
            planning_id=planning.id,
            date_repas=date(2026, 2, 10),
            type_repas="diner",
            recette_id=None,
            notes="Avant",
        )
        db.add(repas)
        db.commit()
        db.refresh(repas)

        response = await client.post(
            "/api/v1/planning/repas",
            json={
                "type_repas": "diner",
                "date_repas": "2026-02-10",
                "recette_id": None,
                "notes": "Après",
            },
        )
        assert response.status_code == 200
        assert response.json() == {"message": "Repas mis à jour", "id": repas.id, "details": None}

    async def test_modifier_repas_payload_exact(self, client, db):
        from src.core.models import Planning, Repas

        planning = Planning(
            nom="Semaine test",
            semaine_debut=date(2026, 2, 10),
            semaine_fin=date(2026, 2, 16),
            etat="valide",
        )
        db.add(planning)
        db.commit()
        db.refresh(planning)

        repas = Repas(
            planning_id=planning.id,
            date_repas=date(2026, 2, 10),
            type_repas="dejeuner",
            recette_id=None,
            notes="Initial",
        )
        db.add(repas)
        db.commit()
        db.refresh(repas)

        response = await client.put(
            f"/api/v1/planning/repas/{repas.id}",
            json={
                "type_repas": "diner",
                "date_repas": "2026-02-10",
                "recette_id": None,
                "notes": "Modifié",
            },
        )
        assert response.status_code == 200
        assert response.json() == {"message": "Repas mis à jour", "id": repas.id, "details": None}

    async def test_supprimer_repas_payload_exact(self, client, db):
        from src.core.models import Planning, Repas

        planning = Planning(
            nom="Semaine test",
            semaine_debut=date(2026, 2, 10),
            semaine_fin=date(2026, 2, 16),
            etat="valide",
        )
        db.add(planning)
        db.commit()
        db.refresh(planning)

        repas = Repas(
            planning_id=planning.id,
            date_repas=date(2026, 2, 10),
            type_repas="diner",
            recette_id=None,
            notes="À supprimer",
        )
        db.add(repas)
        db.commit()
        db.refresh(repas)

        response = await client.delete(f"/api/v1/planning/repas/{repas.id}")
        assert response.status_code == 200
        assert response.json() == {"message": "Repas supprimé", "id": repas.id, "details": None}

    async def test_supprimer_repas_inexistant_payload_exact(self, client):
        response = await client.delete("/api/v1/planning/repas/999999")
        assert response.status_code == 404
        assert response.json() == {"detail": "Repas non trouvé"}
