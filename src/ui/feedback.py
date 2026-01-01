"""
Composants UI de Feedback Temps Réel
Spinners intelligents, progress bars, estimations temps
"""
import streamlit as st
import time
from typing import Optional, Callable, Any
from contextlib import contextmanager
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# SPINNER INTELLIGENT
# ═══════════════════════════════════════════════════════════

@contextmanager
def smart_spinner(
        operation: str,
        estimated_seconds: Optional[int] = None,
        show_elapsed: bool = True
):
    """
    Spinner avec estimation temps et temps écoulé

    Usage:
        with smart_spinner("Génération recettes", estimated_seconds=5):
            result = await generate_recipes()

    Args:
        operation: Nom de l'opération
        estimated_seconds: Temps estimé (affiche countdown)
        show_elapsed: Afficher temps écoulé après
    """
    start_time = datetime.now()

    # Message initial
    if estimated_seconds:
        message = f"⏳ {operation}... (estimation: {estimated_seconds}s)"
    else:
        message = f"⏳ {operation}..."

    with st.spinner(message):
        try:
            yield
        finally:
            # Calculer temps écoulé
            elapsed = (datetime.now() - start_time).total_seconds()

            if show_elapsed:
                if elapsed < 1:
                    st.caption(f"✅ Terminé en {elapsed*1000:.0f}ms")
                else:
                    st.caption(f"✅ Terminé en {elapsed:.1f}s")


# ═══════════════════════════════════════════════════════════
# PROGRESS BAR AVANCÉE
# ═══════════════════════════════════════════════════════════

class ProgressTracker:
    """
    Tracker de progression pour opérations longues

    Usage:
        progress = ProgressTracker("Import recettes", total=100)
        for i, item in enumerate(items):
            process_item(item)
            progress.update(i+1, f"Traitement: {item.name}")
        progress.complete()
    """

    def __init__(self, operation: str, total: int, show_percentage: bool = True):
        self.operation = operation
        self.total = total
        self.show_percentage = show_percentage
        self.current = 0
        self.start_time = datetime.now()

        # Créer éléments Streamlit
        self.title_placeholder = st.empty()
        self.progress_bar = st.progress(0)
        self.status_placeholder = st.empty()

        self._update_display()

    def update(self, current: int, status: str = ""):
        """
        Met à jour la progression

        Args:
            current: Valeur actuelle (0 à total)
            status: Message de statut
        """
        self.current = current
        self._update_display(status)

    def increment(self, step: int = 1, status: str = ""):
        """Incrémente la progression"""
        self.current = min(self.current + step, self.total)
        self._update_display(status)

    def complete(self, message: str = ""):
        """Marque comme terminé"""
        self.current = self.total
        self._update_display()

        elapsed = (datetime.now() - self.start_time).total_seconds()

        if message:
            self.status_placeholder.success(f"✅ {message} (en {elapsed:.1f}s)")
        else:
            self.status_placeholder.success(f"✅ Terminé en {elapsed:.1f}s")

        # Nettoyer après 2s
        time.sleep(2)
        self.title_placeholder.empty()
        self.progress_bar.empty()

    def error(self, message: str):
        """Affiche une erreur"""
        self.status_placeholder.error(f"❌ {message}")

    def _update_display(self, status: str = ""):
        """Met à jour l'affichage"""
        progress_pct = self.current / self.total if self.total > 0 else 0

        # Titre avec pourcentage
        if self.show_percentage:
            title = f"{self.operation} - {progress_pct*100:.0f}%"
        else:
            title = f"{self.operation} - {self.current}/{self.total}"

        self.title_placeholder.markdown(f"**{title}**")

        # Progress bar
        self.progress_bar.progress(progress_pct)

        # Estimation temps restant
        if self.current > 0 and self.current < self.total:
            elapsed = (datetime.now() - self.start_time).total_seconds()
            estimated_total = elapsed / self.current * self.total
            remaining = estimated_total - elapsed

            status_msg = f"⏱️ Temps restant: ~{remaining:.0f}s"

            if status:
                status_msg = f"{status} • {status_msg}"

            self.status_placeholder.caption(status_msg)
        elif status:
            self.status_placeholder.caption(status)


# ═══════════════════════════════════════════════════════════
# LOADING STATES
# ═══════════════════════════════════════════════════════════

