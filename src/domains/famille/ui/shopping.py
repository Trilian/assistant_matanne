"""
Module Shopping - Listes de courses intelligentes avec budget tracking

Features:
- Listes de courses (Jules, Nous, Autres)
- Suggestions intelligentes (basées sur activités & milestones)
- Budget par catégorie (Plotly bonus graphique)
- Intégration avec Courses module
"""

import streamlit as st
from datetime import date, timedelta
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

from src.core.database import get_db
from src.core.models import FamilyActivity, FamilyBudget, ShoppingItem

# Logique métier pure
from src.domains.famille.logic.shopping_logic import (
    calculer_cout_liste,
    calculer_budget_mensuel,
    calculer_statistiques_shopping,
    suggerer_budget_optimal,
    detecter_articles_recurrents,
    valider_article_shopping
)

from src.domains.famille.logic.helpers import (
    get_activites_semaine,
    get_budget_par_period,
    clear_famille_cache
)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# HELPER FUNCTIONS
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

@st.cache_data(ttl=1800)
def get_shopping_items(categorie=None):
    """Récupère les articles du shopping"""
    try:
        with get_db() as db:
            query = db.query(ShoppingItem).filter(ShoppingItem.actif == True)
            
            if categorie:
                query = query.filter(ShoppingItem.categorie == categorie)
            
            items = query.all()
            return items
    except Exception as e:
        st.error(f"âŒ Erreur récupération shopping: {e}")
        return []


@st.cache_data(ttl=1800)
def get_shopping_suggestions():
    """Suggestions intelligentes basées sur activités & milestones"""
    try:
        suggestions = {
            "Jules": {
                "jouets": ["Blocs de construction", "Livre bébé", "Jouet musical", "Poupée", "Voiture bois"],
                "vêtements": ["T-shirt 18-24m", "Legging", "Chaussettes", "Pull", "Bonnet"],
                "hygiène": ["Couches Taille 5", "Lingettes", "Savon bébé", "Crème change", "Brosse dent"]
            },
            "Nous": {
                "épicerie": ["Riz", "PÃ¢tes", "Oeuf", "Pain", "Lait", "Fromage"],
                "fruits_légumes": ["Pommes", "Carottes", "Tomates", "Oignons", "Bananes"],
                "hygiène": ["Savon mains", "Dentifrice", "Shampoing", "Gel douche"],
                "autre": ["Café", "Thé", "Huile olive", "Sel", "Sucre"]
            },
            "Activités": {
                "picnic": ["Serviettes", "Gobelets réutilisables", "Sacs glacés", "Nappe"],
                "parc": ["Ballon", "Bubbles", "Frisbee", "Sacs poubelle"],
                "sport": ["Bouteille eau", "Gourde", "Brassard sport", "Chaussettes sport"]
            }
        }
        
        return suggestions
    except Exception as e:
        st.error(f"âŒ Erreur suggestions: {e}")
        return {}


def ajouter_article(titre, categorie, qty=1, prix_estime=0.0, liste="Nous"):
    """Ajoute un article au shopping"""
    try:
        with get_db() as db:
            item = ShoppingItem(
                titre=titre,
                categorie=categorie,
                quantite=qty,
                prix_estime=prix_estime,
                liste=liste,
                date_ajout=date.today(),
                actif=True
            )
            
            db.add(item)
            db.commit()
        
        clear_famille_cache()
        st.success(f"âœ… {titre} ajouté à {liste}")
        return True
    except Exception as e:
        st.error(f"âŒ Erreur ajout article: {e}")
        return False


def marquer_achete(item_id):
    """Marque un article comme acheté"""
    try:
        with get_db() as db:
            item = db.query(ShoppingItem).get(item_id)
            
            if item:
                item.actif = False
                item.date_achat = date.today()
                if item.prix_reel is None:
                    item.prix_reel = item.prix_estime
                
                db.commit()
                clear_famille_cache()
                return True
        return False
    except Exception as e:
        st.error(f"âŒ Erreur marquer acheté: {e}")
        return False


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# STREAMLIT APP
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

