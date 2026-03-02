"""
Configuration déclarative des pages de navigation.

Chaque section contient une liste de pages avec:
- key: Identifiant unique du module (utilisé pour le routage)
- path: Chemin d'import Python du module
- title: Titre affiché dans la navigation
- icon: Emoji affiché devant le titre
- hidden: (optionnel) True → page routable mais cachée de la sidebar
- parent: (optionnel) Clé du hub parent pour le bouton retour automatique

Pages hidden : accessibles via URL directe et st.switch_page() depuis les hubs.
Le masquage est purement CSS (injection dans navigation.py).

Pour ajouter une page: ajouter une entrée dans la section appropriée.
Pour ajouter une section: ajouter un nouveau dict dans PAGES.
"""

from __future__ import annotations

from typing import Required, TypedDict


class PageConfig(TypedDict, total=False):
    """Configuration d'une page de navigation.

    ``hidden`` masque la page de la sidebar tout en la gardant routable
    (URL directe + ``st.switch_page`` depuis les hubs).

    ``parent`` détermine le hub cible du bouton « ⬅️ Retour » automatique
    ajouté par ``navigation.py`` sur les pages cachées.
    """

    key: Required[str]
    path: Required[str]
    title: Required[str]
    icon: str
    hidden: bool
    parent: str


class SectionConfig(TypedDict):
    """Configuration d'une section de navigation."""

    name: str
    pages: list[PageConfig]


# ─────────────────────────────────────────────────────────
# Raccourcis pour lisibilité de la déclaration
# ─────────────────────────────────────────────────────────


def _h(key: str, path: str, title: str, icon: str, parent: str) -> PageConfig:
    """Crée une PageConfig cachée (hidden) avec parent."""
    return {
        "key": key,
        "path": path,
        "title": title,
        "icon": icon,
        "hidden": True,
        "parent": parent,
    }


def _v(key: str, path: str, title: str, icon: str) -> PageConfig:
    """Crée une PageConfig visible (raccourci lisibilité)."""
    return {"key": key, "path": path, "title": title, "icon": icon}


# ═════════════════════════════════════════════════════════════
# LISTE DÉCLARATIVE DES PAGES
# ═════════════════════════════════════════════════════════════
#
# Visibles dans la sidebar : ~15 pages (hubs + accès fréquents)
# Cachées (accessibles par bouton / URL) : ~59 pages
# Total inchangé : 74 pages — zéro fonctionnalité perdue
# ═════════════════════════════════════════════════════════════

