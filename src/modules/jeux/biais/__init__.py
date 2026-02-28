"""
Module Biais Cognitifs — Détection et sensibilisation aux biais du joueur

Fonctionnalités:
- Détection automatique de patterns biaisés dans l'historique de mises
- Gambler's fallacy, chasing losses, confirmation bias, sunk cost
- Messages pédagogiques contextuels
- Score de rationalité global avec radar
- Catalogue éducatif complet
"""

import logging
from datetime import date, timedelta

import plotly.graph_objects as go
import streamlit as st

from src.core.decorators import avec_session_db
from src.core.monitoring.rerun_profiler import profiler_rerun
from src.modules._framework import error_boundary
from src.ui.keys import KeyNamespace
from src.ui.state.url import tabs_with_url

logger = logging.getLogger(__name__)
_keys = KeyNamespace("biais_jeux")


# ═══════════════════════════════════════════════════════════
# Catalogue des biais
# ═══════════════════════════════════════════════════════════

BIAIS_CATALOGUE = {
    "gambler_fallacy": {
        "nom": "🎰 Gambler's Fallacy",
        "description": (
            "Croire qu'après une série de pertes, une victoire est 'due'. "
            "En réalité, chaque tirage/match est indépendant."
        ),
        "detection": "Augmentation des mises après 3+ pertes consécutives",
        "conseil": (
            "Gardez la même mise quelle que soit la série. "
            "Les résultats passés n'influent pas sur les futurs."
        ),
    },
    "chasing_losses": {
        "nom": "💸 Chasing Losses (Courir après les pertes)",
        "description": (
            "Augmenter ses mises pour 'récupérer' les pertes passées. "
            "C'est la première cause de pertes lourdes."
        ),
        "detection": "Mise > 2x la mise moyenne après une perte",
        "conseil": (
            "Fixez un budget strict par session. Acceptez les pertes "
            "comme un coût incompressible du jeu."
        ),
    },
    "confirmation_bias": {
        "nom": "🔍 Biais de confirmation",
        "description": (
            "Ne retenir que les victoires et oublier les défaites. "
            "Surestimer ses compétences de pronostiqueur."
        ),
        "detection": "Ratio mises gagnantes rapportées vs réelles très différent",
        "conseil": ("Tenez un journal objectif de TOUS vos paris, même ceux qui vous déplaisent."),
    },
    "sunk_cost": {
        "nom": "⚓ Coût irrécupérable (Sunk Cost)",
        "description": (
            "Continuer à parier parce qu'on a déjà investi beaucoup, "
            "même si la stratégie ne fonctionne pas."
        ),
        "detection": "Mises continues malgré ROI négatif sur 30+ sessions",
        "conseil": (
            "Ce que vous avez déjà perdu est perdu. Évaluez chaque "
            "nouveau pari indépendamment des précédents."
        ),
    },
    "hot_hand": {
        "nom": "🔥 Hot Hand Fallacy",
        "description": (
            "Croire qu'une série de victoires va continuer. "
            "Prendre des risques excessifs en confiance."
        ),
        "detection": "Multiplication des mises après 3+ victoires consécutives",
        "conseil": (
            "Une série gagnante est statistiquement normale. "
            "Ne changez pas votre stratégie en cours de route."
        ),
    },
    "ancrage": {
        "nom": "⚖️ Biais d'ancrage",
        "description": (
            "Se fixer sur un chiffre (cote, prix, gain passé) et "
            "l'utiliser comme référence irrationnelle."
        ),
        "detection": "Paris répétés sur les mêmes cotes/équipes",
        "conseil": (
            "Analysez chaque situation indépendamment. Ne vous fixez pas sur une cote 'habituelle'."
        ),
    },
}


# ═══════════════════════════════════════════════════════════
# Analyse des patterns
# ═══════════════════════════════════════════════════════════


