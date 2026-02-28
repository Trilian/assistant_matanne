"""
Boîte à outils — Hub central pour tous les utilitaires.

Affiche une grille de cartes cliquables organisées par catégorie.
Chaque carte navigue vers la page utilitaire correspondante
(pages cachées de la sidebar, accessibles via ce hub).
"""

from __future__ import annotations

import streamlit as st

from src.core.state import GestionnaireEtat, rerun

# Note: chat global s'ouvre via session_state flag 'chat_global_visible'

# ═══════════════════════════════════════════════════════════
# CATÉGORIES D'OUTILS
# ═══════════════════════════════════════════════════════════

_CATEGORIES: list[dict] = [
    {
        "titre": "💬 Assistant",
        "outils": [
            {
                "key": "chat_ia",
                "icon": "💬",
                "nom": "Chat IA",
                "desc": "Assistant IA",
            }
        ],
    },
    {
        "titre": "🔍 Scan & Recherche",
        "outils": [
            {
                "key": "barcode",
                "icon": "📱",
                "nom": "Code-barres",
                "desc": "Scanner & lookup produits",
            },
            {
                "key": "scan_factures",
                "icon": "🧾",
                "nom": "Scan Factures",
                "desc": "OCR de factures",
            },
            {
                "key": "recherche_produits",
                "icon": "🔍",
                "nom": "Produits",
                "desc": "Recherche produits",
            },
            {"key": "qr_code_gen", "icon": "📱", "nom": "QR Codes", "desc": "Générer des QR codes"},
        ],
    },
    {
        "titre": "📦 Données & Rapports",
        "outils": [
            {"key": "rapports", "icon": "📊", "nom": "Rapports", "desc": "Rapports & analytics"},
            {
                "key": "export_global",
                "icon": "📤",
                "nom": "Export Global",
                "desc": "Exporter toutes les données",
            },
            {
                "key": "import_masse",
                "icon": "📥",
                "nom": "Import Masse",
                "desc": "Importer des données",
            },
            {
                "key": "notifications_push",
                "icon": "🔔",
                "nom": "Notifications",
                "desc": "Alertes & rappels",
            },
        ],
    },
    {
        "titre": "📝 Productivité",
        "outils": [
            {"key": "notes_memos", "icon": "📝", "nom": "Notes", "desc": "Notes & mémos rapides"},
            {"key": "journal_bord", "icon": "📓", "nom": "Journal", "desc": "Journal de bord"},
            {
                "key": "presse_papiers",
                "icon": "📋",
                "nom": "Presse-papiers",
                "desc": "Clipboard manager",
            },
            {"key": "liens_utiles", "icon": "🔗", "nom": "Favoris", "desc": "Liens & bookmarks"},
            {
                "key": "annuaire_contacts",
                "icon": "📇",
                "nom": "Contacts",
                "desc": "Annuaire contacts",
            },
            {
                "key": "compte_rebours",
                "icon": "⏳",
                "nom": "Compte à rebours",
                "desc": "Timers & countdowns",
            },
        ],
    },
    {
        "titre": "🔐 Sécurité & Maison",
        "outils": [
            {
                "key": "mots_de_passe",
                "icon": "🔐",
                "nom": "Mots de passe",
                "desc": "Gestionnaire sécurisé",
            },
            {"key": "meteo", "icon": "🌤️", "nom": "Météo", "desc": "Prévisions météo"},
            {
                "key": "suivi_energie",
                "icon": "⚡",
                "nom": "Suivi Énergie",
                "desc": "Consommation énergie",
            },
        ],
    },
]


# ═══════════════════════════════════════════════════════════
# UI
# ═══════════════════════════════════════════════════════════


def _naviguer(key: str) -> None:
    """Navigue vers un outil via switch_page natif."""
    GestionnaireEtat.naviguer_vers(key)
    rerun()


def app():
    """Point d'entrée Boîte à outils."""
    st.header("🧰 Boîte à outils")
    st.caption("Tous vos utilitaires au même endroit")

    for categorie in _CATEGORIES:
        st.subheader(categorie["titre"])

        outils = categorie["outils"]

        # Afficher les outils en rangées de 4 colonnes
        for row_start in range(0, len(outils), 4):
            row_outils = outils[row_start : row_start + 4]
            cols = st.columns(min(len(row_outils), 4))

            for i, outil in enumerate(row_outils):
                with cols[i]:
                    with st.container(border=True):
                        if st.button(
                            f"{outil['icon']}\n\n**{outil['nom']}**",
                            key=f"outil_{outil['key']}",
                            use_container_width=True,
                        ):
                            # Ouvrir le chat global (persistant) si demandé,
                            # sinon naviguer vers la page utilitaire correspondante.
                            if outil.get("key") == "chat_ia":
                                st.session_state["chat_global_visible"] = True
                                # ouvrir remet à zéro le compteur de non lus
                                st.session_state["chat_global_unread"] = 0
                                rerun()
                            else:
                                _naviguer(outil["key"])

                        # Badge de nouveaux messages pour l'outil Chat IA
                        if outil.get("key") == "chat_ia":
                            unread = st.session_state.get("chat_global_unread", 0)
                            if unread > 0:
                                st.markdown(
                                    f"<div class='chat-open-badge' title='{unread} nouveau(x)'>🔴 {unread}</div>",
                                    unsafe_allow_html=True,
                                )

                        st.caption(outil["desc"])
