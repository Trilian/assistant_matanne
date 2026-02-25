"""
Module Meubles - Wishlist d'achats par pièce avec budget.

Fonctionnalités:
- Wishlist de meubles/achats souhaités par pièce
- Suivi du statut (souhaité → acheté)
- Budget estimé et max par pièce
- Vue par pièce avec résumé financier
"""

import logging
from decimal import Decimal

import streamlit as st

from src.core.db import obtenir_contexte_db
from src.core.monitoring.rerun_profiler import profiler_rerun
from src.modules._framework import error_boundary
from src.ui.keys import KeyNamespace

try:
    from src.core.models import Meuble
except ImportError:
    from sqlalchemy import Boolean, Date, Numeric, String
    from sqlalchemy.orm import Mapped, mapped_column

    from src.core.models.base import Base

    class Meuble(Base):
        """Modèle Meuble (wishlist achats)."""

        __tablename__ = "meubles_wishlist"

        id: Mapped[int] = mapped_column(primary_key=True)
        nom: Mapped[str] = mapped_column(String(200))
        piece: Mapped[str] = mapped_column(String(50))
        description: Mapped[str | None] = mapped_column(String(500), nullable=True)
        priorite: Mapped[str] = mapped_column(String(20), default="normale")
        statut: Mapped[str] = mapped_column(String(20), default="souhaite")
        prix_estime: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
        prix_max: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
        magasin: Mapped[str | None] = mapped_column(String(200), nullable=True)
        url: Mapped[str | None] = mapped_column(String(500), nullable=True)
        dimensions: Mapped[str | None] = mapped_column(String(100), nullable=True)
        actif: Mapped[bool] = mapped_column(Boolean, default=True)


__all__ = [
    "app",
    "PIECES_LABELS",
    "STATUTS_LABELS",
    "PRIORITES_LABELS",
    "get_all_meubles",
    "get_meuble_by_id",
    "create_meuble",
    "update_meuble",
    "delete_meuble",
    "get_budget_resume",
    "afficher_formulaire",
    "afficher_meuble_card",
    "afficher_budget_summary",
    "afficher_vue_par_piece",
    "afficher_onglet_wishlist",
    "afficher_onglet_ajouter",
    "afficher_onglet_budget",
]

_keys = KeyNamespace("meubles")
logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════
# CONSTANTES
# ═══════════════════════════════════════════════════════════

PIECES_LABELS = {
    "salon": "🛋️ Salon",
    "cuisine": "🍳 Cuisine",
    "chambre_parentale": "🛏️ Chambre parentale",
    "chambre_enfant": "👶 Chambre enfant",
    "bureau": "💻 Bureau",
    "salle_de_bain": "🚿 Salle de bain",
    "entree": "🚪 Entrée",
    "buanderie": "🧺 Buanderie",
    "garage": "🔧 Garage",
    "terrasse": "🌿 Terrasse",
}

STATUTS_LABELS = {
    "souhaite": "💭 Souhaité",
    "recherche": "🔍 En recherche",
    "trouve": "📌 Trouvé",
    "commande": "📦 Commandé",
    "achete": "✅ Acheté",
    "annule": "❌ Annulé",
}

PRIORITES_LABELS = {
    "urgent": "🔴 Urgent",
    "haute": "🟠 Haute",
    "normale": "🟢 Normale",
    "basse": "🔵 Basse",
    "plus_tard": "⚪ Plus tard",
}


# ═══════════════════════════════════════════════════════════
# CRUD FONCTIONS
# ═══════════════════════════════════════════════════════════


def get_all_meubles(filtre_statut: str | None = None, filtre_piece: str | None = None) -> list:
    """Récupère tous les meubles avec filtres optionnels.

    Args:
        filtre_statut: Filtrer par statut.
        filtre_piece: Filtrer par pièce.

    Returns:
        Liste d'objets Meuble.
    """
    with obtenir_contexte_db() as db:
        query = db.query(Meuble)
        if filtre_statut:
            query = query.filter(Meuble.statut == filtre_statut)
        if filtre_piece:
            query = query.filter(Meuble.piece == filtre_piece)
        return query.order_by(Meuble.id).all()


def get_meuble_by_id(meuble_id: int):
    """Récupère un meuble par son ID."""
    with obtenir_contexte_db() as db:
        return db.query(Meuble).filter(Meuble.id == meuble_id).first()


def create_meuble(data: dict) -> None:
    """Crée un nouveau meuble."""
    with obtenir_contexte_db() as db:
        meuble = Meuble(**data)
        db.add(meuble)
        db.commit()
        db.refresh(meuble)


def update_meuble(meuble_id: int, data: dict):
    """Met à jour un meuble existant."""
    with obtenir_contexte_db() as db:
        meuble = db.query(Meuble).filter(Meuble.id == meuble_id).first()
        if meuble is None:
            return None
        for key, value in data.items():
            setattr(meuble, key, value)
        db.commit()
        db.refresh(meuble)
        return meuble


