"""
Mode Voyage – Checklists, templates et gestion des voyages familiaux.

Onglets:
  1. Voyages (liste + création)
  2. Checklists (préparation par catégorie)
  3. Templates (modèles réutilisables)
"""

from __future__ import annotations

import json
import logging
from datetime import date
from pathlib import Path

import streamlit as st

from src.core.monitoring.rerun_profiler import profiler_rerun
from src.modules._framework import error_boundary
from src.ui.components.atoms import etat_vide
from src.ui.keys import KeyNamespace
from src.ui.state.url import tabs_with_url

logger = logging.getLogger(__name__)
_keys = KeyNamespace("voyage")

_service = None


def _get_service():
    global _service
    if _service is None:
        from src.services.famille.voyage import obtenir_service_voyage

        _service = obtenir_service_voyage()
    return _service


TYPES_VOYAGE = [
    "plage",
    "montagne",
    "city_trip",
    "camping",
    "voyage_avion",
    "road_trip",
    "autre",
]


# ═══════════════════════════════════════════════════════════
# ONGLET 1 – VOYAGES
# ═══════════════════════════════════════════════════════════


def _onglet_voyages():
    """Liste et création de voyages."""
    st.subheader("✈️ Mes Voyages")

    svc = _get_service()

    with st.expander("➕ Planifier un voyage", expanded=False):
        with st.form(_keys("form_voyage")):
            titre = st.text_input("Destination / Titre *", key=_keys("v_titre"))
            col1, col2 = st.columns(2)
            with col1:
                date_depart = st.date_input(
                    "Date de départ", value=date.today(), key=_keys("v_depart")
                )
                type_voyage = st.selectbox("Type", options=TYPES_VOYAGE, key=_keys("v_type"))
            with col2:
                date_retour = st.date_input(
                    "Date de retour", value=date.today(), key=_keys("v_retour")
                )
                budget = st.number_input(
                    "Budget prévu (€)", min_value=0.0, step=50.0, key=_keys("v_budget")
                )

            participants = st.multiselect(
                "Participants",
                options=["Jules", "Anne", "Mathieu", "Grands-parents", "Amis"],
                default=["Jules", "Anne", "Mathieu"],
                key=_keys("v_participants"),
            )
            notes = st.text_area("Notes / hébergement", key=_keys("v_notes"))

            if st.form_submit_button("💾 Créer le voyage", type="primary"):
                if not titre:
                    st.warning("La destination est requise.")
                else:
                    try:
                        svc.create(
                            {
                                "titre": titre,
                                "date_depart": date_depart,
                                "date_retour": date_retour,
                                "type_voyage": type_voyage,
                                "budget_prevu": budget if budget > 0 else None,
                                "notes": notes or None,
                            }
                        )
                        st.success(f"✅ Voyage « {titre} » créé !")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Erreur : {e}")

    st.markdown("#### 🌍 Mes voyages")
    try:
        voyages = svc.list_all()
        if not voyages:
            etat_vide("Aucun voyage planifié", icone="✈️")
            return

        today = date.today()
        a_venir = [v for v in voyages if v.date_depart and v.date_depart >= today]
        passes = [v for v in voyages if v.date_depart and v.date_depart < today]

        if a_venir:
            st.markdown("**🔜 À venir**")
            for v in sorted(a_venir, key=lambda x: x.date_depart):
                jours = (v.date_depart - today).days
                with st.container(border=True):
                    col1, col2, col3 = st.columns([3, 2, 1])
                    with col1:
                        st.markdown(f"✈️ **{v.titre}**")
                        duree = (v.date_retour - v.date_depart).days if v.date_retour else "?"
                        st.caption(
                            f"📅 {v.date_depart.strftime('%d/%m')} → "
                            f"{v.date_retour.strftime('%d/%m') if v.date_retour else '?'} "
                            f"({duree}j)"
                        )
                    with col2:
                        st.metric("Dans", f"{jours}j")
                        if v.budget_prevu:
                            st.caption(f"💰 Budget : {v.budget_prevu}€")
                    with col3:
                        if st.button("🗑️", key=_keys(f"del_v_{v.id}")):
                            svc.delete(v.id)
                            st.rerun()

        if passes:
            with st.expander(f"📜 Voyages passés ({len(passes)})"):
                for v in sorted(passes, key=lambda x: x.date_depart, reverse=True):
                    st.write(f"• **{v.titre}** — {v.date_depart.strftime('%d/%m/%Y')}")

    except Exception as e:
        st.error(f"Erreur : {e}")


