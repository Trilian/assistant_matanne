"""
Service Import/Export Inventaire
Format CSV pour faciliter la gestion
"""
from src.utils.formatters import format_quantity, format_quantity_with_unit

import csv
import io
import logging
from typing import List, Dict
from datetime import datetime, date

logger = logging.getLogger(__name__)


# ===================================
# EXPORT
# ===================================


class InventaireExporter:
    """Export inventaire en CSV"""

    @staticmethod
    def to_csv(inventaire: List[Dict]) -> str:
        """
        Exporte l'inventaire en CSV

        Args:
            inventaire: Liste d'articles

        Returns:
            String CSV
        """
        output = io.StringIO()

        fieldnames = [
            "Nom",
            "Catégorie",
            "Quantité",
            "Unité",
            "Seuil",
            "Emplacement",
            "Péremption",
            "Statut",
        ]

        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()

        for item in inventaire:
            writer.writerow(
                {
                    "Nom": item["nom"],
                    "Catégorie": item["categorie"],
                    "Quantité": f"{format_quantity(item['quantite'])}",
                    "Unité": item["unite"],
                    "Seuil": f"{format_quantity(item['seuil'])}",
                    "Emplacement": item["emplacement"],
                    "Péremption": item["date_peremption"].strftime("%d/%m/%Y")
                    if item.get("date_peremption")
                    else "",
                    "Statut": item["statut"],
                }
            )

        logger.info(f"Export CSV: {len(inventaire)} articles")
        return output.getvalue()

    @staticmethod
    def to_excel_format(inventaire: List[Dict]) -> List[List]:
        """
        Format pour Excel/Sheets

        Returns:
            Liste de listes (tableau)
        """
        data = [["Nom", "Catégorie", "Quantité", "Unité", "Seuil", "Emplacement", "Péremption"]]

        for item in inventaire:
            data.append(
                [
                    item["nom"],
                    item["categorie"],
                    item["quantite"],
                    item["unite"],
                    item["seuil"],
                    item["emplacement"],
                    item["date_peremption"].strftime("%d/%m/%Y")
                    if item.get("date_peremption")
                    else "",
                ]
            )

        return data


# ===================================
# IMPORT
# ===================================


class InventaireImporter:
    """Import inventaire depuis CSV"""

    @staticmethod
    def from_csv(csv_str: str) -> List[Dict]:
        """
        Importe depuis CSV

        Args:
            csv_str: Contenu CSV

        Returns:
            Liste d'articles validés
        """
        reader = csv.DictReader(io.StringIO(csv_str))

        articles = []
        errors = []

        for row_num, row in enumerate(reader, start=2):
            try:
                # Validation basique
                nom = row.get("Nom", "").strip()
                if not nom:
                    errors.append(f"Ligne {row_num}: Nom manquant")
                    continue

                # Parse quantité
                try:
                    quantite = float(row.get("Quantité", "0").replace(",", "."))
                except ValueError:
                    errors.append(f"Ligne {row_num}: Quantité invalide")
                    continue

                # Parse seuil
                try:
                    seuil = float(row.get("Seuil", "1").replace(",", "."))
                except ValueError:
                    seuil = 1.0

                # Parse date
                date_peremption = None
                date_str = row.get("Péremption", "").strip()
                if date_str:
                    try:
                        date_peremption = datetime.strptime(date_str, "%d/%m/%Y").date()
                    except ValueError:
                        try:
                            date_peremption = datetime.strptime(date_str, "%Y-%m-%d").date()
                        except ValueError:
                            errors.append(f"Ligne {row_num}: Date péremption invalide")

                articles.append(
                    {
                        "nom": nom,
                        "categorie": row.get("Catégorie", "Autre").strip() or "Autre",
                        "quantite": quantite,
                        "unite": row.get("Unité", "pcs").strip() or "pcs",
                        "seuil": seuil,
                        "emplacement": row.get("Emplacement", "").strip() or None,
                        "date_peremption": date_peremption,
                    }
                )

            except Exception as e:
                errors.append(f"Ligne {row_num}: {str(e)}")

        logger.info(f"Import CSV: {len(articles)} articles, {len(errors)} erreurs")

        return articles, errors

    @staticmethod
    def validate_csv_structure(csv_str: str) -> tuple[bool, str]:
        """
        Valide la structure du CSV

        Returns:
            (valide: bool, message: str)
        """
        try:
            reader = csv.DictReader(io.StringIO(csv_str))
            fieldnames = reader.fieldnames

            required = ["Nom", "Quantité"]
            missing = [f for f in required if f not in fieldnames]

            if missing:
                return False, f"Colonnes manquantes: {', '.join(missing)}"

            # Vérifier au moins une ligne
            try:
                next(reader)
                return True, "Structure valide"
            except StopIteration:
                return False, "CSV vide"

        except Exception as e:
            return False, f"Erreur structure: {str(e)}"


