"""
Service d'authentification Supabase.

Fonctionnalités:
- Inscription/Connexion utilisateurs
- Gestion des sessions
- Récupération mot de passe
- Profils utilisateurs
- Rôles et permissions
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

import streamlit as st
from pydantic import BaseModel, EmailStr, Field

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# TYPES ET SCHÉMAS
# ═══════════════════════════════════════════════════════════


class Role(str, Enum):
    """Rôles utilisateur."""
    ADMIN = "admin"
    MEMBRE = "membre"
    INVITE = "invite"


class Permission(str, Enum):
    """Permissions granulaires."""
    READ_RECIPES = "read_recipes"
    WRITE_RECIPES = "write_recipes"
    DELETE_RECIPES = "delete_recipes"
    READ_INVENTORY = "read_inventory"
    WRITE_INVENTORY = "write_inventory"
    READ_PLANNING = "read_planning"
    WRITE_PLANNING = "write_planning"
    MANAGE_USERS = "manage_users"
    ADMIN_ALL = "admin_all"


ROLE_PERMISSIONS = {
    Role.ADMIN: [p for p in Permission],  # Toutes les permissions
    Role.MEMBRE: [
        Permission.READ_RECIPES, Permission.WRITE_RECIPES,
        Permission.READ_INVENTORY, Permission.WRITE_INVENTORY,
        Permission.READ_PLANNING, Permission.WRITE_PLANNING,
    ],
    Role.INVITE: [
        Permission.READ_RECIPES,
        Permission.READ_INVENTORY,
        Permission.READ_PLANNING,
    ],
}


class UserProfile(BaseModel):
    """Profil utilisateur."""
    
    id: str = ""
    email: str = ""
    nom: str = ""
    prenom: str = ""
    role: Role = Role.MEMBRE
    avatar_url: str | None = None
    preferences: dict = Field(default_factory=dict)
    created_at: datetime | None = None
    last_login: datetime | None = None
    
    def has_permission(self, permission: Permission) -> bool:
        """Vérifie si l'utilisateur a une permission."""
        return permission in ROLE_PERMISSIONS.get(self.role, [])
    
    @property
    def display_name(self) -> str:
        """Nom d'affichage."""
        if self.prenom and self.nom:
            return f"{self.prenom} {self.nom}"
        return self.email.split("@")[0] if self.email else "Utilisateur"


class AuthResult(BaseModel):
    """Résultat d'une opération d'authentification."""
    
    success: bool = False
    user: UserProfile | None = None
    message: str = ""
    error_code: str | None = None


# ═══════════════════════════════════════════════════════════
# SERVICE D'AUTHENTIFICATION
# ═══════════════════════════════════════════════════════════


