"""Service OCR mutualise pour tickets/factures (famille et jeux)."""

from __future__ import annotations

from typing import Any

from src.services.core.registry import service_factory
from src.services.integrations.multimodal import FactureExtraite, get_multimodal_service


class OCRService:
    """Encapsule la validation et l'extraction OCR des tickets."""

    MAX_TAILLE_OCTETS = 10 * 1024 * 1024

    def valider_upload_image(
        self,
        content_type: str | None,
        contenu: bytes,
        formats_autorises: str,
    ) -> None:
        """Valide le type MIME et la taille du fichier image."""
        if not content_type or not content_type.startswith("image/"):
            raise ValueError(f"Le fichier doit etre une image ({formats_autorises})")
        if len(contenu) > self.MAX_TAILLE_OCTETS:
            raise ValueError("Fichier trop volumineux (max 10 Mo)")

    def extraire_ticket(self, contenu: bytes) -> FactureExtraite | None:
        """Extrait les donnees OCR d'un ticket/facture via le service multimodal."""
        service = get_multimodal_service()
        return service.extraire_facture_sync(contenu)

    def formater_donnees_budget(self, resultat: FactureExtraite) -> dict[str, Any]:
        """Formate la sortie OCR pour l'API budget famille."""
        return {
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
        }

    def formater_donnees_jeux(self, resultat: FactureExtraite) -> dict[str, Any]:
        """Formate la sortie OCR pour l'API jeux."""
        return {
            "point_vente": resultat.magasin,
            "date_achat": resultat.date,
            "lignes": [
                {
                    "description": ligne.description,
                    "quantite": ligne.quantite,
                    "prix_unitaire": ligne.prix_unitaire,
                    "prix_total": ligne.prix_total,
                }
                for ligne in resultat.lignes
            ],
            "total": resultat.total,
            "mode_paiement": resultat.mode_paiement,
        }


@service_factory("ocr_service", tags={"utilitaires", "ia"})
def obtenir_ocr_service() -> OCRService:
    """Factory singleton OCRService."""
    return OCRService()



