"""
Paramètres - Configuration Budget
Catégories de dépenses et sauvegarde des données
"""

import streamlit as st

from src.ui.feedback import afficher_erreur, afficher_succes, spinner_intelligent


def render_budget_config():
    """Configuration du budget."""

    st.markdown("### 💰 Budget")

    # Section Budget
    st.markdown("#### 📈 Catégories de dépenses")

    try:
        from src.services.budget import CategorieDepense

        # Mapping complet avec accents
        emoji_map = {
            "alimentation": "🍞",
            "courses": "🛒",
            "maison": "🏠",
            "santé": "🏥",
            "transport": "🚗",
            "loisirs": "🎮",
            "vêtements": "👕",
            "enfant": "👶",
            "éducation": "📚",
            "services": "🔧",
            "impôts": "📋",
            "épargne": "💰",
            "gaz": "🔥",
            "electricite": "⚡",
            "eau": "💧",
            "internet": "🌐",
            "loyer": "🏘️",
            "assurance": "🛡️",
            "taxe_fonciere": "🏛️",
            "creche": "🧒",
            "autre": "📦",
        }

        # Affichage en grille
        categories = list(CategorieDepense)
        cols = st.columns(4)
        for i, cat in enumerate(categories):
            with cols[i % 4]:
                emoji = emoji_map.get(cat.value, "📦")
                st.markdown(f"{emoji} {cat.value.replace('_', ' ').capitalize()}")

        st.info("👉 Accède au module **Budget** dans le menu Famille pour gérer tes dépenses")

    except ImportError:
        st.warning("Module budget non disponible")

    st.markdown("---")

    # Section Backup
    st.markdown("#### 💾 Sauvegarde des données")

    try:
        from src.services.backup import get_backup_service

        backup_service = get_backup_service()

        col1, col2 = st.columns(2)

        with col1:
            if st.button("💾 Créer une sauvegarde", type="primary", use_container_width=True):
                with spinner_intelligent("Sauvegarde en cours..."):
                    result = backup_service.create_backup()
                    if result.success:
                        afficher_succes(f"✅ {result.message}")
                    else:
                        afficher_erreur(f"❌ {result.message}")

        with col2:
            if st.button("📂 Voir les sauvegardes", use_container_width=True):
                backups = backup_service.list_backups()
                if backups:
                    for b in backups[:5]:
                        st.text(f"📄 {b.filename} ({b.size_bytes // 1024} KB)")
                else:
                    st.info("Aucune sauvegarde trouvée")

    except ImportError:
        st.warning("Module backup non disponible")
