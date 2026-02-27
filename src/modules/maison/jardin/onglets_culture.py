"""Jardin - Onglets gestion des plantes, récoltes et plan.

Extrait de onglets.py (Phase 4 Audit, item 18 — split >500 LOC).
"""

import logging
from datetime import date

import streamlit as st

from src.core.session_keys import SK
from src.core.state import rerun
from src.ui.fragments import ui_fragment

from .data import charger_catalogue_plantes
from .db_access import (
    ajouter_plante_jardin,
    ajouter_recolte_jardin,
    mettre_a_jour_plante_jardin,
    supprimer_plante_jardin,
)
from .ui import afficher_calendrier_plante, afficher_compagnons

logger = logging.getLogger(__name__)


@ui_fragment
def onglet_mes_plantes(mes_plantes: list[dict]):
    """Onglet de gestion des plantes."""
    st.subheader("🌿 Mes Plantations")

    catalogue = charger_catalogue_plantes()

    # Bouton ajouter
    if st.button("➕ Ajouter une plante", type="primary", use_container_width=True):
        st.session_state.jardin_mode_ajout = True

    # Mode ajout
    if st.session_state.get(SK.JARDIN_MODE_AJOUT):
        st.markdown("### Choisir une plante")

        # Filtres
        categories = list(
            set(p.get("categorie", "Autre") for p in catalogue.get("plantes", {}).values())
        )
        categorie_filtre = st.selectbox("Catégorie", ["Toutes"] + sorted(categories))

        # Grille de plantes
        plantes_filtrees = {
            k: v
            for k, v in catalogue.get("plantes", {}).items()
            if categorie_filtre == "Toutes" or v.get("categorie") == categorie_filtre
        }

        cols = st.columns(4)
        for i, (plante_id, plante_data) in enumerate(plantes_filtrees.items()):
            with cols[i % 4]:
                if st.button(
                    f"{plante_data.get('emoji', '🌱')} {plante_data.get('nom', plante_id)}",
                    key=f"add_{plante_id}",
                    use_container_width=True,
                ):
                    st.session_state.jardin_plante_selectionnee = plante_id

        # Formulaire d'ajout détaillé
        if st.session_state.get(SK.JARDIN_PLANTE_SELECTIONNEE):
            plante_id = st.session_state.jardin_plante_selectionnee
            plante_data = catalogue.get("plantes", {}).get(plante_id, {})

            st.markdown(f"### {plante_data.get('emoji', '🌱')} {plante_data.get('nom', plante_id)}")

            # Calendrier
            afficher_calendrier_plante(plante_data)

            # Compagnons
            afficher_compagnons(plante_data)

            st.divider()

            with st.form("form_ajout_plante"):
                surface = st.number_input("Surface (m²)", min_value=0.1, value=1.0, step=0.5)
                quantite = st.number_input(
                    "Nombre de plants", min_value=1, value=plante_data.get("densite_plants_m2", 4)
                )
                zone = st.text_input("Zone/Emplacement", placeholder="Ex: Carré potager nord")

                semis_fait = st.checkbox("Semis déjà effectué")
                en_terre = st.checkbox("Déjà planté en terre")

                if st.form_submit_button("✅ Ajouter au jardin", type="primary"):
                    nouvelle_plante = {
                        "plante_id": plante_id,
                        "surface_m2": surface,
                        "quantite": quantite,
                        "zone": zone,
                        "semis_fait": semis_fait,
                        "plante_en_terre": en_terre,
                        "date_ajout": date.today().isoformat(),
                    }
                    # Persister en DB
                    ajouter_plante_jardin(nouvelle_plante)
                    mes_plantes.append(nouvelle_plante)
                    st.session_state.mes_plantes_jardin = mes_plantes
                    st.session_state.jardin_mode_ajout = False
                    st.session_state.jardin_plante_selectionnee = None
                    st.session_state._jardin_reload = True
                    st.success(f"✅ {plante_data.get('nom')} ajouté au jardin !")
                    rerun()

        if st.button("❌ Annuler"):
            st.session_state.jardin_mode_ajout = False
            st.session_state.jardin_plante_selectionnee = None
            rerun()

    else:
        # Afficher mes plantes
        if not mes_plantes:
            st.info("🌱 Votre jardin est vide. Ajoutez vos premières plantes pour commencer !")
            return

        for i, ma_plante in enumerate(mes_plantes):
            plante_id = ma_plante.get("plante_id")
            plante_data = catalogue.get("plantes", {}).get(plante_id, {})

            with st.expander(
                f"{plante_data.get('emoji', '🌱')} **{plante_data.get('nom', plante_id)}** - {ma_plante.get('surface_m2', 1)}m²",
                expanded=False,
            ):
                col1, col2 = st.columns([3, 1])

                with col1:
                    st.write(f"📍 Zone: {ma_plante.get('zone', 'Non définie')}")
                    st.write(f"🌱 Quantité: {ma_plante.get('quantite', 1)} plants")

                    statut = []
                    if ma_plante.get("semis_fait"):
                        statut.append("✅ Semis")
                    if ma_plante.get("plante_en_terre"):
                        statut.append("✅ En terre")
                    st.write(f"État: {' • '.join(statut) if statut else '⏳ À semer'}")

                    afficher_calendrier_plante(plante_data)

                with col2:
                    if not ma_plante.get("semis_fait"):
                        if st.button("🌱 Semis fait", key=f"semis_{i}"):
                            mes_plantes[i]["semis_fait"] = True
                            db_id = ma_plante.get("db_id")
                            if db_id:
                                mettre_a_jour_plante_jardin(db_id, {"semis_fait": True})
                            st.session_state.mes_plantes_jardin = mes_plantes
                            st.session_state._jardin_reload = True
                            rerun()

                    elif not ma_plante.get("plante_en_terre"):
                        if st.button("🏡 Planté", key=f"plante_{i}"):
                            mes_plantes[i]["plante_en_terre"] = True
                            db_id = ma_plante.get("db_id")
                            if db_id:
                                mettre_a_jour_plante_jardin(db_id, {"plante_en_terre": True})
                            st.session_state.mes_plantes_jardin = mes_plantes
                            st.session_state._jardin_reload = True
                            rerun()

                    if st.button("🗑️", key=f"del_{i}", help="Supprimer"):
                        db_id = ma_plante.get("db_id")
                        if db_id:
                            supprimer_plante_jardin(db_id)
                        mes_plantes.pop(i)
                        st.session_state.mes_plantes_jardin = mes_plantes
                        st.session_state._jardin_reload = True
                        rerun()