def delete_meuble(meuble_id: int) -> bool:
    """Supprime un meuble."""
    with obtenir_contexte_db() as db:
        meuble = db.query(Meuble).filter(Meuble.id == meuble_id).first()
        if meuble is None:
            return False
        db.delete(meuble)
        db.commit()
        return True


def get_budget_resume() -> dict:
    """Calcule le résumé budget des meubles souhaités.

    Returns:
        Dict avec nb_articles, total_estime, total_max, par_piece.
    """
    with obtenir_contexte_db() as db:
        meubles = db.query(Meuble).filter(Meuble.statut != "achete").all()

    if not meubles:
        return {
            "nb_articles": 0,
            "total_estime": 0,
            "total_max": 0,
            "par_piece": {},
        }

    total_estime = 0.0
    total_max = 0.0
    par_piece: dict = {}

    for m in meubles:
        prix_e = float(m.prix_estime) if m.prix_estime else 0.0
        prix_m = float(m.prix_max) if m.prix_max else 0.0
        total_estime += prix_e
        total_max += prix_m

        piece = getattr(m, "piece", "autre")
        if piece not in par_piece:
            par_piece[piece] = {"count": 0, "total_estime": 0.0, "total_max": 0.0}
        par_piece[piece]["count"] += 1
        par_piece[piece]["total_estime"] += prix_e
        par_piece[piece]["total_max"] += prix_m

    return {
        "nb_articles": len(meubles),
        "total_estime": total_estime,
        "total_max": total_max,
        "par_piece": par_piece,
    }


# ═══════════════════════════════════════════════════════════
# UI COMPONENTS
# ═══════════════════════════════════════════════════════════


def afficher_formulaire(meuble=None) -> None:
    """Affiche le formulaire de création/édition d'un meuble."""
    with st.form(key=_keys("form_meuble")):
        nom = st.text_input("Nom *", value=getattr(meuble, "nom", ""))

        col1, col2 = st.columns(2)
        with col1:
            pieces_list = list(PIECES_LABELS.keys())
            idx_piece = 0
            if meuble and hasattr(meuble, "piece") and meuble.piece in pieces_list:
                idx_piece = pieces_list.index(meuble.piece)
            piece = st.selectbox(
                "Pièce",
                pieces_list,
                format_func=lambda x: PIECES_LABELS[x],
                index=idx_piece,
            )
        with col2:
            priorites_list = list(PRIORITES_LABELS.keys())
            idx_prio = priorites_list.index("normale")
            if meuble and hasattr(meuble, "priorite") and meuble.priorite in priorites_list:
                idx_prio = priorites_list.index(meuble.priorite)
            priorite = st.selectbox(
                "Priorité",
                priorites_list,
                format_func=lambda x: PRIORITES_LABELS[x],
                index=idx_prio,
            )

        description = st.text_area("Description", value=getattr(meuble, "description", "") or "")
        prix_estime = st.number_input(
            "Prix estimé (€)",
            min_value=0.0,
            value=float(getattr(meuble, "prix_estime", 0) or 0),
        )
        prix_max = st.number_input(
            "Prix max (€)",
            min_value=0.0,
            value=float(getattr(meuble, "prix_max", 0) or 0),
        )
        magasin = st.text_input("Magasin", value=getattr(meuble, "magasin", "") or "")
        url = st.text_input("URL", value=getattr(meuble, "url", "") or "")
        dimensions = st.text_input("Dimensions", value=getattr(meuble, "dimensions", "") or "")

        submitted = st.form_submit_button("💾 Enregistrer", use_container_width=True)

    if submitted and nom:
        data = {
            "nom": nom,
            "piece": piece,
            "priorite": priorite,
            "description": description or None,
            "prix_estime": Decimal(str(prix_estime)) if prix_estime > 0 else None,
            "prix_max": Decimal(str(prix_max)) if prix_max > 0 else None,
            "magasin": magasin or None,
            "url": url or None,
            "dimensions": dimensions or None,
            "statut": "souhaite",
        }
        if meuble:
            update_meuble(meuble.id, data)
            st.success("✅ Meuble mis à jour !")
        else:
            create_meuble(data)
            st.success("✅ Meuble ajouté !")
        st.rerun()


