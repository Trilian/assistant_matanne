"""
Module Inventaire - UI Refactorisée
Version simplifiée : 500 lignes max, logique externalisée
"""
import streamlit as st
import asyncio
import pandas as pd
from datetime import datetime, date
from typing import List, Dict, Optional

from src.services.inventaire.inventaire_service import (
from src.utils.formatters import format_quantity, format_quantity_with_unit
    inventaire_service, CATEGORIES, EMPLACEMENTS
)
from src.services.inventaire.inventaire_ai_service import create_inventaire_ai_service
from src.services.inventaire.inventaire_io_service import (
    render_export_ui, render_import_ui
)
from src.core.state_manager import StateManager, get_state
from src.ui.components import (
    render_stat_row, render_empty_state, render_toast, render_badge
)


# ===================================
# CONSTANTES UI
# ===================================

STATUT_COLORS = {
    "ok": "#d4edda",
    "sous_seuil": "#fff3cd",
    "peremption_proche": "#f8d7da",
    "critique": "#dc3545"
}


# ===================================
# COMPOSANTS UI
# ===================================

def render_article_card(article: Dict, key: str):
    """Affiche une carte article"""
    couleur = STATUT_COLORS.get(article["statut"], "#f8f9fa")

    with st.container():
        st.markdown(f"""
        <div style="border-left: 4px solid {couleur}; 
                    padding: 1rem; 
                    background: {couleur}; 
                    border-radius: 8px; 
                    margin-bottom: 0.5rem;">
        </div>
        """, unsafe_allow_html=True)

        col1, col2, col3 = st.columns([3, 2, 2])

        with col1:
            st.markdown(f"### {article['icone']} {article['nom']}")
            st.caption(f"{article['categorie']} • {article['emplacement']}")

            # Alerte péremption
            if article.get("jours_peremption") is not None:
                jours = article["jours_peremption"]
                if jours <= 3:
                    st.error(f"⏳ Périme dans {jours} jour(s)")
                elif jours <= 7:
                    st.warning(f"⏳ Péremption dans {jours} jours")

        with col2:
            delta = None
            if article["quantite"] < article["seuil"]:
                delta = f"Seuil: {article['seuil']}"

            st.metric(
                "Stock",
                f"{format_quantity(article['quantite'])} {article['unite']}",
                delta=delta,
                delta_color="inverse" if delta else "off"
            )

        with col3:
            col_btn1, col_btn2, col_btn3 = st.columns(3)

            with col_btn1:
                if st.button("➕", key=f"plus_{key}", help="Ajouter 1"):
                    inventaire_service.ajuster_quantite(article["id"], 1)
                    render_toast(f"✅ +1 {article['unite']}", "success")
                    st.rerun()

            with col_btn2:
                if st.button("➖", key=f"minus_{key}", help="Retirer 1"):
                    inventaire_service.ajuster_quantite(article["id"], -1)
                    render_toast(f"➖ -1 {article['unite']}", "success")
                    st.rerun()

            with col_btn3:
                if st.button("🛒", key=f"cart_{key}", help="→ Courses"):
                    inventaire_service.ajouter_a_courses(article["id"])
                    render_toast(f"✅ Ajouté aux courses", "success")
                    st.rerun()


def render_quick_filters():
    """Filtres rapides"""
    col1, col2, col3, col4 = st.columns(4)

    filters = {}

    with col1:
        if st.button("⚠️ Stock bas", use_container_width=True):
            filters["sous_seuil_only"] = True

    with col2:
        if st.button("⏳ Péremption proche", use_container_width=True):
            StateManager.get().filter_peremption = True

    with col3:
        categorie = st.selectbox("Catégorie", ["Toutes"] + CATEGORIES, key="filter_cat")
        if categorie != "Toutes":
            filters["categorie"] = categorie

    with col4:
        emplacement = st.selectbox("Emplacement", ["Tous"] + EMPLACEMENTS, key="filter_emp")
        if emplacement != "Tous":
            filters["emplacement"] = emplacement

    return filters


# ===================================
# TABS
# ===================================

