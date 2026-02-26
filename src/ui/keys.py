"""
Key Policy Engine — gestion centralisée des clés de widgets Streamlit.

Résout le problème de collisions de ``key=`` entre widgets en fournissant:
- ``KeyNamespace``: générateur de clés scopé avec préfixe automatique
- ``WidgetKeys``: registre singleton avec détection de doublons

Compatible avec le système existant ``SK`` (session state keys dans
``src/core/session_keys.py``). Ce module gère les **widget keys**
(le paramètre ``key=`` de ``st.text_input``, ``st.button``, etc.).

Usage:
    from src.ui.keys import KeyNamespace

    # Créer un namespace pour un module/composant
    keys = KeyNamespace("recettes")

    st.text_input("Nom", key=keys("nom"))          # → "recettes__nom"
    st.button("Supprimer", key=keys("del", item.id))  # → "recettes__del_42"

    # Sous-namespace pour un composant enfant
    card_keys = keys.child("carte")
    st.button("Like", key=card_keys("like", item.id))  # → "recettes__carte__like_42"

    # Détection de collisions (mode debug)
    from src.ui.keys import widget_keys
    widget_keys.report()  # Affiche les doublons détectés
"""

from __future__ import annotations

import logging
import threading
from typing import Any

logger = logging.getLogger(__name__)

# Séparateur entre segments de namespace
_SEP = "__"
# Séparateur entre nom de clé et suffixe dynamique (ID, index)
_ID_SEP = "_"


class KeyNamespace:
    """Générateur de clés scopé avec préfixe automatique.

    Chaque instance crée des clés préfixées par son namespace,
    empêchant les collisions entre modules/composants.

    Args:
        prefix: Préfixe du namespace (ex: "recettes", "famille")
        register: Si True, enregistre chaque clé générée dans le registre global

    Usage:
        keys = KeyNamespace("planning")
        st.button("OK", key=keys("confirm"))     # → "planning__confirm"
        st.button("OK", key=keys("confirm", 5))  # → "planning__confirm_5"
    """

    __slots__ = ("_prefix", "_register")

    def __init__(self, prefix: str, *, register: bool = True) -> None:
        if not prefix:
            raise ValueError("Le préfixe du namespace ne peut pas être vide")
        self._prefix = prefix
        self._register = register

    # ── API principale ──────────────────────────────────────

    def __call__(self, name: str, *suffixes: Any) -> str:
        """Génère une clé préfixée.

        Args:
            name: Nom logique du widget (ex: "save", "delete")
            *suffixes: Suffixes dynamiques optionnels (ex: item.id, index)

        Returns:
            Clé formatée: ``{prefix}__{name}`` ou ``{prefix}__{name}_{suffix}``
        """
        key = f"{self._prefix}{_SEP}{name}"
        if suffixes:
            parts = _ID_SEP.join(str(s) for s in suffixes)
            key = f"{key}{_ID_SEP}{parts}"

        if self._register:
            widget_keys._register(key, self._prefix)
            # Enregistrer aussi dans le registre centralisé session keys
            try:
                from src.core.session_keys import obtenir_registre_session_keys

                obtenir_registre_session_keys().enregistrer_dynamique(self._prefix, name)
            except ImportError:
                pass  # Éviter erreur circulaire au bootstrap

        return key

    def child(self, sub_prefix: str) -> KeyNamespace:
        """Crée un sous-namespace.

        Args:
            sub_prefix: Préfixe enfant

        Returns:
            Nouveau KeyNamespace avec préfixe composé

        Usage:
            parent = KeyNamespace("cuisine")
            child = parent.child("carte")
            child("like", 42)  # → "cuisine__carte__like_42"
        """
        return KeyNamespace(
            f"{self._prefix}{_SEP}{sub_prefix}",
            register=self._register,
        )

    @property
    def prefix(self) -> str:
        """Retourne le préfixe du namespace."""
        return self._prefix

    def __repr__(self) -> str:
        return f"KeyNamespace({self._prefix!r})"


class _WidgetKeyRegistry:
    """Registre global des clés de widgets avec détection de collisions.

    Singleton thread-safe qui trace toutes les clés générées via
    ``KeyNamespace`` et détecte les doublons potentiels.

    Usage interne — accès via le singleton ``widget_keys``.
    """

    def __init__(self) -> None:
        self._keys: dict[str, str] = {}  # key → namespace source
        self._collisions: list[tuple[str, str, str]] = []  # (key, ns1, ns2)
        self._lock = threading.Lock()

    def _register(self, key: str, namespace: str) -> None:
        """Enregistre une clé et vérifie les collisions."""
        with self._lock:
            if key in self._keys:
                existing_ns = self._keys[key]
                if existing_ns != namespace:
                    self._collisions.append((key, existing_ns, namespace))
                    logger.warning(
                        "Collision clé widget '%s': namespace '%s' vs '%s'",
                        key,
                        existing_ns,
                        namespace,
                    )
            else:
                self._keys[key] = namespace

    def has_collisions(self) -> bool:
        """Vérifie si des collisions ont été détectées."""
        return bool(self._collisions)

    @property
    def collisions(self) -> list[tuple[str, str, str]]:
        """Retourne la liste des collisions (key, ns1, ns2)."""
        return list(self._collisions)

    @property
    def registered_count(self) -> int:
        """Nombre de clés enregistrées."""
        return len(self._keys)

    def report(self) -> str:
        """Génère un rapport texte des collisions détectées.

        Returns:
            Rapport formaté ou message de succès si aucune collision
        """
        if not self._collisions:
            return f"✅ Aucune collision — {len(self._keys)} clés enregistrées"

        lines = [
            f"⚠️ {len(self._collisions)} collision(s) détectée(s):",
            "",
        ]
        for key, ns1, ns2 in self._collisions:
            lines.append(f"  • '{key}': '{ns1}' ↔ '{ns2}'")

        return "\n".join(lines)

    def reset(self) -> None:
        """Réinitialise le registre (utile pour les tests)."""
        with self._lock:
            self._keys.clear()
            self._collisions.clear()

    def keys_for_namespace(self, namespace: str) -> list[str]:
        """Retourne toutes les clés d'un namespace donné."""
        return [k for k, ns in self._keys.items() if ns == namespace]

    def __repr__(self) -> str:
        return f"_WidgetKeyRegistry(keys={len(self._keys)}, collisions={len(self._collisions)})"


# ═══════════════════════════════════════════════════════════
# SINGLETON
# ═══════════════════════════════════════════════════════════

widget_keys = _WidgetKeyRegistry()
"""Registre global des clés de widgets Streamlit."""
