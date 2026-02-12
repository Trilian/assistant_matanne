"""
Schémas Pydantic pour la synchronisation des calendriers.

Types et modèles de données pour l'import/export de calendriers.
"""

from datetime import datetime
from enum import Enum
from uuid import uuid4

from pydantic import BaseModel, Field


class CalendarProvider(str, Enum):
    """Fournisseurs de calendrier supportés."""
    GOOGLE = "google"
    APPLE = "apple"  # iCal/iCloud
    OUTLOOK = "outlook"
    ICAL_URL = "ical_url"  # URL iCal générique


class SyncDirection(str, Enum):
    """Direction de synchronisation."""
    IMPORT_ONLY = "import"  # Du calendrier externe vers l'app
    EXPORT_ONLY = "export"  # De l'app vers le calendrier externe
    BIDIRECTIONAL = "both"  # Dans les deux sens


class ExternalCalendarConfig(BaseModel):
    """Configuration d'un calendrier externe."""
    
    id: str = Field(default_factory=lambda: str(uuid4())[:12])
    user_id: str
    provider: CalendarProvider
    name: str = "Mon calendrier"
    
    # Configuration selon le provider
    calendar_id: str = ""  # ID Google/Outlook
    ical_url: str = ""  # URL pour iCal
    
    # OAuth tokens (pour Google/Outlook)
    access_token: str = ""
    refresh_token: str = ""
    token_expiry: datetime | None = None
    
    # Options de sync
    sync_direction: SyncDirection = SyncDirection.BIDIRECTIONAL
    sync_meals: bool = True
    sync_activities: bool = True
    sync_events: bool = True
    
    # État
    last_sync: datetime | None = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.now)


class CalendarEventExternal(BaseModel):
    """Événement de calendrier externe."""
    
    id: str = ""
    external_id: str = ""  # ID dans le calendrier externe
    title: str
    description: str = ""
    start_time: datetime
    end_time: datetime
    all_day: bool = False
    location: str = ""
    color: str = ""
    
    # Métadonnées de sync
    source_type: str = ""  # "meal", "activity", "event"
    source_id: int | None = None
    last_modified: datetime = Field(default_factory=datetime.now)


class SyncResult(BaseModel):
    """Résultat d'une synchronisation."""
    
    success: bool = False
    message: str = ""
    events_imported: int = 0
    events_exported: int = 0
    events_updated: int = 0
    conflicts: list[dict] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
    duration_seconds: float = 0.0
