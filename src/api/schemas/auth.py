"""
Schémas Pydantic pour l'authentification.
"""

from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    """Requête de connexion."""

    email: EmailStr = Field(..., description="Adresse email de l'utilisateur")
    password: str = Field(..., description="Mot de passe")


class RegisterRequest(BaseModel):
    """Requête d'inscription."""

    email: EmailStr = Field(..., description="Adresse email")
    password: str = Field(..., description="Mot de passe (6 caractères min.)")
    nom: str = Field(..., min_length=2, description="Nom de l'utilisateur")


class UserInfoResponse(BaseModel):
    """Réponse avec les infos utilisateur."""

    id: str
    email: str
    role: str
