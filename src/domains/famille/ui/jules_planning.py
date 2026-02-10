"""
Module Planning Semaine Jules - Activités d'éveil organisées par jour.

Pour un enfant de ~19 mois:
- Planning hebdomadaire d'activités
- Répartition équilibrée (motricité, langage, créativité, extérieur)
- Suivi de ce qui a été fait
- Suggestions IA personnalisées
"""

import streamlit as st
from datetime import date, timedelta
from typing import Optional
import random

from src.core.database import obtenir_contexte_db
from src.core.models import ChildProfile


# ═══════════════════════════════════════════════════════════
# CONSTANTES - ACTIVITÉS PAR CATÉGORIE
# ═══════════════════════════════════════════════════════════

CATEGORIES_ACTIVITES = {
    "motricite": {
        "emoji": "🏃",
        "couleur": "#4CAF50",
        "activites": [
            {"nom": "Parcours coussins", "duree": 15, "desc": "Grimper, sauter sur les coussins"},
            {"nom": "Danse sur musique", "duree": 10, "desc": "Bouger librement sur comptines"},
            {"nom": "Jeu de ballon", "duree": 15, "desc": "Rouler, lancer, attraper"},
            {"nom": "Monter/descendre escalier", "duree": 10, "desc": "Avec aide, alterner les pieds"},
            {"nom": "Porteur/trotteur", "duree": 20, "desc": "Se déplacer dans la maison"},
            {"nom": "Yoga bébé", "duree": 10, "desc": "Imiter des postures animaux"},
        ]
    },
    "langage": {
        "emoji": "💬",
        "couleur": "#2196F3",
        "activites": [
            {"nom": "Lecture interactive", "duree": 15, "desc": "Pointer et nommer les images"},
            {"nom": "Comptines gestuelles", "duree": 10, "desc": "Ainsi font font, Petit escargot..."},
            {"nom": "Nommer les objets", "duree": 10, "desc": "Lors du bain, repas, habillage"},
            {"nom": "Imagier sonore", "duree": 10, "desc": "Sons animaux, véhicules"},
            {"nom": "Téléphone jouet", "duree": 10, "desc": "Faire semblant de parler"},
            {"nom": "Chansons répétitives", "duree": 10, "desc": "La même chanson plusieurs fois"},
        ]
    },
    "creativite": {
        "emoji": "🎨",
        "couleur": "#FF9800",
        "activites": [
            {"nom": "Peinture au doigt", "duree": 20, "desc": "Sur grande feuille ou carton"},
            {"nom": "Pâte à modeler", "duree": 20, "desc": "Manipuler, écraser, rouler"},
            {"nom": "Gommettes", "duree": 15, "desc": "Coller sur une feuille"},
            {"nom": "Dessin aux crayons", "duree": 15, "desc": "Gros crayons adaptés"},
            {"nom": "Pâte à sel", "duree": 20, "desc": "Faire des formes simples"},
            {"nom": "Collage", "duree": 15, "desc": "Coller des morceaux de papier"},
        ]
    },
    "sensoriel": {
        "emoji": "✋",
        "couleur": "#9C27B0",
        "activites": [
            {"nom": "Bac sensoriel", "duree": 20, "desc": "Riz, pâtes, sable kinetic"},
            {"nom": "Jeux d'eau", "duree": 20, "desc": "Transvaser, verser, éclabousser"},
            {"nom": "Textures à toucher", "duree": 10, "desc": "Doux, rugueux, lisse..."},
            {"nom": "Boîte à trésors", "duree": 15, "desc": "Explorer objets du quotidien"},
            {"nom": "Bulles de savon", "duree": 10, "desc": "Attraper, observer"},
            {"nom": "Cuisine sensorielle", "duree": 15, "desc": "Toucher fruits, légumes"},
        ]
    },
    "exterieur": {
        "emoji": "🌳",
        "couleur": "#795548",
        "activites": [
            {"nom": "Promenade nature", "duree": 30, "desc": "Observer, ramasser feuilles"},
            {"nom": "Bac à sable", "duree": 30, "desc": "Creuser, construire"},
            {"nom": "Arrosage plantes", "duree": 15, "desc": "Avec petit arrosoir"},
            {"nom": "Jeux au parc", "duree": 45, "desc": "Toboggan, balançoire"},
            {"nom": "Vélo/draisienne", "duree": 20, "desc": "Dans le jardin ou parc"},
            {"nom": "Chasse aux trésors", "duree": 20, "desc": "Trouver des objets dehors"},
        ]
    },
    "imitation": {
        "emoji": "🎭",
        "couleur": "#E91E63",
        "activites": [
            {"nom": "Dînette", "duree": 20, "desc": "Préparer à manger, servir"},
            {"nom": "Poupée/doudou", "duree": 15, "desc": "Nourrir, coucher, promener"},
            {"nom": "Ménage avec balai", "duree": 10, "desc": "Imiter papa/maman"},
            {"nom": "Téléphone", "duree": 10, "desc": "Faire semblant d'appeler"},
            {"nom": "Voitures/garage", "duree": 20, "desc": "Faire rouler, garer"},
            {"nom": "Docteur", "duree": 15, "desc": "Soigner les doudous"},
        ]
    },
}

