"""
Système de dialogues modernes basé sur st.dialog() (Streamlit 1.35+).

Remplace la classe ``Modale`` legacy par des dialogues natifs Streamlit
avec une API fluent, support callbacks, et accessibilité native.

Features:
- DialogBuilder avec pattern fluent
- Variantes prêtes à l'emploi: confirm, alert, form
- Gestion automatique du state
- Fallback gracieux si st.dialog non disponible
- Callbacks typés avec Result pattern

Usage:
    from src.ui.dialogs import confirm_dialog, DialogBuilder, ouvrir_dialog

    # Dialogue de confirmation simple
    if st.button("Supprimer"):
        ouvrir_dialog("delete_confirm")

    if confirm_dialog(
        "delete_confirm",
        titre="Supprimer la recette ?",
        message="Cette action est irréversible.",
        on_confirm=lambda: service.supprimer(recette_id),
    ):
        st.success("Recette supprimée")

    # Builder avancé
    with DialogBuilder("edit_item") as dialog:
        dialog.titre("Modifier l'élément")
        dialog.content(lambda: afficher_formulaire_edition())
        dialog.action("Sauvegarder", on_click=sauvegarder, primary=True)
        dialog.action("Annuler")
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any, Callable, TypeVar

import streamlit as st

logger = logging.getLogger(__name__)

T = TypeVar("T")


class DialogType(StrEnum):
    """Types de dialogues prédéfinis."""

    CONFIRM = "confirm"
    ALERT = "alert"
    FORM = "form"
    CUSTOM = "custom"


@dataclass
class DialogAction:
    """Action (bouton) dans un dialogue."""

    label: str
    on_click: Callable[[], Any] | None = None
    primary: bool = False
    danger: bool = False
    close_on_click: bool = True


@dataclass
class DialogConfig:
    """Configuration complète d'un dialogue."""

    key: str
    titre: str = ""
    message: str = ""
    type_dialog: DialogType = DialogType.CUSTOM
    icon: str = ""
    actions: list[DialogAction] = field(default_factory=list)
    content_fn: Callable[[], Any] | None = None
    width: str = "small"  # small, large


def _has_dialog_support() -> bool:
    """Vérifie si Streamlit supporte st.dialog (>= 1.35)."""
    return hasattr(st, "dialog")


def _get_state_key(dialog_key: str) -> str:
    """Génère la clé session_state pour un dialogue."""
    return f"_dialog_{dialog_key}_open"


def _get_result_key(dialog_key: str) -> str:
    """Clé pour stocker le résultat du dialogue."""
    return f"_dialog_{dialog_key}_result"


def ouvrir_dialog(key: str) -> None:
    """Ouvre un dialogue par sa clé."""
    st.session_state[_get_state_key(key)] = True


def fermer_dialog(key: str, result: Any = None) -> None:
    """Ferme un dialogue et stocke optionnellement un résultat."""
    st.session_state[_get_state_key(key)] = False
    if result is not None:
        st.session_state[_get_result_key(key)] = result


def dialog_est_ouvert(key: str) -> bool:
    """Vérifie si un dialogue est actuellement ouvert."""
    return st.session_state.get(_get_state_key(key), False)


def obtenir_resultat_dialog(key: str, default: T = None) -> T | None:
    """Récupère le résultat d'un dialogue fermé."""
    return st.session_state.get(_get_result_key(key), default)


