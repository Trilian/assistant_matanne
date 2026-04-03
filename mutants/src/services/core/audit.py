"""
Service d'audit trail — Journal d'actions métier transversal.

Enregistre toutes les actions utilisateur importantes:
- Qui a fait quoi, quand, sur quelle entité
- Enrichissement automatique via le bus d'événements
- Consultation et recherche de l'historique

Architecture:
- Souscrit automatiquement au bus d'événements (wildcard "*")
- Persiste dans une table `journal_audit` en base
- Fournit une API de query pour UI et exports

Usage:
    from src.services.core.audit import obtenir_service_audit

    service = obtenir_service_audit()

    # Enregistrement manuel
    service.enregistrer_action(
        action="recette.creee",
        entite_type="recette",
        entite_id=42,
        details={"nom": "Tarte aux pommes"},
    )

    # Consultation
    historique = service.consulter(entite_type="recette", limite=50)
"""

from __future__ import annotations

import logging
from collections import deque
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from src.services.core.registry import service_factory

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# SCHÉMAS
# ═══════════════════════════════════════════════════════════


class EntreeAudit(BaseModel):
    """Une entrée dans le journal d'audit."""

    id: int | None = None
    timestamp: datetime = Field(default_factory=datetime.now)
    action: str = ""  # Type d'événement (ex: "recette.creee")
    source: str = ""  # Service émetteur
    utilisateur_id: str | None = None
    entite_type: str = ""  # "recette", "meuble", "planning", etc.
    entite_id: int | str | None = None
    details: dict[str, Any] = Field(default_factory=dict)
    ip_address: str | None = None


class ResultatRecherche(BaseModel):
    """Résultat paginé d'une recherche dans l'audit."""

    entrees: list[EntreeAudit] = Field(default_factory=list)
    total: int = 0
    page: int = 1
    par_page: int = 50


# ═══════════════════════════════════════════════════════════
# SERVICE
# ═══════════════════════════════════════════════════════════


# Extraction du type d'entité à partir du type d'événement
_MAPPING_ENTITE: dict[str, str] = {
    "recette": "recette",
    "stock": "inventaire",
    "courses": "courses",
    "planning": "planning",
    "batch_cooking": "batch_cooking",
    "entretien": "entretien",
    "depenses": "depense",
    "jardin": "jardin",
    "projets": "projet",
    "meubles": "meuble",
    "eco_tips": "action_ecologique",
    "budget": "budget",
    "sante": "sante",
    "loto": "loto",
    "paris": "pari",
    "activites": "activite",
    "routines": "routine",
    "weekend": "weekend",
    "achats": "achat",
    "food_log": "journal_alimentaire",
    "jeux": "jeux",
}