def app():
    st.set_page_config(page_title="Shopping", page_icon="ðŸ›’", layout="wide")
    st.title("ðŸ›’ Listes de Courses")
    
    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "ðŸ“‹ Ma Liste",
        "ðŸ’¡ Suggestions",
        "ðŸ’° Budget",
        "ðŸ“Š Analytics"
    ])
    
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    # TAB 1: MA LISTE
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    
    with tab1:
        st.subheader("Mes articles à acheter")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            listes = ["Nous", "Jules", "Activités"]
            liste_selectionnee = st.selectbox("Sélectionner liste:", listes)
        
        with col2:
            if st.button("ðŸ”„ Rafraîchir", use_container_width=True):
                clear_famille_cache()
                st.rerun()
        
        # Ajouter article
        st.markdown("### âž• Ajouter article")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            titre = st.text_input("Article:", key="add_titre")
        with col2:
            categorie = st.selectbox(
                "Catégorie:",
                ["épicerie", "fruits_légumes", "hygiène", "jouets", "vêtements", "autre"],
                key="add_cat"
            )
        with col3:
            qty = st.number_input("Quantité:", min_value=1, value=1)
        with col4:
            prix = st.number_input("Prix (â‚¬):", min_value=0.0, value=0.0, step=0.50)
        
        if st.button("âœ… Ajouter", use_container_width=True):
            if titre:
                ajouter_article(titre, categorie, qty, prix, liste_selectionnee)
            else:
                st.error("âŒ Entrez un article")
        
        st.divider()
        
        # Afficher articles
        st.markdown("### ðŸ“‹ Articles à acheter")
        
        articles = get_shopping_items(categorie=None)
        articles_liste = [a for a in articles if a.liste == liste_selectionnee and a.actif]
        
        if articles_liste:
            # Grouper par catégorie
            categories_dict = {}
            for article in articles_liste:
                if article.categorie not in categories_dict:
                    categories_dict[article.categorie] = []
                categories_dict[article.categorie].append(article)
            
            for categorie, items in sorted(categories_dict.items()):
                with st.expander(f"**{categorie.upper()}** ({len(items)} articles)", expanded=True):
                    cols = st.columns([3, 1, 1, 1])
                    
                    for item in items:
                        col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                        
                        with col1:
                            st.write(f"â€¢ **{item.titre}** Ã— {item.quantite}")
                            if item.prix_estime > 0:
                                st.caption(f"~{item.prix_estime:.2f}â‚¬")
                        
                        with col2:
                            st.write("")
                        
                        with col3:
                            st.write("")
                        
                        with col4:
                            if st.button("âœ“", key=f"buy_{item.id}", use_container_width=True):
                                marquer_achete(item.id)
                                st.rerun()
            
            # Total estimé
            total_estime = sum(a.prix_estime * a.quantite for a in articles_liste)
            st.markdown(f"### ðŸ’° Total estimé: **{total_estime:.2f}â‚¬**")
        
        else:
            st.info("âœ¨ Aucun article à acheter!")
    
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    # TAB 2: SUGGESTIONS
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    
    with tab2:
        st.subheader("ðŸ’¡ Suggestions intelligentes")
        
        suggestions = get_shopping_suggestions()
        
        # Afficher suggestions par catégorie
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("### ðŸ‘¶ Pour Jules (19m)")
            for cat, items in suggestions.get("Jules", {}).items():
                with st.expander(f"**{cat.title()}**"):
                    for item in items:
                        if st.button(f"âž• {item}", key=f"suggest_jules_{item}"):
                            ajouter_article(item, cat, 1, 0, "Jules")
                            st.rerun()
        
        with col2:
            st.markdown("### ðŸ‘¨â€ðŸ‘©â€ðŸ‘¦ Pour Nous")
            for cat, items in suggestions.get("Nous", {}).items():
                with st.expander(f"**{cat.title()}**"):
                    for item in items:
                        if st.button(f"âž• {item}", key=f"suggest_nous_{item}"):
                            ajouter_article(item, cat, 1, 0, "Nous")
                            st.rerun()
        
        with col3:
            st.markdown("### ðŸŽª Pour Activités")
            for cat, items in suggestions.get("Activités", {}).items():
                with st.expander(f"**{cat.title()}**"):
                    for item in items:
                        if st.button(f"âž• {item}", key=f"suggest_act_{item}"):
                            ajouter_article(item, cat, 1, 0, "Activités")
                            st.rerun()
        
        # Suggestions basées sur activités cette semaine
        st.divider()
        st.markdown("### ðŸ“… Basé sur activités cette semaine")
        
        try:
            activites = get_activites_semaine()
            if activites:
                activites_texte = ", ".join([f"**{a['titre']}**" if isinstance(a, dict) else f"**{a.titre}**" for a in activites[:3]])
                st.info(f"ðŸŽ¯ Vous avez prévu: {activites_texte}")
                
                # Suggestions contextées
                for activity in activites[:2]:
                    activity_type = activity.get('type') if isinstance(activity, dict) else activity.type_activite
                    if activity_type == "picnic":
                        st.write("ðŸ§º **Pour pique-nique**: Serviettes, gobelets, sacs glacés")
                    elif activity_type == "parc":
                        st.write("âš½ **Pour parc**: Ballon, bubbles, frisbee")
                    elif activity_type == "sport":
                        st.write("ðŸƒ **Pour sport**: Bouteille eau, gourde, vêtements")
            else:
                st.info("â„¹ï¸ Aucune activité prévue cette semaine")
        except Exception as e:
            st.warning(f"âš ï¸ {e}")
    
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    # TAB 3: BUDGET
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    
    with tab3:
        st.subheader("ðŸ’° Budget Shopping")
        
        # Sélectionner période
        col1, col2 = st.columns(2)
        
        with col1:
            periode = st.selectbox("Période:", ["Cette semaine", "Ce mois", "Ce trimestre"])
            if periode == "Cette semaine":
                days = 7
            elif periode == "Ce mois":
                days = 30
            else:
                days = 90
        
        with col2:
            refresh = st.checkbox("Mise à jour en temps réel")
        
        st.divider()
        
        # Récupérer budget par période
        try:
            budget_data = get_budget_par_period(days)
            
            if budget_data and budget_data.get("TOTAL", 0) > 0:
                # Exclure TOTAL du dataframe
                budget_dict = {k: v for k, v in budget_data.items() if k != "TOTAL"}
                
                df_categorie = pd.DataFrame([
                    {"Catégorie": cat, "Montant": montant}
                    for cat, montant in budget_dict.items()
                ])
                df_categorie = df_categorie.sort_values("Montant", ascending=False)
                
                # Plotly: Budget par catégorie
                fig_cat = px.bar(
                    df_categorie,
                    x="Catégorie",
                    y="Montant",
                    color="Montant",
                    color_continuous_scale="Viridis",
                    title=f"Budget Shopping par Catégorie ({periode})"
                )
                fig_cat.update_layout(
                    hovermode="x unified",
                    height=400,
                    showlegend=False
                )
                st.plotly_chart(fig_cat, use_container_width=True)
                
                # Métriques
                col1, col2, col3 = st.columns(3)
                with col1:
                    total = budget_data.get("TOTAL", 0)
                    st.metric("ðŸ’° Total dépensé", f"{total:.2f}â‚¬")
                
                with col2:
                    avg = df_categorie["Montant"].mean()
                    st.metric("ðŸ“Š Moyenne/catégorie", f"{avg:.2f}â‚¬")
                
                with col3:
                    if len(df_categorie) > 0:
                        top_cat = df_categorie.iloc[0]["Catégorie"]
                        st.metric("ðŸ” Top catégorie", top_cat)
                
                # Tableau détail
                st.markdown("### ðŸ“‹ Détail par catégorie")
                st.dataframe(df_categorie, use_container_width=True)
            
            else:
                st.info("â„¹ï¸ Aucune dépense enregistrée")
        
        except Exception as e:
            st.error(f"âŒ Erreur budget: {e}")
    
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    # TAB 4: ANALYTICS
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    
    with tab4:
        st.subheader("ðŸ“Š Analytics Shopping")
        
        try:
            # Récupérer tous les articles achetés ce mois
            with get_db() as db:
                items_achetes = db.query(ShoppingItem).filter(
                    ShoppingItem.date_achat >= date.today() - timedelta(days=30),
                    ShoppingItem.actif == False
                ).all()
                
                if items_achetes:
                    df_achetes = pd.DataFrame([
                        {
                            "Article": i.titre,
                            "Catégorie": i.categorie,
                            "Quantité": i.quantite,
                            "Estimé": i.prix_estime * i.quantite,
                            "Réel": (i.prix_reel or i.prix_estime) * i.quantite,
                            "Date": i.date_achat
                        }
                        for i in items_achetes
                    ])
                    
                    # Plotly: Différence Estimé vs Réel
                    df_cat = df_achetes.groupby("Catégorie").agg({
                        "Estimé": "sum",
                        "Réel": "sum"
                    }).reset_index()
                    
                    fig = go.Figure(data=[
                        go.Bar(name="Estimé", x=df_cat["Catégorie"], y=df_cat["Estimé"], marker_color="lightblue"),
                        go.Bar(name="Réel", x=df_cat["Catégorie"], y=df_cat["Réel"], marker_color="lightcoral")
                    ])
                    
                    fig.update_layout(
                        barmode="group",
                        title="Estimé vs Réel (30 jours)",
                        height=400,
                        hovermode="x unified"
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Stats
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        diff = (df_achetes["Réel"].sum() - df_achetes["Estimé"].sum())
                        st.metric("ðŸ’¨ Différence", f"{diff:+.2f}â‚¬", delta=f"{diff/df_achetes['Estimé'].sum()*100:.1f}%")
                    
                    with col2:
                        st.metric("ðŸ“¦ Articles achetés", len(items_achetes))
                    
                    with col3:
                        precision = ((df_achetes["Estimé"].sum() - abs(diff)) / df_achetes["Estimé"].sum() * 100)
                        st.metric("ðŸŽ¯ Précision estimé", f"{precision:.1f}%")
                
                else:
                    st.info("â„¹ï¸ Aucun article acheté ce mois")
        
        except Exception as e:
            st.error(f"âŒ Erreur analytics: {e}")


if __name__ == "__main__":
    main()