class DialogBuilder:
    """Builder fluent pour créer des dialogues personnalisés.

    Utilise ``st.dialog()`` quand disponible, sinon fallback sur
    ``st.container()`` stylisé.

    Usage:
        builder = DialogBuilder("edit_user")
        builder.titre("Modifier l'utilisateur")
        builder.message("Entrez les nouvelles informations")
        builder.action("Sauvegarder", on_click=save_fn, primary=True)
        builder.action("Annuler")
        builder.render()

    Ou avec context manager:
        with DialogBuilder("confirm") as d:
            d.titre("Confirmer ?")
            d.render()
    """

    def __init__(self, key: str, width: str = "small"):
        """
        Args:
            key: Identifiant unique du dialogue
            width: Largeur ('small' ou 'large')
        """
        self._config = DialogConfig(key=key, width=width)
        self._rendered = False

    def titre(self, titre: str) -> DialogBuilder:
        """Définit le titre du dialogue."""
        self._config.titre = titre
        return self

    def message(self, message: str) -> DialogBuilder:
        """Définit le message principal."""
        self._config.message = message
        return self

    def icon(self, icon: str) -> DialogBuilder:
        """Définit l'icône (emoji)."""
        self._config.icon = icon
        return self

    def type(self, type_dialog: DialogType) -> DialogBuilder:
        """Définit le type de dialogue."""
        self._config.type_dialog = type_dialog
        return self

    def content(self, content_fn: Callable[[], Any]) -> DialogBuilder:
        """Définit une fonction de contenu personnalisé.

        Args:
            content_fn: Fonction appelée pour rendre le contenu
        """
        self._config.content_fn = content_fn
        return self

    def action(
        self,
        label: str,
        on_click: Callable[[], Any] | None = None,
        primary: bool = False,
        danger: bool = False,
        close_on_click: bool = True,
    ) -> DialogBuilder:
        """Ajoute une action (bouton) au dialogue.

        Args:
            label: Texte du bouton
            on_click: Callback lors du clic
            primary: Style primaire (bleu)
            danger: Style danger (rouge)
            close_on_click: Fermer le dialogue après clic
        """
        self._config.actions.append(
            DialogAction(
                label=label,
                on_click=on_click,
                primary=primary,
                danger=danger,
                close_on_click=close_on_click,
            )
        )
        return self

    def render(self) -> Any | None:
        """Rend le dialogue si ouvert.

        Returns:
            Résultat de l'action exécutée, ou None
        """
        if self._rendered:
            return None

        self._rendered = True
        key = self._config.key

        if not dialog_est_ouvert(key):
            return None

        if _has_dialog_support():
            return self._render_native()
        else:
            return self._render_fallback()

    def _render_native(self) -> Any | None:
        """Rendu avec st.dialog() natif."""
        config = self._config

        @st.dialog(config.titre or "Dialog", width=config.width)
        def _dialog_content():
            result = None

            # Icon + message
            if config.icon:
                st.markdown(f"## {config.icon}")

            if config.message:
                st.markdown(config.message)

            # Contenu personnalisé
            if config.content_fn:
                config.content_fn()

            # Actions
            if config.actions:
                cols = st.columns(len(config.actions))
                for i, action in enumerate(config.actions):
                    with cols[i]:
                        btn_type = "primary" if action.primary else "secondary"
                        if st.button(
                            action.label,
                            key=f"{config.key}_action_{i}",
                            type=btn_type,
                            use_container_width=True,
                        ):
                            if action.on_click:
                                result = action.on_click()
                            if action.close_on_click:
                                fermer_dialog(config.key, result)
                                st.rerun()

            return result

        return _dialog_content()

    def _render_fallback(self) -> Any | None:
        """Rendu fallback sans st.dialog() (container stylisé)."""
        config = self._config
        result = None

        with st.container(border=True):
            if config.titre:
                titre_display = f"{config.icon} {config.titre}" if config.icon else config.titre
                st.subheader(titre_display)

            if config.message:
                st.markdown(config.message)

            if config.content_fn:
                config.content_fn()

            # Actions
            if config.actions:
                cols = st.columns(len(config.actions))
                for i, action in enumerate(config.actions):
                    with cols[i]:
                        btn_type = "primary" if action.primary else "secondary"
                        if st.button(
                            action.label,
                            key=f"{config.key}_action_{i}",
                            type=btn_type,
                            use_container_width=True,
                        ):
                            if action.on_click:
                                result = action.on_click()
                            if action.close_on_click:
                                fermer_dialog(config.key, result)
                                st.rerun()

        return result

    def __enter__(self) -> DialogBuilder:
        """Support context manager."""
        return self

    def __exit__(self, *args: Any) -> None:
        """Rend automatiquement à la sortie du context."""
        self.render()


# ═══════════════════════════════════════════════════════════
# DIALOGUES PRÉ-CONFIGURÉS
# ═══════════════════════════════════════════════════════════


def confirm_dialog(
    key: str,
    titre: str = "Confirmer",
    message: str = "Êtes-vous sûr ?",
    on_confirm: Callable[[], Any] | None = None,
    on_cancel: Callable[[], Any] | None = None,
    confirm_label: str = "✅ Confirmer",
    cancel_label: str = "❌ Annuler",
    danger: bool = False,
) -> bool:
    """Dialogue de confirmation simple.

    Args:
        key: Clé unique
        titre: Titre du dialogue
        message: Message de confirmation
        on_confirm: Callback si confirmé
        on_cancel: Callback si annulé
        confirm_label: Texte bouton confirmer
        cancel_label: Texte bouton annuler
        danger: Style danger pour action destructive

    Returns:
        True si confirmé, False sinon

    Usage:
        if st.button("Supprimer"):
            ouvrir_dialog("delete_confirm")

        if confirm_dialog(
            "delete_confirm",
            titre="Supprimer ?",
            message="Cette action est irréversible.",
            on_confirm=lambda: service.delete(item_id),
            danger=True
        ):
            st.success("Supprimé !")
    """
    builder = DialogBuilder(key)
    builder.titre(titre)
    builder.message(message)
    builder.icon("⚠️" if danger else "❓")
    builder.type(DialogType.CONFIRM)

    def _on_confirm():
        if on_confirm:
            on_confirm()
        return True

    def _on_cancel():
        if on_cancel:
            on_cancel()
        return False

    builder.action(confirm_label, on_click=_on_confirm, primary=not danger, danger=danger)
    builder.action(cancel_label, on_click=_on_cancel)

    result = builder.render()
    return result is True


