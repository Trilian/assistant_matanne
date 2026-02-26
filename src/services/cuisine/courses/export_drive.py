"""
Export Drive — Génération de listes pour La Fourche et Mon Petit Potager.

Exporte la liste de courses au format adapté pour chaque drive,
avec deep links et copie presse-papier.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from urllib.parse import quote_plus

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# TYPES
# ═══════════════════════════════════════════════════════════


@dataclass
class DriveConfig:
    """Configuration d'un service drive."""

    nom: str
    url_base: str
    url_recherche: str = ""  # Template pour recherche produit
    logo_emoji: str = "🛒"
    categories_fortes: list[str] = field(default_factory=list)
    notes: str = ""


@dataclass
class ArticleExport:
    """Article formaté pour export drive."""

    nom: str
    quantite: float
    unite: str
    url_recherche: str = ""
    categorie: str = ""


@dataclass
class ExportDrive:
    """Export complet pour un drive."""

    drive: DriveConfig
    articles: list[ArticleExport]
    texte_copie: str = ""  # Texte formaté pour copie presse-papier
    url_panier: str = ""  # URL vers le panier (si applicable)


# ═══════════════════════════════════════════════════════════
# CONFIGURATION DES DRIVES
# ═══════════════════════════════════════════════════════════

DRIVES: dict[str, DriveConfig] = {
    "la_fourche": DriveConfig(
        nom="La Fourche",
        url_base="https://www.lafourche.fr/",
        url_recherche="https://www.lafourche.fr/search?q={query}",
        logo_emoji="🌿",
        categories_fortes=["épicerie bio", "produits secs", "hygiène", "entretien", "vrac"],
        notes="Supermarché bio en ligne — adhésion annuelle ~60€",
    ),
    "mon_petit_potager": DriveConfig(
        nom="Mon Petit Potager",
        url_base="https://www.monpetitpotager.fr/",
        url_recherche="https://www.monpetitpotager.fr/recherche?q={query}",
        logo_emoji="🥕",
        categories_fortes=["légumes", "fruits", "herbes", "panier frais"],
        notes="Maraîcher local — livraison de paniers",
    ),
}


# ═══════════════════════════════════════════════════════════
# FONCTIONS
# ═══════════════════════════════════════════════════════════


def generer_url_recherche(drive_id: str, article: str) -> str:
    """Génère l'URL de recherche d'un article sur un drive."""
    drive = DRIVES.get(drive_id)
    if not drive or not drive.url_recherche:
        return ""

    return drive.url_recherche.format(query=quote_plus(article))


def exporter_pour_drive(
    articles: list[dict],
    drive_id: str = "la_fourche",
) -> ExportDrive:
    """
    Exporte une liste d'articles formatée pour un drive spécifique.

    Args:
        articles: Liste de dicts {nom, quantite, unite, categorie?}
        drive_id: Identifiant du drive (la_fourche, mon_petit_potager)

    Returns:
        ExportDrive prêt à copier ou ouvrir
    """
    drive = DRIVES.get(drive_id)
    if not drive:
        raise ValueError(f"Drive inconnu: {drive_id}. Disponibles: {list(DRIVES.keys())}")

    articles_export = []
    lignes_copie = [f"📋 Liste de courses — {drive.nom}\n"]

    for art in articles:
        nom = art.get("nom", "")
        qte = art.get("quantite", 1)
        unite = art.get("unite", "")
        categorie = art.get("categorie", "")

        url = generer_url_recherche(drive_id, nom)

        articles_export.append(
            ArticleExport(
                nom=nom,
                quantite=qte,
                unite=unite,
                url_recherche=url,
                categorie=categorie,
            )
        )

        ligne = f"  • {nom}"
        if qte and qte != 1:
            ligne += f" × {qte}"
        if unite:
            ligne += f" {unite}"
        lignes_copie.append(ligne)

    lignes_copie.append(f"\n🔗 {drive.url_base}")
    texte = "\n".join(lignes_copie)

    return ExportDrive(
        drive=drive,
        articles=articles_export,
        texte_copie=texte,
        url_panier=drive.url_base,
    )


def exporter_multi_drives(
    articles: list[dict],
    repartition: dict[str, list[dict]] | None = None,
) -> dict[str, ExportDrive]:
    """
    Exporte la liste répartie entre plusieurs drives.

    Args:
        articles: Liste complète (utilisée si pas de répartition)
        repartition: Dict drive_id → articles spécifiques

    Returns:
        Dict drive_id → ExportDrive
    """
    if repartition:
        return {
            drive_id: exporter_pour_drive(arts, drive_id)
            for drive_id, arts in repartition.items()
            if drive_id in DRIVES
        }

    # Si pas de répartition, tout va sur le drive par défaut
    return {"la_fourche": exporter_pour_drive(articles, "la_fourche")}


def generer_texte_partage(exports: dict[str, ExportDrive]) -> str:
    """Génère un texte combiné pour partage (WhatsApp, SMS, etc.)."""
    sections = []
    for _drive_id, export in exports.items():
        sections.append(export.texte_copie)

    return "\n\n---\n\n".join(sections)


def lister_drives_disponibles() -> list[DriveConfig]:
    """Retourne la liste des drives configurés."""
    return list(DRIVES.values())


__all__ = [
    "DriveConfig",
    "ArticleExport",
    "ExportDrive",
    "DRIVES",
    "generer_url_recherche",
    "exporter_pour_drive",
    "exporter_multi_drives",
    "generer_texte_partage",
    "lister_drives_disponibles",
]
