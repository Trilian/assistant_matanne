"""
Résumé matinal IA personnalisé pour le dashboard.

Génère un message d'accueil personnalisé qui agrège:
- Météo du jour
- Repas planifiés
- Événements à venir
- Stocks critiques
- Infos Jules (âge, RDV)
- Tâches en retard
"""

import logging
from datetime import date, datetime, timedelta

import streamlit as st

from src.ui.fragments import cached_fragment
from src.ui.keys import KeyNamespace
from src.ui.tokens import Couleur, Rayon
from src.ui.tokens_semantic import Sem

logger = logging.getLogger(__name__)

_keys = KeyNamespace("resume_matinal")


# ═══════════════════════════════════════════════════════════
# COLLECTE DES DONNÉES DU JOUR
# ═══════════════════════════════════════════════════════════


def _collecter_donnees_jour() -> dict:
    """Collecte toutes les données nécessaires au résumé matinal."""
    donnees = {
        "date": date.today(),
        "heure": datetime.now().hour,
        "meteo": None,
        "repas_midi": None,
        "repas_soir": None,
        "evenements_jour": [],
        "evenements_demain": [],
        "stocks_bas": [],
        "taches_retard": 0,
        "jules_age_mois": 0,
        "jules_rdv": [],
    }

    # Météo
    try:
        from src.services.integrations.weather import obtenir_service_meteo

        previsions = obtenir_service_meteo().get_previsions(nb_jours=1)
        if previsions:
            meteo = previsions[0]
            donnees["meteo"] = {
                "temp_max": meteo.temperature_max,
                "temp_min": meteo.temperature_min,
                "condition": meteo.condition,
                "icone": meteo.icone,
                "pluie": meteo.probabilite_pluie,
            }
    except Exception as e:
        logger.debug(f"Météo indisponible: {e}")

    # Repas planifiés
    try:
        from src.core.db import obtenir_contexte_db
        from src.core.models import PlanningRepas

        aujourdhui = date.today()
        with obtenir_contexte_db() as session:
            repas = (
                session.query(PlanningRepas).filter(PlanningRepas.date_repas == aujourdhui).all()
            )
            for r in repas:
                nom = r.recette.nom if r.recette else "Non défini"
                if r.type_repas == "dejeuner":
                    donnees["repas_midi"] = nom
                elif r.type_repas == "diner":
                    donnees["repas_soir"] = nom
    except Exception as e:
        logger.debug(f"Planning repas indisponible: {e}")

    # Événements du jour et demain
    try:
        from src.modules.planning.timeline_ui import charger_events_periode

        aujourdhui = date.today()
        demain = aujourdhui + timedelta(days=1)

        events_jour = charger_events_periode(aujourdhui, aujourdhui + timedelta(days=1))
        if events_jour:
            donnees["evenements_jour"] = [
                {
                    "titre": e.get("titre", ""),
                    "heure": e.get("date_debut", "").strftime("%H:%M")
                    if hasattr(e.get("date_debut", ""), "strftime")
                    else "",
                }
                for e in events_jour[:5]
            ]

        events_demain = charger_events_periode(demain, demain + timedelta(days=1))
        if events_demain:
            donnees["evenements_demain"] = [
                {
                    "titre": e.get("titre", ""),
                    "heure": e.get("date_debut", "").strftime("%H:%M")
                    if hasattr(e.get("date_debut", ""), "strftime")
                    else "",
                }
                for e in events_demain[:3]
            ]
    except Exception as e:
        logger.debug(f"Événements indisponibles: {e}")

    # Stocks critiques
    try:
        from src.services.inventaire import obtenir_service_inventaire

        inventaire = obtenir_service_inventaire().get_inventaire_complet()
        donnees["stocks_bas"] = [
            a.get("ingredient_nom", a.get("nom", "Article"))
            for a in inventaire
            if a.get("statut") in ("critique", "sous_seuil")
        ][:5]
    except Exception as e:
        logger.debug(f"Inventaire indisponible: {e}")

    # Tâches ménage en retard
    try:
        from src.services.accueil_data_service import get_accueil_data_service

        taches = get_accueil_data_service().get_taches_en_retard(limit=10)
        donnees["taches_retard"] = len(taches) if taches else 0
    except Exception:
        pass

    # Jules
    try:
        from src.core.constants import JULES_NAISSANCE

        aujourdhui = date.today()
        donnees["jules_age_mois"] = (aujourdhui - JULES_NAISSANCE).days // 30
    except Exception:
        pass

    return donnees


