"""Jardin - Onglets principaux."""

import logging
from datetime import date, datetime

import streamlit as st

from .data import charger_catalogue_plantes
from .logic import (
    calculer_autonomie,
    calculer_stats_jardin,
    calculer_streak_jardin,
    generer_planning_jardin,
    generer_previsions_recoltes,
    generer_taches_jardin,
    obtenir_badges_jardin,
)
from .ui import (
    afficher_badges_jardin,
    afficher_calendrier_plante,
    afficher_compagnons,
    afficher_planning_jardin_ui,
    afficher_previsions_recoltes_ui,
    afficher_score_jardin_gamifie,
    afficher_tache,
)

# Import optionnel Plotly
try:
    import plotly.express as px
    import plotly.graph_objects as go

    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False

# Import pandas pour export
try:
    import pandas as pd

    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False

logger = logging.getLogger(__name__)


def onglet_taches(mes_plantes: list[dict], meteo: dict):
    """Onglet des tâches automatiques."""
    st.subheader("🎯 Tâches du jour")

    taches = generer_taches_jardin(mes_plantes, meteo)

    if not taches:
        st.success("✨ **Rien à faire aujourd'hui !** Votre jardin est à jour.")
        st.info(
            "Les tâches apparaîtront automatiquement selon le calendrier, la météo et vos plantations."
        )
        return

    # Résumé
    urgentes = len([t for t in taches if t["priorite"] in ["urgente", "haute"]])
    temps_total = sum(t["duree_min"] for t in taches)

    col1, col2, col3 = st.columns(3)
    col1.metric("Tâches", len(taches))
    col2.metric("Urgentes", urgentes, delta=None if urgentes == 0 else "⚠️")
    col3.metric("Temps estimé", f"{temps_total} min")

    st.divider()

    # Afficher les tâches
    for i, tache in enumerate(taches):
        done = afficher_tache(tache, f"tache_{i}")
        if done:
            st.toast(f"✅ {tache['titre']} accompli !")
            # TODO: Sauvegarder en base


def onglet_mes_plantes(mes_plantes: list[dict]):
    """Onglet de gestion des plantes."""
    st.subheader("🌿 Mes Plantations")

    catalogue = charger_catalogue_plantes()

    # Bouton ajouter
    if st.button("➕ Ajouter une plante", type="primary", use_container_width=True):
        st.session_state.jardin_mode_ajout = True

    # Mode ajout
    if st.session_state.get("jardin_mode_ajout"):
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
        if st.session_state.get("jardin_plante_selectionnee"):
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
                    mes_plantes.append(nouvelle_plante)
                    st.session_state.mes_plantes_jardin = mes_plantes
                    st.session_state.jardin_mode_ajout = False
                    st.session_state.jardin_plante_selectionnee = None
                    st.success(f"✅ {plante_data.get('nom')} ajouté au jardin !")
                    st.rerun()

        if st.button("❌ Annuler"):
            st.session_state.jardin_mode_ajout = False
            st.session_state.jardin_plante_selectionnee = None
            st.rerun()

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
                            st.session_state.mes_plantes_jardin = mes_plantes
                            st.rerun()

                    elif not ma_plante.get("plante_en_terre"):
                        if st.button("🏡 Planté", key=f"plante_{i}"):
                            mes_plantes[i]["plante_en_terre"] = True
                            st.session_state.mes_plantes_jardin = mes_plantes
                            st.rerun()

                    if st.button("🗑️", key=f"del_{i}", help="Supprimer"):
                        mes_plantes.pop(i)
                        st.session_state.mes_plantes_jardin = mes_plantes
                        st.rerun()