# ═══════════════════════════════════════════════════════════
# ONGLET 2 – CHECKLISTS
# ═══════════════════════════════════════════════════════════


def _onglet_checklists():
    """Gestion des checklists de voyage."""
    st.subheader("📋 Checklists de Voyage")

    svc = _get_service()

    try:
        voyages = svc.list_all()
        if not voyages:
            etat_vide("Créez d'abord un voyage", icone="✈️")
            return

        voyage_selectionne = st.selectbox(
            "Voyage",
            options=voyages,
            format_func=lambda v: f"{v.titre} ({v.date_depart})",
            key=_keys("checklist_voyage"),
        )

        if not voyage_selectionne:
            return

        try:
            checklists = svc.lister_checklists(voyage_selectionne.id)
        except Exception:
            checklists = []

        if not checklists:
            st.info("Aucune checklist pour ce voyage.")
            if st.button(
                "📋 Créer depuis un template",
                key=_keys("creer_checklist"),
                type="primary",
            ):
                try:
                    svc.importer_templates_defaut(
                        voyage_selectionne.id,
                        voyage_selectionne.type_voyage or "general",
                    )
                    st.success("✅ Checklist créée depuis le template !")
                    st.rerun()
                except Exception as e:
                    st.error(str(e))
            return

        for checklist in checklists:
            articles = checklist.articles or []
            total = len(articles)
            faits = sum(1 for a in articles if a.get("fait", False))
            pourcentage = faits / total * 100 if total > 0 else 0

            with st.expander(
                f"📋 {checklist.nom} — {faits}/{total} ({pourcentage:.0f}%)",
                expanded=True,
            ):
                st.progress(pourcentage / 100)

                for i, article in enumerate(articles):
                    fait = st.checkbox(
                        article.get("nom", f"Item {i}"),
                        value=article.get("fait", False),
                        key=_keys(f"chk_{checklist.id}_{i}"),
                    )
                    if fait != article.get("fait", False):
                        articles[i]["fait"] = fait
                        try:
                            svc.mettre_a_jour_checklist(checklist.id, {"articles": articles})
                        except Exception as e:
                            logger.debug("Erreur MAJ checklist: %s", e)

    except Exception as e:
        st.error(f"Erreur checklists : {e}")


# ═══════════════════════════════════════════════════════════
# ONGLET 3 – TEMPLATES
# ═══════════════════════════════════════════════════════════


def _onglet_templates():
    """Templates de checklists réutilisables."""
    st.subheader("📝 Templates de Checklist")

    chemin = Path("data/templates_checklist_voyage.json")
    if chemin.exists():
        templates = json.loads(chemin.read_text(encoding="utf-8")).get("templates", [])
    else:
        templates = []

    if not templates:
        etat_vide("Aucun template disponible", icone="📝")
        return

    for template in templates:
        with st.expander(
            f"📝 {template.get('nom', '?')} ({template.get('type', '')})",
            expanded=False,
        ):
            st.caption(template.get("description", ""))

            categories = template.get("categories", [])
            for cat in categories:
                st.markdown(f"**{cat.get('nom', '?')}**")
                articles = cat.get("articles", [])
                for a in articles:
                    priorite = "❗" if a.get("priorite") == "essentiel" else "·"
                    bebe = " 👶" if a.get("bebe_obligatoire") else ""
                    st.caption(f"  {priorite} {a.get('nom', '?')}{bebe}")


# ═══════════════════════════════════════════════════════════
# POINT D'ENTRÉE
# ═══════════════════════════════════════════════════════════


@profiler_rerun("voyage")
def app():
    """Point d'entrée Mode Voyage."""
    st.title("✈️ Mode Voyage")
    st.caption("Organisez vos voyages familiaux avec checklists intelligentes")

    with error_boundary(titre="Erreur mode voyage"):
        TAB_LABELS = ["✈️ Voyages", "📋 Checklists", "📝 Templates"]
        tab_index = tabs_with_url(TAB_LABELS, param="tab")

        tabs = st.tabs(TAB_LABELS)
        with tabs[0]:
            _onglet_voyages()
        with tabs[1]:
            _onglet_checklists()
        with tabs[2]:
            _onglet_templates()
