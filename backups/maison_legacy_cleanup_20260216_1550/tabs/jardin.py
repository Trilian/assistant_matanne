"""Tab Jardin - Vue interactive des zones et plantes."""

import streamlit as st

from src.core.database import obtenir_contexte_db


def tab_jardin():
    """Affiche le plan du jardin avec zones."""
    try:
        from src.core.models import PlanteJardin, ZoneJardin
        from src.ui.maison.plan_jardin import (
            COULEURS_ZONES,
            PlanJardinInteractif,
            PlanteData,
            ZoneJardinData,
        )

        with obtenir_contexte_db() as db:
            zones_db = db.query(ZoneJardin).all()

            if not zones_db:
                _afficher_fallback_jardin()
                return

            zones_data = []
            plantes_par_zone: dict[int, list] = {}

            for zone in zones_db:
                plantes = db.query(PlanteJardin).filter(PlanteJardin.zone_id == zone.id).all()

                zone_data = ZoneJardinData(
                    id=zone.id,
                    nom=zone.nom,
                    type_zone=zone.type_zone,
                    superficie_m2=float(zone.superficie_m2) if zone.superficie_m2 else None,
                    exposition=zone.exposition,
                    type_sol=zone.type_sol,
                    arrosage_auto=zone.arrosage_auto or False,
                    nb_plantes=len(plantes),
                    couleur=COULEURS_ZONES.get(zone.type_zone, "#22c55e"),
                )
                zones_data.append(zone_data)

                plantes_data = []
                for plante in plantes:
                    plantes_data.append(
                        PlanteData(
                            id=plante.id,
                            nom=plante.nom,
                            variete=plante.variete,
                            etat=plante.etat or "bon",
                            date_plantation=plante.date_plantation,
                        )
                    )
                plantes_par_zone[zone.id] = plantes_data

        plan = PlanJardinInteractif(zones=zones_data, plantes_par_zone=plantes_par_zone)
        plan.render()

    except ImportError:
        st.warning("Module Plan Jardin non disponible")
        _afficher_fallback_jardin()
    except Exception as e:
        st.error(f"Erreur chargement jardin: {e}")
        _afficher_fallback_jardin()


def _afficher_fallback_jardin():
    """Affichage simplifié du jardin."""
    try:
        from src.core.models import PlanteJardin, ZoneJardin

        with obtenir_contexte_db() as db:
            zones = db.query(ZoneJardin).all()

        if not zones:
            st.info("Aucune zone jardin créée.")
            return

        for zone in zones:
            with st.expander(f"🌱 {zone.nom} ({zone.type_zone})", expanded=True):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Surface", f"{zone.superficie_m2 or 0}m²")
                with col2:
                    st.metric("Exposition", zone.exposition or "-")
                with col3:
                    arrosage = "✅ Auto" if zone.arrosage_auto else "🖐️ Manuel"
                    st.metric("Arrosage", arrosage)

                with obtenir_contexte_db() as db:
                    plantes = db.query(PlanteJardin).filter(PlanteJardin.zone_id == zone.id).all()

                if plantes:
                    st.markdown("**Plantes :**")
                    for plante in plantes:
                        etat_icon = {
                            "excellent": "🟢",
                            "bon": "🟡",
                            "attention": "🟠",
                            "probleme": "🔴",
                        }.get(plante.etat, "⚪")
                        st.write(
                            f"- {etat_icon} {plante.nom} ({plante.variete or 'variété non spécifiée'})"
                        )

    except Exception as e:
        st.error(f"Erreur chargement jardin: {e}")
