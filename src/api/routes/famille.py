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
    AchatCreate,
    AchatPatch,
    AnnonceIBCRequest,
    AnnonceVintedRequest,
    AnniversaireCreate,
    ChecklistAnniversaireItemCreate,
    ChecklistAnniversaireItemPatch,
    ChecklistAnniversaireSyncRequest,
    AnniversairePatch,
    ConfigGardeRequest,
    ContexteFamilialResponse,
    EvenementFamilialCreate,
    EvenementFamilialPatch,
    MarquerAchetePayload,
    PreferencesFamilleRequest,
    PreferencesFamilleResponse,
    PrefillReventeResponse,
    ResumeSemaineRequest,
    RetrospectiveRequest,
    SuggestionAchatResponse,
    SuggestionsActivitesSimpleRequest,
    SuggestionsAchatsEnrichiesRequest,
    SuggestionsSoireeRequest,
    SuggestionsSejourRequest,
    SuggestionsWeekendRequest,
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


@router.get("/anniversaires/{anniversaire_id}/checklist-auto", responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def apercu_checklist_auto_anniversaire(
    anniversaire_id: int,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Retourne un aperçu dynamique de checklist (sans persistance)."""
    from src.services.famille.checklists_anniversaire import obtenir_service_checklists_anniversaire

    def _query():
        service = obtenir_service_checklists_anniversaire()
        preview = service.generer_apercu_auto(anniversaire_id=anniversaire_id, user_id=user.get("id"))
        if not preview:
            raise HTTPException(status_code=404, detail="Anniversaire non trouvé")
        return preview

    return await executer_async(_query)


@router.post(
    "/anniversaires/{anniversaire_id}/checklist-auto/synchroniser",
    responses=REPONSES_CRUD_ECRITURE,
)
@gerer_exception_api
async def synchroniser_checklist_auto_anniversaire(
    anniversaire_id: int,
    payload: ChecklistAnniversaireSyncRequest,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Synchronise les items auto de checklist sans écraser les items manuels."""
    from src.services.famille.checklists_anniversaire import obtenir_service_checklists_anniversaire

    def _query():
        service = obtenir_service_checklists_anniversaire()
        data = service.synchroniser_checklist_auto(
            anniversaire_id=anniversaire_id,
            user_id=user.get("id"),
            force_recalcul_budget=payload.force_recalcul_budget,
        )
        if not data:
            raise HTTPException(status_code=404, detail="Anniversaire non trouvé")
        return data

    return await executer_async(_query)


@router.get("/anniversaires/{anniversaire_id}/checklists", responses=REPONSES_LISTE)
@gerer_exception_api
async def lister_checklists_anniversaire(
    anniversaire_id: int,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Liste les checklists existantes d'un anniversaire."""
    from src.services.famille.checklists_anniversaire import obtenir_service_checklists_anniversaire

    def _query():
        service = obtenir_service_checklists_anniversaire()
        items = service.lister_checklists(anniversaire_id=anniversaire_id)
        return {"items": items}

    return await executer_async(_query)


@router.post(
    "/anniversaires/{anniversaire_id}/checklists/{checklist_id}/items",
    status_code=201,
    responses=REPONSES_CRUD_CREATION,
)
@gerer_exception_api
async def ajouter_item_checklist_anniversaire(
    anniversaire_id: int,
    checklist_id: int,
    payload: ChecklistAnniversaireItemCreate,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Ajoute un item manuel à une checklist anniversaire."""
    from src.services.famille.checklists_anniversaire import obtenir_service_checklists_anniversaire

    def _query():
        service = obtenir_service_checklists_anniversaire()
        data = service.ajouter_item_manuel(
            checklist_id=checklist_id,
            payload=payload.model_dump(),
        )
        if not data:
            raise HTTPException(status_code=404, detail="Checklist non trouvée")
        return data

    return await executer_async(_query)


@router.post(
    "/anniversaires/{anniversaire_id}/checklists/{checklist_id}/items/{item_id}/vers-achats",
    status_code=201,
    responses=REPONSES_CRUD_CREATION,
)
@gerer_exception_api
async def envoyer_item_checklist_vers_achats(
    anniversaire_id: int,
    checklist_id: int,
    item_id: int,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Crée un achat pré-rempli (nom/catégorie/prix/pour_qui) depuis un item de checklist."""
    from src.services.famille.achats import obtenir_service_achats_famille
    from src.services.famille.checklists_anniversaire import obtenir_service_checklists_anniversaire

    def _query():
        svc_cl = obtenir_service_checklists_anniversaire()
        prefill = svc_cl.item_vers_achat_prefill(item_id=item_id)
        if not prefill:
            raise HTTPException(status_code=404, detail="Item de checklist non trouvé")

        svc_achats = obtenir_service_achats_famille()
        achat = svc_achats.ajouter_achat(
            nom=prefill["nom"],
            categorie=prefill["categorie"],
            prix_estime=prefill.get("prix_estime"),
            pour_qui=prefill.get("pour_qui", "famille"),
            description=prefill.get("description"),
            suggere_par="checklist_anniversaire",
        )
        if not achat:
            raise HTTPException(status_code=500, detail="Erreur lors de la création de l'achat")
        return {**_serialiser_achat(achat), "source_item_id": item_id}

    return await executer_async(_query)


@router.patch(
    "/anniversaires/{anniversaire_id}/checklists/{checklist_id}/items/{item_id}",
    responses=REPONSES_CRUD_ECRITURE,
)
@gerer_exception_api
async def modifier_item_checklist_anniversaire(
    anniversaire_id: int,
    checklist_id: int,
    item_id: int,
    payload: ChecklistAnniversaireItemPatch,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Modifie un item de checklist (fait, budget réel, contenu)."""
    from src.services.famille.checklists_anniversaire import obtenir_service_checklists_anniversaire

    def _query():
        service = obtenir_service_checklists_anniversaire()
        data = service.modifier_item(item_id=item_id, patch=payload.model_dump(exclude_unset=True))
        if not data:
            raise HTTPException(status_code=404, detail="Item non trouvé")
        return data

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


# ═══════════════════════════════════════════════════════════
# CONTEXTE FAMILIAL (Phase M)
# ═══════════════════════════════════════════════════════════


@router.get("/contexte", response_model=ContexteFamilialResponse, responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def obtenir_contexte_familial(
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Retourne le contexte familial complet (météo, anniversaires, jules, etc.)."""
    from src.services.famille.contexte import obtenir_service_contexte_familial

    def _query():
        service = obtenir_service_contexte_familial()
        return service.obtenir_contexte()

    return await executer_async(_query)


# ═══════════════════════════════════════════════════════════
# SUGGESTIONS IA (Phase M3)
# ═══════════════════════════════════════════════════════════


@router.post("/weekend/suggestions-ia", responses=REPONSES_LISTE)
@gerer_exception_api
async def suggestions_weekend_ia(
    payload: SuggestionsWeekendRequest,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Suggestions d'activités weekend avec météo et âge Jules auto-injectés."""
    from src.services.famille.jules import obtenir_service_jules
    from src.services.famille.weekend_ai import obtenir_weekend_ai_service
    from src.services.integrations.weather.service import obtenir_service_meteo

    async def _query():
        # Auto-inject météo
        meteo_service = obtenir_service_meteo()
        previsions = meteo_service.get_previsions(nb_jours=3)
        meteo_desc = "variable"
        if previsions:
            conditions = [p.condition for p in previsions[:3] if p.condition]
            meteo_desc = ", ".join(conditions[:2]) if conditions else "variable"

        # Auto-inject âge Jules
        jules_service = obtenir_service_jules()
        date_naissance = jules_service.get_date_naissance_jules()
        age_mois = 19
        if date_naissance:
            age_mois = (date.today() - date_naissance).days // 30

        service = obtenir_weekend_ai_service()
        resultat = await service.suggerer_activites(
            meteo=meteo_desc,
            age_enfant_mois=age_mois,
            budget=payload.budget,
            region=payload.region,
            nb_suggestions=payload.nb_suggestions,
        )
        return {"suggestions": resultat}

    return await _query()


@router.post("/journal/resume-semaine", responses=REPONSES_CRUD_LECTURE)
@router.post("/journal/resumer-semaine", responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def resume_semaine_ia(
    payload: ResumeSemaineRequest,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Génère un résumé narratif de la semaine familiale via IA."""
    from src.services.famille.journal_ia import obtenir_service_journal_ia

    async def _query():
        service = obtenir_service_journal_ia()
        resultat = await service.generer_resume_semaine(
            evenements=payload.evenements,
            jalons=payload.jalons,
            humeur_famille=payload.humeur_famille,
        )
        return {"resume": resultat}

    return await _query()


@router.post("/journal/retrospective", responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def retrospective_mensuelle_ia(
    payload: RetrospectiveRequest,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Génère une rétrospective mensuelle via IA."""
    from src.services.famille.journal_ia import obtenir_service_journal_ia

    async def _query():
        service = obtenir_service_journal_ia()
        resultat = await service.generer_retrospective_mensuelle(
            mois=payload.mois,
            resumes_semaines=payload.resumes_semaines,
            nb_evenements=payload.nb_evenements,
            nb_jalons=payload.nb_jalons,
        )
        return {"retrospective": resultat}

    return await _query()


@router.post("/soiree/suggestions-ia", responses=REPONSES_LISTE)
@gerer_exception_api
async def suggestions_soiree_ia(
    payload: SuggestionsSoireeRequest,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Suggestions de soirées en couple via IA."""
    from src.services.famille.soiree_ai import obtenir_service_soiree_ai

    async def _query():
        service = obtenir_service_soiree_ai()
        resultat = await service.suggerer_soirees(
            budget=payload.budget,
            duree_heures=payload.duree_heures,
            type_soiree=payload.type_soiree,
            region=payload.region,
        )
        return {"suggestions": resultat}

    return await _query()


# ═══════════════════════════════════════════════════════════
# ACHATS FAMILLE CRUD (Phase M4)
# ═══════════════════════════════════════════════════════════


def _serialiser_achat(a) -> dict:  # noqa: ANN001
    return {
        "id": a.id,
        "nom": a.nom,
        "categorie": a.categorie,
        "priorite": a.priorite,
        "prix_estime": a.prix_estime,
        "prix_reel": a.prix_reel,
        "taille": a.taille,
        "magasin": a.magasin,
        "url": a.url,
        "description": a.description,
        "age_recommande_mois": a.age_recommande_mois,
        "suggere_par": a.suggere_par,
        "achete": a.achete,
        "date_achat": a.date_achat.isoformat() if a.date_achat else None,
        "pour_qui": getattr(a, "pour_qui", "famille"),
        "a_revendre": getattr(a, "a_revendre", False),
        "prix_revente_estime": getattr(a, "prix_revente_estime", None),
        "vendu_le": a.vendu_le.isoformat() if getattr(a, "vendu_le", None) else None,
    }


@router.get("/achats", responses=REPONSES_LISTE)
@gerer_exception_api
async def lister_achats_famille(
    categorie: str | None = Query(None, description="Filtrer par catégorie"),
    achete: bool | None = Query(None, description="Filtrer sur l'état acheté (true/false)"),
    pour_qui: str | None = Query(None, description="Filtrer par destinataire: famille, jules, anne, mathieu"),
    a_revendre: bool | None = Query(None, description="Filtrer sur les articles à revendre"),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Liste les achats famille (route canonique)."""
    from src.services.famille.achats import obtenir_service_achats_famille

    def _query():
        service = obtenir_service_achats_famille()
        if pour_qui is not None:
            items = service.lister_par_personne(pour_qui=pour_qui, achete=achete)
        elif a_revendre is True:
            items = service.lister_a_revendre()
        elif categorie and achete is not None:
            items = service.lister_par_categorie(categorie=categorie, achete=achete)
        elif categorie:
            items = [
                *service.lister_par_categorie(categorie=categorie, achete=False),
                *service.lister_par_categorie(categorie=categorie, achete=True),
            ]
        elif achete is not None:
            items = service.lister_achats(achete=achete)
        else:
            items = [*service.lister_achats(achete=False), *service.lister_achats(achete=True)]
        return {
            "items": [_serialiser_achat(a) for a in items],
            "total": len(items),
        }

    return await executer_async(_query)


@router.post("/achats", status_code=201, responses=REPONSES_CRUD_CREATION)
@gerer_exception_api
async def creer_achat(
    payload: AchatCreate,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Crée un nouvel achat familial."""
    from src.services.famille.achats import obtenir_service_achats_famille

    def _query():
        service = obtenir_service_achats_famille()
        achat = service.ajouter_achat(
            nom=payload.nom,
            categorie=payload.categorie,
            priorite=payload.priorite,
            prix_estime=payload.prix_estime,
            taille=payload.taille,
            magasin=payload.magasin,
            url=payload.url,
            description=payload.description,
            age_recommande_mois=payload.age_recommande_mois,
            suggere_par=payload.suggere_par,
            pour_qui=payload.pour_qui,
            a_revendre=payload.a_revendre,
            prix_revente_estime=payload.prix_revente_estime,
        )
        if not achat:
            raise HTTPException(status_code=500, detail="Erreur lors de la création de l'achat")
        return _serialiser_achat(achat)

    return await executer_async(_query)


@router.patch("/achats/{achat_id}", responses=REPONSES_CRUD_ECRITURE)
@gerer_exception_api
async def modifier_achat(
    achat_id: int,
    payload: AchatPatch,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Modifie un achat familial existant."""
    from src.core.models import AchatFamille

    def _query():
        with executer_avec_session() as session:
            achat = session.query(AchatFamille).filter(AchatFamille.id == achat_id).first()
            if not achat:
                raise HTTPException(status_code=404, detail="Achat non trouvé")

            updates = payload.model_dump(exclude_unset=True)
            for field, value in updates.items():
                setattr(achat, field, value)

            session.commit()
            session.refresh(achat)
            return _serialiser_achat(achat)

    return await executer_async(_query)


@router.post("/achats/{achat_id}/achete", responses=REPONSES_CRUD_ECRITURE)
@gerer_exception_api
async def marquer_achat_achete(
    achat_id: int,
    payload: MarquerAchetePayload,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Marque un achat comme acheté."""
    from src.services.famille.achats import obtenir_service_achats_famille

    def _query():
        service = obtenir_service_achats_famille()
        success = service.marquer_achete(achat_id, prix_reel=payload.prix_reel)
        if not success:
            raise HTTPException(status_code=404, detail="Achat non trouvé")
        return MessageResponse(message="Achat marqué comme acheté")

    return await executer_async(_query)


@router.delete("/achats/{achat_id}", responses=REPONSES_CRUD_SUPPRESSION)
@gerer_exception_api
async def supprimer_achat(
    achat_id: int,
    user: dict[str, Any] = Depends(require_auth),
) -> MessageResponse:
    """Supprime un achat familial."""
    from src.core.models import AchatFamille

    def _query():
        with executer_avec_session() as session:
            achat = session.query(AchatFamille).filter(AchatFamille.id == achat_id).first()
            if not achat:
                raise HTTPException(status_code=404, detail="Achat non trouvé")
            session.delete(achat)
            session.commit()
            return MessageResponse(message="Achat supprimé")

    return await executer_async(_query)


# ═══════════════════════════════════════════════════════════
# ACHATS — ENDPOINTS PHASE REFONTE
# ═══════════════════════════════════════════════════════════


@router.post("/achats/suggestions-ia-enrichies", responses=REPONSES_LISTE)
@gerer_exception_api
async def suggestions_achats_enrichies(
    payload: SuggestionsAchatsEnrichiesRequest,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Génère des suggestions d'achats IA selon les triggers fournis."""
    from src.services.famille.achats_ia import obtenir_service_achats_ia

    def _query():
        service = obtenir_service_achats_ia()
        resultats: list[dict] = []

        for trigger in payload.triggers:
            if trigger == "vetements_qualite" and payload.pour_qui:
                items = service.suggerer_vetements_qualite(
                    pour_qui=payload.pour_qui, saison="courante"
                )
                resultats.extend(items)
            elif trigger == "sejour" and payload.destination:
                items = service.suggerer_achats_sejour(
                    destination=payload.destination,
                    duree_jours=7,
                    age_jules_mois=payload.age_jules_mois or 0,
                )
                resultats.extend(items)
            elif trigger == "culture" and payload.ville:
                items = service.suggerer_sorties_culture(
                    ville=payload.ville,
                    age_jules_mois=payload.age_jules_mois or 0,
                    budget=payload.budget or 50,
                    interets=[],
                )
                resultats.extend(items)
            else:
                suggestions = service.suggerer_achats(payload.pour_qui or "famille")
                resultats.extend(suggestions if isinstance(suggestions, list) else [])

        return {"items": resultats, "total": len(resultats)}

    return await executer_async(_query)


@router.post("/achats/{achat_id}/annonce-lbc", responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def generer_annonce_lbc(
    achat_id: int,
    payload: AnnonceIBCRequest,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Génère une annonce LeBonCoin pour un article à revendre."""
    from src.services.famille.achats_ia import obtenir_service_achats_ia

    service = obtenir_service_achats_ia()
    texte = await service.generer_annonce_lbc(
        nom=payload.nom,
        description=payload.description,
        etat_usage=payload.etat_usage,
        prix_cible=payload.prix_cible,
    )
    return {"annonce": texte}


@router.post("/achats/{achat_id}/annonce-vinted", responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def generer_annonce_vinted(
    achat_id: int,
    payload: AnnonceVintedRequest,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Génère une annonce Vinted pour un article à revendre."""
    from src.services.famille.achats_ia import obtenir_service_achats_ia

    service = obtenir_service_achats_ia()
    texte = await service.generer_annonce_vinted(
        nom=payload.nom,
        description=payload.description,
        etat_usage=payload.etat_usage,
        prix_cible=payload.prix_cible,
        marque=payload.marque,
        taille=payload.taille,
        categorie_vinted=payload.categorie_vinted,
    )
    return {"annonce": texte}


@router.post("/achats/{achat_id}/vendu", responses=REPONSES_CRUD_ECRITURE)
@gerer_exception_api
async def marquer_achat_vendu(
    achat_id: int,
    user: dict[str, Any] = Depends(require_auth),
) -> MessageResponse:
    """Marque un achat comme vendu (met à jour vendu_le)."""
    from src.services.famille.achats import obtenir_service_achats_famille

    def _query():
        service = obtenir_service_achats_famille()
        success = service.marquer_vendu(achat_id)
        if not success:
            raise HTTPException(status_code=404, detail="Achat non trouvé")
        return MessageResponse(message="Achat marqué comme vendu")

    return await executer_async(_query)


# ─── Catégories orientées Vinted ──────────────────────────
_CATEGORIES_VINTED = frozenset({
    "jules_vetements", "nous_vetements", "vetements", "chaussures",
    "jouets", "jules_jouets", "livres", "livres_jouets",
})


@router.get("/achats/{achat_id}/prefill-revente", response_model=PrefillReventeResponse, responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def prefill_revente_achat(
    achat_id: int,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Retourne les données pré-remplies pour l'annonce de revente d'un achat.

    Déduit:
    - plateforme recommandée (Vinted pour vêtements/jouets/livres, LBC sinon)
    - marque/taille depuis les préférences famille ou l'achat lui-même
    - prix conseillé (40% du prix d'achat par défaut)
    """
    from src.core.models import AchatFamille

    def _query():
        with executer_avec_session() as session:
            achat = session.query(AchatFamille).filter(AchatFamille.id == achat_id).first()
            if not achat:
                raise HTTPException(status_code=404, detail="Achat non trouvé")

            categorie = achat.categorie or ""
            pour_qui = getattr(achat, "pour_qui", "famille") or "famille"
            plateforme = "vinted" if categorie in _CATEGORIES_VINTED else "lbc"
            plateforme_libelle = "Vinted" if plateforme == "vinted" else "LeBonCoin"

            # Prefill taille depuis les préférences famille ou l'achat
            taille = achat.taille
            raisons: list[str] = []

            try:
                from src.core.models.user_preferences import PreferenceUtilisateur

                prefs_row = session.query(PreferenceUtilisateur).first()
                if prefs_row:
                    prefs_data = prefs_row.preferences or {}
                    if pour_qui == "anne":
                        tailles_prefs = prefs_data.get("taille_vetements_anne", {})
                    elif pour_qui == "mathieu":
                        tailles_prefs = prefs_data.get("taille_vetements_mathieu", {})
                    elif pour_qui == "jules":
                        tailles_prefs = prefs_data.get("taille_vetements_jules", {})
                    else:
                        tailles_prefs = {}

                    if not taille and tailles_prefs:
                        if "chaussures" in categorie:
                            taille = str(tailles_prefs.get("pointure", "") or prefs_data.get("pointure_jules", ""))
                        else:
                            taille = (
                                tailles_prefs.get("haut")
                                or tailles_prefs.get("tee_shirt")
                                or tailles_prefs.get("s")
                                or ""
                            )
                        if taille:
                            raisons.append(f"Taille '{taille}' issue des préférences famille")
            except Exception:  # noqa: BLE001
                pass  # Préférences optionnelles

            # Raison choix plateforme
            if plateforme == "vinted":
                raisons.append(
                    f"Catégorie '{categorie}' → Vinted recommandée (vêtements, jouets, livres)"
                )
            else:
                raisons.append(
                    f"Catégorie '{categorie}' → LeBonCoin recommandé (divers, électronique, mobilier)"
                )

            # Prix conseillé
            base_prix = achat.prix_reel or achat.prix_estime
            prix_suggere = (
                round(float(base_prix) * 0.4, 2) if base_prix else None
            )
            if prix_suggere:
                raisons.append(f"Prix conseillé : {prix_suggere}€ (40% du prix d'achat)")

            return {
                "achat_id": achat_id,
                "plateforme": plateforme,
                "plateforme_libelle": plateforme_libelle,
                "marque": achat.magasin,
                "taille": taille or achat.taille,
                "prix_suggere": prix_suggere,
                "pour_qui": pour_qui,
                "raisons": raisons,
            }

    return await executer_async(_query)




@router.patch("/routines/{routine_id}/completer", responses=REPONSES_CRUD_ECRITURE)
@gerer_exception_api
async def completer_routine(
    routine_id: int,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Marque une routine comme complétée aujourd'hui."""
    from src.core.models.maison import Routine

    def _query():
        with executer_avec_session() as session:
            routine = session.query(Routine).filter(Routine.id == routine_id).first()
            if not routine:
                raise HTTPException(status_code=404, detail="Routine non trouvée")
            routine.derniere_completion = date.today()
            session.commit()
            return {
                "id": routine.id,
                "nom": routine.nom,
                "derniere_completion": routine.derniere_completion.isoformat(),
            }

    return await executer_async(_query)


# ═══════════════════════════════════════════════════════════
# BUDGET — RÉSUMÉ MENSUEL
# ═══════════════════════════════════════════════════════════


@router.get("/budget/resume-mois", responses=REPONSES_LISTE)
@gerer_exception_api
async def resume_budget_mois(
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Retourne le résumé des achats du mois courant vs précédent."""
    from src.core.models import AchatFamille

    def _query():
        today = date.today()
        with executer_avec_session() as session:
            # Mois courant
            debut_courant = today.replace(day=1)
            achats_courant = (
                session.query(AchatFamille)
                .filter(
                    AchatFamille.achete == True,  # noqa: E712
                    AchatFamille.date_achat >= debut_courant,
                )
                .all()
            )
            total_courant = sum(
                (a.prix_reel or a.prix_estime or 0) for a in achats_courant
            )

            # Calcul début du mois précédent
            if today.month == 1:
                debut_prec = today.replace(year=today.year - 1, month=12, day=1)
                fin_prec = today.replace(day=1)
            else:
                debut_prec = today.replace(month=today.month - 1, day=1)
                fin_prec = debut_courant

            achats_prec = (
                session.query(AchatFamille)
                .filter(
                    AchatFamille.achete == True,  # noqa: E712
                    AchatFamille.date_achat >= debut_prec,
                    AchatFamille.date_achat < fin_prec,
                )
                .all()
            )
            total_prec = sum(
                (a.prix_reel or a.prix_estime or 0) for a in achats_prec
            )

            variation = None
            if total_prec and total_prec > 0:
                variation = round((total_courant - total_prec) / total_prec * 100, 1)

            par_categorie: dict[str, float] = {}
            for a in achats_courant:
                par_categorie[a.categorie] = par_categorie.get(a.categorie, 0) + (
                    a.prix_reel or a.prix_estime or 0
                )

            return {
                "mois_courant": debut_courant.strftime("%Y-%m"),
                "total_courant": total_courant,
                "total_precedent": total_prec if total_prec else None,
                "variation_pct": variation,
                "achats_par_categorie": par_categorie,
            }

    return await executer_async(_query)


# ═══════════════════════════════════════════════════════════
# CONFIG GARDE
# ═══════════════════════════════════════════════════════════


@router.get("/config/garde", responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def lire_config_garde(
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Retourne la configuration de garde / crèche."""
    from src.services.famille.jours_speciaux import obtenir_service_jours_speciaux

    def _query():
        service = obtenir_service_jours_speciaux()
        service.charger_config_depuis_db()
        from src.services.famille import jours_speciaux as _mod

        cfg = dict(_mod._config_creche)
        return {
            "semaines_fermeture": cfg.get("semaines_fermeture", []),
            "nom_creche": cfg.get("nom_creche", ""),
            "zone_academique": cfg.get("zone_academique", "B"),
            "annee_courante": cfg.get("annee_courante"),
        }

    return await executer_async(_query)


@router.put("/config/garde", responses=REPONSES_CRUD_ECRITURE)
@gerer_exception_api
async def sauvegarder_config_garde(
    payload: ConfigGardeRequest,
    user: dict[str, Any] = Depends(require_auth),
) -> MessageResponse:
    """Sauvegarde la configuration crèche."""
    from src.services.famille.jours_speciaux import obtenir_service_jours_speciaux

    def _query():
        service = obtenir_service_jours_speciaux()
        semaines = [s.model_dump() for s in payload.semaines_fermeture]
        service.sauvegarder_fermetures_creche(
            semaines=semaines,
            nom_creche=payload.nom_creche,
            zone_academique=payload.zone_academique,
        )
        return MessageResponse(message="Configuration crèche sauvegardée")

    return await executer_async(_query)


# ═══════════════════════════════════════════════════════════
# CONFIG — PRÉFÉRENCES FAMILIALES
# ═══════════════════════════════════════════════════════════


@router.get("/config/preferences", responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def lire_preferences_famille(
    user: dict[str, Any] = Depends(require_auth),
) -> PreferencesFamilleResponse:
    """Lit les préférences familiales (tailles, style achats, intérêts)."""

    def _query():
        from src.core.models.user_preferences import PreferenceUtilisateur
        from sqlalchemy import select as sa_select

        with executer_avec_session() as session:
            pref = session.execute(
                sa_select(PreferenceUtilisateur)
            ).scalar_one_or_none()
            if pref is None:
                return PreferencesFamilleResponse()
            return PreferencesFamilleResponse(
                taille_vetements_anne=pref.taille_vetements_anne or {},
                taille_vetements_mathieu=pref.taille_vetements_mathieu or {},
                style_achats_anne=pref.style_achats_anne or {},
                style_achats_mathieu=pref.style_achats_mathieu or {},
                interets_gaming=pref.interets_gaming or [],
                interets_culture=pref.interets_culture or [],
                equipement_activites=pref.equipement_activites or {},
            )

    return await executer_async(_query)


@router.put("/config/preferences", responses=REPONSES_CRUD_ECRITURE)
@gerer_exception_api
async def sauvegarder_preferences_famille(
    payload: PreferencesFamilleRequest,
    user: dict[str, Any] = Depends(require_auth),
) -> MessageResponse:
    """Sauvegarde les préférences familiales (tailles, style achats, intérêts)."""

    def _query():
        from src.core.models.user_preferences import PreferenceUtilisateur
        from sqlalchemy import select as sa_select

        with executer_avec_session() as session:
            pref = session.execute(
                sa_select(PreferenceUtilisateur)
            ).scalar_one_or_none()
            if pref is None:
                pref = PreferenceUtilisateur(user_id="matanne")
                session.add(pref)
            pref.taille_vetements_anne = payload.taille_vetements_anne
            pref.taille_vetements_mathieu = payload.taille_vetements_mathieu
            pref.style_achats_anne = payload.style_achats_anne
            pref.style_achats_mathieu = payload.style_achats_mathieu
            pref.interets_gaming = payload.interets_gaming
            pref.interets_culture = payload.interets_culture
            pref.equipement_activites = payload.equipement_activites
            session.commit()
        return MessageResponse(message="Préférences familiales sauvegardées")

    return await executer_async(_query)


# ═══════════════════════════════════════════════════════════
# PLANNING — JOURS SANS CRÈCHE
# ═══════════════════════════════════════════════════════════


@router.get("/planning/jours-sans-creche", responses=REPONSES_LISTE)
@gerer_exception_api
async def jours_sans_creche(
    mois: str | None = Query(None, description="Mois YYYY-MM. Par défaut: mois courant"),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Liste les jours sans crèche pour un mois donné."""
    from src.services.famille.jours_speciaux import obtenir_service_jours_speciaux

    def _query():
        service = obtenir_service_jours_speciaux()
        service.charger_config_depuis_db()

        if mois:
            try:
                annee, mo = int(mois[:4]), int(mois[5:7])
            except (ValueError, IndexError):
                raise HTTPException(status_code=422, detail="Format mois invalide, attendu YYYY-MM")
        else:
            annee, mo = date.today().year, date.today().month

        tous_jours = service.fermetures_creche(annee=annee)
        jours_du_mois = [j for j in tous_jours if j.date_jour.month == mo]
        return {
            "mois": f"{annee:04d}-{mo:02d}",
            "jours": [
                {"date": j.date_jour.isoformat(), "label": j.nom}
                for j in jours_du_mois
            ],
            "total": len(jours_du_mois),
        }

    return await executer_async(_query)


# ═══════════════════════════════════════════════════════════
# WEEKEND — SUGGESTIONS SÉJOUR
# ═══════════════════════════════════════════════════════════


@router.post("/weekend/suggestions-sejour", responses=REPONSES_LISTE)
@gerer_exception_api
async def suggestions_sejour(
    payload: SuggestionsSejourRequest,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Génère des suggestions d'activités pour un séjour."""
    from src.services.famille.weekend_ai import obtenir_service_weekend_ia

    def _query():
        service = obtenir_service_weekend_ia()
        texte = service.suggerer_activites_sejour(
            destination=payload.destination,
            nb_jours=payload.nb_jours,
            age_enfant_mois=payload.age_jules_mois or 0,
            nb_suggestions=payload.nb_suggestions,
        )
        return {"suggestions": texte, "destination": payload.destination}

    return await executer_async(_query)


# ═══════════════════════════════════════════════════════════
# SUGGESTIONS IA ACHATS (Phase P)
# ═══════════════════════════════════════════════════════════


class SuggestionsAchatsRequest(BaseModel):
    """Demande de suggestions d'achats/cadeaux IA."""
    type: str = Field(..., description="'anniversaire' | 'jalon' | 'saison'")
    nom: str | None = Field(None, description="Prénom de la personne (pour anniversaire)")
    age: int | None = Field(None, ge=0, description="Âge en années (anniversaire) ou mois (jalon/saison)")
    relation: str | None = Field(None, description="parent, ami, etc. (pour anniversaire)")
    budget_max: float = Field(default=50.0, ge=5, le=500)
    historique_cadeaux: list[str] | None = None
    prochains_jalons: list[str] | None = None
    saison: str | None = None
    tailles: dict | None = None


class SuggestionsAchatsAutoRequest(BaseModel):
    """Demande auto pour suggestions achats proactives (anniversaires/jalons/saison)."""

    budget_max: float = Field(default=60.0, ge=5, le=500)
    relation_defaut: str = Field(default="famille")


def _saison_actuelle() -> str:
    mois = date.today().month
    if mois in (12, 1, 2):
        return "hiver"
    if mois in (3, 4, 5):
        return "printemps"
    if mois in (6, 7, 8):
        return "ete"
    return "automne"


@router.post("/achats/suggestions-ia", responses=REPONSES_LISTE)
@gerer_exception_api
async def suggestions_achats_ia(
    payload: SuggestionsAchatsRequest,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Génère des suggestions d'achats ou cadeaux via IA (Mistral)."""
    from src.services.famille.achats_ia import obtenir_service_achats_ia

    service = obtenir_service_achats_ia()

    if payload.type == "anniversaire":
        if not payload.nom or payload.age is None:
            raise HTTPException(status_code=422, detail="'nom' et 'age' requis pour les suggestions d'anniversaire")
        suggestions = await service.suggerer_cadeaux_anniversaire(
            nom=payload.nom,
            age=payload.age,
            relation=payload.relation or "ami(e)",
            budget_max=payload.budget_max,
            historique_cadeaux=payload.historique_cadeaux,
        )
    elif payload.type == "jalon":
        if payload.age is None or not payload.prochains_jalons:
            raise HTTPException(status_code=422, detail="'age' (en mois) et 'prochains_jalons' requis")
        suggestions = await service.suggerer_achats_jalon(
            age_mois=payload.age,
            prochains_jalons=payload.prochains_jalons,
        )
    elif payload.type == "saison":
        if payload.age is None or not payload.saison:
            raise HTTPException(status_code=422, detail="'age' (en mois) et 'saison' requis")
        suggestions = await service.suggerer_achats_saison(
            age_enfant_mois=payload.age,
            saison=payload.saison,
            tailles=payload.tailles,
        )
    else:
        raise HTTPException(status_code=422, detail="type doit être 'anniversaire', 'jalon' ou 'saison'")

    return {"suggestions": suggestions, "total": len(suggestions), "type": payload.type}


@router.post("/achats/suggestions", responses=REPONSES_LISTE)
@gerer_exception_api
async def suggestions_achats_auto(
    payload: SuggestionsAchatsAutoRequest,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Génère automatiquement des suggestions d'achats proactives.

    Déclencheurs:
    - Anniversaires proches (J-14)
    - Prochains jalons de Jules
    - Saison en cours
    """
    from src.services.famille.achats_ia import obtenir_service_achats_ia
    from src.services.famille.contexte import obtenir_service_contexte_familial

    async def _query() -> dict[str, Any]:
        service_ia = obtenir_service_achats_ia()
        contexte_service = obtenir_service_contexte_familial()
        contexte = contexte_service.obtenir_contexte()

        suggestions_anniversaire: list[dict[str, Any]] = []
        suggestions_jalons: list[dict[str, Any]] = []
        suggestions_saison: list[dict[str, Any]] = []

        anniversaires = (contexte.get("anniversaires_proches") or [])
        anniversaire_cible = next((a for a in anniversaires if (a.get("jours_restants") or 99) <= 14), None)
        if anniversaire_cible:
            suggestions_anniversaire = await service_ia.suggerer_cadeaux_anniversaire(
                nom=anniversaire_cible.get("nom_personne", "Proche"),
                age=anniversaire_cible.get("age") or 3,
                relation=anniversaire_cible.get("relation") or payload.relation_defaut,
                budget_max=payload.budget_max,
            )

        jules = contexte.get("jules") or {}
        prochains_jalons = jules.get("prochains_jalons") or []
        age_mois = jules.get("age_mois") or 24
        if prochains_jalons:
            suggestions_jalons = await service_ia.suggerer_achats_jalon(
                age_mois=age_mois,
                prochains_jalons=prochains_jalons,
            )

        suggestions_saison = await service_ia.suggerer_achats_saison(
            age_enfant_mois=age_mois,
            saison=_saison_actuelle(),
            tailles=None,
        )

        toutes = [
            *[{**s, "source": "anniversaire"} for s in suggestions_anniversaire],
            *[{**s, "source": "jalon"} for s in suggestions_jalons],
            *[{**s, "source": "saison"} for s in suggestions_saison],
        ]

        return {
            "suggestions": toutes,
            "groupes": {
                "anniversaire": suggestions_anniversaire,
                "jalon": suggestions_jalons,
                "saison": suggestions_saison,
            },
            "total": len(toutes),
        }

    return await _query()


# ═══════════════════════════════════════════════════════════
# RAPPELS FAMILLE (Phase Q)
# ═══════════════════════════════════════════════════════════


@router.get("/rappels/evaluer", responses=REPONSES_LISTE)
@gerer_exception_api
async def evaluer_rappels_famille(
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Évalue et retourne les rappels pertinents du jour."""
    from src.services.famille.rappels import obtenir_service_rappels_famille

    def _query():
        service = obtenir_service_rappels_famille()
        rappels = service.evaluer_rappels()
        return {
            "rappels": [r if isinstance(r, dict) else r for r in rappels],
            "total": len(rappels),
        }

    return await executer_async(_query)


@router.post("/rappels/envoyer", responses=REPONSES_CRUD_CREATION)
@gerer_exception_api
async def envoyer_rappels_famille(
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Déclenche l'envoi push des rappels du jour."""
    from src.services.famille.rappels import obtenir_service_rappels_famille

    def _query():
        service = obtenir_service_rappels_famille()
        nb_envoyes = service.envoyer_rappels_du_jour()
        return {"envoyes": nb_envoyes, "message": f"{nb_envoyes} rappel(s) envoyé(s)"}

    return await executer_async(_query)


# ═══════════════════════════════════════════════════════════
# CROISSANCE OMS (Phase R)
# ═══════════════════════════════════════════════════════════


@router.get("/jules/croissance", responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def obtenir_croissance_jules(
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Retourne les normes OMS de croissance pour l'âge de Jules."""
    from src.services.famille.contexte import obtenir_service_contexte_familial
    from src.services.famille.jules import obtenir_service_jules

    def _query():
        jules_service = obtenir_service_jules()
        date_naissance = jules_service.get_date_naissance_jules()
        if not date_naissance:
            raise HTTPException(status_code=404, detail="Profil Jules non trouvé")

        age_mois = (date.today() - date_naissance).days // 30

        contexte_service = obtenir_service_contexte_familial()
        normes = contexte_service.obtenir_croissance_oms(age_mois, sexe="M")

        return {
            "age_mois": age_mois,
            "normes": normes,
        }

    return await executer_async(_query)


# ═══════════════════════════════════════════════════════════
# SUGGESTIONS ACTIVITÉS SIMPLIFIÉES (Phase O)
# ═══════════════════════════════════════════════════════════


@router.post("/activites/suggestions-ia-auto", responses=REPONSES_LISTE)
@gerer_exception_api
async def suggestions_activites_auto(
    payload: SuggestionsActivitesSimpleRequest,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Suggestions d'activités avec météo et âge auto-injectés (sans saisie manuelle)."""
    from src.services.famille.activites import obtenir_service_activites
    from src.services.famille.jours_speciaux import obtenir_service_jours_speciaux
    from src.services.famille.jules import obtenir_service_jules
    from src.services.integrations.weather.service import obtenir_service_meteo

    def _structurer_suggestions_texte(texte: str) -> list[dict[str, Any]]:
        """Convertit le texte IA en suggestions structurées pour pré-remplissage UI."""
        suggestions: list[dict[str, Any]] = []
        if not texte:
            return suggestions

        blocs = [b.strip() for b in texte.split("🎯") if b.strip()]
        for bloc in blocs:
            lignes = [l.strip() for l in bloc.splitlines() if l.strip()]
            titre = lignes[0] if lignes else "Activité familiale"
            description = ""
            duree_minutes = 90
            type_activite = "autre"
            lieu = "interieur"

            for ligne in lignes[1:]:
                low = ligne.lower()
                if "description" in low:
                    description = ligne.split(":", 1)[-1].strip()
                elif "dur" in low and any(c.isdigit() for c in ligne):
                    chiffres = "".join(c if c.isdigit() else " " for c in ligne).split()
                    if chiffres:
                        duree_minutes = int(chiffres[0]) * 60 if "heure" in low else int(chiffres[0])
                elif "météo" in low or "meteo" in low:
                    lieu = "exterieur" if "extérieur" in low or "exterieur" in low else "interieur"

            titre_low = titre.lower()
            if "parc" in titre_low or "balade" in titre_low:
                type_activite = "sortie"
            elif "sport" in titre_low:
                type_activite = "sport"
            elif "atelier" in titre_low or "dessin" in titre_low:
                type_activite = "culture"
            elif "jeu" in titre_low:
                type_activite = "jeu"

            suggestions.append(
                {
                    "titre": titre,
                    "description": description or "Suggestion IA adaptée au contexte du jour.",
                    "type": type_activite,
                    "duree_minutes": duree_minutes,
                    "lieu": lieu,
                }
            )

        return suggestions

    async def _query():
        # Auto-inject météo
        meteo_service = obtenir_service_meteo()
        previsions = meteo_service.get_previsions(nb_jours=3)
        meteo_txt = "variable"
        if previsions:
            meteo_txt = previsions[0].condition or "variable"

        # Force intérieur si pluie
        type_effectif = payload.type_prefere
        if previsions and previsions[0].precipitation_mm > 5 and type_effectif == "les_deux":
            type_effectif = "interieur"

        # Auto-inject âge Jules
        jules_service = obtenir_service_jules()
        date_naissance = jules_service.get_date_naissance_jules()
        age_mois = 19
        if date_naissance:
            age_mois = (date.today() - date_naissance).days // 30

        # Détecter journée libre (férié + crèche fermée dans les 3 prochains jours)
        jours_service = obtenir_service_jours_speciaux()
        prochains = jours_service.prochains_jours_speciaux(nb=5)
        from datetime import timedelta

        journee_libre = any(
            j.date_jour <= date.today() + timedelta(days=3)
            and j.type in ("ferie", "creche")
            for j in prochains
        )

        # Construire le prompt enrichi
        prompt_extra = ""
        if journee_libre:
            prompt_extra = " C'est une journée libre (férié ou crèche fermée), propose des activités pour une journée complète."

        # Appel au service IA activités existant
        service = obtenir_service_activites()
        if hasattr(service, "suggerer_activites_ia"):
            resultat = service.suggerer_activites_ia(
                age_mois=age_mois,
                meteo=meteo_txt,
                budget_max=payload.budget_max,
            )
            return {
                "suggestions": resultat,
                "suggestions_struct": _structurer_suggestions_texte(str(resultat)),
                "meteo": meteo_txt,
                "journee_libre": journee_libre,
            }

        # Fallback: utiliser le service weekend IA
        from src.services.famille.weekend_ai import obtenir_weekend_ai_service

        weekend_service = obtenir_weekend_ai_service()
        resultat = await weekend_service.suggerer_activites(
            meteo=meteo_txt + (" " + type_effectif if type_effectif != "les_deux" else ""),
            age_enfant_mois=age_mois,
            budget=int(payload.budget_max),
            nb_suggestions=5,
        )
        return {
            "suggestions": resultat,
            "suggestions_struct": _structurer_suggestions_texte(str(resultat)),
            "meteo": meteo_txt,
            "journee_libre": journee_libre,
        }

    return await _query()
