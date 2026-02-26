"""
Module Alertes Pronostics — Détection proactive de matchs intéressants

Fonctionnalités:
- Scan automatique des matchs avec critères: value bets, streaks, H2H
- Alertes IA multi-critères (forme, blessures, tendances)
- Badge notification "X matchs intéressants ce week-end"
- Filtre par championnat / date / type de value bet
- Cotes en temps réel via The Odds API
"""

import logging
from datetime import date, timedelta

import pandas as pd
import streamlit as st

from src.core.decorators import avec_session_db
from src.core.monitoring.rerun_profiler import profiler_rerun
from src.modules._framework import error_boundary
from src.ui.keys import KeyNamespace
from src.ui.state.url import tabs_with_url

logger = logging.getLogger(__name__)
_keys = KeyNamespace("alertes_jeux")


# ═══════════════════════════════════════════════════════════
# Chargement données
# ═══════════════════════════════════════════════════════════


@avec_session_db
def _charger_matchs_a_venir(jours: int = 7, db=None) -> list[dict]:
    """Charge les matchs dans les prochains jours."""
    from src.core.models.jeux import Match

    date_limite = date.today() + timedelta(days=jours)
    rows = (
        db.query(Match)
        .filter(Match.date_match >= date.today(), Match.date_match <= date_limite)
        .order_by(Match.date_match.asc())
        .all()
    )
    return [
        {
            "id": r.id,
            "domicile": r.equipe_domicile.nom if r.equipe_domicile else str(r.equipe_domicile_id),
            "exterieur": r.equipe_exterieur.nom
            if r.equipe_exterieur
            else str(r.equipe_exterieur_id),
            "date": r.date_match,
            "championnat": r.championnat,
            "cote_dom": float(r.cote_domicile) if r.cote_domicile else None,
            "cote_nul": float(r.cote_nul) if r.cote_nul else None,
            "cote_ext": float(r.cote_exterieur) if r.cote_exterieur else None,
        }
        for r in rows
    ]


# ═══════════════════════════════════════════════════════════
# Détection value bets
# ═══════════════════════════════════════════════════════════


def _detecter_value_bets(matchs: list[dict]) -> list[dict]:
    """Détecte les value bets potentiels (cote > espérance estimée)."""
    alertes = []
    for m in matchs:
        # Heuristique: cote élevée domicile (>3) = potentiel upset
        if m["cote_dom"] and m["cote_dom"] > 3.0:
            alertes.append(
                {
                    **m,
                    "type_alerte": "Value bet domicile",
                    "raison": f"Cote élevée ({m['cote_dom']:.2f}) pour le domicile",
                    "score": m["cote_dom"],
                }
            )
        if m["cote_ext"] and m["cote_ext"] > 3.5:
            alertes.append(
                {
                    **m,
                    "type_alerte": "Value bet extérieur",
                    "raison": f"Cote élevée ({m['cote_ext']:.2f}) pour l'extérieur",
                    "score": m["cote_ext"],
                }
            )
        # Nul sous-coté
        if m["cote_nul"] and 3.0 <= m["cote_nul"] <= 3.3:
            alertes.append(
                {
                    **m,
                    "type_alerte": "Nul probable",
                    "raison": f"Cote nul serrée ({m['cote_nul']:.2f})",
                    "score": 3.5 - m["cote_nul"],
                }
            )

    return sorted(alertes, key=lambda x: x["score"], reverse=True)


# ═══════════════════════════════════════════════════════════
# UI – Alertes
# ═══════════════════════════════════════════════════════════


def _afficher_alertes_matchs(alertes: list[dict]) -> None:
    """Affiche les alertes de matchs."""
    if not alertes:
        st.info("🔍 Aucune alerte détectée pour la période sélectionnée")
        return

    st.success(f"🔔 **{len(alertes)} alerte(s)** détectées")

    for a in alertes:
        with st.expander(
            f"⚡ {a['domicile']} vs {a['exterieur']} — {a['date']} | {a['type_alerte']}"
        ):
            cols = st.columns(4)
            cols[0].metric("🏠 Dom.", f"{a['cote_dom']:.2f}" if a["cote_dom"] else "N/A")
            cols[1].metric("🤝 Nul", f"{a['cote_nul']:.2f}" if a["cote_nul"] else "N/A")
            cols[2].metric("✈️ Ext.", f"{a['cote_ext']:.2f}" if a["cote_ext"] else "N/A")
            cols[3].metric("📊 Score", f"{a['score']:.2f}")

            st.caption(f"🏆 {a['championnat']} | Raison: {a['raison']}")


# ═══════════════════════════════════════════════════════════
# UI – Analyse IA match
# ═══════════════════════════════════════════════════════════


