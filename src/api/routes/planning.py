"""
Routes API pour le planning.

Gestion du planning de repas hebdomadaire : consultation, création,
modification et suppression de repas planifiés.
"""

import logging
from datetime import UTC, date, datetime, timedelta
from typing import Any

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from fastapi.responses import Response

from src.api.dependencies import require_auth
from src.api.schemas import (
    GenererPlanningRequest,
    MessageResponse,
    PlanningSemaineResponse,
    RepasCreate,
)
from src.api.schemas.errors import (
    REPONSES_CRUD_CREATION,
    REPONSES_CRUD_ECRITURE,
    REPONSES_CRUD_SUPPRESSION,
    REPONSES_IA,
    REPONSES_LISTE,
)
from src.api.schemas.ia_transverses import PlanificationHebdoCompleteResponse
from src.api.utils import executer_async, executer_avec_session, gerer_exception_api
from src.services.cuisine.service_ia import obtenir_service_innovations_cuisine

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/planning", tags=["Planning"])


@router.get(
    "/planification-auto", response_model=PlanificationHebdoCompleteResponse, responses=REPONSES_IA
)
@gerer_exception_api
async def planification_automatique(
    user: dict[str, Any] = Depends(require_auth),
) -> PlanificationHebdoCompleteResponse:
    """Alias métier pour la planification hebdomadaire automatique."""
    service = obtenir_service_innovations_cuisine()
    user_id = str(user.get("id") or "")
    result = service.generer_planification_hebdo_complete(user_id=user_id)
    return result or PlanificationHebdoCompleteResponse()


