"""Configuration de la limitation de débit."""

from dataclasses import dataclass, field
from enum import StrEnum


class StrategieLimitationDebit(StrEnum):
    """Stratégies de limitation de débit."""

    FENETRE_FIXE = "fixed_window"
    FENETRE_GLISSANTE = "sliding_window"
    SEAU_A_JETONS = "token_bucket"


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


# Configuration globale
config_limitation_debit = ConfigLimitationDebit()
