"""
Mixin de persistance base de données pour le service météo.

Fournit les méthodes CRUD pour les alertes météo et la configuration,
extraites de ServiceMeteo pour une meilleure séparation des responsabilités.
"""

import logging
from datetime import date, timedelta
from decimal import Decimal
from uuid import UUID

from sqlalchemy.orm import Session

from src.core.decorators import avec_session_db
from src.core.models import (
    AlerteMeteo as AlerteMeteoModel,
)
from src.core.models import (
    ConfigMeteo,
)

from .types import AlerteMeteo

logger = logging.getLogger(__name__)

__all__ = ["MeteoPersistenceMixin"]


class MeteoPersistenceMixin:
    """
    Mixin fournissant la persistance base de données pour le service météo.

    Méthodes:
    - sauvegarder_alerte: Sauvegarde une alerte dans la BD
    - sauvegarder_alertes: Sauvegarde plusieurs alertes en batch
    - lister_alertes_actives: Liste les alertes non lues
    - marquer_alerte_lue: Marque une alerte comme lue
    - obtenir_config_meteo: Récupère la config utilisateur
    - sauvegarder_config_meteo: Crée ou met à jour la config utilisateur
    """

    @avec_session_db
    def sauvegarder_alerte(
        self,
        alerte: AlerteMeteo,
        user_id: UUID | str | None = None,
        db: Session = None,
    ) -> AlerteMeteoModel | None:
        """
        Sauvegarde une alerte météo dans la base de données.

        Args:
            alerte: Alerte Pydantic à sauvegarder
            user_id: UUID de l'utilisateur (optionnel)
            db: Session SQLAlchemy (injectée)

        Returns:
            Modèle AlerteMeteo créé
        """
        try:
            db_alerte = AlerteMeteoModel(
                type_alerte=alerte.type_alerte.value,
                niveau=alerte.niveau.value,
                titre=alerte.titre,
                message=alerte.message,
                conseil_jardin=alerte.conseil_jardin,
                date_debut=alerte.date_debut,
                date_fin=alerte.date_fin,
                temperature=Decimal(str(alerte.temperature)) if alerte.temperature else None,
                user_id=UUID(str(user_id)) if user_id else None,
            )
            db.add(db_alerte)
            db.commit()
            db.refresh(db_alerte)
            logger.info(f"Alerte météo sauvegardée: {db_alerte.id}")
            return db_alerte
        except Exception as e:
            logger.error(f"Erreur sauvegarde alerte météo: {e}")
            db.rollback()
            return None

    @avec_session_db
    def sauvegarder_alertes(
        self,
        alertes: list[AlerteMeteo],
        user_id: UUID | str | None = None,
        db: Session = None,
    ) -> list[AlerteMeteoModel]:
        """
        Sauvegarde plusieurs alertes météo.

        Args:
            alertes: Liste d'alertes à sauvegarder
            user_id: UUID de l'utilisateur
            db: Session SQLAlchemy

        Returns:
            Liste des modèles créés
        """
        resultats = []
        for alerte in alertes:
            db_alerte = AlerteMeteoModel(
                type_alerte=alerte.type_alerte.value,
                niveau=alerte.niveau.value,
                titre=alerte.titre,
                message=alerte.message,
                conseil_jardin=alerte.conseil_jardin,
                date_debut=alerte.date_debut,
                date_fin=alerte.date_fin,
                temperature=Decimal(str(alerte.temperature)) if alerte.temperature else None,
                user_id=UUID(str(user_id)) if user_id else None,
            )
            db.add(db_alerte)
            resultats.append(db_alerte)

        try:
            db.commit()
            for r in resultats:
                db.refresh(r)
            logger.info(f"{len(resultats)} alertes météo sauvegardées")
        except Exception as e:
            logger.error(f"Erreur sauvegarde alertes: {e}")
            db.rollback()
            return []

        return resultats

    @avec_session_db
    def lister_alertes_actives(
        self,
        user_id: UUID | str | None = None,
        db: Session = None,
    ) -> list[AlerteMeteoModel]:
        """
        Liste les alertes actives (non lues, date pas dépassée).

        Args:
            user_id: UUID de l'utilisateur (filtre optionnel)
            db: Session SQLAlchemy

        Returns:
            Liste des alertes actives
        """
        query = db.query(AlerteMeteoModel).filter(
            AlerteMeteoModel.lu == False,
            AlerteMeteoModel.date_debut >= date.today() - timedelta(days=1),
        )

        if user_id:
            query = query.filter(AlerteMeteoModel.user_id == UUID(str(user_id)))

        return query.order_by(AlerteMeteoModel.date_debut).all()

    @avec_session_db
    def marquer_alerte_lue(
        self,
        alerte_id: int,
        db: Session = None,
    ) -> bool:
        """
        Marque une alerte comme lue.

        Args:
            alerte_id: ID de l'alerte
            db: Session SQLAlchemy

        Returns:
            True si succès
        """
        alerte = db.query(AlerteMeteoModel).filter(AlerteMeteoModel.id == alerte_id).first()
        if alerte:
            alerte.lu = True
            db.commit()
            return True
        return False

    @avec_session_db
    def obtenir_config_meteo(
        self,
        user_id: UUID | str,
        db: Session = None,
    ) -> ConfigMeteo | None:
        """
        Récupère la configuration météo d'un utilisateur.

        Args:
            user_id: UUID de l'utilisateur
            db: Session SQLAlchemy

        Returns:
            Configuration ou None
        """
        return db.query(ConfigMeteo).filter(ConfigMeteo.user_id == UUID(str(user_id))).first()

    @avec_session_db
    def sauvegarder_config_meteo(
        self,
        user_id: UUID | str,
        latitude: float | None = None,
        longitude: float | None = None,
        ville: str | None = None,
        surface_jardin: float | None = None,
        db: Session = None,
    ) -> ConfigMeteo:
        """
        Crée ou met à jour la configuration météo d'un utilisateur.

        Args:
            user_id: UUID de l'utilisateur
            latitude, longitude: Coordonnées
            ville: Nom de la ville
            surface_jardin: Surface en m²
            db: Session SQLAlchemy

        Returns:
            Configuration créée ou mise à jour
        """
        config = db.query(ConfigMeteo).filter(ConfigMeteo.user_id == UUID(str(user_id))).first()

        if not config:
            config = ConfigMeteo(user_id=UUID(str(user_id)))
            db.add(config)

        if latitude is not None:
            config.latitude = Decimal(str(latitude))
        if longitude is not None:
            config.longitude = Decimal(str(longitude))
        if ville is not None:
            config.ville = ville
        if surface_jardin is not None:
            config.surface_jardin_m2 = Decimal(str(surface_jardin))

        db.commit()
        db.refresh(config)
        return config
