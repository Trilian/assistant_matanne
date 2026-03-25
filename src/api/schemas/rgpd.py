"""
Schémas Pydantic pour les endpoints RGPD.

Export de données personnelles, suppression de compte, résumé des données.
"""

from datetime import datetime

from pydantic import BaseModel, Field


class ResumeDonnees(BaseModel):
    """Résumé du nombre d'éléments stockés par catégorie."""

    categorie: str = Field(description="Nom de la catégorie de données")
    nombre: int = Field(description="Nombre d'éléments dans cette catégorie")


class ExportRGPDResponse(BaseModel):
    """Réponse lors d'un export de données RGPD."""

    message: str = Field(description="Message de confirmation")
    format: str = Field(default="zip", description="Format du fichier exporté")
    taille_octets: int = Field(description="Taille du fichier en octets")


class ResumeDonneesResponse(BaseModel):
    """Résumé complet des données utilisateur."""

    user_id: str = Field(description="ID de l'utilisateur")
    categories: list[ResumeDonnees] = Field(description="Données par catégorie")
    total_elements: int = Field(description="Nombre total d'éléments")


class SuppressionCompteRequest(BaseModel):
    """Requête de suppression de compte."""

    confirmation: str = Field(
        description="Doit être exactement 'SUPPRIMER MON COMPTE' pour confirmer"
    )
    motif: str | None = Field(default=None, description="Motif optionnel de suppression")


class SuppressionCompteResponse(BaseModel):
    """Réponse de suppression de compte."""

    message: str = Field(description="Confirmation de la suppression")
    deleted_at: datetime = Field(description="Date de suppression")
    elements_supprimes: int = Field(description="Nombre total d'éléments supprimés")
