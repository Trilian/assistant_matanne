"""

Module Inventaire - Gestion du stock

 Fonctionnalités complètes:

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

from src.services.predictions import obtenir_service_predictions

from src.core.errors_base import ErreurValidation



# Import du module logique métier séparé

from src.domains.cuisine.logic.inventaire_logic import (

    EMPLACEMENTS,

    CATEGORIES,

    STATUS_CONFIG,

    calculer_status_stock,

    calculer_status_peremption,

    calculer_alertes,

    calculer_statistiques_inventaire,

    valider_article_inventaire,

    formater_article_inventaire,

    trier_par_urgence,

    filtrer_par_status,

    filtrer_par_categorie,

    filtrer_par_emplacement,

    grouper_par_categorie,

)





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

    tab_stock, tab_alertes, tab_categories, tab_suggestions, tab_historique, tab_photos, tab_notifications, tab_predictions, tab_tools = st.tabs([

        "📊 Stock", 

        "⚠️ Alertes", 

        "🏷️ Catégories", 

        "🛒 Suggestions IA",

        "📋 Historique",

        "📷 Photos",

        "📢 Notifications",

        "🔮 Prévisions",

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



    with tab_historique:

        render_historique()



    with tab_photos:

        render_photos()



    with tab_notifications:

        render_notifications()



    with tab_predictions:

        render_predictions()



    with tab_tools:

        render_tools()


    # Afficher formulaire d'ajout si demandé
    if st.session_state.show_form:
        st.divider()
        render_add_article_form()





def render_add_article_form():
    """Affiche le formulaire pour ajouter un nouvel article"""
    service = get_inventaire_service()
    
    if service is None:
        st.error("❌ Service inventaire indisponible")
        return
    
    st.subheader("➕ Ajouter un nouvel article")
    
    try:
        col1, col2 = st.columns(2)
        
        with col1:
            ingredient_nom = st.text_input("Nom de l'article *", placeholder="Ex: Tomates cerises")
        
        with col2:
            quantite = st.number_input("Quantité", value=1.0, min_value=0.0)
        
        col1, col2 = st.columns(2)
        
        with col1:
            emplacement = st.text_input("Emplacement", placeholder="Frigo, Placard...")
        
        with col2:
            date_peremption = st.date_input("Date de péremption", value=None)
        
        col1, col2 = st.columns([1, 4])
        
        with col1:
            if st.button("✨ Ajouter", use_container_width=True, type="primary"):
                if not ingredient_nom:
                    st.error("❌ Le nom est obligatoire")
                else:
                    try:
                        article = service.ajouter_article(
                            ingredient_nom=ingredient_nom,
                            quantite=quantite,
                            emplacement=emplacement if emplacement else None,
                            date_peremption=date_peremption if date_peremption else None
                        )
                        
                        if article:
                            st.success(f"✅ Article '{ingredient_nom}' ajouté avec succès!")
                            st.session_state.show_form = False
                            st.session_state.refresh_counter += 1
                            st.rerun()
                        else:
                            st.error(f"❌ Impossible d'ajouter l'article")
                    
                    except ErreurValidation as e:
                        st.error(f"❌ Erreur: {e}")
                    except Exception as e:
                        st.error(f"❌ Erreur lors de l'ajout: {str(e)}")
                        logger.error(f"Erreur ajouter_article: {e}")
        
        with col2:
            if st.button("❌ Annuler", use_container_width=True):
                st.session_state.show_form = False
                st.rerun()
    
    except Exception as e:
        st.error(f"❌ Erreur: {str(e)}")
        logger.error(f"Erreur render_add_article_form: {e}")


def render_stock():

    """Affiche le stock actuel avec filtres et statistiques"""

    service = get_inventaire_service()

    

    if service is None:

        st.error("❌ Service inventaire indisponible")

        return

    

    try:

        inventaire = service.get_inventaire_complet()

        

        if not inventaire:

            st.info("📆 Inventaire vide. Commencez par ajouter des articles!")

            if st.button("➕ Ajouter un article"):

                st.session_state.show_form = True

            return

        

        # ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•

        # STATISTIQUES GLOBALES

        # ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•

        col1, col2, col3, col4 = st.columns(4)

        

        alertes = service.get_alertes()

        stock_critique = len(alertes.get("critique", []))

        stock_bas = len(alertes.get("stock_bas", []))

        peremption = len(alertes.get("peremption_proche", []))

        

        with col1:

            st.metric("[PKG] Articles", len(inventaire), delta=None)

        with col2:

            color = "❌" if stock_critique > 0 else "✅"

            st.metric(f"{color} Critique", stock_critique)

        with col3:

            color = " " if stock_bas > 0 else "✅"

            st.metric(f"{color} Faible", stock_bas)

        with col4:

            color = "⏰" if peremption > 0 else "✅"

            st.metric(f"{color} Péremption", peremption)

        

        st.divider()

        

        # ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•

        # FILTRES ET TRI

        # ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•

        col_filter1, col_filter2, col_filter3 = st.columns(3)

        

        with col_filter1:

            emplacements = sorted(set(a["emplacement"] for a in inventaire if a["emplacement"]))

            selected_emplacements = st.multiselect(

                "📈 Emplacement",

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

                "[!] Statut",

                options=["critique", "stock_bas", "peremption_proche", "ok"],

                default=[]

            )

        

        # ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•

        # APPLIQUER LES FILTRES

        # ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•

        inventaire_filtres = inventaire

        

        if selected_emplacements:

            inventaire_filtres = [a for a in inventaire_filtres if a["emplacement"] in selected_emplacements]

        

        if selected_categories:

            inventaire_filtres = [a for a in inventaire_filtres if a["ingredient_categorie"] in selected_categories]

        

        if status_filter:

            inventaire_filtres = [a for a in inventaire_filtres if a["statut"] in status_filter]

        

        # ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•

        # AFFICHER LE TABLEAU

        # ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•

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

        

        # ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•

        # BOUTONS D'ACTION

        # ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•

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

            if st.button("📷 Importer CSV", use_container_width=True):

                st.session_state.show_import = True

    

    except ErreurValidation as e:

        st.error(f"❌ Erreur de validation: {e}")

    except Exception as e:

        st.error(f"❌ Erreur: {str(e)}")





def render_notifications_widget():

    """Widget affichant les notifications actives (à utiliser en sidebar)"""

    from src.services.notifications import obtenir_service_notifications

    

    service_notifs = obtenir_service_notifications()

    notifs = service_notifs.obtenir_notifications(non_lues_seulement=True)

    

    if not notifs:

        return

    

    # Affiche le badge de notification

    col1, col2, col3 = st.columns([2, 1, 1])

    

    with col1:

        st.metric("⏰ Notifications", len(notifs), delta="À traiter")

    

    with col2:

        if st.button("🔄 Actualiser", key="refresh_notifs", use_container_width=True):

            st.rerun()

    

    with col3:

        if st.button("✨ Tout lire", key="mark_all_read", use_container_width=True):

            for notif in notifs:

                service_notifs.marquer_lue(notif.id)

            st.rerun()

    

    # Affiche les notifications groupées par priorité

    st.divider()

    

    # Critiques

    critiques = [n for n in notifs if n.priorite == "haute"]

    if critiques:

        st.markdown("### 🚨 CRITIQUES")

        for notif in critiques:

            with st.container(border=True):

                col1, col2 = st.columns([0.9, 0.1])

                with col1:

                    st.write(f"**{notif.icone} {notif.titre}**")

                    st.caption(notif.message)

                with col2:

                    if st.button("êœ“", key=f"mark_read_{notif.id}", help="Marquer comme lu"):

                        service_notifs.marquer_lue(notif.id)

                        st.rerun()

    

    # Moyennes

    moyennes = [n for n in notifs if n.priorite == "moyenne"]

    if moyennes:

        st.markdown("### [!] MOYENNES")

        for notif in moyennes[:3]:  # Affiche seulement les 3 premières

            with st.container(border=True):

                col1, col2 = st.columns([0.9, 0.1])

                with col1:

                    st.write(f"**{notif.icone} {notif.titre}**")

                    st.caption(notif.message)

                with col2:

                    if st.button("êœ“", key=f"mark_read_{notif.id}", help="Marquer comme lu"):

                        service_notifs.marquer_lue(notif.id)

                        st.rerun()

        

        if len(moyennes) > 3:

            st.caption(f"... et {len(moyennes) - 3} autres")





def render_alertes():

    """Affiche les articles en alerte avec actions rapides"""

    service = get_inventaire_service()

    

    if service is None:

        st.error("❌ Service inventaire indisponible")

        return

    

    try:

        alertes = service.get_alertes()

        

        if not any(alertes.values()):

            st.success("✨ Aucune alerte! Votre inventaire est en bon état.")

            return

        

        # ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•

        # ARTICLES CRITIQUES

        # ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•

        if alertes["critique"]:

            st.error(f"❌ {len(alertes['critique'])} articles en stock critique")

            df = _prepare_alert_dataframe(alertes["critique"])

            st.dataframe(df, use_container_width=True, hide_index=True)

        

        st.divider()

        

        # ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•

        # STOCK BAS

        # ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•

        if alertes["stock_bas"]:

            st.warning(f"  {len(alertes['stock_bas'])} articles avec stock faible")

            df = _prepare_alert_dataframe(alertes["stock_bas"])

            st.dataframe(df, use_container_width=True, hide_index=True)

        

        st.divider()

        

        # ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•

        # PÉREMPTION PROCHE

        # ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•

        if alertes["peremption_proche"]:

            st.warning(f"⏰ {len(alertes['peremption_proche'])} articles proche péremption")

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

                    st.metric("[!] Alertes", cat_alertes)

                

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

    

    if st.button("🗑️ Générer les suggestions", use_container_width=True):

        try:

            with st.spinner("Génération des suggestions..."):

                suggestions = service.suggerer_courses_ia()

            

            if suggestions:

                st.success(f"✨ {len(suggestions)} suggestions générées")

                

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

                        icon = "❌" if priority == "haute" else " " if priority == "moyenne" else "✅"

                        with st.expander(f"{icon} Priorité {priority.upper()} ({len(by_priority[priority])})"):

                            for sugg in by_priority[priority]:

                                col1, col2, col3, col4 = st.columns(4)

                                with col1:

                                    st.write(f"**{sugg.nom}**")

                                with col2:

                                    st.write(f"{sugg.quantite} {sugg.unite}")

                                with col3:

                                    st.write(f"📈 {sugg.rayon}")

                                with col4:

                                    if st.button("✨ Ajouter", key=f"add_{sugg.nom}"):

                                        st.success(f"✨ {sugg.nom} ajouté aux courses")

            else:

                st.warning("Aucune suggestion générée")

        

        except Exception as e:

            st.error(f"❌ Erreur: {str(e)}")





def render_photos():

    """Gestion des photos pour les articles de l'inventaire"""

    st.subheader("📷 Gestion des photos")

    

    # Récupère l'inventaire

    service = get_inventaire_service()

    articles_data = service.get_inventaire_complet()

    

    if not articles_data:

        st.info("Aucun article dans l'inventaire")

        return

    

    # Sélectionne un article

    col1, col2 = st.columns([3, 1])

    with col1:

        article_names = [f"{a['ingredient_nom']} ({a['quantite']} {a['unite']})" for a in articles_data]

        selected_idx = st.selectbox("Sélectionne un article", range(len(article_names)), format_func=lambda i: article_names[i], key="select_photo_article")

        selected_article = articles_data[selected_idx]

        article_id = selected_article["id"]

    

    # Affiche la photo actuelle

    with col2:

        st.metric("État", "📷 Photo" if selected_article.get("photo_url") else "❌ Pas photo")

    

    # Onglets upload/gestion

    tab_upload, tab_view = st.tabs(["🍽️ Ajouter/Remplacer", "👁️ Afficher"])

    

    with tab_upload:

        st.write("**Ajouter ou remplacer la photo**")

        

        # Upload image

        uploaded_file = st.file_uploader(

            "Sélectionne une image",

            type=["jpg", "jpeg", "png", "webp"],

            help="Format: JPG, PNG, ou WebP. Max 5 MB"

        )

        

        if uploaded_file:

            # Affiche un aperçu

            col1, col2 = st.columns([1, 2])

            with col1:

                st.image(uploaded_file, width=150, caption="Aperçu")

            

            with col2:

                st.write(f"**Fichier:** {uploaded_file.name}")

                st.write(f"**Taille:** {uploaded_file.size / 1024:.1f} KB")

                

                # Simule l'upload (dans une vraie app, on sauvegarderait le fichier)

                if st.button("✨ Confirmer l'upload", key="confirm_photo_upload"):

                    try:

                        # Pour le prototype, on utilise une URL Streamlit

                        photo_url = f"streamlit_uploaded://{uploaded_file.name}"

                        

                        result = service.ajouter_photo(

                            article_id=article_id,

                            photo_url=photo_url,

                            photo_filename=uploaded_file.name,

                        )

                        

                        st.success("✨ Photo ajoutée avec succès!")

                        st.toast("Photo mise à jour", icon="📷")

                        st.rerun()

                    except Exception as e:

                        st.error(f"Erreur: {str(e)}")

        

        # Bouton supprimer

        if selected_article.get("photo_url"):

            st.divider()

            if st.button("🧹¸  Supprimer la photo", key="delete_photo"):

                try:

                    service.supprimer_photo(article_id)

                    st.success("✨ Photo supprimée")

                    st.rerun()

                except Exception as e:

                    st.error(f"Erreur: {str(e)}")

    

    with tab_view:

        st.write(f"**Photo de {selected_article['ingredient_nom']}**")

        

        if selected_article.get("photo_url"):

            # Affiche la photo

            col1, col2 = st.columns([2, 1])

            

            with col1:

                # Essaie d'afficher l'image

                try:

                    st.image(

                        selected_article["photo_url"],

                        caption=selected_article.get("photo_filename", "Photo"),

                        use_column_width=True

                    )

                except:

                    st.warning("Impossible d'afficher la photo")

            

            with col2:

                # Info

                st.metric("Fichier", selected_article.get("photo_filename", "N/A"))

                if selected_article.get("photo_uploaded_at"):

                    st.caption(f"Uploadée: {selected_article['photo_uploaded_at']}")

        else:

            st.info("Pas de photo pour cet article")

            st.write("Ajoute une photo dans l'onglet 'Ajouter/Remplacer'")





