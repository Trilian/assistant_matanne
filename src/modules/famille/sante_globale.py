"""
Santé Globale – Dashboard santé de toute la famille.

Onglets:
  1. Vue d'ensemble (métriques clés)
  2. Suivi individuel
  3. Alertes & rappels
"""

from __future__ import annotations

import logging
from datetime import date, timedelta

import streamlit as st

from src.core.monitoring.rerun_profiler import profiler_rerun
from src.modules._framework import error_boundary
from src.ui.components.atoms import etat_vide
from src.ui.keys import KeyNamespace
from src.ui.state.url import tabs_with_url

logger = logging.getLogger(__name__)
_keys = KeyNamespace("sante_globale")

_service_carnet = None
_service_sante = None


def _get_service_carnet():
    global _service_carnet
    if _service_carnet is None:
        from src.services.famille.carnet_sante import obtenir_service_carnet_sante

        _service_carnet = obtenir_service_carnet_sante()
    return _service_carnet


def _get_service_sante():
    global _service_sante
    if _service_sante is None:
        from src.services.famille.sante import obtenir_service_sante

        _service_sante = obtenir_service_sante()
    return _service_sante


# ═══════════════════════════════════════════════════════════
# ONGLET 1 – VUE D'ENSEMBLE
# ═══════════════════════════════════════════════════════════


def _onglet_vue_ensemble():
    """Dashboard santé famille."""
    st.subheader("📊 Vue d'ensemble Santé Famille")

    svc_carnet = _get_service_carnet()

    try:
        resume = svc_carnet.obtenir_resume_sante()
    except Exception as e:
        logger.debug("Erreur résumé santé: %s", e)
        resume = {}

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("💉 Vaccins à jour", resume.get("vaccins_a_jour", 0))
    with col2:
        st.metric("🏥 Prochains RDV", resume.get("prochains_rdv", 0))
    with col3:
        rappels = resume.get("rappels_vaccins", 0)
        st.metric("⚠️ Rappels vaccins" if rappels > 0 else "✅ Rappels vaccins", rappels)
    with col4:
        st.metric("📏 Mesures OMS", resume.get("nb_mesures", 0))

    st.markdown("---")

    # Dernière mesure Jules
    st.markdown("#### 👶 Dernière mesure de Jules")
    try:
        derniere = resume.get("derniere_mesure")
        if derniere:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Poids", f"{derniere.get('poids_kg', '?')} kg")
            with col2:
                st.metric("Taille", f"{derniere.get('taille_cm', '?')} cm")
            with col3:
                st.metric("PC", f"{derniere.get('perimetre_cranien_cm', '?')} cm")
            st.caption(f"📅 Mesurée à {derniere.get('age_mois', '?')} mois")
        else:
            etat_vide("Aucune mesure enregistrée", icone="📏")
    except Exception as e:
        logger.debug("Erreur dernière mesure: %s", e)

    # Prochains RDV
    st.markdown("---")
    st.markdown("#### 📅 Prochains rendez-vous")
    try:
        rdvs = svc_carnet.lister_prochains_rdv(limite=5)
        if rdvs:
            for rdv in rdvs:
                jours = (rdv.date_rdv - date.today()).days
                urgence = "🔴" if jours <= 2 else "🟡" if jours <= 7 else "🟢"
                st.write(
                    f"{urgence} **{rdv.specialite}** — Dr {rdv.medecin or '?'} "
                    f"• {rdv.date_rdv.strftime('%d/%m')} ({jours}j) • {rdv.membre_famille}"
                )
        else:
            st.caption("Aucun RDV programmé")
    except Exception as e:
        logger.debug("Erreur RDV: %s", e)


# ═══════════════════════════════════════════════════════════
# ONGLET 2 – SUIVI INDIVIDUEL
# ═══════════════════════════════════════════════════════════


