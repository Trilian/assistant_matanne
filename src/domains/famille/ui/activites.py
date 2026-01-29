"""
Module ActivitÃ©s - Planning et budget des activitÃ©s familiales
Version amÃ©liorÃ©e avec helpers, caching, graphiques et Plotly
"""

import streamlit as st
from datetime import date, timedelta
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

from src.core.database import get_session
from src.core.models import FamilyActivity

# Logique mÃ©tier pure
from src.domains.famille.logic.activites_logic import (
    calculer_budget_activite,
    suggerer_activites_par_age
)

from src.domains.famille.logic.helpers import (
    get_activites_semaine,
    get_budget_activites_mois,
    get_budget_par_period,
    clear_famille_cache
)


def ajouter_activite(titre: str, type_activite: str, date_prevue: date, 
                     duree: float, lieu: str, participants: list, 
                     cout_estime: float, notes: str = ""):
    """Ajoute une nouvelle activitÃ© familiale"""
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
                statut="planifiÃ©",
                notes=notes
            )
            session.add(activity)
            session.commit()
            st.success(f"âœ… ActivitÃ© '{titre}' crÃ©Ã©e!")
            clear_famille_cache()
            return True
    except Exception as e:
        st.error(f"âŒ Erreur ajout activitÃ©: {str(e)}")
        return False


def marquer_terminee(activity_id: int, cout_reel: float = None, notes: str = ""):
    """Marque une activitÃ© comme terminÃ©e"""
    try:
        with get_session() as session:
            activity = session.get(FamilyActivity, activity_id)
            if activity:
                activity.statut = "terminÃ©"
                if cout_reel is not None:
                    activity.cout_reel = cout_reel
                session.commit()
                st.success("âœ… ActivitÃ© marquÃ©e comme terminÃ©e!")
                clear_famille_cache()
                return True
    except Exception as e:
        st.error(f"âŒ Erreur mise Ã  jour: {str(e)}")
        return False


SUGGESTIONS_ACTIVITES = {
    "parc": ["Parc local", "Parc d'attractions (mini)", "Terrain de jeu"],
    "musÃ©e": ["MusÃ©e enfants", "Exposition interactive", "Aquarium"],
    "eau": ["Piscine", "Plage", "Parc aquatique bÃ©bÃ©"],
    "jeu_maison": ["Jeux intÃ©rieurs", "Chasse au trÃ©sor", "SoirÃ©e jeux de sociÃ©tÃ©"],
    "sport": ["Cours de gym douce", "Ã‰quitation enfant", "Skating"],
    "sortie": ["Restaurant enfant-friendly", "CinÃ©ma familial", "Zoo"]
}


