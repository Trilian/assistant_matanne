"""
Service Documents Famille - Coffre-fort numérique de documents.

Opérations:
- CRUD documents avec catégorisation
- Alertes d'expiration
- Recherche par type et membre
"""

import logging
from datetime import date as date_type
from datetime import timedelta
from typing import Any, TypedDict

from sqlalchemy import and_, func
from sqlalchemy.orm import Session

from src.core.decorators import avec_cache, avec_gestion_erreurs, avec_session_db
from src.core.models import DocumentFamille
from src.core.monitoring import chronometre
from src.services.core.base import BaseService
from src.services.core.events import obtenir_bus
from src.services.core.registry import service_factory

logger = logging.getLogger(__name__)

TYPES_DOCUMENTS = [
    "identite",
    "medical",
    "scolaire",
    "administratif",
    "assurance",
    "autre",
]


class AlerteDocumentDict(TypedDict):
    """Alerte pour un document expirant bientôt."""

    id: int
    nom: str
    type_document: str
    date_expiration: str
    jours_restants: int
    est_expire: bool


class ServiceDocuments(BaseService[DocumentFamille]):
    """Service de gestion des documents famille.

    Hérite de BaseService[DocumentFamille] pour le CRUD générique.
    """

    def __init__(self):
        super().__init__(model=DocumentFamille, cache_ttl=600)

    # ═══════════════════════════════════════════════════════════
    # CRUD
    # ═══════════════════════════════════════════════════════════

    @chronometre("documents.liste", seuil_alerte_ms=1000)
    @avec_cache(ttl=600)
    @avec_gestion_erreurs(default_return=[])
    @avec_session_db
    def obtenir_documents(
        self,
        *,
        type_document: str | None = None,
        membre: str | None = None,
        db: Session | None = None,
    ) -> list[DocumentFamille]:
        """Récupère les documents, filtrés optionnellement."""
        if db is None:
            return []
        query = db.query(DocumentFamille)
        if type_document:
            query = query.filter_by(type_document=type_document)
        if membre:
            query = query.filter_by(membre_famille=membre)
        return query.order_by(DocumentFamille.nom.asc()).all()

    @avec_gestion_erreurs(default_return=None)
    @avec_session_db
    def ajouter_document(
        self, data: dict[str, Any], *, db: Session | None = None
    ) -> DocumentFamille | None:
        """Ajoute un document famille."""
        if db is None:
            return None
        doc = DocumentFamille(**data)
        db.add(doc)
        db.commit()
        db.refresh(doc)
        logger.info("Document ajouté: %s (%s)", doc.nom, doc.type_document)
        obtenir_bus().emettre(
            "documents.ajoute",
            {"document_id": doc.id, "nom": doc.nom},
            source="ServiceDocuments",
        )
        return doc

    @avec_gestion_erreurs(default_return=False)
    @avec_session_db
    def modifier_document(
        self, document_id: int, data: dict[str, Any], *, db: Session | None = None
    ) -> bool:
        """Modifie un document existant."""
        if db is None:
            return False
        doc = db.query(DocumentFamille).get(document_id)
        if not doc:
            return False
        for key, value in data.items():
            if hasattr(doc, key):
                setattr(doc, key, value)
        db.commit()
        return True

    @avec_gestion_erreurs(default_return=False)
    @avec_session_db
    def supprimer_document(self, document_id: int, *, db: Session | None = None) -> bool:
        """Supprime un document."""
        if db is None:
            return False
        deleted = db.query(DocumentFamille).filter_by(id=document_id).delete()
        db.commit()
        return deleted > 0

    # ═══════════════════════════════════════════════════════════
    # ALERTES EXPIRATION
    # ═══════════════════════════════════════════════════════════

    @chronometre("documents.alertes", seuil_alerte_ms=1000)
    @avec_cache(ttl=3600)
    @avec_gestion_erreurs(default_return=[])
    @avec_session_db
    def obtenir_alertes_expiration(
        self, *, jours: int = 90, db: Session | None = None
    ) -> list[AlerteDocumentDict]:
        """Identifie les documents expirant dans les prochains jours."""
        if db is None:
            return []
        aujourd_hui = date_type.today()
        limite = aujourd_hui + timedelta(days=jours)
        docs = (
            db.query(DocumentFamille)
            .filter(
                and_(
                    DocumentFamille.date_expiration.isnot(None),
                    DocumentFamille.date_expiration <= limite,
                )
            )
            .order_by(DocumentFamille.date_expiration.asc())
            .all()
        )
        alertes: list[AlerteDocumentDict] = []
        for doc in docs:
            if doc.date_expiration:
                jours_restants = (doc.date_expiration - aujourd_hui).days
                alertes.append(
                    AlerteDocumentDict(
                        id=doc.id,
                        nom=doc.nom,
                        type_document=doc.type_document,
                        date_expiration=doc.date_expiration.isoformat(),
                        jours_restants=jours_restants,
                        est_expire=jours_restants < 0,
                    )
                )
        return alertes

    # ═══════════════════════════════════════════════════════════
    # STATISTIQUES
    # ═══════════════════════════════════════════════════════════

    @avec_cache(ttl=600)
    @avec_gestion_erreurs(default_return={})
    @avec_session_db
    def obtenir_stats_documents(self, *, db: Session | None = None) -> dict[str, Any]:
        """Statistiques sur les documents famille."""
        if db is None:
            return {}
        total = db.query(func.count(DocumentFamille.id)).scalar() or 0
        par_type = dict(
            db.query(DocumentFamille.type_document, func.count(DocumentFamille.id))
            .group_by(DocumentFamille.type_document)
            .all()
        )
        expires = (
            db.query(func.count(DocumentFamille.id))
            .filter(
                and_(
                    DocumentFamille.date_expiration.isnot(None),
                    DocumentFamille.date_expiration < date_type.today(),
                )
            )
            .scalar()
            or 0
        )
        return {
            "total": total,
            "par_type": par_type,
            "expires": expires,
        }


# ═══════════════════════════════════════════════════════════
# FACTORY
# ═══════════════════════════════════════════════════════════


@service_factory("documents_famille", tags={"famille", "documents"})
def obtenir_service_documents() -> ServiceDocuments:
    """Factory pour le service documents famille (singleton via ServiceRegistry)."""
    return ServiceDocuments()


# Alias anglais
get_documents_service = obtenir_service_documents