def alert_dialog(
    key: str,
    titre: str = "Information",
    message: str = "",
    icon: str = "ℹ️",
    ok_label: str = "OK",
) -> None:
    """Dialogue d'alerte/information simple.

    Args:
        key: Clé unique
        titre: Titre
        message: Message à afficher
        icon: Icône emoji
        ok_label: Texte du bouton OK
    """
    builder = DialogBuilder(key)
    builder.titre(titre)
    builder.message(message)
    builder.icon(icon)
    builder.type(DialogType.ALERT)
    builder.action(ok_label, primary=True)
    builder.render()


def form_dialog(
    key: str,
    titre: str,
    form_content: Callable[[], dict[str, Any]],
    on_submit: Callable[[dict[str, Any]], Any] | None = None,
    submit_label: str = "💾 Enregistrer",
    cancel_label: str = "Annuler",
) -> dict[str, Any] | None:
    """Dialogue avec formulaire intégré.

    Args:
        key: Clé unique
        titre: Titre du dialogue
        form_content: Fonction qui rend le formulaire et retourne les valeurs
        on_submit: Callback avec les données du formulaire
        submit_label: Texte bouton submit
        cancel_label: Texte bouton annuler

    Returns:
        Données du formulaire si soumis, None sinon

    Usage:
        def mon_formulaire():
            return {
                "nom": st.text_input("Nom"),
                "email": st.text_input("Email"),
            }

        result = form_dialog(
            "edit_user",
            titre="Modifier utilisateur",
            form_content=mon_formulaire,
            on_submit=lambda data: service.update(data)
        )
    """

    form_data: dict[str, Any] = {}

    def _content():
        nonlocal form_data
        form_data = form_content()

    def _on_submit():
        if on_submit:
            on_submit(form_data)
        return form_data

    builder = DialogBuilder(key)
    builder.titre(titre)
    builder.type(DialogType.FORM)
    builder.content(_content)
    builder.action(submit_label, on_click=_on_submit, primary=True)
    builder.action(cancel_label)

    result = builder.render()
    return result if isinstance(result, dict) else None


# ═══════════════════════════════════════════════════════════
# TRIGGER HELPERS
# ═══════════════════════════════════════════════════════════


def bouton_dialog(
    dialog_key: str,
    label: str,
    icon: str = "",
    button_type: str = "secondary",
    use_container_width: bool = False,
) -> bool:
    """Bouton qui ouvre un dialogue au clic.

    Args:
        dialog_key: Clé du dialogue à ouvrir
        label: Texte du bouton
        icon: Icône optionnelle
        button_type: Type de bouton ('primary' ou 'secondary')
        use_container_width: Largeur complète

    Returns:
        True si le dialogue est ouvert
    """
    display_label = f"{icon} {label}" if icon else label

    if st.button(
        display_label,
        key=f"trigger_{dialog_key}",
        type=button_type,
        use_container_width=use_container_width,
    ):
        ouvrir_dialog(dialog_key)
        st.rerun()

    return dialog_est_ouvert(dialog_key)


# ═══════════════════════════════════════════════════════════
# COMPATIBILITÉ LEGACY (Modale)
# ═══════════════════════════════════════════════════════════


class Modale:
    """DEPRECATED: Utiliser DialogBuilder ou confirm_dialog à la place.

    Wrapper de compatibilité pour migration progressive.
    Émet un DeprecationWarning à l'instanciation.

    Migration:
        # Ancien
        modal = Modale("delete_confirm")
        if modal.is_showing():
            st.warning("Confirmer ?")
            if modal.confirm():
                delete_item()
                modal.close()
            modal.cancel()

        # Nouveau
        if st.button("Supprimer"):
            ouvrir_dialog("delete_confirm")

        confirm_dialog(
            "delete_confirm",
            titre="Supprimer ?",
            on_confirm=delete_item
        )
    """

    def __init__(self, key: str):
        import warnings

        warnings.warn(
            "Modale est déprécié. Utilisez DialogBuilder ou confirm_dialog().",
            DeprecationWarning,
            stacklevel=2,
        )
        self.key = f"modal_{key}"
        if self.key not in st.session_state:
            st.session_state[self.key] = False

    def show(self) -> None:
        """Affiche la modale."""
        st.session_state[self.key] = True

    def close(self) -> None:
        """Ferme la modale."""
        st.session_state[self.key] = False
        st.rerun()

    def is_showing(self) -> bool:
        """Vérifie si la modale est visible."""
        return st.session_state.get(self.key, False)

    def confirm(self, label: str = "✅ Confirmer") -> bool:
        """Bouton confirmer."""
        return st.button(label, key=f"{self.key}_yes", type="primary", use_container_width=True)

    def cancel(self, label: str = "❌ Annuler") -> None:
        """Bouton annuler."""
        if st.button(label, key=f"{self.key}_no", use_container_width=True):
            self.close()

    # Alias français
    afficher = show
    fermer = close
    est_affichee = is_showing
    confirmer = confirm
    annuler = cancel
