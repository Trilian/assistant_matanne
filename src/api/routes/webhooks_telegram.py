"""Backward-compat shim -- redirige vers src.api.routes.telegram.

DEPRECATED: Importer directement depuis `src.api.routes.telegram`.
Ce fichier sera supprime dans une version future.
"""

from src.api.routes.telegram import *  # noqa: F401, F403
from src.api.routes.telegram import router  # noqa: F811
