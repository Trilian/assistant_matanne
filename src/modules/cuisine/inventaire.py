"""
Module Inventaire - Gestion du stock
✨ Fonctionnalités complètes:
- Gestion complète du stock avec alertes
- Catégorisation et filtres avancés
- Suggestions IA pour les courses
- Export/Import des données
"""

import streamlit as st
import pandas as pd
from datetime import date, timedelta
from typing import Any

from src.services.inventaire import get_inventaire_service
from src.core.errors_base import ErreurValidation


def app():
    """Point d'entrée module inventaire"""
    st.set_page_config(page_title="📦 Inventaire", layout="wide")
    
    st.title("📦 Inventaire")
    st.caption("Gestion complète de votre stock d'ingrédients")

    # Initialiser session state
    if "show_form" not in st.session_state:
        st.session_state.show_form = False
    if "refresh_counter" not in st.session_state:
        st.session_state.refresh_counter = 0

    # Tabs principales
    tab_stock, tab_alertes, tab_categories, tab_suggestions, tab_tools = st.tabs([
        "📊 Stock", 
        "⚠️ Alertes", 
        "🏷️ Catégories", 
        "🛒 Suggestions IA",
        "🔧 Outils"
    ])

    with tab_stock:
        render_stock()

    with tab_alertes:
        render_alertes()

    with tab_categories:
        render_categories()

    with tab_suggestions:
        render_suggestions_ia()

    with tab_tools:
        render_tools()


def render_stock():
    """Affiche le stock actuel avec filtres et statistiques"""
    service = get_inventaire_service()
    
    if service is None:
        st.error("❌ Service inventaire indisponible")
        return
    
    try:
        inventaire = service.get_inventaire_complet()
        
        if not inventaire:
            st.info("📦 Inventaire vide. Commencez par ajouter des articles!")
            if st.button("➕ Ajouter un article"):
                st.session_state.show_form = True
            return
        
        # ═══════════════════════════════════════════════════════════
        # STATISTIQUES GLOBALES
        # ═══════════════════════════════════════════════════════════
        col1, col2, col3, col4 = st.columns(4)
        
        alertes = service.get_alertes()
        stock_critique = len(alertes.get("critique", []))
        stock_bas = len(alertes.get("stock_bas", []))
        peremption = len(alertes.get("peremption_proche", []))
        
        with col1:
            st.metric("📦 Articles", len(inventaire), delta=None)
        with col2:
            color = "🔴" if stock_critique > 0 else "🟢"
            st.metric(f"{color} Critique", stock_critique)
        with col3:
            color = "🟠" if stock_bas > 0 else "🟢"
            st.metric(f"{color} Faible", stock_bas)
        with col4:
            color = "🔔" if peremption > 0 else "🟢"
            st.metric(f"{color} Péremption", peremption)
        
        st.divider()
        
        # ═══════════════════════════════════════════════════════════
        # FILTRES ET TRI
        # ═══════════════════════════════════════════════════════════
        col_filter1, col_filter2, col_filter3 = st.columns(3)
        
        with col_filter1:
            emplacements = sorted(set(a["emplacement"] for a in inventaire if a["emplacement"]))
            selected_emplacements = st.multiselect(
                "📍 Emplacement",
                options=emplacements,
                default=[]
            )
        
        with col_filter2:
            categories = sorted(set(a["ingredient_categorie"] for a in inventaire))
            selected_categories = st.multiselect(
                "🏷️ Catégorie",
                options=categories,
                default=[]
            )
        
        with col_filter3:
            status_filter = st.multiselect(
                "⚠️ Statut",
                options=["critique", "stock_bas", "peremption_proche", "ok"],
                default=[]
            )
        
        # ═══════════════════════════════════════════════════════════
        # APPLIQUER LES FILTRES
        # ═══════════════════════════════════════════════════════════
        inventaire_filtres = inventaire
        
        if selected_emplacements:
            inventaire_filtres = [a for a in inventaire_filtres if a["emplacement"] in selected_emplacements]
        
        if selected_categories:
            inventaire_filtres = [a for a in inventaire_filtres if a["ingredient_categorie"] in selected_categories]
        
        if status_filter:
            inventaire_filtres = [a for a in inventaire_filtres if a["statut"] in status_filter]
        
        # ═══════════════════════════════════════════════════════════
        # AFFICHER LE TABLEAU
        # ═══════════════════════════════════════════════════════════
        if inventaire_filtres:
            df = _prepare_inventory_dataframe(inventaire_filtres)
            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Statut": st.column_config.TextColumn(width="small"),
                    "Quantité": st.column_config.NumberColumn(width="small"),
                    "Jours": st.column_config.NumberColumn(width="small"),
                }
            )
        else:
            st.info("Aucun article ne correspond aux filtres sélectionnés.")
        
        # ═══════════════════════════════════════════════════════════
        # BOUTONS D'ACTION
        # ═══════════════════════════════════════════════════════════
        st.divider()
        col_btn1, col_btn2, col_btn3 = st.columns(3)
        
        with col_btn1:
            if st.button("➕ Ajouter un article", use_container_width=True):
                st.session_state.show_form = True
                st.rerun()
        
        with col_btn2:
            if st.button("🔄 Rafraîchir", use_container_width=True):
                st.session_state.refresh_counter += 1
                st.rerun()
        
        with col_btn3:
            if st.button("📥 Importer CSV", use_container_width=True):
                st.session_state.show_import = True
    
    except ErreurValidation as e:
        st.error(f"❌ Erreur de validation: {e}")
    except Exception as e:
        st.error(f"❌ Erreur: {str(e)}")