def _generer_resume_local(donnees: dict) -> str:
    """Génère un résumé matinal sans appel IA (fallback rapide)."""
    parts = []
    aujourdhui = donnees["date"]

    # Salutation basée sur l'heure
    heure = donnees.get("heure", 12)
    if heure < 12:
        salut = "☀️ Bonjour"
    elif heure < 18:
        salut = "👋 Bon après-midi"
    else:
        salut = "🌙 Bonsoir"

    try:
        from src.core.state import obtenir_etat

        nom = obtenir_etat().nom_utilisateur
    except Exception:
        nom = ""

    jour_semaine = aujourdhui.strftime("%A").capitalize()
    jour_mois = aujourdhui.strftime("%d %B")
    parts.append(f"**{salut} {nom} !** Nous sommes {jour_semaine} {jour_mois}.")

    # Météo
    if donnees.get("meteo"):
        m = donnees["meteo"]
        parts.append(
            f"{m.get('icone', '🌤️')} Il fait **{m['temp_min']:.0f}°/{m['temp_max']:.0f}°C** "
            f"aujourd'hui ({m.get('condition', '')})."
        )
        if m.get("pluie", 0) > 50:
            parts.append(f"🌧️ **{m['pluie']}% de chance de pluie** — prévoyez un parapluie !")

    # Repas
    repas_parts = []
    if donnees.get("repas_midi"):
        repas_parts.append(f"ce midi **{donnees['repas_midi']}**")
    if donnees.get("repas_soir"):
        repas_parts.append(f"ce soir **{donnees['repas_soir']}**")
    if repas_parts:
        parts.append(f"🍽️ Au menu : {' et '.join(repas_parts)}.")

    # Événements du jour
    if donnees.get("evenements_jour"):
        events_str = ", ".join(
            f"**{e['titre']}**" + (f" à {e['heure']}" if e.get("heure") else "")
            for e in donnees["evenements_jour"][:3]
        )
        parts.append(f"📅 Aujourd'hui : {events_str}.")

    # Événements de demain (rappels)
    if donnees.get("evenements_demain"):
        events_str = ", ".join(f"**{e['titre']}**" for e in donnees["evenements_demain"][:2])
        parts.append(f"📌 Demain : {events_str}.")

    # Jules
    if donnees.get("jules_age_mois"):
        parts.append(f"👶 Jules a **{donnees['jules_age_mois']} mois** aujourd'hui.")

    # Stocks bas
    if donnees.get("stocks_bas"):
        articles = ", ".join(donnees["stocks_bas"][:3])
        suite = (
            f" (+{len(donnees['stocks_bas']) - 3} autres)" if len(donnees["stocks_bas"]) > 3 else ""
        )
        parts.append(f"⚠️ Stocks bas : {articles}{suite}")

    # Tâches en retard
    if donnees.get("taches_retard", 0) > 0:
        parts.append(f"🧹 **{donnees['taches_retard']}** tâche(s) ménage en retard.")

    if not parts:
        parts.append("✅ Tout est en ordre pour aujourd'hui !")

    return "\n\n".join(parts)


