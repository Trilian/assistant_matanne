"""
Schémas Pydantic pour l'authentification.
"""

from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    """Requête de connexion."""

    email: EmailStr = Field(..., description="Adresse email de l'utilisateur")
    password: str = Field(..., description="Mot de passe", min_length=8, max_length=200)

    model_config = {
        "json_schema_extra": {
            "example": {"email": "anne@example.com", "password": "MotDePasseFort!2026"}
        }
    }


class RegisterRequest(BaseModel):
    """Requête d'inscription."""

    email: EmailStr = Field(..., description="Adresse email")
    password: str = Field(
        ..., description="Mot de passe (6 caractères min.)", min_length=8, max_length=200
    )
    nom: str = Field(..., min_length=2, max_length=120, description="Nom de l'utilisateur")

    model_config = {
        "json_schema_extra": {
            "example": {
                "email": "anne@example.com",
                "password": "MotDePasseFort!2026",
                "nom": "Anne",
            }
        }
    }


class UserInfoResponse(BaseModel):
    """Réponse avec les infos utilisateur."""

    id: str = Field(max_length=100)
    email: str = Field(max_length=200)
    role: str = Field(max_length=50)
    nom: str = Field(default="", max_length=120)

    model_config = {
        "json_schema_extra": {
            "example": {"id": "user_123", "email": "anne@example.com", "role": "admin", "nom": "Anne"}
        }
    }


# ─── 2FA Schemas ──────────────────────────────────────────


class TwoFactorEnableResponse(BaseModel):
    """Réponse d'activation 2FA avec QR code et codes backup."""

    secret: str = Field(..., description="Secret TOTP (à ne pas afficher)", max_length=200)
    qr_code: str = Field(..., description="QR code en base64 data URI", max_length=10000)
    backup_codes: list[str] = Field(..., description="Codes de récupération (à sauvegarder)")

    model_config = {
        "json_schema_extra": {
            "example": {
                "secret": "ABCDEF1234567890",
                "qr_code": "data:image/png;base64,iVBORw0KGgoAAA...",
                "backup_codes": ["A1B2C3D4", "E5F6G7H8"],
            }
        }
    }


class TwoFactorVerifyRequest(BaseModel):
    """Requête de vérification 2FA."""

    code: str = Field(
        ..., min_length=6, max_length=8, description="Code TOTP 6 chiffres ou code backup"
    )


class TwoFactorLoginRequest(BaseModel):
    """Requête de vérification 2FA pendant le login."""

    temp_token: str = Field(..., description="Token temporaire reçu lors du login", max_length=500)
    code: str = Field(..., min_length=6, max_length=8, description="Code TOTP ou code backup")

    model_config = {
        "json_schema_extra": {"example": {"temp_token": "temp.jwt.token", "code": "123456"}}
    }


class TwoFactorStatusResponse(BaseModel):
    """Statut 2FA de l'utilisateur."""

    enabled: bool
    backup_codes_remaining: int = 0

    model_config = {
        "json_schema_extra": {"example": {"enabled": True, "backup_codes_remaining": 6}}
    }


class LoginResponse(BaseModel):
    """Réponse de login (avec ou sans 2FA)."""

    access_token: str | None = Field(None, max_length=1000)
    token_type: str = Field("bearer", max_length=20)
    expires_in: int | None = None
    requires_2fa: bool = False
    temp_token: str | None = Field(None, max_length=500)

    model_config = {
        "json_schema_extra": {
            "example": {
                "access_token": "jwt.token.value",
                "token_type": "bearer",
                "expires_in": 3600,
                "requires_2fa": False,
                "temp_token": None,
            }
        }
    }