def render_notifications():

    """Gestion et affichage des notifications d'alerte"""

    from src.services.notifications import obtenir_service_notifications

    

    st.subheader("⏰ Notifications et Alertes")

    

    service = get_inventaire_service()

    service_notifs = obtenir_service_notifications()

    

    # Onglets

    tab_center, tab_config = st.tabs(["👧 Centre de notifications", "⚙️ Configuration"])

    

    with tab_center:

        # Actualiser les notifications

        col1, col2, col3 = st.columns([2, 1, 1])

        

        with col1:

            if st.button("🔄 Actualiser les alertes", use_container_width=True, key="refresh_all_alerts"):

                try:

                    stats = service.generer_notifications_alertes()

                    total = sum(len(v) for v in stats.values())

                    st.toast(f"✨ {total} alertes détectées", icon="⏰")

                except Exception as e:

                    st.error(f"Erreur: {str(e)}")

        

        with col2:

            stats_notifs = service_notifs.obtenir_stats()

            st.metric("👧 Non lues", stats_notifs["non_lues"])

        

        with col3:

            if st.button("✨ Tout marquer comme lu", use_container_width=True):

                service_notifs.effacer_toutes_lues()

                st.toast("✨ Notifications marquées comme lues")

                st.rerun()

        

        st.divider()

        

        # Affiche les notifications groupées

        notifs = service_notifs.obtenir_notifications()

        

        if not notifs:

            st.info("✨ Aucune notification pour le moment")

        else:

            # Grouper par priorité

            critiques = [n for n in notifs if n.priorite == "haute"]

            moyennes = [n for n in notifs if n.priorite == "moyenne"]

            basses = [n for n in notifs if n.priorite == "basse"]

            

            # Affiche les critiques

            if critiques:

                st.markdown("### 🚨 Alertes Critiques")

                for notif in critiques:

                    with st.container(border=True):

                        col1, col2 = st.columns([0.85, 0.15])

                        with col1:

                            st.write(f"**{notif.icone} {notif.titre}**")

                            st.write(notif.message)

                            st.caption(f"{'✨ Lue' if notif.lue else '📌 Non lue'} ê€✅ {notif.date_creation.strftime('%d/%m %H:%M')}")

                        with col2:

                            col_a, col_b = st.columns(2)

                            with col_a:

                                if st.button("êœ“", key=f"mark_{notif.id}", help="Marquer comme lu", use_container_width=True):

                                    service_notifs.marquer_lue(notif.id)

                                    st.rerun()

                            with col_b:

                                if st.button("êœ•", key=f"delete_{notif.id}", help="Supprimer", use_container_width=True):

                                    service_notifs.supprimer_notification(notif.id)

                                    st.rerun()

            

            # Affiche les moyennes

            if moyennes:

                st.markdown("### [!] Alertes Moyennes")

                for notif in moyennes:

                    with st.container(border=True):

                        col1, col2 = st.columns([0.85, 0.15])

                        with col1:

                            st.write(f"**{notif.icone} {notif.titre}**")

                            st.write(notif.message)

                            st.caption(f"{'✨ Lue' if notif.lue else '📌 Non lue'} ê€✅ {notif.date_creation.strftime('%d/%m %H:%M')}")

                        with col2:

                            col_a, col_b = st.columns(2)

                            with col_a:

                                if st.button("êœ“", key=f"mark_{notif.id}", help="Marquer comme lu", use_container_width=True):

                                    service_notifs.marquer_lue(notif.id)

                                    st.rerun()

                            with col_b:

                                if st.button("êœ•", key=f"delete_{notif.id}", help="Supprimer", use_container_width=True):

                                    service_notifs.supprimer_notification(notif.id)

                                    st.rerun()

            

            # Affiche les basses

            if basses:

                st.markdown("### ê„¹ï¸ Informations")

                for notif in basses[:5]:  # Limit to 5

                    with st.container(border=True):

                        col1, col2 = st.columns([0.85, 0.15])

                        with col1:

                            st.write(f"**{notif.icone} {notif.titre}**")

                            st.write(notif.message)

                            st.caption(f"{'✨ Lue' if notif.lue else '📌 Non lue'} ê€✅ {notif.date_creation.strftime('%d/%m %H:%M')}")

                        with col2:

                            col_a, col_b = st.columns(2)

                            with col_a:

                                if st.button("êœ“", key=f"mark_{notif.id}", help="Marquer comme lu", use_container_width=True):

                                    service_notifs.marquer_lue(notif.id)

                                    st.rerun()

                            with col_b:

                                if st.button("êœ•", key=f"delete_{notif.id}", help="Supprimer", use_container_width=True):

                                    service_notifs.supprimer_notification(notif.id)

                                    st.rerun()

                

                if len(basses) > 5:

                    st.caption(f"... et {len(basses) - 5} autres informations")

    

    with tab_config:

        st.write("**Configuration des notifications**")

        

        col1, col2 = st.columns(2)

        

        with col1:

            st.markdown("### ⏰ Alertes actives")

            enable_stock = st.checkbox("Stock critique", value=True, key="alert_stock_crit")

            enable_stock_bas = st.checkbox("Stock bas", value=True, key="alert_stock_bas")

            enable_peremption = st.checkbox("Péremption", value=True, key="alert_peremption")

        

        with col2:

            st.markdown("### [WATER] Canaux")

            browser_notif = st.checkbox("Notifications navigateur", value=True, help="Popup dans le navigateur")

            email_notif = st.checkbox("Email (bientôt)", value=False, disabled=True)

            slack_notif = st.checkbox("Slack (bientôt)", value=False, disabled=True)

        

        st.divider()

        

        # Bouton pour générer les alertes

        if st.button("🔄 Générer les alertes maintenant", use_container_width=True, type="primary"):

            try:

                stats = service.generer_notifications_alertes()

                

                col1, col2, col3, col4 = st.columns(4)

                with col1:

                    st.metric("❌ Critique", len(stats["stock_critique"]))

                with col2:

                    st.metric("  Bas", len(stats["stock_bas"]))

                with col3:

                    st.metric("⏰ Péremption", len(stats["peremption_proche"]))

                with col4:

                    st.metric("🚨 Expirés", len(stats["peremption_depassee"]))

                

                st.toast(f"✨ {sum(len(v) for v in stats.values())} alertes créées", icon="⏰")

            except Exception as e:

                st.error(f"Erreur: {str(e)}")





