"""
Mixin CRUD Jardin — Opérations base de données du service jardin.

Extrait de jardin_service.py pour maintenir chaque fichier sous 500 LOC.
Contient:
- CRUD plantes (obtenir, ajouter, arroser)
- Requêtes arrosage et récoltes
- Statistiques jardin
- CRUD zones jardin (charger, mettre à jour, photos)
- Logs d'activité jardin
"""

from __future__ import annotations

import logging
from datetime import date, timedelta

from sqlalchemy.orm import Session

from src.core.decorators import avec_cache, avec_session_db
from src.core.models import ElementJardin
from src.core.monitoring import chronometre
from src.services.core.events import obtenir_bus

logger = logging.getLogger(__name__)


class JardinCrudMixin:
    """Mixin fournissant les opérations CRUD du service jardin.

    Toutes les méthodes utilisent @avec_session_db pour l'injection de session.
    """

    # ─────────────────────────────────────────────────────────
    # ÉMISSION D'ÉVÉNEMENTS
    # ─────────────────────────────────────────────────────────

    @staticmethod
    def emettre_modification(
        element_id: int = 0,
        nom: str = "",
        action: str = "modifie",
    ) -> None:
        """Émet un événement jardin.modifie pour déclencher l'invalidation de cache.

        Args:
            element_id: ID de l'élément
            nom: Nom de l'élément
            action: "plante_ajoutee", "arrosage", "recolte", "supprime"
        """
        obtenir_bus().emettre(
            "jardin.modifie",
            {"element_id": element_id, "nom": nom, "action": action},
            source="jardin",
        )

    # ─────────────────────────────────────────────────────────
    # LECTURE PLANTES
    # ─────────────────────────────────────────────────────────

    @chronometre(nom="jardin.obtenir_plantes", seuil_alerte_ms=1500)
    @chronometre("maison.jardin.plantes", seuil_alerte_ms=1500)
    @avec_cache(ttl=300)
    @avec_session_db
    def obtenir_plantes(self, db: Session | None = None) -> list[ElementJardin]:
        """Récupère toutes les plantes du jardin.

        Args:
            db: Session DB (injectée automatiquement par @avec_session_db)

        Returns:
            Liste des plantes
        """
        return db.query(ElementJardin).all()

    def get_plantes(self, db: Session | None = None) -> list[ElementJardin]:
        """Alias anglais pour obtenir_plantes (rétrocompatibilité)."""
        return self.obtenir_plantes(db)

    @chronometre(nom="jardin.plantes_a_arroser", seuil_alerte_ms=1500)
    @avec_cache(ttl=300)
    @avec_session_db
    def obtenir_plantes_a_arroser(self, db: Session | None = None) -> list[ElementJardin]:
        """Récupère les plantes nécessitant arrosage.

        Args:
            db: Session DB (injectée automatiquement par @avec_session_db)

        Returns:
            Liste des plantes à arroser
        """
        return self._query_plantes_arrosage(db)

    def get_plantes_a_arroser(self, db: Session | None = None) -> list[ElementJardin]:
        """Alias anglais pour obtenir_plantes_a_arroser (rétrocompatibilité)."""
        return self.obtenir_plantes_a_arroser(db)

    def _query_plantes_arrosage(self, db: Session) -> list[ElementJardin]:
        """Query interne pour plantes à arroser."""
        seuil = date.today() - timedelta(days=3)
        return (
            db.query(ElementJardin)
            .filter(
                (ElementJardin.dernier_arrosage < seuil)
                | (ElementJardin.dernier_arrosage.is_(None))
            )
            .all()
        )

    @avec_cache(ttl=300)
    @avec_session_db
    def obtenir_recoltes_proches(self, db: Session | None = None) -> list[ElementJardin]:
        """Récupère les plantes à récolter dans les 7 prochains jours.

        Args:
            db: Session DB (injectée automatiquement par @avec_session_db)

        Returns:
            Liste des plantes à récolter bientôt.
        """
        today = date.today()
        dans_7_jours = today + timedelta(days=7)
        return (
            db.query(ElementJardin)
            .filter(
                ElementJardin.date_recolte_prevue.isnot(None),
                ElementJardin.date_recolte_prevue >= today,
                ElementJardin.date_recolte_prevue <= dans_7_jours,
            )
            .all()
        )

    def get_recoltes_proches(self, db: Session | None = None) -> list[ElementJardin]:
        """Alias anglais pour obtenir_recoltes_proches (rétrocompatibilité)."""
        return self.obtenir_recoltes_proches(db)

    @avec_cache(ttl=300)
    @avec_session_db
    def obtenir_stats_jardin(self, db: Session | None = None) -> dict:
        """Calcule les statistiques du jardin.

        Args:
            db: Session DB (injectée automatiquement par @avec_session_db)

        Returns:
            Dict avec total_plantes, a_arroser, recoltes_proches, categories.
        """
        total = db.query(ElementJardin).filter(ElementJardin.statut == "actif").count()
        plantes_arroser = len(self._query_plantes_arrosage(db))

        today = date.today()
        dans_7_jours = today + timedelta(days=7)
        recoltes_proches = (
            db.query(ElementJardin)
            .filter(
                ElementJardin.date_recolte_prevue.isnot(None),
                ElementJardin.date_recolte_prevue >= today,
                ElementJardin.date_recolte_prevue <= dans_7_jours,
            )
            .count()
        )

        from sqlalchemy import func

        categories = (
            db.query(func.count(func.distinct(ElementJardin.type)))
            .filter(ElementJardin.statut == "actif")
            .scalar()
            or 0
        )

        return {
            "total_plantes": total,
            "a_arroser": plantes_arroser,
            "recoltes_proches": recoltes_proches,
            "categories": categories,
        }

    def get_stats_jardin(self, db: Session | None = None) -> dict:
        """Alias anglais pour obtenir_stats_jardin (rétrocompatibilité)."""
        return self.obtenir_stats_jardin(db)

    # ─────────────────────────────────────────────────────────
    # CRUD PLANTES
    # ─────────────────────────────────────────────────────────

    @avec_session_db
    def ajouter_plante(
        self,
        nom: str,
        type_plante: str,
        db: Session | None = None,
        **kwargs,
    ) -> ElementJardin | None:
        """Ajoute une plante au jardin.

        Args:
            nom: Nom de la plante
            type_plante: Type (legume, fruit, fleur, etc.)
            db: Session DB (injectée par @avec_session_db)
            **kwargs: Champs additionnels (zone_id, date_plantation, etc.)

        Returns:
            ElementJardin créé, ou None en cas d'erreur.
        """
        try:
            plante = ElementJardin(nom=nom, type_plante=type_plante, **kwargs)
            db.add(plante)
            db.commit()
            db.refresh(plante)
            logger.info(f"✅ Plante ajoutée: {nom}")
            return plante
        except Exception as e:
            logger.error(f"Erreur ajout plante: {e}")
            db.rollback()
            return None

    @avec_session_db
    def ajouter_zone(
        self,
        nom: str,
        type_zone: str = "autre",
        superficie_m2: float | None = None,
        description: str | None = None,
        db: Session | None = None,
        **kwargs,
    ) -> dict | None:
        """Crée une nouvelle zone jardin et retourne un dict minimal.

        Args:
            nom: Nom de la zone
            type_zone: Type (pelouse, potager, arbres, ...)
            superficie_m2: Surface en m²
            description: Description libre
        Returns:
            Dictionnaire représentant la zone créée ou None en cas d'erreur.
        """
        try:
            from src.core.models.temps_entretien import ZoneJardin

            zone = ZoneJardin(
                nom=nom,
                type_zone=type_zone,
                superficie_m2=superficie_m2,
                description=description,
                etat_note=3,
            )
            db.add(zone)
            db.commit()
            db.refresh(zone)
            logger.info(f"✅ Zone créée: {zone.nom} (id={zone.id})")
            # return a minimal dict compatible with loader
            return {
                "id": zone.id,
                "nom": zone.nom,
                "type_zone": zone.type_zone,
                "etat_note": zone.etat_note,
                "surface_m2": float(zone.superficie_m2) if zone.superficie_m2 is not None else 0,
                "etat_description": zone.etat_description or "",
                "photos_url": zone.photos_url or [],
            }
        except Exception as e:
            logger.error(f"Erreur création zone: {e}")
            db.rollback()
            return None

    @avec_session_db
    def arroser_plante(self, plante_id: int, db: Session | None = None) -> bool:
        """Enregistre un arrosage pour une plante.

        Args:
            plante_id: ID de la plante
            db: Session DB (injectée par @avec_session_db)

        Returns:
            True si l'arrosage a été enregistré.
        """
        try:
            from src.core.models.maison import JournalJardin

            log = JournalJardin(garden_item_id=plante_id, action="arrosage")
            db.add(log)
            db.commit()
            logger.info(f"✅ Arrosage enregistré pour plante {plante_id}")
            return True
        except Exception as e:
            logger.error(f"Erreur arrosage: {e}")
            db.rollback()
            return False

    @avec_session_db
    def ajouter_log_jardin(
        self,
        plante_id: int,
        action: str,
        notes: str = "",
        db: Session | None = None,
    ) -> bool:
        """Ajoute un log d'activité pour une plante.

        Args:
            plante_id: ID de la plante
            action: Type d'action (arrosage, taille, recolte, etc.)
            notes: Notes additionnelles
            db: Session DB (injectée par @avec_session_db)

        Returns:
            True si le log a été enregistré.
        """
        try:
            from src.core.models.maison import JournalJardin

            log = JournalJardin(
                garden_item_id=plante_id,
                action=action,
                notes=notes,
            )
            db.add(log)
            db.commit()
            logger.info(f"✅ Log jardin ajouté: {action} pour plante {plante_id}")
            return True
        except Exception as e:
            logger.error(f"Erreur log jardin: {e}")
            db.rollback()
            return False

    # ─────────────────────────────────────────────────────────
    # CRUD ZONES JARDIN
    # ─────────────────────────────────────────────────────────

    @avec_session_db
    def charger_zones(self, db: Session | None = None) -> list[dict]:
        """Charge toutes les zones du jardin depuis la DB.

        Args:
            db: Session DB (injectée par @avec_session_db)

        Returns:
            Liste de dicts avec: id, nom, type_zone, etat_note, superficie,
            commentaire, photos.
        """
        try:
            from src.core.models.temps_entretien import ZoneJardin

            zones = db.query(ZoneJardin).all()
            result = []
            for z in zones:
                result.append(
                    {
                        "id": z.id,
                        "nom": z.nom,
                        "type_zone": getattr(z, "type_zone", "autre"),
                        "etat_note": getattr(z, "etat_note", None) or 3,
                        "surface_m2": getattr(z, "surface_m2", None)
                        or getattr(z, "superficie", None)
                        or 0,
                        "etat_description": getattr(z, "etat_description", None)
                        or getattr(z, "commentaire", None)
                        or "",
                        "objectif": getattr(z, "objectif", None) or "",
                        "prochaine_action": getattr(z, "prochaine_action", None) or "",
                        "date_prochaine_action": getattr(z, "date_prochaine_action", None),
                        "photos_url": getattr(z, "photos_url", None)
                        or getattr(z, "photos", None)
                        or [],
                        "budget_estime": getattr(z, "budget_estime", None) or 0,
                    }
                )
            return result
        except Exception as e:
            logger.error(f"Erreur chargement zones: {e}")
            return []

    @avec_session_db
    def mettre_a_jour_zone(
        self,
        zone_id: int,
        updates: dict,
        db: Session | None = None,
    ) -> bool:
        """Met à jour une zone du jardin.

        Args:
            zone_id: ID de la zone.
            updates: Dict des champs à mettre à jour.
            db: Session DB (injectée par @avec_session_db)

        Returns:
            True si la mise à jour a réussi.
        """
        try:
            from src.core.models.temps_entretien import ZoneJardin

            zone = db.query(ZoneJardin).filter_by(id=zone_id).first()
            if zone is None:
                logger.warning(f"Zone {zone_id} non trouvée")
                return False
            for key, value in updates.items():
                setattr(zone, key, value)
            db.commit()
            logger.info(f"✅ Zone {zone_id} mise à jour")
            return True
        except Exception as e:
            logger.error(f"Erreur mise à jour zone: {e}")
            db.rollback()
            return False

    @avec_session_db
    def ajouter_photo_zone(
        self,
        zone_id: int,
        url: str,
        est_avant: bool = True,
        db: Session | None = None,
    ) -> bool:
        """Ajoute une photo à une zone.

        Args:
            zone_id: ID de la zone.
            url: URL de la photo.
            est_avant: True pour photo 'avant', False pour 'après'.
            db: Session DB (injectée par @avec_session_db)

        Returns:
            True si l'ajout a réussi.
        """
        try:
            from src.core.models.temps_entretien import ZoneJardin

            prefix = "avant:" if est_avant else "apres:"
            photo_entry = f"{prefix}{url}"

            zone = db.query(ZoneJardin).filter_by(id=zone_id).first()
            if zone is None:
                logger.warning(f"Zone {zone_id} non trouvée")
                return False
            photos = zone.photos_url if zone.photos_url is not None else []
            photos.append(photo_entry)
            zone.photos_url = photos
            db.commit()
            logger.info(f"✅ Photo ajoutée à zone {zone_id}")
            return True
        except Exception as e:
            logger.error(f"Erreur ajout photo: {e}")
            db.rollback()
            return False