def render_alertes():
    """Affiche les articles en alerte avec actions rapides"""
    service = get_inventaire_service()
    
    if service is None:
        st.error("❌ Service inventaire indisponible")
        return
    
    try:
        alertes = service.get_alertes()
        
        if not any(alertes.values()):
            st.success("✅ Aucune alerte! Votre inventaire est en bon état.")
            return
        
        # ═══════════════════════════════════════════════════════════
        # ARTICLES CRITIQUES
        # ═══════════════════════════════════════════════════════════
        if alertes["critique"]:
            st.error(f"🔴 {len(alertes['critique'])} articles en stock critique")
            df = _prepare_alert_dataframe(alertes["critique"])
            st.dataframe(df, use_container_width=True, hide_index=True)
        
        st.divider()
        
        # ═══════════════════════════════════════════════════════════
        # STOCK BAS
        # ═══════════════════════════════════════════════════════════
        if alertes["stock_bas"]:
            st.warning(f"🟠 {len(alertes['stock_bas'])} articles avec stock faible")
            df = _prepare_alert_dataframe(alertes["stock_bas"])
            st.dataframe(df, use_container_width=True, hide_index=True)
        
        st.divider()
        
        # ═══════════════════════════════════════════════════════════
        # PÉREMPTION PROCHE
        # ═══════════════════════════════════════════════════════════
        if alertes["peremption_proche"]:
            st.warning(f"🔔 {len(alertes['peremption_proche'])} articles proche péremption")
            df = _prepare_alert_dataframe(alertes["peremption_proche"])
            st.dataframe(df, use_container_width=True, hide_index=True)
    
    except Exception as e:
        st.error(f"❌ Erreur: {str(e)}")


def render_categories():
    """Gestion des catégories d'ingrédients"""
    service = get_inventaire_service()
    
    if service is None:
        st.error("❌ Service inventaire indisponible")
        return
    
    try:
        inventaire = service.get_inventaire_complet()
        
        if not inventaire:
            st.info("Inventaire vide")
            return
        
        # Grouper par catégorie
        categories = {}
        for article in inventaire:
            cat = article["ingredient_categorie"]
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(article)
        
        # Afficher par onglet
        tabs = st.tabs([f"🏷️ {cat} ({len(articles)})" for cat, articles in sorted(categories.items())])
        
        for (cat, articles), tab in zip(sorted(categories.items()), tabs):
            with tab:
                # Statistiques catégorie
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Articles", len(articles))
                with col2:
                    total_qty = sum(a["quantite"] for a in articles)
                    st.metric("Quantité totale", f"{total_qty:.1f}")
                with col3:
                    alertes = service.get_alertes()
                    cat_alertes = len([a for a in articles if a["statut"] in ["critique", "stock_bas"]])
                    st.metric("⚠️ Alertes", cat_alertes)
                
                st.divider()
                
                # Tableau catégorie
                df = _prepare_inventory_dataframe(articles)
                st.dataframe(df, use_container_width=True, hide_index=True)
    
    except Exception as e:
        st.error(f"❌ Erreur: {str(e)}")


def render_suggestions_ia():
    """Affiche les suggestions IA pour les courses"""
    service = get_inventaire_service()
    
    if service is None:
        st.error("❌ Service inventaire indisponible")
        return
    
    st.info("🤖 Suggestions IA basées sur l'état de votre inventaire")
    
    if st.button("🛒 Générer les suggestions", use_container_width=True):
        try:
            with st.spinner("Génération des suggestions..."):
                suggestions = service.suggerer_courses_ia()
            
            if suggestions:
                st.success(f"✅ {len(suggestions)} suggestions générées")
                
                # Grouper par priorité
                by_priority = {}
                for sugg in suggestions:
                    p = sugg.priorite
                    if p not in by_priority:
                        by_priority[p] = []
                    by_priority[p].append(sugg)
                
                # Afficher par priorité
                for priority in ["haute", "moyenne", "basse"]:
                    if priority in by_priority:
                        icon = "🔴" if priority == "haute" else "🟠" if priority == "moyenne" else "🟢"
                        with st.expander(f"{icon} Priorité {priority.upper()} ({len(by_priority[priority])})"):
                            for sugg in by_priority[priority]:
                                col1, col2, col3, col4 = st.columns(4)
                                with col1:
                                    st.write(f"**{sugg.nom}**")
                                with col2:
                                    st.write(f"{sugg.quantite} {sugg.unite}")
                                with col3:
                                    st.write(f"📍 {sugg.rayon}")
                                with col4:
                                    if st.button("✅ Ajouter", key=f"add_{sugg.nom}"):
                                        st.success(f"✅ {sugg.nom} ajouté aux courses")
            else:
                st.warning("Aucune suggestion générée")
        
        except Exception as e:
            st.error(f"❌ Erreur: {str(e)}")


