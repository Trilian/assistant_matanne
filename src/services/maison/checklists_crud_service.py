"""
Service CRUD Checklists Vacances.

Templates de checklists avec items cochables et suggestions IA.
"""

import logging

from sqlalchemy.orm import Session

from src.core.decorators import avec_cache, avec_gestion_erreurs, avec_session_db
from src.core.models.maison_extensions import ChecklistVacances, ItemChecklist
from src.core.monitoring import chronometre
from src.services.core.base import BaseService
from src.services.core.event_bus_mixin import EventBusMixin
from src.services.core.registry import service_factory

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════
# TEMPLATES PRÉDÉFINIS
# ═══════════════════════════════════════════════════════════

TEMPLATES_CHECKLIST: dict[str, list[dict]] = {
    "vacances_ete": [
        # Maison
        {"libelle": "Couper l'eau (robinet principal)", "categorie": "maison", "quand": "jour_j"},
        {
            "libelle": "Débrancher les appareils électriques inutiles",
            "categorie": "maison",
            "quand": "jour_j",
        },
        {"libelle": "Programmer les volets / lumières", "categorie": "maison", "quand": "j-1"},
        {"libelle": "Activer l'alarme", "categorie": "maison", "quand": "jour_j"},
        {"libelle": "Donner le double des clés au voisin", "categorie": "maison", "quand": "j-3"},
        {"libelle": "Vider le frigo / poubelles", "categorie": "maison", "quand": "j-1"},
        {
            "libelle": "Arroser les plantes (ou demander au voisin)",
            "categorie": "maison",
            "quand": "j-1",
        },
        {"libelle": "Fermer volets / fenêtres", "categorie": "maison", "quand": "jour_j"},
        # Administratif
        {
            "libelle": "Vérifier passeports / CNI validité",
            "categorie": "administratif",
            "quand": "j-7",
        },
        {
            "libelle": "Imprimer réservations (hôtel, vol, location)",
            "categorie": "administratif",
            "quand": "j-3",
        },
        {"libelle": "Assurance voyage souscrite", "categorie": "administratif", "quand": "j-7"},
        {"libelle": "Prévenir la banque (étranger)", "categorie": "administratif", "quand": "j-7"},
        {"libelle": "Faire suivre le courrier", "categorie": "administratif", "quand": "j-7"},
        # Jules
        {"libelle": "Préparer le sac à langer", "categorie": "jules", "quand": "j-1"},
        {
            "libelle": "Médicaments Jules (Doliprane, sérum phy)",
            "categorie": "jules",
            "quand": "j-1",
        },
        {"libelle": "Doudou + tétine de secours", "categorie": "jules", "quand": "jour_j"},
        {"libelle": "Carnet de santé Jules", "categorie": "jules", "quand": "jour_j"},
        # Bagages
        {"libelle": "Valises bouclées", "categorie": "bagages", "quand": "j-1"},
        {"libelle": "Trousse de toilette", "categorie": "bagages", "quand": "j-1"},
        {"libelle": "Chargeurs téléphones / tablette", "categorie": "bagages", "quand": "jour_j"},
        {"libelle": "Crème solaire + chapeaux", "categorie": "bagages", "quand": "j-1"},
        {"libelle": "Pharmacie de voyage", "categorie": "bagages", "quand": "j-3"},
        # Véhicule
        {"libelle": "Vérifier niveau huile et pneus", "categorie": "vehicule", "quand": "j-3"},
        {"libelle": "Plein d'essence", "categorie": "vehicule", "quand": "j-1"},
        {
            "libelle": "Gilet jaune + triangle dans le coffre",
            "categorie": "vehicule",
            "quand": "j-1",
        },
    ],
    "weekend": [
        {"libelle": "Fermer les fenêtres", "categorie": "maison", "quand": "jour_j"},
        {"libelle": "Sortir les poubelles", "categorie": "maison", "quand": "jour_j"},
        {"libelle": "Charger les téléphones", "categorie": "bagages", "quand": "j-1"},
        {"libelle": "Sac Jules (changes, repas, doudou)", "categorie": "jules", "quand": "jour_j"},
        {"libelle": "Préparer les repas route", "categorie": "bagages", "quand": "j-1"},
    ],
    "vacances_hiver": [
        {
            "libelle": "Baisser le chauffage (mode hors-gel)",
            "categorie": "maison",
            "quand": "jour_j",
        },
        {"libelle": "Couper l'eau si gel possible", "categorie": "maison", "quand": "jour_j"},
        {
            "libelle": "Chaînes neige / pneus hiver vérifiés",
            "categorie": "vehicule",
            "quand": "j-3",
        },
        {
            "libelle": "Combinaisons ski enfant vérifiées (taille)",
            "categorie": "bagages",
            "quand": "j-7",
        },
        {"libelle": "Forfaits ski réservés", "categorie": "administratif", "quand": "j-7"},
        {"libelle": "Crème solaire + après-ski", "categorie": "bagages", "quand": "j-1"},
        {"libelle": "Médicaments Jules (altitude, froid)", "categorie": "jules", "quand": "j-1"},
    ],
    "camping": [
        {"libelle": "Tente vérifiée (pas de trous)", "categorie": "bagages", "quand": "j-7"},
        {
            "libelle": "Sacs de couchage + matelas gonflables",
            "categorie": "bagages",
            "quand": "j-3",
        },
        {"libelle": "Réchaud + gaz + briquets", "categorie": "bagages", "quand": "j-3"},
        {"libelle": "Glacière + pains de glace", "categorie": "bagages", "quand": "j-1"},
        {"libelle": "Lampes frontales + piles de rechange", "categorie": "bagages", "quand": "j-1"},
        {"libelle": "Anti-moustiques", "categorie": "bagages", "quand": "j-1"},
    ],
}