class AuthService:
    """
    Service d'authentification utilisant Supabase Auth.
    
    Gère:
    - Inscription/Connexion
    - Sessions persistantes
    - Profils utilisateurs
    - Permissions
    """
    
    SESSION_KEY = "_auth_session"
    USER_KEY = "_auth_user"
    
    def __init__(self):
        """Initialise le service avec le client Supabase."""
        self._client = None
        self._init_client()
    
    def _init_client(self):
        """Initialise le client Supabase."""
        try:
            from supabase import create_client, Client
            from src.core.config import obtenir_parametres
            
            params = obtenir_parametres()
            
            # Vérifier les variables d'environnement requises
            supabase_url = getattr(params, 'SUPABASE_URL', None)
            supabase_key = getattr(params, 'SUPABASE_ANON_KEY', None)
            
            if not supabase_url or not supabase_key:
                logger.warning("Variables Supabase non configurées (SUPABASE_URL, SUPABASE_ANON_KEY)")
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
    
    # ═══════════════════════════════════════════════════════════
    # INSCRIPTION
    # ═══════════════════════════════════════════════════════════
    
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
                error_code="NOT_CONFIGURED"
            )
        
        try:
            # Inscription via Supabase Auth
            response = self._client.auth.sign_up({
                "email": email,
                "password": password,
                "options": {
                    "data": {
                        "nom": nom,
                        "prenom": prenom,
                        "role": Role.MEMBRE.value,
                    }
                }
            })
            
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
                    message="Inscription réussie! Vérifiez votre email."
                )
            
            return AuthResult(
                success=False,
                message="Erreur lors de l'inscription"
            )
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Erreur inscription: {error_msg}")
            
            # Messages d'erreur plus clairs
            if "already registered" in error_msg.lower():
                return AuthResult(
                    success=False,
                    message="Cet email est déjà utilisé",
                    error_code="EMAIL_EXISTS"
                )
            
            return AuthResult(
                success=False,
                message=f"Erreur: {error_msg}",
                error_code="SIGNUP_ERROR"
            )
    
    # ═══════════════════════════════════════════════════════════
    # CONNEXION
    # ═══════════════════════════════════════════════════════════
    
    def login(self, email: str, password: str) -> AuthResult:
        """
        Connecte un utilisateur.
        
        Args:
            email: Adresse email
            password: Mot de passe
            
        Returns:
            Résultat de la connexion
        """
        if not self.is_configured:
            return AuthResult(
                success=False,
                message="Service d'authentification non configuré",
                error_code="NOT_CONFIGURED"
            )
        
        try:
            response = self._client.auth.sign_in_with_password({
                "email": email,
                "password": password,
            })
            
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
                
                return AuthResult(
                    success=True,
                    user=user,
                    message="Connexion réussie!"
                )
            
            return AuthResult(
                success=False,
                message="Identifiants incorrects"
            )
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Erreur connexion: {error_msg}")
            
            if "invalid" in error_msg.lower():
                return AuthResult(
                    success=False,
                    message="Email ou mot de passe incorrect",
                    error_code="INVALID_CREDENTIALS"
                )
            
            return AuthResult(
                success=False,
                message=f"Erreur de connexion",
                error_code="LOGIN_ERROR"
            )
    
    # ═══════════════════════════════════════════════════════════
    # DÉCONNEXION
    # ═══════════════════════════════════════════════════════════
    
    def logout(self) -> AuthResult:
        """Déconnecte l'utilisateur actuel."""
        if not self.is_configured:
            return AuthResult(success=True, message="Déconnecté")
        
        try:
            self._client.auth.sign_out()
            self._clear_session()
            
            logger.info("Utilisateur déconnecté")
            
            return AuthResult(
                success=True,
                message="Déconnexion réussie"
            )
            
        except Exception as e:
            logger.error(f"Erreur déconnexion: {e}")
            self._clear_session()  # Nettoyer quand même
            return AuthResult(success=True, message="Déconnecté")
    
    # ═══════════════════════════════════════════════════════════
    # MOT DE PASSE OUBLIÉ
    # ═══════════════════════════════════════════════════════════
    
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
                success=False,
                message="Service non configuré",
                error_code="NOT_CONFIGURED"
            )
        
        try:
            self._client.auth.reset_password_for_email(email)
            
            logger.info(f"Email de reset envoyé à: {email}")
            
            return AuthResult(
                success=True,
                message="Si cet email existe, vous recevrez un lien de réinitialisation."
            )
            
        except Exception as e:
            logger.error(f"Erreur reset password: {e}")
            return AuthResult(
                success=True,  # Ne pas révéler si l'email existe
                message="Si cet email existe, vous recevrez un lien de réinitialisation."
            )
    
    # ═══════════════════════════════════════════════════════════
    # SESSION
    # ═══════════════════════════════════════════════════════════
    
    def get_current_user(self) -> UserProfile | None:
        """Retourne l'utilisateur actuellement connecté."""
        return st.session_state.get(self.USER_KEY)
    
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
    
    def require_permission(self, permission: Permission) -> bool:
        """
        Vérifie si l'utilisateur a une permission.
        
        Args:
            permission: Permission requise
            
        Returns:
            True si autorisé
        """
        user = self.get_current_user()
        
        if not user:
            return False
        
        return user.has_permission(permission)
    
    def _save_session(self, session: Any, user: UserProfile):
        """Sauvegarde la session."""
        st.session_state[self.SESSION_KEY] = session
        st.session_state[self.USER_KEY] = user
    
    def _clear_session(self):
        """Efface la session."""
        if self.SESSION_KEY in st.session_state:
            del st.session_state[self.SESSION_KEY]
        if self.USER_KEY in st.session_state:
            del st.session_state[self.USER_KEY]
    
    def refresh_session(self) -> bool:
        """
        Rafraîchit la session si nécessaire.
        
        Returns:
            True si session valide
        """
        if not self.is_configured:
            return False
        
        try:
            session = st.session_state.get(self.SESSION_KEY)
            
            if session:
                # Vérifier et rafraîchir le token
                response = self._client.auth.get_session()
                
                if response:
                    return True
            
            return False
            
        except Exception as e:
            logger.debug(f"Session refresh: {e}")
            return False
    
    # ═══════════════════════════════════════════════════════════
    # VALIDATION JWT (pour API REST)
    # ═══════════════════════════════════════════════════════════
    
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
            parts = token.split('.')
            if len(parts) != 3:
                return None
            
            # Décoder le payload (partie 2)
            payload = parts[1]
            # Ajouter padding si nécessaire
            payload += '=' * (4 - len(payload) % 4)
            decoded = base64.urlsafe_b64decode(payload)
            
            return json.loads(decoded)
            
        except Exception as e:
            logger.debug(f"Erreur décodage JWT: {e}")
            return None
    
    # ═══════════════════════════════════════════════════════════
    # MISE À JOUR PROFIL
    # ═══════════════════════════════════════════════════════════
    
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
                success=False,
                message="Service non configuré",
                error_code="NOT_CONFIGURED"
            )
        
        user = self.get_current_user()
        if not user:
            return AuthResult(
                success=False,
                message="Non connecté",
                error_code="NOT_AUTHENTICATED"
            )
        
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
                return AuthResult(
                    success=True,
                    message="Aucune modification",
                    user=user
                )
            
            # Mettre à jour via Supabase Auth
            response = self._client.auth.update_user({
                "data": update_data
            })
            
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
                st.session_state[self.USER_KEY] = updated_user
                
                logger.info(f"Profil mis à jour: {user.email}")
                
                return AuthResult(
                    success=True,
                    message="Profil mis à jour avec succès",
                    user=updated_user
                )
            
            return AuthResult(
                success=False,
                message="Erreur lors de la mise à jour"
            )
            
        except Exception as e:
            logger.error(f"Erreur update profile: {e}")
            return AuthResult(
                success=False,
                message=f"Erreur: {str(e)}",
                error_code="UPDATE_ERROR"
            )
    
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
            return AuthResult(
                success=False,
                message="Mot de passe trop court (min 6 caractères)"
            )
        
        try:
            response = self._client.auth.update_user({
                "password": new_password
            })
            
            if response:
                logger.info("Mot de passe changé")
                return AuthResult(
                    success=True,
                    message="Mot de passe changé avec succès"
                )
            
            return AuthResult(success=False, message="Erreur lors du changement")
            
        except Exception as e:
            logger.error(f"Erreur changement mot de passe: {e}")
            return AuthResult(success=False, message=f"Erreur: {str(e)}")