def _onglet_individuel():
    """Suivi santé par membre de la famille."""
    st.subheader("👤 Suivi Individuel")

    membre = st.selectbox(
        "Membre de la famille",
        ["Jules", "Anne", "Mathieu"],
        key=_keys("membre_suivi"),
    )

    st.markdown(f"#### Santé de {membre}")

    svc_sante = _get_service_sante()

    try:
        entrees = svc_sante.lister_entrees(membre.lower(), limite=10)
        if entrees:
            for e in entrees:
                with st.container(border=True):
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.write(f"📋 {e.type_entree} — {e.description or ''}")
                    with col2:
                        st.caption(f"📅 {e.date_entree}")
        else:
            etat_vide(f"Aucune donnée santé pour {membre}", icone="📋")
    except Exception as e:
        logger.debug("Erreur suivi individuel: %s", e)
        etat_vide(f"Module santé non configuré pour {membre}", icone="📋")

    with st.expander(f"➕ Ajouter une entrée pour {membre}"):
        with st.form(_keys(f"form_sante_{membre}")):
            type_entree = st.selectbox(
                "Type",
                ["Symptôme", "Médicament", "Allergie", "Note", "Poids", "Température"],
                key=_keys(f"type_sante_{membre}"),
            )
            description = st.text_area("Description", key=_keys(f"desc_sante_{membre}"))

            if st.form_submit_button("💾 Enregistrer"):
                try:
                    svc_sante.ajouter_entree(
                        {
                            "membre": membre.lower(),
                            "type_entree": type_entree,
                            "description": description,
                            "date_entree": date.today(),
                        }
                    )
                    st.success("✅ Entrée enregistrée !")
                    st.rerun()
                except Exception as e:
                    st.error(str(e))


# ═══════════════════════════════════════════════════════════
# ONGLET 3 – ALERTES & RAPPELS
# ═══════════════════════════════════════════════════════════


def _onglet_alertes():
    """Alertes et rappels santé."""
    st.subheader("🔔 Alertes & Rappels Santé")

    svc = _get_service_carnet()
    today = date.today()
    alertes: list[tuple[str, str, str]] = []

    # Rappels vaccins
    try:
        vaccins = svc.lister_vaccins()
        for v in vaccins:
            if v.rappel_prevu and v.rappel_prevu <= today + timedelta(days=30):
                jours = (v.rappel_prevu - today).days
                if jours < 0:
                    alertes.append(
                        (
                            "🔴",
                            f"Rappel vaccin **{v.nom_vaccin}** en RETARD ({abs(jours)}j)",
                            "urgent",
                        )
                    )
                elif jours <= 7:
                    alertes.append(
                        (
                            "🟡",
                            f"Rappel vaccin **{v.nom_vaccin}** dans {jours}j",
                            "attention",
                        )
                    )
                else:
                    alertes.append(
                        (
                            "🟢",
                            f"Rappel vaccin **{v.nom_vaccin}** dans {jours}j",
                            "info",
                        )
                    )
    except Exception as e:
        logger.debug("Erreur alertes vaccins: %s", e)

    # RDV prochains
    try:
        rdvs = svc.lister_prochains_rdv(limite=10)
        for rdv in rdvs:
            jours = (rdv.date_rdv - today).days
            if jours <= 2:
                alertes.append(
                    (
                        "🔴",
                        f"RDV **{rdv.specialite}** dans {jours}j — {rdv.membre_famille}",
                        "urgent",
                    )
                )
            elif jours <= 7:
                alertes.append(
                    (
                        "🟡",
                        f"RDV **{rdv.specialite}** dans {jours}j — {rdv.membre_famille}",
                        "attention",
                    )
                )
    except Exception as e:
        logger.debug("Erreur alertes RDV: %s", e)

    if not alertes:
        st.success("✅ Aucune alerte santé ! Tout est en ordre.")
        return

    ordre = {"urgent": 0, "attention": 1, "info": 2}
    alertes.sort(key=lambda a: ordre.get(a[2], 3))

    for emoji, message, niveau in alertes:
        if niveau == "urgent":
            st.error(f"{emoji} {message}")
        elif niveau == "attention":
            st.warning(f"{emoji} {message}")
        else:
            st.info(f"{emoji} {message}")


# ═══════════════════════════════════════════════════════════
# POINT D'ENTRÉE
# ═══════════════════════════════════════════════════════════


@profiler_rerun("sante_globale")
def app():
    """Point d'entrée Santé Globale."""
    st.title("🏥 Santé Globale Famille")
    st.caption("Vue complète de la santé familiale")

    with error_boundary(titre="Erreur santé globale"):
        TAB_LABELS = ["📊 Vue d'ensemble", "👤 Individuel", "🔔 Alertes"]
        tab_index = tabs_with_url(TAB_LABELS, param="tab")

        tabs = st.tabs(TAB_LABELS)
        with tabs[0]:
            _onglet_vue_ensemble()
        with tabs[1]:
            _onglet_individuel()
        with tabs[2]:
            _onglet_alertes()
