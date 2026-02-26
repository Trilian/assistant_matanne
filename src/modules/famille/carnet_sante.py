"""
Carnet de santé – Vaccinations, RDV médicaux, courbes de croissance OMS.

Onglets:
  1. Vaccinations (calendrier vaccinal + rappels)
  2. RDV Médicaux (liste, ajout, prochains)
  3. Courbes OMS (poids, taille, périmètre crânien avec percentiles)
"""

from __future__ import annotations

import json
import logging
from datetime import date, timedelta
from pathlib import Path

import streamlit as st

from src.core.monitoring.rerun_profiler import profiler_rerun
from src.modules._framework import error_boundary
from src.ui.components.atoms import etat_vide
from src.ui.keys import KeyNamespace
from src.ui.state.url import tabs_with_url

logger = logging.getLogger(__name__)
_keys = KeyNamespace("carnet_sante")

# ═══════════════════════════════════════════════════════════
# LAZY SERVICE
# ═══════════════════════════════════════════════════════════
_service = None


def _get_service():
    global _service
    if _service is None:
        from src.services.famille.carnet_sante import obtenir_service_carnet_sante

        _service = obtenir_service_carnet_sante()
    return _service


def _charger_calendrier_vaccinal() -> list[dict]:
    """Charge le référentiel vaccinal français."""
    chemin = Path("data/calendrier_vaccinal_fr.json")
    if chemin.exists():
        return json.loads(chemin.read_text(encoding="utf-8")).get("vaccins", [])
    return []


def _charger_normes_oms() -> dict:
    """Charge les normes OMS 0-36 mois."""
    chemin = Path("data/normes_oms.json")
    if chemin.exists():
        return json.loads(chemin.read_text(encoding="utf-8"))
    return {}


# ═══════════════════════════════════════════════════════════
# ONGLET 1 – VACCINATIONS
# ═══════════════════════════════════════════════════════════


def _onglet_vaccinations():
    """Gestion des vaccinations avec calendrier vaccinal intégré."""
    st.subheader("💉 Vaccinations")

    svc = _get_service()

    # --- Formulaire d'ajout ---
    with st.expander("➕ Enregistrer une vaccination", expanded=False):
        calendrier = _charger_calendrier_vaccinal()
        noms_vaccins = [v["nom"] for v in calendrier] if calendrier else []

        with st.form(_keys("form_vaccin")):
            col1, col2 = st.columns(2)
            with col1:
                nom = st.selectbox("Vaccin", options=noms_vaccins, key=_keys("vaccin_nom"))
                date_admin = st.date_input(
                    "Date d'administration", value=date.today(), key=_keys("vaccin_date")
                )
            with col2:
                dose = st.number_input(
                    "Dose n°", min_value=1, max_value=5, value=1, key=_keys("vaccin_dose")
                )
                medecin = st.text_input("Médecin", key=_keys("vaccin_medecin"))
            lot = st.text_input("N° de lot (optionnel)", key=_keys("vaccin_lot"))
            notes = st.text_area("Notes", key=_keys("vaccin_notes"))

            if st.form_submit_button("💾 Enregistrer", type="primary"):
                try:
                    svc.ajouter_vaccin(
                        {
                            "nom_vaccin": nom,
                            "date_administration": date_admin,
                            "dose_numero": dose,
                            "medecin": medecin,
                            "numero_lot": lot or None,
                            "notes": notes or None,
                        }
                    )
                    st.success(f"✅ Vaccination {nom} (dose {dose}) enregistrée !")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Erreur : {e}")

    # --- Historique ---
    st.markdown("#### 📋 Historique des vaccinations")
    try:
        vaccins = svc.lister_vaccins()
        if not vaccins:
            etat_vide("Aucune vaccination enregistrée", icone="💉")
        else:
            for v in vaccins:
                col1, col2, col3 = st.columns([3, 2, 1])
                with col1:
                    st.markdown(f"**{v.nom_vaccin}** – Dose {v.dose_numero}")
                with col2:
                    st.caption(f"📅 {v.date_administration} • Dr {v.medecin or '?'}")
                with col3:
                    if v.rappel_prevu:
                        jours = (v.rappel_prevu - date.today()).days
                        if jours <= 30:
                            st.warning(f"⏰ Rappel dans {jours}j")
                        else:
                            st.info(f"📅 {v.rappel_prevu}")
    except Exception as e:
        st.error(f"Erreur chargement vaccins : {e}")

    # --- Calendrier vaccinal de référence ---
    with st.expander("📖 Calendrier vaccinal français", expanded=False):
        calendrier = _charger_calendrier_vaccinal()
        if calendrier:
            for v in calendrier:
                obligatoire = "🔴 Obligatoire" if v.get("obligatoire") else "🔵 Recommandé"
                st.markdown(f"**{v['nom']}** — {obligatoire}")
                st.caption(f"Âges : {', '.join(v.get('ages', []))} • Doses : {v.get('doses', '?')}")
        else:
            st.info("Calendrier vaccinal non trouvé.")