def tab_mon_stock():
    """Tab 1: Mon stock"""
    st.subheader("📦 Mon Stock")

    # Filtres
    filters = render_quick_filters()

    # Charger inventaire
    inventaire = inventaire_service.get_inventaire_complet(filters)

    # Filtrer péremption côté client si besoin
    if getattr(get_state(), "filter_peremption", False):
        inventaire = [
            i for i in inventaire
            if i.get("jours_peremption") is not None
               and i["jours_peremption"] <= 7
        ]

    if not inventaire:
        render_empty_state(
            message="Inventaire vide",
            icon="📦",
            action_label="➕ Ajouter un article",
            action_callback=lambda: st.session_state.update({"active_tab": 2})
        )
        return

    # Stats
    stats = inventaire_service.get_stats()
    stats_data = [
        {"label": "Total", "value": stats["total_articles"]},
        {"label": "Stock bas", "value": stats["total_stock_bas"], "delta_color": "inverse"},
        {"label": "Péremption", "value": stats["total_peremption"], "delta_color": "inverse"},
        {"label": "Critiques", "value": stats["total_critiques"], "delta_color": "inverse"}
    ]
    render_stat_row(stats_data, cols=4)

    st.markdown("---")

    # Afficher par statut
    for statut in ["critique", "sous_seuil", "peremption_proche", "ok"]:
        articles = [a for a in inventaire if a["statut"] == statut]

        if not articles:
            continue

        labels = {
            "critique": "🔴 Critiques",
            "sous_seuil": "⚠️ Stock Bas",
            "peremption_proche": "⏳ Péremption Proche",
            "ok": "✅ OK"
        }

        with st.expander(f"{labels[statut]} ({len(articles)})", expanded=statut in ["critique", "sous_seuil"]):
            for idx, article in enumerate(articles):
                render_article_card(article, f"{statut}_{idx}")


def tab_analyse_ia():
    """Tab 2: Analyse IA"""
    st.subheader("🤖 Analyse Intelligente")

    agent = get_state().agent_ia
    if not agent:
        st.error("❌ Agent IA non disponible")
        return

    ai_service = create_inventaire_ai_service(agent)
    inventaire = inventaire_service.get_inventaire_complet()

    if not inventaire:
        st.info("Inventaire vide - Rien à analyser")
        return

    # Analyses disponibles
    col1, col2 = st.columns(2)

    with col1:
        if st.button("🚨 Détecter Gaspillage", use_container_width=True, type="primary"):
            with st.spinner("🤖 Analyse en cours..."):
                try:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)

                    result = loop.run_until_complete(
                        ai_service.detecter_gaspillage(inventaire)
                    )

                    StateManager.cache_set("gaspillage_analyse", result)
                    st.rerun()

                except Exception as e:
                    st.error(f"❌ Erreur: {str(e)}")

    with col2:
        if st.button("🍽️ Suggérer Recettes", use_container_width=True, type="primary"):
            with st.spinner("🤖 Recherche recettes..."):
                try:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)

                    result = loop.run_until_complete(
                        ai_service.suggerer_recettes_stock(inventaire, nb=5)
                    )

                    StateManager.cache_set("recettes_suggestions", result)
                    st.rerun()

                except Exception as e:
                    st.error(f"❌ Erreur: {str(e)}")

    st.markdown("---")

    # Afficher résultats gaspillage
    gaspillage = StateManager.cache_get("gaspillage_analyse", ttl=3600)
    if gaspillage:
        st.markdown("### 🚨 Analyse Gaspillage")

        if gaspillage["statut"] == "OK":
            st.success("✅ Aucun risque de gaspillage détecté")
        else:
            st.warning(f"⚠️ {gaspillage.get('items_risque', 0)} article(s) à risque")

            if gaspillage.get("recettes_urgentes"):
                st.markdown("**Recettes urgentes :**")
                for recette in gaspillage["recettes_urgentes"]:
                    st.info(f"🍽️ {recette}")

            if gaspillage.get("conseils"):
                st.markdown("**Conseils :**")
                for conseil in gaspillage["conseils"]:
                    st.write(f"💡 {conseil}")

    # Afficher suggestions recettes
    recettes = StateManager.cache_get("recettes_suggestions", ttl=3600)
    if recettes:
        st.markdown("---")
        st.markdown("### 🍽️ Recettes Faisables")

        for recette in recettes:
            with st.expander(f"{recette['nom']} - Faisabilité: {recette['faisabilite']}%"):
                st.write(f"**Raison :** {recette.get('raison', '')}")
                st.write(f"**Temps :** {recette.get('temps_total', '?')} min")

                if recette.get("ingredients_utilises"):
                    st.caption(f"Ingrédients : {', '.join(recette['ingredients_utilises'][:5])}")

    # Analyse complète
    st.markdown("---")
    if st.button("📊 Analyse Complète", use_container_width=True):
        with st.spinner("🤖 Analyse approfondie..."):
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

                result = loop.run_until_complete(
                    ai_service.analyser_inventaire_complet(inventaire)
                )

                st.markdown("### 📊 Analyse Complète")

                col_score1, col_score2 = st.columns(2)
                with col_score1:
                    st.metric("Score Global", f"{result.get('score_global', 0)}/100")
                with col_score2:
                    statut = result.get("statut", "").upper()
                    if statut in ["CRITIQUE", "ATTENTION"]:
                        st.error(f"⚠️ {statut}")
                    else:
                        st.success(f"✅ {statut}")

                if result.get("problemes"):
                    st.markdown("**Problèmes détectés :**")
                    for pb in result["problemes"]:
                        st.warning(f"• {pb.get('conseil', '')}")

                if result.get("recommandations"):
                    st.markdown("**Recommandations :**")
                    for reco in result["recommandations"]:
                        st.info(f"💡 {reco}")

            except Exception as e:
                st.error(f"❌ Erreur: {str(e)}")


