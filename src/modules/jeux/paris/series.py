"""
Paris Sportifs - Affichage des séries (Loi des séries).

Tableau des séries actuelles pour détecter les opportunités.
Utilise les données de SeriesService pour afficher:
- Série actuelle par marché/championnat
- Fréquence historique
- Value (frequence × serie)
- Niveau d'opportunité (🟢🟡⚪)
"""

import logging

import pandas as pd
import streamlit as st

from src.services.jeux import (
    APSCHEDULER_AVAILABLE,
    FootballDataService,
    SeriesService,
    get_scheduler_service,
    get_sync_service,
)
from src.services.jeux import COMPETITIONS, SEUIL_VALUE_ALERTE, SEUIL_VALUE_HAUTE

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# CONSTANTES UI
# ═══════════════════════════════════════════════════════════

NOMS_MARCHES = {
    "domicile_mi_temps": "Domicile MT",
    "exterieur_mi_temps": "Extérieur MT",
    "nul_mi_temps": "Nul MT",
    "domicile_final": "Domicile Final",
    "exterieur_final": "Extérieur Final",
    "nul_final": "Nul Final",
}

# CSS pour réduire la taille des éléments
STYLES_SERIES = """
<style>
/* Réduire taille metrics dans les séries */
div[data-testid="stMetric"] > div {
    font-size: 0.85rem !important;
}
div[data-testid="stMetric"] label {
    font-size: 0.7rem !important;
}
div[data-testid="stMetric"] [data-testid="stMetricValue"] {
    font-size: 1.1rem !important;
}
</style>
"""


# ═══════════════════════════════════════════════════════════
# FONCTIONS UI
# ═══════════════════════════════════════════════════════════


def afficher_series_paris():
    """Affiche le tableau des séries pour les paris sportifs."""
    # Injecter CSS pour tailles réduites
    st.markdown(STYLES_SERIES, unsafe_allow_html=True)

    st.header("📈 Loi des Séries - Opportunités")

    st.markdown("""
    **Principe**: Plus un événement fréquent n'arrive pas, plus sa probabilité
    de survenir augmente (perception psychologique).

    **Value = Fréquence × Série**
    - 🟢 **Value ≥ 2.5** : Haute opportunité
    - 🟡 **Value ≥ 2.0** : Opportunité moyenne
    - ⚪ **Value < 2.0** : Pas d'opportunité
    """)

    # ─────────────────────────────────────────────────────────────────
    # CONTRÔLES
    # ─────────────────────────────────────────────────────────────────

    col1, col2, col3 = st.columns([2, 2, 1])

    with col1:
        competition = st.selectbox(
            "Championnat",
            options=list(COMPETITIONS.keys()),
            format_func=lambda x: f"{COMPETITIONS[x]} ({x})",
            index=0,  # FL1 par défaut
        )

    with col2:
        filtre_opportunite = st.selectbox(
            "Filtre",
            options=["Toutes", "Opportunités", "Haute seulement"],
            index=0,
        )

    with col3:
        if st.button("🔄 Sync", help="Synchroniser les données depuis l'API"):
            _synchroniser_donnees(competition)

    # ─────────────────────────────────────────────────────────────────
    # AFFICHAGE DES SÉRIES
    # ─────────────────────────────────────────────────────────────────

    # Calculer les séries à la volée (sans DB pour l'instant)
    with st.spinner("Calcul des séries..."):
        data = _calculer_series_competition(competition)

    if not data:
        st.warning(f"Pas de données pour {COMPETITIONS[competition]}. Cliquez sur 🔄 Sync.")
        return

    # Filtrer selon le choix
    df = pd.DataFrame(data)

    if filtre_opportunite == "Opportunités":
        df = df[df["value"] >= SEUIL_VALUE_ALERTE]
    elif filtre_opportunite == "Haute seulement":
        df = df[df["value"] >= SEUIL_VALUE_HAUTE]

    if df.empty:
        st.info("Aucune opportunité détectée avec ce filtre.")
        return

    # Trier par value décroissante
    df = df.sort_values("value", ascending=False)

    # ─────────────────────────────────────────────────────────────────
    # TABLEAU
    # ─────────────────────────────────────────────────────────────────

    st.subheader(f"Séries - {COMPETITIONS[competition]}")

    # En-tête
    col_ind, col_marche, col_serie, col_freq, col_val = st.columns([0.5, 2.5, 1.5, 1.5, 1])
    with col_ind:
        st.caption("")
    with col_marche:
        st.caption("Marché")
    with col_serie:
        st.caption("Série")
    with col_freq:
        st.caption("Fréq.")
    with col_val:
        st.caption("Value")

    # Afficher avec style compact
    for _, row in df.iterrows():
        niveau = row["niveau"]
        marche = row["marche_nom"]
        serie = row["serie"]
        frequence = row["frequence"]
        value = row["value"]

        col_ind, col_marche, col_serie, col_freq, col_val = st.columns([0.5, 2.5, 1.5, 1.5, 1])

        with col_ind:
            st.write(niveau)
        with col_marche:
            st.write(f"**{marche}**")
        with col_serie:
            st.write(f"**{serie}** matchs")
        with col_freq:
            st.write(f"{frequence:.1%}")
        with col_val:
            st.write(f"**{value:.2f}**")

    st.markdown("---")

    # ─────────────────────────────────────────────────────────────────
    # DÉTAILS AVANCÉS
    # ─────────────────────────────────────────────────────────────────

    with st.expander("📊 Tableau détaillé"):
        # Tableau formaté
        df_affichage = df[["marche_nom", "serie", "frequence", "value", "niveau"]].copy()
        df_affichage.columns = ["Marché", "Série", "Fréquence", "Value", "Niveau"]
        df_affichage["Fréquence"] = df_affichage["Fréquence"].apply(lambda x: f"{x:.1%}")
        df_affichage["Value"] = df_affichage["Value"].apply(lambda x: f"{x:.2f}")

        st.dataframe(df_affichage, use_container_width=True, hide_index=True)

    # ─────────────────────────────────────────────────────────────────
    # SCHEDULER STATUS
    # ─────────────────────────────────────────────────────────────────

    with st.expander("⏰ Synchronisation automatique"):
        _afficher_scheduler_status()


