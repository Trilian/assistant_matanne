"""
Service Voyage Famille - Gestion des voyages, checklists et templates.

Opérations:
- CRUD voyages avec budget
- Checklists de voyage avec progression
- Templates de checklists pré-remplies
- Import depuis fichier JSON de référence
"""

import json
import logging
from datetime import date as date_type
from pathlib import Path
from typing import Any, TypedDict

from sqlalchemy import func
from sqlalchemy.orm import Session

from src.core.decorators import avec_cache, avec_gestion_erreurs, avec_session_db
from src.core.models import ChecklistVoyage, TemplateChecklist, Voyage
from src.core.monitoring import chronometre
from src.services.core.base import BaseService
from src.services.core.events import obtenir_bus
from src.services.core.registry import service_factory

logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).resolve().parents[3] / "data"


class ResumeVoyageDict(TypedDict):
    """Résumé d'un voyage pour le dashboard."""

    id: int
    titre: str
    destination: str
    date_depart: str
    jours_restants: int | None
    preparation_pct: float
    budget_restant: float | None


class ServiceVoyage(BaseService[Voyage]):
    """Service de gestion des voyages famille.

    Hérite de BaseService[Voyage] pour le CRUD générique.
    """

    def __init__(self):
        super().__init__(model=Voyage, cache_ttl=300)

    # ═══════════════════════════════════════════════════════════
    # VOYAGES
    # ═══════════════════════════════════════════════════════════

    @chronometre("voyage.liste", seuil_alerte_ms=1000)
    @avec_cache(ttl=300)
    @avec_gestion_erreurs(default_return=[])
    @avec_session_db
    def obtenir_voyages(
        self,
        *,
        statut: str | None = None,
        db: Session | None = None,
    ) -> list[Voyage]:
        """Récupère les voyages, filtrés optionnellement par statut."""
        if db is None:
            return []
        query = db.query(Voyage)
        if statut:
            query = query.filter_by(statut=statut)
        return query.order_by(Voyage.date_depart.desc()).all()

    @avec_gestion_erreurs(default_return=None)
    @avec_session_db
    def ajouter_voyage(self, data: dict[str, Any], *, db: Session | None = None) -> Voyage | None:
        """Ajoute un voyage."""
        if db is None:
            return None
        voyage = Voyage(**data)
        db.add(voyage)
        db.commit()
        db.refresh(voyage)
        logger.info("Voyage ajouté: %s → %s", voyage.titre, voyage.destination)
        obtenir_bus().emettre(
            "voyage.ajoute",
            {"voyage_id": voyage.id, "titre": voyage.titre},
            source="ServiceVoyage",
        )
        return voyage

    @avec_gestion_erreurs(default_return=False)
    @avec_session_db
    def modifier_voyage(
        self, voyage_id: int, data: dict[str, Any], *, db: Session | None = None
    ) -> bool:
        """Modifie un voyage existant."""
        if db is None:
            return False
        voyage = db.query(Voyage).get(voyage_id)
        if not voyage:
            return False
        for key, value in data.items():
            if hasattr(voyage, key):
                setattr(voyage, key, value)
        db.commit()
        return True

    @avec_gestion_erreurs(default_return=False)
    @avec_session_db
    def supprimer_voyage(self, voyage_id: int, *, db: Session | None = None) -> bool:
        """Supprime un voyage et ses checklists associées."""
        if db is None:
            return False
        deleted = db.query(Voyage).filter_by(id=voyage_id).delete()
        db.commit()
        return deleted > 0

    @avec_gestion_erreurs(default_return=None)
    @avec_session_db
    def obtenir_voyage(self, voyage_id: int, *, db: Session | None = None) -> Voyage | None:
        """Récupère un voyage par ID."""
        if db is None:
            return None
        return db.query(Voyage).get(voyage_id)

    # ═══════════════════════════════════════════════════════════
    # CHECKLISTS
    # ═══════════════════════════════════════════════════════════

    @avec_cache(ttl=300)
    @avec_gestion_erreurs(default_return=[])
    @avec_session_db
    def obtenir_checklists(
        self, voyage_id: int, *, db: Session | None = None
    ) -> list[ChecklistVoyage]:
        """Récupère les checklists d'un voyage."""
        if db is None:
            return []
        return (
            db.query(ChecklistVoyage)
            .filter_by(voyage_id=voyage_id)
            .order_by(ChecklistVoyage.nom.asc())
            .all()
        )

    @avec_gestion_erreurs(default_return=None)
    @avec_session_db
    def creer_checklist(
        self, data: dict[str, Any], *, db: Session | None = None
    ) -> ChecklistVoyage | None:
        """Crée une checklist pour un voyage."""
        if db is None:
            return None
        checklist = ChecklistVoyage(**data)
        db.add(checklist)
        db.commit()
        db.refresh(checklist)
        logger.info("Checklist créée: %s pour voyage %d", checklist.nom, checklist.voyage_id)
        return checklist

    @avec_gestion_erreurs(default_return=None)
    @avec_session_db
    def creer_checklist_depuis_template(
        self,
        voyage_id: int,
        template_id: int,
        *,
        db: Session | None = None,
    ) -> ChecklistVoyage | None:
        """Crée une checklist à partir d'un template pré-rempli."""
        if db is None:
            return None
        template = db.query(TemplateChecklist).get(template_id)
        if not template:
            logger.warning("Template %d non trouvé", template_id)
            return None

        # Copier les articles du template avec statut non-coché
        articles = []
        for article in template.articles or []:
            articles.append({**article, "fait": False})

        checklist = ChecklistVoyage(
            voyage_id=voyage_id,
            template_id=template_id,
            nom=template.nom,
            articles=articles,
        )
        db.add(checklist)
        db.commit()
        db.refresh(checklist)
        logger.info(
            "Checklist créée depuis template '%s' pour voyage %d",
            template.nom,
            voyage_id,
        )
        return checklist

    @avec_gestion_erreurs(default_return=False)
    @avec_session_db
    def cocher_article(
        self,
        checklist_id: int,
        index_article: int,
        fait: bool = True,
        *,
        db: Session | None = None,
    ) -> bool:
        """Coche/décoche un article dans une checklist."""
        if db is None:
            return False
        checklist = db.query(ChecklistVoyage).get(checklist_id)
        if not checklist or not checklist.articles:
            return False
        articles = list(checklist.articles)
        if 0 <= index_article < len(articles):
            articles[index_article]["fait"] = fait
            checklist.articles = articles
            db.commit()
            return True
        return False

    # ═══════════════════════════════════════════════════════════
    # TEMPLATES
    # ═══════════════════════════════════════════════════════════

    @avec_cache(ttl=3600)
    @avec_gestion_erreurs(default_return=[])
    @avec_session_db
    def obtenir_templates(self, *, db: Session | None = None) -> list[TemplateChecklist]:
        """Récupère tous les templates de checklists."""
        if db is None:
            return []
        return db.query(TemplateChecklist).order_by(TemplateChecklist.nom.asc()).all()

    def charger_templates_defaut(self) -> list[dict[str, Any]]:
        """Charge les templates par défaut depuis le fichier JSON."""
        chemin = DATA_DIR / "templates_checklist_voyage.json"
        if not chemin.exists():
            logger.warning("Fichier templates voyage non trouvé: %s", chemin)
            return []
        with open(chemin, encoding="utf-8") as f:
            data = json.load(f)
        return data.get("templates", [])

    @avec_gestion_erreurs(default_return=0)
    @avec_session_db
    def importer_templates_defaut(self, *, db: Session | None = None) -> int:
        """Importe les templates par défaut dans la base de données."""
        if db is None:
            return 0
        templates_data = self.charger_templates_defaut()
        count = 0
        for tpl in templates_data:
            # Vérifier si le template existe déjà
            existant = db.query(TemplateChecklist).filter_by(nom=tpl["nom"]).first()
            if existant:
                continue
            template = TemplateChecklist(
                nom=tpl["nom"],
                type_voyage=tpl.get("type_voyage"),
                description=tpl.get("description", ""),
                articles=tpl.get("articles", []),
                est_defaut=True,
            )
            db.add(template)
            count += 1
        db.commit()
        logger.info("%d templates voyage importés", count)
        return count

    # ═══════════════════════════════════════════════════════════
    # RÉSUMÉS
    # ═══════════════════════════════════════════════════════════

    @avec_cache(ttl=300)
    @avec_gestion_erreurs(default_return=[])
    @avec_session_db
    def obtenir_resumes_voyages(self, *, db: Session | None = None) -> list[ResumeVoyageDict]:
        """Résumés de tous les voyages pour le dashboard."""
        if db is None:
            return []
        voyages = (
            db.query(Voyage)
            .filter(Voyage.statut.in_(["planifie", "en_cours"]))
            .order_by(Voyage.date_depart.asc())
            .all()
        )
        resumes: list[ResumeVoyageDict] = []
        aujourd_hui = date_type.today()

        for v in voyages:
            # Calculer la progression des checklists
            checklists = db.query(ChecklistVoyage).filter_by(voyage_id=v.id).all()
            total_articles = 0
            articles_faits = 0
            for cl in checklists:
                for article in cl.articles or []:
                    total_articles += 1
                    if article.get("fait"):
                        articles_faits += 1

            pct = (articles_faits / total_articles * 100) if total_articles > 0 else 0.0
            jours = (v.date_depart - aujourd_hui).days if v.date_depart >= aujourd_hui else None

            budget_restant = None
            if v.budget_prevu is not None:
                depense = float(v.budget_depense or 0)
                budget_restant = float(v.budget_prevu) - depense

            resumes.append(
                ResumeVoyageDict(
                    id=v.id,
                    titre=v.titre,
                    destination=v.destination,
                    date_depart=v.date_depart.isoformat(),
                    jours_restants=jours,
                    preparation_pct=round(pct, 1),
                    budget_restant=budget_restant,
                )
            )

        return resumes


# ═══════════════════════════════════════════════════════════
# FACTORY
# ═══════════════════════════════════════════════════════════


@service_factory("voyage", tags={"famille", "voyage"})
def obtenir_service_voyage() -> ServiceVoyage:
    """Factory pour le service voyage (singleton via ServiceRegistry)."""
    return ServiceVoyage()


# Alias anglais
get_voyage_service = obtenir_service_voyage
