"""
Module Meubles - Inventaire et gestion du mobilier.

Fonctionnalités:
- Inventaire de tous les meubles par pièce
- Suivi de l'état et de l'ancienneté
- Liste de souhaits meubles
- Estimation valeur d'assurance
- Historique achats et garanties
"""

import logging
from datetime import date, datetime

import streamlit as st

from src.core.monitoring.rerun_profiler import profiler_rerun
from src.modules._framework import error_boundary
from src.ui.keys import KeyNamespace
from src.ui.state.url import tabs_with_url

__all__ = ["app"]

_keys = KeyNamespace("meubles")
logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════
# CONSTANTES
# ═══════════════════════════════════════════════════════════

PIECES = [
    "Salon",
    "Chambre parentale",
    "Chambre enfant",
    "Cuisine",
    "Salle de bain",
    "Entrée",
    "Bureau",
    "Garage",
    "Buanderie",
    "Terrasse/Balcon",
]

ETATS = ["Neuf", "Bon", "Correct", "Usé", "À remplacer"]

CATEGORIES_MEUBLES = [
    "Canapé/Fauteuil",
    "Table",
    "Chaise",
    "Lit/Matelas",
    "Armoire/Commode",
    "Bureau/Étagère",
    "Meuble TV",
    "Rangement",
    "Décoration",
    "Électroménager",
    "Autre",
]


@profiler_rerun("meubles")
def app():
    """Point d'entrée du module Meubles."""
    st.title("🛋️ Inventaire Meubles")
    st.caption("Gérez l'inventaire de votre mobilier, garanties et valeur d'assurance.")

    # Init données
    if _keys("meubles") not in st.session_state:
        st.session_state[_keys("meubles")] = []
    if _keys("souhaits") not in st.session_state:
        st.session_state[_keys("souhaits")] = []

    TAB_LABELS = [
        "📦 Inventaire",
        "➕ Ajouter",
        "⭐ Liste de souhaits",
        "💰 Valeur assurance",
    ]
    tabs_with_url(TAB_LABELS, param="tab")
    tab1, tab2, tab3, tab4 = st.tabs(TAB_LABELS)

    with tab1:
        with error_boundary(titre="Erreur inventaire meubles"):
            _onglet_inventaire()

    with tab2:
        with error_boundary(titre="Erreur ajout meuble"):
            _onglet_ajouter()

    with tab3:
        with error_boundary(titre="Erreur souhaits"):
            _onglet_souhaits()

    with tab4:
        with error_boundary(titre="Erreur valeur assurance"):
            _onglet_assurance()


def _onglet_inventaire():
    """Liste des meubles par pièce."""
    meubles = st.session_state[_keys("meubles")]

    if not meubles:
        st.info("Aucun meuble répertorié. Ajoutez-en dans l'onglet '➕ Ajouter'.")
        return

    # Filtre par pièce
    pieces_presentes = sorted(set(m["piece"] for m in meubles))
    filtre_piece = st.selectbox(
        "Filtrer par pièce",
        ["Toutes"] + pieces_presentes,
        key=_keys("filtre_piece"),
    )

    meubles_filtres = meubles
    if filtre_piece != "Toutes":
        meubles_filtres = [m for m in meubles if m["piece"] == filtre_piece]

    st.markdown(f"**{len(meubles_filtres)} meuble(s)**")

    for i, meuble in enumerate(meubles_filtres):
        with st.container(border=True):
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.markdown(f"**{meuble['nom']}**")
                st.caption(
                    f"📍 {meuble['piece']} | "
                    f"📁 {meuble['categorie']} | "
                    f"🏷️ {meuble['etat']}"
                )
                if meuble.get("date_achat"):
                    st.caption(f"📅 Acheté le {meuble['date_achat']}")
                if meuble.get("garantie_fin"):
                    fin = date.fromisoformat(meuble["garantie_fin"])
                    if fin >= date.today():
                        st.caption(f"✅ Garantie jusqu'au {meuble['garantie_fin']}")
                    else:
                        st.caption("⚠️ Garantie expirée")

            with col2:
                if meuble.get("prix"):
                    st.metric("Prix", f"{meuble['prix']}€")

            with col3:
                if st.button("🗑️", key=_keys(f"del_{i}")):
                    st.session_state[_keys("meubles")].remove(meuble)
                    st.rerun()


