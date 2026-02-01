"""
Module Accueil - Dashboard principal Famille

Hub affichant:
- Profil Jules (âge, prochains jalons)
- Objectifs santé et progression
- Activités cette semaine
- Budget semaine/mois
- Notifications & recommandations
"""

import streamlit as st
from datetime import date, timedelta
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

from src.core.database import get_db
from src.core.models import ChildProfile, FamilyActivity, HealthObjective, FamilyBudget

# Logique métier pure
from src.domains.famille.logic.accueil_logic import (
    calculer_metriques_dashboard_famille,
    generer_notifications_famille
)

from src.domains.famille.logic.helpers import (
    get_or_create_jules,
    calculer_age_jules,
    get_milestones_by_category,
    count_milestones_by_category,
    get_objectives_actifs,
    get_activites_semaine,
    get_budget_par_period,
    get_stats_santé_semaine
)

# Import du module logique métier séparé
from src.domains.famille.logic.accueil_logic import (
    JULIUS_BIRTHDAY,
    NOTIFICATION_TYPES,
    DASHBOARD_SECTIONS,
    calculer_age_julius,
    formater_age_julius,
    calculer_metriques_globales,
    calculer_metriques_sante,
    calculer_metriques_budget,
    generer_notifications_critiques,
    generer_suggestions_actions,
    calculer_temps_ecoule,
)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# HELPER: DASHBOARD METRICS
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

@st.cache_data(ttl=1800)
def get_dashboard_metrics():
    """Récupère les métriques principales du dashboard"""
    try:
        child_id = get_or_create_jules()
        metrics = {
            "jules_age": calculer_age_julius(),
            "milestones_count": count_milestones_by_category(child_id),
            "objectifs_actifs": len(get_objectives_actifs()),
            "activites_semaine": len(get_activites_semaine()),
            "budget_mois": get_budget_par_period(30),
            "stats_sante": get_stats_santé_semaine()
        }
        return metrics
    except Exception as e:
        st.error(f"❌ Erreur dashboard: {e}")
        return {}


def calculer_julius():
    """Alias pour get_or_create_jules puis calculer l'âge"""
    try:
        child_id = get_or_create_jules()
        return calculer_age_jules(child_id)
    except Exception as e:
        return None


@st.cache_data(ttl=1800)
def get_notifications():
    """Génère les notifications du dashboard"""
    notifications = []
    
    try:
        # Obtenir le child_id
        child_id = get_or_create_jules()
        
        # Notification 1: Prochain jalon
        milestones_dict = get_milestones_by_category(child_id)
        if milestones_dict:
            # Trouver le jalon le plus récent
            all_milestones = []
            for cat, milestones in milestones_dict.items():
                all_milestones.extend(milestones)
            
            if all_milestones:
                recent = max(all_milestones, key=lambda x: x.get('date_atteint', date.today()))
                recent_date = recent.get('date_atteint', date.today())
                days_since = (date.today() - recent_date).days
                if days_since < 7:
                    notifications.append({
                        "type": "success",
                        "emoji": "🎯,
                        "titre": "Nouveau jalon!",
                        "message": f"{recent['titre']} ({days_since}j ago)"
                    })
        
        # Notification 2: Objectifs en retard
        objectives = get_objectives_actifs()
        for obj in objectives:
            progress = obj.get('progression', 0)
            
            days_remaining = obj.get('jours_restants')
            
            if days_remaining and days_remaining < 7 and progress < 80:
                notifications.append({
                    "type": "warning",
                    "emoji": "âš ï¸",
                    "titre": "Objectif en retard",
                    "message": f"{obj['titre']} - {progress:.0f}% ({days_remaining}j restants)"
                })
        
        # Notification 3: Budget
        budget_data = get_budget_par_period("week")
        if budget_data:
            total = budget_data.get("TOTAL", 0)
            if total > 500:
                notifications.append({
                    "type": "info",
                    "emoji": "📋",
                    "titre": "Budget élevé cette semaine",
                    "message": f"{total:.2f}€ dépensés (cette semaine)"
                })
        
        # Notification 4: Activités
        activites = get_activites_semaine()
        if len(activites) > 5:
            notifications.append({
                "type": "info",
                "emoji": "📱…",
                "titre": "Semaine chargée!",
                "message": f"{len(activites)} activités planifiées"
            })
        
    except Exception as e:
        notifications.append({
            "type": "error",
            "emoji": "❌",
            "titre": "Erreur chargement",
            "message": str(e)
        })
    
    return notifications


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# STREAMLIT: DASHBOARD
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

