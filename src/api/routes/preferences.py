"""
Routes API pour les préférences utilisateur.

CRUD pour les préférences alimentaires, robots, magasins.
"""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException

from src.api.dependencies import require_auth
from src.api.schemas.errors import REPONSES_CRUD_ECRITURE, REPONSES_CRUD_LECTURE
from src.api.schemas.preferences import PreferencesCreate, PreferencesPatch
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
