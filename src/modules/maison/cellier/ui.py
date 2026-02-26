"""Composants UI pour le module Cellier."""

from datetime import date

import streamlit as st

from src.core.state import rerun
from src.ui.fragments import ui_fragment
from src.ui.keys import KeyNamespace

from .constants import CATEGORIES_LABELS, UNITES
from .crud import (
    ajuster_quantite,
    create_article,
    delete_article,
    get_alertes_peremption,
    get_alertes_stock,
    get_all_articles,
    get_stats_cellier,
    update_article,
)

_keys = KeyNamespace("cellier")


def afficher_formulaire_article(article=None) -> None:
    """Formulaire de création/édition d'un article."""
    with st.form(key=_keys("form_article")):
        nom = st.text_input("Nom *", value=getattr(article, "nom", ""))

        col1, col2 = st.columns(2)
        with col1:
            categories_list = list(CATEGORIES_LABELS.keys())
            idx_cat = 0
            if article and hasattr(article, "categorie") and article.categorie in categories_list:
                idx_cat = categories_list.index(article.categorie)
            categorie = st.selectbox(
                "Catégorie *",
                categories_list,
                format_func=lambda x: CATEGORIES_LABELS[x],
                index=idx_cat,
            )
        with col2:
            marque = st.text_input("Marque", value=getattr(article, "marque", "") or "")

        col3, col4, col5 = st.columns(3)
        with col3:
            quantite = st.number_input(
                "Quantité",
                min_value=0,
                value=int(getattr(article, "quantite", 1)),
            )
        with col4:
            idx_unite = 0
            if article and hasattr(article, "unite") and article.unite in UNITES:
                idx_unite = UNITES.index(article.unite)
            unite = st.selectbox("Unité", UNITES, index=idx_unite)
        with col5:
            seuil_alerte = st.number_input(
                "Seuil alerte",
                min_value=0,
                value=int(getattr(article, "seuil_alerte", 1)),
            )

        st.markdown("**📅 Dates**")
        col6, col7 = st.columns(2)
        with col6:
            dlc = st.date_input(
                "DLC (Date Limite Consommation)",
                value=getattr(article, "dlc", None),
            )
        with col7:
            dluo = st.date_input(
                "DLUO (Utilisation Optimale)",
                value=getattr(article, "dluo", None),
            )

        emplacement = st.text_input(
            "Emplacement (étagère, congélateur...)",
            value=getattr(article, "emplacement", "") or "",
        )

        prix_unitaire = st.number_input(
            "Prix unitaire (€)",
            min_value=0.0,
            value=float(getattr(article, "prix_unitaire", 0) or 0),
            step=0.10,
        )

        notes = st.text_area("Notes", value=getattr(article, "notes", "") or "")

        submitted = st.form_submit_button("💾 Enregistrer", use_container_width=True)

    if submitted and nom:
        from decimal import Decimal

        data = {
            "nom": nom,
            "categorie": categorie,
            "marque": marque or None,
            "quantite": quantite,
            "unite": unite,
            "seuil_alerte": seuil_alerte,
            "dlc": dlc if dlc else None,
            "dluo": dluo if dluo else None,
            "emplacement": emplacement or None,
            "prix_unitaire": Decimal(str(prix_unitaire)) if prix_unitaire > 0 else None,
            "notes": notes or None,
        }
        if article:
            update_article(article.id, data)
            st.success("✅ Article mis à jour !")
        else:
            create_article(data)
            st.success("✅ Article ajouté !")
        rerun()


