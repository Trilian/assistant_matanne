"""
Loto - Affichage des numéros en retard (Loi des séries).

Tableau des numéros en retard selon la loi des séries.
Utilise les données de LotoDataService pour afficher:
- Série actuelle (tirages depuis dernière sortie)
- Fréquence historique vs théorique
- Value (frequence × serie)
- Niveau d'opportunité (🟢🟡⚪)

⚠️ RAPPEL: Le Loto est un jeu de hasard pur. La "loi des séries"
est une perception psychologique, pas une réalité mathématique.
"""

import logging
from typing import Any

import pandas as pd
import streamlit as st

from src.services.jeux import (
    NB_NUMEROS_CHANCE,
    NB_NUMEROS_PRINCIPAUX,
    NUMEROS_PAR_TIRAGE,
    SEUIL_VALUE_ALERTE,
    SEUIL_VALUE_HAUTE,
    LotoDataService,
    SeriesService,
    get_sync_service,
)
from src.ui import etat_vide

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# FONCTIONS UI
# ═══════════════════════════════════════════════════════════


def afficher_series_loto():
    """Affiche le tableau des numéros en retard pour le Loto."""
    st.header("📈 Numéros en Retard")

    # Avertissement
    st.warning("""
    **⚠️ Rappel**: La "loi des séries" est une **perception psychologique**.
    Chaque tirage est **totalement indépendant**. Un numéro "en retard" n'a
    **pas plus de chances** de sortir au prochain tirage.
    """)

    st.markdown("""
    **Value = Fréquence × Série**
    - 🟢 **Value ≥ 2.5** : Numéro très en retard
    - 🟡 **Value ≥ 2.0** : Numéro en retard
    - ⚪ **Value < 2.0** : Dans la normale
    """)

    # ─────────────────────────────────────────────────────────────────
    # CONTRÔLES
    # ─────────────────────────────────────────────────────────────────

    col1, col2, col3 = st.columns([2, 2, 1])

    with col1:
        type_numero = st.selectbox(
            "Type de numéro",
            options=["principal", "chance"],
            format_func=lambda x: (
                "Numéros principaux (1-49)" if x == "principal" else "Numéro Chance (1-10)"
            ),
        )

    with col2:
        filtre_opportunite = st.selectbox(
            "Filtre",
            options=["Tous", "En retard", "Très en retard"],
            index=1,  # Par défaut: En retard
        )

    with col3:
        if st.button("🔄 Sync", help="Télécharger les derniers tirages"):
            _synchroniser_loto()

    # ─────────────────────────────────────────────────────────────────
    # CALCUL DES SÉRIES
    # ─────────────────────────────────────────────────────────────────

    with st.spinner("Analyse des tirages..."):
        data = _calculer_numeros_retard(type_numero)

    if not data:
        st.warning("Pas de données. Cliquez sur 🔄 Sync pour télécharger les tirages.")
        return

    # Filtrer selon le choix
    df = pd.DataFrame(data)

    if filtre_opportunite == "En retard":
        df = df[df["value"] >= SEUIL_VALUE_ALERTE]
    elif filtre_opportunite == "Très en retard":
        df = df[df["value"] >= SEUIL_VALUE_HAUTE]

    # Trier par value décroissante
    df = df.sort_values("value", ascending=False)

    if df.empty:
        etat_vide("Aucun numéro en retard avec ce filtre", "🔢")
        return

    # ─────────────────────────────────────────────────────────────────
    # AFFICHAGE VISUEL
    # ─────────────────────────────────────────────────────────────────

    st.subheader(f"{'Numéros principaux' if type_numero == 'principal' else 'Numéros Chance'}")

    # Grille de numéros
    # Top numéros en retard
    top_numeros = df.head(10)

    st.markdown("**Top numéros en retard:**")
    cols = st.columns(min(len(top_numeros), 5))

    for i, (_, row) in enumerate(top_numeros.iterrows()):
        col_idx = i % 5
        with cols[col_idx]:
            niveau = row["niveau"]
            numero = row["numero"]
            value = row["value"]
            serie = row["serie"]

            st.markdown(
                f"""
            <div style="text-align: center; padding: 10px; border-radius: 10px;
                        background-color: {"#90EE90" if niveau == "🟢" else "#FFFFE0" if niveau == "🟡" else "#F5F5F5"};">
                <span style="font-size: 24px; font-weight: bold;">{numero}</span><br>
                <span style="font-size: 14px;">{niveau} Value: {value:.1f}</span><br>
                <span style="font-size: 12px; color: gray;">{serie} tirages</span>
            </div>
            """,
                unsafe_allow_html=True,
            )

    # ─────────────────────────────────────────────────────────────────
    # TABLEAU DÉTAILLÉ
    # ─────────────────────────────────────────────────────────────────

    with st.expander("📊 Tableau complet"):
        df_affichage = df[
            ["numero", "serie", "frequence", "frequence_theorique", "value", "niveau"]
        ].copy()

        df_affichage.columns = [
            "Numéro",
            "Série",
            "Fréquence obs.",
            "Fréquence théo.",
            "Value",
            "Niveau",
        ]
        df_affichage["Fréquence obs."] = df_affichage["Fréquence obs."].apply(lambda x: f"{x:.1%}")
        df_affichage["Fréquence théo."] = df_affichage["Fréquence théo."].apply(
            lambda x: f"{x:.1%}"
        )
        df_affichage["Value"] = df_affichage["Value"].apply(lambda x: f"{x:.2f}")

        st.dataframe(df_affichage, use_container_width=True, hide_index=True)

    # ─────────────────────────────────────────────────────────────────
    # INFOS TIRAGES
    # ─────────────────────────────────────────────────────────────────

    with st.expander("ℹ️ Informations"):
        if data:
            total_tirages = data[0].get("total_tirages", 0)
            st.metric("Tirages analysés", total_tirages)

            freq_theorique = (
                NUMEROS_PAR_TIRAGE / NB_NUMEROS_PRINCIPAUX
                if type_numero == "principal"
                else 1 / NB_NUMEROS_CHANCE
            )
            st.markdown(f"""
            **Fréquence théorique**: {freq_theorique:.1%}

            - Numéros principaux: 5 numéros parmi 49 → {NUMEROS_PAR_TIRAGE}/{NB_NUMEROS_PRINCIPAUX} ≈ 10.2%
            - Numéro Chance: 1 numéro parmi 10 → 10%

            **Calcul de la Value**:
            ```
            Value = Fréquence observée × Série actuelle
            ```

            Exemple: Si un numéro sort 10% du temps et n'est pas sorti depuis 25 tirages:
            ```
            Value = 0.10 × 25 = 2.5 (en retard)
            ```
            """)