def render_tools():

    """Outils utilitaires pour l'inventaire"""

    st.subheader("📥 Outils d'administration")

    

    tab_import_export, tab_stats = st.tabs(["📅Ÿ“¤ Import/Export", "[CHART] Statistiques"])

    

    with tab_import_export:

        render_import_export()

    

    with tab_stats:

        service = get_inventaire_service()

        if service:

            try:

                inventaire = service.get_inventaire_complet()

                alertes = service.get_alertes()

                

                st.subheader("[CHART] Statistiques globales")

                

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

                st.subheader("📤 Répartition")

                

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





def render_import_export():

    """Gestion import/export avancée"""

    service = get_inventaire_service()

    

    st.subheader("📅Ÿ“¤ Import/Export Avancé")

    

    tab_import, tab_export = st.tabs(["📷 Importer", "🍽️ Exporter"])

    

    with tab_import:

        st.write("**Importer articles depuis fichier**")

        

        # Uploader fichier

        uploaded_file = st.file_uploader(

            "Sélectionne un fichier CSV ou Excel",

            type=["csv", "xlsx", "xls"],

            help="Format: Nom, Quantité, Unité, Seuil Min, Emplacement, Catégorie, Date Péremption"

        )

        

        if uploaded_file:

            try:

                import pandas as pd

                

                # Parse le fichier

                if uploaded_file.name.endswith(".csv"):

                    df = pd.read_csv(uploaded_file)

                else:

                    df = pd.read_excel(uploaded_file)

                

                st.write(f"**Fichier parsé:** {len(df)} lignes")

                

                # Affiche un aperçu

                st.dataframe(df.head(5), use_container_width=True)

                

                # Valide les données

                if st.button("✨ Valider & Importer", type="primary", use_container_width=True):

                    try:

                        # Convertit en format attendu

                        articles_list = df.to_dict("records")

                        

                        # Renomme colonnes si besoin

                        articles_list = [

                            {

                                "nom": row.get("Nom") or row.get("nom"),

                                "quantite": float(row.get("Quantité") or row.get("quantite") or 0),

                                "quantite_min": float(row.get("Seuil Min") or row.get("quantite_min") or 1),

                                "unite": row.get("Unité") or row.get("unite") or "pièce",

                                "emplacement": row.get("Emplacement") or row.get("emplacement"),

                                "categorie": row.get("Catégorie") or row.get("categorie"),

                                "date_peremption": row.get("Date Péremption") or row.get("date_peremption"),

                            }

                            for row in articles_list

                        ]

                        

                        # Valide

                        rapport = service.valider_fichier_import(articles_list)

                        

                        col1, col2, col3 = st.columns(3)

                        with col1:

                            st.metric("✨ Valides", rapport["valides"])

                        with col2:

                            st.metric("❌ Invalides", rapport["invalides"])

                        with col3:

                            if rapport["valides"] > 0:

                                pct = (rapport["valides"] / (rapport["valides"] + rapport["invalides"]) * 100) if (rapport["valides"] + rapport["invalides"]) > 0 else 0

                                st.metric("% OK", f"{pct:.0f}%")

                        

                        # Affiche les erreurs

                        if rapport["erreurs"]:

                            st.error("**Erreurs de validation:**")

                            for err in rapport["erreurs"][:5]:

                                st.caption(f"Ligne {err['ligne']}: {err['erreur']}")

                            if len(rapport["erreurs"]) > 5:

                                st.caption(f"... et {len(rapport['erreurs']) - 5} autres")

                        

                        # Confirme et importe

                        if rapport["valides"] > 0:

                            if st.button("🚀 Importer les articles valides", use_container_width=True):

                                resultats = service.importer_articles(articles_list)

                                

                                # Affiche résultats

                                success = [r for r in resultats if r["status"] == "✨"]

                                errors = [r for r in resultats if r["status"] == "❌"]

                                

                                st.success(f"✨ {len(success)}/{len(resultats)} articles importés!")

                                st.toast(f"Import complété: {len(success)} réussis", icon="✨")

                                

                                if errors:

                                    st.warning(f"[!] {len(errors)} articles avec erreurs")

                                    for err in errors[:3]:

                                        st.caption(f"ê€✅ {err['nom']}: {err['message']}")

                    

                    except Exception as e:

                        st.error(f"❌ Erreur import: {str(e)}")

            

            except Exception as e:

                st.error(f"❌ Erreur parsing fichier: {str(e)}")

    

    with tab_export:

        st.write("**Exporter l'inventaire**")

        

        col1, col2 = st.columns(2)

        

        with col1:

            if st.button("📷 Télécharger CSV", use_container_width=True):

                try:

                    csv_content = service.exporter_inventaire("csv")

                    st.download_button(

                        label="🎯 Télécharger CSV",

                        data=csv_content,

                        file_name="inventaire.csv",

                        mime="text/csv",

                    )

                    st.success("✨ CSV prêt à télécharger")

                except Exception as e:

                    st.error(f"❌ Erreur: {str(e)}")

        

        with col2:

            if st.button("📷 Télécharger JSON", use_container_width=True):

                try:

                    json_content = service.exporter_inventaire("json")

                    st.download_button(

                        label="🎯 Télécharger JSON",

                        data=json_content,

                        file_name="inventaire.json",

                        mime="application/json",

                    )

                    st.success("✨ JSON prêt à télécharger")

                except Exception as e:

                    st.error(f"❌ Erreur: {str(e)}")

        

        st.divider()

        

        # Info export

        articles = service.get_inventaire_complet()

        st.info(

            f"[CHART] **Statistiques export:**\n"

            f"ê€✅ **Articles:** {len(articles)}\n"

            f"ê€✅ **Stock total:** {sum(a['quantite'] for a in articles)}\n"

            f"ê€✅ **Date export:** Automatique"

        )





