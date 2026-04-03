"""
Schémas Pydantic pour les calendriers et événements.
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


# ═══════════════════════════════════════════════════════════
# CALENDRIERS EXTERNES
# ═══════════════════════════════════════════════════════════


class CalendrierResponse(BaseModel):
    id: int
    provider: str | None = Field(None, max_length=50)
    nom: str = Field(max_length=200)
    enabled: bool = True
    sync_interval_minutes: int | None = None
    last_sync: str | None = None
    sync_direction: str | None = Field(None, max_length=30)
    evenements_count: int = 0

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": 3,
                "provider": "google",
                "nom": "Calendrier famille",
                "enabled": True,
                "sync_interval_minutes": 30,
                "last_sync": "2026-04-03T08:00:00",
                "sync_direction": "bidirectionnel",
                "evenements_count": 42,
            }
        }
    }


class CalendrierDetailResponse(CalendrierResponse):
    url: str | None = Field(None, max_length=500)
    created_at: str | None = None
    updated_at: str | None = None


# ═══════════════════════════════════════════════════════════
# ÉVÉNEMENTS
# ═══════════════════════════════════════════════════════════


class EvenementResponse(BaseModel):
    id: int
    uid: str | None = Field(None, max_length=200)
    titre: str = Field(max_length=200)
    description: str | None = Field(None, max_length=2000)
    date_debut: str
    date_fin: str | None = None
    lieu: str | None = Field(None, max_length=200)
    all_day: bool = False
    recurrence_rule: str | None = Field(None, max_length=200)
    rappel_minutes: int | None = None
    source_calendrier_id: int | None = None

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": 15,
                "uid": "evt_123",
                "titre": "Vaccin Jules",
                "description": "Rendez-vous pédiatre pour rappel.",
                "date_debut": "2026-04-08T09:30:00",
                "date_fin": "2026-04-08T10:00:00",
                "lieu": "Cabinet Dr Martin",
                "all_day": False,
                "recurrence_rule": None,
                "rappel_minutes": 60,
                "source_calendrier_id": 3,
            }
        }
    }


class EvenementDetailResponse(EvenementResponse):
    created_at: str | None = None
    updated_at: str | None = None


class EvenementJourResponse(BaseModel):
    id: int
    titre: str = Field(max_length=200)
    date_debut: str
    date_fin: str | None = None
    lieu: str | None = Field(None, max_length=200)
    all_day: bool = False


class EvenementsAujourdhuiResponse(BaseModel):
    date: str
    items: list[EvenementJourResponse] = Field(default_factory=list)

    model_config = {
        "json_schema_extra": {
            "example": {
                "date": "2026-04-03",
                "items": [{"id": 15, "titre": "Vaccin Jules", "date_debut": "2026-04-03T09:30:00", "date_fin": "2026-04-03T10:00:00", "lieu": "Cabinet Dr Martin", "all_day": False}]
            }
        }
    }


class EvenementsSemaineResponse(BaseModel):
    date_debut: str
    date_fin: str
    par_jour: dict[str, list[EvenementJourResponse]] = Field(default_factory=dict)
    total: int = 0
