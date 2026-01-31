"""
Module Activités - Planning et budget des activités familiales
Version améliorée avec helpers, caching, graphiques et Plotly
"""

import streamlit as st
from datetime import date, timedelta
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

from src.core.database import get_session
from src.core.models import FamilyActivity

# Logique métier pure
from src.domains.famille.logic.helpers import (
    get_activites_semaine,
    get_budget_activites_mois,
    get_budget_par_period,
    clear_famille_cache
)


def ajouter_activite(titre: str, type_activite: str, date_prevue: date, 
                     duree: float, lieu: str, participants: list, 
                     cout_estime: float, notes: str = ""):
    """Ajoute une nouvelle activité familiale"""
    try:
        with get_session() as session:
            activity = FamilyActivity(
                titre=titre,
                type_activite=type_activite,
                date_prevue=date_prevue,
                duree_heures=duree,
                lieu=lieu,
                qui_participe=participants,
                cout_estime=cout_estime,
                statut="planifié",
                notes=notes
            )
            session.add(activity)
            session.commit()
            st.success(f"✅ Activité '{titre}' créée!")
            clear_famille_cache()
            return True
    except Exception as e:
        st.error(f"❌ Erreur ajout activité: {str(e)}")
        return False


def marquer_terminee(activity_id: int, cout_reel: float = None, notes: str = ""):
    """Marque une activité comme terminée"""
    try:
        with get_session() as session:
            activity = session.get(FamilyActivity, activity_id)
            if activity:
                activity.statut = "terminé"
                if cout_reel is not None:
                    activity.cout_reel = cout_reel
                session.commit()
                st.success("✅ Activité marquée comme terminée!")
                clear_famille_cache()
                return True
    except Exception as e:
        st.error(f"❌ Erreur mise à jour: {str(e)}")
        return False


SUGGESTIONS_ACTIVITES = {
    "parc": ["Parc local", "Parc d'attractions (mini)", "Terrain de jeu"],
    "musée": ["Musée enfants", "Exposition interactive", "Aquarium"],
    "eau": ["Piscine", "Plage", "Parc aquatique bébé"],
    "jeu_maison": ["Jeux intérieurs", "Chasse au trésor", "Soirée jeux de société"],
    "sport": ["Cours de gym douce", "Équitation enfant", "Skating"],
    "sortie": ["Restaurant enfant-friendly", "Cinéma familial", "Zoo"]
}


