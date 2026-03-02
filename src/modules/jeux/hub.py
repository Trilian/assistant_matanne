"""
Hub Jeux - Accès centralisé aux modules de jeux et paris.

Regroupe: Paris Sportifs, Loto, Bilan Global et modules secondaires.
"""

from __future__ import annotations

import streamlit as st

from src.core.monitoring.rerun_profiler import profiler_rerun
from src.modules._framework import error_boundary
from src.ui.keys import KeyNamespace

_keys = KeyNamespace("jeux_hub")


def _naviguer(cle: str) -> None:
    from src.core.state import GestionnaireEtat

    GestionnaireEtat.naviguer_vers(cle)


@profiler_rerun("jeux_hub")
def app():
    """Point d'entrée Hub Jeux."""
    with error_boundary("jeux_hub"):
        st.title("🎮 Jeux & Paris")
        st.caption("Paris sportifs, Loto et suivi de vos résultats")

        st.divider()

        # ── Modules principaux ─────────────────────────────
        c1, c2, c3 = st.columns(3)

        with c1:
            st.markdown("### ⚽ Paris Sportifs")
            st.caption("Suivi des championnats, prédictions IA et paris virtuels")
            if st.button(
                "Ouvrir Paris Sportifs",
                key=_keys("goto_paris"),
                use_container_width=True,
                type="primary",
            ):
                _naviguer("jeux.paris")
                st.rerun()

        with c2:
            st.markdown("### 🎰 Loto")
            st.caption("Analyse statistique, générateur de grilles et simulations")
            if st.button(
                "Ouvrir Loto",
                key=_keys("goto_loto"),
                use_container_width=True,
                type="primary",
            ):
                _naviguer("jeux.loto")
                st.rerun()

        with c3:
            st.markdown("### 📊 Bilan Global")
            st.caption("Dashboard consolidé gains/pertes tous jeux confondus")
            if st.button(
                "Ouvrir Bilan",
                key=_keys("goto_bilan"),
                use_container_width=True,
                type="primary",
            ):
                _naviguer("jeux.bilan")
                st.rerun()

        st.divider()

        # ── Modules secondaires ──────────────────────────────
        st.markdown("#### Outils complémentaires")

        cols = st.columns(4)
        secondary = [
            ("⭐ Euromillions", "jeux.euromillions"),
            ("📈 Comparatif ROI", "jeux.comparatif_roi"),
            ("🔔 Alertes", "jeux.alertes"),
            ("🧠 Biais Cognitifs", "jeux.biais"),
            ("📅 Calendrier", "jeux.calendrier"),
            ("🎓 Module Éducatif", "jeux.educatif"),
        ]

        for i, (label, cle) in enumerate(secondary):
            with cols[i % 4]:
                if st.button(label, key=_keys(f"goto_{cle}"), use_container_width=True):
                    _naviguer(cle)
                    st.rerun()

        # ── Avertissement responsable ─────────────────────────
        st.divider()
        st.info(
            "⚠️ **Jeu responsable** — Les jeux d'argent comportent des risques. "
            "Jouez uniquement avec ce que vous pouvez vous permettre de perdre. "
            "[Aide : joueurs-info-service.fr](https://www.joueurs-info-service.fr)"
        )
