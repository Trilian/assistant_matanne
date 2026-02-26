"""
Mini-calendrier de la semaine intégré au dashboard.

Affiche une vue compacte lun→dim avec:
- Pastilles colorées par type d'événement
- Jour courant mis en évidence
- Nombre d'événements par jour
- Détails au clic/expansion
"""

import logging
from datetime import date, datetime, timedelta

import streamlit as st

from src.ui.engine import StyleSheet
from src.ui.fragments import cached_fragment
from src.ui.keys import KeyNamespace
from src.ui.tokens import Couleur, Espacement, Rayon
from src.ui.tokens_semantic import Sem

logger = logging.getLogger(__name__)

_keys = KeyNamespace("mini_calendrier")

# Couleurs par type d'événement
COULEURS_TYPES = {
    "repas": "#4CAF50",  # Vert
    "medical": "#F44336",  # Rouge
    "activite": "#2196F3",  # Bleu
    "menage": "#FF9800",  # Orange
    "famille": "#9C27B0",  # Violet
    "ferie": "#EF5350",  # Rouge drapeau
    "creche": "#FFB74D",  # Orange chaud
    "pont": "#CE93D8",  # Violet doux
    "autre": "#757575",  # Gris
}

JOURS_COURTS = ["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"]


# ═══════════════════════════════════════════════════════════
# LOGIQUE MÉTIER
# ═══════════════════════════════════════════════════════════


def _obtenir_semaine() -> list[date]:
    """Retourne les 7 dates de la semaine courante (lundi → dimanche)."""
    aujourdhui = date.today()
    lundi = aujourdhui - timedelta(days=aujourdhui.weekday())
    return [lundi + timedelta(days=i) for i in range(7)]


def _classifier_evenement(event: dict) -> str:
    """Classifie un événement par type pour la couleur."""
    titre = (event.get("titre", "") + " " + event.get("type", "")).lower()

    if any(mot in titre for mot in ["repas", "déjeuner", "dîner", "cuisine", "batch"]):
        return "repas"
    if any(mot in titre for mot in ["médecin", "pédiatre", "docteur", "rdv", "santé"]):
        return "medical"
    if any(mot in titre for mot in ["activité", "parc", "sortie", "sport", "promenade"]):
        return "activite"
    if any(mot in titre for mot in ["ménage", "nettoyage", "entretien", "lessive"]):
        return "menage"
    if any(mot in titre for mot in ["famille", "anniversaire", "fête"]):
        return "famille"
    return "autre"


def _charger_evenements_semaine() -> dict[str, list[dict]]:
    """Charge les événements de la semaine groupés par date.

    Returns:
        Dict {date_iso: [liste d'événements]}.
    """
    semaine = _obtenir_semaine()
    debut = semaine[0]
    fin = semaine[-1] + timedelta(days=1)

    events_par_jour: dict[str, list[dict]] = {d.isoformat(): [] for d in semaine}

    # Événements calendrier/planning
    try:
        from src.modules.planning.timeline_ui import charger_events_periode

        events = charger_events_periode(debut, fin)
        if events:
            for event in events:
                date_event = None
                if hasattr(event.get("date_debut"), "date"):
                    date_event = event["date_debut"].date()
                elif hasattr(event.get("date_debut"), "isoformat"):
                    date_event = event["date_debut"]

                if date_event:
                    key = date_event.isoformat()
                    if key in events_par_jour:
                        event["type_couleur"] = _classifier_evenement(event)
                        events_par_jour[key].append(event)
    except Exception as e:
        logger.debug(f"Événements timeline indisponibles: {e}")

    # Repas planifiés
    try:
        from src.core.db import obtenir_contexte_db
        from src.core.models import PlanningRepas

        with obtenir_contexte_db() as session:
            repas = (
                session.query(PlanningRepas)
                .filter(
                    PlanningRepas.date_repas >= debut,
                    PlanningRepas.date_repas <= fin,
                )
                .all()
            )
            for r in repas:
                key = r.date_repas.isoformat()
                if key in events_par_jour:
                    nom_recette = r.recette.nom if r.recette else r.type_repas
                    events_par_jour[key].append(
                        {
                            "titre": f"🍽️ {r.type_repas}: {nom_recette}",
                            "type_couleur": "repas",
                        }
                    )
    except Exception as e:
        logger.debug(f"Repas planifiés indisponibles: {e}")

    # Tâches ménage planifiées
    try:
        from src.services.accueil_data_service import get_accueil_data_service

        taches = get_accueil_data_service().get_taches_en_retard(limit=20)
        if taches:
            for t in taches:
                if t.get("prochaine_date"):
                    key = (
                        t["prochaine_date"].isoformat()
                        if hasattr(t["prochaine_date"], "isoformat")
                        else ""
                    )
                    if key in events_par_jour:
                        events_par_jour[key].append(
                            {
                                "titre": f"🧹 {t['nom']}",
                                "type_couleur": "menage",
                            }
                        )
    except Exception:
        pass

    # Jours spéciaux (fériés, fermetures crèche, ponts)
    try:
        from src.services.famille.jours_speciaux import obtenir_service_jours_speciaux

        service_js = obtenir_service_jours_speciaux()
        jours_speciaux = service_js.jours_speciaux_semaine(debut)

        for js in jours_speciaux:
            key = js.date_jour.isoformat()
            if key in events_par_jour:
                icone = {"ferie": "🇫🇷", "creche": "🏫", "pont": "🌉"}.get(js.type, "📅")
                events_par_jour[key].insert(
                    0,
                    {
                        "titre": f"{icone} {js.nom}",
                        "type_couleur": js.type,
                    },
                )
    except Exception as e:
        logger.debug(f"Jours spéciaux indisponibles: {e}")

    return events_par_jour