# ═══════════════════════════════════════════════════════════
# COMPOSANTS UI
# ═══════════════════════════════════════════════════════════


def render_login_form(redirect_on_success: bool = True):
    """
    Affiche le formulaire de connexion.
    
    Args:
        redirect_on_success: Rerun après connexion réussie
    """
    auth = get_auth_service()
    
    st.markdown("### 🔐 Connexion")
    
    tab1, tab2 = st.tabs(["Se connecter", "S'inscrire"])
    
    with tab1:
        with st.form("login_form"):
            email = st.text_input("Email", placeholder="votre@email.com")
            password = st.text_input("Mot de passe", type="password")
            
            col1, col2 = st.columns([2, 1])
            with col1:
                submit = st.form_submit_button("Se connecter", use_container_width=True)
            with col2:
                forgot = st.form_submit_button("Mot de passe oublié?")
            
            if submit and email and password:
                result = auth.login(email, password)
                
                if result.success:
                    st.success(result.message)
                    if redirect_on_success:
                        st.rerun()
                else:
                    st.error(result.message)
            
            if forgot and email:
                result = auth.reset_password(email)
                st.info(result.message)
    
    with tab2:
        with st.form("signup_form"):
            email = st.text_input("Email", key="signup_email")
            col1, col2 = st.columns(2)
            with col1:
                prenom = st.text_input("Prénom")
            with col2:
                nom = st.text_input("Nom")
            password = st.text_input("Mot de passe", type="password", key="signup_pass")
            password2 = st.text_input("Confirmer mot de passe", type="password")
            
            submit = st.form_submit_button("S'inscrire", use_container_width=True)
            
            if submit:
                if not email or not password:
                    st.error("Email et mot de passe requis")
                elif password != password2:
                    st.error("Les mots de passe ne correspondent pas")
                elif len(password) < 6:
                    st.error("Mot de passe trop court (min 6 caractères)")
                else:
                    result = auth.signup(email, password, nom, prenom)
                    
                    if result.success:
                        st.success(result.message)
                    else:
                        st.error(result.message)


