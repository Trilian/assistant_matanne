"""
Configuration de la limitation de débit.

Noms français avec alias anglais pour compatibilité.
"""

from dataclasses import dataclass, field
from enum import StrEnum


class StrategieLimitationDebit(StrEnum):
    """Stratégies de limitation de débit."""

    FENETRE_FIXE = "fixed_window"
    FENETRE_GLISSANTE = "sliding_window"
    SEAU_A_JETONS = "token_bucket"

    # Alias anglais
    FIXED_WINDOW = "fixed_window"
    SLIDING_WINDOW = "sliding_window"
    TOKEN_BUCKET = "token_bucket"


# Alias rétrocompatibilité
RateLimitStrategy = StrategieLimitationDebit


@dataclass
class ConfigLimitationDebit:
    """Configuration de la limitation de débit."""

    # Limites globales par défaut
    requetes_par_minute: int = 60
    requetes_par_heure: int = 1000
    requetes_par_jour: int = 10000

    # Limites par type d'utilisateur
    requetes_anonyme_par_minute: int = 20
    requetes_authentifie_par_minute: int = 60
    requetes_premium_par_minute: int = 200

    # Limites spécifiques aux endpoints IA
    requetes_ia_par_minute: int = 10
    requetes_ia_par_heure: int = 100
    requetes_ia_par_jour: int = 500

    # Configuration
    strategie: StrategieLimitationDebit = StrategieLimitationDebit.FENETRE_GLISSANTE
    activer_headers: bool = True

    # Endpoints exemptés
    chemins_exemptes: list[str] = field(
        default_factory=lambda: ["/health", "/docs", "/redoc", "/openapi.json"]
    )

    # Alias anglais (propriétés)
    @property
    def requests_per_minute(self) -> int:
        return self.requetes_par_minute

    @property
    def requests_per_hour(self) -> int:
        return self.requetes_par_heure

    @property
    def requests_per_day(self) -> int:
        return self.requetes_par_jour

    @property
    def anonymous_requests_per_minute(self) -> int:
        return self.requetes_anonyme_par_minute

    @property
    def authenticated_requests_per_minute(self) -> int:
        return self.requetes_authentifie_par_minute

    @property
    def premium_requests_per_minute(self) -> int:
        return self.requetes_premium_par_minute

    @property
    def ai_requests_per_minute(self) -> int:
        return self.requetes_ia_par_minute

    @property
    def ai_requests_per_hour(self) -> int:
        return self.requetes_ia_par_heure

    @property
    def ai_requests_per_day(self) -> int:
        return self.requetes_ia_par_jour

    @property
    def strategy(self) -> StrategieLimitationDebit:
        return self.strategie

    @property
    def enable_headers(self) -> bool:
        return self.activer_headers

    @property
    def exempt_paths(self) -> list[str]:
        return self.chemins_exemptes


# Alias rétrocompatibilité
RateLimitConfig = ConfigLimitationDebit

# Configuration globale
config_limitation_debit = ConfigLimitationDebit()
rate_limit_config = config_limitation_debit
