"""
Interface UI pour l'authentification et le profil utilisateur.

Note: Ce fichier a été extrait depuis src/services/utilisateur/authentification.py
pour respecter la séparation UI/Services.
"""

import streamlit as st

from src.services.core.utilisateur.authentification import (
    Role,
    get_auth_service,
)


def afficher_formulaire_connexion(rediriger_apres_succes: bool = True):
    """
    Affiche le formulaire de connexion.

    Args:
        rediriger_apres_succes: Rerun après connexion réussie
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
                    if rediriger_apres_succes:
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


def afficher_menu_utilisateur():
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


def afficher_parametres_profil():
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
        avatar_url = st.text_input(
            "URL Avatar",
            value=user.avatar_url or "",
            help="URL d'une image pour votre avatar",
        )

        st.markdown("---")
        st.caption(f"📧 Email: {user.email}")
        st.caption(f"🏆 Rôle: {user.role.value.title()}")
        st.caption(
            f"📅 Membre depuis: {user.created_at.strftime('%d/%m/%Y') if user.created_at else 'N/A'}"
        )

        if st.form_submit_button(
            "💾 Enregistrer les modifications", use_container_width=True, type="primary"
        ):
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
    st.markdown("### 🔐 Changer le mot de passe")

    with st.form("password_form"):
        new_password = st.text_input("Nouveau mot de passe", type="password", key="new_pwd")
        confirm_password = st.text_input(
            "Confirmer le mot de passe", type="password", key="confirm_pwd"
        )

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


def require_authenticated(func):
    """Décorateur qui exige une authentification."""
    from functools import wraps

    @wraps(func)
    def wrapper(*args, **kwargs):
        auth = get_auth_service()

        if not auth.is_authenticated():
            st.warning("🔐 Authentification requise")
            afficher_formulaire_connexion()
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
                afficher_formulaire_connexion()
                return None

            # Hiérarchie des rôles
            role_hierarchy = [Role.INVITE, Role.MEMBRE, Role.ADMIN]

            if role_hierarchy.index(user.role) < role_hierarchy.index(role):
                st.error(f"❌ Accès refusé. Rôle requis: {role.value}")
                return None

            return func(*args, **kwargs)

        return wrapper

    return decorator


__all__ = [
    "afficher_formulaire_connexion",
    "afficher_menu_utilisateur",
    "afficher_parametres_profil",
    "require_authenticated",
    "require_role",
]
