"""Entretien - Onglet export CSV."""

from datetime import date

import streamlit as st

from src.ui import etat_vide
from src.ui.fragments import cached_fragment, ui_fragment

from .logic import generer_planning_previsionnel

# Import pandas pour export
try:
    import pandas as pd

    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False


@cached_fragment(ttl=300)
def onglet_export(mes_objets: list[dict], historique: list[dict]):
    """Onglet export CSV de l'historique et de l'inventaire."""
    st.subheader("📥 Export des données")

    if not HAS_PANDAS:
        st.warning("📦 Pandas non installé. `pip install pandas` pour l'export.")
        return

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 📜 Historique des entretiens")

        if not historique:
            etat_vide("Aucun historique à exporter", "📜")
        else:
            # Préparer le DataFrame
            df_hist = pd.DataFrame(
                [
                    {
                        "Date": h.get("date", ""),
                        "Objet": h.get("objet_id", "").replace("_", " "),
                        "Tâche": h.get("tache_nom", ""),
                        "Pro": "Oui" if h.get("est_pro") else "Non",
                    }
                    for h in historique
                ]
            )
            df_hist = df_hist.sort_values("Date", ascending=False)

            st.dataframe(df_hist, use_container_width=True, height=300)

            # Bouton download CSV
            csv = df_hist.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="📥 Télécharger CSV",
                data=csv,
                file_name=f"entretien_historique_{date.today().isoformat()}.csv",
                mime="text/csv",
                type="primary",
            )

            st.metric("Total tâches", len(historique))

    with col2:
        st.markdown("### 📦 Inventaire équipements")

        if not mes_objets:
            etat_vide("Aucun équipement à exporter", "📦")
        else:
            df_inv = pd.DataFrame(
                [
                    {
                        "Objet": obj.get("objet_id", "").replace("_", " "),
                        "Catégorie": obj.get("categorie_id", "").replace("_", " "),
                        "Pièce": obj.get("piece", ""),
                        "Marque": obj.get("marque", ""),
                        "Date ajout": obj.get("date_ajout", ""),
                        "Date achat": obj.get("date_achat", ""),
                    }
                    for obj in mes_objets
                ]
            )

            st.dataframe(df_inv, use_container_width=True, height=300)

            csv_inv = df_inv.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="📥 Télécharger CSV",
                data=csv_inv,
                file_name=f"entretien_inventaire_{date.today().isoformat()}.csv",
                mime="text/csv",
                key="download_inv",
            )

            st.metric("Total équipements", len(mes_objets))

    st.divider()

    # Planning prévisionnel export
    st.markdown("### 📅 Planning prévisionnel")

    planning = generer_planning_previsionnel(mes_objets, historique, horizon_jours=90)

    if planning:
        df_plan = pd.DataFrame(
            [
                {
                    "Date prévue": t.get("date_prevue", ""),
                    "Jours restants": t.get("jours_restants", 0),
                    "Tâche": t.get("tache_nom", ""),
                    "Objet": t.get("objet_nom", ""),
                    "Pièce": t.get("piece", ""),
                    "Durée (min)": t.get("duree_min", 15),
                }
                for t in planning
            ]
        )

        st.dataframe(df_plan, use_container_width=True, height=200)

        csv_plan = df_plan.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Télécharger Planning CSV",
            data=csv_plan,
            file_name=f"entretien_planning_{date.today().isoformat()}.csv",
            mime="text/csv",
            key="download_plan",
        )
    else:
        st.success("✨ Aucune tâche prévue dans les 90 prochains jours !")