def app():
    """Interface principale du module ActivitÃ©s"""
    st.title("ðŸŽ¨ ActivitÃ©s Familiales")
    
    tabs = st.tabs(["ðŸ“… Planning Semaine", "ðŸ’¡ IdÃ©es ActivitÃ©s", "ðŸ’° Budget"])
    
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    # TAB 1: PLANNING SEMAINE
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    with tabs[0]:
        st.header("ðŸ“… Planning de la Semaine")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("ActivitÃ©s PrÃ©vues")
            
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
                                st.caption(f"{act['type']} â€¢ {act.get('lieu', 'TBD')}")
                                if act.get('participants'):
                                    st.caption(f"ðŸ‘¥ {', '.join(act['participants'])}")
                                st.caption(f"ðŸ’° {act.get('cout_estime', 0):.2f}â‚¬")
                else:
                    st.info("Aucune activitÃ© cette semaine. Planifiez une activitÃ©!")
            
            except Exception as e:
                st.error(f"âŒ Erreur chargement: {str(e)}")
        
        with col2:
            st.subheader("âž• Ajouter ActivitÃ©")
            
            with st.form("form_activite"):
                titre = st.text_input("Nom")
                type_act = st.selectbox("Type", 
                    ["parc", "musÃ©e", "eau", "jeu_maison", "sport", "sortie"])
                date_act = st.date_input("Date")
                duree = st.number_input("DurÃ©e (h)", 0.5, 8.0, 2.0)
                lieu = st.text_input("Lieu")
                cout = st.number_input("CoÃ»t estimÃ© (â‚¬)", 0.0, 500.0, 0.0)
                
                if st.form_submit_button("âœ… Ajouter", use_container_width=True):
                    if titre and type_act:
                        ajouter_activite(titre, type_act, date_act, duree, lieu, 
                                       ["Famille"], cout)
    
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    # TAB 2: IDÃ‰ES ACTIVITÃ‰S
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    with tabs[1]:
        st.header("ðŸ’¡ IdÃ©es d'ActivitÃ©s")
        
        st.subheader("Suggestions par type")
        
        col1, col2, col3 = st.columns(3)
        
        cols = [col1, col2, col3]
        type_keys = list(SUGGESTIONS_ACTIVITES.keys())
        
        for i, type_key in enumerate(type_keys[:3]):
            with cols[i]:
                emoji = "ðŸŽª" if type_key == "parc" else "ðŸ›ï¸" if type_key == "musÃ©e" else "ðŸ’§" if type_key == "eau" else "ðŸŽ®" if type_key == "jeu_maison" else "âš½" if type_key == "sport" else "ðŸ½ï¸"
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
                emoji = "ðŸŽª" if type_key == "parc" else "ðŸ›ï¸" if type_key == "musÃ©e" else "ðŸ’§" if type_key == "eau" else "ðŸŽ®" if type_key == "jeu_maison" else "âš½" if type_key == "sport" else "ðŸ½ï¸"
                title = type_key.replace("_", " ").title()
                
                st.subheader(f"{emoji} {title}")
                for suggestion in SUGGESTIONS_ACTIVITES[type_key]:
                    if st.button(suggestion, key=f"suggest_{type_key}_{suggestion}", 
                               use_container_width=True):
                        st.session_state.suggestion = suggestion
    
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    # TAB 3: BUDGET
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    with tabs[2]:
        st.header("ðŸ’° Budget ActivitÃ©s")
        
        # Stats
        col1, col2, col3 = st.columns(3)
        
        try:
            budget_mois = get_budget_activites_mois()
            budget_semaine = get_budget_par_period("week").get("ActivitÃ©s", 0)
            
            with col1:
                st.metric("ðŸ’° Ce mois", f"{budget_mois:.2f}â‚¬")
            with col2:
                st.metric("ðŸ“Š Cette semaine", f"{budget_semaine:.2f}â‚¬")
            with col3:
                st.metric("ðŸ“ˆ Budget moyen", f"{budget_mois / 4:.2f}â‚¬ par semaine")
        
        except Exception as e:
            st.error(f"âŒ Erreur budget: {str(e)}")
        
        st.divider()
        
        # Graphique timeline
        st.subheader("ðŸ“ˆ Graphique DÃ©penses")
        
        try:
            with get_session() as session:
                # RÃ©cupÃ©rer les 30 derniers jours
                debut = date.today() - timedelta(days=30)
                activites = session.query(FamilyActivity).filter(
                    FamilyActivity.date_prevue >= debut
                ).all()
                
                if activites:
                    # CrÃ©er DataFrame
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
                        name="CoÃ»t estimÃ©",
                        line_color="blue"
                    ))
                    fig1.add_trace(go.Scatter(
                        x=df["date"],
                        y=df["cout_reel"],
                        mode="lines+markers",
                        name="CoÃ»t rÃ©el",
                        line_color="red"
                    ))
                    
                    fig1.update_layout(
                        title="DÃ©penses par Date",
                        xaxis_title="Date",
                        yaxis_title="Montant (â‚¬)",
                        height=400,
                        hovermode="x unified"
                    )
                    st.plotly_chart(fig1, use_container_width=True)
                    
                    # Graphique 2: Par type d'activitÃ©
                    type_budget = df.groupby("type")["cout_estime"].sum().reset_index()
                    type_budget.columns = ["Type", "Budget"]
                    
                    fig2 = go.Figure(data=[
                        go.Bar(x=type_budget["Type"], y=type_budget["Budget"],
                               marker_color="lightblue")
                    ])
                    fig2.update_layout(
                        title="Budget par Type d'ActivitÃ©",
                        xaxis_title="Type",
                        yaxis_title="Budget (â‚¬)",
                        height=400
                    )
                    st.plotly_chart(fig2, use_container_width=True)
                else:
                    st.info("Aucune activitÃ© sur 30 jours")
        
        except Exception as e:
            st.error(f"âŒ Erreur graphiques: {str(e)}")


if __name__ == "__main__":
    main()

