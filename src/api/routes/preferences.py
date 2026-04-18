"""
Routes API pour les préférences utilisateur.

CRUD pour les préférences alimentaires, robots, magasins.
W4 : ajout endpoints préférences canaux de notification.
"""

import logging
from typing import Any, cast
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query

from src.api.dependencies import require_auth
from src.api.schemas.errors import REPONSES_CRUD_ECRITURE, REPONSES_CRUD_LECTURE, REPONSES_IA
from src.api.schemas.ia_transverses import (
    ApprentissageHabitudesResponse,
    ApprentissagePreferencesResponse,
    ModePiloteAutomatiqueResponse,
    ModePiloteConfigurationRequest,
)
from src.api.schemas.preferences import (
    PreferencesCreate,
    PreferencesNotificationsUpdate,
    PreferencesPatch,
)
from src.api.utils import executer_async, executer_avec_session, gerer_exception_api
from src.services.core.service_ia import obtenir_service_innovations_core

router = APIRouter(prefix="/api/v1/preferences", tags=["Préférences"])


@router.get("/apprentissage-habitudes", responses=REPONSES_IA)
@gerer_exception_api
async def apprentissage_habitudes(
    user: dict[str, Any] = Depends(require_auth),
) -> ApprentissageHabitudesResponse:
    """Alias métier pour l'apprentissage continu des habitudes utilisateur."""
    service = obtenir_service_innovations_core()
    result = service.apprendre_habitudes_utilisateur()
    return result or ApprentissageHabitudesResponse()


@router.get("/mode-pilote", responses=REPONSES_IA)
@gerer_exception_api
async def lire_mode_pilote(
    user: dict[str, Any] = Depends(require_auth),
) -> ModePiloteAutomatiqueResponse:
    """Alias métier pour la lecture du mode pilote automatique."""
    service = obtenir_service_innovations_core()
    user_id_raw = user.get("id")
    user_id = (
        int(user_id_raw)
        if isinstance(user_id_raw, (int, str)) and str(user_id_raw).isdigit()
        else None
    )
    result = service.obtenir_mode_pilote_automatique(user_id=user_id)
    return result or ModePiloteAutomatiqueResponse()


@router.post("/mode-pilote/config", responses=REPONSES_IA)
@gerer_exception_api
async def configurer_mode_pilote(
    body: ModePiloteConfigurationRequest,
    user: dict[str, Any] = Depends(require_auth),
) -> ModePiloteAutomatiqueResponse:
    """Alias métier pour la configuration du mode pilote automatique."""
    service = obtenir_service_innovations_core()
    user_id_raw = user.get("id")
    user_id = (
        int(user_id_raw)
        if isinstance(user_id_raw, (int, str)) and str(user_id_raw).isdigit()
        else None
    )
    result = service.configurer_mode_pilote_automatique(
        user_id=user_id,
        actif=body.actif,
        niveau_autonomie=body.niveau_autonomie,
    )
    return result or ModePiloteAutomatiqueResponse(actif=body.actif)


@router.get("/preferences-apprises", responses=REPONSES_IA)
@gerer_exception_api
async def preferences_apprises(
    user: dict[str, Any] = Depends(require_auth),
) -> ApprentissagePreferencesResponse:
    """Alias métier pour les préférences apprises par l'IA."""
    service = obtenir_service_innovations_core()
    user_id = str(user.get("id") or "")
    result = service.analyser_preferences_apprises(user_id=user_id)
    return result or ApprentissagePreferencesResponse()


logger = logging.getLogger(__name__)


