"""
Service de synchronisation avec calendriers externes.

Fonctionnalités:
- Import/Export Google Calendar
- Import/Export Apple Calendar (iCal)
- Synchronisation bidirectionnelle
- Mapping des événements planning → calendrier
- Gestion des conflits
"""

import logging
from datetime import datetime, date, timedelta
from enum import Enum
from typing import Any
from uuid import uuid4

import httpx
from pydantic import BaseModel, Field

from src.core.decorators import with_error_handling
from src.core.database import obtenir_contexte_db
from src.core.models import CalendarEvent, Planning, Repas, FamilyActivity

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# TYPES ET SCHÉMAS
# ═══════════════════════════════════════════════════════════


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


# ═══════════════════════════════════════════════════════════
# GÉNÉRATEUR iCAL
# ═══════════════════════════════════════════════════════════


class ICalGenerator:
    """Génère des fichiers iCal (.ics) à partir des événements."""
    
    @staticmethod
    def generate_ical(events: list[CalendarEventExternal], calendar_name: str = "Assistant Matanne") -> str:
        """
        Génère un fichier iCal complet.
        
        Args:
            events: Liste d'événements à inclure
            calendar_name: Nom du calendrier
            
        Returns:
            Contenu du fichier .ics
        """
        lines = [
            "BEGIN:VCALENDAR",
            "VERSION:2.0",
            "PRODID:-//Assistant Matanne//Planning Familial//FR",
            f"X-WR-CALNAME:{calendar_name}",
            "CALSCALE:GREGORIAN",
            "METHOD:PUBLISH",
        ]
        
        for event in events:
            lines.extend(ICalGenerator._event_to_vevent(event))
        
        lines.append("END:VCALENDAR")
        
        return "\r\n".join(lines)
    
    @staticmethod
    def _event_to_vevent(event: CalendarEventExternal) -> list[str]:
        """Convertit un événement en VEVENT iCal."""
        uid = event.external_id or str(uuid4())
        
        lines = [
            "BEGIN:VEVENT",
            f"UID:{uid}@assistant-matanne",
            f"DTSTAMP:{datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}",
        ]
        
        if event.all_day:
            lines.append(f"DTSTART;VALUE=DATE:{event.start_time.strftime('%Y%m%d')}")
            lines.append(f"DTEND;VALUE=DATE:{event.end_time.strftime('%Y%m%d')}")
        else:
            lines.append(f"DTSTART:{event.start_time.strftime('%Y%m%dT%H%M%S')}")
            lines.append(f"DTEND:{event.end_time.strftime('%Y%m%dT%H%M%S')}")
        
        # Échapper les caractères spéciaux
        summary = event.title.replace(",", "\\,").replace(";", "\\;")
        lines.append(f"SUMMARY:{summary}")
        
        if event.description:
            desc = event.description.replace("\n", "\\n").replace(",", "\\,")
            lines.append(f"DESCRIPTION:{desc}")
        
        if event.location:
            lines.append(f"LOCATION:{event.location}")
        
        # Catégorie basée sur le type
        if event.source_type == "meal":
            lines.append("CATEGORIES:Repas")
        elif event.source_type == "activity":
            lines.append("CATEGORIES:Activité Familiale")
        
        lines.append("END:VEVENT")
        
        return lines
    
    @staticmethod
    def parse_ical(ical_content: str) -> list[CalendarEventExternal]:
        """
        Parse un fichier iCal et extrait les événements.
        
        Args:
            ical_content: Contenu du fichier .ics
            
        Returns:
            Liste d'événements extraits
        """
        events = []
        current_event = None
        
        for line in ical_content.split("\n"):
            line = line.strip()
            
            if line == "BEGIN:VEVENT":
                current_event = {}
            elif line == "END:VEVENT" and current_event is not None:
                # Créer l'événement
                try:
                    event = CalendarEventExternal(
                        external_id=current_event.get("UID", ""),
                        title=current_event.get("SUMMARY", "Sans titre"),
                        description=current_event.get("DESCRIPTION", ""),
                        start_time=ICalGenerator._parse_ical_datetime(current_event.get("DTSTART", "")),
                        end_time=ICalGenerator._parse_ical_datetime(current_event.get("DTEND", "")),
                        all_day=";VALUE=DATE" in current_event.get("DTSTART_RAW", ""),
                        location=current_event.get("LOCATION", ""),
                    )
                    events.append(event)
                except Exception as e:
                    logger.warning(f"Erreur parsing événement: {e}")
                
                current_event = None
            elif current_event is not None and ":" in line:
                key, value = line.split(":", 1)
                
                # Gérer les paramètres (ex: DTSTART;VALUE=DATE:20260101)
                if ";" in key:
                    current_event[key.split(";")[0]] = value
                    current_event[key.split(";")[0] + "_RAW"] = key
                else:
                    current_event[key] = value.replace("\\n", "\n").replace("\\,", ",")
        
        return events
    
    @staticmethod
    def _parse_ical_datetime(value: str) -> datetime:
        """Parse une date/heure iCal."""
        value = value.strip()
        
        # Format date seule: 20260101
        if len(value) == 8:
            return datetime.strptime(value, "%Y%m%d")
        
        # Format datetime: 20260101T120000 ou 20260101T120000Z
        if "T" in value:
            value = value.rstrip("Z")
            return datetime.strptime(value, "%Y%m%dT%H%M%S")
        
        return datetime.now()


