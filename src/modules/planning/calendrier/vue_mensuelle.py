"""
Vue mensuelle du calendrier familial.

Affiche un calendrier mensuel compact avec:
- Grille 7 colonnes (lun→dim)
- Pastilles colorées par type d'événement
- Indicateurs de charge par jour
- Jours spéciaux marqués visuellement
- Navigation mois par mois
- Clic sur un jour → semaine correspondante
"""

import calendar
import logging
from datetime import date, timedelta

import streamlit as st

from src.core.constants import JOURS_SEMAINE_COURT
from src.ui.keys import KeyNamespace
from src.ui.tokens import Couleur

from .types import TypeEvenement

logger = logging.getLogger(__name__)

_keys = KeyNamespace("vue_mensuelle")

# Mapping TypeEvenement → couleur pastille
_COULEUR_PASTILLE = {
    TypeEvenement.REPAS_MIDI: "#4CAF50",
    TypeEvenement.REPAS_SOIR: "#4CAF50",
    TypeEvenement.RDV_MEDICAL: "#F44336",
    TypeEvenement.ACTIVITE: "#2196F3",
    TypeEvenement.COURSES: "#4DD0E1",
    TypeEvenement.BATCH_COOKING: "#81C784",
    TypeEvenement.MENAGE: "#FF9800",
    TypeEvenement.FERIE: "#EF5350",
    TypeEvenement.CRECHE: "#FFB74D",
    TypeEvenement.PONT: "#CE93D8",
}


def afficher_vue_mensuelle():
    """Affiche la vue mensuelle complète avec navigation."""

    # Navigation mois
    if "vue_mois_annee" not in st.session_state:
        st.session_state.vue_mois_annee = date.today().year
    if "vue_mois_mois" not in st.session_state:
        st.session_state.vue_mois_mois = date.today().month

    annee = st.session_state.vue_mois_annee
    mois = st.session_state.vue_mois_mois

    # Barre de navigation
    col_prev, col_titre, col_next = st.columns([1, 3, 1])

    with col_prev:
        if st.button("Mois", key=_keys("prev_mois"), use_container_width=True):
            if mois == 1:
                st.session_state.vue_mois_mois = 12
                st.session_state.vue_mois_annee = annee - 1
            else:
                st.session_state.vue_mois_mois = mois - 1
            st.rerun()

    with col_titre:
        noms_mois = [
            "",
            "Janvier",
            "Février",
            "Mars",
            "Avril",
            "Mai",
            "Juin",
            "Juillet",
            "Août",
            "Septembre",
            "Octobre",
            "Novembre",
            "Décembre",
        ]
        st.markdown(
            f"<h3 style='text-align:center;margin:0;'>📅 {noms_mois[mois]} {annee}</h3>",
            unsafe_allow_html=True,
        )

    with col_next:
        if st.button("Mois", key=_keys("next_mois"), use_container_width=True):
            if mois == 12:
                st.session_state.vue_mois_mois = 1
                st.session_state.vue_mois_annee = annee + 1
            else:
                st.session_state.vue_mois_mois = mois + 1
            st.rerun()

    # Bouton aujourd'hui
    col_spacer, col_today, col_spacer2 = st.columns([2, 1, 2])
    with col_today:
        if st.button("📍 Aujourd'hui", key=_keys("today"), use_container_width=True):
            st.session_state.vue_mois_annee = date.today().year
            st.session_state.vue_mois_mois = date.today().month
            st.rerun()

    st.divider()

    # Charger les données du mois
    donnees_mois = _charger_donnees_mois(annee, mois)

    # Grille calendrier
    _afficher_grille_mois(annee, mois, donnees_mois)

    # Statistiques mensuelles
    _afficher_stats_mois(donnees_mois)

    # Légende
    _afficher_legende()