def onglet_autonomie(mes_plantes: list[dict], recoltes: list[dict]):
    """Onglet objectif autonomie gamifié avec badges."""
    st.subheader("🎯 Objectif Autonomie Alimentaire")

    autonomie = calculer_autonomie(mes_plantes, recoltes)
    stats = calculer_stats_jardin(mes_plantes, recoltes)
    badges_obtenus = obtenir_badges_jardin(stats)
    streak = calculer_streak_jardin(recoltes)

    col1, col2 = st.columns([1, 2])

    with col1:
        afficher_score_jardin_gamifie(autonomie, streak)

    with col2:
        # Stats gamifiées
        m1, m2, m3 = st.columns(3)
        m1.metric("Plantes", stats.get("nb_plantes", 0), help="Plantes cultivées")
        m2.metric("Variétés", stats.get("varietes_uniques", 0), help="Diversité du potager")
        m3.metric("Récoltes", f'{stats.get("production_kg", 0)} kg', help="Production totale")

        # Prévisions
        previsions = generer_previsions_recoltes(mes_plantes)
        if previsions:
            afficher_previsions_recoltes_ui(previsions)

    st.divider()

    # Badges collection
    afficher_badges_jardin(badges_obtenus, stats)

    st.divider()

    # Par catégorie
    st.markdown("### Par catégorie")

    for cat, data in autonomie.get("par_categorie", {}).items():
        col1, col2 = st.columns([1, 3])
        with col1:
            st.write(f"**{cat.capitalize()}**")
        with col2:
            st.progress(
                data["couverture"] / 100,
                text=f"{data['couverture']}% • {data['prevu']}/{data['besoin']} kg",
            )


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
                    recoltes.append(nouvelle_recolte)
                    st.session_state.recoltes_jardin = recoltes
                    st.success(f"✅ Récolte de {quantite}kg enregistrée !")
                    st.rerun()

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
                <span style="font-size: 1.5rem">{plante_data.get('emoji', '🌱')}</span>
                <span><strong>{plante_data.get('nom', recolte.get('plante_id'))}</strong></span>
                <span class="quantite">{recolte.get('quantite_kg')} kg</span>
                <span style="color: #718096">{recolte.get('date')}</span>
            </div>
            """,
                unsafe_allow_html=True,
            )


def onglet_plan():
    """Onglet plan du jardin."""
    st.subheader("🗺️ Plan du Jardin")

    st.info(
        "🚧 Le plan interactif 2D avec drag & drop sera disponible prochainement avec `streamlit-elements`."
    )

    # Plan simplifié pour l'instant
    st.markdown(
        """
    <div class="plan-jardin">
        <div style="color: white; margin-bottom: 1rem;">
            <h4>Zones de culture</h4>
        </div>
        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem;">
            <div class="zone-culture active">
                <span style="color: white;">🥬 Zone A</span>
                <br><small style="color: #aaa;">Légumes feuilles</small>
            </div>
            <div class="zone-culture active">
                <span style="color: white;">🍅 Zone B</span>
                <br><small style="color: #aaa;">Tomates & cucurbitacées</small>
            </div>
            <div class="zone-culture">
                <span style="color: #8d6e63;">📦 Zone C</span>
                <br><small style="color: #6d4c41;">À planter</small>
            </div>
            <div class="zone-culture active">
                <span style="color: white;">🥕 Zone D</span>
                <br><small style="color: #aaa;">Légumes racines</small>
            </div>
            <div class="zone-culture active">
                <span style="color: white;">🌿 Zone E</span>
                <br><small style="color: #aaa;">Aromatiques</small>
            </div>
            <div class="zone-culture">
                <span style="color: #8d6e63;">🌸 Zone F</span>
                <br><small style="color: #6d4c41;">Fleurs mellifères</small>
            </div>
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )


