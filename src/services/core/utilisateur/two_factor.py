"""
Service d'authentification à deux facteurs (TOTP).

Gère la génération de secrets TOTP, QR codes, et vérification de codes.
Utilise pyotp pour TOTP (RFC 6238) et qrcode pour la génération de QR.

Usage:
    from src.services.core.utilisateur.two_factor import obtenir_service_2fa

    service = obtenir_service_2fa()
    secret = service.generer_secret()
    qr_b64 = service.generer_qr_code(secret, "user@example.com")
    ok = service.verifier_code(secret, "123456")
"""

from __future__ import annotations

import base64
import hashlib
import io
import logging
import secrets
from typing import Any

from src.services.core.registry import service_factory

logger = logging.getLogger(__name__)


class ServiceDeuxFacteurs:
    """Service TOTP pour authentification 2FA."""

    ISSUER = "Assistant Matanne"
    NB_CODES_BACKUP = 10

    def generer_secret(self) -> str:
        """Génère un secret TOTP aléatoire (base32, 32 chars)."""
        import pyotp

        return pyotp.random_base32()

    def generer_qr_code(self, secret: str, email: str) -> str:
        """Génère un QR code pour Google Authenticator (base64 PNG).

        Args:
            secret: Secret TOTP base32
            email: Email utilisateur (affiché dans l'app authenticator)

        Returns:
            Image PNG encodée en base64 (data URI)
        """
        import pyotp
        import qrcode

        totp = pyotp.TOTP(secret)
        uri = totp.provisioning_uri(name=email, issuer_name=self.ISSUER)

        img = qrcode.make(uri)
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)

        b64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
        return f"data:image/png;base64,{b64}"

    def verifier_code(self, secret: str, code: str) -> bool:
        """Vérifie un code TOTP (accepte ±1 fenêtre de 30s).

        Args:
            secret: Secret TOTP base32
            code: Code 6 chiffres saisi par l'utilisateur

        Returns:
            True si le code est valide
        """
        import pyotp

        totp = pyotp.TOTP(secret)
        return totp.verify(code, valid_window=1)

    def generer_codes_backup(self) -> list[str]:
        """Génère des codes de récupération à usage unique.

        Returns:
            Liste de codes en clair (8 chars hex chacun)
        """
        return [secrets.token_hex(4).upper() for _ in range(self.NB_CODES_BACKUP)]

    def hasher_codes_backup(self, codes: list[str]) -> list[str]:
        """Hashe les codes backup pour stockage en base.

        Args:
            codes: Codes en clair

        Returns:
            Liste de hashes SHA-256
        """
        return [hashlib.sha256(c.encode()).hexdigest() for c in codes]

    def verifier_code_backup(
        self, code: str, codes_hashes: list[str]
    ) -> tuple[bool, list[str]]:
        """Vérifie un code backup et le consume (usage unique).

        Args:
            code: Code backup en clair
            codes_hashes: Liste des hashes restants

        Returns:
            (valide, codes_restants) — codes_restants sans le code utilisé
        """
        code_hash = hashlib.sha256(code.upper().encode()).hexdigest()
        if code_hash in codes_hashes:
            restants = [h for h in codes_hashes if h != code_hash]
            return True, restants
        return False, codes_hashes


@service_factory("two_factor", tags={"core", "auth", "security"})
def obtenir_service_2fa() -> ServiceDeuxFacteurs:
    """Factory singleton pour le service 2FA."""
    return ServiceDeuxFacteurs()


__all__ = ["ServiceDeuxFacteurs", "obtenir_service_2fa"]
