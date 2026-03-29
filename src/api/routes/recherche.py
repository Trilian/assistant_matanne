"""
Routes API pour la recherche globale.

Recherche multi-entités à travers toutes les données utilisateur.
"""

from typing import Any

from fastapi import APIRouter, Depends, Query
from sqlalchemy import or_

from src.api.dependencies import require_auth
from src.api.utils import executer_async, executer_avec_session, gerer_exception_api

router = APIRouter(prefix="/api/v1/recherche", tags=["Recherche"])


@router.get("/global")
@gerer_exception_api
async def recherche_globale(
    q: str = Query(..., min_length=2, description="Terme de recherche minimum 2 caractères"),
    limit: int = Query(20, ge=1, le=100, description="Nombre maximum de résultats"),
    user: dict[str, Any] = Depends(require_auth),
) -> list[dict[str, Any]]:
    """
    Recherche globale à travers toutes les entités.
    
    Recherche dans : recettes, projets maison, activités famille, notes, contacts.
    
    Args:
        q: Terme de recherche (min 2 caractères)
        limit: Maximum de résultats (défaut: 20)
        user: Utilisateur authentifié
    
    Returns:
        Liste de résultats avec type, id, titre, description, url
    """
    import logging
    from src.core.models import (
        Recette,
        Projet,
        ActiviteFamille,
        NoteMemo,
        ContactFamille,
    )

    _logger = logging.getLogger(__name__)
    
    def _search():
        user_id = user.get("sub") or user.get("id") or "dev"
        resultats = []
        
        with executer_avec_session() as session:
            # Pattern de recherche (fuzzy - insensible à la casse)
            pattern = f"%{q.lower()}%"
            
            # 1. Recettes
            recettes = (
                session.query(Recette)
                .filter(
                    Recette.cree_par == user_id,
                    or_(
                        Recette.nom.ilike(pattern),
                        Recette.description.ilike(pattern),
                    )
                )
                .limit(limit // 5)  # Max 1/5 des résultats pour chaque type
                .all()
            )
            for r in recettes:
                resultats.append({
                    "type": "recette",
                    "id": r.id,
                    "titre": r.nom,
                    "description": r.description or f"{r.temps_total}min • {r.portions} pers",
                    "url": f"/cuisine/recettes/{r.id}",
                    "categorie": r.categorie,
                    "icone": "📖",
                })
            
            # 2. Projets maison
            projets = (
                session.query(Projet)
                .filter(
                    Projet.cree_par == user_id,
                    or_(
                        Projet.titre.ilike(pattern),
                        Projet.description.ilike(pattern),
                    )
                )
                .limit(limit // 5)
                .all()
            )
            for p in projets:
                resultats.append({
                    "type": "projet",
                    "id": p.id,
                    "titre": p.titre,
                    "description": p.description or f"Statut: {p.statut}",
                    "url": f"/maison/projets",
                    "statut": p.statut,
                    "icone": "🔨",
                })
            
            # 3. Activités famille (ActiviteFamille — titre + description)
            try:
                activites = (
                    session.query(ActiviteFamille)
                    .filter(
                        or_(
                            ActiviteFamille.titre.ilike(pattern),
                            ActiviteFamille.description.ilike(pattern),
                        )
                    )
                    .limit(limit // 5)
                    .all()
                )
                for a in activites:
                    resultats.append({
                        "type": "activite",
                        "id": a.id,
                        "titre": a.titre,
                        "description": a.description or f"{a.type_activite}",
                        "url": "/famille/activites",
                        "icone": "🎯",
                    })
            except Exception as e:
                _logger.warning("[recherche] Erreur requête activités famille: %s", e)
            
            # 4. Notes / mémos
            try:
                notes = (
                    session.query(NoteMemo)
                    .filter(
                        or_(
                            NoteMemo.titre.ilike(pattern),
                            NoteMemo.contenu.ilike(pattern),
                        )
                    )
                    .limit(limit // 5)
                    .all()
                )
                for n in notes:
                    resultats.append({
                        "type": "note",
                        "id": n.id,
                        "titre": n.titre,
                        "description": (n.contenu[:100] + "...") if n.contenu and len(n.contenu) > 100 else n.contenu,
                        "url": "/outils/notes",
                        "icone": "📝",
                    })
            except Exception as e:
                _logger.warning("[recherche] Erreur requête notes mémos: %s", e)
            
            # 5. Contacts famille (ContactFamille — nom, email, telephone)
            try:
                contacts = (
                    session.query(ContactFamille)
                    .filter(
                        or_(
                            ContactFamille.nom.ilike(pattern),
                            ContactFamille.email.ilike(pattern),
                            ContactFamille.telephone.ilike(pattern),
                        )
                    )
                    .limit(limit // 5)
                    .all()
                )
                for c in contacts:
                    resultats.append({
                        "type": "contact",
                        "id": c.id,
                        "titre": c.nom,
                        "description": c.email or c.telephone or c.categorie,
                        "url": "/famille/contacts",
                        "icone": "👤",
                    })
            except Exception as e:
                _logger.warning("[recherche] Erreur requête contacts famille: %s", e)
        
        # Limiter au nombre total demandé
        return resultats[:limit]
    
    return await executer_async(_search)
