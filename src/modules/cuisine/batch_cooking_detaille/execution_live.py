"""
Composant d'exécution live du Batch Cooking avec st.status()

Utilise st.status() de Streamlit pour afficher la progression
multi-étapes du batch cooking en temps réel.
"""

import logging
from datetime import datetime, timedelta

import streamlit as st

from src.core.session_keys import SK

logger = logging.getLogger(__name__)


def executer_batch_cooking_live(batch_data: dict) -> bool:
    """
    Exécute le batch cooking avec progression st.status().

    Args:
        batch_data: Données du batch (recettes, étapes, etc.)

    Returns:
        True si exécution complète, False sinon
    """
    if not batch_data:
        st.warning("⚠️ Aucune donnée de batch cooking")
        return False

    recettes = batch_data.get("recettes", [])
    session_info = batch_data.get("session", {})

    if not recettes:
        st.warning("⚠️ Aucune recette dans le batch")
        return False

    # Collecter toutes les étapes
    toutes_etapes = []
    for recette in recettes:
        nom_recette = recette.get("nom", "Recette")
        for etape in recette.get("etapes_batch", []):
            toutes_etapes.append(
                {
                    "recette": nom_recette,
                    "description": etape.get("description", ""),
                    "duree_minutes": etape.get("duree_minutes", 10),
                    "type": etape.get("type", "preparation"),
                    "robot": etape.get("robot"),
                }
            )

    if not toutes_etapes:
        st.warning("⚠️ Aucune étape de batch cooking trouvée")
        return False

    # Initialiser l'état de progression si nécessaire
    if "batch_etape_courante" not in st.session_state:
        st.session_state.batch_etape_courante = 0
    if "batch_heure_debut" not in st.session_state:
        st.session_state.batch_heure_debut = datetime.now()

    etape_courante = st.session_state.batch_etape_courante
    total_etapes = len(toutes_etapes)
    heure_debut = st.session_state.batch_heure_debut

    # ── Progression globale ──
    progress_pct = int((etape_courante / total_etapes) * 100) if total_etapes else 0
    st.progress(progress_pct / 100, text=f"Progression: {etape_courante}/{total_etapes} étapes ({progress_pct}%)")

    # ── Afficher les étapes terminées (résumé compact) ──
    if etape_courante > 0:
        with st.expander(f"✅ {etape_courante} étape(s) terminée(s)", expanded=False):
            for i, etape in enumerate(toutes_etapes[:etape_courante]):
                icon = (
                    "🔪" if etape["type"] == "preparation"
                    else "🔥" if etape["type"] == "cuisson"
                    else "🥣"
                )
                st.caption(f"{icon} ~~{etape['recette']}: {etape['description']}~~")

    # ── Étape en cours ──
    if etape_courante < total_etapes:
        etape = toutes_etapes[etape_courante]
        recette_nom = etape["recette"]
        description = etape["description"]
        duree = etape["duree_minutes"]
        type_etape = etape["type"]
        robot = etape.get("robot")

        icon = (
            "🔪" if type_etape == "preparation"
            else "🔥" if type_etape == "cuisson"
            else "🥣"
        )
        robot_info = f" • 🤖 {robot}" if robot else ""

        st.markdown(f"### {icon} Étape {etape_courante + 1}/{total_etapes}")

        with st.container(border=True):
            st.markdown(f"**{recette_nom}**")
            st.markdown(f"{description}")
            st.caption(f"⏱️ Durée estimée: {duree} min{robot_info}")

        # Aperçu de l'étape suivante
        if etape_courante + 1 < total_etapes:
            next_etape = toutes_etapes[etape_courante + 1]
            st.caption(f"⏭️ Prochaine étape: {next_etape['recette']} — {next_etape['description']}")

        st.divider()

        # Bouton pour passer à l'étape suivante
        col_prev, col_next = st.columns([1, 2])
        with col_prev:
            if etape_courante > 0:
                if st.button("⬅️ Précédent", use_container_width=True):
                    st.session_state.batch_etape_courante -= 1
                    st.rerun()
        with col_next:
            if st.button(
                f"✅ Terminé — Passer à l'étape {etape_courante + 2}"
                if etape_courante + 1 < total_etapes
                else "✅ Terminer le batch cooking",
                type="primary",
                use_container_width=True,
            ):
                st.session_state.batch_etape_courante += 1
                st.rerun()

        return False  # Pas encore terminé

    # ── Toutes les étapes terminées: phase stockage ──
    st.markdown("### 📦 Stockage")
    for recette in recettes:
        stockage = recette.get("stockage", "frigo")
        duree_conservation = recette.get("duree_conservation_jours", 3)
        st.write(f"📦 {recette['nom']} → {stockage.upper()} ({duree_conservation}j)")

    # Résumé final
    heure_fin = datetime.now()
    duree_totale = heure_fin - heure_debut
    minutes_totales = int(duree_totale.total_seconds() / 60)

    st.success(
        f"""
    ### 🎉 Batch Cooking Terminé!

    - **{total_etapes} étapes** complétées
    - **{len(recettes)} recettes** préparées
    - **Durée**: {minutes_totales} minutes
    """
    )

    # Nettoyer l'état
    del st.session_state["batch_etape_courante"]
    del st.session_state["batch_heure_debut"]

    return True


def afficher_execution_live():
    """Affiche l'interface d'exécution live du batch cooking."""

    st.markdown("### 🎬 Exécution Live")
    st.caption("Suivez votre session de batch cooking en temps réel")

    batch_data = st.session_state.get(SK.BATCH_DATA, {})

    if not batch_data:
        st.info("👆 Générez d'abord les instructions dans l'onglet 'Préparer'")
        return

    # Afficher résumé avant exécution
    recettes = batch_data.get("recettes", [])
    session_info = batch_data.get("session", {})
    duree_estimee = session_info.get("duree_estimee_minutes", 120)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("🍳 Recettes", len(recettes))

    with col2:
        total_etapes = sum(len(r.get("etapes_batch", [])) for r in recettes)
        st.metric("📋 Étapes", total_etapes)

    with col3:
        st.metric("⏱️ Durée estimée", f"{duree_estimee} min")

    st.divider()

    # État de l'exécution
    if "batch_en_cours" not in st.session_state:
        st.session_state.batch_en_cours = False

    if "batch_termine" not in st.session_state:
        st.session_state.batch_termine = False

    # Bouton de démarrage
    if not st.session_state.batch_en_cours and not st.session_state.batch_termine:
        if st.button("▶️ Démarrer le Batch Cooking", type="primary", use_container_width=True):
            st.session_state.batch_en_cours = True
            # Initialiser la progression
            st.session_state.batch_etape_courante = 0
            st.session_state.batch_heure_debut = datetime.now()
            st.rerun()

    # Exécution étape par étape
    if st.session_state.batch_en_cours:
        success = executer_batch_cooking_live(batch_data)
        if success:
            st.session_state.batch_en_cours = False
            st.session_state.batch_termine = True

    # Terminé
    if st.session_state.batch_termine:
        if st.button("🔄 Recommencer", use_container_width=True):
            st.session_state.batch_termine = False
            for key in ["batch_etape_courante", "batch_heure_debut"]:
                st.session_state.pop(key, None)
            st.rerun()


# Export pour utilisation dans le module
__all__ = [
    "executer_batch_cooking_live",
    "afficher_execution_live",
]
