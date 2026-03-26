"""
Routes API pour le planning.

Gestion du planning de repas hebdomadaire : consultation, création,
modification et suppression de repas planifiés.
"""

from datetime import UTC, datetime, timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response

from src.api.dependencies import require_auth
from src.api.schemas import (
    MessageResponse,
    PlanningSemaineResponse,
    RepasCreate,
)
from src.api.schemas.errors import (
    REPONSES_CRUD_CREATION,
    REPONSES_CRUD_ECRITURE,
    REPONSES_CRUD_SUPPRESSION,
    REPONSES_LISTE,
)
from src.api.utils import executer_async, executer_avec_session, gerer_exception_api

router = APIRouter(prefix="/api/v1/planning", tags=["Planning"])


@router.get("/semaine", response_model=PlanningSemaineResponse, responses=REPONSES_LISTE)
@gerer_exception_api
async def obtenir_planning_semaine(
    date_debut: datetime | None = Query(
        None, description="Date de début de semaine (ISO 8601). Défaut: lundi courant"
    ),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """
    Récupère le planning de repas de la semaine.

    Retourne tous les repas planifiés pour une semaine donnée, organisés
    par jour et type de repas (petit-déjeuner, déjeuner, dîner).

    Args:
        date_debut: Date de début (défaut: lundi de la semaine courante)

    Returns:
        Planning structuré par jour avec date_debut, date_fin et repas

    Example:
        ```
        GET /api/v1/planning/semaine?date_debut=2026-02-16

        Response:
        {
            "date_debut": "2026-02-16T00:00:00",
            "date_fin": "2026-02-23T00:00:00",
            "planning": {
                "2026-02-16": {
                    "dejeuner": {"id": 1, "recette_id": 42, "notes": null},
                    "diner": {"id": 2, "recette_id": 15, "notes": "Rapide"}
                }
            }
        }
        ```
    """
    from src.core.models import Repas

    if not date_debut:
        today = datetime.now(UTC)
        date_debut = today - timedelta(days=today.weekday())

    date_fin = date_debut + timedelta(days=7)

    def _query():
        with executer_avec_session() as session:
            repas = (
                session.query(Repas)
                .filter(Repas.date_repas >= date_debut, Repas.date_repas < date_fin)
                .order_by(Repas.date_repas)
                .all()
            )

            planning = {}
            for r in repas:
                jour = r.date_repas.strftime("%Y-%m-%d")
                if jour not in planning:
                    planning[jour] = {}
                planning[jour][r.type_repas] = {
                    "id": r.id,
                    "recette_id": r.recette_id,
                    "notes": getattr(r, "notes", None),
                }

            return {
                "date_debut": date_debut.isoformat(),
                "date_fin": date_fin.isoformat(),
                "planning": planning,
            }

    return await executer_async(_query)


@router.post("/repas", response_model=MessageResponse, responses=REPONSES_CRUD_CREATION)
@gerer_exception_api
async def creer_repas(repas: RepasCreate, user: dict[str, Any] = Depends(require_auth)):
    """
    Planifie un repas pour une date et un type donnés.

    Crée automatiquement le planning hebdomadaire s'il n'existe pas.
    Si un repas existe déjà pour la même date et le même type,
    il est mis à jour au lieu d'être dupliqué.

    Args:
        repas: Données du repas (date, type_repas, recette_id, notes)

    Returns:
        Message de confirmation avec l'ID du repas créé/mis à jour

    Raises:
        401: Non authentifié
        422: Données invalides

    Example:
        ```
        POST /api/v1/planning/repas
        Authorization: Bearer <token>

        Body:
        {
            "date": "2026-02-19",
            "type_repas": "diner",
            "recette_id": 42,
            "notes": "Préparer la veille"
        }

        Response:
        {"message": "Repas planifié", "id": 7}
        ```
    """
    from src.core.models import Planning, Repas

    def _create():
        with executer_avec_session() as session:
            # Récupérer ou créer un planning par défaut
            # repas.date est un objet date (plus datetime) depuis le schéma corrigé
            date_repas = repas.date

            # Chercher un planning existant pour cette date
            planning = (
                session.query(Planning)
                .filter(Planning.semaine_debut <= date_repas, Planning.semaine_fin >= date_repas)
                .first()
            )

            if not planning:
                # Créer un planning par défaut
                debut = date_repas - timedelta(days=date_repas.weekday())
                fin = debut + timedelta(days=6)
                planning = Planning(
                    nom=f"Semaine du {debut.strftime('%d/%m')}",
                    semaine_debut=debut,
                    semaine_fin=fin,
                    actif=True,
                )
                session.add(planning)
                session.flush()

            # Vérifier s'il existe déjà un repas pour cette date/type
            existing = (
                session.query(Repas)
                .filter(
                    Repas.date_repas == date_repas,
                    Repas.type_repas == repas.type_repas,
                    Repas.planning_id == planning.id,
                )
                .first()
            )

            if existing:
                # Mettre à jour
                existing.recette_id = repas.recette_id
                if hasattr(existing, "notes"):
                    existing.notes = repas.notes
                session.commit()
                return MessageResponse(message="Repas mis à jour", id=existing.id)

            # Créer
            db_repas = Repas(
                planning_id=planning.id,
                date_repas=date_repas,
                type_repas=repas.type_repas,
                recette_id=repas.recette_id,
            )
            session.add(db_repas)
            session.commit()

            return MessageResponse(message="Repas planifié", id=db_repas.id)

    return await executer_async(_create)


@router.put("/repas/{repas_id}", response_model=MessageResponse, responses=REPONSES_CRUD_ECRITURE)
@gerer_exception_api
async def modifier_repas(
    repas_id: int, repas: RepasCreate, user: dict[str, Any] = Depends(require_auth)
):
    """
    Met à jour un repas planifié.

    Permet de changer la recette, le type de repas ou les notes
    d'un repas déjà planifié.

    Args:
        repas_id: ID du repas à modifier
        repas: Nouvelles données du repas

    Returns:
        Message de confirmation

    Raises:
        401: Non authentifié
        404: Repas non trouvé

    Example:
        ```
        PUT /api/v1/planning/repas/7
        Authorization: Bearer <token>

        Body:
        {
            "date": "2026-02-19",
            "type_repas": "diner",
            "recette_id": 15,
            "notes": "Changement de dernière minute"
        }

        Response:
        {"message": "Repas mis à jour", "id": 7}
        ```
    """
    from src.core.models import Repas

    def _update():
        with executer_avec_session() as session:
            db_repas = session.query(Repas).filter(Repas.id == repas_id).first()

            if not db_repas:
                raise HTTPException(status_code=404, detail="Repas non trouvé")

            db_repas.type_repas = repas.type_repas
            db_repas.recette_id = repas.recette_id
            if hasattr(db_repas, "notes") and repas.notes:
                db_repas.notes = repas.notes

            session.commit()
            session.refresh(db_repas)

            return MessageResponse(message="Repas mis à jour", id=db_repas.id)

    return await executer_async(_update)


@router.delete(
    "/repas/{repas_id}", response_model=MessageResponse, responses=REPONSES_CRUD_SUPPRESSION
)
@gerer_exception_api
async def supprimer_repas(repas_id: int, user: dict[str, Any] = Depends(require_auth)):
    """
    Supprime un repas planifié.

    Args:
        repas_id: ID du repas à supprimer

    Returns:
        Message de confirmation

    Raises:
        401: Non authentifié
        404: Repas non trouvé

    Example:
        ```
        DELETE /api/v1/planning/repas/7
        Authorization: Bearer <token>

        Response:
        {"message": "Repas supprimé", "id": 7}
        ```
    """
    from src.core.models import Repas

    def _delete():
        with executer_avec_session() as session:
            repas = session.query(Repas).filter(Repas.id == repas_id).first()

            if not repas:
                raise HTTPException(status_code=404, detail="Repas non trouvé")

            session.delete(repas)
            session.commit()

            return MessageResponse(message="Repas supprimé", id=repas_id)

    return await executer_async(_delete)


# ─────────────────────────────────────────────────────────
# GÉNÉRATION IA
# ─────────────────────────────────────────────────────────


@router.post("/generer", response_model=PlanningSemaineResponse)
@gerer_exception_api
async def generer_planning_ia(
    body: "GenererPlanningRequest | None" = None,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """
    Génère un planning de repas hebdomadaire via l'IA Mistral.

    Crée 7 jours × 2 repas (déjeuner + dîner) en utilisant Mistral AI.
    Persiste directement les repas dans la DB.

    Args:
        body: Paramètres optionnels (date_debut, nb_personnes, preferences)

    Returns:
        Planning complet de la semaine générée

    Example:
        ```
        POST /api/v1/planning/generer
        Body: {"nb_personnes": 4}

        Response:
        {
            "date_debut": "2026-03-23",
            "date_fin": "2026-03-30",
            "planning": {
                "2026-03-23": {"dejeuner": {...}, "diner": {...}},
                ...
            }
        }
        ```
    """
    from datetime import date

    from src.api.schemas.planning import GenererPlanningRequest
    from src.services.cuisine.planning import obtenir_service_planning

    if body is None:
        body = GenererPlanningRequest()

    # Calculer le lundi de la semaine
    if body.date_debut:
        semaine_debut = body.date_debut
    else:
        today = date.today()
        semaine_debut = today - timedelta(days=today.weekday())

    def _generate():
        service = obtenir_service_planning()
        planning_obj = service.generer_planning_ia(
            semaine_debut=semaine_debut,
            preferences=body.preferences,
        )

        if not planning_obj:
            raise HTTPException(
                status_code=503,
                detail="Impossible de générer le planning. Réessayez plus tard."
            )

        # Reconstruire la réponse dans le même format que GET /semaine
        with executer_avec_session() as session:
            from src.core.models import Repas

            date_fin = semaine_debut + timedelta(days=7)
            repas = (
                session.query(Repas)
                .filter(
                    Repas.planning_id == planning_obj.id,
                )
                .order_by(Repas.date_repas)
                .all()
            )

            planning_dict = {}
            for r in repas:
                jour = r.date_repas.strftime("%Y-%m-%d")
                if jour not in planning_dict:
                    planning_dict[jour] = {}

                # Inclure le nom de la recette si liée
                entry = {
                    "id": r.id,
                    "recette_id": r.recette_id,
                    "notes": getattr(r, "notes", None),
                }
                if r.recette_id and hasattr(r, "recette") and r.recette:
                    entry["recette_nom"] = r.recette.nom

                planning_dict[jour][r.type_repas] = entry

            return {
                "date_debut": semaine_debut.isoformat(),
                "date_fin": date_fin.isoformat(),
                "planning": planning_dict,
            }

    return await executer_async(_generate)


# ─────────────────────────────────────────────────────────
# SUGGESTIONS RAPIDES
# ─────────────────────────────────────────────────────────


@router.get("/suggestions-rapides")
@gerer_exception_api
async def obtenir_suggestions_rapides(
    type_repas: str = Query("diner", description="Type de repas (dejeuner, diner, etc.)"),
    date_repas: str | None = Query(None, description="Date du repas (YYYY-MM-DD)"),
    nombre: int = Query(6, ge=1, le=12, description="Nombre de suggestions"),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """
    Suggestions rapides de recettes pour le sélecteur de repas.

    Retourne des recettes adaptées au type de repas et à la saison,
    en excluant celles déjà planifiées cette semaine.
    """
    from src.core.models import Recette, Repas

    def _query():
        with executer_avec_session() as session:
            # Trouver les recettes déjà planifiées cette semaine pour les exclure
            from datetime import date

            today = date.today()
            debut_semaine = today - timedelta(days=today.weekday())
            fin_semaine = debut_semaine + timedelta(days=7)

            recettes_planifiees_ids = [
                r.recette_id
                for r in session.query(Repas.recette_id)
                .filter(
                    Repas.date_repas >= debut_semaine,
                    Repas.date_repas < fin_semaine,
                    Repas.recette_id.isnot(None),
                )
                .all()
            ]

            # Chercher des recettes adaptées
            query = session.query(Recette)

            # Exclure les déjà planifiées
            if recettes_planifiees_ids:
                query = query.filter(Recette.id.notin_(recettes_planifiees_ids))

            # Adapter au type de repas
            if type_repas in ("petit_dejeuner", "gouter"):
                query = query.filter(
                    Recette.categorie.in_(["Petit-déjeuner", "Dessert", "Goûter", "Snack"])
                )

            # Trier par popularité (nombre d'historiques) et varier
            from sqlalchemy import func
            from src.core.models.recettes import HistoriqueRecette

            query = query.outerjoin(
                HistoriqueRecette, HistoriqueRecette.recette_id == Recette.id
            ).group_by(Recette.id).order_by(
                func.count(HistoriqueRecette.id).desc(),
                func.random(),
            )

            recettes = query.limit(nombre).all()

            return {
                "suggestions": [
                    {
                        "id": r.id,
                        "nom": r.nom,
                        "description": r.description,
                        "temps_total": (r.temps_preparation or 0) + (r.temps_cuisson or 0),
                        "categorie": r.categorie,
                    }
                    for r in recettes
                ],
                "type_repas": type_repas,
            }

    return await executer_async(_query)


# ─────────────────────────────────────────────────────────
# EXPORT iCAL
# ─────────────────────────────────────────────────────────


@router.get("/export/ical")
@gerer_exception_api
async def exporter_planning_ical(
    semaines: int = Query(2, ge=1, le=8, description="Nombre de semaines à exporter (1-8)"),
    user: dict[str, Any] = Depends(require_auth),
) -> Response:
    """
    Exporte le planning de repas au format iCalendar (.ics).

    Compatible Google Calendar, Apple Calendar, Outlook.

    Args:
        semaines: Nombre de semaines à inclure (défaut: 2, max: 8)

    Returns:
        Fichier .ics téléchargeable

    Example:
        ```
        GET /api/v1/planning/export/ical?semaines=4
        Authorization: Bearer <token>
        ```
    """
    from src.core.models import Repas

    def _build_ical():
        with executer_avec_session() as session:
            date_debut = datetime.now(UTC).replace(
                hour=0, minute=0, second=0, microsecond=0
            )
            # Reculer au lundi de la semaine courante
            date_debut -= timedelta(days=date_debut.weekday())
            date_fin = date_debut + timedelta(weeks=semaines)

            repas_liste = (
                session.query(Repas)
                .filter(
                    Repas.date_repas >= date_debut.date(),
                    Repas.date_repas < date_fin.date(),
                )
                .order_by(Repas.date_repas)
                .all()
            )

            # Construire le calendrier iCal
            lignes = [
                "BEGIN:VCALENDAR",
                "VERSION:2.0",
                "PRODID:-//Assistant Matanne//Planning Repas//FR",
                "CALSCALE:GREGORIAN",
                "METHOD:PUBLISH",
                "X-WR-CALNAME:Planning Repas Matanne",
                "X-WR-TIMEZONE:Europe/Paris",
            ]

            TYPES_REPAS_HEURES = {
                "petit_déjeuner": "070000",
                "déjeuner": "120000",
                "goûter": "160000",
                "dîner": "190000",
            }

            for repas in repas_liste:
                heure = TYPES_REPAS_HEURES.get(repas.type_repas, "120000")
                dt_debut = f"{repas.date_repas.strftime('%Y%m%d')}T{heure}"
                # Durée par défaut 30 min
                heure_fin = str(int(heure[:2]) * 10000 + int(heure[2:4]) * 100 + 3000).zfill(6)
                dt_fin = f"{repas.date_repas.strftime('%Y%m%d')}T{heure_fin}"

                # Titre : recette ou type de repas
                nom_recette = "Repas à planifier"
                if repas.recette:
                    nom_recette = repas.recette.nom

                type_label = repas.type_repas.replace("_", " ").capitalize()
                summary = f"{type_label} – {nom_recette}"

                description_parts = []
                if repas.entree:
                    description_parts.append(f"Entrée: {repas.entree}")
                if repas.dessert:
                    description_parts.append(f"Dessert: {repas.dessert}")
                if repas.notes:
                    description_parts.append(repas.notes)
                description = "\\n".join(description_parts)

                uid = f"repas-{repas.id}@matanne"
                now = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")

                lignes += [
                    "BEGIN:VEVENT",
                    f"UID:{uid}",
                    f"DTSTAMP:{now}",
                    f"DTSTART:{dt_debut}",
                    f"DTEND:{dt_fin}",
                    f"SUMMARY:{summary}",
                ]
                if description:
                    lignes.append(f"DESCRIPTION:{description}")
                lignes.append("END:VEVENT")

            lignes.append("END:VCALENDAR")
            return "\r\n".join(lignes)

    contenu = await executer_async(_build_ical)
    return Response(
        content=contenu,
        media_type="text/calendar; charset=utf-8",
        headers={
            "Content-Disposition": "attachment; filename=planning-repas.ics",
        },
    )


@router.get(
    "/nutrition-hebdo",
    responses=REPONSES_LISTE,
    summary="Analyse nutritionnelle hebdomadaire",
    description="Agrège les données nutritionnelles des repas planifiés pour une semaine donnée.",
)
@gerer_exception_api
async def nutrition_hebdomadaire(
    semaine: str | None = Query(
        None,
        description="Date de début de semaine ISO 8601 (YYYY-MM-DD). Défaut: semaine courante.",
    ),
    user: dict = Depends(require_auth),
) -> dict:
    """
    Retourne l'analyse nutritionnelle agrégée de la semaine :
    - Totaux calories / protéines / lipides / glucides
    - Répartition par jour
    - Nombre de repas sans données nutritionnelles
    """
    from datetime import date
    from src.core.models.planning import Repas
    from src.core.models.recettes import Recette

    def _query() -> dict:
        import datetime as dt

        # Calculer la semaine
        if semaine:
            debut = dt.date.fromisoformat(semaine)
        else:
            aujourd_hui = dt.date.today()
            debut = aujourd_hui - dt.timedelta(days=aujourd_hui.weekday())
        fin = debut + dt.timedelta(days=6)

        with executer_avec_session() as session:
            repas_liste = (
                session.query(Repas)
                .join(Recette, Repas.recette_id == Recette.id, isouter=True)
                .filter(
                    Repas.date_repas >= debut,
                    Repas.date_repas <= fin,
                )
                .all()
            )

            totaux = {"calories": 0, "proteines": 0.0, "lipides": 0.0, "glucides": 0.0}
            par_jour: dict[str, dict] = {}
            sans_donnees = 0

            for repas in repas_liste:
                jour = repas.date_repas.isoformat()
                if jour not in par_jour:
                    par_jour[jour] = {
                        "calories": 0,
                        "proteines": 0.0,
                        "lipides": 0.0,
                        "glucides": 0.0,
                        "repas": [],
                    }

                recette = repas.recette
                if recette and recette.calories is not None:
                    portions = repas.portion_ajustee or (recette.portions or 1)
                    # Valeur nutritionnelle = par portion × nombre de portions / portions standard
                    facteur = portions / (recette.portions or 1) if recette.portions else 1
                    cal = int((recette.calories or 0) * facteur)
                    prot = round((recette.proteines or 0.0) * facteur, 1)
                    lip = round((recette.lipides or 0.0) * facteur, 1)
                    gluc = round((recette.glucides or 0.0) * facteur, 1)

                    totaux["calories"] += cal
                    totaux["proteines"] += prot
                    totaux["lipides"] += lip
                    totaux["glucides"] += gluc
                    par_jour[jour]["calories"] += cal
                    par_jour[jour]["proteines"] += prot
                    par_jour[jour]["lipides"] += lip
                    par_jour[jour]["glucides"] += gluc
                else:
                    sans_donnees += 1

                par_jour[jour]["repas"].append({
                    "id": repas.id,
                    "type": repas.type_repas,
                    "nom_recette": recette.nom if recette else None,
                    "calories": int((recette.calories or 0) * facteur) if recette and recette.calories else None,
                })

            # Arrondis finaux
            totaux["proteines"] = round(totaux["proteines"], 1)
            totaux["lipides"] = round(totaux["lipides"], 1)
            totaux["glucides"] = round(totaux["glucides"], 1)

            nb_jours_avec_donnees = sum(
                1 for j in par_jour.values() if j["calories"] > 0
            )
            moyenne_calories = (
                round(totaux["calories"] / nb_jours_avec_donnees)
                if nb_jours_avec_donnees > 0
                else 0
            )

            return {
                "semaine_debut": debut.isoformat(),
                "semaine_fin": fin.isoformat(),
                "totaux": totaux,
                "moyenne_calories_par_jour": moyenne_calories,
                "par_jour": par_jour,
                "nb_repas_sans_donnees": sans_donnees,
                "nb_repas_total": len(repas_liste),
            }

    return await executer_async(_query)


# ═══════════════════════════════════════════════════════════
# SEMAINE UNIFIÉE — Vue trans-modules (AC1)
# ═══════════════════════════════════════════════════════════


@router.get("/semaine-unifiee", responses=REPONSES_LISTE)
@gerer_exception_api
async def obtenir_semaine_unifiee(
    date_debut: str | None = Query(
        None,
        description="Date de début de semaine ISO (YYYY-MM-DD). Défaut: lundi courant.",
    ),
    user: dict = Depends(require_auth),
) -> dict:
    """
    Vue unifiée de la semaine trans-modules : repas, tâches maison, activités famille, matchs.

    Agrège en une seule réponse :
    - `repas` : planning repas (déjeuner/dîner par jour)
    - `taches_maison` : tâches ménage/entretien du jour
    - `activites_famille` : activités Jules et famille de la semaine
    - `matchs` : paris sportifs prévus cette semaine
    - `meta` : dates de début/fin de semaine
    """
    import datetime as dt

    from src.core.models.planning import Repas
    from src.core.models.recettes import Recette

    if date_debut:
        debut = dt.date.fromisoformat(date_debut)
    else:
        aujourd_hui = dt.date.today()
        debut = aujourd_hui - dt.timedelta(days=aujourd_hui.weekday())
    fin = debut + dt.timedelta(days=6)

    def _query() -> dict:
        with executer_avec_session() as session:
            # ── Repas ────────────────────────────────────────────────
            repas_liste = (
                session.query(Repas)
                .join(Recette, Repas.recette_id == Recette.id, isouter=True)
                .filter(
                    Repas.date_repas >= debut,
                    Repas.date_repas <= fin,
                )
                .order_by(Repas.date_repas)
                .all()
            )
            repas_par_jour: dict[str, list[dict]] = {}
            for r in repas_liste:
                jour = r.date_repas.isoformat()
                repas_par_jour.setdefault(jour, []).append(
                    {
                        "id": r.id,
                        "type": r.type_repas,
                        "recette_id": r.recette_id,
                        "nom_recette": r.recette.nom if r.recette else None,
                    }
                )

            # ── Activités famille ─────────────────────────────────────
            activites: list[dict] = []
            try:
                from src.core.models.famille import ActiviteFamille

                acts = (
                    session.query(ActiviteFamille)
                    .filter(
                        ActiviteFamille.date >= debut,
                        ActiviteFamille.date <= fin,
                    )
                    .order_by(ActiviteFamille.date)
                    .all()
                )
                activites = [
                    {
                        "id": a.id,
                        "date": a.date.isoformat() if a.date else None,
                        "titre": a.titre,
                        "type": getattr(a, "type_activite", None) or getattr(a, "type", None),
                    }
                    for a in acts
                ]
            except Exception:
                pass

            # ── Matchs / Paris jeux ───────────────────────────────────
            matchs: list[dict] = []
            try:
                from src.core.models.jeux import Match

                ms = (
                    session.query(Match)
                    .filter(
                        Match.date_match >= debut,
                        Match.date_match <= fin,
                    )
                    .order_by(Match.date_match)
                    .all()
                )
                matchs = [
                    {
                        "id": m.id,
                        "date": m.date_match.isoformat() if m.date_match else None,
                        "equipe_domicile": getattr(m, "equipe_domicile", None),
                        "equipe_exterieur": getattr(m, "equipe_exterieur", None),
                        "competition": getattr(m, "competition", None),
                    }
                    for m in ms
                ]
            except Exception:
                pass

            # ── Tâches maison du jour ──────────────────────────────────
            taches_maison: list[dict] = []
            try:
                from src.services.maison import get_service_menage

                service_menage = get_service_menage()
                taches_raw = service_menage.obtenir_taches_jour()
                taches_maison = [
                    {
                        "nom": t.get("nom") or getattr(t, "nom", ""),
                        "categorie": t.get("categorie") or getattr(t, "categorie", None),
                        "duree_estimee_min": t.get("duree_estimee_min")
                        or getattr(t, "duree_estimee_min", None),
                    }
                    for t in (taches_raw or [])
                ]
            except Exception:
                pass

            return {
                "meta": {
                    "semaine_debut": debut.isoformat(),
                    "semaine_fin": fin.isoformat(),
                },
                "repas": repas_par_jour,
                "activites_famille": activites,
                "matchs": matchs,
                "taches_maison": taches_maison,
            }

    return await executer_async(_query)