@router.get("/mensuel", responses=REPONSES_LISTE)
@gerer_exception_api
async def obtenir_planning_mensuel(
    mois: str = Query(..., description="Mois cible au format YYYY-MM"),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Retourne les repas planifiés pour un mois complet."""
    from src.core.models import Repas

    try:
        annee_str, mois_str = mois.split("-", 1)
        annee = int(annee_str)
        numero_mois = int(mois_str)
        if numero_mois < 1 or numero_mois > 12:
            raise ValueError
    except ValueError as exc:
        raise HTTPException(
            status_code=422, detail="Le paramètre 'mois' doit être au format YYYY-MM"
        ) from exc

    debut_mois = date(annee, numero_mois, 1)
    if numero_mois == 12:
        debut_mois_suivant = date(annee + 1, 1, 1)
    else:
        debut_mois_suivant = date(annee, numero_mois + 1, 1)

    def _query() -> dict[str, Any]:
        with executer_avec_session() as session:
            repas = (
                session.query(Repas)
                .filter(Repas.date_repas >= debut_mois, Repas.date_repas < debut_mois_suivant)
                .order_by(Repas.date_repas)
                .all()
            )

            items: list[dict[str, Any]] = []
            par_jour: dict[str, list[dict[str, Any]]] = {}

            for r in repas:
                item = {
                    "id": r.id,
                    "date_repas": r.date_repas.isoformat()
                    if hasattr(r.date_repas, "isoformat")
                    else str(r.date_repas),
                    "type_repas": r.type_repas,
                    "recette_id": r.recette_id,
                    "recette_nom": r.recette.nom if getattr(r, "recette", None) else None,
                    "notes": getattr(r, "notes", None),
                }
                items.append(item)
                key = item["date_repas"]
                if key not in par_jour:
                    par_jour[key] = []
                par_jour[key].append(item)

            return {
                "mois": mois,
                "debut": debut_mois.isoformat(),
                "fin": (debut_mois_suivant - timedelta(days=1)).isoformat(),
                "repas": items,
                "par_jour": par_jour,
            }

    return await executer_async(_query)


@router.get("/conflits", responses=REPONSES_LISTE)
@gerer_exception_api
async def obtenir_conflits_planning(
    date_debut: datetime | None = Query(
        None,
        description="Date de début de semaine (ISO 8601). Défaut: lundi courant",
    ),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Retourne les conflits planning détectés pour une semaine."""
    from src.core.date_utils import obtenir_debut_semaine
    from src.services.planning.conflits import obtenir_service_conflits

    base = date_debut.date() if date_debut else datetime.now(UTC).date()
    lundi = obtenir_debut_semaine(base)

    def _query() -> dict[str, Any]:
        service = obtenir_service_conflits()
        rapport = service.detecter_conflits_semaine(lundi)

        return {
            "date_debut": rapport.date_debut.isoformat(),
            "date_fin": rapport.date_fin.isoformat(),
            "resume": rapport.resume,
            "nb_erreurs": rapport.nb_erreurs,
            "nb_avertissements": rapport.nb_avertissements,
            "nb_infos": rapport.nb_infos,
            "items": [
                {
                    "type": conflit.type.value,
                    "niveau": conflit.niveau.value,
                    "message": conflit.message,
                    "date_jour": conflit.date_jour.isoformat(),
                    "suggestion": conflit.suggestion,
                    "evenement_1": conflit.evenement_1,
                    "evenement_2": conflit.evenement_2,
                }
                for conflit in rapport.conflits
            ],
        }

    return await executer_async(_query)


@router.get("/semaine", response_model=PlanningSemaineResponse, responses=REPONSES_LISTE)
@gerer_exception_api
async def obtenir_planning_semaine(
    date_debut: date | None = Query(
        None, description="Date de début de semaine (YYYY-MM-DD). Défaut: lundi courant"
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
        today = date.today()
        date_debut = today - timedelta(days=today.weekday())

    date_fin = date_debut + timedelta(days=7)

    def _query():
        from src.core.models import Planning
        from src.core.models.recettes import Recette

        with executer_avec_session() as session:
            repas = (
                session.query(Repas)
                .filter(Repas.date_repas >= date_debut, Repas.date_repas < date_fin)
                .order_by(Repas.date_repas)
                .all()
            )

            # Récupérer les noms de recettes en une seule requête
            # (plat principal + entrée + dessert)
            recette_ids = list(
                {
                    rid
                    for r in repas
                    for rid in (r.recette_id, r.entree_recette_id, r.dessert_recette_id)
                    if rid is not None
                }
            )
            recettes_map: dict[int, str] = {}
            if recette_ids:
                for rec in session.query(Recette.id, Recette.nom).filter(
                    Recette.id.in_(recette_ids)
                ):
                    recettes_map[rec.id] = rec.nom

            # Récupérer l'ID du planning actif (non archivé) pour la période
            planning_db = (
                session.query(Planning)
                .filter(
                    Planning.semaine_debut <= date_debut,
                    Planning.semaine_fin >= date_debut,
                    Planning.etat.notin_(["archive"]),
                )
                .order_by(Planning.id.desc())
                .first()
            )
            planning_id = planning_db.id if planning_db else None

            # Normalise les valeurs accentuées stockées en DB vers les valeurs
            # canoniques sans accents attendues par le frontend.
            _TYPE_NORM = {
                "petit_déjeuner": "petit_dejeuner",
                "déjeuner": "dejeuner",
                "dîner": "diner",
                "goûter": "gouter",
            }

            planning_dict: dict = {}
            repas_list = []
            for r in repas:
                jour = r.date_repas.strftime("%Y-%m-%d")
                recette_nom = recettes_map.get(r.recette_id) if r.recette_id else None
                type_repas = _TYPE_NORM.get(r.type_repas, r.type_repas)
                entry: dict = {
                    "id": r.id,
                    "recette_id": r.recette_id,
                    "notes": getattr(r, "notes", None),
                    "recette_nom": recette_nom,
                    "entree": getattr(r, "entree", None),
                    "entree_recette_id": getattr(r, "entree_recette_id", None),
                    "entree_recette_nom": recettes_map.get(r.entree_recette_id)
                    if r.entree_recette_id
                    else None,
                    "laitage": getattr(r, "laitage", None),
                    "dessert": getattr(r, "dessert", None),
                    "dessert_recette_id": getattr(r, "dessert_recette_id", None),
                    "dessert_recette_nom": recettes_map.get(r.dessert_recette_id)
                    if r.dessert_recette_id
                    else None,
                }
                if jour not in planning_dict:
                    planning_dict[jour] = {}
                planning_dict[jour][type_repas] = entry

                repas_list.append(
                    {
                        "id": r.id,
                        "date_repas": jour,
                        "type_repas": type_repas,
                        "recette_id": r.recette_id,
                        "recette_nom": recette_nom,
                        "notes": getattr(r, "notes", None),
                        "entree": getattr(r, "entree", None),
                        "entree_recette_id": getattr(r, "entree_recette_id", None),
                        "entree_recette_nom": recettes_map.get(r.entree_recette_id)
                        if r.entree_recette_id
                        else None,
                        "laitage": getattr(r, "laitage", None),
                        "dessert": getattr(r, "dessert", None),
                        "dessert_recette_id": getattr(r, "dessert_recette_id", None),
                        "dessert_recette_nom": recettes_map.get(r.dessert_recette_id)
                        if r.dessert_recette_id
                        else None,
                        "plat_jules": getattr(r, "plat_jules", None),
                        "notes_jules": getattr(r, "notes_jules", None),
                        "adaptation_auto": getattr(r, "adaptation_auto", True),
                    }
                )

            return {
                "date_debut": date_debut.isoformat(),
                "date_fin": date_fin.isoformat(),
                "planning": planning_dict,
                "planning_id": planning_id,
                "repas": repas_list,
            }

    return await executer_async(_query)


@router.post("/repas", response_model=MessageResponse, responses=REPONSES_CRUD_CREATION)
@gerer_exception_api
async def creer_repas(donnees: RepasCreate, user: dict[str, Any] = Depends(require_auth)):
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
            # donnees.date est un objet date (plus datetime) depuis le schéma corrigé
            date_repas = donnees.date

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
                    Repas.type_repas == donnees.type_repas,
                    Repas.planning_id == planning.id,
                )
                .first()
            )

            if existing:
                # Mettre à jour
                existing.recette_id = donnees.recette_id
                if hasattr(existing, "notes"):
                    existing.notes = donnees.notes
                session.commit()
                return MessageResponse(message="Repas mis à jour", id=existing.id)

            # Créer
            db_repas = Repas(
                planning_id=planning.id,
                date_repas=date_repas,
                type_repas=donnees.type_repas,
                recette_id=donnees.recette_id,
            )
            session.add(db_repas)
            session.commit()

            return MessageResponse(message="Repas planifié", id=db_repas.id)

    return await executer_async(_create)


@router.put("/repas/{repas_id}", response_model=MessageResponse, responses=REPONSES_CRUD_ECRITURE)
@gerer_exception_api
async def modifier_repas(
    repas_id: int, maj: RepasCreate, user: dict[str, Any] = Depends(require_auth)
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

            db_repas.type_repas = maj.type_repas
            db_repas.recette_id = maj.recette_id
            if hasattr(db_repas, "notes") and maj.notes:
                db_repas.notes = maj.notes

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


# ----------------------------------------------------------
# VALIDATION & CONSOMMATION
# ----------------------------------------------------------


@router.post(
    "/{planning_id}/valider",
    response_model=MessageResponse,
    responses=REPONSES_CRUD_ECRITURE,
)
@gerer_exception_api
async def valider_planning(
    planning_id: int,
    background_tasks: "BackgroundTasks",
    user: dict[str, Any] = Depends(require_auth),
) -> MessageResponse:
    """Valide un planning brouillon et active la génération des courses.

    Le planning passe à l'état ``valide``. Les autres plannings validés de la
    même semaine sont archivés.
    """
    from src.core.models import Planning

    def _valider():
        with executer_avec_session() as session:
            planning = session.query(Planning).filter(Planning.id == planning_id).first()
            if not planning:
                raise HTTPException(status_code=404, detail="Planning non trouvé")

            if planning.etat == "valide":
                return MessageResponse(
                    message="Planning déjà validé",
                    id=planning_id,
                    data={
                        "semaine_debut": planning.semaine_debut.isoformat()
                        if planning.semaine_debut
                        else None,
                        "etat": planning.etat,
                    },
                )

            if planning.etat != "brouillon":
                raise HTTPException(
                    status_code=409,
                    detail=f"Le planning ne peut pas être validé depuis l'état '{planning.etat}'",
                )

            # Désactiver les plannings actifs de la même semaine
            session.query(Planning).filter(
                Planning.semaine_debut == planning.semaine_debut,
                Planning.id != planning_id,
                Planning.etat.in_(["valide", "actif"]),
            ).update({"etat": "archive"})

            planning.etat = "valide"
            session.commit()

            return MessageResponse(
                message="Planning validé",
                id=planning_id,
                data={
                    "semaine_debut": planning.semaine_debut.isoformat()
                    if planning.semaine_debut
                    else None,
                    "etat": planning.etat,
                },
            )

    resultat = await executer_async(_valider)
    resultat_data = getattr(resultat, "data", None)
    semaine_debut = resultat_data.get("semaine_debut") if isinstance(resultat_data, dict) else None

    # Bridge inter-modules : validation planning -> génération courses automatique.
    try:
        from src.services.core.events import obtenir_bus

        payload_event = {
            "planning_id": planning_id,
            "semaine_debut": semaine_debut,
            "user_id": user.get("sub", user.get("id")),
        }

        # Legacy event name currently wired in subscribers.
        obtenir_bus().emettre(
            "planning.valide",
            payload_event,
            source="api.planning.valider",
        )

        # Événement bridge inter-modules.
        obtenir_bus().emettre(
            "planning.semaine_validee",
            {
                **payload_event,
            },
            source="api.planning.valider",
        )
    except Exception as exc:
        logger.debug("Emission event planning.semaine_validee ignorée: %s", exc)

    # Notification Telegram best-effort après validation — en tâche de fond
    # pour ne pas bloquer la réponse HTTP (le dispatcher utilise time.sleep()
    # pour ses retries, ce qui bloquerait la boucle d'événements asyncio).
    def _notifier_validation() -> None:
        try:
            from src.services.core.notifications import get_dispatcher_notifications

            semaine = semaine_debut
            if semaine:
                try:
                    from datetime import date as _date
                    semaine_formatee = _date.fromisoformat(semaine).strftime("du %d/%m")
                except Exception:
                    semaine_formatee = semaine
            else:
                semaine_formatee = "de la semaine"
            message = (
                f"✅ Planning validé ({semaine_formatee}). "
                "La semaine est activée et prête pour les courses."
            )
            dispatcher = get_dispatcher_notifications()
            dispatcher.envoyer(
                user_id=str(user.get("id", user.get("sub", ""))),
                message=message,
                canaux=["telegram"],
                titre="Planning validé",
                strategie="failover",
            )
        except Exception as exc:
            logger.debug("Notification Telegram planning non envoyée: %s", exc)

    background_tasks.add_task(_notifier_validation)

    # Enrichir les recettes stubs du planning (étapes + ingrédients) en arrière-plan.
    # Déclenché à la validation pour couvrir aussi les stubs créés avant ce correctif.
    try:
        from src.services.cuisine.planning import obtenir_service_planning

        _service_planning = obtenir_service_planning()
        background_tasks.add_task(
            _service_planning.enrichir_recettes_stub_planning, planning_id
        )
    except Exception as _enr_exc:
        logger.debug("[planning] Enrichissement stubs au démarrage ignoré: %s", _enr_exc)

    return resultat


@router.post(
    "/{planning_id}/copier",
    response_model=MessageResponse,
    responses=REPONSES_CRUD_CREATION,
)
@gerer_exception_api
async def copier_planning(
    planning_id: int,
    semaine_debut: date = Query(..., description="Date du lundi de la semaine cible (YYYY-MM-DD)"),
    user: dict[str, Any] = Depends(require_auth),
) -> MessageResponse:
    """Copie un planning existant vers une nouvelle semaine.

    Duplique tous les repas du planning source en recalculant les dates
    pour la semaine cible. Le nouveau planning est créé en état brouillon.
    """
    from src.core.models import Planning, Repas

    def _copier():
        with executer_avec_session() as session:
            source = session.query(Planning).filter(Planning.id == planning_id).first()
            if not source:
                raise HTTPException(status_code=404, detail="Planning source non trouvé")

            semaine_fin = semaine_debut + timedelta(days=6)

            # Vérifier qu'il n'existe pas déjà un planning pour cette semaine
            existant = (
                session.query(Planning).filter(Planning.semaine_debut == semaine_debut).first()
            )
            if existant:
                raise HTTPException(
                    status_code=409,
                    detail=f"Un planning existe déjà pour la semaine du {semaine_debut.isoformat()}",
                )

            nouveau = Planning(
                nom=f"Copie — semaine du {semaine_debut.strftime('%d/%m')}",
                semaine_debut=semaine_debut,
                semaine_fin=semaine_fin,
                etat="brouillon",
                genere_par_ia=False,
                notes=f"Copié depuis le planning #{planning_id}",
            )
            session.add(nouveau)
            session.flush()

            # Calculer le décalage entre les deux semaines
            if source.semaine_debut:
                delta_jours = (semaine_debut - source.semaine_debut).days
            else:
                delta_jours = 0

            repas_source = session.query(Repas).filter(Repas.planning_id == planning_id).all()

            nb_copies = 0
            for repas in repas_source:
                nouvelle_date = (
                    repas.date_repas + timedelta(days=delta_jours)
                    if repas.date_repas
                    else semaine_debut
                )
                nouveau_repas = Repas(
                    planning_id=nouveau.id,
                    recette_id=repas.recette_id,
                    date_repas=nouvelle_date,
                    type_repas=repas.type_repas,
                    portion_ajustee=repas.portion_ajustee,
                    notes=repas.notes,
                    entree=repas.entree,
                    entree_recette_id=repas.entree_recette_id,
                    dessert=repas.dessert,
                    dessert_recette_id=repas.dessert_recette_id,
                    dessert_jules=repas.dessert_jules,
                    dessert_jules_recette_id=repas.dessert_jules_recette_id,
                    plat_jules=repas.plat_jules,
                    notes_jules=repas.notes_jules,
                    adaptation_auto=repas.adaptation_auto,
                )
                session.add(nouveau_repas)
                nb_copies += 1

            session.commit()
            return MessageResponse(
                message=f"Planning copié avec {nb_copies} repas",
                id=nouveau.id,
                data={
                    "semaine_debut": semaine_debut.isoformat(),
                    "semaine_fin": semaine_fin.isoformat(),
                    "nb_repas": nb_copies,
                },
            )

    return await executer_async(_copier)


@router.post(
    "/{planning_id}/regenerer",
    response_model=MessageResponse,
    responses=REPONSES_CRUD_ECRITURE,
)
@gerer_exception_api
async def regenerer_planning(
    planning_id: int,
    user: dict[str, Any] = Depends(require_auth),
) -> MessageResponse:
    """Régénère un planning en conservant la semaine, puis remet en brouillon."""
    from src.services.cuisine.planning import obtenir_service_planning

    def _regenerer() -> MessageResponse:
        from src.core.models import Planning

        with executer_avec_session() as session:
            planning_courant = session.query(Planning).filter(Planning.id == planning_id).first()
            if not planning_courant:
                raise HTTPException(status_code=404, detail="Planning non trouvé")

            if planning_courant.etat == "archive":
                raise HTTPException(
                    status_code=409,
                    detail="Impossible de régénérer un planning archivé",
                )

            semaine_debut = planning_courant.semaine_debut
            planning_courant.etat = "archive"
            session.commit()

        service = obtenir_service_planning()
        nouveau = service.generer_planning_ia(semaine_debut=semaine_debut, preferences={})
        if not nouveau:
            raise HTTPException(status_code=503, detail="Impossible de régénérer le planning")

        with executer_avec_session() as session:
            planning_nouveau = session.query(Planning).filter(Planning.id == nouveau.id).first()
            if planning_nouveau:
                planning_nouveau.etat = "brouillon"
                session.commit()

        return MessageResponse(
            message="Nouveau brouillon généré",
            id=nouveau.id,
            data={
                "semaine_debut": semaine_debut.isoformat(),
                "planning_source_id": planning_id,
            },
        )

    return await executer_async(_regenerer)


@router.post(
    "/{planning_id}/adapter-jules",
    response_model=MessageResponse,
    responses=REPONSES_CRUD_ECRITURE,
)
@gerer_exception_api
async def adapter_planning_jules(
    planning_id: int,
    user: dict[str, Any] = Depends(require_auth),
) -> MessageResponse:
    """Adapte TOUS les repas d'une semaine pour Jules (IM1).

    Génère une version Jules pour chaque repas du planning, en tenant compte de:
    - L'âge de Jules
    - Ses aliments exclus
    - Les règles de nutrition pédiatrique

    Les adaptations sont auto-persistées dans les champs plat_jules / notes_jules
    de chaque repas.

    Args:
        planning_id: ID du planning à adapter

    Returns:
        Message avec résumé des adaptations (nombre réussi, erreurs)

    Example:
        ```
        POST /api/v1/planning/15/adapter-jules
        Response:
        {
            "message": "5 repas adaptés pour Jules, 0 erreurs",
            "nb_adapte": 5,
            "nb_erreurs": 0
        }
        ```
    """
    from src.services.famille import obtenir_version_recette_jules_service

    def _adapter():
        try:
            service = obtenir_version_recette_jules_service()
            result = service.adapter_planning(planning_id)

            return MessageResponse(
                message=result.get("summary", "Planning adapté"),
                id=planning_id,
                data={
                    "nb_adapte": result.get("adapte", 0),
                    "nb_erreurs": result.get("erreurs", 0),
                    "details": result.get("details", []),
                },
            )
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))

    return await executer_async(_adapter)


