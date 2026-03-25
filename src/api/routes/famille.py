"""
Routes API pour la famille.

Endpoints pour la gestion familiale:
- Profils enfants
- Activités familiales
- Jalons de développement
- Budget familial
- Shopping familial
"""

from datetime import date
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile
from pydantic import BaseModel, Field

from src.api.dependencies import require_auth
from src.api.pagination import appliquer_cursor_filter, construire_reponse_cursor, decoder_cursor
from src.api.schemas.common import MessageResponse, ReponsePaginee
from src.api.schemas.errors import (
    REPONSES_CRUD_CREATION,
    REPONSES_CRUD_ECRITURE,
    REPONSES_CRUD_LECTURE,
    REPONSES_CRUD_SUPPRESSION,
    REPONSES_LISTE,
)
from src.api.schemas.famille import (
    AnniversaireCreate,
    AnniversairePatch,
    EvenementFamilialCreate,
    EvenementFamilialPatch,
)
from src.api.utils import executer_async, executer_avec_session, gerer_exception_api

router = APIRouter(prefix="/api/v1/famille", tags=["Famille"])


# ═══════════════════════════════════════════════════════════
# SCHEMAS PYDANTIC LOCAUX
# ═══════════════════════════════════════════════════════════


class ParamsSuggestionsActivites(BaseModel):
    """Paramètres pour suggestions d'activités IA"""

    age_mois: int = Field(..., ge=0, le=72, description="Âge de l'enfant en mois (0-72 mois)")
    meteo: str = Field(
        default="mixte",
        description="Type de météo: pluie, soleil, nuageux, mixte, interieur, exterieur",
    )
    budget_max: float = Field(default=50.0, ge=0, le=500, description="Budget maximum par activité")
    duree_min: int = Field(default=30, ge=5, le=300, description="Durée minimum en minutes")
    duree_max: int = Field(default=120, ge=10, le=360, description="Durée maximum en minutes")
    preferences: list[str] | None = Field(
        default=None, description="Tags de préférences (creatif, sportif, educatif, sensoriel, etc.)"
    )
    nb_suggestions: int = Field(
        default=5, ge=1, le=10, description="Nombre de suggestions souhaitées"
    )


# ═══════════════════════════════════════════════════════════
# PROFILS ENFANTS
# ═══════════════════════════════════════════════════════════


