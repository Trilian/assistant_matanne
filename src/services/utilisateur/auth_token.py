"""
Mixin de validation de tokens JWT.

Fournit la validation et le décodage de tokens JWT Supabase,
utilisable notamment pour l'authentification d'appels API REST.

Dépendances attendues sur ``self``
-----------------------------------
- ``self._client``     : client Supabase (peut être ``None``)
- ``self.is_configured``: propriété indiquant si le client est actif
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from .auth_schemas import Role, UserProfile

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


class TokenValidationMixin:
    """Mixin fournissant la validation et le décodage de tokens JWT."""

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
        Décode le payload d'un JWT sans validation de signature.

        Utile pour le debug ou l'extraction d'infos basiques.

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