def render_user_menu():
    """Affiche le menu utilisateur dans la sidebar."""
    auth = get_auth_service()
    user = auth.get_current_user()
    
    if user:
        with st.sidebar:
            st.markdown("---")
            
            col1, col2 = st.columns([1, 3])
            with col1:
                st.markdown("👤")
            with col2:
                st.markdown(f"**{user.display_name}**")
                st.caption(user.role.value.title())
            
            if st.button("🚪 Déconnexion", use_container_width=True, key="logout_btn"):
                auth.logout()
                st.rerun()
    else:
        with st.sidebar:
            st.markdown("---")
            if st.button("🔐 Se connecter", use_container_width=True, key="login_btn"):
                st.session_state["show_login"] = True


def render_profile_settings():
    """Affiche les paramètres du profil utilisateur."""
    auth = get_auth_service()
    user = auth.get_current_user()
    
    if not user:
        st.warning("Vous devez être connecté")
        return
    
    st.markdown("### 👤 Mon profil")
    
    # Formulaire de mise à jour du profil
    with st.form("profile_form"):
        prenom = st.text_input("Prénom", value=user.prenom)
        nom = st.text_input("Nom", value=user.nom)
        avatar_url = st.text_input("URL Avatar", value=user.avatar_url or "", help="URL d'une image pour votre avatar")
        
        st.markdown("---")
        st.caption(f"📧 Email: {user.email}")
        st.caption(f"🏷️ Rôle: {user.role.value.title()}")
        st.caption(f"📅 Membre depuis: {user.created_at.strftime('%d/%m/%Y') if user.created_at else 'N/A'}")
        
        if st.form_submit_button("💾 Enregistrer les modifications", use_container_width=True, type="primary"):
            result = auth.update_profile(
                nom=nom if nom != user.nom else None,
                prenom=prenom if prenom != user.prenom else None,
                avatar_url=avatar_url if avatar_url != user.avatar_url else None,
            )
            
            if result.success:
                st.success(f"✅ {result.message}")
                st.rerun()
            else:
                st.error(f"❌ {result.message}")
    
    # Section changement de mot de passe
    st.markdown("---")
    st.markdown("### 🔒 Changer le mot de passe")
    
    with st.form("password_form"):
        new_password = st.text_input("Nouveau mot de passe", type="password", key="new_pwd")
        confirm_password = st.text_input("Confirmer le mot de passe", type="password", key="confirm_pwd")
        
        if st.form_submit_button("🔐 Changer le mot de passe", use_container_width=True):
            if not new_password:
                st.error("Veuillez entrer un nouveau mot de passe")
            elif new_password != confirm_password:
                st.error("Les mots de passe ne correspondent pas")
            elif len(new_password) < 6:
                st.error("Mot de passe trop court (min 6 caractères)")
            else:
                result = auth.change_password(new_password)
                if result.success:
                    st.success(f"✅ {result.message}")
                else:
                    st.error(f"❌ {result.message}")


# ═══════════════════════════════════════════════════════════
# DÉCORATEURS DE PERMISSION
# ═══════════════════════════════════════════════════════════


def require_authenticated(func):
    """Décorateur qui exige une authentification."""
    from functools import wraps
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        auth = get_auth_service()
        
        if not auth.is_authenticated():
            st.warning("🔐 Authentification requise")
            render_login_form()
            return None
        
        return func(*args, **kwargs)
    
    return wrapper


def require_role(role: Role):
    """Décorateur qui exige un rôle minimum."""
    def decorator(func):
        from functools import wraps
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            auth = get_auth_service()
            user = auth.get_current_user()
            
            if not user:
                st.warning("🔐 Authentification requise")
                render_login_form()
                return None
            
            # Hiérarchie des rôles
            role_hierarchy = [Role.INVITE, Role.MEMBRE, Role.ADMIN]
            
            if role_hierarchy.index(user.role) < role_hierarchy.index(role):
                st.error(f"⛔ Accès refusé. Rôle requis: {role.value}")
                return None
            
            return func(*args, **kwargs)
        
        return wrapper
    return decorator


# ═══════════════════════════════════════════════════════════
# FACTORY
# ═══════════════════════════════════════════════════════════


_auth_service: AuthService | None = None


def get_auth_service() -> AuthService:
    """Factory pour le service d'authentification."""
    global _auth_service
    if _auth_service is None:
        _auth_service = AuthService()
    return _auth_service


__all__ = [
    "AuthService",
    "get_auth_service",
    "UserProfile",
    "AuthResult",
    "Role",
    "Permission",
    "render_login_form",
    "render_user_menu",
    "render_profile_settings",
    "require_authenticated",
    "require_role",
]