@avec_session_db
def _analyser_patterns(jours: int = 90, db=None) -> dict[str, dict]:
    """Analyse les patterns de biais dans l'historique."""
    from src.core.models.jeux import PariSportif

    date_debut = date.today() - timedelta(days=jours)

    paris = (
        db.query(PariSportif)
        .filter(PariSportif.date_pari >= date_debut)
        .order_by(PariSportif.date_pari.asc())
        .all()
    )

    resultats: dict[str, dict] = {}

    if not paris:
        return resultats

    mises = [float(p.mise) for p in paris]
    mise_moy = sum(mises) / len(mises) if mises else 0

    # ── Gambler's fallacy ──
    serie_pertes = 0
    gambler_count = 0
    for i, p in enumerate(paris):
        if p.statut and p.statut.value == "perdu":
            serie_pertes += 1
        else:
            if serie_pertes >= 3 and i < len(paris) - 1:
                prochaine_mise = float(paris[i].mise)
                if prochaine_mise > mise_moy * 1.5:
                    gambler_count += 1
            serie_pertes = 0

    resultats["gambler_fallacy"] = {
        "detecte": gambler_count > 0,
        "occurrences": gambler_count,
        "severite": min(gambler_count * 20, 100),
    }

    # ── Chasing losses ──
    chasing_count = 0
    for i in range(1, len(paris)):
        prev = paris[i - 1]
        curr = paris[i]
        if prev.statut and prev.statut.value == "perdu":
            if float(curr.mise) > mise_moy * 2:
                chasing_count += 1

    resultats["chasing_losses"] = {
        "detecte": chasing_count > 0,
        "occurrences": chasing_count,
        "severite": min(chasing_count * 15, 100),
    }

    # ── Hot hand ──
    serie_victoires = 0
    hot_hand_count = 0
    for i, p in enumerate(paris):
        if p.statut and p.statut.value == "gagne":
            serie_victoires += 1
        else:
            if serie_victoires >= 3 and i < len(paris):
                if float(paris[i].mise) > mise_moy * 1.5:
                    hot_hand_count += 1
            serie_victoires = 0

    resultats["hot_hand"] = {
        "detecte": hot_hand_count > 0,
        "occurrences": hot_hand_count,
        "severite": min(hot_hand_count * 20, 100),
    }

    # ── Ancrage ──
    equipes_count: dict[str, int] = {}
    for p in paris:
        if p.match and p.match.equipe_domicile:
            eq = p.match.equipe_domicile.nom
            equipes_count[eq] = equipes_count.get(eq, 0) + 1

    max_equipe = max(equipes_count.values()) if equipes_count else 0
    ratio_ancrage = max_equipe / len(paris) if paris else 0

    resultats["ancrage"] = {
        "detecte": ratio_ancrage > 0.3,
        "occurrences": max_equipe,
        "severite": min(int(ratio_ancrage * 100), 100),
    }

    # ── Sunk cost ──
    gains = sum(float(p.gain_net or 0) for p in paris)
    sunk_cost = gains < 0 and len(paris) >= 30

    resultats["sunk_cost"] = {
        "detecte": sunk_cost,
        "occurrences": 1 if sunk_cost else 0,
        "severite": 80 if sunk_cost else 0,
    }

    # ── Confirmation bias (pas de détection automatique fiable) ──
    resultats["confirmation_bias"] = {
        "detecte": False,
        "occurrences": 0,
        "severite": 0,
    }

    return resultats


# ═══════════════════════════════════════════════════════════
# Score de rationalité
# ═══════════════════════════════════════════════════════════


def _calculer_score_rationalite(analyses: dict[str, dict]) -> int:
    """Score de rationalité global (0-100, 100=parfaitement rationnel)."""
    if not analyses:
        return 100

    severite_totale = sum(a["severite"] for a in analyses.values())
    nb_biais = len(analyses)
    score = max(0, 100 - int(severite_totale / nb_biais)) if nb_biais > 0 else 100
    return score


# ═══════════════════════════════════════════════════════════
# UI
# ═══════════════════════════════════════════════════════════