@router.get(
    "/repas/{repas_id}/alternatives",
    responses=REPONSES_LISTE,
)
@gerer_exception_api
async def obtenir_alternatives_repas(
    repas_id: int,
    nb: int = Query(3, ge=1, le=5, description="Nombre d'alternatives à proposer"),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Retourne des recettes alternatives pour un slot de repas.

    Utilise les contraintes du jour (équilibre, type de repas) pour proposer
    des alternatives cohérentes via la logique IA existante.
    """
    from src.core.models import Recette, Repas

    def _alternatives():
        with executer_avec_session() as session:
            repas = session.query(Repas).filter(Repas.id == repas_id).first()
            if not repas:
                raise HTTPException(status_code=404, detail="Repas non trouvé")

            # Exclure la recette actuelle
            exclude_ids = [repas.recette_id] if repas.recette_id else []

            # Chercher des alternatives du même type de repas
            query = session.query(Recette).filter(Recette.id.notin_(exclude_ids))

            # Priorité aux rapides pour le soir
            if repas.type_repas in ("dîner", "diner"):
                query = query.order_by(Recette.temps_total.asc().nullslast())

            alternatives = query.limit(nb * 3).all()

            # Sélectionner les meilleures alternatives (variété de catégories)
            seen_categories: set[str] = set()
            result = []
            for r in alternatives:
                cat = r.categorie or "Autre"
                if len(result) >= nb:
                    break
                if cat not in seen_categories or len(result) < nb:
                    seen_categories.add(cat)
                    result.append(
                        {
                            "id": r.id,
                            "nom": r.nom,
                            "temps_total": r.temps_total,
                            "difficulte": r.difficulte,
                            "categorie": r.categorie,
                            "tag_robot_cookeo": r.tag_robot_cookeo
                            if hasattr(r, "tag_robot_cookeo")
                            else False,
                            "tag_robot_airfryer": r.tag_robot_airfryer
                            if hasattr(r, "tag_robot_airfryer")
                            else False,
                            "tag_bio": r.tag_bio if hasattr(r, "tag_bio") else False,
                            "tag_local": r.tag_local if hasattr(r, "tag_local") else False,
                            "photo_url": r.photo_url if hasattr(r, "photo_url") else None,
                        }
                    )

            return {
                "repas_id": repas_id,
                "date_repas": repas.date_repas.isoformat(),
                "type_repas": repas.type_repas,
                "alternatives": result,
            }

    return await executer_async(_alternatives)


# ----------------------------------------------------------
# GÉNÉRATION IA
# ----------------------------------------------------------


@router.post("/ia/circuit-reset", response_model=MessageResponse)
@gerer_exception_api
async def reset_circuit_breaker_ia(
    user: dict[str, Any] = Depends(require_auth),
) -> MessageResponse:
    """Réinitialise le circuit breaker IA (utile après correction d'une panne transitoire)."""
    from src.core.ai.circuit_breaker import EtatCircuit, obtenir_circuit

    cb = obtenir_circuit("ai_planning", seuil_echecs=5, delai_reset=60.0)
    etat_avant = cb.obtenir_statistiques().get("etat", "unknown")
    with cb._lock:
        cb._etat = EtatCircuit.FERME
        cb._echecs_consecutifs = 0
    logger.info(
        "[planning] Circuit breaker IA réinitialisé par %s: %s → closed", user.get("id"), etat_avant
    )
    return MessageResponse(message=f"Circuit breaker réinitialisé ({etat_avant} → closed)")


@router.post("/generer", response_model=PlanningSemaineResponse)
@gerer_exception_api
async def generer_planning_ia(
    background_tasks: BackgroundTasks,
    body: GenererPlanningRequest | None = None,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """
    Génère un planning de repas hebdomadaire via l'IA Mistral.

    Crée 7 jours × 2 repas (déjeuner + dîner) en utilisant Mistral AI.
    Persiste directement les repas dans la DB.
    Enrichit les recettes stubs (étapes + ingrédients) en arrière-plan.

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

    from src.services.cuisine.planning import obtenir_service_planning

    # Vérification anticipée : la clé Mistral doit être configurée
    try:
        from src.core.config import obtenir_parametres

        _ = obtenir_parametres().MISTRAL_API_KEY  # Lève ValueError si absente
    except Exception:
        raise HTTPException(
            status_code=503,
            detail=(
                "L'IA Mistral n'est pas configurée. "
                "Ajoutez MISTRAL_API_KEY dans vos variables d'environnement "
                "pour utiliser la génération automatique de planning."
            ),
        )

    if body is None:
        body = GenererPlanningRequest()

    # Calculer le lundi de la semaine
    today = date.today()
    if body.date_debut:
        semaine_debut = body.date_debut
    else:
        semaine_debut = today - timedelta(days=today.weekday())

    def _generate():
        from sqlalchemy import func

        from src.core.models import Recette
        from src.core.models.finances import Depense
        from src.core.models.inventaire import ArticleInventaire
        from src.core.models.recettes import HistoriqueRecette

        # Enrichir les préférences avec signaux historiques + nutrition
        preferences_base = getattr(body, "preferences", None) or {}
        preferences_enrichies = dict(preferences_base)

        # Chaque enrichissement est isolé : un échec n'interrompt pas la génération.
        try:
            with executer_avec_session() as session:
                top_recettes = (
                    session.query(Recette.nom, func.count(HistoriqueRecette.id).label("nb"))
                    .join(HistoriqueRecette, HistoriqueRecette.recette_id == Recette.id)
                    .group_by(Recette.id, Recette.nom)
                    .order_by(func.count(HistoriqueRecette.id).desc())
                    .limit(8)
                    .all()
                )
                if top_recettes:
                    preferences_enrichies["recettes_favorites"] = [
                        {"nom": r.nom, "frequence": int(r.nb or 0)}
                        for r in top_recettes[:5]  # Top 5 seulement
                    ]
        except Exception as e:
            logger.warning("[planning] Enrichissement recettes favorites ignoré: %s", e)

        try:
            with executer_avec_session() as session:
                stats_nutri = (
                    session.query(
                        func.avg(Recette.calories).label("avg_cal"),
                        func.avg(Recette.proteines).label("avg_prot"),
                        func.avg(Recette.lipides).label("avg_lip"),
                        func.avg(Recette.glucides).label("avg_glu"),
                    )
                    .filter(Recette.calories.isnot(None))
                    .first()
                )
                avg_cal = float(getattr(stats_nutri, "avg_cal", 900) or 900)
                avg_prot = float(getattr(stats_nutri, "avg_prot", 25) or 25)
                avg_lip = float(getattr(stats_nutri, "avg_lip", 20) or 20)
                avg_glu = float(getattr(stats_nutri, "avg_glu", 55) or 55)
                cal_cible = max(1500, min(2800, int(avg_cal * 2)))
                preferences_enrichies["objectif_nutrition"] = {
                    "calories_jour_cible": cal_cible,
                    "proteines_min_jour": round(avg_prot * 2, 1),
                    "lipides_max_jour": round(avg_lip * 2.2, 1),
                    "glucides_cible_jour": round(avg_glu * 2, 1),
                }
        except Exception as e:
            logger.warning("[planning] Enrichissement nutrition ignoré: %s", e)

        try:
            with executer_avec_session() as session:
                inventaire_disponible = (
                    session.query(ArticleInventaire)
                    .filter(ArticleInventaire.quantite > 0)
                    .order_by(ArticleInventaire.quantite.desc())
                    .limit(40)
                    .all()
                )
                if inventaire_disponible:
                    preferences_enrichies["inventaire_disponible"] = [
                        {
                            "ingredient": item.nom,
                            "quantite": float(item.quantite or 0),
                            "unite": item.unite,
                        }
                        for item in inventaire_disponible[
                            :15
                        ]  # Limité à 15 pour réduire la taille du prompt
                        if item.nom
                    ]
        except Exception as e:
            logger.warning("[planning] Enrichissement inventaire ignoré: %s", e)

        try:
            with executer_avec_session() as session:
                debut_budget = datetime.now(UTC).date() - timedelta(days=60)
                depenses_alim = (
                    session.query(
                        func.sum(Depense.montant).label("total"), func.count(Depense.id).label("nb")
                    )
                    .filter(
                        Depense.categorie == "alimentation",
                        Depense.date >= debut_budget,
                    )
                    .first()
                )
                total_budget = float(getattr(depenses_alim, "total", 0) or 0)
                nb_depenses = int(getattr(depenses_alim, "nb", 0) or 0)
                preferences_enrichies["budget_alimentation"] = {
                    "periode_jours": 60,
                    "depenses_total": round(total_budget, 2),
                    "depense_moyenne": round(total_budget / nb_depenses, 2)
                    if nb_depenses > 0
                    else 0,
                    "nb_transactions": nb_depenses,
                }
        except Exception as e:
            logger.warning("[planning] Enrichissement budget ignoré: %s", e)

        # Enrichir avec les produits de saison du mois en cours (catalogue enrichi ~120 ingrédients)
        try:
            from src.services.cuisine.suggestions.saisons_enrichi import (
                INGREDIENTS_SAISON_ENRICHI,
                obtenir_saison,
            )

            mois_actuel = today.month
            saison_actuelle = obtenir_saison()
            produits_saison = [
                ing.nom
                for ing in INGREDIENTS_SAISON_ENRICHI.get(saison_actuelle, [])
                if mois_actuel in ing.pic_mois
            ]
            if produits_saison:
                preferences_enrichies["produits_de_saison"] = produits_saison
        except Exception as e:
            logger.warning("[planning] Enrichissement saisonnier non chargé: %s", e)

        from src.core.exceptions import ExceptionApp

        service = obtenir_service_planning()
        try:
            planning_obj = service.generer_planning_ia(
                semaine_debut=semaine_debut,
                preferences=preferences_enrichies,
            )
        except ExceptionApp as e:
            tech_msg = getattr(e, "message", "") or ""
            user_msg = getattr(
                e, "message_utilisateur", "Génération IA impossible. Réessayez plus tard."
            )
            logger.warning(
                "[planning] Exception métier depuis generer_planning_ia: %s — %s",
                type(e).__name__,
                tech_msg,
            )
            logger.warning("[planning] Détail technique: %s", tech_msg)
            raise HTTPException(status_code=503, detail=user_msg) from e
        except Exception as e:
            logger.error(
                "[planning] Erreur inattendue depuis generer_planning_ia: %s", e, exc_info=True
            )
            raise HTTPException(
                status_code=503,
                detail="Génération IA impossible. Réessayez plus tard.",
            ) from e

        if not planning_obj:
            raise HTTPException(
                status_code=503, detail="Impossible de générer le planning. Réessayez plus tard."
            )

        # Reconstruire la réponse dans le même format que GET /semaine
        with executer_avec_session() as session:
            from src.core.models import Planning, Repas
            from src.core.models.recettes import Recette

            planning_db = session.query(Planning).filter(Planning.id == planning_obj.id).first()
            if planning_db and planning_db.etat != "brouillon":
                planning_db.etat = "brouillon"
                session.commit()

            date_fin = semaine_debut + timedelta(days=7)
            repas = (
                session.query(Repas)
                .filter(
                    Repas.planning_id == planning_obj.id,
                )
                .order_by(Repas.date_repas)
                .all()
            )

            # Récupérer les noms de recettes en une seule requête
            # (plat principal + entrée + dessert)
            recette_ids = list(
                {
                    rid
                    for r in repas
                    for rid in (r.recette_id, r.entree_recette_id, r.dessert_recette_id)
                    if rid is not None
                }
            )
            recettes_map: dict[int, str] = {}
            if recette_ids:
                for rec in session.query(
                    Recette.id, Recette.nom, Recette.calories, Recette.proteines, Recette.lipides
                ).filter(Recette.id.in_(recette_ids)):
                    recettes_map[rec.id] = rec

            # Normalise les valeurs accentuées stockées en DB vers les valeurs
            # canoniques sans accents attendues par le frontend.
            _TYPE_NORM = {
                "petit_déjeuner": "petit_dejeuner",
                "déjeuner": "dejeuner",
                "dîner": "diner",
                "goûter": "gouter",
            }

            planning_dict = {}
            repas_list = []
            for r in repas:
                if not r.date_repas:
                    continue
                jour = r.date_repas.strftime("%Y-%m-%d")
                if jour not in planning_dict:
                    planning_dict[jour] = {}

                rec = recettes_map.get(r.recette_id) if r.recette_id else None
                recette_nom = rec.nom if rec else None
                rec_entree = recettes_map.get(r.entree_recette_id) if r.entree_recette_id else None
                rec_dessert = (
                    recettes_map.get(r.dessert_recette_id) if r.dessert_recette_id else None
                )
                type_repas = _TYPE_NORM.get(r.type_repas, r.type_repas)
                entry: dict = {
                    "id": r.id,
                    "recette_id": r.recette_id,
                    "notes": getattr(r, "notes", None),
                    "recette_nom": recette_nom,
                    "entree": getattr(r, "entree", None),
                    "entree_recette_id": getattr(r, "entree_recette_id", None),
                    "entree_recette_nom": rec_entree.nom if rec_entree else None,
                    "laitage": getattr(r, "laitage", None),
                    "dessert": getattr(r, "dessert", None),
                    "dessert_recette_id": getattr(r, "dessert_recette_id", None),
                    "dessert_recette_nom": rec_dessert.nom if rec_dessert else None,
                }
                if rec:
                    cal = rec.calories or 0
                    prot = rec.proteines or 0
                    lip = rec.lipides or 0
                    if cal > 0 or prot > 0:
                        score = 0
                        if cal > 600:
                            score += 2
                        elif cal > 400:
                            score += 1
                        if lip and lip > 20:
                            score += 2
                        elif lip and lip > 10:
                            score += 1
                        if prot > 20:
                            score -= 1
                        grade = ["a", "a", "b", "c", "d", "e"][min(score, 5)]
                        entry["nutri_score"] = grade

                planning_dict[jour][type_repas] = entry

                repas_list.append(
                    {
                        "id": r.id,
                        "date_repas": jour,
                        "type_repas": type_repas,
                        "recette_id": r.recette_id,
                        "recette_nom": recette_nom,
                        "notes": getattr(r, "notes", None),
                        "nutri_score": entry.get("nutri_score"),
                        "entree": getattr(r, "entree", None),
                        "entree_recette_id": getattr(r, "entree_recette_id", None),
                        "entree_recette_nom": rec_entree.nom if rec_entree else None,
                        "laitage": getattr(r, "laitage", None),
                        "dessert": getattr(r, "dessert", None),
                        "dessert_recette_id": getattr(r, "dessert_recette_id", None),
                        "dessert_recette_nom": rec_dessert.nom if rec_dessert else None,
                        "plat_jules": getattr(r, "plat_jules", None),
                        "notes_jules": getattr(r, "notes_jules", None),
                        "adaptation_auto": getattr(r, "adaptation_auto", True),
                    }
                )

            ia_success = bool(
                getattr(planning_db, "genere_par_ia", False) if planning_db else False
            )
            if not ia_success:
                raise HTTPException(
                    status_code=503,
                    detail="Le planning n'a pas pu être généré par l'IA. Réessayez dans quelques secondes.",
                )

            return {
                "date_debut": semaine_debut.isoformat(),
                "date_fin": date_fin.isoformat(),
                "planning_id": planning_obj.id,
                "genere_par_ia": True,
                "planning": planning_dict,
                "repas": repas_list,
            }

    resultat = await executer_async(_generate)

    # Enrichir les recettes stubs (étapes + ingrédients) en arrière-plan
    # pour ne pas bloquer la réponse HTTP (~5-8 s au lieu de 75 s).
    planning_id_bg = resultat.get("planning_id") if isinstance(resultat, dict) else None
    if planning_id_bg:
        from src.services.cuisine.planning import obtenir_service_planning

        background_tasks.add_task(
            obtenir_service_planning().enrichir_recettes_stub_planning,
            planning_id_bg,
        )

    return resultat


# ----------------------------------------------------------
# SUGGESTIONS RAPIDES
# ----------------------------------------------------------


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

    Retourne des recettes adaptées au type de repas, à la saison et à la météo,
    en excluant celles déjà planifiées cette semaine.
    """
    from src.core.models import Recette, Repas

    # Récupérer la météo (non bloquant - fallback si échec)
    meteo_ctx: dict[str, Any] = {}
    try:
        from src.services.utilitaires.meteo_service import obtenir_meteo_service

        meteo = obtenir_meteo_service().obtenir_meteo()
        if meteo.actuelle:
            meteo_ctx = {
                "temperature": meteo.actuelle.temperature,
                "description": meteo.actuelle.description,
                "emoji": meteo.actuelle.emoji,
            }
    except Exception as e:
        logger.warning("[planning] Météo non chargée pour suggestions rapides: %s", e)

    def _query():
        with executer_avec_session() as session:
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

            # Adaptation météo : favoriser catégories selon température
            categories_favorites: list[str] = []
            temp = meteo_ctx.get("temperature")
            if temp is not None:
                if temp < 10:
                    categories_favorites = ["Soupe", "Plat mijoté", "Gratin", "Plat"]
                elif temp > 25:
                    categories_favorites = ["Salade", "Entrée froide", "Smoothie"]

            # Trier par popularité (nombre d'historiques) et varier
            from sqlalchemy import case, func

            from src.core.models.recettes import HistoriqueRecette

            query = query.outerjoin(
                HistoriqueRecette, HistoriqueRecette.recette_id == Recette.id
            ).group_by(Recette.id)

            if categories_favorites:
                # Boost les catégories adaptées à la météo
                meteo_boost = case(
                    (Recette.categorie.in_(categories_favorites), 1),
                    else_=0,
                )
                query = query.order_by(
                    meteo_boost.desc(),
                    func.count(HistoriqueRecette.id).desc(),
                    func.random(),
                )
            else:
                query = query.order_by(
                    func.count(HistoriqueRecette.id).desc(),
                    func.random(),
                )

            recettes = query.limit(nombre).all()

            result: dict[str, Any] = {
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
            if meteo_ctx:
                result["meteo"] = meteo_ctx
            return result

    return await executer_async(_query)


# ----------------------------------------------------------
# EXPORT iCAL
# ----------------------------------------------------------


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
            date_debut = datetime.now(UTC).replace(hour=0, minute=0, second=0, microsecond=0)
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
                summary = f"{type_label} - {nom_recette}"

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
    - Signaux de carences probables + suggestions compensatoires
    """
    from datetime import date

    from src.core.models.planning import Repas
    from src.core.models.recettes import Recette
    from src.services.cuisine.nutrition import obtenir_service_nutrition

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

                par_jour[jour]["repas"].append(
                    {
                        "id": repas.id,
                        "type": repas.type_repas,
                        "nom_recette": recette.nom if recette else None,
                        "calories": int((recette.calories or 0) * facteur)
                        if recette and recette.calories
                        else None,
                    }
                )

            # Arrondis finaux
            totaux["proteines"] = round(totaux["proteines"], 1)
            totaux["lipides"] = round(totaux["lipides"], 1)
            totaux["glucides"] = round(totaux["glucides"], 1)

            nb_jours_avec_donnees = sum(1 for j in par_jour.values() if j["calories"] > 0)
            moyenne_calories = (
                round(totaux["calories"] / nb_jours_avec_donnees)
                if nb_jours_avec_donnees > 0
                else 0
            )

            service_nutrition = obtenir_service_nutrition()
            insights = service_nutrition.analyser_carences_et_suggestions(
                totaux_hebdo=totaux,
                nb_jours=nb_jours_avec_donnees,
            )

            return {
                "semaine_debut": debut.isoformat(),
                "semaine_fin": fin.isoformat(),
                "totaux": totaux,
                "moyenne_calories_par_jour": moyenne_calories,
                "par_jour": par_jour,
                "nb_repas_sans_donnees": sans_donnees,
                "nb_repas_total": len(repas_liste),
                "insights": insights,
            }

    return await executer_async(_query)


# ===========================================================
# SEMAINE UNIFIEE - Vue trans-modules (AC1)
# ===========================================================


@router.get("/semaine-unifiee", responses=REPONSES_LISTE)
@gerer_exception_api
async def obtenir_semaine_unifiee(
    date_debut: str | None = Query(
        None,
        description="Date de début de semaine ISO (YYYY-MM-DD). Défaut: lundi courant.",
    ),
    user: dict = Depends(require_auth),
) -> dict:
    """Vue unifiee de la semaine trans-modules.

    Agrege en une seule reponse:
    - repas: planning repas (dejeuner/diner par jour)
    - taches_maison: taches menage/entretien du jour
    - activites_famille: activites Jules et famille de la semaine
    - meta: dates de debut/fin de semaine
    """
    import datetime as dt

    from src.core.models.planning import Repas

    if date_debut:
        debut = dt.date.fromisoformat(date_debut)
    else:
        aujourd_hui = dt.date.today()
        debut = aujourd_hui - dt.timedelta(days=aujourd_hui.weekday())
    fin = debut + dt.timedelta(days=6)

    def _query() -> dict:
        with executer_avec_session() as session:
            # Repas
            repas_liste = (
                session.query(Repas)
                .filter(
                    Repas.date_repas >= debut,
                    Repas.date_repas <= fin,
                )
                .order_by(Repas.date_repas)
                .all()
            )

            # Charger les noms de recettes en une seule requête (évite le lazy-loading N+1)
            recette_ids = [r.recette_id for r in repas_liste if r.recette_id]
            recettes_map: dict[int, str] = {}
            if recette_ids:
                from src.core.models.recettes import Recette as RecetteModel

                for rec in session.query(RecetteModel.id, RecetteModel.nom).filter(
                    RecetteModel.id.in_(recette_ids)
                ):
                    recettes_map[rec.id] = rec.nom

            repas_par_jour: dict[str, list[dict]] = {}
            for r in repas_liste:
                jour = r.date_repas.isoformat()
                repas_par_jour.setdefault(jour, []).append(
                    {
                        "id": r.id,
                        "type": r.type_repas,
                        "recette_id": r.recette_id,
                        "nom_recette": recettes_map.get(r.recette_id) if r.recette_id else None,
                    }
                )

            # Activites famille
            activites: list[dict] = []
            try:
                from src.core.models.famille import ActiviteFamille

                acts = (
                    session.query(ActiviteFamille)
                    .filter(
                        ActiviteFamille.date_prevue >= debut,
                        ActiviteFamille.date_prevue <= fin,
                    )
                    .order_by(ActiviteFamille.date_prevue)
                    .all()
                )
                activites = [
                    {
                        "id": a.id,
                        "date": a.date_prevue.isoformat() if a.date_prevue else None,
                        "titre": a.titre,
                        "type": getattr(a, "type_activite", None),
                    }
                    for a in acts
                ]
            except Exception as e:
                logger.warning("[planning] Activites famille non chargees pour ma-semaine: %s", e)

            # Taches maison (non disponible pour l'instant)
            taches_maison: list[dict] = []

            return {
                "meta": {
                    "semaine_debut": debut.isoformat(),
                    "semaine_fin": fin.isoformat(),
                },
                "repas": repas_par_jour,
                "activites_famille": activites,
                "taches_maison": taches_maison,
            }

    return await executer_async(_query)
