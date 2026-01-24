"""
Module Jules - Suivi développement et apprentissages (19 mois)
Version améliorée avec helpers, caching et graphiques
"""

import streamlit as st
from datetime import date, timedelta
import pandas as pd
import plotly.graph_objects as go

from src.core.database import get_session
from src.core.models import ChildProfile, Milestone, FamilyActivity
from src.modules.famille.helpers import (
    get_or_create_jules,
    calculer_age_jules,
    get_milestones_by_category,
    count_milestones_by_category,
    get_activites_semaine,
    clear_famille_cache
)


def ajouter_milestone(titre: str, description: str, categorie: str, notes: str = ""):
    """Ajoute un nouveau jalon de Jules"""
    try:
        child_id = get_or_create_jules()
        
        with get_session() as session:
            milestone = Milestone(
                child_id=child_id,
                titre=titre,
                description=description,
                categorie=categorie,
                date_atteint=date.today(),
                notes=notes
            )
            session.add(milestone)
            session.commit()
            st.success(f"✅ Jalon '{titre}' enregistré!")
            clear_famille_cache()
            return True
    except Exception as e:
        st.error(f"❌ Erreur ajout jalon: {str(e)}")
        return False


MILESTONES_CATEGORIES = {
    "langage": "🗣️ Langage",
    "motricité": "🚶 Motricité",
    "social": "👥 Social",
    "cognitif": "🧠 Cognitif",
    "alimentation": "🍽️ Alimentation",
    "sommeil": "😴 Sommeil",
    "autre": "⭐ Autre"
}

ACTIVITES_19_MOIS = {
    "parc": [
        "Jeux dans le sable",
        "Toboggan (avec aide)",
        "Balançoire",
        "Courir dans l'herbe",
        "Observer les oiseaux"
    ],
    "maison": [
        "Jeux de cache-cache simples",
        "Danser sur musique",
        "Construire avec blocs",
        "Lire des livres illustrés",
        "Jouer avec des jouets à pousser"
    ],
    "eau": [
        "Piscine bébé (peu profonde)",
        "Baignoire avec jouets",
        "Arroser des plantes",
        "Verser de l'eau d'un verre",
        "Jouer avec éponges"
    ],
    "apprentissage": [
        "Montrer des animaux (bruits)",
        "Nommer les couleurs",
        "Compter jusqu'à 3",
        "Imiter les gestes",
        "Puzzles simples (2-3 pièces)"
    ],
    "sport": [
        "Marcher sur ligne",
        "Monter/descendre escaliers (avec aide)",
        "Lancer un ballon",
        "Sauter sur place",
        "Frapper un ballon"
    ]
}

SHOPPING_JULES = {
    "jouets": [
        "Jouets à empiler",
        "Balles sensorielles",
        "Livres cartonnés",
        "Voitures à pousser",
        "Figurines animaux"
    ],
    "vetements": [
        "Vêtements confortables",
        "Chaussures souples",
        "Bonnet/gants (hiver)",
        "Maillot de bain",
        "Tablier repas"
    ],
    "hygiene": [
        "Couches (taille 4)",
        "Lingettes bébé",
        "Savon doux",
        "Brosse à dents souple",
        "Dentifrice enfant"
    ]
}


