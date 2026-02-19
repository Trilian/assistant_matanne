"""
Schémas Pydantic pour l'authentification.
"""

from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    """Requête de connexion."""

    email: str = Field(..., description="Adresse email de l'utilisateur")
    password: str = Field(..., description="Mot de passe")


class UserInfoResponse(BaseModel):
    """Réponse avec les infos utilisateur."""

    id: str
    email: str
    role: str
