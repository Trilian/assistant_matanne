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
                    or_(
                        Projet.nom.ilike(pattern),
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
                    "titre": p.nom,
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

            # 6. B11: Plantes jardin
            try:
                from src.core.models.temps_entretien import PlanteJardin

                plantes = (
                    session.query(PlanteJardin)
                    .filter(
                        or_(
                            PlanteJardin.nom.ilike(pattern),
                            PlanteJardin.variete.ilike(pattern),
                            PlanteJardin.notes.ilike(pattern),
                        )
                    )
                    .limit(limit // 5)
                    .all()
                )
                for p in plantes:
                    resultats.append({
                        "type": "plante",
                        "id": p.id,
                        "titre": p.nom,
                        "description": p.variete or f"État: {p.etat}",
                        "url": "/maison/jardin",
                        "icone": "🌱",
                    })
            except Exception as e:
                _logger.warning("[recherche] Erreur requête plantes jardin: %s", e)

            # 7. B11: Contrats maison
            try:
                from src.core.models.maison_extensions import ContratMaison

                contrats = (
                    session.query(ContratMaison)
                    .filter(
                        or_(
                            ContratMaison.nom.ilike(pattern),
                            ContratMaison.fournisseur.ilike(pattern),
                            ContratMaison.type_contrat.ilike(pattern),
                        )
                    )
                    .limit(limit // 5)
                    .all()
                )
                for c in contrats:
                    resultats.append({
                        "type": "contrat",
                        "id": c.id,
                        "titre": c.nom,
                        "description": f"{c.fournisseur or ''} — {c.type_contrat or ''}".strip(" — "),
                        "url": "/maison/contrats",
                        "icone": "📄",
                    })
            except Exception as e:
                _logger.warning("[recherche] Erreur requête contrats maison: %s", e)

            # 8. B11: Documents famille
            try:
                from src.core.models import DocumentFamille

                documents = (
                    session.query(DocumentFamille)
                    .filter(
                        DocumentFamille.actif.is_(True),
                        or_(
                            DocumentFamille.titre.ilike(pattern),
                            DocumentFamille.notes.ilike(pattern),
                        )
                    )
                    .limit(limit // 5)
                    .all()
                )
                for d in documents:
                    resultats.append({
                        "type": "document",
                        "id": d.id,
                        "titre": d.titre,
                        "description": f"{d.categorie} — {d.membre_famille or ''}".strip(" — "),
                        "url": "/famille/documents",
                        "icone": "📁",
                    })
            except Exception as e:
                _logger.warning("[recherche] Erreur requête documents famille: %s", e)
        
        # Limiter au nombre total demandé
        return resultats[:limit]
    
    return await executer_async(_search)