class ChecklistsCrudService(EventBusMixin, BaseService[ChecklistVacances]):
    """Service CRUD pour les checklists vacances."""

    _event_source = "checklists"

    def __init__(self):
        super().__init__(model=ChecklistVacances, cache_ttl=300)

    @chronometre("maison.checklists.lister", seuil_alerte_ms=1500)
    @avec_cache(ttl=300)
    @avec_session_db
    @avec_gestion_erreurs(default_return=[])
    def get_all_checklists(
        self,
        inclure_archivees: bool = False,
        db: Session | None = None,
    ) -> list[ChecklistVacances]:
        """Récupère toutes les checklists."""
        query = db.query(ChecklistVacances)
        if not inclure_archivees:
            query = query.filter(ChecklistVacances.archivee.is_(False))
        return query.order_by(ChecklistVacances.id.desc()).all()

    @avec_cache(ttl=300)
    @avec_session_db
    @avec_gestion_erreurs(default_return=None)
    def get_checklist_by_id(
        self, checklist_id: int, db: Session | None = None
    ) -> ChecklistVacances | None:
        """Récupère une checklist avec ses items."""
        return db.query(ChecklistVacances).filter(ChecklistVacances.id == checklist_id).first()

    @avec_session_db
    def create_checklist(self, data: dict, db: Session | None = None) -> ChecklistVacances:
        """Crée une nouvelle checklist."""
        checklist = ChecklistVacances(**data)
        db.add(checklist)
        db.commit()
        db.refresh(checklist)
        logger.info(f"Checklist créée: {checklist.id} - {checklist.nom}")
        self._emettre_evenement(
            "checklists.modifie",
            {"checklist_id": checklist.id, "nom": checklist.nom, "action": "cree"},
        )
        return checklist

    @avec_session_db
    def create_from_template(
        self,
        nom: str,
        type_voyage: str,
        destination: str | None = None,
        date_depart=None,
        date_retour=None,
        db: Session | None = None,
    ) -> ChecklistVacances:
        """Crée une checklist à partir d'un template prédéfini."""
        checklist = ChecklistVacances(
            nom=nom,
            type_voyage=type_voyage,
            destination=destination,
            date_depart=date_depart,
            date_retour=date_retour,
        )
        db.add(checklist)
        db.flush()

        template_items = TEMPLATES_CHECKLIST.get(type_voyage, [])
        for i, item_data in enumerate(template_items):
            item = ItemChecklist(
                checklist_id=checklist.id,
                libelle=item_data["libelle"],
                categorie=item_data["categorie"],
                ordre=i,
                quand=item_data.get("quand"),
            )
            db.add(item)

        db.commit()
        db.refresh(checklist)
        logger.info(f"Checklist créée depuis template '{type_voyage}': {checklist.id}")
        return checklist

    @avec_session_db
    def delete_checklist(self, checklist_id: int, db: Session | None = None) -> bool:
        """Supprime une checklist et ses items."""
        checklist = db.query(ChecklistVacances).filter(ChecklistVacances.id == checklist_id).first()
        if checklist is None:
            return False
        db.delete(checklist)
        db.commit()
        return True

    # ── Items ──

    @avec_cache(ttl=300)
    @avec_session_db
    @avec_gestion_erreurs(default_return=[])
    def get_items(self, checklist_id: int, db: Session | None = None) -> list[ItemChecklist]:
        """Récupère les items d'une checklist."""
        return (
            db.query(ItemChecklist)
            .filter(ItemChecklist.checklist_id == checklist_id)
            .order_by(ItemChecklist.categorie, ItemChecklist.ordre)
            .all()
        )

    @avec_session_db
    def add_item(self, data: dict, db: Session | None = None) -> ItemChecklist:
        """Ajoute un item à une checklist."""
        item = ItemChecklist(**data)
        db.add(item)
        db.commit()
        db.refresh(item)
        return item

    @avec_session_db
    def toggle_item(self, item_id: int, db: Session | None = None) -> ItemChecklist | None:
        """Bascule le statut fait/non fait d'un item."""
        item = db.query(ItemChecklist).filter(ItemChecklist.id == item_id).first()
        if item is None:
            return None
        item.fait = not item.fait
        db.commit()
        db.refresh(item)
        return item

    @avec_session_db
    def delete_item(self, item_id: int, db: Session | None = None) -> bool:
        """Supprime un item."""
        item = db.query(ItemChecklist).filter(ItemChecklist.id == item_id).first()
        if item is None:
            return False
        db.delete(item)
        db.commit()
        return True

    def get_templates_disponibles(self) -> list[dict]:
        """Liste les templates de checklists disponibles."""
        return [{"type_voyage": k, "nb_items": len(v)} for k, v in TEMPLATES_CHECKLIST.items()]


# ═══════════════════════════════════════════════════════════
# FACTORY
# ═══════════════════════════════════════════════════════════


@service_factory("checklists_crud", tags={"maison", "crud", "checklists"})
def get_checklists_crud_service() -> ChecklistsCrudService:
    """Factory singleton pour le service CRUD checklists."""
    return ChecklistsCrudService()


def obtenir_service_checklists_crud() -> ChecklistsCrudService:
    """Factory française pour le service CRUD checklists."""
    return get_checklists_crud_service()
