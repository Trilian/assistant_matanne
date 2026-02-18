"""
Interface UI pour la gestion des sauvegardes.

Note: Ce fichier a été extrait depuis src/services/backup/service.py
pour respecter la séparation UI/Services.
"""

from pathlib import Path

import streamlit as st

from src.services.backup.service import obtenir_service_backup


def afficher_sauvegarde():
    """Affiche l'interface de gestion des backups dans Streamlit."""
    st.subheader("💾 Sauvegarde & Restauration")

    service = obtenir_service_backup()

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Créer un backup")

        compress = st.checkbox("Compresser (gzip)", value=True, key="backup_compress")

        if st.button("📥 Créer un backup maintenant", use_container_width=True, type="primary"):
            with st.spinner("Création du backup..."):
                result = service.creer_sauvegarde(compress=compress)

                if result and result.success:
                    st.success(f"✅ {result.message}")
                    st.info(
                        f"📊 {result.metadata.total_records} enregistrements, "
                        f"{result.metadata.file_size_bytes / 1024:.1f} KB"
                    )
                else:
                    st.error("❌ Erreur lors de la création du backup")

    with col2:
        st.markdown("### Backups disponibles")

        backups = service.lister_sauvegardes()

        if not backups:
            st.info("Aucun backup disponible")
        else:
            for backup in backups[:5]:  # Afficher les 5 derniers
                with st.expander(f"📝 {backup.id}"):
                    st.write(f"**Date:** {backup.created_at.strftime('%d/%m/%Y %H:%M')}")
                    st.write(f"**Taille:** {backup.file_size_bytes / 1024:.1f} KB")
                    st.write(f"**Compressé:** {'Oui' if backup.compressed else 'Non'}")

                    col_a, col_b = st.columns(2)
                    with col_a:
                        if st.button("🔄 Restaurer", key=f"restore_{backup.id}"):
                            st.warning("⚠️ Cette action va écraser les données actuelles!")
                    with col_b:
                        if st.button("🗑️ Supprimer", key=f"delete_{backup.id}"):
                            if service.supprimer_sauvegarde(backup.id):
                                st.success("Backup supprimé")
                                st.rerun()

    # Section restauration
    st.markdown("---")
    st.markdown("### Restaurer depuis un fichier")

    uploaded_file = st.file_uploader(
        "Choisir un fichier de backup", type=["json", "gz"], key="backup_upload"
    )

    if uploaded_file:
        clear_existing = st.checkbox(
            "Supprimer les données existantes avant restauration",
            value=False,
            key="clear_before_restore",
        )

        if st.button("🔄 Restaurer ce backup", type="secondary"):
            # Sauvegarder temporairement le fichier
            temp_path = Path(service.config.backup_dir) / f"temp_{uploaded_file.name}"
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.read())

            with st.spinner("Restauration en cours..."):
                result = service.restaurer_sauvegarde(str(temp_path), clear_existing=clear_existing)

                if result.success:
                    st.success(f"✅ {result.message}")
                    st.info(f"📊 {result.records_restored} enregistrements restaurés")
                else:
                    st.error(f"❌ {result.message}")
                    if result.errors:
                        for error in result.errors:
                            st.warning(error)

            # Nettoyer le fichier temporaire
            temp_path.unlink(missing_ok=True)


# Alias rétrocompatibilité
render_backup_ui = afficher_sauvegarde


__all__ = [
    "afficher_sauvegarde",
    "render_backup_ui",
]
