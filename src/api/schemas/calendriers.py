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
    provider: str | None = None
    nom: str
    enabled: bool = True
    sync_interval_minutes: int | None = None
    last_sync: str | None = None
    sync_direction: str | None = None
    evenements_count: int = 0


class CalendrierDetailResponse(CalendrierResponse):
    url: str | None = None
    created_at: str | None = None
    updated_at: str | None = None


# ═══════════════════════════════════════════════════════════
# ÉVÉNEMENTS
# ═══════════════════════════════════════════════════════════


class EvenementResponse(BaseModel):
    id: int
    uid: str | None = None
    titre: str
    description: str | None = None
    date_debut: str
    date_fin: str | None = None
    lieu: str | None = None
    all_day: bool = False
    recurrence_rule: str | None = None
    rappel_minutes: int | None = None
    source_calendrier_id: int | None = None


class EvenementDetailResponse(EvenementResponse):
    created_at: str | None = None
    updated_at: str | None = None


class EvenementJourResponse(BaseModel):
    id: int
    titre: str
    date_debut: str
    date_fin: str | None = None
    lieu: str | None = None
    all_day: bool = False


class EvenementsAujourdhuiResponse(BaseModel):
    date: str
    items: list[EvenementJourResponse] = Field(default_factory=list)


class EvenementsSemaineResponse(BaseModel):
    date_debut: str
    date_fin: str
    par_jour: dict[str, list[EvenementJourResponse]] = Field(default_factory=dict)
    total: int = 0