# ═══════════════════════════════════════════════════════════
# WIDGET UI
# ═══════════════════════════════════════════════════════════


@cached_fragment(ttl=300)  # Cache 5 min
def afficher_mini_calendrier():
    """Affiche le mini-calendrier de la semaine."""
    semaine = _obtenir_semaine()
    aujourdhui = date.today()
    events_semaine = _charger_evenements_semaine()

    st.markdown("### 📅 Ma semaine")

    # ── Barre des 7 jours ──
    cols = st.columns(7)

    for i, (jour_date, col) in enumerate(zip(semaine, cols, strict=True)):
        est_aujourdhui = jour_date == aujourdhui
        est_passe = jour_date < aujourdhui
        events_jour = events_semaine.get(jour_date.isoformat(), [])
        nb_events = len(events_jour)

        with col:
            # Styles conditionnels
            if est_aujourdhui:
                bg = f"linear-gradient(135deg, {Couleur.ACCENT}, {Couleur.ACCENT}CC)"
                text_color = "#FFFFFF"
                border = f"2px solid {Couleur.ACCENT}"
                font_weight = "bold"
            elif est_passe:
                bg = Sem.SURFACE_ALT
                text_color = Sem.ON_SURFACE_SECONDARY
                border = "1px solid transparent"
                font_weight = "normal"
            else:
                bg = Sem.SURFACE_ALT
                text_color = Sem.ON_SURFACE
                border = "1px solid transparent"
                font_weight = "500"

            # Pastilles de couleurs (max 4)
            pastilles = ""
            types_vus = set()
            for event in events_jour[:4]:
                type_ev = event.get("type_couleur", "autre")
                if type_ev not in types_vus:
                    types_vus.add(type_ev)
                    couleur = COULEURS_TYPES.get(type_ev, "#757575")
                    pastilles += (
                        f'<span style="display:inline-block;width:6px;height:6px;'
                        f'border-radius:50%;background:{couleur};margin:0 1px;"></span>'
                    )

            # Indicateur nombre d'événements
            badge = ""
            if nb_events > 0:
                badge = (
                    f'<span style="display:inline-block;background:{Couleur.ACCENT};'
                    f"color:#fff;border-radius:50%;width:18px;height:18px;"
                    f"font-size:0.7rem;line-height:18px;text-align:center;"
                    f'margin-top:2px;">{nb_events}</span>'
                )

            st.markdown(
                f'<div style="text-align:center;padding:8px 4px;'
                f"background:{bg};border:{border};border-radius:10px;"
                f'cursor:pointer;">'
                f'<div style="font-size:0.75rem;color:{text_color};font-weight:{font_weight};">'
                f"{JOURS_COURTS[i]}</div>"
                f'<div style="font-size:1.1rem;color:{text_color};font-weight:{font_weight};">'
                f"{jour_date.day}</div>"
                f'<div style="margin-top:2px;">{pastilles}</div>'
                f"{badge}"
                f"</div>",
                unsafe_allow_html=True,
            )

    # ── Détails du jour sélectionné (aujourd'hui par défaut) ──
    events_aujourdhui = events_semaine.get(aujourdhui.isoformat(), [])

    if events_aujourdhui:
        with st.expander(
            f"📋 Aujourd'hui — {len(events_aujourdhui)} événement(s)",
            expanded=False,
        ):
            for event in events_aujourdhui:
                type_ev = event.get("type_couleur", "autre")
                couleur = COULEURS_TYPES.get(type_ev, "#757575")
                titre = event.get("titre", "Événement")

                heure = ""
                if hasattr(event.get("date_debut"), "strftime"):
                    heure = event["date_debut"].strftime("%H:%M") + " "

                st.markdown(
                    f'<div style="padding:4px 8px;margin:2px 0;'
                    f"border-left:3px solid {couleur};border-radius:3px;"
                    f'background:{Sem.SURFACE_ALT};">'
                    f"<small><strong>{heure}</strong>{titre}</small>"
                    f"</div>",
                    unsafe_allow_html=True,
                )

    # Légende compacte
    legende_items = " ".join(
        f'<span style="display:inline-flex;align-items:center;margin-right:8px;">'
        f'<span style="display:inline-block;width:8px;height:8px;'
        f'border-radius:50%;background:{couleur};margin-right:3px;"></span>'
        f'<span style="font-size:0.7rem;color:{Sem.ON_SURFACE_SECONDARY};">{label}</span>'
        f"</span>"
        for label, couleur in [
            ("Repas", COULEURS_TYPES["repas"]),
            ("Médical", COULEURS_TYPES["medical"]),
            ("Activité", COULEURS_TYPES["activite"]),
            ("Ménage", COULEURS_TYPES["menage"]),
            ("Férié", COULEURS_TYPES["ferie"]),
            ("Crèche", COULEURS_TYPES["creche"]),
        ]
    )
    st.markdown(
        f'<div style="text-align:center;margin-top:4px;">{legende_items}</div>',
        unsafe_allow_html=True,
    )

    # ── Prochains jours spéciaux ──
    _afficher_prochains_jours_speciaux()

    # ── Rappels haute priorité ──
    _afficher_rappels_urgents()