def _charger_donnees_mois(annee: int, mois: int) -> dict[date, dict]:
    """Charge les données agrégées pour chaque jour du mois.

    Returns:
        Dict {date: {nb_events: int, types: set, charge: int, jours_speciaux: list}}
    """
    premier = date(annee, mois, 1)
    if mois == 12:
        dernier = date(annee + 1, 1, 1) - timedelta(days=1)
    else:
        dernier = date(annee, mois + 1, 1) - timedelta(days=1)

    donnees: dict[date, dict] = {}

    # Initialiser chaque jour
    current = premier
    while current <= dernier:
        donnees[current] = {
            "nb_events": 0,
            "types": set(),
            "charge": 0,
            "jours_speciaux": [],
            "titres": [],
        }
        current += timedelta(days=1)

    # Charger les événements semaine par semaine
    try:
        from src.core.date_utils import obtenir_debut_semaine

        from .aggregation import construire_semaine_calendrier
        from .data import charger_donnees_semaine

        # Trouver les semaines qui couvrent le mois
        debut_semaine = obtenir_debut_semaine(premier)
        while debut_semaine <= dernier:
            try:
                raw = charger_donnees_semaine(debut_semaine)
                semaine = construire_semaine_calendrier(
                    date_debut=debut_semaine,
                    repas=raw.get("repas", []),
                    sessions_batch=raw.get("sessions_batch", []),
                    activites=raw.get("activites", []),
                    events=raw.get("events", []),
                    courses_planifiees=raw.get("courses_planifiees", []),
                    taches_menage=raw.get("taches_menage", []),
                )

                for jour in semaine.jours:
                    if jour.date_jour in donnees:
                        donnees[jour.date_jour] = {
                            "nb_events": jour.nb_evenements,
                            "types": {e.type for e in jour.evenements},
                            "charge": jour.charge_score,
                            "jours_speciaux": jour.jours_speciaux,
                            "titres": [e.titre for e in jour.evenements[:5]],
                        }
            except Exception as e:
                logger.debug(f"Erreur chargement semaine {debut_semaine}: {e}")

            debut_semaine += timedelta(days=7)

    except Exception as e:
        logger.warning(f"Impossible de charger les données du mois: {e}")

    return donnees


def _afficher_grille_mois(
    annee: int,
    mois: int,
    donnees: dict[date, dict],
):
    """Affiche la grille mensuelle 7 colonnes."""
    aujourdhui = date.today()

    # En-têtes des jours
    cols_header = st.columns(7)
    for i, col in enumerate(cols_header):
        with col:
            st.markdown(
                f"<div style='text-align:center;font-weight:bold;"
                f"font-size:0.85rem;color:#666;'>"
                f"{JOURS_SEMAINE_COURT[i]}</div>",
                unsafe_allow_html=True,
            )

    # Calculer les semaines du mois
    cal = calendar.Calendar(firstweekday=0)  # Lundi = 0
    semaines = cal.monthdayscalendar(annee, mois)

    for semaine in semaines:
        cols = st.columns(7)

        for i, jour_num in enumerate(semaine):
            with cols[i]:
                if jour_num == 0:
                    # Jour hors du mois
                    st.markdown(
                        "<div style='height:70px;'></div>",
                        unsafe_allow_html=True,
                    )
                    continue

                jour_date = date(annee, mois, jour_num)
                data = donnees.get(jour_date, {})
                est_aujourdhui = jour_date == aujourdhui
                est_weekend = i >= 5

                _afficher_cellule_mois(jour_date, data, est_aujourdhui, est_weekend)


def _afficher_cellule_mois(
    jour_date: date,
    data: dict,
    est_aujourdhui: bool,
    est_weekend: bool,
):
    """Affiche une cellule de jour dans la grille mensuelle."""
    nb = data.get("nb_events", 0)
    types_evt = data.get("types", set())
    charge = data.get("charge", 0)
    jours_speciaux = data.get("jours_speciaux", [])
    titres = data.get("titres", [])

    # Styles conditionnels
    if est_aujourdhui:
        bg = f"linear-gradient(135deg, {Couleur.ACCENT}20, {Couleur.ACCENT}10)"
        border = f"2px solid {Couleur.ACCENT}"
        num_color = Couleur.ACCENT
    elif jours_speciaux:
        bg = "#FFF3E0"  # Orange très clair pour jours spéciaux
        border = f"1px solid {Couleur.CAL_FERIE}80"
        num_color = Couleur.CAL_FERIE
    elif est_weekend:
        bg = "#f5f5f5"
        border = "1px solid transparent"
        num_color = "#888"
    else:
        bg = "transparent"
        border = "1px solid transparent"
        num_color = "#333"

    # Pastilles de couleurs (types d'événements du jour)
    pastilles = ""
    types_vus = set()
    for t in list(types_evt)[:5]:
        if t not in types_vus:
            types_vus.add(t)
            couleur = _COULEUR_PASTILLE.get(t, "#757575")
            pastilles += (
                f'<span style="display:inline-block;width:5px;height:5px;'
                f'border-radius:50%;background:{couleur};margin:0 1px;"></span>'
            )

    # Charge indicator
    charge_indicator = ""
    if charge >= 60:
        charge_indicator = "🔴"
    elif charge >= 40:
        charge_indicator = "🟡"
    elif nb > 0:
        charge_indicator = "🟢"

    # Badge nombre
    badge = ""
    if nb > 0:
        badge = f'<span style="font-size:0.6rem;color:#888;">{nb}</span>'

    # Jours spéciaux icône
    special_icon = ""
    for js in jours_speciaux[:1]:
        t = js.type.value if hasattr(js.type, "value") else str(js.type)
        icone = {"ferie": "🇫🇷", "creche": "🏫", "pont": "🌉"}.get(t, "")
        if icone:
            special_icon = f'<span style="font-size:0.65rem;">{icone}</span>'

    # Tooltip
    tooltip_text = ""
    if titres:
        tooltip_text = " | ".join(titres[:3])
        if len(titres) > 3:
            tooltip_text += f" +{len(titres) - 3}"

    st.markdown(
        f'<div style="text-align:center;padding:3px 2px;height:70px;'
        f"background:{bg};border:{border};border-radius:8px;"
        f'cursor:pointer;" title="{tooltip_text}">'
        f'<div style="font-size:0.9rem;color:{num_color};font-weight:600;">'
        f"{jour_date.day} {special_icon}</div>"
        f'<div style="margin-top:1px;">{pastilles}</div>'
        f'<div style="margin-top:1px;">{charge_indicator} {badge}</div>'
        f"</div>",
        unsafe_allow_html=True,
    )

    # Bouton invisible pour naviguer vers cette semaine
    if st.button(
        "→",
        key=_keys(f"goto_{jour_date.isoformat()}"),
        help=f"Voir la semaine du {jour_date.strftime('%d/%m')}",
        use_container_width=True,
    ):
        from src.core.date_utils import obtenir_debut_semaine

        st.session_state.cal_semaine_debut = obtenir_debut_semaine(jour_date)
        st.rerun()


