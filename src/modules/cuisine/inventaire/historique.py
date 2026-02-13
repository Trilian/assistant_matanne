"""
Historique des modifications - Onglet historique de l'inventaire.
Affiche l'historique des modifications de l'inventaire.
"""

import pandas as pd
import streamlit as st

from src.services.inventaire import get_inventaire_service


def render_historique():
    """Affiche l'historique des modifications de l'inventaire"""
    service = get_inventaire_service()

    if service is None:
        st.error("❌ Service inventaire indisponible")
        return

    st.subheader("📋 Historique des Modifications")

    # Filtres
    col1, col2, col3 = st.columns(3)

    with col1:
        days = st.slider("Période (jours)", 1, 90, 30)

    with col2:
        article_id = st.selectbox(
            "Article (optionnel)",
            options=["Tous"] + [f"Article #{i}" for i in range(1, 20)],
            index=0,
        )

    with col3:
        type_modif = st.multiselect(
            "Type modification",
            options=["ajout", "modification", "suppression"],
            default=["ajout", "modification", "suppression"],
        )

    # Récupérer historique
    try:
        historique = service.get_historique(days=days)

        if not historique:
            st.info("📋 Aucune modification enregistrée dans cette période")
            return

        # Filtrer par type
        historique_filtres = [h for h in historique if h["type"] in type_modif]

        if not historique_filtres:
            st.info("Aucune modification ne correspond aux filtres")
            return

        # Afficher tableau
        data = []
        for h in historique_filtres:
            action_icon = {"ajout": "➕", "modification": "âœï¸", "suppression": "🗑️"}.get(
                h["type"], "❓"
            )

            # Résumer les changements
            changements = []
            if h["quantite_avant"] is not None:
                changements.append(f"Qty: {h['quantite_avant']:.1f} → {h['quantite_apres']:.1f}")
            if h["emplacement_avant"] is not None:
                changements.append(f"Empl: {h['emplacement_avant']} → {h['emplacement_apres']}")
            if h["date_peremption_avant"] is not None:
                changements.append(
                    f"Péremption: {h['date_peremption_avant']} → {h['date_peremption_apres']}"
                )

            changement_text = " | ".join(changements) if changements else "Détails disponibles"

            data.append(
                {
                    "Date": pd.Timestamp(h["date_modification"]).strftime("%d/%m/%Y %H:%M"),
                    "Article": h["ingredient_nom"],
                    "Action": f"{action_icon} {h['type']}",
                    "Changements": changement_text,
                }
            )

        df = pd.DataFrame(data)
        st.dataframe(df, width="stretch", hide_index=True)

        st.divider()

        # Stats
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total modifications", len(historique_filtres))
        with col2:
            ajouts = len([h for h in historique_filtres if h["type"] == "ajout"])
            st.metric("Ajouts", ajouts)
        with col3:
            modifs = len([h for h in historique_filtres if h["type"] == "modification"])
            st.metric("Modifications", modifs)

    except Exception as e:
        st.error(f"❌ Erreur: {str(e)}")


__all__ = ["render_historique"]
