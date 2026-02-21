"""
Timer de cuisine avec compte à rebours réel.

Remplace le timer statique de ``kitchen.py`` par un vrai compte à rebours
basé sur ``datetime`` et le cycle de rerun de Streamlit.

Usage::

    from src.ui.tablet.timer import TimerCuisine

    timer = TimerCuisine()
    timer.afficher()
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Any

import streamlit as st

logger = logging.getLogger(__name__)


class TimerCuisine:
    """Timer de cuisine persistant via session_state."""

    _STATE_KEY = "cuisine_timer"
    _PRESETS: dict[str, int] = {
        "1 min": 60,
        "3 min": 180,
        "5 min": 300,
        "10 min": 600,
        "15 min": 900,
        "20 min": 1200,
        "30 min": 1800,
    }

    def __init__(self) -> None:
        """Initialise l'état du timer dans session_state."""
        if self._STATE_KEY not in st.session_state:
            st.session_state[self._STATE_KEY] = {
                "actif": False,
                "fin": None,
                "duree_totale": 0,
                "label": "",
                "termine": False,
            }

    @property
    def _state(self) -> dict[str, Any]:
        """Accès à l'état du timer."""
        return st.session_state[self._STATE_KEY]

    @property
    def est_actif(self) -> bool:
        """Vérifie si le timer est en cours."""
        return bool(self._state["actif"])

    @property
    def est_termine(self) -> bool:
        """Vérifie si le timer est terminé."""
        if not self._state["actif"] or self._state["fin"] is None:
            return self._state.get("termine", False)
        return datetime.now() >= self._state["fin"]

    @property
    def temps_restant(self) -> timedelta:
        """Calcule le temps restant."""
        if not self._state["actif"] or self._state["fin"] is None:
            return timedelta(0)
        reste = self._state["fin"] - datetime.now()
        return max(reste, timedelta(0))

    @property
    def progression(self) -> float:
        """Retourne le pourcentage de progression (0.0 à 1.0)."""
        duree_totale = self._state.get("duree_totale", 0)
        if duree_totale <= 0:
            return 0.0
        restant = self.temps_restant.total_seconds()
        return max(0.0, min(1.0, 1.0 - (restant / duree_totale)))

    def demarrer(self, duree_secondes: int, label: str = "") -> None:
        """Démarre le timer pour *duree_secondes* secondes."""
        self._state.update(
            {
                "actif": True,
                "fin": datetime.now() + timedelta(seconds=duree_secondes),
                "duree_totale": duree_secondes,
                "label": label,
                "termine": False,
            }
        )
        logger.info("Timer démarré: %ds (%s)", duree_secondes, label or "sans label")

    def arreter(self) -> None:
        """Arrête le timer en cours."""
        self._state.update(
            {
                "actif": False,
                "fin": None,
                "duree_totale": 0,
                "label": "",
                "termine": False,
            }
        )

    def formater_temps(self) -> str:
        """Formate le temps restant en MM:SS ou HH:MM:SS."""
        delta = self.temps_restant
        total_sec = int(delta.total_seconds())

        if total_sec <= 0 and self.est_actif:
            return "00:00"

        heures, reste = divmod(total_sec, 3600)
        minutes, secondes = divmod(reste, 60)

        if heures > 0:
            return f"{heures:02d}:{minutes:02d}:{secondes:02d}"
        return f"{minutes:02d}:{secondes:02d}"

    def afficher(self, compact: bool = False) -> None:
        """Affiche le timer complet avec contrôles.

        Args:
            compact: Si True, affiche une version compacte (badge seulement).
        """
        if compact:
            self._afficher_badge()
            return

        st.markdown("#### ⏱️ Timer Cuisine")

        if not self.est_actif:
            self._afficher_demarrage()
        elif self.est_termine:
            self._afficher_termine()
        else:
            self._afficher_en_cours()

    def _afficher_demarrage(self) -> None:
        """Affiche l'interface de démarrage du timer."""
        col_preset, col_custom = st.columns([3, 2])

        with col_preset:
            st.markdown("**Durées prédéfinies**")
            cols = st.columns(4)
            for i, (label, secondes) in enumerate(self._PRESETS.items()):
                with cols[i % 4]:
                    if st.button(label, key=f"timer_preset_{secondes}"):
                        self.demarrer(secondes, label)
                        st.rerun()

        with col_custom:
            st.markdown("**Personnalisé**")
            minutes = st.number_input(
                "Minutes",
                min_value=1,
                max_value=180,
                value=5,
                key="timer_custom_minutes",
            )
            if st.button("▶️ Démarrer", key="timer_start_custom"):
                self.demarrer(int(minutes) * 60, f"{int(minutes)} min")
                st.rerun()

    def _afficher_en_cours(self) -> None:
        """Affiche le timer en cours avec progression."""
        label = self._state.get("label", "")
        temps_str = self.formater_temps()
        pct = self.progression

        # Grand affichage du temps — semantic tokens pour dark mode
        if pct < 0.75:
            couleur = "var(--sem-success, #4CAF50)"
        elif pct < 0.9:
            couleur = "var(--sem-warning, #FF9800)"
        else:
            couleur = "var(--sem-danger, #f44336)"

        st.markdown(
            f'<div style="text-align:center;font-size:3em;font-weight:bold;'
            f'color:{couleur};font-family:monospace">{temps_str}</div>',
            unsafe_allow_html=True,
        )

        if label:
            st.markdown(
                f'<p style="text-align:center;'
                f'color:var(--sem-on-surface-muted, #888)">{label}</p>',
                unsafe_allow_html=True,
            )

        # Barre de progression
        st.progress(pct)

        # Bouton d'arrêt
        if st.button("⏹️ Arrêter", key="timer_stop"):
            self.arreter()
            st.rerun()

    def _afficher_termine(self) -> None:
        """Affiche l'alerte de fin de timer."""
        label = self._state.get("label", "")
        msg = f"⏰ Timer terminé ! ({label})" if label else "⏰ Timer terminé !"

        st.success(msg)
        st.balloons()

        if st.button("🔄 Nouveau timer", key="timer_reset"):
            self.arreter()
            st.rerun()

    def _afficher_badge(self) -> None:
        """Affiche un badge compact pour le timer actif."""
        if not self.est_actif:
            return

        if self.est_termine:
            badge_html = (
                '<span style="background:var(--sem-danger, #f44336);'
                "color:var(--sem-on-interactive, white);padding:4px 12px;"
                'border-radius:12px;font-size:0.85em;animation:pulse 1s infinite">'
                "⏰ Terminé!</span>"
            )
        else:
            temps_str = self.formater_temps()
            badge_html = (
                f'<span style="background:var(--sem-interactive, #4CAF50);'
                f"color:var(--sem-on-interactive, white);padding:4px 12px;"
                f'border-radius:12px;font-size:0.85em;font-family:monospace">'
                f"⏱️ {temps_str}</span>"
            )

        st.markdown(badge_html, unsafe_allow_html=True)


__all__ = ["TimerCuisine"]