# ═══════════════════════════════════════════════════════════
# ONGLET 2 – RDV MÉDICAUX
# ═══════════════════════════════════════════════════════════


def _onglet_rdv():
    """Gestion des rendez-vous médicaux."""
    st.subheader("🏥 Rendez-vous Médicaux")

    svc = _get_service()

    # --- Formulaire d'ajout ---
    with st.expander("➕ Nouveau RDV", expanded=False):
        specialites = [
            "Pédiatre",
            "Généraliste",
            "Dentiste",
            "Ophtalmologue",
            "ORL",
            "Dermatologue",
            "Allergologue",
            "Kinésithérapeute",
            "Psychologue",
            "Autre",
        ]
        with st.form(_keys("form_rdv")):
            col1, col2 = st.columns(2)
            with col1:
                specialite = st.selectbox("Spécialité", options=specialites, key=_keys("rdv_spe"))
                date_rdv = st.date_input("Date", value=date.today(), key=_keys("rdv_date"))
                heure = st.time_input("Heure", key=_keys("rdv_heure"))
            with col2:
                medecin = st.text_input("Médecin", key=_keys("rdv_medecin"))
                lieu = st.text_input("Lieu", key=_keys("rdv_lieu"))
                membre = st.selectbox("Pour", ["Jules", "Anne", "Mathieu"], key=_keys("rdv_membre"))

            motif = st.text_area("Motif", key=_keys("rdv_motif"))

            if st.form_submit_button("💾 Enregistrer", type="primary"):
                try:
                    svc.ajouter_rdv(
                        {
                            "specialite": specialite,
                            "date_rdv": date_rdv,
                            "heure_rdv": str(heure),
                            "medecin": medecin,
                            "lieu": lieu or None,
                            "membre_famille": membre,
                            "motif": motif or None,
                        }
                    )
                    st.success(f"✅ RDV {specialite} le {date_rdv} enregistré !")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Erreur : {e}")

    # --- Prochains RDV ---
    st.markdown("#### 📅 Prochains rendez-vous")
    try:
        rdvs = svc.lister_prochains_rdv()
        if not rdvs:
            etat_vide("Aucun RDV à venir", icone="🏥")
        else:
            for rdv in rdvs:
                jours = (rdv.date_rdv - date.today()).days
                urgence = "🔴" if jours <= 2 else "🟡" if jours <= 7 else "🟢"
                with st.container(border=True):
                    col1, col2, col3 = st.columns([3, 2, 1])
                    with col1:
                        st.markdown(f"{urgence} **{rdv.specialite}** — Dr {rdv.medecin or '?'}")
                    with col2:
                        st.caption(f"📅 {rdv.date_rdv} • {rdv.heure_rdv or ''}")
                        st.caption(f"👤 {rdv.membre_famille}")
                    with col3:
                        st.metric("Dans", f"{jours}j")
    except Exception as e:
        st.error(f"Erreur chargement RDV : {e}")


# ═══════════════════════════════════════════════════════════
# ONGLET 3 – COURBES OMS
# ═══════════════════════════════════════════════════════════


