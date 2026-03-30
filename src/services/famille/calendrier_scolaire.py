"""Service calendrier scolaire (INNO-14).

Fournit une source interne de periodes scolaires par zone (A/B/C),
importe ces periodes dans ``evenements_calendrier`` et ajuste le
planning interne via ``evenements_planning``.
"""

from __future__ import annotations

from datetime import date, datetime, time, timedelta
from uuid import UUID

from src.core.db import obtenir_contexte_db
from src.core.models import CalendrierExterne, EvenementCalendrier, EvenementPlanning

ZONES_SCOLAIRES = ("A", "B", "C")

# Source interne minimale pour demarrer l'integration INNO-14.
# Les dates sont donnees a titre operationnel et peuvent etre
# remplacees plus tard par une source officielle API/ICS.
_VACANCES_PAR_ZONE: dict[str, list[dict[str, str]]] = {
    "A": [
        {"nom": "Vacances de la Toussaint", "debut": "2026-10-17", "fin": "2026-11-02"},
        {"nom": "Vacances de Noel", "debut": "2026-12-19", "fin": "2027-01-04"},
        {"nom": "Vacances d'hiver", "debut": "2027-02-06", "fin": "2027-02-22"},
        {"nom": "Vacances de printemps", "debut": "2027-04-10", "fin": "2027-04-26"},
        {"nom": "Vacances d'ete", "debut": "2027-07-06", "fin": "2027-09-01"},
    ],
    "B": [
        {"nom": "Vacances de la Toussaint", "debut": "2026-10-17", "fin": "2026-11-02"},
        {"nom": "Vacances de Noel", "debut": "2026-12-19", "fin": "2027-01-04"},
        {"nom": "Vacances d'hiver", "debut": "2027-02-20", "fin": "2027-03-08"},
        {"nom": "Vacances de printemps", "debut": "2027-04-24", "fin": "2027-05-10"},
        {"nom": "Vacances d'ete", "debut": "2027-07-06", "fin": "2027-09-01"},
    ],
    "C": [
        {"nom": "Vacances de la Toussaint", "debut": "2026-10-17", "fin": "2026-11-02"},
        {"nom": "Vacances de Noel", "debut": "2026-12-19", "fin": "2027-01-04"},
        {"nom": "Vacances d'hiver", "debut": "2027-02-13", "fin": "2027-03-01"},
        {"nom": "Vacances de printemps", "debut": "2027-04-17", "fin": "2027-05-03"},
        {"nom": "Vacances d'ete", "debut": "2027-07-06", "fin": "2027-09-01"},
    ],
}


def _normaliser_zone(zone: str) -> str:
    zone_norm = (zone or "").strip().upper()
    if zone_norm not in ZONES_SCOLAIRES:
        raise ValueError(f"Zone scolaire invalide: {zone}")
    return zone_norm


def _coerce_uuid(value: str | UUID | None) -> UUID | None:
    if value is None:
        return None
    try:
        return value if isinstance(value, UUID) else UUID(str(value))
    except Exception:
        return None


def lister_zones_scolaires() -> list[str]:
    """Retourne la liste des zones scolaires supportees."""
    return list(ZONES_SCOLAIRES)