def app():
    """Interface principale du module Activités"""
    st.title("🎨 Activités Familiales")
    
    tabs = st.tabs(["📱 Planning Semaine", "👶 Idées Activités", "💡 Budget"])
    
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    # TAB 1: PLANNING SEMAINE
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    with tabs[0]:
        st.header("📱 Planning de la Semaine")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("Activités Prévues")
            
            try:
                activites = get_activites_semaine()
                
                if activites:
                    # Trier par date
                    activites_sorted = sorted(activites, key=lambda x: x['date'])
                    
                    for act in activites_sorted:
                        with st.container(border=True):
                            col_date, col_info = st.columns([1, 3])
                            
                            with col_date:
                                jour = act['date'].strftime('%a')
                                jour_num = act['date'].strftime('%d')
                                st.write(f"**{jour}**")
                                st.write(f"*{jour_num}*")
                            
                            with col_info:
                                st.write(f"**{act['titre']}**")
                                st.caption(f"{act['type']} • {act.get('lieu', 'TBD')}")
                                if act.get('participants'):
                                    st.caption(f"📅 {', '.join(act['participants'])}")
                                st.caption(f"💡 {act.get('cout_estime', 0):.2f}€")
                else:
                    st.info("Aucune activité cette semaine. Planifiez une activité!")
            
            except Exception as e:
                st.error(f"❌ Erreur chargement: {str(e)}")
        
        with col2:
            st.subheader("➕ Ajouter Activité")
            
            with st.form("form_activite"):
                titre = st.text_input("Nom")
                type_act = st.selectbox("Type", 
                    ["parc", "musée", "eau", "jeu_maison", "sport", "sortie"])
                date_act = st.date_input("Date")
                duree = st.number_input("Durée (h)", 0.5, 8.0, 2.0)
                lieu = st.text_input("Lieu")
                cout = st.number_input("Coût estimé (€)", 0.0, 500.0, 0.0)
                
                if st.form_submit_button("✅ Ajouter", use_container_width=True):
                    if titre and type_act:
                        ajouter_activite(titre, type_act, date_act, duree, lieu, 
                                       ["Famille"], cout)
    
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    # TAB 2: IDÉES ACTIVITÉS
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    with tabs[1]:
        st.header("👶 Idées d'Activités")
        
        st.subheader("Suggestions par type")
        
        col1, col2, col3 = st.columns(3)
        
        cols = [col1, col2, col3]
        type_keys = list(SUGGESTIONS_ACTIVITES.keys())
        
        for i, type_key in enumerate(type_keys[:3]):
            with cols[i]:
                emoji = "💰" if type_key == "parc" else "🧹" if type_key == "musée" else "📋" if type_key == "eau" else "🎯" if type_key == "jeu_maison" else "⚽" if type_key == "sport" else "🍽️"
                title = type_key.replace("_", " ").title()
                
                st.subheader(f"{emoji} {title}")
                for suggestion in SUGGESTIONS_ACTIVITES[type_key]:
                    if st.button(suggestion, key=f"suggest_{type_key}_{suggestion}", 
                               use_container_width=True):
                        st.session_state.suggestion = suggestion
        
        col4, col5, col6 = st.columns(3)
        cols2 = [col4, col5, col6]
        
        for i, type_key in enumerate(type_keys[3:]):
            with cols2[i]:
                emoji = "💰" if type_key == "parc" else "🧹" if type_key == "musée" else "📋" if type_key == "eau" else "🎯" if type_key == "jeu_maison" else "⚽" if type_key == "sport" else "🍽️"
                title = type_key.replace("_", " ").title()
                
                st.subheader(f"{emoji} {title}")
                for suggestion in SUGGESTIONS_ACTIVITES[type_key]:
                    if st.button(suggestion, key=f"suggest_{type_key}_{suggestion}", 
                               use_container_width=True):
                        st.session_state.suggestion = suggestion
    
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    # TAB 3: BUDGET
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    with tabs[2]:
        st.header("💡 Budget Activités")
        
        # Stats
        col1, col2, col3 = st.columns(3)
        
        try:
            budget_mois = get_budget_activites_mois()
            budget_semaine = get_budget_par_period("week").get("Activités", 0)
            
            with col1:
                st.metric("💡 Ce mois", f"{budget_mois:.2f}€")
            with col2:
                st.metric("📊 Cette semaine", f"{budget_semaine:.2f}€")
            with col3:
                st.metric("🗑️ Budget moyen", f"{budget_mois / 4:.2f}€ par semaine")
        
        except Exception as e:
            st.error(f"❌ Erreur budget: {str(e)}")
        
        st.divider()
        
        # Graphique timeline
        st.subheader("🗑️ Graphique Dépenses")
        
        try:
            with get_session() as session:
                # Récupérer les 30 derniers jours
                debut = date.today() - timedelta(days=30)
                activites = session.query(FamilyActivity).filter(
                    FamilyActivity.date_prevue >= debut
                ).all()
                
                if activites:
                    # Créer DataFrame
                    data = []
                    for act in activites:
                        data.append({
                            "date": act.date_prevue,
                            "titre": act.titre,
                            "cout_estime": act.cout_estime or 0,
                            "cout_reel": act.cout_reel or 0,
                            "type": act.type_activite
                        })
                    
                    df = pd.DataFrame(data)
                    df["date"] = pd.to_datetime(df["date"])
                    
                    # Graphique 1: Timeline
                    fig1 = go.Figure()
                    fig1.add_trace(go.Scatter(
                        x=df["date"],
                        y=df["cout_estime"],
                        mode="lines+markers",
                        name="Coût estimé",
                        line_color="blue"
                    ))
                    fig1.add_trace(go.Scatter(
                        x=df["date"],
                        y=df["cout_reel"],
                        mode="lines+markers",
                        name="Coût réel",
                        line_color="red"
                    ))
                    
                    fig1.update_layout(
                        title="Dépenses par Date",
                        xaxis_title="Date",
                        yaxis_title="Montant (€)",
                        height=400,
                        hovermode="x unified"
                    )
                    st.plotly_chart(fig1, use_container_width=True)
                    
                    # Graphique 2: Par type d'activité
                    type_budget = df.groupby("type")["cout_estime"].sum().reset_index()
                    type_budget.columns = ["Type", "Budget"]
                    
                    fig2 = go.Figure(data=[
                        go.Bar(x=type_budget["Type"], y=type_budget["Budget"],
                               marker_color="lightblue")
                    ])
                    fig2.update_layout(
                        title="Budget par Type d'Activité",
                        xaxis_title="Type",
                        yaxis_title="Budget (€)",
                        height=400
                    )
                    st.plotly_chart(fig2, use_container_width=True)
                else:
                    st.info("Aucune activité sur 30 jours")
        
        except Exception as e:
            st.error(f"❌ Erreur graphiques: {str(e)}")


if __name__ == "__main__":
    main()