# ═══════════════════════════════════════════════════════════
# SERVICE DE SYNCHRONISATION
# ═══════════════════════════════════════════════════════════


class CalendarSyncService:
    """
    Service de synchronisation avec les calendriers externes.
    
    Supporte:
    - Google Calendar (OAuth2)
    - Apple iCloud Calendar (via URL iCal)
    - Outlook Calendar (OAuth2)
    - URLs iCal génériques
    """
    
    def __init__(self):
        """Initialise le service."""
        self._configs: dict[str, ExternalCalendarConfig] = {}
        self.http_client = httpx.Client(timeout=30.0)
    
    # ═══════════════════════════════════════════════════════════
    # CONFIGURATION
    # ═══════════════════════════════════════════════════════════
    
    def add_calendar(self, config: ExternalCalendarConfig) -> str:
        """
        Ajoute un calendrier externe à synchroniser.
        
        Args:
            config: Configuration du calendrier
            
        Returns:
            ID du calendrier ajouté
        """
        self._configs[config.id] = config
        self._save_config_to_db(config)
        logger.info(f"Calendrier ajouté: {config.name} ({config.provider.value})")
        return config.id
    
    def remove_calendar(self, calendar_id: str):
        """Supprime un calendrier."""
        if calendar_id in self._configs:
            del self._configs[calendar_id]
        self._remove_config_from_db(calendar_id)
    
    def get_user_calendars(self, user_id: str) -> list[ExternalCalendarConfig]:
        """Récupère les calendriers d'un utilisateur."""
        return [c for c in self._configs.values() if c.user_id == user_id]
    
    # ═══════════════════════════════════════════════════════════
    # EXPORT VERS CALENDRIER EXTERNE
    # ═══════════════════════════════════════════════════════════
    
    @with_error_handling(default_return=None, afficher_erreur=True)
    def export_to_ical(
        self,
        user_id: str,
        start_date: date | None = None,
        end_date: date | None = None,
        include_meals: bool = True,
        include_activities: bool = True,
    ) -> str | None:
        """
        Exporte les événements vers un fichier iCal.
        
        Args:
            user_id: ID de l'utilisateur
            start_date: Date de début (défaut: aujourd'hui)
            end_date: Date de fin (défaut: +30 jours)
            include_meals: Inclure les repas du planning
            include_activities: Inclure les activités familiales
            
        Returns:
            Contenu du fichier .ics
        """
        start = start_date or date.today()
        end = end_date or (date.today() + timedelta(days=30))
        
        events = []
        
        with obtenir_contexte_db() as db:
            # Repas du planning
            if include_meals:
                repas_list = db.query(Repas).join(Planning).filter(
                    Repas.date_repas >= start,
                    Repas.date_repas <= end,
                ).all()
                
                for repas in repas_list:
                    # Déterminer l'heure selon le type de repas
                    if repas.type_repas == "petit_déjeuner":
                        hour = 8
                    elif repas.type_repas == "déjeuner":
                        hour = 12
                    elif repas.type_repas == "goûter":
                        hour = 16
                    else:  # dîner
                        hour = 19
                    
                    start_time = datetime.combine(repas.date_repas, datetime.min.time().replace(hour=hour))
                    end_time = start_time + timedelta(hours=1)
                    
                    title = f"🍽️ {repas.type_repas.title()}"
                    if repas.recette:
                        title += f": {repas.recette.nom}"
                    
                    events.append(CalendarEventExternal(
                        external_id=f"meal-{repas.id}",
                        title=title,
                        description=repas.notes or "",
                        start_time=start_time,
                        end_time=end_time,
                        source_type="meal",
                        source_id=repas.id,
                    ))
            
            # Activités familiales
            if include_activities:
                activities = db.query(FamilyActivity).filter(
                    FamilyActivity.date_prevue >= start,
                    FamilyActivity.date_prevue <= end,
                    FamilyActivity.statut != "annulé",
                ).all()
                
                for activity in activities:
                    start_time = datetime.combine(activity.date_prevue, datetime.min.time().replace(hour=10))
                    duration_hours = activity.duree_heures or 2
                    end_time = start_time + timedelta(hours=duration_hours)
                    
                    events.append(CalendarEventExternal(
                        external_id=f"activity-{activity.id}",
                        title=f"👨‍👩‍👧 {activity.titre}",
                        description=activity.description or "",
                        start_time=start_time,
                        end_time=end_time,
                        location=activity.lieu or "",
                        source_type="activity",
                        source_id=activity.id,
                    ))
            
            # Événements du calendrier interne
            calendar_events = db.query(CalendarEvent).filter(
                CalendarEvent.date_debut >= start,
                CalendarEvent.date_debut <= end,
            ).all()
            
            for event in calendar_events:
                events.append(CalendarEventExternal(
                    external_id=f"event-{event.id}",
                    title=event.titre,
                    description=event.description or "",
                    start_time=datetime.combine(event.date_debut, datetime.min.time().replace(hour=9)),
                    end_time=datetime.combine(event.date_fin or event.date_debut, datetime.min.time().replace(hour=10)),
                    all_day=event.journee_entiere if hasattr(event, 'journee_entiere') else False,
                    source_type="event",
                    source_id=event.id,
                ))
        
        logger.info(f"Export iCal: {len(events)} événements")
        return ICalGenerator.generate_ical(events)
    
    # ═══════════════════════════════════════════════════════════
    # IMPORT DEPUIS CALENDRIER EXTERNE
    # ═══════════════════════════════════════════════════════════
    
    @with_error_handling(default_return=None, afficher_erreur=True)
    def import_from_ical_url(
        self,
        user_id: str,
        ical_url: str,
        calendar_name: str = "Calendrier importé",
    ) -> SyncResult:
        """
        Importe les événements depuis une URL iCal.
        
        Args:
            user_id: ID de l'utilisateur
            ical_url: URL du calendrier iCal
            calendar_name: Nom à donner au calendrier
            
        Returns:
            Résultat de l'import
        """
        start_time = datetime.now()
        
        try:
            response = self.http_client.get(ical_url)
            response.raise_for_status()
            ical_content = response.text
        except Exception as e:
            return SyncResult(
                success=False,
                message=f"Impossible de télécharger le calendrier: {e}",
                errors=[str(e)]
            )
        
        # Parser le contenu iCal
        events = ICalGenerator.parse_ical(ical_content)
        
        if not events:
            return SyncResult(
                success=False,
                message="Aucun événement trouvé dans le calendrier"
            )
        
        # Sauvegarder les événements
        imported_count = 0
        errors = []
        
        with obtenir_contexte_db() as db:
            for event in events:
                try:
                    # Créer un CalendarEvent dans la base
                    cal_event = CalendarEvent(
                        titre=event.title,
                        description=event.description,
                        date_debut=event.start_time.date(),
                        date_fin=event.end_time.date() if event.end_time else None,
                        # heure_debut=event.start_time.time() if not event.all_day else None,
                        # journee_entiere=event.all_day,
                        source_externe=f"ical:{ical_url}",
                        external_id=event.external_id,
                    )
                    
                    # Vérifier si existe déjà (par external_id)
                    existing = db.query(CalendarEvent).filter(
                        CalendarEvent.external_id == event.external_id
                    ).first()
                    
                    if existing:
                        # Mettre à jour
                        existing.titre = event.title
                        existing.description = event.description
                        existing.date_debut = event.start_time.date()
                    else:
                        db.add(cal_event)
                    
                    imported_count += 1
                except Exception as e:
                    errors.append(f"Erreur import '{event.title}': {e}")
            
            db.commit()
        
        duration = (datetime.now() - start_time).total_seconds()
        
        return SyncResult(
            success=len(errors) == 0,
            message=f"{imported_count} événements importés",
            events_imported=imported_count,
            errors=errors,
            duration_seconds=duration,
        )
    
    # ═══════════════════════════════════════════════════════════
    # GOOGLE CALENDAR
    # ═══════════════════════════════════════════════════════════
    
    def get_google_auth_url(self, user_id: str, redirect_uri: str) -> str:
        """
        Génère l'URL d'autorisation Google Calendar.
        
        Args:
            user_id: ID de l'utilisateur
            redirect_uri: URL de callback
            
        Returns:
            URL d'autorisation OAuth2
        """
        from src.core.config import obtenir_parametres
        
        params = obtenir_parametres()
        client_id = getattr(params, 'GOOGLE_CLIENT_ID', '')
        
        if not client_id:
            raise ValueError("GOOGLE_CLIENT_ID non configuré")
        
        scope = "https://www.googleapis.com/auth/calendar.readonly"
        
        auth_url = (
            f"https://accounts.google.com/o/oauth2/v2/auth?"
            f"client_id={client_id}&"
            f"redirect_uri={redirect_uri}&"
            f"response_type=code&"
            f"scope={scope}&"
            f"access_type=offline&"
            f"state={user_id}"
        )
        
        return auth_url
    
    def handle_google_callback(
        self,
        user_id: str,
        code: str,
        redirect_uri: str,
    ) -> ExternalCalendarConfig | None:
        """
        Gère le callback OAuth2 Google.
        
        Args:
            user_id: ID de l'utilisateur
            code: Code d'autorisation
            redirect_uri: URL de callback utilisée
            
        Returns:
            Configuration du calendrier ajouté
        """
        from src.core.config import obtenir_parametres
        
        params = obtenir_parametres()
        client_id = getattr(params, 'GOOGLE_CLIENT_ID', '')
        client_secret = getattr(params, 'GOOGLE_CLIENT_SECRET', '')
        
        if not client_id or not client_secret:
            logger.error("Google OAuth non configuré")
            return None
        
        try:
            # Échanger le code contre des tokens
            response = self.http_client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "code": code,
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "redirect_uri": redirect_uri,
                    "grant_type": "authorization_code",
                }
            )
            response.raise_for_status()
            tokens = response.json()
            
            # Créer la configuration
            config = ExternalCalendarConfig(
                user_id=user_id,
                provider=CalendarProvider.GOOGLE,
                name="Google Calendar",
                access_token=tokens["access_token"],
                refresh_token=tokens.get("refresh_token", ""),
                token_expiry=datetime.now() + timedelta(seconds=tokens.get("expires_in", 3600)),
            )
            
            self.add_calendar(config)
            return config
            
        except Exception as e:
            logger.error(f"Erreur callback Google: {e}")
            return None
    
    def sync_google_calendar(self, config: ExternalCalendarConfig) -> SyncResult:
        """Synchronise avec Google Calendar."""
        if config.provider != CalendarProvider.GOOGLE:
            return SyncResult(success=False, message="Pas un calendrier Google")
        
        # Vérifier/rafraîchir le token
        if config.token_expiry and config.token_expiry < datetime.now():
            self._refresh_google_token(config)
        
        try:
            # Récupérer les événements
            headers = {"Authorization": f"Bearer {config.access_token}"}
            
            time_min = datetime.now().isoformat() + "Z"
            time_max = (datetime.now() + timedelta(days=30)).isoformat() + "Z"
            
            response = self.http_client.get(
                f"https://www.googleapis.com/calendar/v3/calendars/primary/events",
                headers=headers,
                params={
                    "timeMin": time_min,
                    "timeMax": time_max,
                    "singleEvents": "true",
                    "orderBy": "startTime",
                }
            )
            response.raise_for_status()
            data = response.json()
            
            events = []
            for item in data.get("items", []):
                start = item.get("start", {})
                end = item.get("end", {})
                
                start_dt = start.get("dateTime") or start.get("date")
                end_dt = end.get("dateTime") or end.get("date")
                
                if start_dt:
                    events.append(CalendarEventExternal(
                        external_id=item["id"],
                        title=item.get("summary", "Sans titre"),
                        description=item.get("description", ""),
                        start_time=datetime.fromisoformat(start_dt.replace("Z", "+00:00")),
                        end_time=datetime.fromisoformat(end_dt.replace("Z", "+00:00")) if end_dt else datetime.now(),
                        all_day="date" in start,
                        location=item.get("location", ""),
                    ))
            
            # Importer les événements dans la base locale
            imported = self._import_events_to_db(events)
            
            config.last_sync = datetime.now()
            self._save_config_to_db(config)
            
            return SyncResult(
                success=True,
                message=f"Synchronisation Google réussie",
                events_imported=imported,
            )
            
        except Exception as e:
            logger.error(f"Erreur sync Google: {e}")
            return SyncResult(success=False, message=str(e), errors=[str(e)])
    
    def _refresh_google_token(self, config: ExternalCalendarConfig):
        """Rafraîchit le token Google."""
        from src.core.config import obtenir_parametres
        
        params = obtenir_parametres()
        
        try:
            response = self.http_client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "client_id": getattr(params, 'GOOGLE_CLIENT_ID', ''),
                    "client_secret": getattr(params, 'GOOGLE_CLIENT_SECRET', ''),
                    "refresh_token": config.refresh_token,
                    "grant_type": "refresh_token",
                }
            )
            response.raise_for_status()
            tokens = response.json()
            
            config.access_token = tokens["access_token"]
            config.token_expiry = datetime.now() + timedelta(seconds=tokens.get("expires_in", 3600))
            self._save_config_to_db(config)
            
        except Exception as e:
            logger.error(f"Erreur refresh token Google: {e}")
    
    def _import_events_to_db(self, events: list[CalendarEventExternal]) -> int:
        """Importe les événements dans la base."""
        count = 0
        
        with obtenir_contexte_db() as db:
            for event in events:
                try:
                    existing = db.query(CalendarEvent).filter(
                        CalendarEvent.external_id == event.external_id
                    ).first()
                    
                    if existing:
                        existing.titre = event.title
                        existing.description = event.description
                    else:
                        cal_event = CalendarEvent(
                            titre=event.title,
                            description=event.description,
                            date_debut=event.start_time.date(),
                            date_fin=event.end_time.date(),
                            external_id=event.external_id,
                        )
                        db.add(cal_event)
                    
                    count += 1
                except Exception as e:
                    logger.warning(f"Erreur import événement: {e}")
            
            db.commit()
        
        return count
    
    # ═══════════════════════════════════════════════════════════
    # PERSISTANCE
    # ═══════════════════════════════════════════════════════════
    
    def _save_config_to_db(self, config: ExternalCalendarConfig):
        """Sauvegarde la configuration en base."""
        # Implémentation avec Supabase ou SQLAlchemy
        pass
    
    def _remove_config_from_db(self, calendar_id: str):
        """Supprime la configuration de la base."""
        pass