def _calculer_numeros_retard(type_numero: str) -> list[dict[str, Any]]:
    """
    Calcule les statistiques de retard pour chaque numéro.
    """
    try:
        with LotoDataService() as service:
            # Télécharger historique
            tirages = service.telecharger_historique("nouveau_loto")

            if not tirages:
                return []

            # Calculer pour chaque numéro
            max_numero = NB_NUMEROS_PRINCIPAUX if type_numero == "principal" else NB_NUMEROS_CHANCE
            freq_theorique = (
                NUMEROS_PAR_TIRAGE / NB_NUMEROS_PRINCIPAUX
                if type_numero == "principal"
                else 1 / NB_NUMEROS_CHANCE
            )

            data = []
            for num in range(1, max_numero + 1):
                stats = service.calculer_statistiques_numero(num, tirages, type_numero)
                niveau = SeriesService.niveau_opportunite(stats.value)

                data.append(
                    {
                        "numero": num,
                        "serie": stats.serie_actuelle,
                        "frequence": stats.frequence,
                        "frequence_theorique": freq_theorique,
                        "nb_sorties": stats.nb_sorties,
                        "total_tirages": stats.total_tirages,
                        "derniere_sortie": stats.derniere_sortie,
                        "value": stats.value,
                        "niveau": niveau,
                    }
                )

            return data

    except Exception as e:
        logger.error(f"Erreur calcul numéros retard: {e}")
        st.error(f"Erreur: {e}")
        return []


def _synchroniser_loto():
    """Synchronise les données Loto."""
    try:
        sync_service = get_sync_service()
        with st.spinner("Téléchargement des tirages..."):
            result = sync_service.synchroniser_loto(type_numeros="tous")

        if result.get("erreurs"):
            st.warning(f"⚠️ Erreurs: {result['erreurs']}")
        else:
            st.success(
                f"✅ {result.get('numeros_maj', 0)} numéros analysés, "
                f"{result.get('alertes_creees', 0)} alertes"
            )
        st.rerun()

    except Exception as e:
        logger.error(f"Erreur sync loto: {e}")
        st.error(f"Erreur: {e}")


# ═══════════════════════════════════════════════════════════
# MÉTRIQUES RAPIDES
# ═══════════════════════════════════════════════════════════


def afficher_metriques_loto():
    """Affiche des métriques rapides pour le dashboard."""
    try:
        with LotoDataService() as service:
            tirages = service.telecharger_historique("nouveau_loto")
            if not tirages:
                return

            numeros_retard = service.obtenir_numeros_en_retard(
                tirages, seuil_value=SEUIL_VALUE_ALERTE
            )

        haute = sum(1 for n in numeros_retard if n.value >= SEUIL_VALUE_HAUTE)
        moyenne = len(numeros_retard) - haute

        col1, col2 = st.columns(2)
        with col1:
            st.metric("🟢 Très en retard", haute)
        with col2:
            st.metric("🟡 En retard", moyenne)

    except Exception as e:
        logger.debug(f"Erreur métriques loto: {e}")


# ═══════════════════════════════════════════════════════════
# EXPORT
# ═══════════════════════════════════════════════════════════

__all__ = [
    "afficher_series_loto",
    "afficher_metriques_loto",
]
