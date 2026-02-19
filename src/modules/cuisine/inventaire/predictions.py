"""
Prédictions ML - Onglet prévisions de l'inventaire.
Affiche les prédictions et recommandations basées sur le Machine Learning.
"""

import pandas as pd
import streamlit as st

from src.services.inventaire import get_inventaire_service
from src.services.cuisine.suggestions import obtenir_service_predictions


def render_predictions():
    """Affiche les prédictions et recommandations ML"""
    st.subheader("🔮 Prévisions et Recommandations")

    try:
        service = get_inventaire_service()
        service_pred = obtenir_service_predictions()

        if service is None:
            st.error("❌ Service inventaire indisponible")
            return

        # Récupère les données
        articles = service.get_inventaire_complet()
        historique_complet = service.get_historique(days=90)  # 3 mois d'historique

        if not articles:
            st.info("Aucun article dans l'inventaire pour générer les prédictions")
            return

        # Bouton pour générer les prédictions
        col1, col2, col3 = st.columns([2, 1, 1])

        with col1:
            if st.button(
                "🔄 Générer les prédictions", width="stretch", key="btn_generate_predictions"
            ):
                st.session_state.predictions_generated = True
                st.session_state.predictions_data = None
                st.rerun()

        with col2:
            # Période de prédiction
            _periode = st.selectbox(
                "Prédiction pour", ["1 semaine", "1 mois", "3 mois"], key="prediction_period"
            )

        with col3:
            st.metric("📦 Articles", len(articles))

        st.divider()

        # Affiche les prédictions si générées
        if st.session_state.get("predictions_generated", False):
            with st.spinner("📊 Génération des prédictions ML..."):
                try:
                    predictions = service_pred.generer_predictions(articles, historique_complet)
                    analyse_globale = service_pred.obtenir_analyse_globale(predictions)
                    recommandations = service_pred.generer_recommandations(predictions)

                    st.session_state.predictions_data = {
                        "predictions": predictions,
                        "analyse": analyse_globale,
                        "recommandations": recommandations,
                    }
                except Exception as e:
                    st.error(f"❌ Erreur lors de la génération: {str(e)}")
                    st.session_state.predictions_generated = False
                    return

        # Affiche les résultats
        if st.session_state.get("predictions_data"):
            data = st.session_state.predictions_data
            predictions = data["predictions"]
            analyse = data["analyse"]
            recommandations = data["recommandations"]

            # Tabs pour les différentes vues
            tab_pred, tab_tendances, tab_recom, tab_analyse = st.tabs(
                [
                    "📝ˆ Prédictions",
                    "📊 Tendances",
                    "🔔 Recommandations",
                    "📝 Analyse globale",
                ]
            )

            with tab_pred:
                st.write("**Prédictions pour tous les articles**")

                # Prépare le dataframe
                df_pred = []
                for pred in predictions:
                    df_pred.append(
                        {
                            "Article": pred.nom,
                            "Quantité actuelle": pred.quantite_actuelle,
                            "Prédite (1 mois)": f"{pred.quantite_predite:.1f}",
                            "Tendance": pred.tendance,
                            "Confiance": f"{pred.confiance:.0%}",
                            "Risque rupture": "❌ OUI" if pred.risque_rupture else "✅ Non",
                            "Jours avant rupture": pred.jours_avant_rupture
                            if pred.jours_avant_rupture
                            else "-",
                        }
                    )

                df_display = pd.DataFrame(df_pred)
                st.dataframe(df_display, width="stretch", hide_index=True)

                st.divider()

                # Filtres et détails
                col1, col2, col3 = st.columns(3)

                with col1:
                    filter_trend = st.multiselect(
                        "Filtrer par tendance",
                        ["croissante", "décroissante", "stable"],
                        default=["croissante", "décroissante", "stable"],
                        key="filter_trend_pred",
                    )

                with col2:
                    filter_risk = st.checkbox(
                        "Afficher seulement les articles à risque", key="filter_risk_pred"
                    )

                with col3:
                    min_confiance = st.slider(
                        "Confiance minimale", 0, 100, 0, key="min_confiance_pred"
                    )

                # Filtre et affiche les détails
                filtered_pred = [
                    p
                    for p in predictions
                    if p.tendance in filter_trend
                    and (not filter_risk or p.risque_rupture)
                    and (p.confiance * 100 >= min_confiance)
                ]

                if filtered_pred:
                    st.write(f"**{len(filtered_pred)} article(s) correspondent aux filtres**")
                    for pred in filtered_pred[:5]:  # Affiche les 5 premiers
                        with st.expander(f"💡 {pred.nom} - {pred.tendance.upper()}"):
                            col1, col2, col3 = st.columns(3)

                            with col1:
                                st.metric(
                                    "Quantité actuelle",
                                    f"{pred.quantite_actuelle:.1f} {pred.unite}",
                                )
                                st.metric("Prédite (1 mois)", f"{pred.quantite_predite:.1f}")

                            with col2:
                                st.metric("Consommation/jour", f"{pred.consommation_moyenne:.2f}")
                                st.metric("Confiance", f"{pred.confiance:.0%}")

                            with col3:
                                if pred.risque_rupture:
                                    st.metric("⚠️ Rupture dans", f"{pred.jours_avant_rupture} j")
                                    st.warning(
                                        f"Stock insuffisant dans {pred.jours_avant_rupture} jours!"
                                    )
                                else:
                                    st.metric("Stock", "⏰ Sûr")
                                    st.success(f"Suffisant pour {pred.jours_avant_rupture} jours")

            with tab_tendances:
                st.write("**Tendances de consommation**")

                # Groupe par tendance
                tendances = {"croissante": [], "décroissante": [], "stable": []}
                for pred in predictions:
                    tendances[pred.tendance].append(pred)

                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric("📝ˆ Croissante", len(tendances["croissante"]))
                    if tendances["croissante"]:
                        with st.expander("Voir les articles"):
                            for p in tendances["croissante"]:
                                st.write(f"• {p.nom} (+{p.consommation_moyenne:.2f}/jour)")

                with col2:
                    st.metric("📝‰ Décroissante", len(tendances["décroissante"]))
                    if tendances["décroissante"]:
                        with st.expander("Voir les articles"):
                            for p in tendances["décroissante"]:
                                st.write(f"• {p.nom} ({p.consommation_moyenne:.2f}/jour)")

                with col3:
                    st.metric("➡️ Stable", len(tendances["stable"]))
                    if tendances["stable"]:
                        with st.expander("Voir les articles"):
                            for p in tendances["stable"]:
                                st.write(f"• {p.nom} (~{p.consommation_moyenne:.2f}/jour)")

                st.divider()

                # Chart des tendances
                if predictions:
                    chart_data = {
                        "Article": [p.nom[:15] for p in predictions[:10]],
                        "Consommation/jour": [p.consommation_moyenne for p in predictions[:10]],
                    }
                    chart_df = pd.DataFrame(chart_data)
                    st.bar_chart(chart_df.set_index("Article"), width="stretch")

            with tab_recom:
                st.write("**Recommandations d'achat prioritaires**")

                if recommandations:
                    # Groupe par priorité
                    by_priority = {}
                    for rec in recommandations:
                        p = rec.priorite
                        if p not in by_priority:
                            by_priority[p] = []
                        by_priority[p].append(rec)

                    # Affiche par priorité
                    for priority in ["CRITIQUE", "HAUTE", "MOYENNE"]:
                        if priority in by_priority:
                            icon = (
                                "❌"
                                if priority == "CRITIQUE"
                                else "⚠️"
                                if priority == "HAUTE"
                                else "ℹ️"
                            )
                            count = len(by_priority[priority])

                            with st.expander(
                                f"{icon} {priority} ({count})", expanded=(priority == "CRITIQUE")
                            ):
                                for rec in by_priority[priority]:
                                    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])

                                    with col1:
                                        st.write(f"**{rec.nom}**")
                                        st.caption(rec.raison)

                                    with col2:
                                        st.metric(
                                            "Quantité",
                                            f"{rec.quantite_recommandee:.0f} {rec.unite}",
                                        )

                                    with col3:
                                        st.metric("Stock actuel", f"{rec.quantite_actuelle:.0f}")

                                    with col4:
                                        if st.button(
                                            "⏰ Ajouter", key=f"add_rec_{rec.nom}", width="stretch"
                                        ):
                                            st.toast(f"⏰ {rec.nom} ajouté", icon="🛒")
                else:
                    st.info("Aucune recommandation d'achat pour le moment")

            with tab_analyse:
                st.write("**Analyse globale de l'inventaire**")

                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    st.metric("📦 Total articles", len(predictions))

                with col2:
                    articles_risque = len([p for p in predictions if p.risque_rupture])
                    st.metric("❌ En risque", articles_risque)

                with col3:
                    articles_croissance = len(
                        [p for p in predictions if p.tendance == "croissante"]
                    )
                    st.metric("📝ˆ Croissance", articles_croissance)

                with col4:
                    confiance_moy = (
                        sum(p.confiance for p in predictions) / len(predictions)
                        if predictions
                        else 0
                    )
                    st.metric("🎯 Confiance moy", f"{confiance_moy:.0%}")

                st.divider()

                # Résumé de l'analyse
                if analyse:
                    st.write("**Tendance générale**: ")
                    if analyse.tendance_globale == "croissante":
                        st.write("📝ˆ **Consommation en augmentation**")
                        st.info(
                            "La consommation générale augmente. Préparez-vous à augmenter vos achats."
                        )
                    elif analyse.tendance_globale == "décroissante":
                        st.write("📝‰ **Consommation en diminution**")
                        st.info(
                            "La consommation générale diminue. Vous pouvez réduire légèrement vos achats."
                        )
                    else:
                        st.write("➡️ **Consommation stable**")
                        st.info(
                            "La consommation est stable. Maintenez votre rythme d'achat actuel."
                        )

                    st.divider()

                    # Stats détaillées
                    col1, col2 = st.columns(2)

                    with col1:
                        st.write("**Consommation quotidienne moyenne**")
                        st.metric(
                            "Total", f"{analyse.consommation_moyenne_globale:.2f} unités/jour"
                        )
                        st.metric("Min", f"{analyse.consommation_min:.2f}")
                        st.metric("Max", f"{analyse.consommation_max:.2f}")

                    with col2:
                        st.write("**Distribution des articles**")
                        st.metric("Croissants", f"{analyse.nb_articles_croissance}")
                        st.metric("Décroissants", f"{analyse.nb_articles_decroissance}")
                        st.metric("Stables", f"{analyse.nb_articles_stables}")

    except Exception as e:
        st.error(f"❌ Erreur: {str(e)}")
        import traceback

        st.text(traceback.format_exc())


__all__ = ["render_predictions"]
