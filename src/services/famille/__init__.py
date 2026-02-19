"""Package famille - Services calendrier et budget.

Imports paresseux pour éviter les imports circulaires.
Importez directement depuis les sous-packages:

    from src.services.famille.calendrier import get_calendar_sync_service
    from src.services.famille.budget import CategorieDepense
"""

__all__ = [
    "calendrier",
    "budget",
]


def __getattr__(name: str):
    """Lazy import pour éviter les imports circulaires."""
    if name == "get_calendar_sync_service":
        from src.services.famille.calendrier import get_calendar_sync_service

        return get_calendar_sync_service
    if name == "CategorieDepense":
        from src.services.famille.budget import CategorieDepense

        return CategorieDepense
    raise AttributeError(f"module 'src.services.famille' has no attribute '{name}'")