@router.get("", responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def obtenir_preferences(
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Récupère les préférences de l'utilisateur courant."""
    from src.core.models import PreferenceUtilisateur

    def _query():
        with executer_avec_session() as session:
            prefs = (
                session.query(PreferenceUtilisateur)
                .filter(PreferenceUtilisateur.user_id == user["id"])
                .first()
            )

            if not prefs:
                # Retourner les valeurs par défaut
                return {
                    "user_id": user["id"],
                    "nb_adultes": 2,
                    "jules_present": True,
                    "jules_age_mois": None,
                    "temps_semaine": 30,
                    "temps_weekend": 60,
                    "aliments_exclus": [],
                    "aliments_favoris": [],
                    "nb_poisson_blanc": 1,
                    "nb_poisson_gras": 1,
                    "vegetarien_par_semaine": 1,
                    "viande_rouge_max": 2,
                    "robots": [],
                    "magasins_preferes": [],
                }

            return {
                "user_id": prefs.user_id,
                "nb_adultes": prefs.nb_adultes,
                "jules_present": prefs.jules_present,
                "jules_age_mois": prefs.jules_age_mois,
                "temps_semaine": prefs.temps_semaine,
                "temps_weekend": prefs.temps_weekend,
                "aliments_exclus": prefs.aliments_exclus or [],
                "aliments_favoris": prefs.aliments_favoris or [],
                "nb_poisson_blanc": prefs.nb_poisson_blanc,
                "nb_poisson_gras": prefs.nb_poisson_gras,
                "vegetarien_par_semaine": prefs.vegetarien_par_semaine,
                "viande_rouge_max": prefs.viande_rouge_max,
                "robots": prefs.robots or [],
                "magasins_preferes": prefs.magasins_preferes or [],
            }

    return await executer_async(_query)


@router.put("", responses=REPONSES_CRUD_ECRITURE)
@gerer_exception_api
async def creer_ou_modifier_preferences(
    donnees: PreferencesCreate,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Crée ou remplace les préférences utilisateur (upsert)."""
    from src.core.models import PreferenceUtilisateur

    def _upsert():
        with executer_avec_session() as session:
            prefs = (
                session.query(PreferenceUtilisateur)
                .filter(PreferenceUtilisateur.user_id == user["id"])
                .first()
            )

            if prefs:
                for key, value in donnees.model_dump().items():
                    setattr(prefs, key, value)
            else:
                prefs = PreferenceUtilisateur(
                    user_id=user["id"],
                    **donnees.model_dump(),
                )
                session.add(prefs)

            session.commit()
            session.refresh(prefs)

            return {
                "user_id": prefs.user_id,
                "nb_adultes": prefs.nb_adultes,
                "jules_present": prefs.jules_present,
                "jules_age_mois": prefs.jules_age_mois,
                "temps_semaine": prefs.temps_semaine,
                "temps_weekend": prefs.temps_weekend,
                "aliments_exclus": prefs.aliments_exclus or [],
                "aliments_favoris": prefs.aliments_favoris or [],
                "nb_poisson_blanc": prefs.nb_poisson_blanc,
                "nb_poisson_gras": prefs.nb_poisson_gras,
                "vegetarien_par_semaine": prefs.vegetarien_par_semaine,
                "viande_rouge_max": prefs.viande_rouge_max,
                "robots": prefs.robots or [],
                "magasins_preferes": prefs.magasins_preferes or [],
            }

    return await executer_async(_upsert)


@router.patch("", responses=REPONSES_CRUD_ECRITURE)
@gerer_exception_api
async def modifier_preferences(
    maj: PreferencesPatch,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Met à jour partiellement les préférences."""
    from src.core.models import PreferenceUtilisateur

    def _update():
        with executer_avec_session() as session:
            prefs = (
                session.query(PreferenceUtilisateur)
                .filter(PreferenceUtilisateur.user_id == user["id"])
                .first()
            )

            if not prefs:
                raise HTTPException(
                    status_code=404,
                    detail="Préférences non trouvées. Utilisez PUT pour créer.",
                )

            updates = maj.model_dump(exclude_unset=True)
            if not updates:
                raise HTTPException(status_code=422, detail="Aucun champ à mettre à jour")

            for key, value in updates.items():
                setattr(prefs, key, value)

            session.commit()
            session.refresh(prefs)

            return {
                "user_id": prefs.user_id,
                "nb_adultes": prefs.nb_adultes,
                "jules_present": prefs.jules_present,
                "jules_age_mois": prefs.jules_age_mois,
                "temps_semaine": prefs.temps_semaine,
                "temps_weekend": prefs.temps_weekend,
                "aliments_exclus": prefs.aliments_exclus or [],
                "aliments_favoris": prefs.aliments_favoris or [],
                "nb_poisson_blanc": prefs.nb_poisson_blanc,
                "nb_poisson_gras": prefs.nb_poisson_gras,
                "vegetarien_par_semaine": prefs.vegetarien_par_semaine,
                "viande_rouge_max": prefs.viande_rouge_max,
                "robots": prefs.robots or [],
                "magasins_preferes": prefs.magasins_preferes or [],
            }

    return await executer_async(_update)


# ─────────────────────────────────────────────────────────
# Valeurs par défaut du modal de génération de planning
# ─────────────────────────────────────────────────────────

_PLANNING_DEFAULTS_KEY = "planning"
_PLANNING_DEFAULTS_DEFAULT: dict[str, Any] = {
    "legumes_souhaites": [],
    "feculents_souhaites": [],
    "plats_souhaites": [],
    "ingredients_interdits": [],
    "autoriser_restes": True,
    "nb_personnes": 4,
}


@router.get("/planning-defaults", responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def obtenir_planning_defaults(
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Récupère les valeurs par défaut du modal de génération de planning."""
    from src.core.models import PreferenceUtilisateur

    def _query():
        with executer_avec_session() as session:
            prefs = (
                session.query(PreferenceUtilisateur)
                .filter(PreferenceUtilisateur.user_id == user["id"])
                .first()
            )
            if not prefs:
                return dict(_PLANNING_DEFAULTS_DEFAULT)
            config = prefs.config_dashboard or {}
            stored = config.get(_PLANNING_DEFAULTS_KEY, {})
            return {**_PLANNING_DEFAULTS_DEFAULT, **stored}

    return await executer_async(_query)


@router.patch("/planning-defaults", responses=REPONSES_CRUD_ECRITURE)
@gerer_exception_api
async def sauvegarder_planning_defaults(
    body: dict[str, Any],
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Sauvegarde les valeurs par défaut du modal de génération de planning."""
    from src.core.models import PreferenceUtilisateur

    def _update():
        with executer_avec_session() as session:
            prefs = (
                session.query(PreferenceUtilisateur)
                .filter(PreferenceUtilisateur.user_id == user["id"])
                .first()
            )
            if not prefs:
                raise HTTPException(
                    status_code=404,
                    detail="Préférences non trouvées. Utilisez PUT /preferences pour créer.",
                )
            config: dict[str, Any] = dict(prefs.config_dashboard or {})
            existing = config.get(_PLANNING_DEFAULTS_KEY, {})
            merged = {**_PLANNING_DEFAULTS_DEFAULT, **existing, **body}
            config[_PLANNING_DEFAULTS_KEY] = merged
            prefs.config_dashboard = config
            session.commit()
            return merged

    return await executer_async(_update)


# ─────────────────────────────────────────────────────────
# Préférences canaux de notification (W4)
# ─────────────────────────────────────────────────────────

_CANAUX_DEFAULTS: dict[str, list[str]] = {
    "rappels": ["push", "ntfy"],
    "alertes": ["push", "ntfy", "email"],
    "resumes": ["email"],
}

_NOTIFICATIONS_MODULES_DEFAULTS: dict[str, bool] = {
    "cuisine": True,
    "famille": True,
    "maison": True,
    "planning": True,
    "jeux": True,
}


def _notif_to_dict(prefs: Any, user_id: str) -> dict[str, Any]:
    """Sérialise une PreferenceNotification en dict API."""
    canaux_par_cat = prefs.canaux_par_categorie or _CANAUX_DEFAULTS
    modules_actifs: dict[str, Any] = dict(prefs.modules_actifs or {})
    notifications_brut = modules_actifs.get("notifications_par_module") or {}
    notifications_par_module_source: dict[str, Any] = (
        cast(dict[str, Any], notifications_brut) if isinstance(notifications_brut, dict) else {}
    )
    notifications_par_module = {
        **_NOTIFICATIONS_MODULES_DEFAULTS,
        **{k: bool(v) for k, v in notifications_par_module_source.items() if isinstance(k, str)},
    }
    return {
        "user_id": user_id,
        "courses_rappel": prefs.courses_rappel,
        "repas_suggestion": prefs.repas_suggestion,
        "stock_alerte": prefs.stock_alerte,
        "meteo_alerte": prefs.meteo_alerte,
        "budget_alerte": prefs.budget_alerte,
        "canal_prefere": prefs.canal_prefere or "push",
        "canaux_par_categorie": {
            "rappels": canaux_par_cat.get("rappels", _CANAUX_DEFAULTS["rappels"]),
            "alertes": canaux_par_cat.get("alertes", _CANAUX_DEFAULTS["alertes"]),
            "resumes": canaux_par_cat.get("resumes", _CANAUX_DEFAULTS["resumes"]),
        },
        "notifications_par_module": notifications_par_module,
        "quiet_hours_start": str(prefs.quiet_hours_start or "22:00")[:5],
        "quiet_hours_end": str(prefs.quiet_hours_end or "07:00")[:5],
        "max_par_heure": int(modules_actifs.get("max_par_heure", 5)),
        "mode_digest": bool(modules_actifs.get("mode_digest", False)),
        "mode_vacances": bool(modules_actifs.get("mode_vacances", False)),
        "checklist_voyage_auto": bool(modules_actifs.get("checklist_voyage_auto", True)),
    }


@router.get("/notifications", responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def obtenir_preferences_notifications(
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Récupère les préférences de canaux de notification de l'utilisateur."""
    from src.core.models.notifications import PreferenceNotification

    def _query():
        try:
            user_uuid = UUID(str(user["id"]))
        except (ValueError, AttributeError):
            # user_id non-UUID (ex: mode dev) — retourner les valeurs par défaut
            return {
                "user_id": user["id"],
                "courses_rappel": True,
                "repas_suggestion": True,
                "stock_alerte": True,
                "meteo_alerte": True,
                "budget_alerte": True,
                "canal_prefere": "push",
                "canaux_par_categorie": _CANAUX_DEFAULTS,
                "notifications_par_module": _NOTIFICATIONS_MODULES_DEFAULTS,
                "quiet_hours_start": "22:00",
                "quiet_hours_end": "07:00",
                "max_par_heure": 5,
                "mode_digest": False,
                "mode_vacances": False,
                "checklist_voyage_auto": True,
            }
        with executer_avec_session() as session:
            prefs = (
                session.query(PreferenceNotification)
                .filter(PreferenceNotification.user_id == user_uuid)
                .first()
            )

            if not prefs:
                # Retourner les valeurs par défaut
                return {
                    "user_id": user["id"],
                    "courses_rappel": True,
                    "repas_suggestion": True,
                    "stock_alerte": True,
                    "meteo_alerte": True,
                    "budget_alerte": True,
                    "canal_prefere": "push",
                    "canaux_par_categorie": _CANAUX_DEFAULTS,
                    "notifications_par_module": _NOTIFICATIONS_MODULES_DEFAULTS,
                    "quiet_hours_start": "22:00",
                    "quiet_hours_end": "07:00",
                    "max_par_heure": 5,
                    "mode_digest": False,
                    "mode_vacances": False,
                    "checklist_voyage_auto": True,
                }

            return _notif_to_dict(prefs, user["id"])

    return await executer_async(_query)


@router.put("/notifications", responses=REPONSES_CRUD_ECRITURE)
@gerer_exception_api
async def modifier_preferences_notifications(
    donnees: PreferencesNotificationsUpdate,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Crée ou met à jour les préférences de canaux de notification (upsert)."""
    from src.core.models.notifications import PreferenceNotification

    def _upsert():
        try:
            user_uuid = UUID(str(user["id"]))
        except (ValueError, AttributeError):
            raise HTTPException(status_code=400, detail="Identifiant utilisateur invalide (UUID requis)")
        with executer_avec_session() as session:
            prefs = (
                session.query(PreferenceNotification)
                .filter(PreferenceNotification.user_id == user_uuid)
                .first()
            )

            if not prefs:
                prefs = PreferenceNotification(user_id=user_uuid)
                session.add(prefs)

            updates = donnees.model_dump(exclude_unset=True)
            modules_actifs: dict[str, Any] = cast(dict[str, Any], prefs.modules_actifs or {})
            for key, value in updates.items():
                if key == "canaux_par_categorie" and value is not None:
                    # Convertir Pydantic model → dict
                    setattr(prefs, key, value if isinstance(value, dict) else value.model_dump())
                elif key in ("quiet_hours_start", "quiet_hours_end") and value is not None:
                    # Stocker comme string "HH:MM", conversion en Time si possible
                    try:
                        from datetime import time as _time

                        h, m = str(value).split(":")
                        setattr(prefs, key, _time(int(h), int(m)))
                    except Exception as e:
                        logger.warning("Format invalide pour %s='%s': %s", key, value, e)
                elif key in (
                    "max_par_heure",
                    "mode_digest",
                    "mode_vacances",
                    "checklist_voyage_auto",
                ):
                    modules_actifs[key] = value
                elif key == "notifications_par_module" and value is not None:
                    modules_actifs["notifications_par_module"] = {
                        k: bool(v) for k, v in dict(value).items()
                    }
                else:
                    setattr(prefs, key, value)

            prefs.modules_actifs = modules_actifs

            session.commit()
            session.refresh(prefs)
            return _notif_to_dict(prefs, user["id"])

    return await executer_async(_upsert)


# ═══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
# MODE VACANCES (INNO-12)
# ═══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════


@router.post("/mode-vacances/activer", responses=REPONSES_CRUD_ECRITURE)
@gerer_exception_api
async def activer_mode_vacances(
    date_depart: str | None = None,  # Format: YYYY-MM-DD
    date_retour: str | None = None,  # Format: YYYY-MM-DD
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """
    INNO-12: Active le mode vacances — pause notifs, generate checklist départ.

    Lors de l'activation:
    1. Les rappels Telegram sont pausés (sauf urgences)
    2. Une checklist de départ est générée
    3. Le frigo sera marqué pour destockage progressif
    4. Les plannings restent visibles mais non rappelés

    Args:
        date_depart: Date de départ (optionnel)
        date_retour: Date de retour (optionnel)

    Returns:
        Statut du mode vacances + checklist générée
    """

    def _activer():
        from datetime import datetime

        from src.core.models.notifications import PreferenceNotification

        with executer_avec_session() as session:
            prefs = (
                session.query(PreferenceNotification)
                .filter(PreferenceNotification.user_id == user["id"])
                .first()
            )

            if not prefs:
                prefs = PreferenceNotification(user_id=user["id"])
                session.add(prefs)

            modules_actifs = prefs.modules_actifs or {}
            modules_actifs["mode_vacances"] = True
            if date_depart:
                try:
                    modules_actifs["vacances_depart"] = datetime.strptime(
                        date_depart, "%Y-%m-%d"
                    ).isoformat()
                except (ValueError, TypeError):
                    logger.warning(
                        "Format date_depart invalide: %s (attendu YYYY-MM-DD)", date_depart
                    )
            if date_retour:
                try:
                    modules_actifs["vacances_retour"] = datetime.strptime(
                        date_retour, "%Y-%m-%d"
                    ).isoformat()
                except (ValueError, TypeError):
                    logger.warning(
                        "Format date_retour invalide: %s (attendu YYYY-MM-DD)", date_retour
                    )

            prefs.modules_actifs = modules_actifs
            session.commit()

            # Générer checklist
            checklist = [
                {
                    "tache": "Fermer tous les robinets intérieurs",
                    "categorie": "eau",
                    "priorite": "haute",
                },
                {
                    "tache": "Vérifier la porte d'entrée",
                    "categorie": "securite",
                    "priorite": "haute",
                },
                {
                    "tache": "Éteindre appareils électriques",
                    "categorie": "electricite",
                    "priorite": "moyenne",
                },
                {
                    "tache": "Vider le frigo (destockage)",
                    "categorie": "cuisine",
                    "priorite": "moyenne",
                },
                {"tache": "Arroser les plantes", "categorie": "jardin", "priorite": "moyenne"},
                {
                    "tache": "Fermer les volets (optionnel)",
                    "categorie": "securite",
                    "priorite": "basse",
                },
            ]

            return {
                "statut": "Mode vacances activé",
                "mode_vacances": True,
                "date_depart": date_depart,
                "date_retour": date_retour,
                "notifications_pausees": True,
                "checklist": checklist,
            }

    return await executer_async(_activer)


@router.post("/mode-vacances/desactiver", responses=REPONSES_CRUD_ECRITURE)
@gerer_exception_api
async def desactiver_mode_vacances(
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """
    Désactive le mode vacances — reprend les notifications.

    Args:
        user: Utilisateur authentifié

    Returns:
        Statut updated
    """

    def _desactiver():
        from src.core.models.notifications import PreferenceNotification

        with executer_avec_session() as session:
            prefs = (
                session.query(PreferenceNotification)
                .filter(PreferenceNotification.user_id == user["id"])
                .first()
            )

            if prefs:
                modules_actifs = prefs.modules_actifs or {}
                modules_actifs["mode_vacances"] = False
                for key in list(modules_actifs.keys()):
                    if key.startswith("vacances_"):
                        del modules_actifs[key]
                prefs.modules_actifs = modules_actifs
                session.commit()

            return {
                "statut": "Mode vacances désactivé",
                "mode_vacances": False,
                "notifications_actives": True,
            }

    return await executer_async(_desactiver)