def app():
    st.set_page_config(page_title="Accueil Famille", page_icon="🗑️", layout="wide")
    
    # Header
    st.title("🗑️ Bienvenue dans le Hub Famille")
    st.markdown("---")
    
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    # SECTION 1: NOTIFICATIONS
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    
    notifications = get_notifications()
    
    if notifications:
        st.subheader("👶 Notifications")
        
        for notif in notifications:
            if notif["type"] == "success":
                st.success(f"{notif['emoji']} **{notif['titre']}** - {notif['message']}")
            elif notif["type"] == "warning":
                st.warning(f"{notif['emoji']} **{notif['titre']}** - {notif['message']}")
            elif notif["type"] == "info":
                st.info(f"{notif['emoji']} **{notif['titre']}** - {notif['message']}")
            else:
                st.error(f"{notif['emoji']} **{notif['titre']}** - {notif['message']}")
        
        st.markdown("---")
    
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    # SECTION 2: PROFIL JULES
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("🍽️ Jules - 19 mois")
        
        try:
            age_info = calculer_julius()
            if age_info:
                st.metric("📱… Ã‚ge", f"{age_info['mois']}m {age_info['jours']}j")
                st.metric("📱 Jours depuis naissance", age_info['jours_total'])
                
                # Anniversaire
                st.caption(f"🔔 Anniversaire: 22 Juin 2025")
        except Exception as e:
            st.error(f"❌ {e}")
        
        # Jalons par catégorie
        try:
            child_id = get_or_create_jules()
            milestones_count = count_milestones_by_category(child_id)
            if milestones_count:
                st.markdown("### Jalons par catégorie")
                for cat, count in sorted(milestones_count.items()):
                    st.write(f"• {cat.capitalize()}: **{count}**")
        except Exception as e:
            st.warning(f"âš ï¸ {e}")
    
    with col2:
        st.subheader("🎯 Objectifs Santé")
        
        try:
            objectifs = get_objectives_actifs()
            
            if objectifs:
                for obj in objectifs[:3]:  # Top 3 objectifs
                    progress = (obj.get('valeur_actuelle') or 0) / (obj.get('valeur_cible') or 1) * 100
                    
                    st.write(f"**{obj['titre']}**")
                    st.progress(min(progress / 100, 1.0))
                    st.caption(f"{obj.get('valeur_actuelle') or 0:.1f}/{obj.get('valeur_cible', 0):.1f} {obj.get('unite', '')}")
                    
                    if obj.get('date_cible'):
                        days = (obj['date_cible'] - date.today()).days
                        st.caption(f"⏱️ {days} jours restants")
                
                if len(objectifs) > 3:
                    st.caption(f"... et {len(objectifs) - 3} autres objectifs")
            
            else:
                st.info("ℹ️ Aucun objectif actif")
        
        except Exception as e:
            st.error(f"❌ {e}")
    
    with col3:
        st.subheader("[CHART] Stats Santé (7j)")
        
        try:
            stats = get_stats_santé_semaine()
            
            if stats and stats.get("nb_seances", 0) > 0:
                st.metric("📥 Séances", stats.get("nb_seances", 0))
                st.metric("⏱️ Minutes totales", int(stats.get("total_minutes", 0)))
                st.metric("âš¡ Énergie moyenne", f"{stats.get('energie_moyenne', 0):.1f}/10")
                st.metric("🧹 Moral moyen", f"{stats.get('moral_moyen', 0):.1f}/10")
            
            else:
                st.info("ℹ️ Aucune activité cette semaine")
        
        except Exception as e:
            st.error(f"❌ {e}")
    
    st.markdown("---")
    
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    # SECTION 3: ACTIVITÉS SEMAINE
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    
    st.subheader("📱… Activités cette semaine")
    
    try:
        activites = get_activites_semaine()
        
        if activites:
            # Timeline graphique
            df_activites = pd.DataFrame([
                {
                    "Date": a.get('date') if isinstance(a, dict) else a.date_prevue,
                    "Activité": a.get('titre') if isinstance(a, dict) else a.titre,
                    "Type": a.get('type') if isinstance(a, dict) else a.type_activite,
                    "Coût": a.get('cout_estime') or 0 if isinstance(a, dict) else a.cout_estime or 0
                }
                for a in activites
            ])
            
            df_activites = df_activites.sort_values("Date")
            
            fig = px.timeline(
                df_activites,
                x_start="Date",
                x_end=pd.to_datetime(df_activites["Date"]) + timedelta(hours=1),
                y="Type",
                color="Type",
                title="Timeline activités semaine"
            )
            
            fig.update_layout(height=400, hovermode="closest")
            st.plotly_chart(fig, width="stretch", key="family_activities_timeline")
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown("### 💰 Détail")
                for activity in activites:
                    with st.expander(f"📅 {activity.titre} - {activity.date_prevue}"):
                        st.write(f"🎨 **Type**: {activity.type_activite}")
                        st.write(f"📱 **Lieu**: {activity.lieu}")
                        st.write(f"⏱️ **Durée**: {activity.duree_heures}h")
                        
                        if activity.cost_estime > 0:
                            st.write(f"📋 **Coût estimé**: {activity.cout_estime:.2f}€")
                        
                        if activity.qui_participe:
                            st.write(f"💡 **Participants**: {', '.join(activity.qui_participe)}")
            
            with col2:
                st.markdown("### 📋 Budget activités")
                
                total_cost = sum(a.cout_estime or 0 for a in activites)
                st.metric("Total estimé", f"{total_cost:.2f}€")
                
                # Par type
                types_count = {}
                for a in activites:
                    types_count[a.type_activite] = types_count.get(a.type_activite, 0) + 1
                
                for activity_type, count in types_count.items():
                    st.write(f"• {activity_type.capitalize()}: {count}")
        
        else:
            st.info("ℹ️ Aucune activité prévue cette semaine")
    
    except Exception as e:
        st.error(f"❌ Erreur activités: {e}")
    
    st.markdown("---")
    
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    # SECTION 4: BUDGET FAMILLE
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📋 Budget cette semaine")
        
        try:
            budget_semaine = get_budget_par_period(7)
            
            if budget_semaine and budget_semaine.get("TOTAL", 0) > 0:
                # Exclure TOTAL du dataframe
                budget_data = {k: v for k, v in budget_semaine.items() if k != "TOTAL"}
                
                df_budget_cat = pd.DataFrame([
                    {"Catégorie": cat, "Montant": montant}
                    for cat, montant in budget_data.items()
                ])
                
                fig = px.pie(
                    df_budget_cat,
                    names="Catégorie",
                    values="Montant",
                    title="Répartition budget (7 jours)"
                )
                
                st.plotly_chart(fig, width="stretch", key="family_budget_pie")
                st.metric("👧 Total", f"{total:.2f}€")
            
            else:
                st.info("ℹ️ Aucune dépense cette semaine")
        
        except Exception as e:
            st.error(f"❌ {e}")
    
    with col2:
        st.subheader("📋 Budget ce mois")
        
        try:
            budget_mois = get_budget_par_period(30)
            
            if budget_mois and budget_mois.get("TOTAL", 0) > 0:
                # Exclure TOTAL du dataframe
                budget_data = {k: v for k, v in budget_mois.items() if k != "TOTAL"}
                
                df_mois_cat = pd.DataFrame([
                    {"Catégorie": cat, "Montant": montant}
                    for cat, montant in budget_data.items()
                ])
                
                total_mois = budget_mois.get("TOTAL", 0)
                
                col_a, col_b = st.columns(2)
                with col_a:
                    st.metric("Réel (mois)", f"{total_mois:.2f}€")
                with col_b:
                    st.metric("Montant moyen par catégorie", f"{total_mois / max(len(budget_data), 1):.2f}€")
            
            else:
                st.info("ℹ️ Aucune dépense ce mois")
        
        except Exception as e:
            st.error(f"❌ {e}")
    
    st.markdown("---")
    
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    # SECTION 5: QUICK LINKS
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    
    st.subheader("âš¡ Accès rapide")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("➕ Ajouter jalon", use_container_width=True):
            st.write("Allez à Jules â†’ Jalons")
    
    with col2:
        if st.button("➕ Nouvelle activité", use_container_width=True):
            st.write("Allez à Activités â†’ Planning")
    
    with col3:
        if st.button("➕ Nouvel objectif", use_container_width=True):
            st.write("Allez à Santé â†’ Objectifs")
    
    with col4:
        if st.button("💰 Shopping", use_container_width=True):
            st.write("Allez à Shopping")
    
    st.markdown("---")
    
    # Footer
    st.caption("🗑️ Hub Famille - Toutes les infos en un coup d'oeil")


if __name__ == "__main__":
    main()

