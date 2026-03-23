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

from fastapi import APIRouter, Depends, HTTPException, Query

from src.api.dependencies import require_auth
from src.api.pagination import appliquer_cursor_filter, construire_reponse_cursor, decoder_cursor
from src.api.schemas.common import MessageResponse, ReponsePaginee
from src.api.schemas.errors import (
    REPONSES_CRUD_CREATION,
    REPONSES_CRUD_LECTURE,
    REPONSES_CRUD_SUPPRESSION,
    REPONSES_LISTE,
)
from src.api.utils import executer_async, executer_avec_session, gerer_exception_api

router = APIRouter(prefix="/api/v1/famille", tags=["Famille"])


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