@ui_fragment
def onglet_recoltes(mes_plantes: list[dict], recoltes: list[dict]):
    """Onglet enregistrement des récoltes."""
    st.subheader("🥕 Mes Récoltes")

    catalogue = charger_catalogue_plantes()

    # Formulaire nouvelle récolte
    with st.expander("➕ Enregistrer une récolte", expanded=not recoltes):
        plantes_en_terre = [p for p in mes_plantes if p.get("plante_en_terre")]

        if not plantes_en_terre:
            st.info(
                "Aucune plante en terre. Les récoltes seront possibles une fois vos plantes établies."
            )
        else:
            plante_options = {
                p[
                    "plante_id"
                ]: f"{catalogue.get('plantes', {}).get(p['plante_id'], {}).get('emoji', '🌱')} {catalogue.get('plantes', {}).get(p['plante_id'], {}).get('nom', p['plante_id'])}"
                for p in plantes_en_terre
            }

            with st.form("form_recolte"):
                plante_sel = st.selectbox(
                    "Plante",
                    options=list(plante_options.keys()),
                    format_func=lambda x: plante_options[x],
                )
                quantite = st.number_input("Quantité (kg)", min_value=0.1, value=0.5, step=0.1)
                date_recolte = st.date_input("Date", value=date.today())
                notes = st.text_area("Notes", placeholder="Qualité, observations...")

                if st.form_submit_button("✅ Enregistrer", type="primary"):
                    nouvelle_recolte = {
                        "plante_id": plante_sel,
                        "quantite_kg": quantite,
                        "date": date_recolte.isoformat(),
                        "notes": notes,
                    }
                    # Persister en DB
                    ajouter_recolte_jardin(nouvelle_recolte)
                    recoltes.append(nouvelle_recolte)
                    st.session_state.recoltes_jardin = recoltes
                    st.session_state._jardin_reload = True
                    st.success(f"✅ Récolte de {quantite}kg enregistrée !")
                    rerun()

    # Historique
    if recoltes:
        st.markdown("### Historique")

        # Stats rapides
        total_kg = sum(r.get("quantite_kg", 0) for r in recoltes)
        st.metric("Total récolté", f"{total_kg:.1f} kg")

        # Liste
        for recolte in sorted(recoltes, key=lambda r: r.get("date", ""), reverse=True):
            plante_data = catalogue.get("plantes", {}).get(recolte.get("plante_id"), {})
            st.markdown(
                f"""
            <div class="recolte-item">
                <span style="font-size: 1.5rem">{plante_data.get("emoji", "🌱")}</span>
                <span><strong>{plante_data.get("nom", recolte.get("plante_id"))}</strong></span>
                <span class="quantite">{recolte.get("quantite_kg")} kg</span>
                <span style="color: #718096">{recolte.get("date")}</span>
            </div>
            """,
                unsafe_allow_html=True,
            )


@ui_fragment
def onglet_plan(mes_plantes: list[dict] | None = None):
    """Onglet plan du jardin — redirige vers le plan interactif 2D/3D."""
    from .onglets_plan import onglet_plan_interactif

    onglet_plan_interactif()