def _afficher_prochains_jours_speciaux():
    """Affiche les prochains jours spéciaux à venir."""
    try:
        from src.services.famille.jours_speciaux import obtenir_service_jours_speciaux

        service = obtenir_service_jours_speciaux()
        prochains = service.prochains_jours_speciaux(nb=3)

        if prochains:
            items_html = ""
            for js in prochains:
                icone = {"ferie": "🇫🇷", "creche": "🏫", "pont": "🌉"}.get(js.type, "📅")
                delta = (js.date_jour - date.today()).days

                if delta == 0:
                    quand = "aujourd'hui"
                elif delta == 1:
                    quand = "demain"
                else:
                    quand = f"dans {delta}j"

                items_html += (
                    f'<span style="display:inline-flex;align-items:center;margin-right:12px;'
                    f'font-size:0.8rem;">'
                    f'{icone} <strong style="margin:0 3px;">{js.nom}</strong> '
                    f'<span style="color:{Sem.ON_SURFACE_SECONDARY};">({quand})</span>'
                    f"</span>"
                )

            st.markdown(
                f'<div style="margin-top:8px;padding:6px 10px;'
                f"background:{Sem.SURFACE_ALT};border-radius:8px;"
                f'overflow-x:auto;white-space:nowrap;">'
                f"{items_html}</div>",
                unsafe_allow_html=True,
            )
    except Exception as e:
        logger.debug(f"Prochains jours spéciaux: {e}")


def _afficher_rappels_urgents():
    """Affiche les rappels haute priorité dans les 24h."""
    try:
        from src.services.planning.rappels import obtenir_service_rappels

        service = obtenir_service_rappels()
        rappels = service.rappels_priorite_haute(heures=24)

        if rappels:
            with st.expander(
                f"🔔 {len(rappels)} rappel(s) important(s)",
                expanded=len(rappels) <= 3,
            ):
                for r in rappels[:5]:
                    st.markdown(
                        f'<div style="padding:4px 8px;margin:2px 0;'
                        f"border-left:3px solid #F44336;border-radius:3px;"
                        f'background:{Sem.SURFACE_ALT};">'
                        f"<small>{r.icone} <strong>{r.message}</strong> "
                        f'— <span style="color:{Sem.ON_SURFACE_SECONDARY};">'
                        f"{r.delai_str}</span></small>"
                        f"</div>",
                        unsafe_allow_html=True,
                    )
    except Exception as e:
        logger.debug(f"Rappels urgents: {e}")


__all__ = ["afficher_mini_calendrier"]
