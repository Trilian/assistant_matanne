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

# Logique métier pure - imports commentés si fonction n'existe pas
# from src.domains.famille.logic.jules_logic import (
#     calculer_progression_milestones,
#     suggerer_prochains_milestones
# )

from src.domains.famille.logic.helpers import (
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
            st.success(f"âœ… Jalon '{titre}' enregistré!")
            clear_famille_cache()
            return True
    except Exception as e:
        st.error(f"âŒ Erreur ajout jalon: {str(e)}")
        return False


MILESTONES_CATEGORIES = {
    "langage": "ðŸ—£ï¸ Langage",
    "motricité": "ðŸš¶ Motricité",
    "social": "ðŸ‘¥ Social",
    "cognitif": "ðŸ§  Cognitif",
    "alimentation": "ðŸ½ï¸ Alimentation",
    "sommeil": "ðŸ˜´ Sommeil",
    "autre": "â­ Autre"
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
    st.title("ðŸ‘¶ Jules (19 mois)")
    
    # Profil Jules
    try:
        child_id = get_or_create_jules()
        age_info = calculer_age_jules()
        
        # Afficher Ã¢ge en gros
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("ðŸ—“ï¸ Ã‚ge", f"{age_info['mois']} mois", f"{age_info['jours']} jours")
        with col2:
            st.metric("ðŸ“… Né le", age_info['date_naissance'].strftime("%d/%m/%Y"))
        with col3:
            st.metric("ðŸŽ‚ Prochain anniversaire", f"Dans {365 - (age_info['jours'] % 365)} jours")
    
    except Exception as e:
        st.error(f"âŒ Erreur chargement profil Jules: {str(e)}")
        return
    
    tabs = st.tabs(["ðŸ“Š Jalons", "ðŸŽ¯ Activités Semaine", "ðŸ›ï¸ Shopping"])
    
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    # TAB 1: JALONS
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
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
                                    st.write(f"âœ“ {m['titre']} ({m['date'].strftime('%d/%m/%Y')})")
                                    if m['description']:
                                        st.caption(m['description'])
                else:
                    st.info("Aucun jalon enregistré. Commencez à documenter!")
            
            except Exception as e:
                st.error(f"âŒ Erreur chargement jalons: {str(e)}")
        
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
                
                if st.form_submit_button("âœ… Ajouter", use_container_width=True):
                    if titre and categorie:
                        ajouter_milestone(titre, description, categorie, notes)
    
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    # TAB 2: ACTIVITÃ‰S SEMAINE
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    with tabs[1]:
        st.header("Activités Adaptées à l'Ã‚ge")
        
        st.info("ðŸ’¡ Idées d'activités recommandées pour Jules (19 mois)")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.subheader("ðŸŽª Parc")
            for act in ACTIVITES_19_MOIS["parc"]:
                st.write(f"â€¢ {act}")
        
        with col2:
            st.subheader("ðŸ  Maison")
            for act in ACTIVITES_19_MOIS["maison"]:
                st.write(f"â€¢ {act}")
        
        with col3:
            st.subheader("ðŸ’§ Eau")
            for act in ACTIVITES_19_MOIS["eau"]:
                st.write(f"â€¢ {act}")
        
        col4, col5 = st.columns(2)
        
        with col4:
            st.subheader("ðŸ§  Apprentissage")
            for act in ACTIVITES_19_MOIS["apprentissage"]:
                st.write(f"â€¢ {act}")
        
        with col5:
            st.subheader("âš½ Sport")
            for act in ACTIVITES_19_MOIS["sport"]:
                st.write(f"â€¢ {act}")
        
        # Activités planifiées
        st.divider()
        st.subheader("ðŸ“… Activités Familiales Prévues")
        
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
                                st.caption(f"ðŸ‘¥ {', '.join(act['participants'])}")
                        with col_status:
                            status_emoji = "âœ…" if act['statut'] == "terminé" else "ðŸ“…"
                            st.write(status_emoji)
            else:
                st.info("Aucune activité planifiée cette semaine")
        except Exception as e:
            st.error(f"âŒ Erreur chargement activités: {str(e)}")
    
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    # TAB 3: SHOPPING
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    with tabs[2]:
        st.header("ðŸ›ï¸ Ã€ Acheter pour Jules")
        
        st.subheader("Suggestions par catégorie")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.subheader("ðŸŽ® Jouets")
            for item in SHOPPING_JULES["jouets"]:
                if st.checkbox(item, key=f"jouets_{item}"):
                    st.write(f"âœ“ {item}")
        
        with col2:
            st.subheader("ðŸ‘• Vêtements")
            for item in SHOPPING_JULES["vetements"]:
                if st.checkbox(item, key=f"vetements_{item}"):
                    st.write(f"âœ“ {item}")
        
        with col3:
            st.subheader("ðŸ§¼ Hygiène")
            for item in SHOPPING_JULES["hygiene"]:
                if st.checkbox(item, key=f"hygiene_{item}"):
                    st.write(f"âœ“ {item}")


if __name__ == "__main__":
    app()