# ===================================
# TEMPLATE
# ===================================


def get_csv_template() -> str:
    """
    Retourne un template CSV vide

    Returns:
        String CSV avec headers
    """
    return """Nom,Catégorie,Quantité,Unité,Seuil,Emplacement,Péremption
Tomates,Légumes,2.5,kg,1.0,Frigo,15/12/2025
Pâtes,Féculents,500,g,200,Placard,
Lait,Laitier,1,L,0.5,Frigo,20/12/2025
"""


# ===================================
# HELPERS STREAMLIT
# ===================================


def render_export_ui(inventaire: List[Dict]):
    """Widget Streamlit pour l'export"""
    import streamlit as st

    st.markdown("### 📤 Exporter l'Inventaire")

    if st.button("📥 Télécharger CSV", use_container_width=True):
        csv_data = InventaireExporter.to_csv(inventaire)

        st.download_button(
            label="💾 Télécharger inventaire.csv",
            data=csv_data,
            file_name=f"inventaire_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True,
        )


def render_import_ui(inventaire_service):
    """Widget Streamlit pour l'import"""
    import streamlit as st

    st.markdown("### 📥 Importer depuis CSV")

    # Template
    with st.expander("📄 Télécharger template CSV"):
        template = get_csv_template()
        st.download_button("💾 Template.csv", template, "template_inventaire.csv", "text/csv")

        st.caption("Format attendu:")
        st.code(template, language="csv")

    # Upload
    uploaded = st.file_uploader("Choisir un fichier CSV", type=["csv"], key="import_csv")

    if uploaded:
        try:
            content = uploaded.read().decode("utf-8")

            # Valider structure
            valide, message = InventaireImporter.validate_csv_structure(content)

            if not valide:
                st.error(f"❌ {message}")
                return

            st.success(f"✅ {message}")

            # Parser
            articles, errors = InventaireImporter.from_csv(content)

            if errors:
                with st.expander("⚠️ Erreurs détectées"):
                    for error in errors:
                        st.warning(error)

            if articles:
                st.success(f"✅ {len(articles)} article(s) détecté(s)")

                # Aperçu
                with st.expander("👁️ Aperçu"):
                    import pandas as pd

                    df = pd.DataFrame(articles[:10])
                    st.dataframe(df, use_container_width=True)

                # Import
                if st.button(
                    "➕ Importer tous les articles", type="primary", use_container_width=True
                ):
                    count_added = 0
                    count_errors = 0

                    for article in articles:
                        try:
                            inventaire_service.ajouter_ou_modifier(
                                nom=article["nom"],
                                categorie=article["categorie"],
                                quantite=article["quantite"],
                                unite=article["unite"],
                                seuil=article["seuil"],
                                emplacement=article.get("emplacement"),
                                date_peremption=article.get("date_peremption"),
                            )
                            count_added += 1
                        except Exception as e:
                            count_errors += 1
                            logger.error(f"Erreur import {article['nom']}: {e}")

                    st.success(f"✅ {count_added} article(s) importé(s)")
                    if count_errors > 0:
                        st.warning(f"⚠️ {count_errors} erreur(s)")

                    st.balloons()
                    st.rerun()

        except Exception as e:
            st.error(f"❌ Erreur: {str(e)}")
