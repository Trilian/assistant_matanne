"""
Service d'authentification Supabase.

Fonctionnalités:
- Inscription/Connexion utilisateurs
- Gestion des sessions (via SessionMixin)
- Validation JWT (via TokenValidationMixin)
- Profils utilisateurs (via ProfileMixin)
- Récupération mot de passe
- Rôles et permissions (via PermissionsMixin)

Note: Les enums/schémas sont dans auth_schemas.py,
la logique de permissions dans auth_permissions.py,
la session dans auth_session.py, les tokens dans auth_token.py,
le profil dans auth_profile.py.
"""

import logging
from collections.abc import MutableMapping
from datetime import datetime
from typing import Any

# Ré-exports pour rétrocompatibilité
from .auth_permissions import ROLE_PERMISSIONS, PermissionsMixin
from .auth_profile import ProfileMixin
from .auth_schemas import AuthResult, Permission, Role, UserProfile
from .auth_session import SessionMixin
from .auth_token import TokenValidationMixin

logger = logging.getLogger(__name__)


# -----------------------------------------------------------
# SERVICE D'AUTHENTIFICATION
# -----------------------------------------------------------


class AuthService(PermissionsMixin, SessionMixin, TokenValidationMixin, ProfileMixin):
    """
    Service d'authentification utilisant Supabase Auth.

    Gère:
    - Inscription/Connexion
    - Sessions persistantes (SessionMixin)
    - Validation JWT (TokenValidationMixin)
    - Profils utilisateurs (ProfileMixin)
    - Permissions (PermissionsMixin)
    """

    SESSION_KEY = "_auth_session"
    USER_KEY = "_auth_user"

    def __init__(self, storage: MutableMapping[str, Any] | None = None):
        """Initialise le service avec le client Supabase.

        Args:
            storage: Stockage clé-valeur mutable (défaut: st.session_state).
        """
        from src.core.storage import obtenir_session_state

        self._storage = storage if storage is not None else obtenir_session_state()
        self._client = None
        self._init_client()

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
# FACTORY
# -----------------------------------------------------------


from src.services.core.registry import service_factory


@service_factory("authentification", tags={"utilisateur", "auth"})
def obtenir_service_authentification() -> AuthService:
    """Factory pour le service d'authentification (thread-safe via registre)."""
    return AuthService()


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
    "SessionMixin",
    "TokenValidationMixin",
    "ProfileMixin",
]
