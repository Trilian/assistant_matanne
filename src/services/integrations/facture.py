"""
Service OCR Factures - Extraction automatique depuis photos de factures.

Supporte:
- EDF (électricité)
- Engie (gaz)
- Veolia / Eau de Paris (eau)

Utilise Mistral AI Vision pour l'extraction de données structurées.
"""

import logging
import re
from datetime import date

from pydantic import BaseModel, Field

from src.core.ai import ClientIA, obtenir_client_ia
from src.services.core.base import BaseAIService

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# MODÈLES DE DONNÉES
# ═══════════════════════════════════════════════════════════


class DonneesFacture(BaseModel):
    """Données extraites d'une facture."""

    fournisseur: str = Field(description="Nom du fournisseur (EDF, Engie, Veolia...)")
    type_energie: str = Field(description="Type: electricite, gaz, eau")

    # Montants
    montant_ttc: float = Field(description="Montant total TTC en euros")
    montant_ht: float | None = Field(default=None, description="Montant HT si disponible")

    # Consommation
    consommation: float | None = Field(default=None, description="Consommation (kWh, m³)")
    unite_consommation: str = Field(default="", description="Unité: kWh ou m³")

    # Période
    date_debut: date | None = Field(default=None, description="Début période facturée")
    date_fin: date | None = Field(default=None, description="Fin période facturée")
    mois_facturation: int | None = Field(default=None, description="Mois principal (1-12)")
    annee_facturation: int | None = Field(default=None, description="Année")

    # Références
    numero_facture: str = Field(default="", description="Numéro de facture")
    numero_client: str = Field(default="", description="Numéro client/contrat")

    # Détails tarif
    prix_kwh: float | None = Field(default=None, description="Prix unitaire kWh")
    abonnement: float | None = Field(default=None, description="Montant abonnement")

    # Confiance
    confiance: float = Field(default=0.0, description="Score de confiance 0-1")
    erreurs: list[str] = Field(default_factory=list, description="Erreurs d'extraction")


class ResultatOCR(BaseModel):
    """Résultat complet de l'OCR."""

    succes: bool = True
    donnees: DonneesFacture | None = None
    texte_brut: str = ""
    message: str = ""


# ═══════════════════════════════════════════════════════════
# SERVICE OCR
# ═══════════════════════════════════════════════════════════


class FactureOCRService(BaseAIService):
    """Service d'extraction OCR de factures via Mistral Vision."""

    def __init__(self):
        super().__init__(
            client=obtenir_client_ia(),
            cache_prefix="facture_ocr",
            default_ttl=3600,
            service_name="facture_ocr",
        )

    async def extraire_donnees_facture(self, image_base64: str) -> ResultatOCR:
        """
        Extrait les données d'une facture depuis une image base64.

        Args:
            image_base64: Image encodée en base64 (sans le préfixe data:image)

        Returns:
            ResultatOCR avec les données extraites
        """
        prompt = """Analyse cette facture d'énergie (électricité, gaz ou eau) et extrait les informations suivantes au format JSON:

{
    "fournisseur": "nom du fournisseur (EDF, Engie, Veolia, TotalEnergies...)",
    "type_energie": "electricite ou gaz ou eau",
    "montant_ttc": montant total TTC en euros (nombre),
    "montant_ht": montant HT si visible (nombre ou null),
    "consommation": consommation en kWh ou m³ (nombre ou null),
    "unite_consommation": "kWh" ou "m³",
    "date_debut": "YYYY-MM-DD" début période ou null,
    "date_fin": "YYYY-MM-DD" fin période ou null,
    "mois_facturation": mois principal 1-12,
    "annee_facturation": année YYYY,
    "numero_facture": "numéro de facture",
    "numero_client": "numéro client/contrat",
    "prix_kwh": prix unitaire si visible (nombre ou null),
    "abonnement": montant abonnement si visible (nombre ou null)
}

IMPORTANT:
- Extrais UNIQUEMENT les informations visibles sur la facture
- Les montants doivent être des nombres (pas de symbole €)
- Si une information n'est pas visible, mets null
- Pour les dates, utilise le format YYYY-MM-DD

Réponds UNIQUEMENT avec le JSON, sans texte autour."""

        try:
            # Appel vision avec image
            response = await self.client.chat_with_vision(
                prompt=prompt, image_base64=image_base64, max_tokens=1000
            )

            # Parser le JSON
            donnees = self._parser_reponse(response)

            return ResultatOCR(
                succes=True, donnees=donnees, texte_brut=response, message="Extraction réussie"
            )

        except Exception as e:
            logger.error(f"Erreur OCR facture: {e}")
            return ResultatOCR(succes=False, message=f"Erreur d'extraction: {str(e)}")

    def _parser_reponse(self, reponse: str) -> DonneesFacture:
        """Parse la réponse JSON de l'IA."""
        import json

        # Nettoyer la réponse (enlever markdown si présent)
        reponse = reponse.strip()
        if reponse.startswith("```"):
            reponse = re.sub(r"```json?\n?", "", reponse)
            reponse = re.sub(r"```$", "", reponse)

        try:
            data = json.loads(reponse)
        except json.JSONDecodeError as e:
            logger.error(f"Erreur parsing JSON: {e}")
            return DonneesFacture(
                fournisseur="Inconnu",
                type_energie="autre",
                montant_ttc=0,
                erreurs=[f"Erreur parsing: {str(e)}"],
            )

        # Convertir les dates
        for date_field in ["date_debut", "date_fin"]:
            if data.get(date_field):
                try:
                    data[date_field] = date.fromisoformat(data[date_field])
                except (ValueError, TypeError):
                    data[date_field] = None

        # Valider et calculer confiance
        erreurs = []
        confiance = 1.0

        if not data.get("montant_ttc"):
            erreurs.append("Montant TTC non trouvé")
            confiance -= 0.3

        if not data.get("fournisseur") or data["fournisseur"] == "Inconnu":
            erreurs.append("Fournisseur non identifié")
            confiance -= 0.2

        if not data.get("consommation"):
            erreurs.append("Consommation non trouvée")
            confiance -= 0.1

        data["confiance"] = max(0, confiance)
        data["erreurs"] = erreurs

        return DonneesFacture(**data)

    def extraire_donnees_facture_sync(self, image_base64: str) -> ResultatOCR:
        """Version synchrone de l'extraction."""
        from src.services.core.base.async_utils import sync_wrapper

        _sync = sync_wrapper(self.extraire_donnees_facture)
        return _sync(image_base64)


