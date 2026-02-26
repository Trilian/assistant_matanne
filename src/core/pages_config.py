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
            {
                "key": "famille.carnet_sante",
                "path": "src.modules.famille.carnet_sante",
                "title": "Carnet Santé",
                "icon": "🏥",
            },
            {
                "key": "famille.calendrier",
                "path": "src.modules.famille.calendrier_famille",
                "title": "Calendrier",
                "icon": "📅",
            },
            {
                "key": "famille.anniversaires",
                "path": "src.modules.famille.anniversaires",
                "title": "Anniversaires",
                "icon": "🎂",
            },
            {
                "key": "famille.contacts",
                "path": "src.modules.famille.contacts_famille",
                "title": "Contacts",
                "icon": "📞",
            },
            {
                "key": "famille.soiree_couple",
                "path": "src.modules.famille.soiree_couple",
                "title": "Soirée Couple",
                "icon": "❤️",
            },
            {
                "key": "famille.album",
                "path": "src.modules.famille.album",
                "title": "Album Souvenirs",
                "icon": "📸",
            },
            {
                "key": "famille.sante_globale",
                "path": "src.modules.famille.sante_globale",
                "title": "Santé Globale",
                "icon": "💪",
            },
            {
                "key": "famille.journal",
                "path": "src.modules.famille.journal_familial",
                "title": "Journal IA",
                "icon": "📝",
            },
            {
                "key": "famille.documents",
                "path": "src.modules.famille.documents_famille",
                "title": "Documents",
                "icon": "📁",
            },
            {
                "key": "famille.voyage",
                "path": "src.modules.famille.voyage",
                "title": "Mode Voyage",
                "icon": "✈️",
            },
            {
                "key": "famille.routines_pdf",
                "path": "src.modules.famille.routines_imprimables",
                "title": "Routines PDF",
                "icon": "🖨️",
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
            {
                "key": "jeux.euromillions",
                "path": "src.modules.jeux.euromillions",
                "title": "Euromillions",
                "icon": "⭐",
            },
            {
                "key": "jeux.bilan",
                "path": "src.modules.jeux.bilan",
                "title": "Bilan Global",
                "icon": "📊",
            },
            {
                "key": "jeux.comparatif_roi",
                "path": "src.modules.jeux.comparatif_roi",
                "title": "Comparatif ROI",
                "icon": "📈",
            },
            {
                "key": "jeux.alertes",
                "path": "src.modules.jeux.alertes",
                "title": "Alertes Pronostics",
                "icon": "🔔",
            },
            {
                "key": "jeux.biais",
                "path": "src.modules.jeux.biais",
                "title": "Biais Cognitifs",
                "icon": "🧠",
            },
            {
                "key": "jeux.calendrier",
                "path": "src.modules.jeux.calendrier",
                "title": "Calendrier",
                "icon": "📅",
            },
            {
                "key": "jeux.educatif",
                "path": "src.modules.jeux.educatif",
                "title": "Module Éducatif",
                "icon": "🎓",
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
    # ── Données ──
    {
        "name": "📦 Données",
        "pages": [
            {
                "key": "export_global",
                "path": "src.modules.utilitaires.export_global",
                "title": "Export Global",
                "icon": "📤",
            },
            {
                "key": "import_masse",
                "path": "src.modules.utilitaires.import_masse",
                "title": "Import Masse",
                "icon": "📥",
            },
        ],
    },
    # ── Outils Cuisine ──
    {
        "name": "🍳 Cuisine+",
        "pages": [
            {
                "key": "convertisseur_unites",
                "path": "src.modules.utilitaires.convertisseur_unites",
                "title": "Convertisseur",
                "icon": "⚖️",
            },
            {
                "key": "calculatrice_portions",
                "path": "src.modules.utilitaires.calculatrice_portions",
                "title": "Portions",
                "icon": "🔢",
            },
            {
                "key": "substitutions",
                "path": "src.modules.utilitaires.substitutions",
                "title": "Substitutions",
                "icon": "🔄",
            },
            {
                "key": "cout_repas",
                "path": "src.modules.utilitaires.cout_repas",
                "title": "Coût Repas",
                "icon": "💰",
            },
            {
                "key": "saisonnalite",
                "path": "src.modules.utilitaires.saisonnalite",
                "title": "Saisons",
                "icon": "🥕",
            },
            {
                "key": "minuteur",
                "path": "src.modules.utilitaires.minuteur",
                "title": "Minuteur",
                "icon": "⏱️",
            },
        ],
    },
    # ── Productivité ──
    {
        "name": "📝 Productivité",
        "pages": [
            {
                "key": "notes_memos",
                "path": "src.modules.utilitaires.notes_memos",
                "title": "Notes",
                "icon": "📝",
            },
            {
                "key": "journal_bord",
                "path": "src.modules.utilitaires.journal_bord",
                "title": "Journal",
                "icon": "📓",
            },
            {
                "key": "presse_papiers",
                "path": "src.modules.utilitaires.presse_papiers",
                "title": "Presse-papiers",
                "icon": "📋",
            },
            {
                "key": "liens_utiles",
                "path": "src.modules.utilitaires.liens_utiles",
                "title": "Favoris",
                "icon": "🔗",
            },
            {
                "key": "annuaire_contacts",
                "path": "src.modules.utilitaires.annuaire_contacts",
                "title": "Contacts",
                "icon": "📇",
            },
            {
                "key": "compte_rebours",
                "path": "src.modules.utilitaires.compte_rebours",
                "title": "Compte à rebours",
                "icon": "⏳",
            },
        ],
    },
    # ── Outils Maison ──
    {
        "name": "🏠 Outils Maison",
        "pages": [
            {
                "key": "meteo",
                "path": "src.modules.utilitaires.meteo",
                "title": "Météo",
                "icon": "🌤️",
            },
            {
                "key": "suivi_energie",
                "path": "src.modules.utilitaires.suivi_energie",
                "title": "Énergie",
                "icon": "⚡",
            },
            {
                "key": "mots_de_passe",
                "path": "src.modules.utilitaires.mots_de_passe",
                "title": "Mots de passe",
                "icon": "🔐",
            },
            {
                "key": "qr_code_gen",
                "path": "src.modules.utilitaires.qr_code_gen",
                "title": "QR Codes",
                "icon": "📱",
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