# Planning type de la semaine (équilibré)
PLANNING_SEMAINE_TYPE = {
    0: ["motricite", "langage", "creativite"],  # Lundi
    1: ["sensoriel", "imitation", "exterieur"],  # Mardi
    2: ["motricite", "creativite", "langage"],  # Mercredi
    3: ["exterieur", "sensoriel", "imitation"],  # Jeudi
    4: ["motricite", "langage", "creativite"],  # Vendredi
    5: ["exterieur", "imitation", "sensoriel"],  # Samedi
    6: ["creativite", "langage", "exterieur"],  # Dimanche
}

JOURS_SEMAINE = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]


# ═══════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════

def get_age_jules_mois() -> int:
    """Retourne l'âge de Jules en mois"""
    try:
        with obtenir_contexte_db() as db:
            jules = db.query(ChildProfile).filter_by(name="Jules", actif=True).first()
            if jules and jules.date_of_birth:
                delta = date.today() - jules.date_of_birth
                return delta.days // 30
    except:
        pass
    # Défaut: né le 22/06/2024
    return (date.today() - date(2024, 6, 22)).days // 30


def generer_activites_jour(jour_semaine: int, seed: Optional[int] = None) -> list[dict]:
    """Génère les activités pour un jour de la semaine."""
    if seed:
        random.seed(seed)
    
    categories_jour = PLANNING_SEMAINE_TYPE.get(jour_semaine, ["motricite", "langage"])
    activites = []
    
    for cat in categories_jour:
        cat_info = CATEGORIES_ACTIVITES.get(cat, {})
        if cat_info.get("activites"):
            activite = random.choice(cat_info["activites"])
            activites.append({
                "categorie": cat,
                "emoji": cat_info["emoji"],
                "couleur": cat_info["couleur"],
                **activite
            })
    
    return activites


def get_planning_semaine() -> dict[int, list[dict]]:
    """Génère le planning de la semaine courante."""
    today = date.today()
    # Seed basé sur la semaine pour consistance
    week_seed = today.isocalendar()[1] * 100 + today.year
    
    planning = {}
    for jour in range(7):
        planning[jour] = generer_activites_jour(jour, seed=week_seed + jour)
    
    return planning


# ═══════════════════════════════════════════════════════════
# SESSION STATE - TRACKING
# ═══════════════════════════════════════════════════════════

def init_tracking():
    """Initialise le tracking des activités faites."""
    if "jules_activites_faites" not in st.session_state:
        st.session_state["jules_activites_faites"] = {}


def marquer_fait(jour: int, activite_nom: str):
    """Marque une activité comme faite."""
    key = f"{date.today().isocalendar()[1]}_{jour}_{activite_nom}"
    st.session_state["jules_activites_faites"][key] = True


def est_fait(jour: int, activite_nom: str) -> bool:
    """Vérifie si une activité est faite."""
    key = f"{date.today().isocalendar()[1]}_{jour}_{activite_nom}"
    return st.session_state.get("jules_activites_faites", {}).get(key, False)


# ═══════════════════════════════════════════════════════════
# UI COMPONENTS
# ═══════════════════════════════════════════════════════════

def render_activite_card(jour: int, activite: dict, index: int):
    """Affiche une carte d'activité."""
    fait = est_fait(jour, activite["nom"])
    
    with st.container(border=True):
        col1, col2 = st.columns([4, 1])
        
        with col1:
            style = "text-decoration: line-through; opacity: 0.6;" if fait else ""
            st.markdown(
                f"<span style='{style}'>"
                f"**{activite['emoji']} {activite['nom']}**"
                f"</span>",
                unsafe_allow_html=True
            )
            st.caption(f"⏱️ {activite['duree']} min • {activite['desc']}")
        
        with col2:
            if fait:
                st.success("✅")
            else:
                if st.button("Fait ✓", key=f"act_{jour}_{index}", type="secondary"):
                    marquer_fait(jour, activite["nom"])
                    st.rerun()


def render_jour(jour_idx: int, nom_jour: str, activites: list[dict], est_aujourd_hui: bool):
    """Affiche un jour du planning."""
    header = f"{'📍 ' if est_aujourd_hui else ''}{nom_jour}"
    
    with st.expander(header, expanded=est_aujourd_hui):
        if not activites:
            st.caption("Pas d'activités planifiées")
            return
        
        # Stats du jour
        nb_faites = sum(1 for a in activites if est_fait(jour_idx, a["nom"]))
        if nb_faites == len(activites):
            st.success(f"🎉 Toutes les activités sont faites ! ({nb_faites}/{len(activites)})")
        else:
            st.progress(nb_faites / len(activites), text=f"{nb_faites}/{len(activites)} faites")
        
        # Activités
        for i, act in enumerate(activites):
            render_activite_card(jour_idx, act, i)


