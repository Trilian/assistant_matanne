"""
Service d'authentification Supabase.

Fonctionnalités:
- Inscription/Connexion utilisateurs
- Gestion des sessions
- Récupération mot de passe
- Profils utilisateurs
- Rôles et permissions

Note: Les enums/schémas sont dans auth_schemas.py,
la logique de permissions dans auth_permissions.py.
"""

import logging
from collections.abc import MutableMapping
from datetime import datetime
from typing import Any

# Ré-exports pour rétrocompatibilité
from .auth_permissions import ROLE_PERMISSIONS, PermissionsMixin
from .auth_schemas import AuthResult, Permission, Role, UserProfile

logger = logging.getLogger(__name__)


# -----------------------------------------------------------
# SERVICE D'AUTHENTIFICATION
# -----------------------------------------------------------


class AuthService(PermissionsMixin):
    """
    Service d'authentification utilisant Supabase Auth.

    Gère:
    - Inscription/Connexion
    - Sessions persistantes
    - Profils utilisateurs
    - Permissions (via PermissionsMixin)
    """

    SESSION_KEY = "_auth_session"
    USER_KEY = "_auth_user"

    def __init__(self, storage: MutableMapping[str, Any] | None = None):
        """Initialise le service avec le client Supabase.

        Args:
            storage: Stockage clé-valeur mutable (défaut: st.session_state).
        """
        self._storage = storage if storage is not None else self._get_default_storage()
        self._client = None
        self._init_client()

    @staticmethod
    def _get_default_storage() -> MutableMapping[str, Any]:
        """Retourne le stockage par défaut (st.session_state)."""
        import streamlit as st

        return st.session_state

    def _init_client(self):
        """Initialise le client Supabase."""
        try:
            from supabase import create_client

            from src.core.config import obtenir_parametres

            params = obtenir_parametres()

            # Vérifier les variables d'environnement requises
            supabase_url = getattr(params, "SUPABASE_URL", None)
            supabase_key = getattr(params, "SUPABASE_ANON_KEY", None)

            if not supabase_url or not supabase_key:
                logger.warning(
                    "Variables Supabase non configurées (SUPABASE_URL, SUPABASE_ANON_KEY)"
                )
                return

            self._client = create_client(supabase_url, supabase_key)
            logger.info("✅ Client Supabase Auth initialisé")

        except ImportError:
            logger.warning("Package supabase non installé: pip install supabase")
        except Exception as e:
            logger.error(f"Erreur initialisation Supabase: {e}")

    @property
    def is_configured(self) -> bool:
        """Vérifie si Supabase est configuré."""
        return self._client is not None

    # -----------------------------------------------------------
    # INSCRIPTION
    # -----------------------------------------------------------

    def signup(
        self,
        email: str,
        password: str,
        nom: str = "",
        prenom: str = "",
    ) -> AuthResult:
        """
        Inscrit un nouvel utilisateur.

        Args:
            email: Adresse email
            password: Mot de passe (min 6 caractères)
            nom: Nom de famille
            prenom: Prénom

        Returns:
            Résultat de l'inscription
        """
        if not self.is_configured:
            return AuthResult(
                success=False,
                message="Service d'authentification non configuré",
                error_code="NOT_CONFIGURED",
            )

        try:
            # Inscription via Supabase Auth
            response = self._client.auth.sign_up(
                {
                    "email": email,
                    "password": password,
                    "options": {
                        "data": {
                            "nom": nom,
                            "prenom": prenom,
                            "role": Role.MEMBRE.value,
                        }
                    },
                }
            )

            if response.user:
                # Créer le profil
                user = UserProfile(
                    id=response.user.id,
                    email=email,
                    nom=nom,
                    prenom=prenom,
                    role=Role.MEMBRE,
                    created_at=datetime.now(),
                )

                # Sauvegarder en session
                self._save_session(response.session, user)

                logger.info(f"Nouvel utilisateur inscrit: {email}")

                return AuthResult(
                    success=True,
                    user=user,
                    message="Inscription réussie! Vérifiez votre email.",
                )

            return AuthResult(success=False, message="Erreur lors de l'inscription")

        except Exception as e:
            error_msg = str(e)
            logger.error(f"Erreur inscription: {error_msg}")

            # Messages d'erreur plus clairs
            if "already registered" in error_msg.lower():
                return AuthResult(
                    success=False,
                    message="Cet email est déjà utilisé",
                    error_code="EMAIL_EXISTS",
                )

            return AuthResult(
                success=False, message=f"Erreur: {error_msg}", error_code="SIGNUP_ERROR"
            )

    # -----------------------------------------------------------
    # CONNEXION
    # -----------------------------------------------------------

    def login(self, email: str, password: str) -> AuthResult:
        """
        Connecte un utilisateur.

        Args:
            email: Adresse email
            password: Mot de passe

        Returns:
            Résultat de la connexion
        """
        # Mode DÉMO - Permet la connexion sans Supabase en développement
        if not self.is_configured:
            logger.warning("⚠️ Mode démo: Authentification Supabase non configurée")

            # Comptes de démonstration disponibles
            DEMO_ACCOUNTS = {
                "anne@matanne.fr": "password123",  # Admin
                "demo@test.fr": "password123",  # Membre
                "test@test.fr": "password123",  # Invité
            }

            # Vérifier si c'est un compte démo valide
            if email in DEMO_ACCOUNTS and DEMO_ACCOUNTS[email] == password:
                # Créer un profil de test
                roles_map = {
                    "anne@matanne.fr": Role.ADMIN,
                    "demo@test.fr": Role.MEMBRE,
                    "test@test.fr": Role.INVITE,
                }

                nom_parts = email.split("@")[0].split(".")
                prenom = nom_parts[0].capitalize()
                nom = nom_parts[1].capitalize() if len(nom_parts) > 1 else "Test"

                user = UserProfile(
                    id=email.replace("@", "_").replace(".", "_"),
                    email=email,
                    nom=nom,
                    prenom=prenom,
                    role=roles_map.get(email, Role.MEMBRE),
                    display_name=f"{prenom} {nom}",
                    created_at=datetime.now(),
                )

                # Sauvegarder en session
                self._storage[self.USER_KEY] = user
                logger.info(f"✅ Connexion démo réussie: {email} ({user.role.value})")

                return AuthResult(
                    success=True, user=user, message=f"Bienvenue {prenom}! (Mode démo)"
                )

            return AuthResult(
                success=False,
                message="⚠️ Mode démo: Utilisez anne@matanne.fr / password123 (ou demo@test.fr / password123)",
                error_code="DEMO_MODE",
            )

        # Mode NORMAL - Authentification via Supabase
        try:
            response = self._client.auth.sign_in_with_password(
                {
                    "email": email,
                    "password": password,
                }
            )

            if response.user:
                # Construire le profil
                metadata = response.user.user_metadata or {}

                user = UserProfile(
                    id=response.user.id,
                    email=response.user.email,
                    nom=metadata.get("nom", ""),
                    prenom=metadata.get("prenom", ""),
                    role=Role(metadata.get("role", "membre")),
                    avatar_url=metadata.get("avatar_url"),
                    last_login=datetime.now(),
                )

                # Sauvegarder en session
                self._save_session(response.session, user)

                logger.info(f"Utilisateur connecté: {email}")

                return AuthResult(success=True, user=user, message="Connexion réussie!")

            return AuthResult(success=False, message="Identifiants incorrects")

        except Exception as e:
            error_msg = str(e)
            logger.error(f"Erreur connexion: {error_msg}")

            if "invalid" in error_msg.lower():
                return AuthResult(
                    success=False,
                    message="Email ou mot de passe incorrect",
                    error_code="INVALID_CREDENTIALS",
                )

            return AuthResult(
                success=False, message="Erreur de connexion", error_code="LOGIN_ERROR"
            )

    # -----------------------------------------------------------
    # DÉCONNEXION
    # -----------------------------------------------------------

    def logout(self) -> AuthResult:
        """Déconnecte l'utilisateur actuel."""
        if not self.is_configured:
            return AuthResult(success=True, message="Déconnecté")

        try:
            self._client.auth.sign_out()
            self._clear_session()

            logger.info("Utilisateur déconnecté")

            return AuthResult(success=True, message="Déconnexion réussie")

        except Exception as e:
            logger.error(f"Erreur déconnexion: {e}")
            self._clear_session()  # Nettoyer quand même
            return AuthResult(success=True, message="Déconnecté")

    # -----------------------------------------------------------
    # MOT DE PASSE OUBLIÉ
    # -----------------------------------------------------------

    def reset_password(self, email: str) -> AuthResult:
        """
        Envoie un email de réinitialisation de mot de passe.

        Args:
            email: Adresse email

        Returns:
            Résultat de l'opération
        """
        if not self.is_configured:
            return AuthResult(
                success=False, message="Service non configuré", error_code="NOT_CONFIGURED"
            )

        try:
            self._client.auth.reset_password_for_email(email)

            logger.info(f"Email de reset envoyé à: {email}")

            return AuthResult(
                success=True,
                message="Si cet email existe, vous recevrez un lien de réinitialisation.",
            )

        except Exception as e:
            logger.error(f"Erreur reset password: {e}")
            return AuthResult(
                success=True,  # Ne pas révéler si l'email existe
                message="Si cet email existe, vous recevrez un lien de réinitialisation.",
            )

    # -----------------------------------------------------------
    # SESSION
    # -----------------------------------------------------------

    def get_current_user(self) -> UserProfile | None:
        """Retourne l'utilisateur actuellement connecté."""
        return self._storage.get(self.USER_KEY)

    def is_authenticated(self) -> bool:
        """Vérifie si un utilisateur est connecté."""
        return self.get_current_user() is not None

    def require_auth(self) -> UserProfile | None:
        """
        Exige une authentification.

        Affiche le formulaire de connexion si non authentifié.

        Returns:
            Utilisateur si authentifié, None sinon
        """
        user = self.get_current_user()

        if user:
            return user

        # Afficher le formulaire de connexion
        render_login_form()
        return None

    def _save_session(self, session: Any, user: UserProfile):
        """Sauvegarde la session."""
        self._storage[self.SESSION_KEY] = session
        self._storage[self.USER_KEY] = user

    def _clear_session(self):
        """Efface la session."""
        if self.SESSION_KEY in self._storage:
            del self._storage[self.SESSION_KEY]
        if self.USER_KEY in self._storage:
            del self._storage[self.USER_KEY]

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

    # -----------------------------------------------------------
    # VALIDATION JWT (pour API REST)
    # -----------------------------------------------------------

    def validate_token(self, token: str) -> UserProfile | None:
        """
        Valide un token JWT Supabase et retourne l'utilisateur.

        Args:
            token: Token JWT Bearer

        Returns:
            UserProfile si valide, None sinon
        """
        if not self.is_configured:
            logger.warning("Auth non configuré pour validation JWT")
            return None

        try:
            # Utiliser l'API Supabase pour valider le token
            self._client.auth._storage_key = token  # Temporaire
            response = self._client.auth.get_user(token)

            if response and response.user:
                metadata = response.user.user_metadata or {}

                return UserProfile(
                    id=response.user.id,
                    email=response.user.email or "",
                    nom=metadata.get("nom", ""),
                    prenom=metadata.get("prenom", ""),
                    role=Role(metadata.get("role", "membre")),
                    avatar_url=metadata.get("avatar_url"),
                )

            return None

        except Exception as e:
            logger.error(f"Erreur validation token JWT: {e}")
            return None

    def decode_jwt_payload(self, token: str) -> dict | None:
        """
        Décode le payload d'un JWT sans validation signature.
        Utile pour debug ou extraction d'infos basiques.

        Args:
            token: Token JWT

        Returns:
            Payload décodé ou None
        """
        try:
            import base64
            import json

            # JWT = header.payload.signature
            parts = token.split(".")
            if len(parts) != 3:
                return None

            # Décoder le payload (partie 2)
            payload = parts[1]
            # Ajouter padding si nécessaire
            payload += "=" * (4 - len(payload) % 4)
            decoded = base64.urlsafe_b64decode(payload)

            return json.loads(decoded)

        except Exception as e:
            logger.debug(f"Erreur décodage JWT: {e}")
            return None

    # -----------------------------------------------------------
    # MISE À JOUR PROFIL
    # -----------------------------------------------------------

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
            update_data = {}

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

                updated_user = UserProfile(
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
                    success=True, message="Profil mis à jour avec succès", user=updated_user
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


# -----------------------------------------------------------
# COMPOSANTS UI — Rétrocompatibilité
# -----------------------------------------------------------
# Les fonctions UI ont été déplacées vers src.ui.views.authentification.
# Les wrappers ci-dessous préservent la rétrocompatibilité des imports.


def render_login_form(redirect_on_success: bool = True):  # pragma: no cover
    """Wrapper rétrocompat — délègue à src.ui.views.authentification."""
    from src.ui.views.authentification import afficher_formulaire_connexion

    return afficher_formulaire_connexion(rediriger_apres_succes=redirect_on_success)


def render_user_menu():  # pragma: no cover
    """Wrapper rétrocompat — délègue à src.ui.views.authentification."""
    from src.ui.views.authentification import afficher_menu_utilisateur

    return afficher_menu_utilisateur()


def render_profile_settings():  # pragma: no cover
    """Wrapper rétrocompat — délègue à src.ui.views.authentification."""
    from src.ui.views.authentification import afficher_parametres_profil

    return afficher_parametres_profil()


def require_authenticated(func):  # pragma: no cover
    """Wrapper rétrocompat — délègue à src.ui.views.authentification."""
    from src.ui.views.authentification import require_authenticated as _require_authenticated

    return _require_authenticated(func)


def require_role(role: Role):  # pragma: no cover
    """Wrapper rétrocompat — délègue à src.ui.views.authentification."""
    from src.ui.views.authentification import require_role as _require_role

    return _require_role(role)


# -----------------------------------------------------------
# FACTORY
# -----------------------------------------------------------


_auth_service: AuthService | None = None


def obtenir_service_authentification() -> AuthService:
    """Factory pour le service d'authentification (convention française)."""
    global _auth_service
    if _auth_service is None:
        _auth_service = AuthService()
    return _auth_service


def get_auth_service() -> AuthService:
    """Factory pour le service d'authentification (alias anglais)."""
    return obtenir_service_authentification()


__all__ = [
    "AuthService",
    "obtenir_service_authentification",
    "get_auth_service",
    "UserProfile",
    "AuthResult",
    "Role",
    "Permission",
    "ROLE_PERMISSIONS",
    "PermissionsMixin",
    "render_login_form",
    "render_user_menu",
    "render_profile_settings",
    "require_authenticated",
    "require_role",
]
