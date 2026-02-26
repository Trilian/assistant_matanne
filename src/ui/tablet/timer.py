"""
Timer de cuisine avec compte à rebours réel et alertes sonores.

Support multi-timers simultanés, notifications navigateur,
vibrations mobile et sons d'alerte via Web Audio API.

Usage::

    from src.ui.tablet.timer import TimerCuisine, GestionnaireTimers

    timer = TimerCuisine()
    timer.afficher()

    # Multi-timers
    gestionnaire = GestionnaireTimers()
    gestionnaire.afficher()
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Any

import streamlit as st

from src.core.state import rerun

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════
# HTML/JS alertes sonores et notifications navigateur
# ═══════════════════════════════════════════════════════════

_AUDIO_ALERT_HTML = """
<div id="timer-audio-{timer_id}" style="display:none">
    <script>
    (function() {{
        function playAlertSound() {{
            try {{
                var ctx = new (window.AudioContext || window.webkitAudioContext)();
                var notes = [523.25, 659.25, 783.99, 1046.50];
                notes.forEach(function(freq, i) {{
                    var osc = ctx.createOscillator();
                    var gain = ctx.createGain();
                    osc.connect(gain);
                    gain.connect(ctx.destination);
                    osc.frequency.value = freq;
                    osc.type = 'sine';
                    gain.gain.setValueAtTime(0.3, ctx.currentTime + i * 0.3);
                    gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + i * 0.3 + 0.25);
                    osc.start(ctx.currentTime + i * 0.3);
                    osc.stop(ctx.currentTime + i * 0.3 + 0.25);
                }});
            }} catch(e) {{ console.log('Audio non supporté:', e); }}
        }}
        playAlertSound();
        setTimeout(playAlertSound, 1500);
        setTimeout(playAlertSound, 3000);
        if ('Notification' in window && Notification.permission === 'granted') {{
            new Notification('⏰ Timer terminé !', {{body: '{label}', requireInteraction: true}});
        }}
        if ('vibrate' in navigator) {{ navigator.vibrate([200, 100, 200, 100, 200]); }}
    }})();
    </script>
</div>
"""

_NOTIFICATION_PERMISSION_HTML = """
<script>
if ('Notification' in window && Notification.permission === 'default') {
    Notification.requestPermission();
}
</script>
"""

_WARNING_SOUND_HTML = """
<div id="timer-warning-{timer_id}" style="display:none">
    <script>
    (function() {{
        try {{
            var ctx = new (window.AudioContext || window.webkitAudioContext)();
            var osc = ctx.createOscillator();
            var gain = ctx.createGain();
            osc.connect(gain);
            gain.connect(ctx.destination);
            osc.frequency.value = 440;
            osc.type = 'sine';
            gain.gain.setValueAtTime(0.15, ctx.currentTime);
            gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.15);
            osc.start(ctx.currentTime);
            osc.stop(ctx.currentTime + 0.15);
        }} catch(e) {{}}
    }})();
    </script>
