"""
Anniversaires – Dates importantes, rappels, idées cadeaux.

Onglets:
  1. Prochains anniversaires (timeline)
  2. Gestion des dates
  3. Idées cadeaux
"""

from __future__ import annotations

import logging

import streamlit as st

from src.core.monitoring.rerun_profiler import profiler_rerun
from src.modules._framework import error_boundary
from src.ui.components.atoms import etat_vide
from src.ui.keys import KeyNamespace
from src.ui.state.url import tabs_with_url

logger = logging.getLogger(__name__)
_keys = KeyNamespace("anniversaires")

_service = None


def _get_service():
    global _service
    if _service is None:
        from src.services.famille.anniversaires import obtenir_service_anniversaires

        _service = obtenir_service_anniversaires()
    return _service


CATEGORIES = [
    "famille_proche",
    "famille_elargie",
    "amis",
    "collegues",
    "enfants_amis",
    "autre",
]


# ═══════════════════════════════════════════════════════════
# ONGLET 1 – PROCHAINS
# ═══════════════════════════════════════════════════════════


def _onglet_prochains():
    """Timeline des prochains anniversaires."""
    st.subheader("🎂 Prochains Anniversaires")

    svc = _get_service()

    try:
        prochains = svc.lister_prochains(limite=15)
        if not prochains:
            etat_vide("Aucun anniversaire enregistré", icone="🎂")
            return

        for anniv in prochains:
            jours_restants = anniv.jours_restants
            prochain = anniv.prochain_anniversaire
            age = anniv.age

            # Code couleur urgence
            if jours_restants <= 7:
                urgence = "🔴"
            elif jours_restants <= 30:
                urgence = "🟡"
            else:
                urgence = "🟢"

            with st.container(border=True):
                col1, col2, col3 = st.columns([3, 2, 1])
                with col1:
                    st.markdown(f"{urgence} **{anniv.prenom} {anniv.nom or ''}**")
                    st.caption(
                        f"📅 {anniv.date_naissance.strftime('%d/%m/%Y')} • {anniv.categorie or ''}"
                    )
                with col2:
                    if age is not None:
                        st.metric("Prochain âge", f"{age + 1} ans")
                    if prochain:
                        st.caption(f"📆 {prochain.strftime('%d/%m/%Y')}")
                with col3:
                    st.metric("Dans", f"{jours_restants}j")
                    if anniv.idees_cadeaux:
                        st.caption(f"🎁 {len(anniv.idees_cadeaux)} idée(s)")

    except Exception as e:
        st.error(f"Erreur : {e}")


# ═══════════════════════════════════════════════════════════
# ONGLET 2 – GESTION
# ═══════════════════════════════════════════════════════════


def _onglet_gestion():
    """CRUD des dates d'anniversaire."""
    st.subheader("✏️ Gestion des dates")

    svc = _get_service()

    with st.expander("➕ Ajouter un anniversaire", expanded=False):
        with st.form(_keys("form_anniv")):
            col1, col2 = st.columns(2)
            with col1:
                prenom = st.text_input("Prénom *", key=_keys("anniv_prenom"))
                nom = st.text_input("Nom", key=_keys("anniv_nom"))
                date_naissance = st.date_input("Date de naissance *", key=_keys("anniv_date"))
            with col2:
                categorie = st.selectbox("Catégorie", options=CATEGORIES, key=_keys("anniv_cat"))
                rappel_jours = st.number_input(
                    "Rappel (jours avant)",
                    min_value=0,
                    max_value=60,
                    value=7,
                    key=_keys("anniv_rappel"),
                )

            notes = st.text_area("Notes", key=_keys("anniv_notes"))

            if st.form_submit_button("💾 Ajouter", type="primary"):
                if not prenom:
                    st.warning("Le prénom est requis.")
                else:
                    try:
                        svc.create(
                            {
                                "prenom": prenom,
                                "nom": nom or None,
                                "date_naissance": date_naissance,
                                "categorie": categorie,
                                "rappel_jours_avant": rappel_jours,
                                "notes": notes or None,
                            }
                        )
                        st.success(f"✅ Anniversaire de {prenom} ajouté !")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Erreur : {e}")

    # Liste complète
    st.markdown("#### 📋 Tous les anniversaires")
    try:
        tous = svc.list_all()
        if not tous:
            etat_vide("Aucun anniversaire enregistré", icone="🎂")
        else:
            # Grouper par catégorie
            par_categorie: dict[str, list[object]] = {}
            for a in tous:
                cat = a.categorie or "autre"
                par_categorie.setdefault(cat, []).append(a)

            for cat, annivs in sorted(par_categorie.items()):
                st.markdown(f"**{cat.replace('_', ' ').title()}** ({len(annivs)})")
                for a in sorted(
                    annivs, key=lambda x: x.date_naissance.month * 100 + x.date_naissance.day
                ):
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        st.write(
                            f"• {a.prenom} {a.nom or ''} — {a.date_naissance.strftime('%d/%m/%Y')}"
                        )
                    with col2:
                        if st.button("🗑️", key=_keys(f"del_{a.id}")):
                            try:
                                svc.delete(a.id)
                                st.rerun()
                            except Exception as e:
                                st.error(str(e))

    except Exception as e:
        st.error(f"Erreur : {e}")