def _afficher_stats_mois(donnees: dict[date, dict]):
    """Affiche les statistiques agrégées du mois."""
    if not donnees:
        return

    total_events = sum(d.get("nb_events", 0) for d in donnees.values())
    jours_avec_events = sum(1 for d in donnees.values() if d.get("nb_events", 0) > 0)
    jours_speciaux_count = sum(1 for d in donnees.values() if d.get("jours_speciaux"))
    charge_moy = 0
    charges = [d.get("charge", 0) for d in donnees.values() if d.get("nb_events", 0) > 0]
    if charges:
        charge_moy = sum(charges) / len(charges)
    jours_intenses = sum(1 for c in charges if c >= 60)

    # Compter les types d'événements distincts
    tous_types: set[TypeEvenement] = set()
    for d in donnees.values():
        tous_types.update(d.get("types", set()))

    with st.expander(f"📊 Résumé du mois — {total_events} événements", expanded=False):
        col1, col2, col3, col4, col5 = st.columns(5)

        with col1:
            st.metric("📅 Événements", total_events)
        with col2:
            st.metric("📆 Jours actifs", f"{jours_avec_events}/{len(donnees)}")
        with col3:
            st.metric("⚡ Charge moy.", f"{charge_moy:.0f}%")
        with col4:
            st.metric("🔴 Jours intenses", jours_intenses)
        with col5:
            st.metric("🎌 Jours spéciaux", jours_speciaux_count)

        # Types d'événements présents
        if tous_types:
            types_str = ", ".join(
                f"{_COULEUR_PASTILLE_EMOJI.get(t, '•')} {t.value}"
                for t in sorted(tous_types, key=lambda x: x.value)
            )
            st.caption(f"Types présents : {types_str}")


# Emoji par type pour le résumé
_COULEUR_PASTILLE_EMOJI = {
    TypeEvenement.REPAS_MIDI: "🍽️",
    TypeEvenement.REPAS_SOIR: "🍽️",
    TypeEvenement.RDV_MEDICAL: "🏥",
    TypeEvenement.ACTIVITE: "🎨",
    TypeEvenement.COURSES: "🛒",
    TypeEvenement.BATCH_COOKING: "🍳",
    TypeEvenement.MENAGE: "🧹",
    TypeEvenement.FERIE: "🇫🇷",
    TypeEvenement.CRECHE: "🏫",
    TypeEvenement.PONT: "🌉",
}


def _afficher_legende():
    """Affiche la légende de la vue mensuelle."""
    st.divider()

    items = [
        ("🟢 Normal", "Charge < 40%"),
        ("🟡 Modéré", "Charge 40-60%"),
        ("🔴 Intense", "Charge > 60%"),
        ("🇫🇷 Férié", "Jour férié"),
        ("🏫 Crèche", "Crèche fermée"),
        ("🌉 Pont", "Jour de pont"),
    ]

    cols = st.columns(len(items))
    for col, (label, desc) in zip(cols, items, strict=False):
        with col:
            st.caption(f"{label}\n{desc}")


__all__ = ["afficher_vue_mensuelle"]
