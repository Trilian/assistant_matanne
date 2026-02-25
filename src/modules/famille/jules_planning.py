"""
Module Planning Semaine Jules - Activites d'eveil organisees par jour.

Pour un enfant de ~19 mois:
- Planning hebdomadaire d'activites
- Repartition equilibree (motricite, langage, creativite, exterieur)
- Suivi de ce qui a ete fait
- Suggestions IA personnalisees
"""

import random
from datetime import date

import streamlit as st

from src.core.constants import JOURS_SEMAINE
from src.core.monitoring.rerun_profiler import profiler_rerun
from src.core.session_keys import SK
from src.modules._framework import error_boundary
from src.ui.keys import KeyNamespace
from src.ui.state.url import tabs_with_url

_keys = KeyNamespace("jules_planning")

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
            {
                "nom": "Monter/descendre escalier",
                "duree": 10,
                "desc": "Avec aide, alterner les pieds",
            },
            {"nom": "Porteur/trotteur", "duree": 20, "desc": "Se deplacer dans la maison"},
            {"nom": "Yoga bebe", "duree": 10, "desc": "Imiter des postures animaux"},
        ],
    },
    "langage": {
        "emoji": "💬",
        "couleur": "#2196F3",
        "activites": [
            {"nom": "Lecture interactive", "duree": 15, "desc": "Pointer et nommer les images"},
            {
                "nom": "Comptines gestuelles",
                "duree": 10,
                "desc": "Ainsi font font, Petit escargot...",
            },
            {"nom": "Nommer les objets", "duree": 10, "desc": "Lors du bain, repas, habillage"},
            {"nom": "Imagier sonore", "duree": 10, "desc": "Sons animaux, vehicules"},
            {"nom": "Telephone jouet", "duree": 10, "desc": "Faire semblant de parler"},
            {"nom": "Chansons repetitives", "duree": 10, "desc": "La même chanson plusieurs fois"},
        ],
    },
    "creativite": {
        "emoji": "🎨",
        "couleur": "#FF9800",
        "activites": [
            {"nom": "Peinture au doigt", "duree": 20, "desc": "Sur grande feuille ou carton"},
            {"nom": "Pâte à modeler", "duree": 20, "desc": "Manipuler, ecraser, rouler"},
            {"nom": "Gommettes", "duree": 15, "desc": "Coller sur une feuille"},
            {"nom": "Dessin aux crayons", "duree": 15, "desc": "Gros crayons adaptes"},
            {"nom": "Pâte à sel", "duree": 20, "desc": "Faire des formes simples"},
            {"nom": "Collage", "duree": 15, "desc": "Coller des morceaux de papier"},
        ],
    },
    "sensoriel": {
        "emoji": "✋",
        "couleur": "#9C27B0",
        "activites": [
            {"nom": "Bac sensoriel", "duree": 20, "desc": "Riz, pâtes, sable kinetic"},
            {"nom": "Jeux d'eau", "duree": 20, "desc": "Transvaser, verser, eclabousser"},
            {"nom": "Textures à toucher", "duree": 10, "desc": "Doux, rugueux, lisse..."},
            {"nom": "Boîte à tresors", "duree": 15, "desc": "Explorer objets du quotidien"},
            {"nom": "Bulles de savon", "duree": 10, "desc": "Attraper, observer"},
            {"nom": "Cuisine sensorielle", "duree": 15, "desc": "Toucher fruits, legumes"},
        ],
    },
    "exterieur": {
        "emoji": "🌳",
        "couleur": "#795548",
        "activites": [
            {"nom": "Promenade nature", "duree": 30, "desc": "Observer, ramasser feuilles"},
            {"nom": "Bac à sable", "duree": 30, "desc": "Creuser, construire"},
            {"nom": "Arrosage plantes", "duree": 15, "desc": "Avec petit arrosoir"},
            {"nom": "Jeux au parc", "duree": 45, "desc": "Toboggan, balançoire"},
            {"nom": "Velo/draisienne", "duree": 20, "desc": "Dans le jardin ou parc"},
            {"nom": "Chasse aux tresors", "duree": 20, "desc": "Trouver des objets dehors"},
        ],
    },
    "imitation": {
        "emoji": "🎭",
        "couleur": "#E91E63",
        "activites": [
            {"nom": "Dînette", "duree": 20, "desc": "Preparer à manger, servir"},
            {"nom": "Poupee/doudou", "duree": 15, "desc": "Nourrir, coucher, promener"},
            {"nom": "Menage avec balai", "duree": 10, "desc": "Imiter papa/maman"},
            {"nom": "Telephone", "duree": 10, "desc": "Faire semblant d'appeler"},
            {"nom": "Voitures/garage", "duree": 20, "desc": "Faire rouler, garer"},
            {"nom": "Docteur", "duree": 15, "desc": "Soigner les doudous"},
        ],
    },
}