class ServiceAudit:
    """Service d'audit trail transversal.

    - Souscrit au bus d'événements pour enregistrement automatique
    - Persiste en mémoire (buffer) + base de données (si disponible)
    - Fournit recherche par type, entité, période
    """

    def __init__(self, taille_buffer: int = 10_000):
        """Initialise le service d'audit.

        Args:
            taille_buffer: Taille max du buffer mémoire (FIFO).
        """
        self._buffer: deque[EntreeAudit] = deque(maxlen=taille_buffer)
        self._compteur: int = 0
        self._souscrit: bool = False

    # ─── Souscription au bus ───

    def souscrire_bus(self) -> None:
        """Souscrit au bus d'événements pour capturer toutes les actions."""
        if self._souscrit:
            return

        try:
            from src.services.core.events import obtenir_bus

            bus = obtenir_bus()
            bus.souscrire("*", self._on_evenement)
            self._souscrit = True
            logger.info("ServiceAudit souscrit au bus d'événements (wildcard *)")
        except Exception as e:
            logger.warning(f"Impossible de souscrire au bus: {e}")

    def _on_evenement(self, type_evenement: str, data: dict, **kwargs: Any) -> None:
        """Handler appelé pour chaque événement du bus."""
        # Ignorer les événements système internes
        if type_evenement.startswith("service."):
            return

        source = kwargs.get("source", data.get("source", "unknown"))

        # Extraire type d'entité depuis le préfixe de l'événement
        prefixe = type_evenement.split(".")[0] if "." in type_evenement else type_evenement
        entite_type = _MAPPING_ENTITE.get(prefixe, prefixe)

        # Extraire l'ID d'entité (convention: *_id)
        entite_id = None
        for cle in data:
            if cle.endswith("_id") and cle != "utilisateur_id":
                entite_id = data[cle]
                break

        self.enregistrer_action(
            action=type_evenement,
            source=source,
            entite_type=entite_type,
            entite_id=entite_id,
            details=data,
        )

    # ─── API publique ───

    def enregistrer_action(
        self,
        action: str,
        entite_type: str = "",
        entite_id: int | str | None = None,
        source: str = "",
        utilisateur_id: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> EntreeAudit:
        """Enregistre une action dans le journal d'audit.

        Args:
            action: Type d'action (ex: "recette.creee")
            entite_type: Type d'entité concernée
            entite_id: ID de l'entité
            source: Service source
            utilisateur_id: ID utilisateur (si disponible)
            details: Données complémentaires

        Returns:
            EntreeAudit créée
        """
        self._compteur += 1

        entree = EntreeAudit(
            id=self._compteur,
            timestamp=datetime.now(),
            action=action,
            source=source,
            utilisateur_id=utilisateur_id,
            entite_type=entite_type,
            entite_id=entite_id,
            details=details or {},
        )

        self._buffer.append(entree)

        # Persister en DB (async, best-effort)
        self._persister_en_db(entree)

        logger.debug(f"Audit: {action} sur {entite_type}#{entite_id} par {source}")
        return entree

    def consulter(
        self,
        entite_type: str | None = None,
        entite_id: int | str | None = None,
        action: str | None = None,
        source: str | None = None,
        depuis: datetime | None = None,
        jusqu_a: datetime | None = None,
        limite: int = 50,
        page: int = 1,
    ) -> ResultatRecherche:
        """Consulte le journal d'audit avec filtres.

        Args:
            entite_type: Filtrer par type d'entité
            entite_id: Filtrer par ID d'entité
            action: Filtrer par type d'action (pattern partiel supporté)
            source: Filtrer par service source
            depuis: Date de début
            jusqu_a: Date de fin
            limite: Nombre max de résultats par page
            page: Numéro de page (1-based)

        Returns:
            ResultatRecherche paginé
        """
        resultats = list(self._buffer)

        # Filtres
        if entite_type:
            resultats = [e for e in resultats if e.entite_type == entite_type]
        if entite_id is not None:
            resultats = [e for e in resultats if e.entite_id == entite_id]
        if action:
            resultats = [e for e in resultats if action in e.action]
        if source:
            resultats = [e for e in resultats if e.source == source]
        if depuis:
            resultats = [e for e in resultats if e.timestamp >= depuis]
        if jusqu_a:
            resultats = [e for e in resultats if e.timestamp <= jusqu_a]

        # Trier par date décroissante
        resultats.sort(key=lambda e: e.timestamp, reverse=True)

        # Pagination
        total = len(resultats)
        debut = (page - 1) * limite
        fin = debut + limite
        page_resultats = resultats[debut:fin]

        return ResultatRecherche(
            entrees=page_resultats,
            total=total,
            page=page,
            par_page=limite,
        )

    def statistiques(self) -> dict[str, Any]:
        """Retourne des statistiques sur le journal d'audit.

        Returns:
            Dict avec compteurs par action, entité, source
        """
        from collections import Counter

        entrees = list(self._buffer)

        actions = Counter(e.action for e in entrees)
        entites = Counter(e.entite_type for e in entrees)
        sources = Counter(e.source for e in entrees)

        return {
            "total_entrees": len(entrees),
            "par_action": dict(actions.most_common(20)),
            "par_entite": dict(entites.most_common(20)),
            "par_source": dict(sources.most_common(20)),
            "buffer_capacite": self._buffer.maxlen,
            "souscrit_bus": self._souscrit,
        }

    def vider(self) -> int:
        """Vide le buffer d'audit (pour maintenance).

        Returns:
            Nombre d'entrées supprimées
        """
        n = len(self._buffer)
        self._buffer.clear()
        logger.info(f"Buffer audit vidé ({n} entrées)")
        return n

    # ─── Persistance DB (best-effort) ───

    def _persister_en_db(self, entree: EntreeAudit) -> None:
        """Persiste une entrée d'audit en base (best-effort, non-bloquant)."""
        try:
            from src.core.db import obtenir_contexte_db

            with obtenir_contexte_db() as session:
                from sqlalchemy import text

                session.execute(
                    text("""
                        INSERT INTO journal_audit (timestamp, action, source, utilisateur_id,
                                                   entite_type, entite_id, details)
                        VALUES (:timestamp, :action, :source, :utilisateur_id,
                                :entite_type, :entite_id, :details::jsonb)
                    """),
                    {
                        "timestamp": entree.timestamp,
                        "action": entree.action,
                        "source": entree.source,
                        "utilisateur_id": entree.utilisateur_id,
                        "entite_type": entree.entite_type,
                        "entite_id": str(entree.entite_id) if entree.entite_id else None,
                        "details": str(entree.details),
                    },
                )
                session.commit()
        except Exception:
            # Best-effort: si la table n'existe pas encore, on ne crash pas
            pass


# ═══════════════════════════════════════════════════════════
# FACTORY
# ═══════════════════════════════════════════════════════════


@service_factory("audit", tags={"core", "audit", "transversal"})
def obtenir_service_audit() -> ServiceAudit:
    """Factory singleton pour le service d'audit trail."""
    service = ServiceAudit()
    service.souscrire_bus()
    return service


__all__ = [
    "ServiceAudit",
    "EntreeAudit",
    "ResultatRecherche",
    "obtenir_service_audit",
]