def render_tools():
    """Outils utilitaires pour l'inventaire"""
    st.subheader("🔧 Outils d'administration")
    
    tab_export, tab_stats = st.tabs(["📥 Export/Import", "📊 Statistiques"])
    
    with tab_export:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📥 Exporter les données")
            if st.button("Télécharger en CSV", use_container_width=True):
                service = get_inventaire_service()
                if service:
                    try:
                        inventaire = service.get_inventaire_complet()
                        df = _prepare_inventory_dataframe(inventaire)
                        csv = df.to_csv(index=False)
                        st.download_button(
                            label="📥 Télécharger CSV",
                            data=csv,
                            file_name="inventaire.csv",
                            mime="text/csv"
                        )
                    except Exception as e:
                        st.error(f"❌ Erreur: {str(e)}")
        
        with col2:
            st.subheader("📤 Importer les données")
            st.warning("⚠️ L'import est en développement")
    
    with tab_stats:
        service = get_inventaire_service()
        if service:
            try:
                inventaire = service.get_inventaire_complet()
                alertes = service.get_alertes()
                
                st.subheader("📊 Statistiques globales")
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total articles", len(inventaire))
                with col2:
                    emplacements = len(set(a["emplacement"] for a in inventaire if a["emplacement"]))
                    st.metric("Emplacements", emplacements)
                with col3:
                    categories = len(set(a["ingredient_categorie"] for a in inventaire))
                    st.metric("Catégories", categories)
                with col4:
                    total_alertes = sum(len(v) for v in alertes.values())
                    st.metric("Alertes actives", total_alertes)
                
                st.divider()
                
                # Graphiques
                st.subheader("📈 Répartition")
                
                col_graph1, col_graph2 = st.columns(2)
                
                with col_graph1:
                    st.write("**Statuts**")
                    statuts = {}
                    for article in inventaire:
                        s = article["statut"]
                        statuts[s] = statuts.get(s, 0) + 1
                    st.bar_chart(statuts)
                
                with col_graph2:
                    st.write("**Catégories**")
                    cats = {}
                    for article in inventaire:
                        c = article["ingredient_categorie"]
                        cats[c] = cats.get(c, 0) + 1
                    st.bar_chart(cats)
            
            except Exception as e:
                st.error(f"❌ Erreur: {str(e)}")


# ═══════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════

def _prepare_inventory_dataframe(inventaire: list[dict[str, Any]]) -> pd.DataFrame:
    """Prépare un DataFrame pour affichage inventaire"""
    data = []
    for article in inventaire:
        statut_icon = {
            "critique": "🔴",
            "stock_bas": "🟠",
            "peremption_proche": "🔔",
            "ok": "🟢"
        }.get(article["statut"], "❓")
        
        data.append({
            "Statut": f"{statut_icon} {article['statut']}",
            "Article": article["ingredient_nom"],
            "Catégorie": article["ingredient_categorie"],
            "Quantité": f"{article['quantite']:.1f} {article['unite']}",
            "Seuil min": f"{article['quantite_min']:.1f} {article['unite']}",
            "Emplacement": article["emplacement"] or "-",
            "Jours": article["jours_avant_peremption"] or "-",
            "Maj": pd.Timestamp(article["derniere_maj"]).strftime("%d/%m/%Y") if "derniere_maj" in article else "-",
        })
    
    return pd.DataFrame(data)


def _prepare_alert_dataframe(articles: list[dict[str, Any]]) -> pd.DataFrame:
    """Prépare un DataFrame pour affichage alertes"""
    data = []
    for article in articles:
        statut_icon = {
            "critique": "🔴",
            "stock_bas": "🟠",
            "peremption_proche": "🔔",
        }.get(article["statut"], "❓")
        
        jours = ""
        if article["jours_avant_peremption"] is not None:
            jours = f"{article['jours_avant_peremption']} jours"
        
        data.append({
            "Article": article["ingredient_nom"],
            "Catégorie": article["ingredient_categorie"],
            "Quantité": f"{article['quantite']:.1f} {article['unite']}",
            "Seuil": f"{article['quantite_min']:.1f}",
            "Emplacement": article["emplacement"] or "-",
            "Problème": jours if jours else "Stock critique",
        })
    
    return pd.DataFrame(data)