@router.get("/enfants", responses=REPONSES_LISTE)
@gerer_exception_api
async def lister_enfants(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    actif: bool = Query(True, description="Filtrer par statut actif"),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """
    Liste les profils enfants.

    Returns:
        Réponse paginée avec les profils enfants
    """
    from src.core.models import ProfilEnfant

    def _query():
        with executer_avec_session() as session:
            query = session.query(ProfilEnfant)

            if actif is not None:
                query = query.filter(ProfilEnfant.actif == actif)

            total = query.count()
            items = (
                query.order_by(ProfilEnfant.name)
                .offset((page - 1) * page_size)
                .limit(page_size)
                .all()
            )

            return {
                "items": [
                    {
                        "id": e.id,
                        "name": e.name,
                        "date_of_birth": e.date_of_birth.isoformat() if e.date_of_birth else None,
                        "gender": e.gender,
                        "notes": e.notes,
                        "actif": e.actif,
                        "taille_vetements": e.taille_vetements or {},
                        "pointure": e.pointure,
                    }
                    for e in items
                ],
                "total": total,
                "page": page,
                "page_size": page_size,
                "pages": (total + page_size - 1) // page_size if total > 0 else 0,
            }

    return await executer_async(_query)


@router.get("/enfants/{enfant_id}", responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def obtenir_enfant(enfant_id: int, user: dict[str, Any] = Depends(require_auth)):
    """Récupère un profil enfant par son ID."""
    from src.core.models import ProfilEnfant

    def _query():
        with executer_avec_session() as session:
            enfant = session.query(ProfilEnfant).filter(ProfilEnfant.id == enfant_id).first()
            if not enfant:
                raise HTTPException(status_code=404, detail="Enfant non trouvé")

            return {
                "id": enfant.id,
                "name": enfant.name,
                "date_of_birth": enfant.date_of_birth.isoformat() if enfant.date_of_birth else None,
                "gender": enfant.gender,
                "notes": enfant.notes,
                "actif": enfant.actif,
                "cree_le": enfant.cree_le.isoformat() if enfant.cree_le else None,
                "taille_vetements": enfant.taille_vetements or {},
                "pointure": enfant.pointure,
            }

    return await executer_async(_query)


@router.get("/enfants/{enfant_id}/jalons", responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def lister_jalons_enfant(
    enfant_id: int,
    categorie: str | None = Query(None, description="Filtrer par catégorie"),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Liste les jalons de développement d'un enfant."""
    from src.core.models import Jalon

    def _query():
        with executer_avec_session() as session:
            query = session.query(Jalon).filter(Jalon.child_id == enfant_id)

            if categorie:
                query = query.filter(Jalon.categorie == categorie)

            jalons = query.order_by(Jalon.date_atteint.desc()).all()

            return {
                "items": [
                    {
                        "id": j.id,
                        "titre": j.titre,
                        "description": j.description,
                        "categorie": j.categorie,
                        "date_atteint": j.date_atteint.isoformat(),
                        "photo_url": j.photo_url,
                    }
                    for j in jalons
                ],
                "enfant_id": enfant_id,
            }

    return await executer_async(_query)


@router.post("/enfants/{enfant_id}/jalons", status_code=201, responses=REPONSES_CRUD_CREATION)
@gerer_exception_api
async def creer_jalon(
    enfant_id: int,
    payload: dict[str, Any],
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Ajoute un jalon de développement pour un enfant."""
    from src.core.models import Jalon, ProfilEnfant

    def _query():
        with executer_avec_session() as session:
            enfant = session.query(ProfilEnfant).filter(ProfilEnfant.id == enfant_id).first()
            if not enfant:
                raise HTTPException(status_code=404, detail="Enfant non trouvé")

            jalon = Jalon(
                child_id=enfant_id,
                titre=payload["titre"],
                description=payload.get("description"),
                categorie=payload.get("categorie", "autre"),
                date_atteint=payload.get("date_atteint", date.today().isoformat()),
                photo_url=payload.get("photo_url"),
                notes=payload.get("notes"),
                lieu=payload.get("lieu"),
                emotion_parents=payload.get("emotion_parents"),
            )
            session.add(jalon)
            session.commit()
            session.refresh(jalon)
            return {
                "id": jalon.id,
                "titre": jalon.titre,
                "categorie": jalon.categorie,
                "date_atteint": jalon.date_atteint.isoformat(),
                "enfant_id": enfant_id,
            }

    return await executer_async(_query)


@router.delete("/enfants/{enfant_id}/jalons/{jalon_id}", responses=REPONSES_CRUD_SUPPRESSION)
@gerer_exception_api
async def supprimer_jalon(
    enfant_id: int,
    jalon_id: int,
    user: dict[str, Any] = Depends(require_auth),
) -> MessageResponse:
    """Supprime un jalon de développement."""
    from src.core.models import Jalon

    def _query():
        with executer_avec_session() as session:
            jalon = (
                session.query(Jalon)
                .filter(Jalon.id == jalon_id, Jalon.child_id == enfant_id)
                .first()
            )
            if not jalon:
                raise HTTPException(status_code=404, detail="Jalon non trouvé")
            session.delete(jalon)
            session.commit()
            return MessageResponse(message=f"Jalon '{jalon.titre}' supprimé")

    return await executer_async(_query)


# ═══════════════════════════════════════════════════════════
# ACTIVITÉS FAMILIALES
# ═══════════════════════════════════════════════════════════


@router.get("/activites", responses=REPONSES_LISTE)
@gerer_exception_api
async def lister_activites(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    type_activite: str | None = Query(None, description="Filtrer par type"),
    statut: str | None = Query(None, description="Filtrer par statut"),
    date_debut: date | None = Query(None, description="Date minimum"),
    date_fin: date | None = Query(None, description="Date maximum"),
    cursor: str | None = Query(None, description="Curseur pour pagination cursor-based"),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """
    Liste les activités familiales avec pagination offset ou cursor.

    Supporte deux modes de pagination:
    - Offset: Utiliser page/page_size (défaut)
    - Cursor: Utiliser cursor pour grandes collections
    """
    from src.core.models import ActiviteFamille

    def _query():
        with executer_avec_session() as session:
            query = session.query(ActiviteFamille)

            if type_activite:
                query = query.filter(ActiviteFamille.type_activite == type_activite)
            if statut:
                query = query.filter(ActiviteFamille.statut == statut)
            if date_debut:
                query = query.filter(ActiviteFamille.date_prevue >= date_debut)
            if date_fin:
                query = query.filter(ActiviteFamille.date_prevue <= date_fin)

            query = query.order_by(ActiviteFamille.date_prevue.desc())

            # Pagination cursor-based si cursor fourni
            if cursor:
                cursor_params = decoder_cursor(cursor)
                query = appliquer_cursor_filter(query, cursor_params, ActiviteFamille)
                items = query.limit(page_size + 1).all()
                return construire_reponse_cursor(
                    items,
                    page_size,
                    cursor_field="id",
                    serializer=None,
                )

            # Pagination offset standard
            total = query.count()
            items = query.offset((page - 1) * page_size).limit(page_size).all()

            return {
                "items": [
                    {
                        "id": a.id,
                        "titre": a.titre,
                        "description": a.description,
                        "type_activite": a.type_activite,
                        "date_prevue": a.date_prevue.isoformat(),
                        "duree_heures": a.duree_heures,
                        "lieu": a.lieu,
                        "statut": a.statut,
                        "cout_estime": a.cout_estime,
                        "cout_reel": a.cout_reel,
                    }
                    for a in items
                ],
                "total": total,
                "page": page,
                "page_size": page_size,
                "pages": (total + page_size - 1) // page_size if total > 0 else 0,
            }

    return await executer_async(_query)


@router.get("/activites/{activite_id}", responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def obtenir_activite(activite_id: int, user: dict[str, Any] = Depends(require_auth)):
    """Récupère une activité par son ID."""
    from src.core.models import ActiviteFamille

    def _query():
        with executer_avec_session() as session:
            activite = (
                session.query(ActiviteFamille).filter(ActiviteFamille.id == activite_id).first()
            )
            if not activite:
                raise HTTPException(status_code=404, detail="Activité non trouvée")

            return {
                "id": activite.id,
                "titre": activite.titre,
                "description": activite.description,
                "type_activite": activite.type_activite,
                "date_prevue": activite.date_prevue.isoformat(),
                "duree_heures": activite.duree_heures,
                "lieu": activite.lieu,
                "qui_participe": activite.qui_participe,
                "age_minimal_recommande": activite.age_minimal_recommande,
                "cout_estime": activite.cout_estime,
                "cout_reel": activite.cout_reel,
                "statut": activite.statut,
                "notes": activite.notes,
            }

    return await executer_async(_query)


@router.post("/activites/suggestions-ia", responses=REPONSES_LISTE)
@gerer_exception_api
async def suggerer_activites_ia(
    params: ParamsSuggestionsActivites,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """
    Génère des suggestions d'activités personnalisées via IA.
    
    Utilise JulesAIService avec parsing structuré pour retourner des activités
    adaptées à l'âge de l'enfant, la météo, le budget et les préférences.
    
    **Paramètres**:
    - age_mois: Âge de l'enfant en mois (utilisé pour adapter les suggestions)
    - meteo: Type de météo ou lieu (pluie/soleil/mixte/interieur/exterieur)
    - budget_max: Budget maximum par activité en euros
    - duree_min/duree_max: Fourchette de durée souhaitée
    - preferences: Tags optionnels (creatif, sportif, educatif, sensoriel, etc.)
    - nb_suggestions: Nombre de suggestions (1-10)
    
    **Retour**: Liste structurée d'activités avec nom, description, durée, budget, 
    lieu, compétences, matériel nécessaire, niveau d'effort.
    """
    from src.services.famille.jules_ai import get_jules_ai_service

    def _query():
        service = get_jules_ai_service()
        suggestions = service.suggerer_activites_enrichies(
            age_mois=params.age_mois,
            meteo=params.meteo,
            budget_max=params.budget_max,
            duree_min=params.duree_min,
            duree_max=params.duree_max,
            preferences=params.preferences,
            nb_suggestions=params.nb_suggestions,
        )
        
        # Convertir Pydantic models en dicts pour JSON response
        return {
            "total": len(suggestions),
            "suggestions": [s.model_dump() for s in suggestions],
            "params": params.model_dump(),
        }

    return await executer_async(_query)


@router.post("/activites", status_code=201, responses=REPONSES_CRUD_CREATION)
@gerer_exception_api
async def creer_activite(
    payload: dict[str, Any],
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Crée une nouvelle activité familiale."""
    from src.core.models import ActiviteFamille

    def _query():
        with executer_avec_session() as session:
            activite = ActiviteFamille(
                titre=payload["titre"],
                description=payload.get("description"),
                type_activite=payload.get("type_activite", "sortie"),
                date_prevue=payload["date_prevue"],
                duree_heures=payload.get("duree_heures"),
                lieu=payload.get("lieu"),
                qui_participe=payload.get("qui_participe"),
                cout_estime=payload.get("cout_estime"),
                statut=payload.get("statut", "planifié"),
                notes=payload.get("notes"),
            )
            session.add(activite)
            session.commit()
            session.refresh(activite)
            return {
                "id": activite.id,
                "titre": activite.titre,
                "type_activite": activite.type_activite,
                "date_prevue": activite.date_prevue.isoformat(),
                "statut": activite.statut,
            }

    return await executer_async(_query)


@router.patch("/activites/{activite_id}", responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def modifier_activite(
    activite_id: int,
    payload: dict[str, Any],
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Met à jour une activité familiale."""
    from src.core.models import ActiviteFamille

    def _query():
        with executer_avec_session() as session:
            activite = (
                session.query(ActiviteFamille).filter(ActiviteFamille.id == activite_id).first()
            )
            if not activite:
                raise HTTPException(status_code=404, detail="Activité non trouvée")

            for champ in ("titre", "description", "type_activite", "date_prevue",
                          "duree_heures", "lieu", "qui_participe", "cout_estime",
                          "cout_reel", "statut", "notes"):
                if champ in payload:
                    setattr(activite, champ, payload[champ])

            session.commit()
            session.refresh(activite)
            return {
                "id": activite.id,
                "titre": activite.titre,
                "statut": activite.statut,
                "date_prevue": activite.date_prevue.isoformat(),
            }

    return await executer_async(_query)


@router.delete("/activites/{activite_id}", responses=REPONSES_CRUD_SUPPRESSION)
@gerer_exception_api
async def supprimer_activite(
    activite_id: int,
    user: dict[str, Any] = Depends(require_auth),
) -> MessageResponse:
    """Supprime une activité familiale."""
    from src.core.models import ActiviteFamille

    def _query():
        with executer_avec_session() as session:
            activite = (
                session.query(ActiviteFamille).filter(ActiviteFamille.id == activite_id).first()
            )
            if not activite:
                raise HTTPException(status_code=404, detail="Activité non trouvée")
            session.delete(activite)
            session.commit()
            return MessageResponse(message=f"Activité '{activite.titre}' supprimée")

    return await executer_async(_query)


# ═══════════════════════════════════════════════════════════
# BUDGET FAMILIAL
# ═══════════════════════════════════════════════════════════


@router.get("/budget", responses=REPONSES_LISTE)
@gerer_exception_api
async def lister_depenses(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    categorie: str | None = Query(None, description="Filtrer par catégorie"),
    date_debut: date | None = Query(None),
    date_fin: date | None = Query(None),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Liste les dépenses familiales."""
    from src.core.models import BudgetFamille

    def _query():
        with executer_avec_session() as session:
            query = session.query(BudgetFamille)

            if categorie:
                query = query.filter(BudgetFamille.categorie == categorie)
            if date_debut:
                query = query.filter(BudgetFamille.date >= date_debut)
            if date_fin:
                query = query.filter(BudgetFamille.date <= date_fin)

            total = query.count()
            items = (
                query.order_by(BudgetFamille.date.desc())
                .offset((page - 1) * page_size)
                .limit(page_size)
                .all()
            )

            return {
                "items": [
                    {
                        "id": d.id,
                        "date": d.date.isoformat(),
                        "categorie": d.categorie,
                        "description": d.description,
                        "montant": d.montant,
                        "magasin": d.magasin,
                        "est_recurrent": d.est_recurrent,
                    }
                    for d in items
                ],
                "total": total,
                "page": page,
                "page_size": page_size,
                "pages": (total + page_size - 1) // page_size if total > 0 else 0,
            }

    return await executer_async(_query)


@router.get("/budget/stats", responses=REPONSES_LISTE)
@gerer_exception_api
async def statistiques_budget(
    mois: int | None = Query(None, ge=1, le=12, description="Mois (1-12)"),
    annee: int | None = Query(None, ge=2020, le=2030, description="Année"),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Retourne les statistiques du budget familial."""
    from datetime import datetime

    from sqlalchemy import func

    from src.core.models import BudgetFamille

    def _query():
        with executer_avec_session() as session:
            query = session.query(BudgetFamille)

            # Filtrer par période si spécifié
            if mois and annee:
                query = query.filter(
                    func.extract("month", BudgetFamille.date) == mois,
                    func.extract("year", BudgetFamille.date) == annee,
                )
            elif annee:
                query = query.filter(func.extract("year", BudgetFamille.date) == annee)

            # Total
            total = query.with_entities(func.sum(BudgetFamille.montant)).scalar() or 0

            # Par catégorie
            par_categorie = (
                query.with_entities(
                    BudgetFamille.categorie, func.sum(BudgetFamille.montant).label("total")
                )
                .group_by(BudgetFamille.categorie)
                .all()
            )

            return {
                "total": float(total),
                "par_categorie": {cat: float(montant) for cat, montant in par_categorie},
                "periode": {"mois": mois, "annee": annee},
            }

    return await executer_async(_query)


@router.post("/budget", status_code=201, responses=REPONSES_CRUD_CREATION)
@gerer_exception_api
async def creer_depense(
    payload: dict[str, Any],
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Ajoute une dépense au budget familial."""
    from src.core.models import BudgetFamille

    def _query():
        with executer_avec_session() as session:
            depense = BudgetFamille(
                date=payload.get("date", date.today().isoformat()),
                categorie=payload["categorie"],
                description=payload.get("description"),
                montant=payload["montant"],
                magasin=payload.get("magasin"),
                est_recurrent=payload.get("est_recurrent", False),
                frequence_recurrence=payload.get("frequence_recurrence"),
                notes=payload.get("notes"),
            )
            session.add(depense)
            session.commit()
            session.refresh(depense)
            return {
                "id": depense.id,
                "date": depense.date.isoformat(),
                "categorie": depense.categorie,
                "montant": depense.montant,
            }

    return await executer_async(_query)


@router.delete("/budget/{depense_id}", responses=REPONSES_CRUD_SUPPRESSION)
@gerer_exception_api
async def supprimer_depense(
    depense_id: int,
    user: dict[str, Any] = Depends(require_auth),
) -> MessageResponse:
    """Supprime une dépense du budget."""
    from src.core.models import BudgetFamille

    def _query():
        with executer_avec_session() as session:
            depense = (
                session.query(BudgetFamille).filter(BudgetFamille.id == depense_id).first()
            )
            if not depense:
                raise HTTPException(status_code=404, detail="Dépense non trouvée")
            session.delete(depense)
            session.commit()
            return MessageResponse(message="Dépense supprimée")

    return await executer_async(_query)


# ═══════════════════════════════════════════════════════════
# BUDGET IA — Prédictions, Anomalies, Économies
# ═══════════════════════════════════════════════════════════


@router.get("/budget/analyse-ia", responses=REPONSES_LISTE)
@gerer_exception_api
async def analyse_budget_ia(
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Analyse complète du budget avec prédictions, anomalies et suggestions."""
    from datetime import datetime

    from sqlalchemy import func

    from src.core.models import BudgetFamille
    from src.services.famille.budget_ai import get_budget_ai_service

    def _query():
        with executer_avec_session() as session:
            aujourd_hui = datetime.now()
            mois_courant = aujourd_hui.month
            annee_courante = aujourd_hui.year

            # Historique 6 derniers mois
            historique = []
            for i in range(6):
                m = mois_courant - i
                a = annee_courante
                if m <= 0:
                    m += 12
                    a -= 1

                depenses_mois = (
                    session.query(
                        BudgetFamille.categorie,
                        func.sum(BudgetFamille.montant).label("total"),
                    )
                    .filter(
                        func.extract("month", BudgetFamille.date) == m,
                        func.extract("year", BudgetFamille.date) == a,
                    )
                    .group_by(BudgetFamille.categorie)
                    .all()
                )

                par_cat = {cat: float(total) for cat, total in depenses_mois}
                total = sum(par_cat.values())

                historique.append({
                    "mois": m,
                    "annee": a,
                    "total": total,
                    "par_categorie": par_cat,
                })

            # Inverser (du plus ancien au plus récent)
            historique.reverse()

            # Dépenses mois courant et moyennes
            depenses_courant = historique[-1]["par_categorie"] if historique else {}
            if len(historique) > 1:
                moyennes = {}
                for h in historique[:-1]:
                    for cat, m in h.get("par_categorie", {}).items():
                        moyennes[cat] = moyennes.get(cat, 0) + m
                nb_mois_prec = len(historique) - 1
                moyennes = {cat: v / nb_mois_prec for cat, v in moyennes.items()}
            else:
                moyennes = {}

            total_moyen = sum(moyennes.values()) if moyennes else 0

            return {
                "historique": historique,
                "depenses_courant": depenses_courant,
                "moyennes": moyennes,
                "total_moyen": total_moyen,
            }

    donnees = await executer_async(_query)

    service = get_budget_ai_service()
    predictions = service.predire_budget_mensuel(donnees["historique"])
    anomalies = service.detecter_anomalies(
        donnees["depenses_courant"], donnees["moyennes"]
    )
    suggestions = service.suggerer_economies(
        donnees["moyennes"], donnees["total_moyen"]
    )

    return {
        "predictions": predictions.model_dump() if predictions else None,
        "anomalies": [a.model_dump() for a in anomalies],
        "suggestions": [s.model_dump() for s in suggestions],
        "historique": donnees["historique"],
    }


@router.get("/budget/predictions", responses=REPONSES_LISTE)
@gerer_exception_api
async def predictions_budget(
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Prédictions du budget pour le mois prochain."""
    from datetime import datetime

    from sqlalchemy import func

    from src.core.models import BudgetFamille
    from src.services.famille.budget_ai import get_budget_ai_service

    def _query():
        with executer_avec_session() as session:
            aujourd_hui = datetime.now()
            mois_courant = aujourd_hui.month
            annee_courante = aujourd_hui.year

            historique = []
            for i in range(6):
                m = mois_courant - i
                a = annee_courante
                if m <= 0:
                    m += 12
                    a -= 1

                depenses_mois = (
                    session.query(
                        BudgetFamille.categorie,
                        func.sum(BudgetFamille.montant).label("total"),
                    )
                    .filter(
                        func.extract("month", BudgetFamille.date) == m,
                        func.extract("year", BudgetFamille.date) == a,
                    )
                    .group_by(BudgetFamille.categorie)
                    .all()
                )

                par_cat = {cat: float(total) for cat, total in depenses_mois}
                total = sum(par_cat.values())
                historique.append({"mois": m, "annee": a, "total": total, "par_categorie": par_cat})

            historique.reverse()
            return historique

    historique = await executer_async(_query)
    service = get_budget_ai_service()
    predictions = service.predire_budget_mensuel(historique)

    return {
        "predictions": predictions.model_dump() if predictions else None,
        "historique": historique,
    }


@router.get("/budget/anomalies", responses=REPONSES_LISTE)
@gerer_exception_api
async def anomalies_budget(
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Détecte les anomalies dans les dépenses du mois courant."""
    from datetime import datetime

    from sqlalchemy import func

    from src.core.models import BudgetFamille
    from src.services.famille.budget_ai import get_budget_ai_service

    def _query():
        with executer_avec_session() as session:
            aujourd_hui = datetime.now()
            mois_courant = aujourd_hui.month
            annee_courante = aujourd_hui.year

            # Mois courant
            courant = (
                session.query(
                    BudgetFamille.categorie,
                    func.sum(BudgetFamille.montant).label("total"),
                )
                .filter(
                    func.extract("month", BudgetFamille.date) == mois_courant,
                    func.extract("year", BudgetFamille.date) == annee_courante,
                )
                .group_by(BudgetFamille.categorie)
                .all()
            )
            depenses_courant = {cat: float(total) for cat, total in courant}

            # Moyennes 5 mois précédents
            moyennes = {}
            for i in range(1, 6):
                m = mois_courant - i
                a = annee_courante
                if m <= 0:
                    m += 12
                    a -= 1
                deps = (
                    session.query(
                        BudgetFamille.categorie,
                        func.sum(BudgetFamille.montant).label("total"),
                    )
                    .filter(
                        func.extract("month", BudgetFamille.date) == m,
                        func.extract("year", BudgetFamille.date) == a,
                    )
                    .group_by(BudgetFamille.categorie)
                    .all()
                )
                for cat, total in deps:
                    moyennes[cat] = moyennes.get(cat, 0) + float(total)

            moyennes = {cat: v / 5 for cat, v in moyennes.items()}

            return {"depenses_courant": depenses_courant, "moyennes": moyennes}

    donnees = await executer_async(_query)
    service = get_budget_ai_service()
    anomalies = service.detecter_anomalies(
        donnees["depenses_courant"], donnees["moyennes"]
    )

    return {"anomalies": [a.model_dump() for a in anomalies]}


@router.post("/budget/ocr-ticket", responses=REPONSES_CRUD_CREATION)
@gerer_exception_api
async def analyser_ticket_ocr(
    file: UploadFile,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Analyse un ticket/facture par OCR IA et extrait les données."""
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Le fichier doit être une image (JPEG, PNG)")

    contenu = await file.read()
    if len(contenu) > 10 * 1024 * 1024:  # 10 MB
        raise HTTPException(status_code=400, detail="Fichier trop volumineux (max 10 Mo)")

    from src.services.integrations.multimodal import get_multimodal_service

    service = get_multimodal_service()
    resultat = service.extraire_facture_sync(contenu)

    if not resultat:
        return {
            "success": False,
            "message": "Impossible d'extraire les données du ticket. Essayez avec une image plus nette.",
            "donnees": None,
        }

    return {
        "success": True,
        "message": "Ticket analysé avec succès",
        "donnees": {
            "magasin": resultat.magasin,
            "date": resultat.date,
            "articles": [
                {
                    "description": ligne.description,
                    "quantite": ligne.quantite,
                    "prix_unitaire": ligne.prix_unitaire,
                    "prix_total": ligne.prix_total,
                }
                for ligne in resultat.lignes
            ],
            "sous_total": resultat.sous_total,
            "tva": resultat.tva,
            "total": resultat.total,
            "mode_paiement": resultat.mode_paiement,
            "categorie_suggeree": "alimentation",
        },
    }


# ═══════════════════════════════════════════════════════════
# SHOPPING FAMILIAL
# ═══════════════════════════════════════════════════════════


@router.get("/shopping", responses=REPONSES_LISTE)
@gerer_exception_api
async def lister_shopping(
    liste: str | None = Query(None, description="Filtrer par liste (Jules, Nous, etc.)"),
    categorie: str | None = Query(None, description="Filtrer par catégorie"),
    actif: bool = Query(True, description="Articles non achetés seulement"),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Liste les articles de shopping familial."""
    from src.core.models import ArticleAchat

    def _query():
        with executer_avec_session() as session:
            query = session.query(ArticleAchat)

            if liste:
                query = query.filter(ArticleAchat.liste == liste)
            if categorie:
                query = query.filter(ArticleAchat.categorie == categorie)
            if actif is not None:
                query = query.filter(ArticleAchat.actif == actif)

            items = query.order_by(ArticleAchat.date_ajout.desc()).all()

            return {
                "items": [
                    {
                        "id": a.id,
                        "titre": a.titre,
                        "categorie": a.categorie,
                        "quantite": a.quantite,
                        "prix_estime": a.prix_estime,
                        "liste": a.liste,
                        "actif": a.actif,
                        "date_ajout": a.date_ajout.isoformat() if a.date_ajout else None,
                    }
                    for a in items
                ],
            }

    return await executer_async(_query)


# ═══════════════════════════════════════════════════════════
# ROUTINES FAMILIALES
# ═══════════════════════════════════════════════════════════


def _serialiser_routine(routine) -> dict[str, Any]:
    """Sérialise une routine avec ses tâches."""
    return {
        "id": routine.id,
        "nom": routine.nom,
        "type": routine.categorie or "journee",
        "est_active": routine.actif,
        "etapes": [
            {
                "id": t.id,
                "titre": t.nom,
                "duree_minutes": None,
                "ordre": t.ordre,
                "est_terminee": t.fait_le is not None,
            }
            for t in sorted(routine.tasks, key=lambda x: x.ordre)
        ],
    }


@router.get("/routines", responses=REPONSES_LISTE)
@gerer_exception_api
async def lister_routines(
    actif: bool | None = Query(None, description="Filtrer par statut actif"),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Liste les routines familiales avec leurs étapes."""
    from src.core.models import Routine

    def _query():
        with executer_avec_session() as session:
            query = session.query(Routine)

            if actif is not None:
                query = query.filter(Routine.actif == actif)

            routines = query.order_by(Routine.nom).all()

            return {
                "items": [_serialiser_routine(r) for r in routines],
            }

    return await executer_async(_query)


@router.get("/routines/{routine_id}", responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def obtenir_routine(
    routine_id: int,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Récupère une routine avec ses étapes."""
    from src.core.models import Routine

    def _query():
        with executer_avec_session() as session:
            routine = session.query(Routine).filter(Routine.id == routine_id).first()
            if not routine:
                raise HTTPException(status_code=404, detail="Routine non trouvée")
            return _serialiser_routine(routine)

    return await executer_async(_query)


@router.post("/routines", status_code=201, responses=REPONSES_LISTE)
@gerer_exception_api
async def creer_routine(
    payload: dict[str, Any],
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Crée une nouvelle routine."""
    from src.core.models import Routine, TacheRoutine

    def _query():
        with executer_avec_session() as session:
            routine = Routine(
                nom=payload["nom"],
                categorie=payload.get("type", "journee"),
                actif=payload.get("est_active", True),
            )
            session.add(routine)
            session.flush()

            for i, etape in enumerate(payload.get("etapes", []), start=1):
                tache = TacheRoutine(
                    routine_id=routine.id,
                    nom=etape["titre"],
                    ordre=etape.get("ordre", i),
                )
                session.add(tache)

            session.commit()
            session.refresh(routine)
            return _serialiser_routine(routine)

    return await executer_async(_query)


@router.patch("/routines/{routine_id}", responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def modifier_routine(
    routine_id: int,
    payload: dict[str, Any],
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Met à jour une routine existante."""
    from src.core.models import Routine

    def _query():
        with executer_avec_session() as session:
            routine = session.query(Routine).filter(Routine.id == routine_id).first()
            if not routine:
                raise HTTPException(status_code=404, detail="Routine non trouvée")

            if "nom" in payload:
                routine.nom = payload["nom"]
            if "type" in payload:
                routine.categorie = payload["type"]
            if "est_active" in payload:
                routine.actif = payload["est_active"]

            session.commit()
            session.refresh(routine)
            return _serialiser_routine(routine)

    return await executer_async(_query)


@router.delete("/routines/{routine_id}", responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def supprimer_routine(
    routine_id: int,
    user: dict[str, Any] = Depends(require_auth),
) -> MessageResponse:
    """Supprime une routine et ses tâches."""
    from src.core.models import Routine

    def _query():
        with executer_avec_session() as session:
            routine = session.query(Routine).filter(Routine.id == routine_id).first()
            if not routine:
                raise HTTPException(status_code=404, detail="Routine non trouvée")

            session.delete(routine)
            session.commit()
            return MessageResponse(message=f"Routine '{routine.nom}' supprimée")

    return await executer_async(_query)


# ═══════════════════════════════════════════════════════════
# ANNIVERSAIRES
# ═══════════════════════════════════════════════════════════


def _serialiser_anniversaire(a) -> dict:  # noqa: ANN001
    return {
        "id": a.id,
        "nom_personne": a.nom_personne,
        "date_naissance": a.date_naissance.isoformat() if a.date_naissance else None,
        "relation": a.relation,
        "rappel_jours_avant": a.rappel_jours_avant or [7, 1, 0],
        "idees_cadeaux": a.idees_cadeaux,
        "historique_cadeaux": a.historique_cadeaux,
        "notes": a.notes,
        "actif": a.actif,
        "age": a.age,
        "jours_restants": a.jours_restants,
        "cree_le": a.cree_le.isoformat() if a.cree_le else None,
    }


@router.get("/anniversaires", responses=REPONSES_LISTE)
@gerer_exception_api
async def lister_anniversaires(
    relation: str | None = Query(None),
    actif: bool = Query(True),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Liste les anniversaires familiaux, triés par jours restants."""
    from src.core.models import AnniversaireFamille

    def _query():
        with executer_avec_session() as session:
            query = session.query(AnniversaireFamille).filter(
                AnniversaireFamille.actif == actif
            )
            if relation:
                query = query.filter(AnniversaireFamille.relation == relation)

            items = query.order_by(AnniversaireFamille.date_naissance).all()
            serialized = [_serialiser_anniversaire(a) for a in items]
            serialized.sort(key=lambda x: x.get("jours_restants", 999))
            return {"items": serialized}

    return await executer_async(_query)


@router.get("/anniversaires/{anniversaire_id}", responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def obtenir_anniversaire(
    anniversaire_id: int,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Récupère un anniversaire par son ID."""
    from src.core.models import AnniversaireFamille

    def _query():
        with executer_avec_session() as session:
            a = session.query(AnniversaireFamille).filter(
                AnniversaireFamille.id == anniversaire_id
            ).first()
            if not a:
                raise HTTPException(status_code=404, detail="Anniversaire non trouvé")
            return _serialiser_anniversaire(a)

    return await executer_async(_query)


@router.post("/anniversaires", status_code=201, responses=REPONSES_CRUD_CREATION)
@gerer_exception_api
async def creer_anniversaire(
    donnees: AnniversaireCreate,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Crée un anniversaire familial."""
    from src.core.models import AnniversaireFamille

    def _query():
        with executer_avec_session() as session:
            a = AnniversaireFamille(
                nom_personne=donnees.nom_personne,
                date_naissance=date.fromisoformat(donnees.date_naissance),
                relation=donnees.relation,
                rappel_jours_avant=donnees.rappel_jours_avant,
                idees_cadeaux=donnees.idees_cadeaux,
                notes=donnees.notes,
            )
            session.add(a)
            session.commit()
            session.refresh(a)
            return _serialiser_anniversaire(a)

    return await executer_async(_query)


@router.patch("/anniversaires/{anniversaire_id}", responses=REPONSES_CRUD_ECRITURE)
@gerer_exception_api
async def modifier_anniversaire(
    anniversaire_id: int,
    donnees: AnniversairePatch,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Met à jour un anniversaire."""
    from src.core.models import AnniversaireFamille

    def _query():
        with executer_avec_session() as session:
            a = session.query(AnniversaireFamille).filter(
                AnniversaireFamille.id == anniversaire_id
            ).first()
            if not a:
                raise HTTPException(status_code=404, detail="Anniversaire non trouvé")

            for champ, valeur in donnees.model_dump(exclude_unset=True).items():
                if champ == "date_naissance" and valeur:
                    setattr(a, champ, date.fromisoformat(valeur))
                else:
                    setattr(a, champ, valeur)

            session.commit()
            session.refresh(a)
            return _serialiser_anniversaire(a)

    return await executer_async(_query)


@router.delete("/anniversaires/{anniversaire_id}", responses=REPONSES_CRUD_SUPPRESSION)
@gerer_exception_api
async def supprimer_anniversaire(
    anniversaire_id: int,
    user: dict[str, Any] = Depends(require_auth),
) -> MessageResponse:
    """Supprime un anniversaire."""
    from src.core.models import AnniversaireFamille

    def _query():
        with executer_avec_session() as session:
            a = session.query(AnniversaireFamille).filter(
                AnniversaireFamille.id == anniversaire_id
            ).first()
            if not a:
                raise HTTPException(status_code=404, detail="Anniversaire non trouvé")

            session.delete(a)
            session.commit()
            return MessageResponse(message=f"Anniversaire '{a.nom_personne}' supprimé")

    return await executer_async(_query)


# ═══════════════════════════════════════════════════════════
# ÉVÉNEMENTS FAMILIAUX
# ═══════════════════════════════════════════════════════════


def _serialiser_evenement(e) -> dict:  # noqa: ANN001
    return {
        "id": e.id,
        "titre": e.titre,
        "date_evenement": e.date_evenement.isoformat() if e.date_evenement else None,
        "type_evenement": e.type_evenement,
        "recurrence": e.recurrence,
        "rappel_jours_avant": e.rappel_jours_avant,
        "notes": e.notes,
        "participants": e.participants,
        "actif": e.actif,
        "cree_le": e.cree_le.isoformat() if e.cree_le else None,
    }


@router.get("/evenements", responses=REPONSES_LISTE)
@gerer_exception_api
async def lister_evenements_familiaux(
    type_evenement: str | None = Query(None),
    actif: bool = Query(True),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Liste les événements familiaux."""
    from src.core.models import EvenementFamilial

    def _query():
        with executer_avec_session() as session:
            query = session.query(EvenementFamilial).filter(
                EvenementFamilial.actif == actif
            )
            if type_evenement:
                query = query.filter(EvenementFamilial.type_evenement == type_evenement)

            items = query.order_by(EvenementFamilial.date_evenement.desc()).all()
            return {"items": [_serialiser_evenement(e) for e in items]}

    return await executer_async(_query)


@router.post("/evenements", status_code=201, responses=REPONSES_CRUD_CREATION)
@gerer_exception_api
async def creer_evenement_familial(
    donnees: EvenementFamilialCreate,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Crée un événement familial."""
    from src.core.models import EvenementFamilial

    def _query():
        with executer_avec_session() as session:
            e = EvenementFamilial(
                titre=donnees.titre,
                date_evenement=date.fromisoformat(donnees.date_evenement),
                type_evenement=donnees.type_evenement,
                recurrence=donnees.recurrence,
                rappel_jours_avant=donnees.rappel_jours_avant,
                notes=donnees.notes,
                participants=donnees.participants,
            )
            session.add(e)
            session.commit()
            session.refresh(e)
            return _serialiser_evenement(e)

    return await executer_async(_query)


@router.patch("/evenements/{evenement_id}", responses=REPONSES_CRUD_ECRITURE)
@gerer_exception_api
async def modifier_evenement_familial(
    evenement_id: int,
    donnees: EvenementFamilialPatch,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Met à jour un événement familial."""
    from src.core.models import EvenementFamilial

    def _query():
        with executer_avec_session() as session:
            e = session.query(EvenementFamilial).filter(
                EvenementFamilial.id == evenement_id
            ).first()
            if not e:
                raise HTTPException(status_code=404, detail="Événement non trouvé")

            for champ, valeur in donnees.model_dump(exclude_unset=True).items():
                if champ == "date_evenement" and valeur:
                    setattr(e, champ, date.fromisoformat(valeur))
                else:
                    setattr(e, champ, valeur)

            session.commit()
            session.refresh(e)
            return _serialiser_evenement(e)

    return await executer_async(_query)


@router.delete("/evenements/{evenement_id}", responses=REPONSES_CRUD_SUPPRESSION)
@gerer_exception_api
async def supprimer_evenement_familial(
    evenement_id: int,
    user: dict[str, Any] = Depends(require_auth),
) -> MessageResponse:
    """Supprime un événement familial."""
    from src.core.models import EvenementFamilial

    def _query():
        with executer_avec_session() as session:
            e = session.query(EvenementFamilial).filter(
                EvenementFamilial.id == evenement_id
            ).first()
            if not e:
                raise HTTPException(status_code=404, detail="Événement non trouvé")

            session.delete(e)
            session.commit()
            return MessageResponse(message=f"Événement '{e.titre}' supprimé")

    return await executer_async(_query)


# ═══════════════════════════════════════════════════════════
# RÉSUMÉ HEBDOMADAIRE
# ═══════════════════════════════════════════════════════════


@router.get("/resume-hebdo", responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def obtenir_resume_hebdomadaire(
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """
    Génère un résumé hebdomadaire de la famille via IA.

    Collecte les données de la semaine écoulée (repas, budget,
    activités, tâches) et génère un résumé narratif avec
    recommandations pour la semaine suivante.
    """
    from src.services.famille.resume_hebdo import obtenir_service_resume_hebdo

    def _generate():
        service = obtenir_service_resume_hebdo()
        resume = service.generer_resume_semaine_sync()
        return resume.model_dump() if hasattr(resume, "model_dump") else resume

    return await executer_async(_generate)
