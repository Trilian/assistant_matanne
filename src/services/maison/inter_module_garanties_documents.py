"""
Service inter-modules : Garanties → Documents.

Phase 4.2 : lier une facture ou un document de garantie à un équipement
maison afin de retrouver rapidement la preuve d'achat depuis la fiche objet.
"""

from __future__ import annotations

import logging
from datetime import date
from typing import Any

from dateutil.relativedelta import relativedelta
from sqlalchemy.orm import Session

from src.core.decorators import avec_gestion_erreurs, avec_session_db
from src.services.core.registry import service_factory

logger = logging.getLogger(__name__)


class GarantiesDocumentsInteractionService:
    """Bridge équipements sous garantie → documents associés."""

    @staticmethod
    def _calculer_jours_restants_garantie(objet: Any) -> int | None:
        """Retourne le nombre de jours restants de garantie pour un objet."""
        if getattr(objet, "date_achat", None) is None or getattr(objet, "duree_garantie_mois", None) is None:
            return None

        try:
            mois_garantie = int(objet.duree_garantie_mois)
        except (TypeError, ValueError):
            return None

        fin_garantie = objet.date_achat + relativedelta(months=mois_garantie)
        return (fin_garantie - date.today()).days

    @avec_gestion_erreurs(default_return={})
    @avec_session_db
    def lier_document_garantie(
        self,
        objet_id: int,
        document_id: int,
        db: Session | None = None,
    ) -> dict[str, Any]:
        """Associe un document/facture à un équipement maison via ses tags."""
        from src.core.models import DocumentFamille
        from src.core.models.temps_entretien import ObjetMaison

        if db is None:
            return {"ok": False, "message": "Session DB indisponible"}

        objet = db.query(ObjetMaison).filter(ObjetMaison.id == objet_id).first()
        if objet is None:
            return {"ok": False, "message": f"Objet maison {objet_id} introuvable"}

        document = db.query(DocumentFamille).filter(DocumentFamille.id == document_id).first()
        if document is None:
            return {"ok": False, "message": f"Document {document_id} introuvable"}

        tags = list(document.tags or [])
        tags_a_ajouter = [
            "garantie",
            f"equipement:{objet.id}",
            f"piece:{objet.piece_id}",
        ]
        if objet.categorie:
            tags_a_ajouter.append(f"categorie:{objet.categorie}")

        document.tags = list(dict.fromkeys(tags + tags_a_ajouter))

        note_liaison = f"Équipement lié : #{objet.id} — {objet.nom}"
        notes_existantes = (document.notes or "").strip()
        if note_liaison not in notes_existantes:
            document.notes = (
                f"{notes_existantes}\n{note_liaison}".strip()
                if notes_existantes
                else note_liaison
            )

        if not document.membre_famille:
            document.membre_famille = "Famille"

        db.commit()
        db.refresh(document)

        jours_restants = self._calculer_jours_restants_garantie(objet)
        resultat = {
            "ok": True,
            "document": {
                "id": document.id,
                "titre": document.titre,
                "tags": document.tags or [],
            },
            "objet": {
                "id": objet.id,
                "nom": objet.nom,
                "categorie": objet.categorie,
                "sous_garantie": objet.sous_garantie,
                "jours_restants_garantie": jours_restants,
            },
            "message": f"Document #{document.id} lié à l'équipement {objet.nom}",
        }
        logger.info(
            "✅ Garanties→Documents objet=%s document=%s sous_garantie=%s",
            objet.id,
            document.id,
            objet.sous_garantie,
        )
        return resultat

    @avec_gestion_erreurs(default_return={})
    @avec_session_db
    def obtenir_documents_garantie_pour_objet(
        self,
        objet_id: int,
        db: Session | None = None,
    ) -> dict[str, Any]:
        """Retourne les documents déjà liés à un équipement donné."""
        from src.core.models import DocumentFamille
        from src.core.models.temps_entretien import ObjetMaison

        if db is None:
            return {"ok": False, "message": "Session DB indisponible"}

        objet = db.query(ObjetMaison).filter(ObjetMaison.id == objet_id).first()
        if objet is None:
            return {"ok": False, "message": f"Objet maison {objet_id} introuvable"}

        marqueur = f"equipement:{objet.id}"
        documents = [
            document
            for document in db.query(DocumentFamille).filter(DocumentFamille.actif.is_(True)).all()
            if marqueur in (document.tags or [])
        ]

        return {
            "ok": True,
            "objet": {
                "id": objet.id,
                "nom": objet.nom,
                "sous_garantie": objet.sous_garantie,
                "jours_restants_garantie": self._calculer_jours_restants_garantie(objet),
            },
            "documents": [
                {
                    "id": document.id,
                    "titre": document.titre,
                    "categorie": document.categorie,
                    "fichier_nom": document.fichier_nom,
                    "fichier_url": document.fichier_url,
                    "date_document": document.date_document.isoformat() if document.date_document else None,
                    "tags": document.tags or [],
                }
                for document in documents
            ],
            "nb_documents": len(documents),
            "message": f"{len(documents)} document(s) de garantie lié(s)",
        }


@service_factory(
    "garanties_documents_interaction",
    tags={"maison", "garanties", "documents", "phase4"},
)
def obtenir_service_garanties_documents_interaction() -> GarantiesDocumentsInteractionService:
    """Factory pour le bridge Garanties → Documents."""
    return GarantiesDocumentsInteractionService()