def render_predictions():

    """Affiche les prédictions et recommandations ML"""

    st.subheader("📱 Prévisions et Recommandations")

    

    try:

        service = get_inventaire_service()

        service_pred = obtenir_service_predictions()

        

        if service is None:

            st.error("❌ Service inventaire indisponible")

            return

        

        # Récupère les données

        articles = service.get_inventaire_complet()

        

        if not articles:

            st.info("Aucun article dans l'inventaire pour générer les prédictions")

            return

        

        # Bouton pour générer les prédictions

        col1, col2, col3 = st.columns([2, 1, 1])

        

        with col1:

            if st.button("🔄 Générer les prédictions", use_container_width=True, key="btn_generate_predictions"):

                st.session_state.predictions_generated = True

                st.session_state.predictions_data = None

        

        with col2:

            # Période de prédiction

            periode = st.selectbox(

                "Prédiction pour",

                ["1 semaine", "1 mois", "3 mois"],

                key="prediction_period"

            )

        

        with col3:

            st.metric("🚀 Articles", len(articles))

        

        st.divider()

        

        # Affiche les prédictions si générées

        if st.session_state.get("predictions_generated", False):

            with st.spinner("ê³ Génération des prédictions ML..."):

                try:

                    predictions = service_pred.generer_predictions()

                    analyse_globale = service_pred.obtenir_analyse_globale()

                    recommandations = service_pred.generer_recommandations()

                    

                    st.session_state.predictions_data = {

                        "predictions": predictions,

                        "analyse": analyse_globale,

                        "recommandations": recommandations

                    }

                except Exception as e:

                    st.error(f"❌ Erreur lors de la génération: {str(e)}")

                    st.session_state.predictions_generated = False

                    return

        

        # Affiche les résultats

        if st.session_state.get("predictions_data"):

            data = st.session_state.predictions_data

            predictions = data["predictions"]

            analyse = data["analyse"]

            recommandations = data["recommandations"]

            

            # Tabs pour les différentes vues

            tab_pred, tab_tendances, tab_recom, tab_analyse = st.tabs([

                "[CHART] Prédictions",

                "📤 Tendances",

                "🔔 Recommandations",

                "📍Analyse globale"

            ])

            

            with tab_pred:

                st.write("**Prédictions pour tous les articles**")

                

                # Prépare le dataframe

                df_pred = []

                for pred in predictions:

                    df_pred.append({

                        "Article": pred.nom,

                        "Quantité actuelle": pred.quantite_actuelle,

                        "Prédite (1 mois)": f"{pred.quantite_predite:.1f}",

                        "Tendance": pred.tendance,

                        "Confiance": f"{pred.confiance:.0%}",

                        "Risque rupture": "❌ OUI" if pred.risque_rupture else "✅ Non",

                        "Jours avant rupture": pred.jours_avant_rupture if pred.jours_avant_rupture else "-"

                    })

                

                df_display = pd.DataFrame(df_pred)

                st.dataframe(df_display, use_container_width=True, hide_index=True)

                

                st.divider()

                

                # Filtres et détails

                col1, col2, col3 = st.columns(3)

                

                with col1:

                    filter_trend = st.multiselect(

                        "Filtrer par tendance",

                        ["croissante", "décroissante", "stable"],

                        default=["croissante", "décroissante", "stable"],

                        key="filter_trend_pred"

                    )

                

                with col2:

                    filter_risk = st.checkbox("Afficher seulement les articles à risque", key="filter_risk_pred")

                

                with col3:

                    min_confiance = st.slider("Confiance minimale", 0, 100, 0, key="min_confiance_pred")

                

                # Filtre et affiche les détails

                filtered_pred = [

                    p for p in predictions 

                    if p.tendance in filter_trend 

                    and (not filter_risk or p.risque_rupture)

                    and (p.confiance * 100 >= min_confiance)

                ]

                

                if filtered_pred:

                    st.write(f"**{len(filtered_pred)} article(s) correspondent aux filtres**")

                    for pred in filtered_pred[:5]:  # Affiche les 5 premiers

                        with st.expander(f"💡 {pred.nom} - {pred.tendance.upper()}"):

                            col1, col2, col3 = st.columns(3)

                            

                            with col1:

                                st.metric("Quantité actuelle", f"{pred.quantite_actuelle:.1f} {pred.unite}")

                                st.metric("Prédite (1 mois)", f"{pred.quantite_predite:.1f}")

                            

                            with col2:

                                st.metric("Consommation/jour", f"{pred.consommation_moyenne:.2f}")

                                st.metric("Confiance", f"{pred.confiance:.0%}")

                            

                            with col3:

                                if pred.risque_rupture:

                                    st.metric("[!] Rupture dans", f"{pred.jours_avant_rupture} j")

                                    st.warning(f"Stock insuffisant dans {pred.jours_avant_rupture} jours!")

                                else:

                                    st.metric("Stock", "✨ Sûr")

                                    st.success(f"Suffisant pour {pred.jours_avant_rupture} jours")

            

            with tab_tendances:

                st.write("**Tendances de consommation**")

                

                # Groupe par tendance

                tendances = {"croissante": [], "décroissante": [], "stable": []}

                for pred in predictions:

                    tendances[pred.tendance].append(pred)

                

                col1, col2, col3 = st.columns(3)

                

                with col1:

                    st.metric("📤 Croissante", len(tendances["croissante"]))

                    if tendances["croissante"]:

                        with st.expander("Voir les articles"):

                            for p in tendances["croissante"]:

                                st.write(f"ê€✅ {p.nom} (+{p.consommation_moyenne:.2f}/jour)")

                

                with col2:

                    st.metric("🎨 Décroissante", len(tendances["décroissante"]))

                    if tendances["décroissante"]:

                        with st.expander("Voir les articles"):

                            for p in tendances["décroissante"]:

                                st.write(f"ê€✅ {p.nom} ({p.consommation_moyenne:.2f}/jour)")

                

                with col3:

                    st.metric("êž¡ï¸ Stable", len(tendances["stable"]))

                    if tendances["stable"]:

                        with st.expander("Voir les articles"):

                            for p in tendances["stable"]:

                                st.write(f"ê€✅ {p.nom} (~{p.consommation_moyenne:.2f}/jour)")

                

                st.divider()

                

                # Chart des tendances

                if predictions:

                    chart_data = {

                        "Article": [p.nom[:15] for p in predictions[:10]],

                        "Consommation/jour": [p.consommation_moyenne for p in predictions[:10]]

                    }

                    chart_df = pd.DataFrame(chart_data)

                    st.bar_chart(chart_df.set_index("Article"), use_container_width=True)

            

            with tab_recom:

                st.write("**Recommandations d'achat prioritaires**")

                

                if recommandations:

                    # Groupe par priorité

                    by_priority = {}

                    for rec in recommandations:

                        p = rec.priorite

                        if p not in by_priority:

                            by_priority[p] = []

                        by_priority[p].append(rec)

                    

                    # Affiche par priorité

                    for priority in ["CRITIQUE", "HAUTE", "MOYENNE"]:

                        if priority in by_priority:

                            icon = "❌" if priority == "CRITIQUE" else " " if priority == "HAUTE" else "¡"

                            count = len(by_priority[priority])

                            

                            with st.expander(f"{icon} {priority} ({count})", expanded=(priority=="CRITIQUE")):

                                for rec in by_priority[priority]:

                                    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])

                                    

                                    with col1:

                                        st.write(f"**{rec.nom}**")

                                        st.caption(rec.raison)

                                    

                                    with col2:

                                        st.metric("Quantité", f"{rec.quantite_recommandee:.0f} {rec.unite}")

                                    

                                    with col3:

                                        st.metric("Stock actuel", f"{rec.quantite_actuelle:.0f}")

                                    

                                    with col4:

                                        if st.button("✨ Ajouter", key=f"add_rec_{rec.nom}", use_container_width=True):

                                            st.toast(f"✨ {rec.nom} ajouté", icon="👶")

                else:

                    st.info("Aucune recommandation d'achat pour le moment")

            

            with tab_analyse:

                st.write("**Analyse globale de l'inventaire**")

                

                col1, col2, col3, col4 = st.columns(4)

                

                with col1:

                    st.metric("[CHART] Total articles", len(predictions))

                

                with col2:

                    articles_risque = len([p for p in predictions if p.risque_rupture])

                    st.metric("❌ En risque", articles_risque)

                

                with col3:

                    articles_croissance = len([p for p in predictions if p.tendance == "croissante"])

                    st.metric("📤 Croissance", articles_croissance)

                

                with col4:

                    confiance_moy = sum(p.confiance for p in predictions) / len(predictions) if predictions else 0

                    st.metric("🎯 Confiance moy", f"{confiance_moy:.0%}")

                

                st.divider()

                

                # Résumé de l'analyse

                if analyse:

                    st.write("**Tendance générale**: ", end="")

                    if analyse.tendance_globale == "croissante":

                        st.write("📤 **Consommation en augmentation**")

                        st.info("La consommation générale augmente. Préparez-vous à augmenter vos achats.")

                    elif analyse.tendance_globale == "décroissante":

                        st.write("🎨 **Consommation en diminution**")

                        st.info("La consommation générale diminue. Vous pouvez réduire légèrement vos achats.")

                    else:

                        st.write("êž¡ï¸ **Consommation stable**")

                        st.info("La consommation est stable. Maintenez votre rythme d'achat actuel.")

                    

                    st.divider()

                    

                    # Stats détaillées

                    col1, col2 = st.columns(2)

                    

                    with col1:

                        st.write("**Consommation quotidienne moyenne**")

                        st.metric("Total", f"{analyse.consommation_moyenne_globale:.2f} unités/jour")

                        st.metric("Min", f"{analyse.consommation_min:.2f}")

                        st.metric("Max", f"{analyse.consommation_max:.2f}")

                    

                    with col2:

                        st.write("**Distribution des articles**")

                        st.metric("Croissants", f"{analyse.nb_articles_croissance}")

                        st.metric("Décroissants", f"{analyse.nb_articles_decroissance}")

                        st.metric("Stables", f"{analyse.nb_articles_stables}")

    

    except Exception as e:

        st.error(f"❌ Erreur: {str(e)}")

        import traceback

        st.text(traceback.format_exc())





# ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•

# HELPERS

# ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•



def _prepare_inventory_dataframe(inventaire: list[dict[str, Any]]) -> pd.DataFrame:

    """Prépare un DataFrame pour affichage inventaire"""

    data = []

    for article in inventaire:

        statut_icon = {

            "critique": "❌",

            "stock_bas": " ",

            "peremption_proche": "⏰",

            "ok": "✅"

        }.get(article["statut"], "ê“")

        

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

            "critique": "❌",

            "stock_bas": " ",

            "peremption_proche": "⏰",

        }.get(article["statut"], "ê“")

        

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



def render_historique():

    """Affiche l'historique des modifications de l'inventaire"""

    service = get_inventaire_service()

    

    if service is None:

        st.error("❌ Service inventaire indisponible")

        return

    

    st.subheader("💰 Historique des Modifications")

    

    # Filtres

    col1, col2, col3 = st.columns(3)

    

    with col1:

        days = st.slider("Période (jours)", 1, 90, 30)

    

    with col2:

        article_id = st.selectbox(

            "Article (optionnel)",

            options=["Tous"] + [f"Article #{i}" for i in range(1, 20)],

            index=0

        )

    

    with col3:

        type_modif = st.multiselect(

            "Type modification",

            options=["ajout", "modification", "suppression"],

            default=["ajout", "modification", "suppression"]

        )

    

    # Récupérer historique

    try:

        historique = service.get_historique(days=days)

        

        if not historique:

            st.info("📋 Aucune modification enregistrée dans cette période")

            return

        

        # Filtrer par type

        historique_filtres = [

            h for h in historique 

            if h["type"] in type_modif

        ]

        

        if not historique_filtres:

            st.info("Aucune modification ne correspond aux filtres")

            return

        

        # Afficher tableau

        data = []

        for h in historique_filtres:

            action_icon = {

                "ajout": "➕",

                "modification": "êœï¸",

                "suppression": "🧹¸"

            }.get(h["type"], "ê“")

            

            # Résumer les changements

            changements = []

            if h["quantite_avant"] is not None:

                changements.append(f"Qty: {h['quantite_avant']:.1f} ê†’ {h['quantite_apres']:.1f}")

            if h["emplacement_avant"] is not None:

                changements.append(f"Empl: {h['emplacement_avant']} ê†’ {h['emplacement_apres']}")

            if h["date_peremption_avant"] is not None:

                changements.append(f"Péremption: {h['date_peremption_avant']} ê†’ {h['date_peremption_apres']}")

            

            changement_text = " | ".join(changements) if changements else "Détails disponibles"

            

            data.append({

                "Date": pd.Timestamp(h["date_modification"]).strftime("%d/%m/%Y %H:%M"),

                "Article": h["ingredient_nom"],

                "Action": f"{action_icon} {h['type']}",

                "Changements": changement_text,

            })

        

        df = pd.DataFrame(data)

        st.dataframe(df, use_container_width=True, hide_index=True)

        

        st.divider()

        

        # Stats

        col1, col2, col3 = st.columns(3)

        with col1:

            st.metric("Total modifications", len(historique_filtres))

        with col2:

            ajouts = len([h for h in historique_filtres if h["type"] == "ajout"])

            st.metric("Ajouts", ajouts)

        with col3:

            modifs = len([h for h in historique_filtres if h["type"] == "modification"])

            st.metric("Modifications", modifs)

    

    except Exception as e:

        st.error(f"❌ Erreur: {str(e)}")



