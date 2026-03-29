"""
Routes API pour les préférences utilisateur.

CRUD pour les préférences alimentaires, robots, magasins.
Sprint 13 — W4 : ajout endpoints préférences canaux de notification.
"""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException

from src.api.dependencies import require_auth
from src.api.schemas.errors import REPONSES_CRUD_ECRITURE, REPONSES_CRUD_LECTURE
from src.api.schemas.preferences import (
    PreferencesCreate,
    PreferencesPatch,
    PreferencesNotificationsUpdate,
)
from src.api.utils import executer_async, executer_avec_session, gerer_exception_api

router = APIRouter(prefix="/api/v1/preferences", tags=["Préférences"])


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
                    "poisson_par_semaine": 2,
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
                "poisson_par_semaine": prefs.poisson_par_semaine,
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
                "poisson_par_semaine": prefs.poisson_par_semaine,
                "vegetarien_par_semaine": prefs.vegetarien_par_semaine,
                "viande_rouge_max": prefs.viande_rouge_max,
                "robots": prefs.robots or [],
                "magasins_preferes": prefs.magasins_preferes or [],
            }

    return await executer_async(_upsert)


@router.patch("", responses=REPONSES_CRUD_ECRITURE)
@gerer_exception_api
async def modifier_preferences(
    patch: PreferencesPatch,
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

            updates = patch.model_dump(exclude_unset=True)
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
                "poisson_par_semaine": prefs.poisson_par_semaine,
                "vegetarien_par_semaine": prefs.vegetarien_par_semaine,
                "viande_rouge_max": prefs.viande_rouge_max,
                "robots": prefs.robots or [],
                "magasins_preferes": prefs.magasins_preferes or [],
            }

    return await executer_async(_update)


# ─────────────────────────────────────────────────────────
# Préférences canaux de notification (Sprint 13 — W4)
# ─────────────────────────────────────────────────────────

_CANAUX_DEFAULTS: dict[str, list[str]] = {
    "rappels": ["push", "ntfy"],
    "alertes": ["push", "ntfy", "email"],
    "resumes": ["email"],
}


def _notif_to_dict(prefs: Any, user_id: str) -> dict[str, Any]:
    """Sérialise une PreferenceNotification en dict API."""
    canaux_par_cat = prefs.canaux_par_categorie or _CANAUX_DEFAULTS
    modules_actifs = prefs.modules_actifs or {}
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
        "quiet_hours_start": str(prefs.quiet_hours_start or "22:00")[:5],
        "quiet_hours_end": str(prefs.quiet_hours_end or "07:00")[:5],
        "max_par_heure": int(modules_actifs.get("max_par_heure", 5)),
        "mode_digest": bool(modules_actifs.get("mode_digest", False)),
    }


@router.get("/notifications", responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def obtenir_preferences_notifications(
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Récupère les préférences de canaux de notification de l'utilisateur."""
    from src.core.models.notifications import PreferenceNotification

    def _query():
        with executer_avec_session() as session:
            prefs = (
                session.query(PreferenceNotification)
                .filter(PreferenceNotification.user_id == user["id"])
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
                    "quiet_hours_start": "22:00",
                    "quiet_hours_end": "07:00",
                    "max_par_heure": 5,
                    "mode_digest": False,
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
        with executer_avec_session() as session:
            prefs = (
                session.query(PreferenceNotification)
                .filter(PreferenceNotification.user_id == user["id"])
                .first()
            )

            if not prefs:
                prefs = PreferenceNotification(user_id=user["id"])
                session.add(prefs)

            updates = donnees.model_dump(exclude_unset=True)
            modules_actifs = dict(prefs.modules_actifs or {})
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
                    except Exception:
                        pass
                elif key in ("max_par_heure", "mode_digest"):
                    modules_actifs[key] = value
                else:
                    setattr(prefs, key, value)

            prefs.modules_actifs = modules_actifs

            session.commit()
            session.refresh(prefs)
            return _notif_to_dict(prefs, user["id"])

    return await executer_async(_upsert)