# ═══════════════════════════════════════════════════════════
# FACTORY
# ═══════════════════════════════════════════════════════════


_calendar_sync_service: CalendarSyncService | None = None


def get_calendar_sync_service() -> CalendarSyncService:
    """Factory pour le service de synchronisation calendrier."""
    global _calendar_sync_service
    if _calendar_sync_service is None:
        _calendar_sync_service = CalendarSyncService()
    return _calendar_sync_service


# ═══════════════════════════════════════════════════════════
# COMPOSANT UI STREAMLIT
# ═══════════════════════════════════════════════════════════


def render_calendar_sync_ui():
    """Interface Streamlit pour la synchronisation des calendriers."""
    import streamlit as st
    
    st.subheader("📅 Synchronisation Calendriers")
    
    service = get_calendar_sync_service()
    
    # Tabs pour les différentes options
    tab1, tab2, tab3 = st.tabs(["📤 Exporter", "📥 Importer", "🔗 Connecter"])
    
    with tab1:
        st.markdown("### Exporter vers iCal")
        st.info("Téléchargez vos repas et activités au format iCal pour les importer dans votre application de calendrier préférée.")
        
        col1, col2 = st.columns(2)
        with col1:
            include_meals = st.checkbox("Inclure les repas", value=True, key="export_meals")
        with col2:
            include_activities = st.checkbox("Inclure les activités", value=True, key="export_activities")
        
        days_ahead = st.slider("Période (jours)", 7, 90, 30, key="export_days")
        
        if st.button("📥 Générer le fichier iCal", type="primary"):
            from src.services.auth import get_auth_service
            auth = get_auth_service()
            user = auth.get_current_user()
            user_id = user.id if user else "anonymous"
            
            ical_content = service.export_to_ical(
                user_id=user_id,
                end_date=date.today() + timedelta(days=days_ahead),
                include_meals=include_meals,
                include_activities=include_activities,
            )
            
            if ical_content:
                st.download_button(
                    label="💾 Télécharger le fichier .ics",
                    data=ical_content,
                    file_name="assistant_matanne_calendar.ics",
                    mime="text/calendar",
                )
                st.success("✅ Fichier généré avec succès!")
    
    with tab2:
        st.markdown("### Importer depuis une URL iCal")
        st.info("Importez des événements depuis un calendrier partagé (Google Calendar, iCloud, etc.)")
        
        ical_url = st.text_input(
            "URL du calendrier iCal",
            placeholder="https://calendar.google.com/calendar/ical/...",
            key="import_ical_url"
        )
        
        calendar_name = st.text_input(
            "Nom du calendrier",
            value="Calendrier importé",
            key="import_calendar_name"
        )
        
        if st.button("📤 Importer", type="primary") and ical_url:
            from src.services.auth import get_auth_service
            auth = get_auth_service()
            user = auth.get_current_user()
            user_id = user.id if user else "anonymous"
            
            with st.spinner("Import en cours..."):
                result = service.import_from_ical_url(
                    user_id=user_id,
                    ical_url=ical_url,
                    calendar_name=calendar_name,
                )
            
            if result and result.success:
                st.success(f"✅ {result.message}")
            else:
                st.error(f"❌ {result.message if result else 'Erreur inconnue'}")
    
    with tab3:
        st.markdown("### Connecter un calendrier")
        
        st.markdown("#### Google Calendar")
        st.caption("Synchronisez automatiquement avec votre Google Calendar")
        
        from src.core.config import obtenir_parametres
        params = obtenir_parametres()
        
        if getattr(params, 'GOOGLE_CLIENT_ID', None):
            if st.button("🔗 Connecter Google Calendar", key="connect_google"):
                # Générer l'URL d'auth
                auth_url = service.get_google_auth_url(
                    user_id="current_user",
                    redirect_uri="http://localhost:8501/callback"
                )
                st.markdown(f"[Cliquez ici pour autoriser]({auth_url})")
        else:
            st.warning("Google Calendar non configuré (GOOGLE_CLIENT_ID manquant)")
        
        st.markdown("---")
        st.markdown("#### Apple iCloud Calendar")
        st.caption("Utilisez l'URL de partage iCal de votre calendrier iCloud")
        st.info("Dans iCloud Calendar: Partager → Calendrier public → Copier le lien")
