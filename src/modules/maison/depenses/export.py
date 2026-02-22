"""
Depenses Maison - Export PDF/CSV/Excel

Génération et téléchargement des données de dépenses.
"""

import io

import pandas as pd

from src.ui.keys import KeyNamespace

_keys = KeyNamespace("depenses")

from .crud import get_depenses_annee
from .utils import CATEGORY_LABELS, MOIS_FR, date, st


def afficher_export_section():
    """Section d'export PDF/CSV des dépenses."""
    st.subheader("📥 Export des données")

    today = date.today()

    col1, col2 = st.columns(2)
    with col1:
        annee_export = st.selectbox(
            "Année à exporter", options=range(today.year, 2019, -1), key=_keys("export_annee")
        )
    with col2:
        format_export = st.selectbox("Format", options=["CSV", "Excel"], key=_keys("export_format"))

    if st.button("📥 Générer l'export", type="primary", use_container_width=True):
        # Récupérer toutes les dépenses de l'année
        toutes_depenses = get_depenses_annee(int(annee_export))

        if not toutes_depenses:
            st.warning(f"Aucune dépense trouvée pour {annee_export}")
            return

        # Convertir en DataFrame
        data = []
        for d in toutes_depenses:
            data.append(
                {
                    "Mois": MOIS_FR[d.mois],
                    "Année": d.annee,
                    "Catégorie": CATEGORY_LABELS.get(d.categorie, d.categorie),
                    "Montant (€)": float(d.montant),
                    "Consommation": float(d.consommation) if d.consommation else "",
                    "Note": d.note or "",
                }
            )

        df = pd.DataFrame(data)

        # Total par mois
        st.markdown(f"**{len(data)} dépenses** pour un total de **{df['Montant (€)'].sum():.2f}€**")

        # Exporter
        if format_export == "CSV":
            csv = df.to_csv(index=False, encoding="utf-8-sig")
            st.download_button(
                label="⬇️ Télécharger CSV",
                data=csv,
                file_name=f"depenses_maison_{annee_export}.csv",
                mime="text/csv",
            )
        else:
            # Excel
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine="openpyxl") as writer:
                df.to_excel(writer, sheet_name="Dépenses", index=False)

                # Résumé par catégorie
                resume = df.groupby("Catégorie")["Montant (€)"].sum().reset_index()
                resume.columns = ["Catégorie", "Total (€)"]
                resume.to_excel(writer, sheet_name="Résumé", index=False)

            output.seek(0)

            st.download_button(
                label="⬇️ Télécharger Excel",
                data=output.getvalue(),
                file_name=f"depenses_maison_{annee_export}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )

        st.success("✅ Export généré avec succès !")