# Planning type de la semaine (equilibre)
PLANNING_SEMAINE_TYPE = {
    0: ["motricite", "langage", "creativite"],  # Lundi
    1: ["sensoriel", "imitation", "exterieur"],  # Mardi
    2: ["motricite", "creativite", "langage"],  # Mercredi
    3: ["exterieur", "sensoriel", "imitation"],  # Jeudi
    4: ["motricite", "langage", "creativite"],  # Vendredi
    5: ["exterieur", "imitation", "sensoriel"],  # Samedi
    6: ["creativite", "langage", "exterieur"],  # Dimanche
}


# ═══════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════


def get_age_jules_mois() -> int:
    """Retourne l'âge de Jules en mois (délègue à age_utils)."""
    from src.modules.famille.age_utils import get_age_jules_mois as _get

    return _get()


def generer_activites_jour(jour_semaine: int, seed: int | None = None) -> list[dict]:
    """Genère les activites pour un jour de la semaine."""
    if seed:
        random.seed(seed)

    categories_jour = PLANNING_SEMAINE_TYPE.get(jour_semaine, ["motricite", "langage"])
    activites = []

    for cat in categories_jour:
        cat_info = CATEGORIES_ACTIVITES.get(cat, {})
        if cat_info.get("activites"):
            activite = random.choice(cat_info["activites"])
            activites.append(
                {
                    "categorie": cat,
                    "emoji": cat_info["emoji"],
                    "couleur": cat_info["couleur"],
                    **activite,
                }
            )

    return activites


def get_planning_semaine() -> dict[int, list[dict]]:
    """Genère le planning de la semaine courante."""
    today = date.today()
    # Seed base sur la semaine pour consistance
    week_seed = today.isocalendar()[1] * 100 + today.year

    planning = {}
    for jour in range(7):
        planning[jour] = generer_activites_jour(jour, seed=week_seed + jour)

    return planning


# ═══════════════════════════════════════════════════════════
# SESSION STATE - TRACKING
# ═══════════════════════════════════════════════════════════


def init_tracking():
    """Initialise le tracking des activites faites."""
    if SK.JULES_ACTIVITES_FAITES not in st.session_state:
        st.session_state[SK.JULES_ACTIVITES_FAITES] = {}


def marquer_fait(jour: int, activite_nom: str):
    """Marque une activite comme faite."""
    key = f"{date.today().isocalendar()[1]}_{jour}_{activite_nom}"
    st.session_state[SK.JULES_ACTIVITES_FAITES][key] = True


def est_fait(jour: int, activite_nom: str) -> bool:
    """Verifie si une activite est faite."""
    key = f"{date.today().isocalendar()[1]}_{jour}_{activite_nom}"
    return st.session_state.get(SK.JULES_ACTIVITES_FAITES, {}).get(key, False)


# ═══════════════════════════════════════════════════════════
# UI COMPONENTS
# ═══════════════════════════════════════════════════════════


def afficher_activite_card(jour: int, activite: dict, index: int, key_prefix: str = "week"):
    """Affiche une carte d'activite."""
    fait = est_fait(jour, activite["nom"])

    with st.container(border=True):
        col1, col2 = st.columns([4, 1])

        with col1:
            style = "text-decoration: line-through; opacity: 0.6;" if fait else ""
            st.markdown(
                f"<span style='{style}'>**{activite['emoji']} {activite['nom']}**</span>",
                unsafe_allow_html=True,
            )
            st.caption(f"⏱️ {activite['duree']} min • {activite['desc']}")

        with col2:
            if fait:
                st.success("✅")
            else:
                if st.button("Fait ✓", key=f"act_{key_prefix}_{jour}_{index}", type="secondary"):
                    marquer_fait(jour, activite["nom"])
                    st.rerun()


def afficher_jour(jour_idx: int, nom_jour: str, activites: list[dict], est_aujourd_hui: bool):
    """Affiche un jour du planning."""
    header = f"{'📍 ' if est_aujourd_hui else ''}{nom_jour}"

    with st.expander(header, expanded=est_aujourd_hui):
        if not activites:
            st.caption("Pas d'activites planifiees")
            return

        # Stats du jour
        nb_faites = sum(1 for a in activites if est_fait(jour_idx, a["nom"]))
        if nb_faites == len(activites):
            st.success(f"🎉 Toutes les activites sont faites ! ({nb_faites}/{len(activites)})")
        else:
            st.progress(nb_faites / len(activites), text=f"{nb_faites}/{len(activites)} faites")

        # Activites
        for i, act in enumerate(activites):
            afficher_activite_card(jour_idx, act, i)


