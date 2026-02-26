"""
Configuration déclarative des pages de navigation.

Chaque section contient une liste de pages avec:
- key: Identifiant unique du module (utilisé pour le routage)
- path: Chemin d'import Python du module
- title: Titre affiché dans la navigation
- icon: Emoji affiché devant le titre

Pour ajouter une page: ajouter une entrée dans la section appropriée.
Pour ajouter une section: ajouter un nouveau dict dans PAGES.
"""

from __future__ import annotations

from typing import TypedDict


class PageConfig(TypedDict):
    """Configuration d'une page de navigation."""

    key: str
    path: str
    title: str
    icon: str


class SectionConfig(TypedDict):
    """Configuration d'une section de navigation."""

    name: str
    pages: list[PageConfig]


PAGES: list[SectionConfig] = [
    # ── Accueil ──
    {
        "name": "",
        "pages": [
            {"key": "accueil", "path": "src.modules.accueil", "title": "Accueil", "icon": "🏠"},
        ],
    },
    # ── Planning ──
    {
        "name": "📅 Planning",
        "pages": [
            {
                "key": "planning.cockpit",
                "path": "src.modules.planning.cockpit_familial",
                "title": "Cockpit Familial",
                "icon": "🎯",
            },
            {
                "key": "planning.calendrier",
                "path": "src.modules.planning.calendrier",
                "title": "Calendrier",
                "icon": "📅",
            },
            {
                "key": "planning.templates_ui",
                "path": "src.modules.planning.templates_ui",
                "title": "Templates",
                "icon": "📋",
            },
            {
                "key": "planning.timeline_ui",
                "path": "src.modules.planning.timeline_ui",
                "title": "Timeline",
                "icon": "📊",
            },
        ],
    },
    # ── Cuisine ──
    {
        "name": "🍳 Cuisine",
        "pages": [
            {
                "key": "cuisine.planificateur_repas",
                "path": "src.modules.cuisine.planificateur_repas",
                "title": "Planifier Repas",
                "icon": "🍽️",
            },
            {
                "key": "cuisine.batch_cooking_detaille",
                "path": "src.modules.cuisine.batch_cooking_detaille",
                "title": "Batch Cooking",
                "icon": "🍳",
            },
            {
                "key": "cuisine.courses",
                "path": "src.modules.cuisine.courses",
                "title": "Courses",
                "icon": "🛒",
            },
            {
                "key": "cuisine.recettes",
                "path": "src.modules.cuisine.recettes",
                "title": "Recettes",
                "icon": "📋",
            },
            {
                "key": "cuisine.inventaire",
                "path": "src.modules.cuisine.inventaire",
                "title": "Inventaire",
                "icon": "🥫",
            },
        ],
    },
    # ── Famille ──
    {
        "name": "👨\u200d👩\u200d👧\u200d👦 Famille",
        "pages": [
            {
                "key": "famille.hub",
                "path": "src.modules.famille.hub_famille",
                "title": "Hub Famille",
                "icon": "🏠",
            },
            {
                "key": "famille.jules",
                "path": "src.modules.famille.jules",
                "title": "Jules",
                "icon": "👶",
            },
            {
                "key": "famille.jules_planning",
                "path": "src.modules.famille.jules_planning",
                "title": "Planning Jules",
                "icon": "📅",
            },
            {
                "key": "famille.suivi_perso",
                "path": "src.modules.famille.suivi_perso",
                "title": "Mon Suivi",
                "icon": "💪",
            },
            {
                "key": "famille.weekend",
                "path": "src.modules.famille.weekend",
                "title": "Weekend",
                "icon": "🎉",
            },
            {
                "key": "famille.achats_famille",
                "path": "src.modules.famille.achats_famille",
                "title": "Achats",
                "icon": "🛍️",
            },
            {
                "key": "famille.activites",
                "path": "src.modules.famille.activites",
                "title": "Activités",
                "icon": "🎭",
            },
            {
                "key": "famille.routines",
                "path": "src.modules.famille.routines",
                "title": "Routines",
                "icon": "⏰",
            },
        ],
    },
    # ── Maison ──
    {
        "name": "🏠 Maison",
        "pages": [
            {
                "key": "maison.hub",
                "path": "src.modules.maison.hub",
                "title": "Hub Maison",
                "icon": "🏠",
            },
            {
                "key": "maison.jardin",
                "path": "src.modules.maison.jardin",
                "title": "Jardin",
                "icon": "🌱",
            },
            {
                "key": "maison.jardin_zones",
                "path": "src.modules.maison.jardin_zones",
                "title": "Zones Jardin",
                "icon": "🌿",
            },
            {
                "key": "maison.entretien",
                "path": "src.modules.maison.entretien",
                "title": "Entretien",
                "icon": "🏡",
            },
            {
                "key": "maison.charges",
                "path": "src.modules.maison.charges",
                "title": "Charges",
                "icon": "💡",
            },
            {
                "key": "maison.depenses",
                "path": "src.modules.maison.depenses",
                "title": "Dépenses",
                "icon": "💰",
            },
            {
                "key": "maison.eco_tips",
                "path": "src.modules.maison.eco_tips",
                "title": "Éco-Tips",
                "icon": "🌿",
            },
            {
                "key": "maison.energie",
                "path": "src.modules.maison.energie",
                "title": "Énergie",
                "icon": "⚡",
            },
            {
                "key": "maison.meubles",
                "path": "src.modules.maison.meubles",
                "title": "Meubles",
                "icon": "🪑",
            },
            {
                "key": "maison.projets",
                "path": "src.modules.maison.projets",
                "title": "Projets",
                "icon": "🏗️",
            },
        ],
    },
    # ── Jeux ──
    {
        "name": "🎲 Jeux",
        "pages": [
            {
                "key": "jeux.paris",
                "path": "src.modules.jeux.paris",
                "title": "Paris Sportifs",
                "icon": "⚽",
            },
            {
                "key": "jeux.loto",
                "path": "src.modules.jeux.loto",
                "title": "Loto",
                "icon": "🎰",
            },
        ],
    },
    # ── Outils ──
    {
        "name": "🔧 Outils",
        "pages": [
            {
                "key": "barcode",
                "path": "src.modules.utilitaires.barcode",
                "title": "Code-barres",
                "icon": "📱",
            },
            {
                "key": "scan_factures",
                "path": "src.modules.utilitaires.scan_factures",
                "title": "Scan Factures",
                "icon": "🧾",
            },
            {
                "key": "recherche_produits",
                "path": "src.modules.utilitaires.recherche_produits",
                "title": "Produits",
                "icon": "🔍",
            },
            {
                "key": "rapports",
                "path": "src.modules.utilitaires.rapports",
                "title": "Rapports",
                "icon": "📊",
            },
            {
                "key": "notifications_push",
                "path": "src.modules.utilitaires.notifications_push",
                "title": "Notifications",
                "icon": "🔔",
            },
            {
                "key": "chat_ia",
                "path": "src.modules.utilitaires.chat_ia",
                "title": "Chat IA",
                "icon": "💬",
            },
        ],
    },
    # ── Configuration ──
    {
        "name": "⚙️ Configuration",
        "pages": [
            {
                "key": "parametres",
                "path": "src.modules.parametres",
                "title": "Paramètres",
                "icon": "⚙️",
            },
            {
                "key": "design_system",
                "path": "src.modules.design_system",
                "title": "Design System",
                "icon": "🎨",
            },
        ],
    },
]