</div>
"""


class TimerCuisine:
    """Timer de cuisine persistant via session_state avec alertes sonores."""

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

    def __init__(self, state_key: str | None = None) -> None:
        """Initialise l'état du timer dans session_state."""
        if state_key:
            self._STATE_KEY = state_key
        if self._STATE_KEY not in st.session_state:
            st.session_state[self._STATE_KEY] = {
                "actif": False,
                "fin": None,
                "duree_totale": 0,
                "label": "",
                "termine": False,
                "alerte_jouee": False,
                "warning_joue": False,
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

    @property
    def label(self) -> str:
        """Retourne le label du timer."""
        return self._state.get("label", "")

    def demarrer(self, duree_secondes: int, label: str = "") -> None:
        """Démarre le timer pour *duree_secondes* secondes."""
        self._state.update(
            {
                "actif": True,
                "fin": datetime.now() + timedelta(seconds=duree_secondes),
                "duree_totale": duree_secondes,
                "label": label,
                "termine": False,
                "alerte_jouee": False,
                "warning_joue": False,
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
                "alerte_jouee": False,
                "warning_joue": False,
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
        """Affiche le timer complet avec contrôles et alertes sonores.

        Args:
            compact: Si True, affiche une version compacte (badge seulement).
        """
        if compact:
            self._afficher_badge()
            return

        # Demander permission notifications navigateur
        st.components.v1.html(_NOTIFICATION_PERMISSION_HTML, height=0)

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
                    if st.button(label, key=f"timer_preset_{self._STATE_KEY}_{secondes}"):
                        self.demarrer(secondes, label)
                        rerun()

        with col_custom:
            st.markdown("**Personnalisé**")
            minutes = st.number_input(
                "Minutes",
                min_value=1,
                max_value=180,
                value=5,
                key=f"timer_custom_minutes_{self._STATE_KEY}",
            )
            if st.button("▶️ Démarrer", key=f"timer_start_custom_{self._STATE_KEY}"):
                self.demarrer(int(minutes) * 60, f"{int(minutes)} min")
                rerun()

    def _afficher_en_cours(self) -> None:
        """Affiche le timer en cours avec progression et alerte warning."""
        label = self._state.get("label", "")
        temps_str = self.formater_temps()
        pct = self.progression
        restant_sec = int(self.temps_restant.total_seconds())

        # Couleur selon progression
        if pct < 0.75:
            couleur = "var(--sem-success, #4CAF50)"
        elif pct < 0.9:
            couleur = "var(--sem-warning, #FF9800)"
        else:
            couleur = "var(--sem-danger, #f44336)"

        # Bip d'avertissement à 30 secondes
        if restant_sec <= 30 and not self._state.get("warning_joue", False):
            self._state["warning_joue"] = True
            st.components.v1.html(
                _WARNING_SOUND_HTML.format(timer_id=self._STATE_KEY),
                height=0,
            )

        st.markdown(
            f'<div style="text-align:center;font-size:3em;font-weight:bold;'
            f'color:{couleur};font-family:monospace">{temps_str}</div>',
            unsafe_allow_html=True,
        )

        if label:
            st.markdown(
                f'<p style="text-align:center;color:var(--sem-on-surface-muted, #888)">{label}</p>',
                unsafe_allow_html=True,
            )

        st.progress(pct)

        if st.button("⏹️ Arrêter", key=f"timer_stop_{self._STATE_KEY}"):
            self.arreter()
            rerun()

    def _afficher_termine(self) -> None:
        """Affiche l'alerte de fin avec son, notification et vibration."""
        label = self._state.get("label", "")
        msg = f"⏰ Timer terminé ! ({label})" if label else "⏰ Timer terminé !"

        # Jouer l'alerte sonore une seule fois par fin de timer
        if not self._state.get("alerte_jouee", False):
            self._state["alerte_jouee"] = True
            st.components.v1.html(
                _AUDIO_ALERT_HTML.format(
                    timer_id=self._STATE_KEY,
                    label=label or "Timer",
                ),
                height=0,
            )

        st.success(msg)
        st.balloons()

        if st.button("🔄 Nouveau timer", key=f"timer_reset_{self._STATE_KEY}"):
            self.arreter()
            rerun()

    def _afficher_badge(self) -> None:
        """Affiche un badge compact pour le timer actif."""
        if not self.est_actif:
            return

        if self.est_termine:
            if not self._state.get("alerte_jouee", False):
                self._state["alerte_jouee"] = True
                st.components.v1.html(
                    _AUDIO_ALERT_HTML.format(
                        timer_id=self._STATE_KEY,
                        label=self.label or "Timer",
                    ),
                    height=0,
                )
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


class GestionnaireTimers:
    """Gestionnaire multi-timers simultanés (jusqu'à 5)."""

    _MAX_TIMERS = 5
    _REGISTRY_KEY = "cuisine_timers_registry"

    def __init__(self) -> None:
        """Initialise le registre de timers."""
        if self._REGISTRY_KEY not in st.session_state:
            st.session_state[self._REGISTRY_KEY] = []

    @property
    def _registry(self) -> list[str]:
        """Liste des clés de timers enregistrés."""
        return st.session_state[self._REGISTRY_KEY]

    @property
    def timers(self) -> list[TimerCuisine]:
        """Retourne tous les timers enregistrés."""
        return [TimerCuisine(state_key=key) for key in self._registry]

    @property
    def timers_actifs(self) -> list[TimerCuisine]:
        """Retourne les timers actifs (en cours ou terminés)."""
        return [t for t in self.timers if t.est_actif]

    @property
    def nb_actifs(self) -> int:
        """Nombre de timers actifs."""
        return len(self.timers_actifs)

    def ajouter_timer(self, duree_secondes: int, label: str = "") -> TimerCuisine | None:
        """Ajoute et démarre un nouveau timer. Retourne None si max atteint."""
        self._nettoyer()
        if len(self._registry) >= self._MAX_TIMERS:
            return None

        key = f"cuisine_timer_{len(self._registry)}_{int(datetime.now().timestamp())}"
        self._registry.append(key)
        timer = TimerCuisine(state_key=key)
        timer.demarrer(duree_secondes, label)
        return timer

    def _nettoyer(self) -> None:
        """Supprime les timers arrêtés (garde les actifs et terminés)."""
        a_garder = []
        for key in self._registry:
            timer = TimerCuisine(state_key=key)
            if timer.est_actif:
                a_garder.append(key)
        st.session_state[self._REGISTRY_KEY] = a_garder

    def supprimer_timer(self, key: str) -> None:
        """Supprime un timer spécifique."""
        timer = TimerCuisine(state_key=key)
        timer.arreter()
        if key in self._registry:
            self._registry.remove(key)

    def afficher(self) -> None:
        """Affiche tous les timers actifs et le panneau d'ajout."""
        st.components.v1.html(_NOTIFICATION_PERMISSION_HTML, height=0)
        st.markdown("#### ⏱️ Timers Cuisine")

        actifs = self.timers
        if actifs:
            for timer in actifs:
                with st.container():
                    col_info, col_action = st.columns([4, 1])
                    with col_info:
                        if timer.est_termine:
                            timer._afficher_termine()
                        elif timer.est_actif:
                            timer._afficher_en_cours()
                    with col_action:
                        if st.button("❌", key=f"rm_{timer._STATE_KEY}", help="Supprimer"):
                            self.supprimer_timer(timer._STATE_KEY)
                            rerun()
                    st.divider()

        if len(self._registry) < self._MAX_TIMERS:
            st.markdown("**Ajouter un timer**")
            col_presets, col_custom = st.columns([3, 2])
            with col_presets:
                cols = st.columns(4)
                for i, (label, secondes) in enumerate(TimerCuisine._PRESETS.items()):
                    with cols[i % 4]:
                        if st.button(label, key=f"multi_preset_{secondes}"):
                            self.ajouter_timer(secondes, label)
                            rerun()
            with col_custom:
                minutes = st.number_input("Minutes", 1, 180, 5, key="multi_timer_min")
                nom = st.text_input("Nom", key="multi_timer_nom", placeholder="Ex: Pâtes")
                if st.button("▶️ Ajouter", key="multi_timer_add"):
                    lab = nom if nom else f"{int(minutes)} min"
                    self.ajouter_timer(int(minutes) * 60, lab)
                    rerun()
        else:
            st.info(f"Maximum de {self._MAX_TIMERS} timers atteint.")

    def afficher_badges(self) -> None:
        """Affiche tous les badges de timers actifs en ligne."""
        actifs = self.timers_actifs
        if not actifs:
            return

        badges = []
        for t in actifs:
            if t.est_termine:
                if not t._state.get("alerte_jouee", False):
                    t._state["alerte_jouee"] = True
                    st.components.v1.html(
                        _AUDIO_ALERT_HTML.format(timer_id=t._STATE_KEY, label=t.label or "Timer"),
                        height=0,
                    )
                lbl = f"⏰ Terminé!{f' ({t.label})' if t.label else ''}"
                bg = "var(--sem-danger, #f44336)"
            else:
                lbl = f"⏱️ {t.formater_temps()}{f' ({t.label})' if t.label else ''}"
                bg = "var(--sem-interactive, #4CAF50)"

            badges.append(
                f'<span style="display:inline-block;margin:2px;background:{bg};'
                f"color:var(--sem-on-interactive, white);padding:4px 10px;"
                f'border-radius:12px;font-size:0.8em;font-family:monospace">'
                f"{lbl}</span>"
            )

        st.markdown(" ".join(badges), unsafe_allow_html=True)


__all__ = ["TimerCuisine", "GestionnaireTimers"]
