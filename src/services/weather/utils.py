"""
Hub de réexportation pour les utilitaires météo.

Ce module réexporte tous les noms publics des sous-modules pour
assurer la rétrocompatibilité avec les imports existants:
    from src.services.weather.utils import ...

Sous-modules:
    - weather_codes: Constantes et conversions de codes météo WMO
    - alertes_meteo: Calculs de températures et détection d'alertes
    - arrosage: Calcul d'arrosage intelligent et risque de sécheresse
    - saisons: Saisons, conseils jardinage, résumé météo
    - parsing: Parsing Open-Meteo et validation de coordonnées
"""

from .alertes_meteo import *  # noqa: F401,F403
from .arrosage import *  # noqa: F401,F403
from .parsing import *  # noqa: F401,F403
from .saisons import *  # noqa: F401,F403
from .weather_codes import *  # noqa: F401,F403