def render_vue_semaine():
    """Affiche la vue semaine complète."""
    st.subheader("📅 Planning de la semaine")
    
    age = get_age_jules_mois()
    st.caption(f"Activités adaptées pour {age} mois")
    
    planning = get_planning_semaine()
    today = date.today()
    jour_actuel = today.weekday()
    
    # Tabs par jour
    tabs = st.tabs(JOURS_SEMAINE)
    
    for jour_idx, tab in enumerate(tabs):
        with tab:
            render_jour(
                jour_idx, 
                JOURS_SEMAINE[jour_idx], 
                planning.get(jour_idx, []),
                jour_idx == jour_actuel
            )


def render_vue_aujourd_hui():
    """Affiche les activités du jour."""
    st.subheader("🌟 Aujourd'hui")
    
    today = date.today()
    jour_actuel = today.weekday()
    planning = get_planning_semaine()
    activites = planning.get(jour_actuel, [])
    
    st.markdown(f"**{JOURS_SEMAINE[jour_actuel]} {today.strftime('%d/%m')}**")
    
    if not activites:
        st.info("Pas d'activités planifiées pour aujourd'hui")
        return
    
    # Stats
    nb_faites = sum(1 for a in activites if est_fait(jour_actuel, a["nom"]))
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Activités", len(activites))
    with col2:
        st.metric("Faites", nb_faites)
    with col3:
        duree_totale = sum(a["duree"] for a in activites)
        st.metric("Durée totale", f"{duree_totale} min")
    
    st.divider()
    
    # Activités
    for i, act in enumerate(activites):
        render_activite_card(jour_actuel, act, i)


def render_categories():
    """Affiche toutes les catégories d'activités."""
    st.subheader("📚 Toutes les activités par catégorie")
    
    tabs = st.tabs([
        f"{info['emoji']} {cat.capitalize()}" 
        for cat, info in CATEGORIES_ACTIVITES.items()
    ])
    
    for tab, (cat, info) in zip(tabs, CATEGORIES_ACTIVITES.items()):
        with tab:
            st.markdown(f"**{info['emoji']} {cat.capitalize()}**")
            
            for act in info["activites"]:
                with st.container(border=True):
                    st.markdown(f"**{act['nom']}**")
                    st.caption(f"⏱️ {act['duree']} min • {act['desc']}")


def render_stats_semaine():
    """Affiche les stats de la semaine."""
    planning = get_planning_semaine()
    today = date.today()
    jour_actuel = today.weekday()
    
    total_activites = sum(len(acts) for acts in planning.values())
    total_faites = sum(
        1 for jour, acts in planning.items() 
        for act in acts if est_fait(jour, act["nom"])
    )
    
    st.subheader("📊 Bilan de la semaine")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total activités", total_activites)
    with col2:
        st.metric("Réalisées", total_faites)
    with col3:
        pct = (total_faites / total_activites * 100) if total_activites > 0 else 0
        st.metric("Progression", f"{pct:.0f}%")
    
    st.progress(total_faites / total_activites if total_activites > 0 else 0)
    
    # Par catégorie
    st.markdown("**Par catégorie:**")
    cat_stats = {}
    for acts in planning.values():
        for act in acts:
            cat = act["categorie"]
            if cat not in cat_stats:
                cat_stats[cat] = {"total": 0, "fait": 0}
            cat_stats[cat]["total"] += 1
    
    # Count faites
    for jour, acts in planning.items():
        for act in acts:
            if est_fait(jour, act["nom"]):
                cat_stats[act["categorie"]]["fait"] += 1
    
    cols = st.columns(3)
    for i, (cat, stats) in enumerate(cat_stats.items()):
        info = CATEGORIES_ACTIVITES.get(cat, {})
        with cols[i % 3]:
            pct = (stats["fait"] / stats["total"] * 100) if stats["total"] > 0 else 0
            st.metric(
                f"{info.get('emoji', '')} {cat.capitalize()}", 
                f"{stats['fait']}/{stats['total']}",
                f"{pct:.0f}%"
            )


# ═══════════════════════════════════════════════════════════
# PAGE PRINCIPALE
# ═══════════════════════════════════════════════════════════

def app():
    """Point d'entrée du module Planning Jules."""
    init_tracking()
    
    st.title("📅 Planning Activités Jules")
    
    age = get_age_jules_mois()
    st.caption(f"🎂 {age} mois • Planning d'éveil hebdomadaire")
    
    # Tabs principaux
    tabs = st.tabs(["🌟 Aujourd'hui", "📅 Semaine", "📊 Bilan", "📚 Catalogue"])
    
    with tabs[0]:
        render_vue_aujourd_hui()
    
    with tabs[1]:
        render_vue_semaine()
    
    with tabs[2]:
        render_stats_semaine()
    
    with tabs[3]:
        render_categories()


if __name__ == "__main__":
    app()

