"""
Affichage des predictions pour les matchs.
"""

import plotly.graph_objects as go
import streamlit as st

from src.modules.jeux.logic.paris.prediction import predire_over_under, predire_resultat_match

from .analyseur import generer_analyse_complete
from .crud import enregistrer_pari
from .forme import calculer_forme_equipe
from .utils import charger_matchs_recents


def afficher_prediction_match(match: dict):
    """Affiche la carte de prédiction intelligente pour un match"""

    # Générer une clé unique pour ce match
    match_id = match.get(
        "id",
        f"{match.get('equipe_domicile', 'X')}_{match.get('equipe_exterieur', 'X')}_{match.get('date', '')}",
    )
    match_key_prefix = f"match_{match_id}"

    # Charger données pour prédiction
    matchs_dom = charger_matchs_recents(match["equipe_domicile_id"])
    matchs_ext = charger_matchs_recents(match["equipe_exterieur_id"])

    forme_dom = calculer_forme_equipe(matchs_dom, match["equipe_domicile_id"])
    forme_ext = calculer_forme_equipe(matchs_ext, match["equipe_exterieur_id"])

    # H2H (matchs entre les deux équipes)
    h2h = {"nb_matchs": 0}

    # Cotes si disponibles
    cotes = None
    if match.get("cote_dom"):
        cotes = {
            "domicile": match["cote_dom"],
            "nul": match["cote_nul"],
            "exterieur": match["cote_ext"],
        }

    # 🧠 ANALYSE INTELLIGENTE COMPLÈTE
    analyse = generer_analyse_complete(forme_dom, forme_ext, h2h, cotes, match.get("championnat"))
    prediction = predire_resultat_match(forme_dom, forme_ext, h2h, cotes)
    over_under = predire_over_under(forme_dom, forme_ext)

    # AFFICHAGE
    with st.container(border=True):
        # Header avec les équipes
        col1, col2, col3 = st.columns([2, 1, 2])

        with col1:
            st.markdown(f"### 🏠 {match['dom_nom']}")
            forme_str = forme_dom.get("forme_str", "?????")
            forme_coloree = (
                forme_str.replace("V", "🟢")
                .replace("N", "🟡")
                .replace("D", "🔴")
                .replace("?", "⚪")
            )
            st.markdown(f"Forme: {forme_coloree}")

            score_dom = forme_dom.get("score", 50)
            if score_dom >= 70:
                st.success(f"💪 Excellente forme ({score_dom:.0f}/100)")
            elif score_dom >= 50:
                st.info(f"👍 Bonne forme ({score_dom:.0f}/100)")
            else:
                st.warning(f"😟 Forme moyenne ({score_dom:.0f}/100)")

        with col2:
            st.markdown("### ⚽")
            st.markdown(f"**{match['date']}**")
            if match.get("heure"):
                st.markdown(f"⏰ {match['heure']}")
            st.markdown(f"🏆 {match['championnat']}")

        with col3:
            st.markdown(f"### ✈️ {match['ext_nom']}")
            forme_str = forme_ext.get("forme_str", "?????")
            forme_coloree = (
                forme_str.replace("V", "🟢")
                .replace("N", "🟡")
                .replace("D", "🔴")
                .replace("?", "⚪")
            )
            st.markdown(f"Forme: {forme_coloree}")

            score_ext = forme_ext.get("score", 50)
            if score_ext >= 70:
                st.success(f"💪 Excellente forme ({score_ext:.0f}/100)")
            elif score_ext >= 50:
                st.info(f"👍 Bonne forme ({score_ext:.0f}/100)")
            else:
                st.warning(f"😟 Forme moyenne ({score_ext:.0f}/100)")

        st.divider()

        # RECOMMANDATION PRINCIPALE
        reco = analyse.get("recommandation", {})
        conseils = analyse.get("conseils", [])
        alertes = analyse.get("alertes", [])

        confiance = reco.get("confiance", 50)
        pari_reco = reco.get("pari", "?")

        if confiance >= 65:
            st.success(f"""
            ### ✅ PARI RECOMMANDÉ: **{pari_reco}**

            **Confiance:** {confiance:.0f}% | **Mise suggérée:** {reco.get("mise", "?")}

            📊 *{reco.get("raison", "")}*
            """)
        elif confiance >= 50:
            st.warning(f"""
            ### ⚠️ PARI POSSIBLE: **{pari_reco}**

            **Confiance:** {confiance:.0f}% | **Mise suggérée:** {reco.get("mise", "?")}

            📊 *{reco.get("raison", "")}*
            """)
        else:
            st.error("""
            ### ❌ MATCH À ÉVITER

            Pas assez de signaux clairs pour ce match.
            **Conseil:** Garde tes sous pour un meilleur match!
            """)

        # PROBABILITÉS & COTES
        col_prob, col_over = st.columns(2)

        with col_prob:
            probas = prediction.get("probabilites", {})

            fig = go.Figure(
                data=[
                    go.Bar(
                        x=["🏠 Dom", "⚖️ Nul", "✈️ Ext"],
                        y=[
                            probas.get("domicile", 33),
                            probas.get("nul", 33),
                            probas.get("exterieur", 33),
                        ],
                        marker_color=["#4CAF50", "#FFC107", "#2196F3"],
                        text=[
                            f"{v:.0f}%"
                            for v in [
                                probas.get("domicile", 33),
                                probas.get("nul", 33),
                                probas.get("exterieur", 33),
                            ]
                        ],
                        textposition="outside",
                    )
                ]
            )
            fig.update_layout(
                title="📊 Probabilités estimées",
                height=220,
                margin=dict(l=20, r=20, t=40, b=20),
                showlegend=False,
                yaxis=dict(range=[0, 100]),
            )
            st.plotly_chart(fig, width="stretch", key=f"{match_key_prefix}_proba")

        with col_over:
            stats = analyse.get("stats", {})
            moy_buts = stats.get("moy_buts_match", 2.5)

            st.markdown("### ⚽ Paris Buts")

            if moy_buts > 2.8:
                st.success(f"**Over 2.5** recommandé ({over_under['probabilite_over']:.0f}%)")
            elif moy_buts < 2.2:
                st.info(f"**Under 2.5** intéressant ({over_under['probabilite_under']:.0f}%)")
            else:
                st.warning("50/50 - Prudence")

            st.caption(f"Buts attendus: **{over_under['buts_attendus']:.1f}**")

            # BTTS
            buts_dom = stats.get("buts_dom", {})
            buts_ext = stats.get("buts_ext", {})
            if buts_dom.get("moy_marques", 0) > 1.0 and buts_ext.get("moy_marques", 0) > 1.0:
                st.success("**BTTS Oui** probable (les 2 marquent)")

        # CONSEILS INTELLIGENTS
        if conseils:
            st.markdown("### 💡 Conseils IA")

            for conseil in conseils[:4]:
                emoji = conseil.get("emoji", "💡")
                titre = conseil.get("titre", "")
                message = conseil.get("message", "")
                conf = conseil.get("confiance", 50)
                mise = conseil.get("mise", "?")
                pari = conseil.get("pari_suggere", "")

                with st.expander(
                    f"{emoji} {titre} - **{pari}** ({conf:.0f}%)", expanded=(conf >= 60)
                ):
                    st.markdown(message)
                    st.caption(f"💰 Mise suggérée: {mise}")

        # ALERTES
        if alertes:
            st.markdown("### ⚠️ Points d'attention")
            for alerte in alertes:
                st.warning(f"{alerte['emoji']} **{alerte['titre']}**: {alerte['message']}")

        # VALUE BETS
        value_bets = analyse.get("value_bets", [])
        if value_bets:
            st.markdown("### 💎 Value Bets détectées")
            for vb in value_bets:
                if vb["qualite"] in ["excellente", "bonne"]:
                    st.success(
                        f"{vb['emoji']} **Pari {vb['pari']}** @ {vb['cote']:.2f} | "
                        f"Notre proba: {vb['proba_estimee']:.0f}% | "
                        f"EV: **+{vb['ev']:.1f}%** ({vb['qualite']})"
                    )

        # BOUTONS DE PARIS
        st.divider()
        st.markdown("### 🎯 Enregistrer un pari")

        col_btn1, col_btn2, col_btn3, col_btn4 = st.columns(4)

        with col_btn1:
            cote_d = match.get("cote_dom") or 2.0
            if st.button(
                f"🏠 {match['dom_nom'][:10]}... ({cote_d:.2f})", key=f"bet_dom_{match['id']}"
            ):
                enregistrer_pari(match["id"], "1", cote_d, est_virtuel=True)
                st.success("✅ Pari enregistré!")
                st.rerun()

        with col_btn2:
            cote_n = match.get("cote_nul") or 3.5
            if st.button(f"⚖️ Match Nul ({cote_n:.2f})", key=f"bet_nul_{match['id']}"):
                enregistrer_pari(match["id"], "N", cote_n, est_virtuel=True)
                st.success("✅ Pari enregistré!")
                st.rerun()

        with col_btn3:
            cote_e = match.get("cote_ext") or 3.0
            if st.button(
                f"✈️ {match['ext_nom'][:10]}... ({cote_e:.2f})", key=f"bet_ext_{match['id']}"
            ):
                enregistrer_pari(match["id"], "2", cote_e, est_virtuel=True)
                st.success("✅ Pari enregistré!")
                st.rerun()

        with col_btn4:
            if st.button("📊 Analyse complète", key=f"analyse_{match['id']}"):
                st.session_state[f"show_details_{match['id']}"] = True

        # Détails complets si demandé
        if st.session_state.get(f"show_details_{match['id']}", False):
            with st.expander("📊 Analyse détaillée complète", expanded=True):
                col_d1, col_d2 = st.columns(2)

                with col_d1:
                    st.markdown("**Équipe Domicile:**")
                    st.json(forme_dom)

                with col_d2:
                    st.markdown("**Équipe Extérieur:**")
                    st.json(forme_ext)

                st.markdown("**Toutes les raisons:**")
                for raison in prediction.get("raisons", []):
                    st.write(f"• {raison}")


__all__ = ["afficher_prediction_match"]
