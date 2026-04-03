"""Adaptateur OCR legacy pour conserver la compatibilite des routes existantes."""

from __future__ import annotations

import base64

from src.services.integrations.facture import obtenir_facture_ocr_service


class OCRService:
    """Facade legacy utilisee par les endpoints budget et jeux."""

    _content_types_acceptes = {"image/jpeg", "image/png", "image/webp"}
    _taille_max_octets = 10 * 1024 * 1024

    def valider_upload_image(
        self,
        content_type: str | None,
        contenu: bytes,
        formats_supportes: str = "JPEG, PNG, WebP",
    ) -> None:
        if not contenu:
            raise ValueError("Fichier image vide")

        if len(contenu) > self._taille_max_octets:
            raise ValueError("Image trop volumineuse (max 10 Mo)")

        if content_type and content_type.lower() not in self._content_types_acceptes:
            raise ValueError(f"Format non supporte. Formats acceptes: {formats_supportes}")

    def extraire_ticket(self, contenu: bytes) -> dict | None:
        image_base64 = base64.b64encode(contenu).decode("ascii")
        service_facture = obtenir_facture_ocr_service()
        resultat = service_facture.extraire_donnees_facture_sync(image_base64)

        if not resultat or not resultat.succes or not resultat.donnees:
            return None

        return resultat.donnees.model_dump()

    def formater_donnees_budget(self, resultat: dict) -> dict:
        return {
            "fournisseur": resultat.get("fournisseur"),
            "categorie": resultat.get("type_energie"),
            "montant": resultat.get("montant_ttc", 0),
            "date_debut": resultat.get("date_debut"),
            "date_fin": resultat.get("date_fin"),
            "confiance": resultat.get("confiance", 0),
        }

    def formater_donnees_jeux(self, resultat: dict) -> dict:
        return {
            "source": resultat.get("fournisseur", "ticket"),
            "montant": resultat.get("montant_ttc", 0),
            "reference": resultat.get("numero_facture", ""),
            "confiance": resultat.get("confiance", 0),
        }


def obtenir_ocr_service() -> OCRService:
    """Factory legacy exposee pour les routes existantes."""
    return OCRService()
