"""
Composant d'exécution live du Batch Cooking avec st.status()

Utilise st.status() de Streamlit pour afficher la progression
multi-étapes du batch cooking en temps réel.
"""

import logging
import time
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

    # Exécution avec st.status()
    with st.status("🍳 **Batch Cooking en cours...**", expanded=True) as status:
        heure_debut = datetime.now()
        etapes_terminees = 0
        total_etapes = len(toutes_etapes)

        # Phase 1: Préparation
        status.update(label="📋 **Phase 1: Préparation**", state="running")
        st.write("🔄 Vérification des ingrédients...")
        time.sleep(0.5)  # Simulation
        st.write("✅ Ingrédients prêts")

        # Afficher les conseils d'organisation
        conseils = session_info.get("conseils_organisation", [])
        if conseils:
            st.write("💡 **Conseils:**")
            for conseil in conseils[:3]:
                st.write(f"  • {conseil}")

        st.divider()

        # Phase 2: Exécution des étapes
        status.update(label="👩‍🍳 **Phase 2: Cuisson & Préparation**", state="running")

        for i, etape in enumerate(toutes_etapes, 1):
            # Mise à jour du status
            progress_pct = int((i / total_etapes) * 100)
            status.update(
                label=f"👩‍🍳 **Étape {i}/{total_etapes}** ({progress_pct}%)", state="running"
            )

            # Afficher l'étape en cours
            recette_nom = etape["recette"]
            description = etape["description"]
            duree = etape["duree_minutes"]
            type_etape = etape["type"]
            robot = etape.get("robot")

            # Icône selon le type
            icon = (
                "🔪" if type_etape == "preparation" else "🔥" if type_etape == "cuisson" else "🥣"
            )
            robot_info = f" ({robot})" if robot else ""

            st.write(f"{icon} **{recette_nom}**: {description}{robot_info}")
            st.caption(f"⏱️ Durée estimée: {duree} min")

            # Barre de progression pour cette étape (simulation)
            progress_bar = st.progress(0)
            for p in range(100):
                time.sleep(0.02)  # Simulation de progression
                progress_bar.progress(p + 1)

            st.write(f"✅ Étape {i} terminée")
            etapes_terminees += 1

            # Pause entre les étapes
            if i < total_etapes:
                st.write("---")

        # Phase 3: Finalisation
        status.update(label="📦 **Phase 3: Stockage**", state="running")
        st.write("🔄 Stockage des préparations...")

        for recette in recettes:
            stockage = recette.get("stockage", "frigo")
            duree_conservation = recette.get("duree_conservation_jours", 3)
            st.write(f"📦 {recette['nom']} → {stockage.upper()} ({duree_conservation}j)")

        time.sleep(0.5)
        st.write("✅ Toutes les préparations sont stockées")

        # Terminé !
        heure_fin = datetime.now()
        duree_totale = heure_fin - heure_debut
        minutes_totales = int(duree_totale.total_seconds() / 60)

        status.update(
            label=f"✅ **Batch Cooking Terminé!** ({etapes_terminees} étapes en {minutes_totales}min)",
            state="complete",
            expanded=False,
        )

    # Résumé final
    st.success(
        f"""
    ### 🎉 Batch Cooking Terminé!

    - **{etapes_terminees} étapes** complétées
    - **{len(recettes)} recettes** préparées
    - **Durée**: {minutes_totales} minutes
    """
    )

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
            st.rerun()

    # Exécution
    if st.session_state.batch_en_cours:
        success = executer_batch_cooking_live(batch_data)
        st.session_state.batch_en_cours = False
        st.session_state.batch_termine = success
        st.rerun()

    # Terminé
    if st.session_state.batch_termine:
        if st.button("🔄 Recommencer", use_container_width=True):
            st.session_state.batch_termine = False
            st.rerun()


# Export pour utilisation dans le module
__all__ = [
    "executer_batch_cooking_live",
    "afficher_execution_live",
]
