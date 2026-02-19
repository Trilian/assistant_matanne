"""
Service de gestion des templates de semaine.

Permet de:
- Créer et gérer des templates de semaine
- Appliquer un template à une semaine donnée
- Copier une semaine existante en template
"""

from datetime import date, datetime, timedelta

from sqlalchemy.orm import Session

from src.core.constants import JOURS_SEMAINE
from src.core.decorators import avec_session_db
from src.core.models import CalendarEvent, TemplateItem, TemplateSemaine


class ServiceTemplates:
    """Service de gestion des templates de semaine."""

    def __init__(self, db: Session | None = None):
        """Initialise le service."""
        self._db = db

    @avec_session_db
    def lister_templates(
        self, actifs_seulement: bool = True, *, db: Session
    ) -> list[TemplateSemaine]:
        """Liste tous les templates disponibles."""
        query = db.query(TemplateSemaine)
        if actifs_seulement:
            query = query.filter(TemplateSemaine.actif == True)
        return query.order_by(TemplateSemaine.nom).all()

    @avec_session_db
    def get_template(self, template_id: int, *, db: Session) -> TemplateSemaine | None:
        """Récupère un template par son ID."""
        return db.query(TemplateSemaine).filter_by(id=template_id).first()

    @avec_session_db
    def get_template_par_nom(self, nom: str, *, db: Session) -> TemplateSemaine | None:
        """Récupère un template par son nom."""
        return db.query(TemplateSemaine).filter_by(nom=nom).first()

    @avec_session_db
    def creer_template(
        self,
        nom: str,
        description: str | None = None,
        items: list[dict] | None = None,
        *,
        db: Session,
    ) -> TemplateSemaine:
        """
        Crée un nouveau template de semaine.

        Args:
            nom: Nom du template
            description: Description optionnelle
            items: Liste d'items [{jour_semaine, heure_debut, heure_fin, titre, type_event, lieu, couleur}]
            db: Session SQLAlchemy

        Returns:
            Le template créé
        """
        template = TemplateSemaine(nom=nom, description=description)
        db.add(template)
        db.flush()  # Pour obtenir l'ID

        if items:
            for item_data in items:
                item = TemplateItem(
                    template_id=template.id,
                    jour_semaine=item_data.get("jour_semaine", 0),
                    heure_debut=item_data.get("heure_debut", "09:00"),
                    heure_fin=item_data.get("heure_fin"),
                    titre=item_data.get("titre", "Événement"),
                    type_event=item_data.get("type_event", "autre"),
                    lieu=item_data.get("lieu"),
                    couleur=item_data.get("couleur"),
                )
                db.add(item)

        db.commit()
        db.refresh(template)
        return template

    @avec_session_db
    def ajouter_item(
        self,
        template_id: int,
        jour_semaine: int,
        heure_debut: str,
        titre: str,
        heure_fin: str | None = None,
        type_event: str = "autre",
        lieu: str | None = None,
        couleur: str | None = None,
        *,
        db: Session,
    ) -> TemplateItem:
        """Ajoute un item à un template."""
        item = TemplateItem(
            template_id=template_id,
            jour_semaine=jour_semaine,
            heure_debut=heure_debut,
            heure_fin=heure_fin,
            titre=titre,
            type_event=type_event,
            lieu=lieu,
            couleur=couleur,
        )
        db.add(item)
        db.commit()
        db.refresh(item)
        return item

    @avec_session_db
    def supprimer_item(self, item_id: int, *, db: Session) -> bool:
        """Supprime un item d'un template."""
        item = db.query(TemplateItem).filter_by(id=item_id).first()
        if item:
            db.delete(item)
            db.commit()
            return True
        return False

    @avec_session_db
    def supprimer_template(self, template_id: int, *, db: Session) -> bool:
        """Supprime un template (cascade sur les items)."""
        template = db.query(TemplateSemaine).filter_by(id=template_id).first()
        if template:
            db.delete(template)
            db.commit()
            return True
        return False

    @avec_session_db
    def appliquer_template(
        self,
        template_id: int,
        date_lundi: date,
        *,
        db: Session,
    ) -> list[CalendarEvent]:
        """
        Applique un template à une semaine donnée.

        Args:
            template_id: ID du template à appliquer
            date_lundi: Date du lundi de la semaine cible
            db: Session SQLAlchemy

        Returns:
            Liste des événements créés
        """
        template = db.query(TemplateSemaine).filter_by(id=template_id).first()
        if not template:
            return []

        events_crees = []

        for item in template.items:
            # Calculer la date exacte
            event_date = date_lundi + timedelta(days=item.jour_semaine)

            # Parser l'heure
            h, m = map(int, item.heure_debut.split(":"))
            date_debut = datetime.combine(event_date, datetime.min.time().replace(hour=h, minute=m))

            date_fin = None
            if item.heure_fin:
                h, m = map(int, item.heure_fin.split(":"))
                date_fin = datetime.combine(
                    event_date, datetime.min.time().replace(hour=h, minute=m)
                )

            # Créer l'événement
            event = CalendarEvent(
                titre=item.titre,
                date_debut=date_debut,
                date_fin=date_fin,
                lieu=item.lieu,
                type_event=item.type_event,
                couleur=item.couleur,
            )
            db.add(event)
            events_crees.append(event)

        db.commit()
        return events_crees

    @avec_session_db
    def creer_depuis_semaine(
        self,
        nom: str,
        date_lundi: date,
        description: str | None = None,
        *,
        db: Session,
    ) -> TemplateSemaine | None:
        """
        Crée un template à partir des événements d'une semaine existante.

        Args:
            nom: Nom du nouveau template
            date_lundi: Date du lundi de la semaine source
            description: Description optionnelle
            db: Session SQLAlchemy

        Returns:
            Le template créé ou None si aucun événement
        """
        date_fin = date_lundi + timedelta(days=6)
        date_debut_dt = datetime.combine(date_lundi, datetime.min.time())
        date_fin_dt = datetime.combine(date_fin, datetime.max.time())

        # Récupérer les événements de la semaine
        events = (
            db.query(CalendarEvent)
            .filter(
                CalendarEvent.date_debut >= date_debut_dt,
                CalendarEvent.date_debut <= date_fin_dt,
            )
            .all()
        )

        if not events:
            return None

        # Créer le template
        template = TemplateSemaine(nom=nom, description=description)
        db.add(template)
        db.flush()

        # Convertir les événements en items
        for event in events:
            jour_semaine = event.date_debut.weekday()
            heure_debut = event.date_debut.strftime("%H:%M")
            heure_fin = event.date_fin.strftime("%H:%M") if event.date_fin else None

            item = TemplateItem(
                template_id=template.id,
                jour_semaine=jour_semaine,
                heure_debut=heure_debut,
                heure_fin=heure_fin,
                titre=event.titre,
                type_event=event.type_event,
                lieu=event.lieu,
                couleur=event.couleur,
            )
            db.add(item)

        db.commit()
        db.refresh(template)
        return template

    def get_items_par_jour(self, template: TemplateSemaine) -> dict[int, list[TemplateItem]]:
        """Organise les items d'un template par jour de la semaine."""
        par_jour: dict[int, list[TemplateItem]] = {i: [] for i in range(7)}
        for item in template.items:
            par_jour[item.jour_semaine].append(item)
        return par_jour


# Factory
_service_templates: ServiceTemplates | None = None


def obtenir_service_templates() -> ServiceTemplates:
    """Retourne l'instance singleton du service de templates."""
    global _service_templates
    if _service_templates is None:
        _service_templates = ServiceTemplates()
    return _service_templates


__all__ = [
    "JOURS_SEMAINE",
    "ServiceTemplates",
    "obtenir_service_templates",
]