def _calculer_series_competition(competition: str) -> list[dict]:
    """
    Calcule les séries pour une compétition.

    Récupère les données depuis l'API et calcule les statistiques.
    """
    try:
        # Essayer d'abord depuis la config
        from src.core.config import obtenir_parametres

        config = obtenir_parametres()
        api_key = getattr(config, "FOOTBALL_DATA_API_KEY", None)

        with FootballDataService(api_key) as service:
            stats = service.calculer_toutes_statistiques(competition, jours=365)

        if not stats:
            return []

        data = []
        for marche, stat in stats.items():
            value = SeriesService.calculer_value(stat.frequence, stat.serie_actuelle)
            niveau = SeriesService.niveau_opportunite(value)

            data.append(
                {
                    "marche": marche,
                    "marche_nom": NOMS_MARCHES.get(marche, marche),
                    "serie": stat.serie_actuelle,
                    "frequence": stat.frequence,
                    "nb_occurrences": stat.nb_occurrences,
                    "total_matchs": stat.total_matchs,
                    "value": round(value, 2),
                    "niveau": niveau,
                }
            )

        return data

    except Exception as e:
        logger.error(f"Erreur calcul séries {competition}: {e}")
        st.error(f"Erreur: {e}")
        return []


def _synchroniser_donnees(competition: str):
    """Synchronise les données depuis l'API."""
    try:
        from src.core.config import obtenir_parametres

        config = obtenir_parametres()
        api_key = getattr(config, "FOOTBALL_DATA_API_KEY", None)

        if not api_key:
            st.warning("⚠️ Clé API Football-Data non configurée")
            return

        sync_service = get_sync_service()
        with st.spinner(f"Synchronisation {COMPETITIONS[competition]}..."):
            result = sync_service.synchroniser_paris(competition, api_key)

        if result.get("erreurs"):
            st.warning(f"⚠️ Erreurs: {result['erreurs']}")
        else:
            st.success(
                f"✅ {result.get('marches_maj', 0)} marchés, "
                f"{result.get('alertes_creees', 0)} alertes"
            )
        st.rerun()

    except Exception as e:
        logger.error(f"Erreur sync: {e}")
        st.error(f"Erreur synchronisation: {e}")


def _afficher_scheduler_status():
    """Affiche le statut du scheduler."""
    if not APSCHEDULER_AVAILABLE:
        st.warning("APScheduler non installé")
        return

    scheduler = get_scheduler_service()

    col1, col2 = st.columns(2)

    with col1:
        if scheduler.est_demarre:
            st.success("🟢 Scheduler actif")
        else:
            st.info("⚪ Scheduler arrêté")

        if st.button("▶️ Démarrer" if not scheduler.est_demarre else "⏹ Arrêter"):
            if scheduler.est_demarre:
                scheduler.arreter()
            else:
                scheduler.demarrer(competitions=["FL1"], inclure_loto=True)
            st.rerun()

    with col2:
        st.markdown("**Prochaines exécutions:**")
        prochaines = scheduler.obtenir_prochaines_executions()
        if prochaines:
            for type_sync, dt in prochaines.items():
                st.caption(f"• {type_sync}: {dt.strftime('%d/%m %H:%M')}")
        else:
            st.caption("Aucune exécution programmée")

    # Historique
    historique = scheduler.obtenir_historique(limite=5)
    if historique:
        st.markdown("**Dernières exécutions:**")
        for entry in historique:
            ts = entry.get("timestamp", "?")
            type_s = entry.get("type", "?")
            comp = entry.get("competition", "")
            st.caption(f"• {ts[:16]} - {type_s} {comp}")


# ═══════════════════════════════════════════════════════════
# MÉTRIQUES RAPIDES
# ═══════════════════════════════════════════════════════════


def afficher_metriques_series():
    """Affiche des métriques rapides pour le dashboard."""
    try:
        # Récupérer opportunités haute
        from src.core.config import obtenir_parametres

        config = obtenir_parametres()
        api_key = getattr(config, "FOOTBALL_DATA_API_KEY", None)

        with FootballDataService(api_key) as service:
            stats = service.calculer_toutes_statistiques("FL1", jours=365)

        opportunites_haute = 0
        opportunites_moyenne = 0

        for stat in stats.values():
            value = SeriesService.calculer_value(stat.frequence, stat.serie_actuelle)
            if value >= SEUIL_VALUE_HAUTE:
                opportunites_haute += 1
            elif value >= SEUIL_VALUE_ALERTE:
                opportunites_moyenne += 1

        col1, col2 = st.columns(2)
        with col1:
            st.metric("🟢 Haute", opportunites_haute)
        with col2:
            st.metric("🟡 Moyenne", opportunites_moyenne)

    except Exception as e:
        logger.debug(f"Erreur métriques: {e}")


# ═══════════════════════════════════════════════════════════
# EXPORT
# ═══════════════════════════════════════════════════════════

__all__ = [
    "afficher_series_paris",
    "afficher_metriques_series",
]