# ═══════════════════════════════════════════════════════════
# PATTERNS DE DÉTECTION MANUELLE (fallback)
# ═══════════════════════════════════════════════════════════

PATTERNS_FOURNISSEURS = {
    "edf": {
        "regex": r"(EDF|Électricité de France)",
        "type": "electricite",
    },
    "engie": {
        "regex": r"(ENGIE|Gaz de France|GDF)",
        "type": "gaz",
    },
    "totalenergies": {
        "regex": r"(TotalEnergies|Total Direct Energie)",
        "type": "electricite",
    },
    "veolia": {
        "regex": r"(Veolia|Eau de Paris|Suez)",
        "type": "eau",
    },
}

PATTERNS_MONTANTS = {
    "montant_ttc": r"Total\s*(?:à payer|TTC)[^\d]*(\d+[,\.]\d{2})\s*€?",
    "consommation_kwh": r"(\d+(?:\s*\d+)?)\s*kWh",
    "consommation_m3": r"(\d+(?:[,\.]\d+)?)\s*m[³3]",
}


def detecter_fournisseur(texte: str) -> tuple[str, str]:
    """Détecte le fournisseur depuis le texte OCR."""
    for nom, info in PATTERNS_FOURNISSEURS.items():
        if re.search(info["regex"], texte, re.IGNORECASE):
            return nom.upper(), info["type"]

    return "Inconnu", "autre"


def extraire_montant(texte: str, pattern: str) -> float | None:
    """Extrait un montant depuis le texte."""
    match = re.search(pattern, texte, re.IGNORECASE)
    if match:
        valeur = match.group(1).replace(",", ".").replace(" ", "")
        try:
            return float(valeur)
        except (ValueError, TypeError):
            pass
    return None


# ═══════════════════════════════════════════════════════════
# FACTORY
# ═══════════════════════════════════════════════════════════


_facture_ocr_instance: FactureOCRService | None = None


def obtenir_service_ocr_facture() -> FactureOCRService:
    """Factory singleton pour le service OCR."""
    global _facture_ocr_instance
    if _facture_ocr_instance is None:
        _facture_ocr_instance = FactureOCRService()
    return _facture_ocr_instance


def get_facture_ocr_service() -> FactureOCRService:
    """Factory pour le service OCR (alias anglais)."""
    return obtenir_service_ocr_facture()