def _onglet_ajouter():
    """Formulaire d'ajout de meuble."""
    st.subheader("Ajouter un meuble")

    with st.form(key=_keys("form_meuble")):
        nom = st.text_input("Nom *", placeholder="ex: Canapé IKEA Söderhamn")

        col1, col2 = st.columns(2)
        with col1:
            piece = st.selectbox("Pièce", PIECES, key=_keys("piece"))
        with col2:
            categorie = st.selectbox("Catégorie", CATEGORIES_MEUBLES, key=_keys("categorie"))

        col3, col4 = st.columns(2)
        with col3:
            etat = st.selectbox("État", ETATS, index=1, key=_keys("etat"))
        with col4:
            prix = st.number_input("Prix d'achat (€)", min_value=0.0, step=10.0, key=_keys("prix"))

        col5, col6 = st.columns(2)
        with col5:
            date_achat = st.date_input("Date d'achat", value=None, key=_keys("date_achat"))
        with col6:
            garantie_fin = st.date_input("Fin de garantie", value=None, key=_keys("garantie"))

        marque = st.text_input("Marque/Magasin", placeholder="ex: IKEA, Maisons du Monde...", key=_keys("marque"))
        notes = st.text_input("Notes", key=_keys("notes"))

        submitted = st.form_submit_button("💾 Ajouter le meuble", use_container_width=True)

    if submitted and nom:
        meuble = {
            "nom": nom,
            "piece": piece,
            "categorie": categorie,
            "etat": etat,
            "prix": prix if prix > 0 else None,
            "date_achat": date_achat.isoformat() if date_achat else None,
            "garantie_fin": garantie_fin.isoformat() if garantie_fin else None,
            "marque": marque or None,
            "notes": notes or None,
            "ajoute_le": datetime.now().isoformat(),
        }
        st.session_state[_keys("meubles")].append(meuble)
        st.success(f"✅ **{nom}** ajouté dans {piece} !")
    elif submitted:
        st.warning("Le nom est obligatoire.")


def _onglet_souhaits():
    """Liste de souhaits pour futurs achats."""
    st.subheader("⭐ Liste de souhaits")
    souhaits = st.session_state[_keys("souhaits")]

    # Formulaire rapide
    with st.form(key=_keys("form_souhait")):
        col1, col2, col3 = st.columns([3, 1, 1])
        with col1:
            nom_souhait = st.text_input("Meuble souhaité", placeholder="ex: Table basse relevable")
        with col2:
            budget_souhait = st.number_input("Budget max (€)", min_value=0, step=50, key=_keys("budget_souhait"))
        with col3:
            priorite_souhait = st.selectbox("Priorité", ["haute", "moyenne", "basse"], index=1, key=_keys("prio_souhait"))
        submitted = st.form_submit_button("➕ Ajouter", use_container_width=True)

    if submitted and nom_souhait:
        st.session_state[_keys("souhaits")].append({
            "nom": nom_souhait,
            "budget": budget_souhait if budget_souhait > 0 else None,
            "priorite": priorite_souhait,
            "ajoute_le": datetime.now().isoformat(),
        })
        st.rerun()

    # Affichage
    if not souhaits:
        st.info("Aucun souhait pour l'instant.")
        return

    for i, souhait in enumerate(souhaits):
        with st.container(border=True):
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.markdown(f"**{souhait['nom']}**")
            with col2:
                if souhait.get("budget"):
                    st.caption(f"Budget: {souhait['budget']}€")
            with col3:
                if st.button("✅ Acheté", key=_keys(f"acheté_{i}")):
                    st.session_state[_keys("souhaits")].remove(souhait)
                    st.rerun()


def _onglet_assurance():
    """Calcul de la valeur totale pour l'assurance."""
    st.subheader("💰 Valeur d'assurance")
    meubles = st.session_state[_keys("meubles")]

    if not meubles:
        st.info("Ajoutez des meubles avec leur prix pour estimer la valeur d'assurance.")
        return

    meubles_avec_prix = [m for m in meubles if m.get("prix")]
    total = sum(m["prix"] for m in meubles_avec_prix)
    nb_sans_prix = len(meubles) - len(meubles_avec_prix)

    # Métriques
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Valeur totale", f"{total:,.0f}€")
    with col2:
        st.metric("Meubles valorisés", f"{len(meubles_avec_prix)}/{len(meubles)}")
    with col3:
        if len(meubles_avec_prix) > 0:
            moyenne = total / len(meubles_avec_prix)
            st.metric("Valeur moyenne", f"{moyenne:,.0f}€")

    if nb_sans_prix > 0:
        st.warning(f"⚠️ {nb_sans_prix} meuble(s) sans prix renseigné.")

    # Détail par pièce
    st.markdown("#### Répartition par pièce")
    pieces_valeur = {}
    for m in meubles_avec_prix:
        pieces_valeur.setdefault(m["piece"], 0)
        pieces_valeur[m["piece"]] += m["prix"]

    if pieces_valeur:
        try:
            import plotly.express as px

            fig = px.pie(
                values=list(pieces_valeur.values()),
                names=list(pieces_valeur.keys()),
                title="Valeur par pièce",
            )
            st.plotly_chart(fig, use_container_width=True)
        except ImportError:
            for piece, valeur in sorted(pieces_valeur.items(), key=lambda x: -x[1]):
                st.markdown(f"- **{piece}**: {valeur:,.0f}€")