# ═══════════════════════════════════════════════════════════
# ONGLET 3 – IDÉES CADEAUX
# ═══════════════════════════════════════════════════════════


def _onglet_cadeaux():
    """Gestion des idées cadeaux par personne."""
    st.subheader("🎁 Idées Cadeaux")

    svc = _get_service()

    try:
        prochains = svc.lister_prochains(limite=10)
        if not prochains:
            etat_vide("Ajoutez d'abord des anniversaires", icone="🎁")
            return

        for anniv in prochains:
            with st.expander(f"🎂 {anniv.prenom} {anniv.nom or ''} — dans {anniv.jours_restants}j"):
                cadeaux = anniv.idees_cadeaux or []

                if cadeaux:
                    for i, cadeau in enumerate(cadeaux):
                        col1, col2 = st.columns([4, 1])
                        with col1:
                            achete = cadeau.get("achete", False)
                            emoji = "✅" if achete else "💡"
                            st.write(
                                f"{emoji} {cadeau.get('idee', '?')} — {cadeau.get('budget', '?')}€"
                            )
                        with col2:
                            if not achete and st.button("✅", key=_keys(f"buy_{anniv.id}_{i}")):
                                cadeaux[i]["achete"] = True
                                try:
                                    svc.update(anniv.id, {"idees_cadeaux": cadeaux})
                                    st.rerun()
                                except Exception as e:
                                    st.error(str(e))
                else:
                    st.caption("Aucune idée pour l'instant")

                # Ajout rapide
                with st.form(_keys(f"form_cadeau_{anniv.id}")):
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        idee = st.text_input("Idée cadeau", key=_keys(f"idee_{anniv.id}"))
                    with col2:
                        budget = st.number_input(
                            "Budget €", min_value=0, value=30, key=_keys(f"budget_{anniv.id}")
                        )

                    if st.form_submit_button("➕ Ajouter"):
                        if idee:
                            new_cadeaux = list(cadeaux) + [
                                {"idee": idee, "budget": budget, "achete": False}
                            ]
                            try:
                                svc.update(anniv.id, {"idees_cadeaux": new_cadeaux})
                                st.success(f"💡 Idée ajoutée pour {anniv.prenom} !")
                                st.rerun()
                            except Exception as e:
                                st.error(str(e))

    except Exception as e:
        st.error(f"Erreur : {e}")


# ═══════════════════════════════════════════════════════════
# POINT D'ENTRÉE
# ═══════════════════════════════════════════════════════════


@profiler_rerun("anniversaires")
def app():
    """Point d'entrée Anniversaires."""
    st.title("🎂 Anniversaires & Dates Importantes")
    st.caption("Ne manquez plus jamais un anniversaire !")

    with error_boundary(titre="Erreur anniversaires"):
        TAB_LABELS = ["🎂 Prochains", "✏️ Gestion", "🎁 Cadeaux"]
        _tab_index = tabs_with_url(TAB_LABELS, param="tab")

        tabs = st.tabs(TAB_LABELS)
        with tabs[0]:
            _onglet_prochains()
        with tabs[1]:
            _onglet_gestion()
        with tabs[2]:
            _onglet_cadeaux()