def _generer_resume_ia(donnees: dict) -> str | None:
    """Génère un résumé matinal via l'IA Mistral."""
    try:
        from src.core.ai import ClientIA

        client = ClientIA()

        contexte_parts = []
        if donnees.get("meteo"):
            m = donnees["meteo"]
            contexte_parts.append(
                f"Météo: {m['temp_min']:.0f}°/{m['temp_max']:.0f}°C, "
                f"{m.get('condition', '')}, {m.get('pluie', 0)}% pluie"
            )
        if donnees.get("repas_midi"):
            contexte_parts.append(f"Déjeuner: {donnees['repas_midi']}")
        if donnees.get("repas_soir"):
            contexte_parts.append(f"Dîner: {donnees['repas_soir']}")
        if donnees.get("evenements_jour"):
            events = ", ".join(e["titre"] for e in donnees["evenements_jour"][:3])
            contexte_parts.append(f"Événements aujourd'hui: {events}")
        if donnees.get("evenements_demain"):
            events = ", ".join(e["titre"] for e in donnees["evenements_demain"][:2])
            contexte_parts.append(f"Événements demain: {events}")
        if donnees.get("jules_age_mois"):
            contexte_parts.append(f"Jules (bébé) a {donnees['jules_age_mois']} mois")
        if donnees.get("stocks_bas"):
            contexte_parts.append(f"Stocks bas: {', '.join(donnees['stocks_bas'][:3])}")
        if donnees.get("taches_retard", 0) > 0:
            contexte_parts.append(f"{donnees['taches_retard']} tâches ménage en retard")

        try:
            from src.core.state import obtenir_etat

            nom = obtenir_etat().nom_utilisateur
        except Exception:
            nom = "la famille"

        jour = donnees["date"].strftime("%A %d %B")
        contexte = "\n".join(f"- {p}" for p in contexte_parts)

        prompt = f"""Génère un court résumé matinal chaleureux et personnalisé pour {nom}.
Nous sommes {jour}.

Données du jour:
{contexte}

Règles:
- Ton chaleureux et familial, comme un assistant personnel bienveillant
- Maximum 4-5 phrases
- Utilise des emojis pertinents
- Mentionne les points importants naturellement
- Si stocks bas ou tâches en retard, le mentionner avec tact
- Termine par une note positive ou un encouragement"""

        reponse = client.generer_texte(prompt, max_tokens=300)
        return reponse.strip() if reponse else None
    except Exception as e:
        logger.debug(f"Résumé IA indisponible: {e}")
        return None


# ═══════════════════════════════════════════════════════════
# WIDGET UI
# ═══════════════════════════════════════════════════════════


@cached_fragment(ttl=3600)  # Cache 1h
def afficher_resume_matinal():
    """Affiche le résumé matinal IA personnalisé."""
    donnees = _collecter_donnees_jour()

    # Container stylisé
    st.markdown(
        f'<div style="background: linear-gradient(135deg, {Couleur.BG_METEO_START}, #FFF5E1); '
        f"border-radius: {Rayon.XL}; padding: 1.5rem; margin-bottom: 1rem; "
        f'border-left: 4px solid {Couleur.ORANGE};">',
        unsafe_allow_html=True,
    )

    col_txt, col_btn = st.columns([5, 1])

    with col_btn:
        use_ia = st.button(
            "✨ Version IA",
            key=_keys("btn_resume_ia"),
            help="Générer un résumé enrichi par l'IA",
        )

    # Générer le résumé
    if use_ia or st.session_state.get(_keys("resume_ia_active")):
        st.session_state[_keys("resume_ia_active")] = True

        with st.spinner("✨ L'IA prépare votre résumé..."):
            resume = _generer_resume_ia(donnees)

        if resume:
            st.markdown(resume)
        else:
            # Fallback local
            st.markdown(_generer_resume_local(donnees))
            st.caption("💡 Résumé IA indisponible, version locale affichée")
    else:
        st.markdown(_generer_resume_local(donnees))

    st.markdown("</div>", unsafe_allow_html=True)


__all__ = ["afficher_resume_matinal"]