def _afficher_analyse_ia_match(matchs: list[dict]) -> None:
    """Analyse IA détaillée d'un match sélectionné."""
    if not matchs:
        st.info("Aucun match à venir pour l'analyse")
        return

    options = [f"{m['domicile']} vs {m['exterieur']} ({m['date']})" for m in matchs]
    choix = st.selectbox("Sélectionner un match", options, key=_keys("match_ia"))
    idx = options.index(choix)
    match = matchs[idx]

    if st.button("🤖 Analyse IA complète", key=_keys("btn_ia")):
        with st.spinner("Analyse en cours..."):
            try:
                from src.services.jeux import get_jeux_ai_service

                service = get_jeux_ai_service()
                prompt = (
                    f"Analyse détaillée du match {match['domicile']} vs {match['exterieur']} "
                    f"le {match['date']} ({match['championnat']}).\n"
                    f"Cotes: Dom={match['cote_dom']}, Nul={match['cote_nul']}, "
                    f"Ext={match['cote_ext']}.\n"
                    "Donne: 1) Analyse des forces en présence, "
                    "2) Prédiction avec pourcentage de confiance, "
                    "3) Meilleur type de pari recommandé, "
                    "4) Mise suggérée (prudente)."
                )

                result = service.call_with_cache(
                    prompt=prompt,
                    system_prompt=(
                        "Expert en analyse sportive. Sois objectif, factuel. "
                        "Rappelle le risque. Ne garantis jamais un résultat."
                    ),
                )
                st.markdown(result)

            except Exception as e:
                logger.warning(f"Analyse IA indisponible: {e}")
                st.warning("Analyse IA indisponible.")


# ═══════════════════════════════════════════════════════════
# UI – Cotes temps réel
# ═══════════════════════════════════════════════════════════


def _afficher_cotes_temps_reel() -> None:
    """Affiche les cotes en temps réel via The Odds API."""
    st.subheader("📡 Cotes en temps réel")

    try:
        from src.services.jeux._internal.odds_data import get_odds_data_service

        service = get_odds_data_service()

        championnat = st.selectbox(
            "Championnat",
            [
                "soccer_france_ligue_one",
                "soccer_epl",
                "soccer_spain_la_liga",
                "soccer_germany_bundesliga",
                "soccer_italy_serie_a",
                "soccer_uefa_champs_league",
            ],
            format_func=lambda x: x.replace("soccer_", "").replace("_", " ").title(),
            key=_keys("champ_cotes"),
        )

        if st.button("🔄 Rafraîchir les cotes", key=_keys("refresh_cotes")):
            with st.spinner("Chargement des cotes…"):
                cotes = service.obtenir_cotes_match(sport=championnat)

                if cotes:
                    rows = []
                    for c in cotes:
                        rows.append(
                            {
                                "Match": f"{c.equipe_dom} vs {c.equipe_ext}",
                                "Date": c.date_match,
                                "Bookmaker": c.bookmaker,
                                "Dom.": f"{c.cote_dom:.2f}",
                                "Nul": f"{c.cote_nul:.2f}",
                                "Ext.": f"{c.cote_ext:.2f}",
                            }
                        )
                    st.dataframe(
                        pd.DataFrame(rows),
                        use_container_width=True,
                        hide_index=True,
                    )

                    # Meilleures cotes
                    st.subheader("🏆 Meilleures cotes par match")
                    meilleures = service.trouver_meilleures_cotes(cotes)
                    for mc in meilleures:
                        with st.expander(f"{mc.match_id}"):
                            cols = st.columns(3)
                            cols[0].metric("Dom.", f"{mc.meilleure_dom:.2f}", mc.bookmaker_dom)
                            cols[1].metric("Nul", f"{mc.meilleure_nul:.2f}", mc.bookmaker_nul)
                            cols[2].metric("Ext.", f"{mc.meilleure_ext:.2f}", mc.bookmaker_ext)
                else:
                    st.info("Aucune cote disponible. Vérifiez la clé API.")

    except Exception as e:
        logger.debug(f"Module cotes indisponible: {e}")
        st.info(
            "📡 Module cotes temps réel indisponible. "
            "Configurez `ODDS_API_KEY` dans vos paramètres."
        )


# ═══════════════════════════════════════════════════════════
# Point d'entrée
# ═══════════════════════════════════════════════════════════


@profiler_rerun("alertes_jeux")
def app():
    """Point d'entrée du module Alertes."""
    st.title("🔔 Alertes Pronostics")
    st.caption("Détection proactive des matchs intéressants et cotes en temps réel")

    TAB_LABELS = ["⚡ Alertes", "🤖 Analyse IA", "📡 Cotes live"]
    tabs_with_url(TAB_LABELS, param="tab")
    tabs = st.tabs(TAB_LABELS)

    jours = st.slider("Horizon (jours)", 1, 14, 7, key=_keys("horizon"))
    matchs = _charger_matchs_a_venir(jours=jours)

    with tabs[0]:
        with error_boundary("alertes"):
            alertes = _detecter_value_bets(matchs)
            _afficher_alertes_matchs(alertes)

    with tabs[1]:
        with error_boundary("analyse_ia"):
            _afficher_analyse_ia_match(matchs)

    with tabs[2]:
        with error_boundary("cotes_live"):
            _afficher_cotes_temps_reel()


def main():
    app()


__all__ = ["app", "main"]
