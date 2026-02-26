"""
Paramètres - Gestion des profils utilisateurs.

Édition du profil actif, préférences par module, vue des deux profils.
"""

from __future__ import annotations

import logging

import streamlit as st

from src.core.state import obtenir_etat
from src.ui.feedback import afficher_erreur, afficher_succes
from src.ui.fragments import ui_fragment
from src.ui.keys import KeyNamespace

logger = logging.getLogger(__name__)

_keys = KeyNamespace("param_profils")


@ui_fragment
def afficher_profils_config():
    """Gestion des profils utilisateurs."""
    from src.services.profils import (
        AVATARS_DISPONIBLES,
        PREFERENCES_MODULES_DEFAUT,
        ProfilService,
    )

    st.markdown("### 👥 Gestion des Profils")
    st.caption("Gère les profils utilisateurs (Anne & Mathieu)")

    etat = obtenir_etat()

    # ── Section 1: Profil actif ──
    profils = ProfilService.obtenir_profils()
    if not profils:
        st.warning("Aucun profil trouvé en base de données.")
        return

    # Trouver le profil actif
    profil_actif = None
    for p in profils:
        if p.display_name == etat.nom_utilisateur or p.username == etat.nom_utilisateur.lower():
            profil_actif = p
            break
    if not profil_actif:
        profil_actif = profils[0]

    st.markdown(
        f"#### ✏️ Éditer le profil : {profil_actif.avatar_emoji} {profil_actif.display_name}"
    )

    with st.form("profil_edition_form"):
        col1, col2 = st.columns(2)

        with col1:
            display_name = st.text_input(
                "Nom affiché",
                value=profil_actif.display_name,
                max_chars=100,
            )
            avatar = st.selectbox(
                "Avatar",
                AVATARS_DISPONIBLES,
                index=(
                    AVATARS_DISPONIBLES.index(profil_actif.avatar_emoji)
                    if profil_actif.avatar_emoji in AVATARS_DISPONIBLES
                    else 0
                ),
            )
            email = st.text_input(
                "Email (optionnel)",
                value=profil_actif.email or "",
                max_chars=200,
            )

        with col2:
            taille = st.number_input(
                "Taille (cm)",
                min_value=100,
                max_value=250,
                value=profil_actif.taille_cm or 170,
            )
            poids = st.number_input(
                "Poids (kg)",
                min_value=30.0,
                max_value=200.0,
                value=float(profil_actif.poids_kg or 70.0),
                step=0.5,
            )
            objectif_poids = st.number_input(
                "Objectif poids (kg)",
                min_value=30.0,
                max_value=200.0,
                value=float(profil_actif.objectif_poids_kg or 70.0),
                step=0.5,
            )

        st.markdown("##### 🏃 Objectifs fitness")
        col3, col4, col5 = st.columns(3)

        with col3:
            pas = st.number_input(
                "Pas quotidiens",
                min_value=1000,
                max_value=50000,
                value=profil_actif.objectif_pas_quotidien or 10000,
                step=1000,
            )
        with col4:
            calories = st.number_input(
                "Calories brûlées / jour",
                min_value=100,
                max_value=3000,
                value=profil_actif.objectif_calories_brulees or 500,
                step=50,
            )
        with col5:
            minutes = st.number_input(
                "Minutes actives / jour",
                min_value=10,
                max_value=300,
                value=profil_actif.objectif_minutes_actives or 30,
                step=5,
            )

        submitted = st.form_submit_button(
            "💾 Sauvegarder le profil", type="primary", use_container_width=True
        )

        if submitted:
            data = {
                "display_name": display_name,
                "avatar_emoji": avatar,
                "email": email if email else None,
                "taille_cm": taille,
                "poids_kg": poids,
                "objectif_poids_kg": objectif_poids,
                "objectif_pas_quotidien": pas,
                "objectif_calories_brulees": calories,
                "objectif_minutes_actives": minutes,
            }
            resultat = ProfilService.mettre_a_jour_profil(profil_actif.username, data)
            if resultat:
                # Mettre à jour le nom global si changé
                etat.nom_utilisateur = display_name
                # Invalider cache sidebar
                st.session_state.pop("profils_disponibles", None)
                afficher_succes("✅ Profil sauvegardé avec succès !")
            else:
                afficher_erreur("❌ Erreur lors de la sauvegarde")

    # ── Section 2: Préférences par module ──
    st.markdown("---")
    st.markdown("#### 🎯 Préférences par module")

    prefs_actuelles = profil_actif.preferences_modules or PREFERENCES_MODULES_DEFAUT.copy()

    modules_config = {
        "🍳 Cuisine": (
            "cuisine",
            {
                "nb_suggestions_ia": ("Nombre de suggestions IA", 1, 20, 5),
                "duree_max_batch_min": ("Durée max batch cooking (min)", 30, 300, 120),
            },
        ),
        "👶 Famille": (
            "famille",
            {
                "frequence_rappels_routines": None,  # handled separately
            },
        ),
        "🏠 Maison": (
            "maison",
            {
                "seuil_alerte_entretien_jours": ("Seuil alerte entretien (jours)", 1, 30, 7),
            },
        ),
        "📅 Planning": ("planning", {}),
        "💰 Budget": (
            "budget",
            {
                "seuils_alerte_pct": ("Seuil alerte budget (%)", 50, 100, 80),
            },
        ),
    }

    for label, (module_key, champs) in modules_config.items():
        with st.expander(label, expanded=False):
            module_prefs = prefs_actuelles.get(module_key, {})

            for champ_key, config in champs.items():
                if config is None:
                    # Champ spécial
                    if champ_key == "frequence_rappels_routines":
                        freq = st.selectbox(
                            "Fréquence rappels routines",
                            ["quotidien", "hebdomadaire", "desactive"],
                            index=["quotidien", "hebdomadaire", "desactive"].index(
                                module_prefs.get("frequence_rappels_routines", "quotidien")
                            ),
                            key=_keys(f"freq_{module_key}"),
                        )
                        module_prefs["frequence_rappels_routines"] = freq
                else:
                    label_champ, min_val, max_val, default_val = config
                    val = st.number_input(
                        label_champ,
                        min_value=min_val,
                        max_value=max_val,
                        value=module_prefs.get(champ_key, default_val),
                        key=_keys(f"{module_key}_{champ_key}"),
                    )
                    module_prefs[champ_key] = val

            prefs_actuelles[module_key] = module_prefs

    if st.button("💾 Sauvegarder les préférences modules", key=_keys("save_prefs")):
        resultat = ProfilService.mettre_a_jour_profil(
            profil_actif.username, {"preferences_modules": prefs_actuelles}
        )
        if resultat:
            afficher_succes("✅ Préférences modules sauvegardées !")
        else:
            afficher_erreur("❌ Erreur lors de la sauvegarde")

    # ── Section 3: Vue de tous les profils ──
    st.markdown("---")
    st.markdown("#### 👥 Tous les profils")

    for profil in profils:
        actif = " ✅ (actif)" if profil.username == profil_actif.username else ""
        with st.expander(f"{profil.avatar_emoji} {profil.display_name}{actif}"):
            col_a, col_b = st.columns(2)
            with col_a:
                st.write(f"**Username:** {profil.username}")
                st.write(f"**Email:** {profil.email or '—'}")
                st.write(f"**Thème:** {profil.theme_prefere}")
            with col_b:
                st.write(f"**Taille:** {profil.taille_cm or '—'} cm")
                st.write(f"**Poids:** {profil.poids_kg or '—'} kg")
                st.write(f"**Objectif:** {profil.objectif_poids_kg or '—'} kg")
            if profil.preferences_modules:
                st.json(profil.preferences_modules)