def _onglet_courbes():
    """Courbes de croissance OMS avec percentiles."""
    st.subheader("📈 Courbes de Croissance OMS")

    svc = _get_service()

    # --- Formulaire mesure ---
    with st.expander("➕ Nouvelle mesure", expanded=False):
        with st.form(_keys("form_mesure")):
            col1, col2 = st.columns(2)
            with col1:
                date_mesure = st.date_input("Date", value=date.today(), key=_keys("mesure_date"))
                age_mois = st.number_input(
                    "Âge (mois)", min_value=0, max_value=36, key=_keys("mesure_age")
                )
            with col2:
                poids = st.number_input(
                    "Poids (kg)", min_value=0.0, max_value=30.0, step=0.1, key=_keys("mesure_poids")
                )
                taille = st.number_input(
                    "Taille (cm)",
                    min_value=0.0,
                    max_value=120.0,
                    step=0.5,
                    key=_keys("mesure_taille"),
                )
            perimetre = st.number_input(
                "Périmètre crânien (cm)",
                min_value=0.0,
                max_value=60.0,
                step=0.1,
                key=_keys("mesure_pc"),
            )

            if st.form_submit_button("💾 Enregistrer", type="primary"):
                try:
                    svc.ajouter_mesure(
                        {
                            "date_mesure": date_mesure,
                            "age_mois": age_mois,
                            "poids_kg": poids if poids > 0 else None,
                            "taille_cm": taille if taille > 0 else None,
                            "perimetre_cranien_cm": perimetre if perimetre > 0 else None,
                        }
                    )
                    st.success("✅ Mesure enregistrée !")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Erreur : {e}")

    # --- Graphiques ---
    try:
        mesures = svc.lister_mesures()
        normes = _charger_normes_oms()

        if not mesures:
            etat_vide("Aucune mesure enregistrée. Ajoutez la première !", icone="📏")
            return

        import plotly.graph_objects as go

        sexe = "garcons"  # TODO: paramétrable

        for indicateur, label, unite in [
            ("poids", "Poids", "kg"),
            ("taille", "Taille", "cm"),
            ("perimetre_cranien", "Périmètre crânien", "cm"),
        ]:
            ages = [m.age_mois for m in mesures]
            valeurs = [
                getattr(
                    m, f"{indicateur}_kg" if indicateur == "poids" else f"{indicateur}_cm", None
                )
                for m in mesures
            ]
            valeurs_filtrees = [
                (a, v) for a, v in zip(ages, valeurs, strict=False) if v is not None
            ]

            if not valeurs_filtrees:
                continue

            fig = go.Figure()

            # Données enfant
            ages_f, vals_f = zip(*valeurs_filtrees, strict=False)
            fig.add_trace(
                go.Scatter(
                    x=list(ages_f),
                    y=list(vals_f),
                    mode="lines+markers",
                    name="Jules",
                    line=dict(color="#1f77b4", width=3),
                    marker=dict(size=8),
                )
            )

            # Percentiles OMS
            normes_indicateur = normes.get(sexe, {}).get(indicateur, [])
            if normes_indicateur:
                ages_oms = [n["age_mois"] for n in normes_indicateur]
                for pct, couleur, dash in [
                    ("p3", "#ff9999", "dot"),
                    ("p50", "#66bb6a", "solid"),
                    ("p97", "#ff9999", "dot"),
                ]:
                    vals_oms = [n.get(pct) for n in normes_indicateur]
                    if any(v is not None for v in vals_oms):
                        fig.add_trace(
                            go.Scatter(
                                x=ages_oms,
                                y=vals_oms,
                                mode="lines",
                                name=f"OMS {pct}",
                                line=dict(color=couleur, dash=dash, width=1),
                                opacity=0.6,
                            )
                        )

            fig.update_layout(
                title=f"📊 {label} – Courbe OMS",
                xaxis_title="Âge (mois)",
                yaxis_title=f"{label} ({unite})",
                height=400,
                showlegend=True,
            )
            st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"Erreur courbes OMS : {e}")


# ═══════════════════════════════════════════════════════════
# POINT D'ENTRÉE
# ═══════════════════════════════════════════════════════════


@profiler_rerun("carnet_sante")
def app():
    """Point d'entrée Carnet de santé."""
    st.title("🩺 Carnet de Santé")
    st.caption("Vaccinations, rendez-vous médicaux et courbes de croissance OMS")

    with error_boundary(titre="Erreur carnet de santé"):
        TAB_LABELS = ["💉 Vaccinations", "🏥 RDV Médicaux", "📈 Courbes OMS"]
        tab_index = tabs_with_url(TAB_LABELS, param="tab")

        tabs = st.tabs(TAB_LABELS)
        with tabs[0]:
            _onglet_vaccinations()
        with tabs[1]:
            _onglet_rdv()
        with tabs[2]:
            _onglet_courbes()