def onglet_graphiques(mes_plantes: list[dict], recoltes: list[dict]):
    """Onglet graphiques Plotly avec visualisations interactives."""
    st.subheader("📈 Graphiques & Analyses")

    if not HAS_PLOTLY:
        st.warning("📦 Plotly non installé. `pip install plotly` pour les graphiques interactifs.")
        return

    if not recoltes and not mes_plantes:
        st.info("📊 Les graphiques apparaîtront avec vos premières plantes et récoltes.")
        return

    # Tab internes
    g1, g2, g3 = st.tabs(["🥕 Récoltes", "🌱 Plantations", "📅 Planning"])

    with g1:
        st.markdown("### Évolution des récoltes")

        if recoltes:
            catalogue = charger_catalogue_plantes()

            # Par mois
            par_mois = {}
            for r in recoltes:
                date_str = r.get("date", "")
                if date_str:
                    try:
                        d = datetime.fromisoformat(date_str).date()
                        mois_key = d.strftime("%Y-%m")
                        par_mois[mois_key] = par_mois.get(mois_key, 0) + r.get("quantite_kg", 0)
                    except Exception:
                        pass

            if par_mois:
                mois_sorted = sorted(par_mois.keys())
                mois_labels = [datetime.strptime(m, "%Y-%m").strftime("%b %Y") for m in mois_sorted]
                quantites = [par_mois[m] for m in mois_sorted]

                fig = go.Figure()
                fig.add_trace(
                    go.Bar(
                        x=mois_labels,
                        y=quantites,
                        marker_color="#27ae60",
                        text=[f"{q:.1f}kg" for q in quantites],
                        textposition="outside",
                    )
                )
                fig.update_layout(
                    title="Récoltes par mois (kg)", template="plotly_dark", height=350
                )
                st.plotly_chart(fig, use_container_width=True)

            # Par plante
            st.markdown("### Répartition par légume")
            par_plante = {}
            for r in recoltes:
                plante_id = r.get("plante_id", "inconnu")
                plante_nom = catalogue.get("plantes", {}).get(plante_id, {}).get("nom", plante_id)
                par_plante[plante_nom] = par_plante.get(plante_nom, 0) + r.get("quantite_kg", 0)

            if par_plante:
                fig = px.pie(
                    values=list(par_plante.values()),
                    names=list(par_plante.keys()),
                    title="Répartition des récoltes",
                    color_discrete_sequence=px.colors.qualitative.Set2,
                    hole=0.4,
                )
                fig.update_layout(template="plotly_dark", height=350)
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Enregistrez vos récoltes pour voir leur évolution ici.")

    with g2:
        st.markdown("### Mes plantations")

        if mes_plantes:
            catalogue = charger_catalogue_plantes()

            # Par catégorie
            par_cat = {}
            for p in mes_plantes:
                plante_id = p.get("plante_id")
                cat = catalogue.get("plantes", {}).get(plante_id, {}).get("categorie", "Autre")
                par_cat[cat] = par_cat.get(cat, 0) + 1

            fig = px.bar(
                x=list(par_cat.keys()),
                y=list(par_cat.values()),
                color=list(par_cat.keys()),
                labels={"x": "Catégorie", "y": "Nombre"},
                title="Répartition des cultures",
            )
            fig.update_layout(template="plotly_dark", height=350, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

            # Surface par plante
            st.markdown("### Surface cultivée")
            surfaces = {}
            for p in mes_plantes:
                plante_id = p.get("plante_id")
                nom = catalogue.get("plantes", {}).get(plante_id, {}).get("nom", plante_id)
                surfaces[nom] = surfaces.get(nom, 0) + p.get("surface_m2", 0)

            if surfaces:
                fig = px.bar(
                    x=list(surfaces.values()),
                    y=list(surfaces.keys()),
                    orientation="h",
                    color=list(surfaces.values()),
                    color_continuous_scale=["#c6f6d5", "#27ae60"],
                    labels={"x": "Surface (m²)", "y": "Plante"},
                )
                fig.update_layout(template="plotly_dark", height=300)
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Ajoutez des plantes pour voir les statistiques.")

    with g3:
        st.markdown("### Planning prévisionnel")

        planning = generer_planning_jardin(mes_plantes, horizon_mois=6)

        if planning:
            afficher_planning_jardin_ui(planning)
        else:
            st.success("✨ Aucune activité prévue dans les 6 prochains mois.")


def onglet_export(mes_plantes: list[dict], recoltes: list[dict]):
    """Onglet export CSV des données jardin."""
    st.subheader("📥 Export des données")

    if not HAS_PANDAS:
        st.warning("📦 Pandas non installé. `pip install pandas` pour l'export.")
        return

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 🌱 Mes Plantations")

        if not mes_plantes:
            st.info("Aucune plantation à exporter.")
        else:
            catalogue = charger_catalogue_plantes()

            df_plantes = pd.DataFrame(
                [
                    {
                        "Plante": catalogue.get("plantes", {})
                        .get(p.get("plante_id"), {})
                        .get("nom", p.get("plante_id")),
                        "Surface (m²)": p.get("surface_m2", 0),
                        "Quantité": p.get("quantite", 0),
                        "Zone": p.get("zone", ""),
                        "Semis fait": "Oui" if p.get("semis_fait") else "Non",
                        "En terre": "Oui" if p.get("plante_en_terre") else "Non",
                        "Date ajout": p.get("date_ajout", ""),
                    }
                    for p in mes_plantes
                ]
            )

            st.dataframe(df_plantes, use_container_width=True, height=250)

            csv = df_plantes.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="📥 Télécharger CSV",
                data=csv,
                file_name=f"jardin_plantations_{date.today().isoformat()}.csv",
                mime="text/csv",
                type="primary",
            )

            st.metric("Total plantes", len(mes_plantes))
            st.metric(
                "Surface totale", f"{sum(p.get('surface_m2', 0) for p in mes_plantes):.1f} m²"
            )

    with col2:
        st.markdown("### 🥕 Historique Récoltes")

        if not recoltes:
            st.info("Aucune récolte à exporter.")
        else:
            catalogue = charger_catalogue_plantes()

            df_recoltes = pd.DataFrame(
                [
                    {
                        "Date": r.get("date", ""),
                        "Plante": catalogue.get("plantes", {})
                        .get(r.get("plante_id"), {})
                        .get("nom", r.get("plante_id")),
                        "Quantité (kg)": r.get("quantite_kg", 0),
                        "Notes": r.get("notes", ""),
                    }
                    for r in recoltes
                ]
            )
            df_recoltes = df_recoltes.sort_values("Date", ascending=False)

            st.dataframe(df_recoltes, use_container_width=True, height=250)

            csv = df_recoltes.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="📥 Télécharger CSV",
                data=csv,
                file_name=f"jardin_recoltes_{date.today().isoformat()}.csv",
                mime="text/csv",
                key="download_recoltes",
            )

            st.metric("Total récoltes", len(recoltes))
            st.metric(
                "Production totale", f"{sum(r.get('quantite_kg', 0) for r in recoltes):.1f} kg"
            )