def app():
    """Interface principale du module Jules"""
    st.title("👶 Jules (19 mois)")
    
    # Profil Jules
    try:
        child_id = get_or_create_jules()
        age_info = calculer_age_jules()
        
        # Afficher âge en gros
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("🗓️ Âge", f"{age_info['mois']} mois", f"{age_info['jours']} jours")
        with col2:
            st.metric("📅 Né le", age_info['date_naissance'].strftime("%d/%m/%Y"))
        with col3:
            st.metric("🎂 Prochain anniversaire", f"Dans {365 - (age_info['jours'] % 365)} jours")
    
    except Exception as e:
        st.error(f"❌ Erreur chargement profil Jules: {str(e)}")
        return
    
    tabs = st.tabs(["📊 Jalons", "🎯 Activités Semaine", "🛍️ Shopping"])
    
    # ════════════════════════════════════════════════════════
    # TAB 1: JALONS
    # ════════════════════════════════════════════════════════
    with tabs[0]:
        st.header("Jalons & Apprentissages")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("Jalons enregistrés")
            
            try:
                milestones_dict = get_milestones_by_category(child_id)
                counts = count_milestones_by_category(child_id)
                
                if milestones_dict:
                    # Afficher par catégorie
                    for cat, title in MILESTONES_CATEGORIES.items():
                        if cat in milestones_dict:
                            with st.container(border=True):
                                col_title, col_count = st.columns([3, 1])
                                with col_title:
                                    st.write(f"**{title}**")
                                with col_count:
                                    st.metric("", counts.get(cat, 0))
                                
                                # Lister les jalons
                                for m in milestones_dict[cat]:
                                    st.write(f"✓ {m['titre']} ({m['date'].strftime('%d/%m/%Y')})")
                                    if m['description']:
                                        st.caption(m['description'])
                else:
                    st.info("Aucun jalon enregistré. Commencez à documenter!")
            
            except Exception as e:
                st.error(f"❌ Erreur chargement jalons: {str(e)}")
        
        with col2:
            st.subheader("Ajouter un jalon")
            
            with st.form("form_milestone"):
                titre = st.text_input("Titre", placeholder="Ex: Premiers pas")
                description = st.text_area("Description", height=80, 
                                         placeholder="Détails du jalon")
                categorie = st.selectbox("Catégorie", 
                    list(MILESTONES_CATEGORIES.keys()),
                    format_func=lambda x: MILESTONES_CATEGORIES[x])
                notes = st.text_area("Notes", height=60, 
                                   placeholder="Détails supplémentaires")
                
                if st.form_submit_button("✅ Ajouter", use_container_width=True):
                    if titre and categorie:
                        ajouter_milestone(titre, description, categorie, notes)
    
    # ════════════════════════════════════════════════════════
    # TAB 2: ACTIVITÉS SEMAINE
    # ════════════════════════════════════════════════════════
    with tabs[1]:
        st.header("Activités Adaptées à l'Âge")
        
        st.info("💡 Idées d'activités recommandées pour Jules (19 mois)")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.subheader("🎪 Parc")
            for act in ACTIVITES_19_MOIS["parc"]:
                st.write(f"• {act}")
        
        with col2:
            st.subheader("🏠 Maison")
            for act in ACTIVITES_19_MOIS["maison"]:
                st.write(f"• {act}")
        
        with col3:
            st.subheader("💧 Eau")
            for act in ACTIVITES_19_MOIS["eau"]:
                st.write(f"• {act}")
        
        col4, col5 = st.columns(2)
        
        with col4:
            st.subheader("🧠 Apprentissage")
            for act in ACTIVITES_19_MOIS["apprentissage"]:
                st.write(f"• {act}")
        
        with col5:
            st.subheader("⚽ Sport")
            for act in ACTIVITES_19_MOIS["sport"]:
                st.write(f"• {act}")
        
        # Activités planifiées
        st.divider()
        st.subheader("📅 Activités Familiales Prévues")
        
        try:
            activites = get_activites_semaine()
            if activites:
                for act in activites:
                    with st.container(border=True):
                        col_info, col_status = st.columns([3, 1])
                        with col_info:
                            st.write(f"**{act['titre']}**")
                            st.caption(f"{act['date'].strftime('%a %d/%m')} - {act['type']}")
                            if act.get('participants'):
                                st.caption(f"👥 {', '.join(act['participants'])}")
                        with col_status:
                            status_emoji = "✅" if act['statut'] == "terminé" else "📅"
                            st.write(status_emoji)
            else:
                st.info("Aucune activité planifiée cette semaine")
        except Exception as e:
            st.error(f"❌ Erreur chargement activités: {str(e)}")
    
    # ════════════════════════════════════════════════════════
    # TAB 3: SHOPPING
    # ════════════════════════════════════════════════════════
    with tabs[2]:
        st.header("🛍️ À Acheter pour Jules")
        
        st.subheader("Suggestions par catégorie")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.subheader("🎮 Jouets")
            for item in SHOPPING_JULES["jouets"]:
                if st.checkbox(item, key=f"jouets_{item}"):
                    st.write(f"✓ {item}")
        
        with col2:
            st.subheader("👕 Vêtements")
            for item in SHOPPING_JULES["vetements"]:
                if st.checkbox(item, key=f"vetements_{item}"):
                    st.write(f"✓ {item}")
        
        with col3:
            st.subheader("🧼 Hygiène")
            for item in SHOPPING_JULES["hygiene"]:
                if st.checkbox(item, key=f"hygiene_{item}"):
                    st.write(f"✓ {item}")


if __name__ == "__main__":
    app()
