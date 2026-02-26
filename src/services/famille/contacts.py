"""
Service Contacts Famille - Répertoire familial avec catégories.

Opérations:
- CRUD contacts avec catégorisation
- Recherche par catégorie (médical, garde, urgence, etc.)
- Contacts d'urgence
"""

import logging
from typing import Any

from sqlalchemy import func
from sqlalchemy.orm import Session

from src.core.decorators import avec_cache, avec_gestion_erreurs, avec_session_db
from src.core.models import ContactFamille
from src.core.monitoring import chronometre
from src.services.core.base import BaseService
from src.services.core.events import obtenir_bus
from src.services.core.registry import service_factory

logger = logging.getLogger(__name__)

CATEGORIES_CONTACTS = [
    "medical",
    "garde",
    "education",
    "administration",
    "famille",
    "urgence",
]


class ServiceContacts(BaseService[ContactFamille]):
    """Service de gestion des contacts famille.

    Hérite de BaseService[ContactFamille] pour le CRUD générique.
    """

    def __init__(self):
        super().__init__(model=ContactFamille, cache_ttl=600)

    # ═══════════════════════════════════════════════════════════
    # CRUD
    # ═══════════════════════════════════════════════════════════

    @chronometre("contacts.liste", seuil_alerte_ms=1000)
    @avec_cache(ttl=600)
    @avec_gestion_erreurs(default_return=[])
    @avec_session_db
    def obtenir_contacts(
        self,
        *,
        categorie: str | None = None,
        urgence_seulement: bool = False,
        db: Session | None = None,
    ) -> list[ContactFamille]:
        """Récupère les contacts, filtrés optionnellement."""
        if db is None:
            return []
        query = db.query(ContactFamille)
        if categorie:
            query = query.filter_by(categorie=categorie)
        if urgence_seulement:
            query = query.filter_by(est_urgence=True)
        return query.order_by(ContactFamille.nom.asc()).all()

    @avec_gestion_erreurs(default_return=None)
    @avec_session_db
    def ajouter_contact(
        self, data: dict[str, Any], *, db: Session | None = None
    ) -> ContactFamille | None:
        """Ajoute un contact famille."""
        if db is None:
            return None
        contact = ContactFamille(**data)
        db.add(contact)
        db.commit()
        db.refresh(contact)
        logger.info("Contact ajouté: %s (%s)", contact.nom, contact.categorie)
        obtenir_bus().emettre(
            "contacts.ajoute",
            {"contact_id": contact.id, "nom": contact.nom},
            source="ServiceContacts",
        )
        return contact

    @avec_gestion_erreurs(default_return=False)
    @avec_session_db
    def modifier_contact(
        self, contact_id: int, data: dict[str, Any], *, db: Session | None = None
    ) -> bool:
        """Modifie un contact existant."""
        if db is None:
            return False
        contact = db.query(ContactFamille).get(contact_id)
        if not contact:
            return False
        for key, value in data.items():
            if hasattr(contact, key):
                setattr(contact, key, value)
        db.commit()
        logger.info("Contact modifié: id=%d", contact_id)
        return True

    @avec_gestion_erreurs(default_return=False)
    @avec_session_db
    def supprimer_contact(self, contact_id: int, *, db: Session | None = None) -> bool:
        """Supprime un contact."""
        if db is None:
            return False
        deleted = db.query(ContactFamille).filter_by(id=contact_id).delete()
        db.commit()
        if deleted > 0:
            logger.info("Contact supprimé: id=%d", contact_id)
        return deleted > 0

    # ═══════════════════════════════════════════════════════════
    # RECHERCHE
    # ═══════════════════════════════════════════════════════════

    @avec_cache(ttl=300)
    @avec_gestion_erreurs(default_return=[])
    @avec_session_db
    def rechercher_contacts(self, terme: str, *, db: Session | None = None) -> list[ContactFamille]:
        """Recherche de contacts par nom, prénom ou relation."""
        if db is None:
            return []
        filtre = f"%{terme.lower()}%"
        return (
            db.query(ContactFamille)
            .filter(
                func.lower(ContactFamille.nom).like(filtre)
                | func.lower(ContactFamille.prenom).like(filtre)
                | func.lower(ContactFamille.relation).like(filtre)
            )
            .order_by(ContactFamille.nom.asc())
            .all()
        )

    @avec_cache(ttl=600)
    @avec_gestion_erreurs(default_return={})
    @avec_session_db
    def obtenir_stats_contacts(self, *, db: Session | None = None) -> dict[str, int]:
        """Statistiques par catégorie de contacts."""
        if db is None:
            return {}
        resultats = (
            db.query(ContactFamille.categorie, func.count(ContactFamille.id))
            .group_by(ContactFamille.categorie)
            .all()
        )
        return {cat: count for cat, count in resultats}


# ═══════════════════════════════════════════════════════════
# FACTORY
# ═══════════════════════════════════════════════════════════


@service_factory("contacts_famille", tags={"famille", "contacts"})
def obtenir_service_contacts() -> ServiceContacts:
    """Factory pour le service contacts famille (singleton via ServiceRegistry)."""
    return ServiceContacts()


# Alias anglais
get_contacts_service = obtenir_service_contacts
