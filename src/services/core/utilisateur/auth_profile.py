"""
Mixin de gestion du profil utilisateur.

Fournit la mise à jour du profil et le changement de mot de passe
via l'API Supabase Auth.

Dépendances attendues sur ``self``
-----------------------------------
- ``self._storage``    : ``MutableMapping[str, Any]`` — magasin de session
- ``self._client``     : client Supabase (peut être ``None``)
- ``self.USER_KEY``    : clé de stockage du ``ProfilUtilisateur``
- ``self.is_configured``: propriété indiquant si le client est actif
- ``self.get_current_user()`` : méthode retournant le ``ProfilUtilisateur`` courant
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from .auth_schemas import AuthResult, ProfilUtilisateur, Role

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


class ProfileMixin:
    """Mixin fournissant la gestion du profil et du mot de passe."""

    def update_profile(
        self,
        nom: str | None = None,
        prenom: str | None = None,
        avatar_url: str | None = None,
        preferences: dict | None = None,
    ) -> AuthResult:
        """
        Met à jour le profil de l'utilisateur connecté.

        Args:
            nom: Nouveau nom (optionnel)
            prenom: Nouveau prénom (optionnel)
            avatar_url: URL de l'avatar (optionnel)
            preferences: Préférences utilisateur (optionnel)

        Returns:
            Résultat de la mise à jour
        """
        if not self.is_configured:
            return AuthResult(
                success=False, message="Service non configuré", error_code="NOT_CONFIGURED"
            )

        user = self.get_current_user()
        if not user:
            return AuthResult(success=False, message="Non connecté", error_code="NOT_AUTHENTICATED")

        try:
            # Construire les données à mettre à jour
            update_data: dict = {}

            if nom is not None:
                update_data["nom"] = nom
            if prenom is not None:
                update_data["prenom"] = prenom
            if avatar_url is not None:
                update_data["avatar_url"] = avatar_url
            if preferences is not None:
                update_data["preferences"] = preferences

            if not update_data:
                return AuthResult(success=True, message="Aucune modification", user=user)

            # Mettre à jour via Supabase Auth
            response = self._client.auth.update_user({"data": update_data})

            if response and response.user:
                # Mettre à jour le profil local
                metadata = response.user.user_metadata or {}

                updated_user = ProfilUtilisateur(
                    id=response.user.id,
                    email=response.user.email or user.email,
                    nom=metadata.get("nom", user.nom),
                    prenom=metadata.get("prenom", user.prenom),
                    role=Role(metadata.get("role", user.role.value)),
                    avatar_url=metadata.get("avatar_url", user.avatar_url),
                    preferences=metadata.get("preferences", {}),
                    last_login=user.last_login,
                    created_at=user.created_at,
                )

                # Mettre à jour la session
                self._storage[self.USER_KEY] = updated_user

                logger.info(f"Profil mis à jour: {user.email}")

                return AuthResult(
                    success=True,
                    message="Profil mis à jour avec succès",
                    user=updated_user,
                )

            return AuthResult(success=False, message="Erreur lors de la mise à jour")

        except Exception as e:
            logger.error(f"Erreur update profile: {e}")
            return AuthResult(success=False, message=f"Erreur: {str(e)}", error_code="UPDATE_ERROR")

    def change_password(self, new_password: str) -> AuthResult:
        """
        Change le mot de passe de l'utilisateur connecté.

        Args:
            new_password: Nouveau mot de passe (min 6 caractères)

        Returns:
            Résultat du changement
        """
        if not self.is_configured:
            return AuthResult(success=False, message="Service non configuré")

        if len(new_password) < 6:
            return AuthResult(success=False, message="Mot de passe trop court (min 6 caractères)")

        try:
            response = self._client.auth.update_user({"password": new_password})

            if response:
                logger.info("Mot de passe changé")
                return AuthResult(success=True, message="Mot de passe changé avec succès")

            return AuthResult(success=False, message="Erreur lors du changement")

        except Exception as e:
            logger.error(f"Erreur changement mot de passe: {e}")
            return AuthResult(success=False, message=f"Erreur: {str(e)}")