class LoadingState:
    """
    Gestion d'états de chargement multiples

    Usage:
        loading = LoadingState("Chargement données")

        loading.add_step("Connexion DB")
        # ... code ...
        loading.complete_step("Connexion DB")

        loading.add_step("Import recettes")
        # ... code ...
        loading.complete_step("Import recettes")

        loading.finish()
    """

    def __init__(self, title: str):
        self.title = title
        self.steps = []
        self.current_step = None
        self.start_time = datetime.now()

        # UI
        self.title_placeholder = st.empty()
        self.steps_placeholder = st.empty()

        self._update_display()

    def add_step(self, step_name: str):
        """Ajoute une étape"""
        self.steps.append({
            "name": step_name,
            "status": "⏳ En cours...",
            "started_at": datetime.now(),
            "completed": False
        })
        self.current_step = len(self.steps) - 1
        self._update_display()

    def complete_step(self, step_name: str = None, success: bool = True):
        """Marque une étape comme terminée"""
        # Trouver l'étape
        if step_name:
            step_idx = next(
                (i for i, s in enumerate(self.steps) if s["name"] == step_name),
                None
            )
        else:
            step_idx = self.current_step

        if step_idx is not None and step_idx < len(self.steps):
            step = self.steps[step_idx]

            elapsed = (datetime.now() - step["started_at"]).total_seconds()

            if success:
                step["status"] = f"✅ OK ({elapsed:.1f}s)"
            else:
                step["status"] = f"❌ Erreur"

            step["completed"] = True
            self._update_display()

    def error_step(self, step_name: str = None, error_msg: str = ""):
        """Marque une étape en erreur"""
        if step_name:
            step_idx = next(
                (i for i, s in enumerate(self.steps) if s["name"] == step_name),
                None
            )
        else:
            step_idx = self.current_step

        if step_idx is not None and step_idx < len(self.steps):
            step = self.steps[step_idx]
            step["status"] = f"❌ {error_msg}" if error_msg else "❌ Erreur"
            step["completed"] = True
            self._update_display()

    def finish(self, success_message: str = ""):
        """Termine le chargement"""
        elapsed = (datetime.now() - self.start_time).total_seconds()

        if success_message:
            self.title_placeholder.success(f"✅ {success_message} (en {elapsed:.1f}s)")
        else:
            self.title_placeholder.success(f"✅ {self.title} terminé (en {elapsed:.1f}s)")

        # Nettoyer après 3s
        time.sleep(3)
        self.title_placeholder.empty()
        self.steps_placeholder.empty()

    def _update_display(self):
        """Met à jour l'affichage"""
        completed = sum(1 for s in self.steps if s["completed"])
        total = len(self.steps)

        title = f"**{self.title}** ({completed}/{total})"
        self.title_placeholder.markdown(title)

        # Liste des étapes
        steps_html = "<div style='padding: 1rem; background: #f8f9fa; border-radius: 8px;'>"

        for step in self.steps:
            steps_html += f"<div style='margin: 0.5rem 0;'>"
            steps_html += f"<strong>{step['name']}</strong> • {step['status']}"
            steps_html += "</div>"

        steps_html += "</div>"

        self.steps_placeholder.markdown(steps_html, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════
# ASYNC OPERATION WRAPPER
# ═══════════════════════════════════════════════════════════

async def run_with_feedback(
        operation: Callable,
        operation_name: str,
        estimated_seconds: Optional[int] = None,
        *args,
        **kwargs
) -> Any:
    """
    Exécute une opération async avec feedback automatique

    Usage:
        result = await run_with_feedback(
            generate_recipes,
            "Génération recettes",
            estimated_seconds=5,
            filters={"saison": "été"}
        )
    """
    with smart_spinner(operation_name, estimated_seconds):
        try:
            result = await operation(*args, **kwargs)
            return result
        except Exception as e:
            logger.exception(f"Erreur dans {operation_name}")
            st.error(f"❌ Erreur: {str(e)}")
            raise


# ═══════════════════════════════════════════════════════════
# TOAST NOTIFICATIONS AVANCÉES
# ═══════════════════════════════════════════════════════════

class ToastManager:
    """
    Gestionnaire de notifications toast

    Affiche des notifications temporaires non-bloquantes
    """

    TOAST_KEY = "toast_notifications"

    @staticmethod
    def _init():
        if ToastManager.TOAST_KEY not in st.session_state:
            st.session_state[ToastManager.TOAST_KEY] = []

    @staticmethod
    def show(message: str, type: str = "info", duration: int = 3):
        """
        Affiche une notification toast

        Args:
            message: Message
            type: "success", "error", "warning", "info"
            duration: Durée en secondes
        """
        ToastManager._init()

        toast = {
            "message": message,
            "type": type,
            "created_at": datetime.now(),
            "expires_at": datetime.now() + timedelta(seconds=duration)
        }

        st.session_state[ToastManager.TOAST_KEY].append(toast)

    @staticmethod
    def render():
        """Affiche les toasts actifs"""
        ToastManager._init()

        toasts = st.session_state[ToastManager.TOAST_KEY]
        now = datetime.now()

        # Filtrer expirés
        active_toasts = [
            toast for toast in toasts
            if toast["expires_at"] > now
        ]

        st.session_state[ToastManager.TOAST_KEY] = active_toasts

        # Afficher
        if active_toasts:
            toast_container = st.container()

            with toast_container:
                for toast in active_toasts[-3:]:  # Max 3 toasts
                    type_map = {
                        "success": st.success,
                        "error": st.error,
                        "warning": st.warning,
                        "info": st.info
                    }

                    display_func = type_map.get(toast["type"], st.info)
                    display_func(toast["message"])


# ═══════════════════════════════════════════════════════════
# HELPERS RACCOURCIS
# ═══════════════════════════════════════════════════════════

def show_success(message: str, duration: int = 3):
    """Raccourci pour toast success"""
    ToastManager.show(message, "success", duration)


def show_error(message: str, duration: int = 5):
    """Raccourci pour toast error"""
    ToastManager.show(message, "error", duration)


def show_warning(message: str, duration: int = 4):
    """Raccourci pour toast warning"""
    ToastManager.show(message, "warning", duration)


def show_info(message: str, duration: int = 3):
    """Raccourci pour toast info"""
    ToastManager.show(message, "info", duration)