def importer_calendrier_scolaire(
    user_id: str | UUID,
    zone: str,
    ajuster_planning: bool = True,
) -> dict[str, int | str | bool]:
    """Importe/met a jour le calendrier scolaire d'une zone pour un utilisateur."""
    zone_norm = _normaliser_zone(zone)
    periodes = _VACANCES_PAR_ZONE.get(zone_norm, [])
    user_uuid = _coerce_uuid(user_id)

    if not periodes:
        return {
            "zone": zone_norm,
            "calendrier_id": 0,
            "evenements_importes": 0,
            "events_planning_ajustes": 0,
            "ajustement_planning": ajuster_planning,
            "success": False,
        }

    with obtenir_contexte_db() as session:
        nom_calendrier = f"Calendrier scolaire Zone {zone_norm}"
        calendrier = (
            session.query(CalendrierExterne)
            .filter(
                CalendrierExterne.provider == "scolaire_auto",
                CalendrierExterne.user_id == user_uuid,
                CalendrierExterne.nom == nom_calendrier,
            )
            .first()
        )

        if calendrier is None:
            calendrier = CalendrierExterne(
                provider="scolaire_auto",
                nom=nom_calendrier,
                enabled=True,
                sync_interval_minutes=24 * 60,
                sync_direction="import",
                user_id=user_uuid,
                credentials={"zone": zone_norm, "source": "interne"},
            )
            session.add(calendrier)
            session.flush()
        else:
            calendrier.enabled = True
            calendrier.sync_interval_minutes = 24 * 60
            calendrier.sync_direction = "import"
            calendrier.credentials = {"zone": zone_norm, "source": "interne"}

        nb_evenements = 0
        nb_planning = 0

        for periode in periodes:
            debut = date.fromisoformat(periode["debut"])
            fin = date.fromisoformat(periode["fin"])
            uid = f"scolaire:{zone_norm}:{periode['nom']}:{periode['debut']}"

            evt = (
                session.query(EvenementCalendrier)
                .filter(
                    EvenementCalendrier.uid == uid,
                    EvenementCalendrier.user_id == user_uuid,
                )
                .first()
            )

            dt_debut = datetime.combine(debut, time.min)
            dt_fin = datetime.combine(fin + timedelta(days=1), time.min)

            if evt is None:
                evt = EvenementCalendrier(
                    uid=uid,
                    titre=f"{periode['nom']} (Zone {zone_norm})",
                    description="Vacances scolaires (import auto)",
                    date_debut=dt_debut,
                    date_fin=dt_fin,
                    all_day=True,
                    source_calendrier_id=calendrier.id,
                    user_id=user_uuid,
                )
                session.add(evt)
            else:
                evt.titre = f"{periode['nom']} (Zone {zone_norm})"
                evt.description = "Vacances scolaires (import auto)"
                evt.date_debut = dt_debut
                evt.date_fin = dt_fin
                evt.all_day = True
                evt.source_calendrier_id = calendrier.id

            nb_evenements += 1

            if ajuster_planning:
                marqueur = f"sync_scolaire:{uid}"
                planning_evt = (
                    session.query(EvenementPlanning)
                    .filter(EvenementPlanning.description == marqueur)
                    .first()
                )

                if planning_evt is None:
                    planning_evt = EvenementPlanning(
                        titre=f"Vacances scolaires - {periode['nom']}",
                        description=marqueur,
                        date_debut=dt_debut,
                        date_fin=dt_fin,
                        type_event="scolaire",
                        couleur="#2E7D32",
                        lieu="Ecole / vacances",
                        rappel_avant_minutes=60 * 24,
                    )
                    session.add(planning_evt)
                else:
                    planning_evt.titre = f"Vacances scolaires - {periode['nom']}"
                    planning_evt.date_debut = dt_debut
                    planning_evt.date_fin = dt_fin
                    planning_evt.type_event = "scolaire"
                    planning_evt.couleur = "#2E7D32"
                    planning_evt.lieu = "Ecole / vacances"
                    planning_evt.rappel_avant_minutes = 60 * 24

                nb_planning += 1

        calendrier.last_sync = datetime.now()
        session.commit()

        return {
            "zone": zone_norm,
            "calendrier_id": calendrier.id,
            "evenements_importes": nb_evenements,
            "events_planning_ajustes": nb_planning,
            "ajustement_planning": ajuster_planning,
            "success": True,
        }


def synchroniser_calendriers_scolaires_actifs() -> dict[str, int]:
    """Resynchronise tous les calendriers scolaires actifs existants."""
    with obtenir_contexte_db() as session:
        calendriers = (
            session.query(CalendrierExterne)
            .filter(
                CalendrierExterne.provider == "scolaire_auto",
                CalendrierExterne.enabled == True,  # noqa: E712
            )
            .all()
        )

    total = len(calendriers)
    succes = 0
    erreurs = 0

    for cal in calendriers:
        try:
            zone = (cal.credentials or {}).get("zone")
            if not zone:
                zone = (cal.nom or "").split(" ")[-1].strip().upper()
            importer_calendrier_scolaire(user_id=cal.user_id, zone=str(zone), ajuster_planning=True)
            succes += 1
        except Exception:
            erreurs += 1

    return {"total": total, "succes": succes, "erreurs": erreurs}