def tab_ajout():
    """Tab 3: Ajout/Modification"""
    st.subheader("➕ Ajouter/Modifier Article")

    with st.form("form_article"):
        col1, col2 = st.columns(2)

        with col1:
            nom = st.text_input("Nom *", placeholder="Ex: Tomates")
            categorie = st.selectbox("Catégorie *", CATEGORIES)
            quantite = st.number_input("Quantité *", 0.0, 10000.0, 1.0, 0.1)
            unite = st.selectbox("Unité", ["pcs", "kg", "g", "L", "mL", "sachets", "boîtes", "botte"])

        with col2:
            seuil = st.number_input("Seuil d'alerte", 0.0, 1000.0, 1.0, 0.1)
            emplacement = st.selectbox("Emplacement", EMPLACEMENTS)
            date_peremption = st.date_input("Péremption (optionnel)", value=None)

        if st.form_submit_button("➕ Ajouter", type="primary", use_container_width=True):
            if not nom:
                st.error("Le nom est obligatoire")
            else:
                inventaire_service.ajouter_ou_modifier(
                    nom=nom,
                    categorie=categorie,
                    quantite=quantite,
                    unite=unite,
                    seuil=seuil,
                    emplacement=emplacement,
                    date_peremption=date_peremption
                )
                render_toast(f"✅ {nom} ajouté", "success")
                st.balloons()
                st.rerun()


def tab_import_export():
    """Tab 4: Import/Export"""
    st.subheader("📤 Import/Export")

    tab_exp, tab_imp = st.tabs(["📤 Export", "📥 Import"])

    with tab_exp:
        inventaire = inventaire_service.get_inventaire_complet()

        if not inventaire:
            st.info("Inventaire vide - Rien à exporter")
        else:
            render_export_ui(inventaire)

    with tab_imp:
        render_import_ui(inventaire_service)


def tab_stats():
    """Tab 5: Statistiques"""
    st.subheader("📊 Statistiques")

    inventaire = inventaire_service.get_inventaire_complet()
    stats = inventaire_service.get_stats()

    if not inventaire:
        st.info("Inventaire vide - Pas de stats")
        return

    # Métriques principales
    stats_data = [
        {"label": "Total articles", "value": stats["total_articles"]},
        {"label": "Catégories", "value": len(stats["categories"])},
        {"label": "Alertes totales", "value": stats["total_critiques"] + stats["total_stock_bas"] + stats["total_peremption"]}
    ]
    render_stat_row(stats_data, cols=3)

    st.markdown("---")

    # Graphiques
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 📈 Par Catégorie")

        if stats["categories"]:
            df_cat = pd.DataFrame([
                {"Catégorie": k, "Nombre": v}
                for k, v in stats["categories"].items()
            ])
            st.bar_chart(df_cat.set_index("Catégorie"))

    with col2:
        st.markdown("### ⚠️ Alertes")

        df_alertes = pd.DataFrame([
            {"Type": "Critiques", "Nombre": stats["total_critiques"]},
            {"Type": "Stock bas", "Nombre": stats["total_stock_bas"]},
            {"Type": "Péremption", "Nombre": stats["total_peremption"]}
        ])
        st.bar_chart(df_alertes.set_index("Type"))

    st.markdown("---")

    # Top/Bottom
    col_top1, col_top2 = st.columns(2)

    with col_top1:
        st.markdown("### 🔝 Plus gros stocks")
        top10 = sorted(inventaire, key=lambda x: x["quantite"], reverse=True)[:10]

        for item in top10:
            st.write(f"• **{item['nom']}** : {format_quantity(item['quantite'])} {item['unite']}")

    with col_top2:
        st.markdown("### 📉 Stocks critiques")
        critiques = [i for i in inventaire if i["statut"] in ["critique", "sous_seuil"]]

        if critiques:
            for item in critiques[:10]:
                st.write(f"• {item['icone']} **{item['nom']}** : {format_quantity(item['quantite'])}/{item['seuil']}")
        else:
            st.success("✅ Aucun stock critique")


# ===================================
# MODULE PRINCIPAL
# ===================================

def app():
    """Point d'entrée du module Inventaire"""
    st.title("📦 Inventaire Intelligent")
    st.caption("Gestion complète avec alertes et prédictions IA")

    # Tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📦 Mon Stock",
        "🤖 Analyse IA",
        "➕ Ajouter",
        "📤 Import/Export",
        "📊 Statistiques"
    ])

    with tab1:
        tab_mon_stock()

    with tab2:
        tab_analyse_ia()

    with tab3:
        tab_ajout()

    with tab4:
        tab_import_export()

    with tab5:
        tab_stats()