def _afficher_score(score: int) -> None:
    """Affiche le score de rationalité."""
    st.subheader("🧠 Score de Rationalité")

    if score >= 80:
        emoji, label = "🟢", "Excellent"
    elif score >= 60:
        emoji, label = "🟡", "Correct"
    elif score >= 40:
        emoji, label = "🟠", "Attention"
    else:
        emoji, label = "🔴", "Critique"

    st.progress(score / 100, text=f"{emoji} {label} — {score}/100")


def _afficher_biais_detectes(analyses: dict[str, dict]) -> None:
    """Affiche les biais détectés avec conseils."""
    if not analyses:
        st.success("✅ Aucun biais détecté ! Votre jeu semble rationnel.")
        return

    detectes = {k: v for k, v in analyses.items() if v["detecte"]}

    if not detectes:
        st.success("✅ Aucun biais significatif détecté.")
        return

    st.warning(f"⚠️ **{len(detectes)} biais détecté(s)** dans vos habitudes de jeu")

    for biais_id, analyse in detectes.items():
        info = BIAIS_CATALOGUE.get(biais_id, {})
        nom = info.get("nom", biais_id)
        severite = analyse["severite"]

        with st.expander(f"{nom} — Sévérité: {severite}%"):
            st.markdown(f"**Description:** {info.get('description', '')}")
            st.markdown(f"**Détection:** {info.get('detection', '')}")
            st.metric("Occurrences", analyse["occurrences"])
            st.progress(severite / 100)
            st.info(f"💡 **Conseil:** {info.get('conseil', '')}")


def _afficher_radar_biais(analyses: dict[str, dict]) -> None:
    """Radar des biais cognitifs."""
    if not analyses:
        st.info("Aucune donnée d'analyse")
        return

    categories = [
        BIAIS_CATALOGUE[k]["nom"].split(" ", 1)[1] if k in BIAIS_CATALOGUE else k for k in analyses
    ]
    values = [a["severite"] for a in analyses.values()]

    fig = go.Figure(
        data=go.Scatterpolar(
            r=values,
            theta=categories,
            fill="toself",
            name="Sévérité",
            line={"color": "crimson"},
        )
    )
    fig.update_layout(
        polar={"radialaxis": {"visible": True, "range": [0, 100]}},
        title="🕸️ Profil de biais cognitifs",
        height=400,
    )
    st.plotly_chart(fig, use_container_width=True)


def _afficher_catalogue() -> None:
    """Affiche le catalogue complet des biais cognitifs."""
    st.subheader("📚 Catalogue des biais cognitifs du joueur")

    for _biais_id, info in BIAIS_CATALOGUE.items():
        with st.expander(info["nom"]):
            st.markdown(f"**{info['description']}**")
            st.caption(f"Détection: {info['detection']}")
            st.info(f"💡 {info['conseil']}")


# ═══════════════════════════════════════════════════════════
# Point d'entrée
# ═══════════════════════════════════════════════════════════


@profiler_rerun("biais_jeux")
def app():
    """Point d'entrée du module Biais Cognitifs."""
    st.title("🧠 Analyse des Biais Cognitifs")
    st.caption("Détectez et comprenez vos biais de joueur pour miser plus rationnellement")

    TAB_LABELS = ["🔍 Analyse", "📊 Radar", "📚 Catalogue"]
    tabs_with_url(TAB_LABELS, param="tab")
    tabs = st.tabs(TAB_LABELS)

    jours = st.selectbox(
        "Période",
        [30, 60, 90, 180],
        index=2,
        format_func=lambda x: f"{x} jours",
        key=_keys("periode"),
    )

    analyses = _analyser_patterns(jours=jours)
    score = _calculer_score_rationalite(analyses)

    with tabs[0]:
        with error_boundary("biais_analyse"):
            _afficher_score(score)
            st.divider()
            _afficher_biais_detectes(analyses)

    with tabs[1]:
        with error_boundary("biais_radar"):
            _afficher_radar_biais(analyses)

    with tabs[2]:
        with error_boundary("biais_catalogue"):
            _afficher_catalogue()


def main():
    app()


__all__ = ["app", "main"]