def afficher_meuble_card(meuble) -> None:
    """Affiche une carte pour un meuble."""
    piece_label = PIECES_LABELS.get(getattr(meuble, "piece", ""), "")
    statut_label = STATUTS_LABELS.get(getattr(meuble, "statut", ""), "")
    priorite_label = PRIORITES_LABELS.get(getattr(meuble, "priorite", ""), "")

    with st.container(border=True):
        col1, col2, col3 = st.columns([3, 1, 1])
        with col1:
            st.markdown(f"**{meuble.nom}**")
            desc = getattr(meuble, "description", None)
            if desc:
                if len(desc) > 100:
                    desc = desc[:100] + "…"
                st.caption(desc)
            st.caption(f"{piece_label} | {statut_label} | {priorite_label}")
        with col2:
            prix = getattr(meuble, "prix_estime", None)
            if prix:
                st.metric("Prix estimé", f"{float(prix):.0f}€")
        with col3:
            magasin = getattr(meuble, "magasin", None)
            if magasin:
                st.caption(f"🏪 {magasin}")

        col_edit, col_del = st.columns(2)
        with col_edit:
            if st.button("✏️ Modifier", key=f"edit_m_{meuble.id}"):
                st.session_state[_keys("edit_id")] = meuble.id
                st.rerun()
        with col_del:
            if st.button("🗑️ Supprimer", key=f"del_m_{meuble.id}"):
                delete_meuble(meuble.id)
                st.rerun()


def afficher_budget_summary() -> None:
    """Affiche le résumé budget."""
    st.subheader("💰 Résumé budget")
    resume = get_budget_resume()

    cols = st.columns(3)
    with cols[0]:
        st.metric("Articles", resume["nb_articles"])
    with cols[1]:
        st.metric("Total estimé", f"{resume['total_estime']:.0f}€")
    with cols[2]:
        st.metric("Budget max", f"{resume['total_max']:.0f}€")

    if resume["par_piece"]:
        st.markdown("**Par pièce:**")
        for piece, data in resume["par_piece"].items():
            label = PIECES_LABELS.get(piece, piece)
            st.caption(f"{label}: {data['count']} articles — ~{data['total_estime']:.0f}€")


def afficher_vue_par_piece() -> None:
    """Affiche la vue groupée par pièce."""
    meubles = get_all_meubles()
    if not meubles:
        st.info("Aucun meuble enregistré.")
        return

    # Grouper par pièce
    par_piece: dict = {}
    for m in meubles:
        piece = getattr(m, "piece", "autre")
        par_piece.setdefault(piece, []).append(m)

    for piece, items in sorted(par_piece.items()):
        label = PIECES_LABELS.get(piece, piece)
        with st.expander(f"{label} ({len(items)})"):
            for item in items:
                afficher_meuble_card(item)


def afficher_onglet_wishlist() -> None:
    """Affiche l'onglet wishlist avec filtres."""
    col1, col2 = st.columns(2)
    with col1:
        filtre_statut = st.selectbox(
            "Statut",
            [""] + list(STATUTS_LABELS.keys()),
            format_func=lambda x: STATUTS_LABELS.get(x, "Tous") if x else "Tous",
        )
    with col2:
        filtre_piece = st.selectbox(
            "Pièce",
            [""] + list(PIECES_LABELS.keys()),
            format_func=lambda x: PIECES_LABELS.get(x, "Toutes") if x else "Toutes",
        )

    meubles = get_all_meubles(
        filtre_statut=filtre_statut or None,
        filtre_piece=filtre_piece or None,
    )

    if not meubles:
        st.info("Aucun meuble trouvé avec ces critères.")
        return

    st.caption(f"{len(meubles)} meuble(s) trouvé(s)")
    for m in meubles:
        afficher_meuble_card(m)


def afficher_onglet_ajouter() -> None:
    """Affiche l'onglet ajout."""
    st.subheader("➕ Ajouter un meuble")
    afficher_formulaire(None)


def afficher_onglet_budget() -> None:
    """Affiche l'onglet budget."""
    afficher_budget_summary()
    st.divider()
    afficher_vue_par_piece()


# ═══════════════════════════════════════════════════════════
# APP
# ═══════════════════════════════════════════════════════════


@profiler_rerun("meubles")
def app():
    """Point d'entrée du module Meubles."""
    with error_boundary(titre="Erreur module Meubles"):
        st.title("🛋️ Meubles & Achats")
        st.caption("Gérez vos achats de meubles par pièce avec suivi de budget.")

        # Mode édition
        edit_id = st.session_state.get(_keys("edit_id"))
        if edit_id:
            meuble = get_meuble_by_id(edit_id)
            if meuble:
                st.subheader(f"✏️ Modifier : {meuble.nom}")
                afficher_formulaire(meuble)
                if st.button("← Annuler"):
                    del st.session_state[_keys("edit_id")]
                    st.rerun()
                return
            else:
                del st.session_state[_keys("edit_id")]

        # Onglets
        TAB_LABELS = ["📋 Wishlist", "➕ Ajouter", "💰 Budget"]
        tab1, tab2, tab3 = st.tabs(TAB_LABELS)

        with tab1:
            afficher_onglet_wishlist()

        with tab2:
            afficher_onglet_ajouter()

        with tab3:
            afficher_onglet_budget()