def afficher_vue_semaine():
    """Affiche la vue semaine complète."""
    st.subheader("📅 Planning de la semaine")

    age = get_age_jules_mois()
    st.caption(f"Activites adaptees pour {age} mois")

    planning = get_planning_semaine()
    today = date.today()
    jour_actuel = today.weekday()

    # Tabs par jour
    tabs = st.tabs(JOURS_SEMAINE)

    for jour_idx, tab in enumerate(tabs):
        with tab:
            afficher_jour(
                jour_idx,
                JOURS_SEMAINE[jour_idx],
                planning.get(jour_idx, []),
                jour_idx == jour_actuel,
            )


def afficher_vue_aujourd_hui():
    """Affiche les activites du jour."""
    st.subheader("🌟 Aujourd'hui")

    today = date.today()
    jour_actuel = today.weekday()
    planning = get_planning_semaine()
    activites = planning.get(jour_actuel, [])

    st.markdown(f"**{JOURS_SEMAINE[jour_actuel]} {today.strftime('%d/%m')}**")

    if not activites:
        st.info("Pas d'activites planifiees pour aujourd'hui")
        return

    # Stats
    nb_faites = sum(1 for a in activites if est_fait(jour_actuel, a["nom"]))
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Activites", len(activites))
    with col2:
        st.metric("Faites", nb_faites)
    with col3:
        duree_totale = sum(a["duree"] for a in activites)
        st.metric("Duree totale", f"{duree_totale} min")

    st.divider()

    # Activites
    for i, act in enumerate(activites):
        afficher_activite_card(jour_actuel, act, i, key_prefix="today")


def afficher_categories():
    """Affiche toutes les categories d'activites."""
    st.subheader("📚 Toutes les activites par categorie")

    tabs = st.tabs(
        [f"{info['emoji']} {cat.capitalize()}" for cat, info in CATEGORIES_ACTIVITES.items()]
    )

    for tab, (cat, info) in zip(tabs, CATEGORIES_ACTIVITES.items(), strict=False):
        with tab:
            st.markdown(f"**{info['emoji']} {cat.capitalize()}**")

            for act in info["activites"]:
                with st.container(border=True):
                    st.markdown(f"**{act['nom']}**")
                    st.caption(f"⏱️ {act['duree']} min • {act['desc']}")


def afficher_stats_semaine():
    """Affiche les stats de la semaine."""
    planning = get_planning_semaine()

    total_activites = sum(len(acts) for acts in planning.values())
    total_faites = sum(
        1 for jour, acts in planning.items() for act in acts if est_fait(jour, act["nom"])
    )

    st.subheader("📊 Bilan de la semaine")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total activites", total_activites)
    with col2:
        st.metric("Realisees", total_faites)
    with col3:
        pct = (total_faites / total_activites * 100) if total_activites > 0 else 0
        st.metric("Progression", f"{pct:.0f}%")

    st.progress(total_faites / total_activites if total_activites > 0 else 0)

    # Par categorie
    st.markdown("**Par categorie:**")
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
                f"{pct:.0f}%",
            )


# ═══════════════════════════════════════════════════════════
# PAGE PRINCIPALE
# ═══════════════════════════════════════════════════════════


@profiler_rerun("jules_planning")
def app():
    """Point d'entree du module Planning Jules."""
    init_tracking()

    st.title("📅 Planning Activites Jules")

    age = get_age_jules_mois()
    st.caption(f"🎂 {age} mois • Planning d'eveil hebdomadaire")

    # Tabs principaux
    TAB_LABELS = ["🌟 Aujourd'hui", "📅 Semaine", "📊 Bilan", "📚 Catalogue"]
    tabs_with_url(TAB_LABELS, param="tab")
    tabs = st.tabs(TAB_LABELS)

    with tabs[0]:
        with error_boundary(titre="Erreur vue aujourd'hui"):
            afficher_vue_aujourd_hui()

    with tabs[1]:
        with error_boundary(titre="Erreur vue semaine"):
            afficher_vue_semaine()

    with tabs[2]:
        with error_boundary(titre="Erreur bilan"):
            afficher_stats_semaine()

    with tabs[3]:
        with error_boundary(titre="Erreur catalogue"):
            afficher_categories()


if __name__ == "__main__":
    app()
