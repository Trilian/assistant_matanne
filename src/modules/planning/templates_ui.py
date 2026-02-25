"""
Interface utilisateur pour la gestion des templates de semaine.

Permet de:
- Voir et gérer les templates existants
- Créer de nouveaux templates
- Appliquer un template à une semaine
- Créer un template depuis une semaine existante
"""

from datetime import date, timedelta

import streamlit as st

from src.core.date_utils import obtenir_debut_semaine
from src.core.monitoring import profiler_rerun
from src.modules._framework import error_boundary
from src.services.cuisine.planning.templates import (
    JOURS_SEMAINE,
    obtenir_service_templates,
)
from src.ui import etat_vide
from src.ui.feedback import afficher_erreur, afficher_succes
from src.ui.keys import KeyNamespace
from src.ui.state.url import tabs_with_url

_keys = KeyNamespace("templates")


@profiler_rerun("templates_ui")
def app():
    """Point d'entrée du module templates."""
    st.title("📋 Templates de semaine")
    st.caption("Créez des semaines types et appliquez-les facilement")

    with error_boundary("templates_ui"):
        service = obtenir_service_templates()

        # Onglets principaux
        TAB_LABELS = [
            "📑 Mes templates",
            "➕ Créer",
            "📅 Appliquer",
        ]
        tabs_with_url(TAB_LABELS, param="tab")
        tab_liste, tab_creer, tab_appliquer = st.tabs(TAB_LABELS)

        # ═══════════════════════════════════════════════════════════
        # TAB: LISTE DES TEMPLATES
        # ═══════════════════════════════════════════════════════════
        with tab_liste:
            templates = service.lister_templates(actifs_seulement=False)

            if not templates:
                etat_vide("Aucun template créé", "📋", "Utilisez l'onglet 'Créer' pour commencer")
            else:
                for template in templates:
                    with st.expander(f"📋 {template.nom}", expanded=False):
                        if template.description:
                            st.caption(template.description)

                        # Afficher les items par jour
                        items_par_jour = service.get_items_par_jour(template)

                        for jour_idx, items in items_par_jour.items():
                            if items:
                                st.markdown(f"**{JOURS_SEMAINE[jour_idx]}**")
                                for item in items:
                                    heure = f"{item.heure_debut}"
                                    if item.heure_fin:
                                        heure += f" - {item.heure_fin}"
                                    st.markdown(f"- {heure}: {item.titre}")

                        # Actions
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("🗑️ Supprimer", key=f"del_{template.id}"):
                                if service.supprimer_template(template.id):
                                    afficher_succes("Template supprimé")
                                    st.rerun()
                                else:
                                    afficher_erreur("Erreur lors de la suppression")

        # ═══════════════════════════════════════════════════════════
        # TAB: CRÉER UN TEMPLATE
        # ═══════════════════════════════════════════════════════════
        with tab_creer:
            st.subheader("Créer un nouveau template")

            mode = st.radio(
                "Mode de création",
                ["✍️ Création manuelle", "📥 Depuis une semaine existante"],
                horizontal=True,
            )

            if mode == "✍️ Création manuelle":
                with st.form("form_creer_template"):
                    nom = st.text_input("Nom du template *", placeholder="Ex: Semaine type travail")
                    description = st.text_area(
                        "Description", placeholder="Description optionnelle..."
                    )

                    st.markdown("---")
                    st.markdown("**Ajouter des événements type**")

                    # Formulaire pour plusieurs items
                    items_data = []
                    for i in range(3):  # 3 slots d'événements
                        st.markdown(f"*Événement {i + 1}*")
                        cols = st.columns([2, 2, 2, 3])
                        with cols[0]:
                            jour = st.selectbox(
                                "Jour",
                                options=list(range(7)),
                                format_func=lambda x: JOURS_SEMAINE[x],
                                key=f"jour_{i}",
                            )
                        with cols[1]:
                            heure_debut = st.text_input("Début", value="09:00", key=f"debut_{i}")
                        with cols[2]:
                            heure_fin = st.text_input("Fin", value="10:00", key=f"fin_{i}")
                        with cols[3]:
                            titre = st.text_input("Titre", key=f"titre_{i}")

                        if titre:  # Seulement si un titre est donné
                            items_data.append(
                                {
                                    "jour_semaine": jour,
                                    "heure_debut": heure_debut,
                                    "heure_fin": heure_fin if heure_fin else None,
                                    "titre": titre,
                                }
                            )

                    submitted = st.form_submit_button(
                        "✅ Créer le template", use_container_width=True
                    )

                    if submitted:
                        if not nom:
                            afficher_erreur("Le nom est obligatoire")
                        elif not items_data:
                            afficher_erreur("Ajoutez au moins un événement")
                        else:
                            try:
                                service.creer_template(
                                    nom=nom, description=description, items=items_data
                                )
                                afficher_succes(
                                    f"Template '{nom}' créé avec {len(items_data)} événements"
                                )
                                st.rerun()
                            except Exception as e:
                                afficher_erreur(f"Erreur: {e}")

            else:  # Depuis une semaine existante
                st.markdown("Sélectionnez une semaine pour en faire un template.")

                col1, col2 = st.columns(2)
                with col1:
                    date_ref = st.date_input("Date dans la semaine", value=date.today())
                with col2:
                    nom_template = st.text_input(
                        "Nom du template *", placeholder="Ex: Ma semaine du 10/02"
                    )

                description_template = st.text_area(
                    "Description", placeholder="Description optionnelle..."
                )

                lundi = obtenir_debut_semaine(date_ref)
                st.info(
                    f"📅 Semaine du {lundi.strftime('%d/%m/%Y')} au "
                    f"{(lundi + timedelta(days=6)).strftime('%d/%m/%Y')}"
                )

                if st.button("📥 Créer depuis cette semaine", use_container_width=True):
                    if not nom_template:
                        afficher_erreur("Le nom est obligatoire")
                    else:
                        template = service.creer_depuis_semaine(
                            nom=nom_template,
                            date_lundi=lundi,
                            description=description_template,
                        )
                        if template:
                            afficher_succes(
                                f"Template '{nom_template}' créé avec "
                                f"{len(template.items)} événements"
                            )
                            st.rerun()
                        else:
                            afficher_erreur("Aucun événement trouvé dans cette semaine")

        # ═══════════════════════════════════════════════════════════
        # TAB: APPLIQUER UN TEMPLATE
        # ═══════════════════════════════════════════════════════════
        with tab_appliquer:
            st.subheader("Appliquer un template")

            templates = service.lister_templates()

            if not templates:
                etat_vide("Aucun template disponible", "📋", "Créez-en un d'abord")
            else:
                col1, col2 = st.columns(2)
                with col1:
                    template_id = st.selectbox(
                        "Template à appliquer",
                        options=[t.id for t in templates],
                        format_func=lambda x: next((t.nom for t in templates if t.id == x), ""),
                    )

                with col2:
                    date_cible = st.date_input("Date dans la semaine cible", value=date.today())

                lundi_cible = obtenir_debut_semaine(date_cible)
                st.info(
                    f"📅 Les événements seront créés du {lundi_cible.strftime('%d/%m/%Y')} "
                    f"au {(lundi_cible + timedelta(days=6)).strftime('%d/%m/%Y')}"
                )

                # Prévisualiser le template sélectionné
                selected_template = service.get_template(template_id)
                if selected_template:
                    with st.expander("👁️ Aperçu du template", expanded=True):
                        items_par_jour = service.get_items_par_jour(selected_template)
                        cols = st.columns(7)
                        for jour_idx, col in enumerate(cols):
                            with col:
                                st.markdown(f"**{JOURS_SEMAINE[jour_idx][:3]}**")
                                for item in items_par_jour[jour_idx]:
                                    st.caption(f"{item.heure_debut}")
                                    st.markdown(f"_{item.titre}_")

                if st.button("✅ Appliquer le template", type="primary", use_container_width=True):
                    events = service.appliquer_template(template_id, lundi_cible)
                    if events:
                        afficher_succes(
                            f"{len(events)} événements créés pour la semaine "
                            f"du {lundi_cible.strftime('%d/%m')}"
                        )
                    else:
                        afficher_erreur("Aucun événement créé")


__all__ = ["app"]