PAGES: list[SectionConfig] = [
    # ── Accueil ──────────────────────────────────────────────
    {
        "name": "",
        "pages": [
            _v("accueil", "src.modules.accueil", "Accueil", "🏠"),
            _v(
                "cuisine_repas",
                "src.modules.cuisine.planificateur_repas",
                "Cuisine & Repas",
                "🍽️",
            ),
            # 'planning' entries removed (no root menu)
            # Cuisine-related pages are registered as hidden subpages of
            # the Planifier Repas hub so the sidebar shows a single entry
            # "Planifier Repas" while keeping recipes/courses/inventaire
            # accessible via URL or hub buttons.
            # 'boite_outils' moved later in the menu (after Jeux)
            # Cuisine subpages (hidden parents -> cuisine_repas)
            _h(
                "cuisine.recettes",
                "src.modules.cuisine.recettes",
                "Recettes",
                "📋",
                "cuisine_repas",
            ),
            _h(
                "cuisine.batch_cooking_detaille",
                "src.modules.cuisine.batch_cooking_detaille",
                "Batch Cooking",
                "🍳",
                "cuisine_repas",
            ),
            _h(
                "cuisine.courses",
                "src.modules.cuisine.courses",
                "Courses",
                "🛒",
                "cuisine_repas",
            ),
            _h(
                "cuisine.inventaire",
                "src.modules.cuisine.inventaire",
                "Inventaire",
                "🥫",
                "cuisine_repas",
            ),
            # Utility helpers used by cuisine features
            _h(
                "convertisseur_unites",
                "src.modules.utilitaires.convertisseur_unites",
                "Convertisseur",
                "⚖️",
                "cuisine.recettes",
            ),
            _h(
                "calculatrice_portions",
                "src.modules.utilitaires.calculatrice_portions",
                "Portions",
                "🔢",
                "cuisine.recettes",
            ),
            _h(
                "substitutions",
                "src.modules.utilitaires.substitutions",
                "Substitutions",
                "🔄",
                "cuisine.recettes",
            ),
            _h(
                "cout_repas",
                "src.modules.utilitaires.cout_repas",
                "Coût Repas",
                "💰",
                "cuisine_repas",
            ),
            _h(
                "saisonnalite",
                "src.modules.utilitaires.saisonnalite",
                "Saisons",
                "🥕",
                "cuisine.recettes",
            ),
            _h(
                "minuteur",
                "src.modules.utilitaires.minuteur",
                "Minuteur",
                "⏱️",
                "cuisine_repas",
            ),
            _h(
                "chat_ia",
                "src.modules.utilitaires.chat_ia",
                "Chat IA",
                "💬",
                "boite_outils",
            ),
            # Hidden utility pages (registered here to keep sidebar uncluttered)
            _h("barcode", "src.modules.utilitaires.barcode", "Code-barres", "📱", "boite_outils"),
            _h(
                "scan_factures",
                "src.modules.utilitaires.scan_factures",
                "Scan Factures",
                "🧾",
                "boite_outils",
            ),
            _h(
                "recherche_produits",
                "src.modules.utilitaires.recherche_produits",
                "Produits",
                "🔍",
                "boite_outils",
            ),
            _h("rapports", "src.modules.utilitaires.rapports", "Rapports", "📊", "boite_outils"),
            _h(
                "notifications_push",
                "src.modules.utilitaires.notifications_push",
                "Notifications",
                "🔔",
                "boite_outils",
            ),
            _h(
                "export_global",
                "src.modules.utilitaires.export_global",
                "Export Global",
                "📤",
                "boite_outils",
            ),
            _h(
                "import_masse",
                "src.modules.utilitaires.import_masse",
                "Import Masse",
                "📥",
                "boite_outils",
            ),
            _h("notes_memos", "src.modules.utilitaires.notes_memos", "Notes", "📝", "boite_outils"),
            _h(
                "journal_bord",
                "src.modules.utilitaires.journal_bord",
                "Journal",
                "📓",
                "boite_outils",
            ),
            _h(
                "presse_papiers",
                "src.modules.utilitaires.presse_papiers",
                "Presse-papiers",
                "📋",
                "boite_outils",
            ),
            _h(
                "liens_utiles",
                "src.modules.utilitaires.liens_utiles",
                "Favoris",
                "🔗",
                "boite_outils",
            ),
            _h(
                "annuaire_contacts",
                "src.modules.utilitaires.annuaire_contacts",
                "Contacts",
                "📇",
                "boite_outils",
            ),
            _h(
                "compte_rebours",
                "src.modules.utilitaires.compte_rebours",
                "Compte à rebours",
                "⏳",
                "boite_outils",
            ),
            _h(
                "mots_de_passe",
                "src.modules.utilitaires.mots_de_passe",
                "Mots de passe",
                "🔐",
                "boite_outils",
            ),
            _h(
                "qr_code_gen",
                "src.modules.utilitaires.qr_code_gen",
                "QR Codes",
                "📱",
                "boite_outils",
            ),
        ],
    },
    # ── Planning (top-level visible page) ─────────────────────────────
    {
        "name": "",
        "pages": [
            _v("planning", "src.modules.planning.cockpit_familial", "Planning", "📅"),
        ],
    },
    # Planning and separate Cuisine sections removed — their pages are now
    # registered under the Accueil section so that "Planifier Repas" stays
    # the single visible entry for meal planning. Hidden subpages remain
    # available via their URL (keys unchanged).
    # ── Famille ──────────────────────────────────────────────
    {
        "name": "",
        "pages": [
            _v("famille", "src.modules.famille.hub_famille", "Famille", "👨‍👩‍👧‍👦"),
            _h("famille.jules", "src.modules.famille.jules", "Jules", "👶", "famille"),
            _h(
                "famille.jules_planning",
                "src.modules.famille.jules_planning",
                "Planning Jules",
                "📅",
                "famille",
            ),
            _h(
                "famille.suivi_perso",
                "src.modules.famille.suivi_perso",
                "Mon Suivi",
                "💪",
                "famille",
            ),
            _h("famille.weekend", "src.modules.famille.weekend", "Weekend", "🎉", "famille"),
            _h(
                "famille.achats_famille",
                "src.modules.famille.achats_famille",
                "Achats",
                "🛍️",
                "famille",
            ),
            _h(
                "famille.activites",
                "src.modules.famille.activites",
                "Activités",
                "🎭",
                "famille",
            ),
            _h("famille.routines", "src.modules.famille.routines", "Routines", "⏰", "famille"),
            _h(
                "famille.carnet_sante",
                "src.modules.famille.carnet_sante",
                "Carnet Santé",
                "🏥",
                "famille",
            ),
            _h(
                "famille.calendrier",
                "src.modules.famille.calendrier_famille",
                "Calendrier",
                "📅",
                "famille",
            ),
            _h(
                "famille.anniversaires",
                "src.modules.famille.anniversaires",
                "Anniversaires",
                "🎂",
                "famille",
            ),
            _h(
                "famille.contacts",
                "src.modules.famille.contacts_famille",
                "Contacts",
                "📞",
                "famille",
            ),
            _h(
                "famille.soiree_couple",
                "src.modules.famille.soiree_couple",
                "Soirée Couple",
                "❤️",
                "famille",
            ),
            _h("famille.album", "src.modules.famille.album", "Album Souvenirs", "📸", "famille"),
            _h(
                "famille.sante_globale",
                "src.modules.famille.sante_globale",
                "Santé Globale",
                "💪",
                "famille",
            ),
            _h(
                "famille.journal",
                "src.modules.famille.journal_familial",
                "Journal IA",
                "📝",
                "famille",
            ),
            _h(
                "famille.documents",
                "src.modules.famille.documents_famille",
                "Documents",
                "📁",
                "famille",
            ),
            _h("famille.voyage", "src.modules.famille.voyage", "Mode Voyage", "✈️", "famille"),
            _h(
                "famille.routines_pdf",
                "src.modules.famille.routines_imprimables",
                "Routines PDF",
                "🖨️",
                "famille",
            ),
        ],
    },
    # ── Maison ───────────────────────────────────────────────
    {
        "name": "",
        "pages": [
            _v("maison", "src.modules.maison.hub", "Maison", "🏠"),
            _h("maison.jardin", "src.modules.maison.jardin", "Jardin", "🌱", "maison"),
            _h(
                "maison.jardin_zones",
                "src.modules.maison.jardin_zones",
                "Zones Jardin",
                "🌿",
                "maison",
            ),
            _h("maison.entretien", "src.modules.maison.entretien", "Entretien", "🏡", "maison"),
            _h("maison.charges", "src.modules.maison.charges", "Charges", "💡", "maison"),
            _h("maison.depenses", "src.modules.maison.depenses", "Dépenses", "💰", "maison"),
            _h("maison.eco_tips", "src.modules.maison.eco_tips", "Éco-Tips", "🌿", "maison"),
            _h("maison.energie", "src.modules.maison.energie", "Énergie", "⚡", "maison"),
            _h("maison.meubles", "src.modules.maison.meubles", "Meubles", "🪑", "maison"),
            _h("maison.projets", "src.modules.maison.projets", "Projets", "🏗️", "maison"),
            _h(
                "maison.visualisation",
                "src.modules.maison.visualisation",
                "Plan Maison",
                "🏘️",
                "maison",
            ),
            # Ex-section « Outils Maison »
            _h("meteo", "src.modules.utilitaires.meteo", "Météo", "🌤️", "maison"),
            _h(
                "suivi_energie",
                "src.modules.utilitaires.suivi_energie",
                "Suivi Énergie",
                "⚡",
                "maison",
            ),
        ],
    },
    # ── Jeux ─────────────────────────────────────────────────
    {
        "name": "",
        "pages": [
            _v("jeux.paris", "src.modules.jeux.paris", "Paris Sportifs", "⚽"),
            _v("jeux.loto", "src.modules.jeux.loto", "Loto", "🎰"),
            _v("jeux.bilan", "src.modules.jeux.bilan", "Bilan Global", "📊"),
            _h(
                "jeux.euromillions",
                "src.modules.jeux.euromillions",
                "Euromillions",
                "⭐",
                "jeux.loto",
            ),
            _h(
                "jeux.comparatif_roi",
                "src.modules.jeux.comparatif_roi",
                "Comparatif ROI",
                "📈",
                "jeux.bilan",
            ),
            _h(
                "jeux.alertes", "src.modules.jeux.alertes", "Alertes Pronostics", "🔔", "jeux.bilan"
            ),
            _h("jeux.biais", "src.modules.jeux.biais", "Biais Cognitifs", "🧠", "jeux.bilan"),
            _h("jeux.calendrier", "src.modules.jeux.calendrier", "Calendrier", "📅", "jeux.bilan"),
            _h("jeux.educatif", "src.modules.jeux.educatif", "Module Éducatif", "🎓", "jeux.bilan"),
        ],
    },
    # ── Boîte à outils (visible after Jeux) ───────────────────────────
    {
        "name": "",
        "pages": [
            _v("boite_outils", "src.modules.utilitaires.boite_outils", "Boîte à outils", "🧰"),
        ],
    },
    # NOTE: 'Outils' section removed — `Boîte à outils` moved to root sidebar.
    # ── Configuration ────────────────────────────────────────
    {
        "name": "",
        "pages": [
            _v("parametres", "src.modules.parametres", "Paramètres", "⚙️"),
            _h("design_system", "src.modules.design_system", "Design System", "🎨", "parametres"),
        ],
    },
]
