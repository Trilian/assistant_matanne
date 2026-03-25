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


# ─── 2FA Schemas ──────────────────────────────────────────


class TwoFactorEnableResponse(BaseModel):
    """Réponse d'activation 2FA avec QR code et codes backup."""

    secret: str = Field(..., description="Secret TOTP (à ne pas afficher)")
    qr_code: str = Field(..., description="QR code en base64 data URI")
    backup_codes: list[str] = Field(..., description="Codes de récupération (à sauvegarder)")


class TwoFactorVerifyRequest(BaseModel):
    """Requête de vérification 2FA."""

    code: str = Field(..., min_length=6, max_length=8, description="Code TOTP 6 chiffres ou code backup")


class TwoFactorLoginRequest(BaseModel):
    """Requête de vérification 2FA pendant le login."""

    temp_token: str = Field(..., description="Token temporaire reçu lors du login")
    code: str = Field(..., min_length=6, max_length=8, description="Code TOTP ou code backup")


class TwoFactorStatusResponse(BaseModel):
    """Statut 2FA de l'utilisateur."""

    enabled: bool
    backup_codes_remaining: int = 0


class LoginResponse(BaseModel):
    """Réponse de login (avec ou sans 2FA)."""

    access_token: str | None = None
    token_type: str = "bearer"
    expires_in: int | None = None
    requires_2fa: bool = False
    temp_token: str | None = None
