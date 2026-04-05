"""Schémas Pydantic et constantes pour le bot Telegram."""

from __future__ import annotations

from pydantic import BaseModel, Field


COMMANDES_TELEGRAM: tuple[tuple[str, str], ...] = (
    ("/planning", "Afficher le planning repas de la semaine"),
    ("/courses", "Afficher la liste de courses avec actions rapides"),
    ("/courses_live", "Ouvrir la liste interactive avec boutons inline"),
    ("/inventaire", "Voir le frigo avec alertes de péremption"),
    ("/recette [nom]", "Trouver une recette rapide et ses ingrédients"),
    ("/batch", "Résumé du batch cooking en cours ou planifié"),
    ("/ajout [article]", "Ajouter un article à la liste de courses"),
    ("/ajouter_course [article]", "Ajouter un article à la liste active"),
    ("/acheter [article]", "Raccourci direct pour ajouter un article à la liste active"),
    ("/repas [midi|soir]", "Voir le repas du jour et répondre au mini-sondage"),
    ("/jules", "Résumé Jules: âge et jalons du moment"),
    ("/maison", "Tâches maison du jour"),
    ("/jardin", "Tâches jardin et récoltes à venir"),
    ("/weekend", "Suggestions et activités du prochain weekend"),
    ("/energie", "KPIs énergie du mois / de l'année"),
    ("/rappels", "Voir tous les rappels groupés"),
    ("/timer [Xmin]", "Lancer un minuteur Telegram"),
    ("/note [texte]", "Créer une note rapide"),
    ("/budget", "Résumé budget du mois en cours"),
    ("/projection", "Projection budgetaire rapide de fin de mois"),
    ("/recap", "Récapitulatif rapide de la journée"),
    ("/rapport", "Résumé hebdomadaire de la famille"),
    ("/photo", "Recevoir l'aide pour analyser une photo (frigo, plante, pièce, document)"),
    ("/meteo", "Météo du jour et impact sur les activités"),
    ("/menu", "Ouvrir le menu principal Telegram"),
    ("/aide", "Lister toutes les commandes disponibles"),
)


class EnvoyerPlanningTelegramRequest(BaseModel):
    """Payload pour l'envoi manuel d'un planning via Telegram."""

    planning_id: int
    contenu: str | None = None


class EnvoyerCoursesTelegramRequest(BaseModel):
    """Payload pour l'envoi manuel d'une liste de courses via Telegram."""

    liste_id: int
    nom_liste: str | None = None


class EnvoyerCoursesMagasinRequest(BaseModel):
    """Payload pour l'envoi d'une sous-liste de courses par magasin via Telegram."""

    liste_id: int
    magasin: str = Field(..., min_length=1, max_length=50, description="Magasin cible (bio_coop, grand_frais, etc.)")
    nom_liste: str | None = None


LIBELLES_MAGASINS: dict[str, str] = {
    "bio_coop": "🥬 Bio Coop",
    "grand_frais": "🧀 Grand Frais",
    "carrefour_drive": "🛒 Carrefour Drive",
}
