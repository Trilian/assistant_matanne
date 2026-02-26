"""
Module Import en Masse — Import CSV avec templates et validation.

Import de données en masse avec templates téléchargeables,
validation ligne par ligne, mode dry-run et rapport d'erreurs.
"""

import logging

import streamlit as st

from src.core.monitoring import profiler_rerun
from src.modules._framework import error_boundary
from src.services.utilitaires.import_service import TEMPLATES_CSV, get_import_service
from src.ui.keys import KeyNamespace

logger = logging.getLogger(__name__)

_keys = KeyNamespace("import_masse")


@profiler_rerun("import_masse")
def app():
    """Point d'entrée module Import en Masse."""
    st.title("📥 Import en Masse")
    st.caption("Importez vos données depuis des fichiers CSV")

    with error_boundary(titre="Erreur import"):
        service = get_import_service()

        # Onglet 1: Templates
        tab1, tab2 = st.tabs(["📋 Templates CSV", "📤 Importer"])

        with tab1:
            _afficher_templates(service)

        with tab2:
            _afficher_import(service)


def _afficher_templates(service):
    """Affiche les templates téléchargeables."""
    st.subheader("📋 Templates CSV")
    st.caption("Téléchargez un template, remplissez-le, puis importez-le.")

    for domaine, config in TEMPLATES_CSV.items():
        with st.container(border=True):
            col1, col2, col3 = st.columns([3, 2, 1])
            with col1:
                st.markdown(f"**{config['label']}**")
                st.caption(f"Colonnes: {', '.join(config['colonnes'])}")
            with col2:
                st.caption("Exemple:")
                st.json(config["exemple"])
            with col3:
                csv_data = service.generer_template_csv(domaine)
                st.download_button(
                    "⬇️ Template",
                    data=csv_data,
                    file_name=f"template_{domaine}.csv",
                    mime="text/csv",
                    key=_keys("template", domaine),
                    use_container_width=True,
                )


def _afficher_import(service):
    """Interface d'import avec upload et validation."""
    st.subheader("📤 Importer un fichier CSV")

    col1, col2 = st.columns([1, 1])

    with col1:
        domaine = st.selectbox(
            "Domaine",
            options=list(TEMPLATES_CSV.keys()),
            format_func=lambda x: TEMPLATES_CSV[x]["label"],
            key=_keys("domaine"),
        )

    with col2:
        dry_run = st.toggle(
            "🔍 Mode aperçu (dry run)",
            value=True,
            key=_keys("dry_run"),
            help="Valide les données sans les importer",
        )

    fichier = st.file_uploader(
        "Fichier CSV",
        type=["csv"],
        key=_keys("fichier"),
        help="Format attendu: UTF-8 avec séparateur virgule",
    )

    if fichier:
        contenu = fichier.getvalue().decode("utf-8")

        # Aperçu du fichier
        with st.expander("👁️ Aperçu du fichier", expanded=True):
            import csv
            import io

            reader = csv.DictReader(io.StringIO(contenu))
            rows = list(reader)
            st.dataframe(rows[:10], use_container_width=True)
            st.caption(f"{len(rows)} ligne(s) détectée(s)")

        # Validation / Import
        st.divider()

        label = "🔍 Valider" if dry_run else "📤 Importer"
        if st.button(label, type="primary", key=_keys("go"), use_container_width=True):
            with st.spinner("Traitement en cours..."):
                resultat = service.importer_donnees(domaine, contenu, dry_run=dry_run)

            # Afficher résultats
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("📊 Total lignes", resultat.total_lignes)
            with col2:
                st.metric(
                    "✅ Importées" if not dry_run else "✅ Valides",
                    resultat.lignes_importees,
                )
            with col3:
                st.metric("❌ Erreurs", resultat.lignes_erreur)

            if resultat.taux_succes == 100:
                st.success(
                    f"{'✅ Import réussi!' if not dry_run else '✅ Validation OK — désactivez le mode aperçu pour importer.'}"
                )
            elif resultat.taux_succes > 0:
                st.warning(f"⚠️ {resultat.taux_succes:.0f}% de succès")
            else:
                st.error("❌ Aucune donnée importée")

            # Détail des erreurs
            if resultat.erreurs:
                with st.expander(f"❌ {len(resultat.erreurs)} erreur(s)", expanded=True):
                    for err in resultat.erreurs:
                        st.markdown(f"- **Ligne {err['ligne']}**: {err['erreur']}")
