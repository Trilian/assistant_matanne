"""
Mixin de gestion des sessions d'authentification.

Gère la persistance de la session utilisateur dans un stockage
clé-valeur mutable (par défaut ``st.session_state``).

Dépendances attendues sur ``self``
-----------------------------------
- ``self._storage``  : ``MutableMapping[str, Any]`` — magasin de session
- ``self._client``   : client Supabase (peut être ``None``)
- ``self.SESSION_KEY``: clé de stockage de la session Supabase
- ``self.USER_KEY``  : clé de stockage du ``ProfilUtilisateur``
- ``self.is_configured``: propriété indiquant si le client est actif
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .auth_schemas import ProfilUtilisateur

logger = logging.getLogger(__name__)


class SessionMixin:
    """Mixin fournissant la gestion des sessions d'authentification."""

    # -----------------------------------------------------------
    # Sauvegarde / nettoyage
    # -----------------------------------------------------------

    def _save_session(self, session: Any, user: ProfilUtilisateur) -> None:
        """Sauvegarde la session et le profil utilisateur dans le stockage."""
        self._storage[self.SESSION_KEY] = session
        self._storage[self.USER_KEY] = user

    def _clear_session(self) -> None:
        """Efface la session et le profil utilisateur du stockage."""
        if self.SESSION_KEY in self._storage:
            del self._storage[self.SESSION_KEY]
        if self.USER_KEY in self._storage:
            del self._storage[self.USER_KEY]

    # -----------------------------------------------------------
    # Lecture / vérification
    # -----------------------------------------------------------

    def get_current_user(self) -> ProfilUtilisateur | None:
        """Retourne l'utilisateur actuellement connecté."""
        return self._storage.get(self.USER_KEY)

    def is_authenticated(self) -> bool:
        """Vérifie si un utilisateur est connecté."""
        return self.get_current_user() is not None

    def require_auth(self) -> ProfilUtilisateur | None:
        """
        Exige une authentification.

        Affiche le formulaire de connexion si non authentifié.

        Returns:
            Utilisateur si authentifié, None sinon
        """
        user = self.get_current_user()

        if user:
            return user

        # Import paresseux — ne pas charger Streamlit au niveau module
        from src.ui.views.authentification import afficher_formulaire_connexion

        afficher_formulaire_connexion()
        return None

    # -----------------------------------------------------------
    # Rafraîchissement
    # -----------------------------------------------------------

    def refresh_session(self) -> bool:
        """
        Rafraîchit la session si nécessaire.

        Returns:
            True si session valide
        """
        if not self.is_configured:
            return False

        try:
            session = self._storage.get(self.SESSION_KEY)

            if session:
                # Vérifier et rafraîchir le token
                response = self._client.auth.obtenir_contexte_db()

                if response:
                    return True

            return False

        except Exception as e:
            logger.debug(f"Session refresh: {e}")
            return False
