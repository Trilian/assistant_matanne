"""
Module Paris Sportifs - Suivi des championnats européens et prédictions IA

Fonctionnalités:
- Suivi des 5 grands championnats + coupes européennes
- Prédictions basées sur la forme, H2H, avantage domicile
- Suivi des paris virtuels et réels
- Dashboard de performance
"""

import pandas as pd
import streamlit as st

from .crud import (
    ajouter_equipe,
    ajouter_match,
    enregistrer_pari,
    enregistrer_resultat_match,
    supprimer_match,
)
from .gestion import afficher_gestion_donnees
from .prediction import afficher_prediction_match

# Imports des sous-modules
from .sync import (
    refresh_scores_matchs,
    sync_equipes_depuis_api,
    sync_matchs_a_venir,
    sync_tous_championnats,
)
from .tableau_bord import afficher_dashboard_performance

# Re-export constantes depuis _common
from .utils import (
    CHAMPIONNATS,
    charger_championnats_disponibles,
    charger_equipes,
    charger_matchs_a_venir,
    charger_matchs_recents,
    charger_paris_utilisateur,
    logger,
)


def app():
    """Point d'entrée du module Paris Sportifs"""

    st.title("âš½ Paris Sportifs - Prédictions IA")
    st.caption("Suivi des championnats européens avec prédictions intelligentes")

    # Tabs principaux
    tabs = st.tabs(["ðŸŽ¯ Prédictions", "ðŸ“Š Performance", "ðŸ† Classements", "âš™ï¸ Gestion"])

    # TAB 1: PRÉDICTIONS
    with tabs[0]:
        st.header("Matchs à venir")

        with st.expander("â„¹ï¸ Comment ça marche"):
            st.markdown("""
            **ðŸ”„ Refresh Scores**: Met à jour les scores des matchs terminés depuis l'API

            **ðŸ“¥ Sync Équipes**: Charge les équipes des 5 championnats depuis l'API

            **ðŸ“… Sync Matchs**: Charge les matchs à venir avec prédictions IA automatiques

            ðŸ’¡ **Conseil**: Faites d'abord "Sync Équipes" puis "Sync Matchs" pour tout automatiser!
            """)

        # Ligne de boutons de synchronisation
        col_btn1, col_btn2, col_btn3 = st.columns(3)

        with col_btn1:
            if st.button(
                "ðŸ”„ Refresh Scores",
                help="Met à jour les scores depuis l'API",
                use_container_width=True,
            ):
                st.info("ðŸ”„ Actualisation en cours...")
                try:
                    with st.spinner("Mise à jour des scores..."):
                        logger.info("ðŸ”˜ Bouton REFRESH cliqué!")
                        count = refresh_scores_matchs()
                        logger.info(f"ðŸ“Š Résultat refresh: {count} matchs")
                        if count > 0:
                            st.success(f"âœ… {count} matchs mis à jour!")
                        else:
                            st.info("âœ… Tous les matchs sont à jour")
                        st.rerun()
                except Exception as e:
                    logger.error(f"âŒ Erreur refresh: {e}", exc_info=True)
                    st.error(f"âŒ Erreur: {e}")

        with col_btn2:
            if st.button(
                "ðŸ“¥ Sync Équipes",
                help="Charge toutes les équipes depuis Football-Data API",
                use_container_width=True,
            ):
                st.info("â³ Synchronisation en cours...")
                try:
                    with st.spinner("Synchronisation des 5 grands championnats..."):
                        logger.info("ðŸ”˜ Bouton SYNC ÉQUIPES cliqué!")
                        resultats = sync_tous_championnats()
                        logger.info(f"ðŸ“Š Résultats sync: {resultats}")
                        total = sum(resultats.values())
                        if total == 0:
                            st.warning("âš ï¸ 0 équipes synchronisées - vérifiez la clé API")
                        else:
                            st.success(f"âœ… {total} équipes synchronisées!")
                            for champ, count in resultats.items():
                                if count > 0:
                                    st.caption(f"  • {champ}: {count} équipes")
                        st.rerun()
                except Exception as e:
                    logger.error(f"âŒ Erreur sync: {e}", exc_info=True)
                    st.error(f"âŒ Erreur: {e}")

        with col_btn3:
            if st.button(
                "ðŸ“… Sync Matchs",
                help="Charge les matchs à venir depuis l'API",
                use_container_width=True,
            ):
                st.info("ðŸ“… Chargement des matchs...")
                try:
                    with st.spinner("Récupération des matchs des 5 championnats..."):
                        logger.info("ðŸ”˜ Bouton SYNC MATCHS cliqué!")
                        resultats = sync_matchs_a_venir(jours=14)
                        logger.info(f"ðŸ“Š Résultats sync matchs: {resultats}")
                        total = sum(resultats.values())
                        if total == 0:
                            st.info("âœ… Tous les matchs sont déjà synchronisés")
                        else:
                            st.success(f"âœ… {total} nouveaux matchs ajoutés!")
                            for champ, count in resultats.items():
                                if count > 0:
                                    st.caption(f"  • {champ}: {count} matchs")
                        st.rerun()
                except Exception as e:
                    logger.error(f"âŒ Erreur sync matchs: {e}", exc_info=True)
                    st.error(f"âŒ Erreur: {e}")

        # Filtres
        col_filtre, col_jours = st.columns([3, 2])
        with col_filtre:
            championnats = ["Tous"] + CHAMPIONNATS
            filtre_champ = st.selectbox("Championnat", championnats)
        with col_jours:
            jours = st.slider("Jours", 1, 14, 7)

        champ_filtre = None if filtre_champ == "Tous" else filtre_champ
        matchs = charger_matchs_a_venir(jours=jours, championnat=champ_filtre)

        if matchs:
            for match in matchs:
                afficher_prediction_match(match)
        else:
            st.info(
                "ðŸ“… Aucun match prévu dans cette période. "
                "Ajoutez des matchs dans l'onglet Gestion."
            )

            with st.expander("ðŸŽ® Voir une démo"):
                st.markdown("""
                ### Comment ça marche?

                1. **Ajoutez des équipes** dans l'onglet Gestion
                2. **Créez des matchs** entre ces équipes
                3. **L'IA prédit** les résultats basés sur:
                   - Forme récente (5 derniers matchs)
                   - Avantage domicile (+12% statistique)
                   - Historique des confrontations
                   - Régression vers la moyenne

                4. **Enregistrez vos paris** (virtuels ou réels)
                5. **Suivez votre performance** dans l'onglet dédié
                """)

    # TAB 2: PERFORMANCE
    with tabs[1]:
        st.header("ðŸ“Š Performance de mes paris")
        afficher_dashboard_performance()

    # TAB 3: CLASSEMENTS
    with tabs[2]:
        st.header("ðŸ† Classements")

        champ_classe = st.selectbox("Sélectionner un championnat", CHAMPIONNATS, key="class_champ")
        equipes = charger_equipes(champ_classe)

        if equipes:
            # Trier par points
            equipes_triees = sorted(
                equipes,
                key=lambda x: (x["points"], x["buts_marques"] - x["buts_encaisses"]),
                reverse=True,
            )

            df = pd.DataFrame(equipes_triees)
            df["Diff"] = df["buts_marques"] - df["buts_encaisses"]
            df = df.rename(
                columns={
                    "nom": "Équipe",
                    "matchs_joues": "J",
                    "victoires": "V",
                    "nuls": "N",
                    "defaites": "D",
                    "buts_marques": "BP",
                    "buts_encaisses": "BC",
                    "points": "Pts",
                }
            )

            df.insert(0, "#", range(1, len(df) + 1))

            st.dataframe(
                df[["#", "Équipe", "J", "V", "N", "D", "BP", "BC", "Diff", "Pts"]],
                hide_index=True,
                use_container_width=True,
            )
        else:
            st.info(f"Aucune équipe enregistrée pour {champ_classe}")

    # TAB 4: GESTION
    with tabs[3]:
        st.header("âš™ï¸ Gestion des données")
        afficher_gestion_donnees()


# Alias pour compatibilité
def main():
    app()


__all__ = [
    "app",
    "main",
    "sync_equipes_depuis_api",
    "sync_tous_championnats",
    "sync_matchs_a_venir",
    "refresh_scores_matchs",
    "charger_championnats_disponibles",
    "charger_equipes",
    "charger_matchs_a_venir",
    "charger_matchs_recents",
    "charger_paris_utilisateur",
    "enregistrer_pari",
    "ajouter_equipe",
    "ajouter_match",
    "enregistrer_resultat_match",
    "supprimer_match",
    "afficher_prediction_match",
    "afficher_dashboard_performance",
    "afficher_gestion_donnees",
    "CHAMPIONNATS",
]