def _afficher_article_card(article) -> None:
    """Affiche une carte pour un article du cellier."""
    cat_label = CATEGORIES_LABELS.get(getattr(article, "categorie", ""), "")

    with st.container(border=True):
        col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
        with col1:
            st.markdown(f"**{article.nom}**")
            marque = getattr(article, "marque", None)
            empl = getattr(article, "emplacement", None)
            st.caption(
                f"{cat_label}"
                + (f" — {marque}" if marque else "")
                + (f" | 📍 {empl}" if empl else "")
            )
        with col2:
            qte = getattr(article, "quantite", 0)
            seuil = getattr(article, "seuil_alerte", 0)
            couleur = "🔴" if qte <= seuil else "🟢"
            st.metric("Stock", f"{couleur} {qte} {article.unite}")
        with col3:
            dlc = getattr(article, "dlc", None)
            if dlc:
                jours = (dlc - date.today()).days
                ic = "🔴" if jours < 7 else "🟡" if jours < 30 else "🟢"
                st.caption(f"{ic} DLC: {dlc:%d/%m/%Y}")
        with col4:
            c1, c2 = st.columns(2)
            with c1:
                if st.button("➕", key=_keys(f"plus_{article.id}")):
                    ajuster_quantite(article.id, 1)
                    rerun()
            with c2:
                if st.button("➖", key=_keys(f"minus_{article.id}")):
                    ajuster_quantite(article.id, -1)
                    rerun()

        col_edit, col_del = st.columns(2)
        with col_edit:
            if st.button("✏️", key=_keys(f"edit_{article.id}")):
                st.session_state[_keys("edit_id")] = article.id
                rerun()
        with col_del:
            if st.button("🗑️", key=_keys(f"del_{article.id}")):
                delete_article(article.id)
                rerun()


@ui_fragment
def afficher_onglet_dashboard() -> None:
    """Onglet dashboard cellier."""
    stats = get_stats_cellier()
    if not stats:
        st.info("Cellier vide — commencez par ajouter des articles.")
        return

    cols = st.columns(4)
    with cols[0]:
        st.metric("Articles", stats.get("total_articles", 0))
    with cols[1]:
        st.metric("Catégories", stats.get("nb_categories", 0))
    with cols[2]:
        st.metric("Alertes DLC", stats.get("alertes_dlc", 0))
    with cols[3]:
        st.metric("Stock bas", stats.get("alertes_stock", 0))

    par_cat = stats.get("par_categorie", {})
    if par_cat:
        st.markdown("**Par catégorie :**")
        for cat, count in sorted(par_cat.items(), key=lambda x: -x[1]):
            label = CATEGORIES_LABELS.get(cat, cat)
            st.caption(f"{label}: {count} article(s)")


@ui_fragment
def afficher_onglet_inventaire() -> None:
    """Onglet liste des articles."""
    filtre_categorie = st.selectbox(
        "Catégorie",
        [""] + list(CATEGORIES_LABELS.keys()),
        format_func=lambda x: CATEGORIES_LABELS.get(x, "Toutes") if x else "Toutes",
        key=_keys("filtre_cat"),
    )

    articles = get_all_articles(filtre_categorie=filtre_categorie or None)
    if not articles:
        st.info("Aucun article trouvé.")
        return

    st.caption(f"{len(articles)} article(s)")
    for a in articles:
        _afficher_article_card(a)


@ui_fragment
def afficher_onglet_alertes() -> None:
    """Onglet alertes DLC et stock bas."""
    st.subheader("⏰ Péremptions proches")
    jours = st.slider("Horizon DLC (jours)", 7, 90, 30, key=_keys("horizon_dlc"))
    alertes_dlc = get_alertes_peremption(jours=jours)
    if alertes_dlc:
        for a in alertes_dlc:
            urgence = (
                "🔴" if a["jours_restants"] < 7 else "🟡" if a["jours_restants"] < 15 else "🟢"
            )
            st.warning(
                f"{urgence} **{a['nom']}** — périme dans **{a['jours_restants']}j** "
                f"({a['dlc']:%d/%m/%Y})"
            )
    else:
        st.success("✅ Aucun article proche de la péremption.")

    st.divider()
    st.subheader("📉 Stocks bas")
    alertes_stock = get_alertes_stock()
    if alertes_stock:
        for a in alertes_stock:
            st.warning(f"⚠️ **{a['nom']}** — {a['quantite']} (seuil: {a['seuil_alerte']})")
    else:
        st.success("✅ Tous les stocks sont suffisants.")
