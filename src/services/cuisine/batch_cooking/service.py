"""
Service Batch Cooking - Gestion des sessions de préparation de repas en lot.

Ce service gère :
- Configuration du batch cooking (jours, robots, préférences)
- Sessions de batch cooking (planification, exécution, suivi)
- Génération IA des plans optimisés (via BatchCookingIAMixin)
- Gestion des préparations stockées (via BatchCookingStatsMixin)

✅ Utilise @avec_session_db et @avec_cache
✅ Validation Pydantic centralisée
✅ Intégration IA pour optimisation
"""

import logging
from datetime import date, datetime, time
from typing import Any

from sqlalchemy.orm import Session, joinedload

from src.core.ai import obtenir_client_ia
from src.core.caching import Cache
from src.core.decorators import avec_cache, avec_gestion_erreurs, avec_session_db
from src.core.errors_base import ErreurNonTrouve, ErreurValidation
from src.core.models import (
    ConfigBatchCooking,
    EtapeBatchCooking,
    SessionBatchCooking,
    StatutEtapeEnum,
    StatutSessionEnum,
)
from src.services.core.base import BaseAIService, BaseService

from .batch_cooking_ia import BatchCookingIAMixin
from .batch_cooking_stats import BatchCookingStatsMixin

logger = logging.getLogger(__name__)


class ServiceBatchCooking(
    BatchCookingIAMixin,
    BatchCookingStatsMixin,
    BaseService[SessionBatchCooking],
    BaseAIService,
):
    """
    Service complet pour le batch cooking.

    Fonctionnalités:
    - Configuration utilisateur (jours, robots, préférences)
    - Sessions batch cooking (création, exécution, suivi)
    - Génération IA de plans optimisés (BatchCookingIAMixin)
    - Gestion des préparations stockées (BatchCookingStatsMixin)
    - Intégration avec le planning hebdomadaire (BatchCookingStatsMixin)
    """

    def __init__(self):
        BaseService.__init__(self, SessionBatchCooking, cache_ttl=1800)
        BaseAIService.__init__(
            self,
            client=obtenir_client_ia(),
            cache_prefix="batch_cooking",
            default_ttl=1800,
            default_temperature=0.6,
            service_name="batch_cooking",
        )

    # ═══════════════════════════════════════════════════════════
    # SECTION 1: CONFIGURATION
    # ═══════════════════════════════════════════════════════════

    @avec_gestion_erreurs(default_return=None)
    @avec_cache(ttl=3600, key_func=lambda self: "batch_config")
    @avec_session_db
    def get_config(self, db: Session | None = None) -> ConfigBatchCooking | None:
        """Récupère la configuration batch cooking (singleton)."""
        config = db.query(ConfigBatchCooking).first()
        if not config:
            # Créer config par défaut
            config = ConfigBatchCooking(
                jours_batch=[6],  # Dimanche
                heure_debut_preferee=time(10, 0),
                duree_max_session=180,
                avec_jules_par_defaut=True,
                robots_disponibles=["four", "plaques", "cookeo"],
                objectif_portions_semaine=20,
            )
            db.add(config)
            db.commit()
            db.refresh(config)
        return config

    @avec_gestion_erreurs(default_return=None)
    @avec_session_db
    def update_config(
        self,
        jours_batch: list[int] | None = None,
        heure_debut: time | None = None,
        duree_max: int | None = None,
        avec_jules: bool | None = None,
        robots: list[str] | None = None,
        objectif_portions: int | None = None,
        db: Session | None = None,
    ) -> ConfigBatchCooking | None:
        """Met à jour la configuration batch cooking."""
        config = db.query(ConfigBatchCooking).first()
        if not config:
            config = ConfigBatchCooking()
            db.add(config)

        if jours_batch is not None:
            config.jours_batch = jours_batch
        if heure_debut is not None:
            config.heure_debut_preferee = heure_debut
        if duree_max is not None:
            config.duree_max_session = duree_max
        if avec_jules is not None:
            config.avec_jules_par_defaut = avec_jules
        if robots is not None:
            config.robots_disponibles = robots
        if objectif_portions is not None:
            config.objectif_portions_semaine = objectif_portions

        db.commit()
        db.refresh(config)

        # Invalider cache
        Cache.invalider(pattern="batch_config")

        logger.info("✅ Configuration batch cooking mise à jour")
        return config

    # ═══════════════════════════════════════════════════════════
    # SECTION 2: SESSIONS BATCH COOKING
    # ═══════════════════════════════════════════════════════════

    @avec_gestion_erreurs(default_return=None)
    @avec_cache(ttl=600, key_func=lambda self, session_id: f"batch_session_{session_id}")
    @avec_session_db
    def obtenir_session(
        self, session_id: int, db: Session | None = None
    ) -> SessionBatchCooking | None:
        """Récupère une session avec ses étapes et préparations."""
        return (
            db.query(SessionBatchCooking)
            .options(
                joinedload(SessionBatchCooking.etapes),
                joinedload(SessionBatchCooking.preparations),
            )
            .filter(SessionBatchCooking.id == session_id)
            .first()
        )

    @avec_gestion_erreurs(default_return=None)
    @avec_cache(ttl=600, key_func=lambda self: "batch_session_active")
    @avec_session_db
    def get_session_active(self, db: Session | None = None) -> SessionBatchCooking | None:
        """Récupère la session en cours (si elle existe)."""
        return (
            db.query(SessionBatchCooking)
            .options(
                joinedload(SessionBatchCooking.etapes),
                joinedload(SessionBatchCooking.preparations),
            )
            .filter(SessionBatchCooking.statut == StatutSessionEnum.EN_COURS.value)
            .first()
        )

    @avec_gestion_erreurs(default_return=[])
    @avec_session_db
    def obtenir_sessions_planifiees(
        self,
        date_debut: date | None = None,
        date_fin: date | None = None,
        db: Session | None = None,
    ) -> list[SessionBatchCooking]:
        """Récupère les sessions planifiées dans une période."""
        query = db.query(SessionBatchCooking).filter(
            SessionBatchCooking.statut == StatutSessionEnum.PLANIFIEE.value
        )

        if date_debut:
            query = query.filter(SessionBatchCooking.date_session >= date_debut)
        if date_fin:
            query = query.filter(SessionBatchCooking.date_session <= date_fin)

        return query.order_by(SessionBatchCooking.date_session).all()

    @avec_gestion_erreurs(default_return=None)
    @avec_session_db
    def creer_session(
        self,
        date_session: date,
        recettes_ids: list[int],
        avec_jules: bool = False,
        robots: list[str] | None = None,
        heure_debut: time | None = None,
        planning_id: int | None = None,
        notes: str | None = None,
        db: Session | None = None,
    ) -> SessionBatchCooking | None:
        """Crée une nouvelle session batch cooking."""
        # Validation
        if not recettes_ids:
            raise ErreurValidation("Au moins une recette doit être sélectionnée")

        # Récupérer config pour valeurs par défaut
        config = self.get_config()

        session = SessionBatchCooking(
            nom=f"Batch {date_session.strftime('%d/%m/%Y')}",
            date_session=date_session,
            heure_debut=heure_debut or (config.heure_debut_preferee if config else time(10, 0)),
            avec_jules=avec_jules,
            recettes_selectionnees=recettes_ids,
            robots_utilises=robots
            or (config.robots_disponibles if config else ["four", "plaques"]),
            planning_id=planning_id,
            notes_avant=notes,
            statut=StatutSessionEnum.PLANIFIEE.value,
        )

        db.add(session)
        db.commit()
        db.refresh(session)

        # Invalider cache
        Cache.invalider(pattern="batch_session")

        logger.info(f"✅ Session batch cooking créée: {session.id}")
        return session

    @avec_gestion_erreurs(default_return=None)
    @avec_session_db
    def demarrer_session(
        self, session_id: int, db: Session | None = None
    ) -> SessionBatchCooking | None:
        """Démarre une session batch cooking."""
        session = db.query(SessionBatchCooking).filter_by(id=session_id).first()
        if not session:
            raise ErreurNonTrouve(f"Session {session_id} non trouvée")

        if session.statut != StatutSessionEnum.PLANIFIEE.value:
            raise ErreurValidation(f"Session ne peut pas être démarrée (statut: {session.statut})")

        session.statut = StatutSessionEnum.EN_COURS.value
        session.heure_debut = datetime.now().time()

        db.commit()
        db.refresh(session)

        # Invalider cache
        Cache.invalider(pattern="batch_session")

        logger.info(f"✅ Session batch cooking démarrée: {session_id}")
        return session

    @avec_gestion_erreurs(default_return=None)
    @avec_session_db
    def terminer_session(
        self,
        session_id: int,
        notes_apres: str | None = None,
        db: Session | None = None,
    ) -> SessionBatchCooking | None:
        """Termine une session batch cooking."""
        session = (
            db.query(SessionBatchCooking)
            .options(joinedload(SessionBatchCooking.etapes))
            .filter_by(id=session_id)
            .first()
        )
        if not session:
            raise ErreurNonTrouve(f"Session {session_id} non trouvée")

        if session.statut != StatutSessionEnum.EN_COURS.value:
            raise ErreurValidation(f"Session ne peut pas être terminée (statut: {session.statut})")

        session.statut = StatutSessionEnum.TERMINEE.value
        session.heure_fin = datetime.now().time()
        session.notes_apres = notes_apres

        # Calculer durée réelle
        if session.heure_debut:
            debut = datetime.combine(session.date_session, session.heure_debut)
            fin = datetime.combine(session.date_session, session.heure_fin)
            session.duree_reelle = int((fin - debut).total_seconds() / 60)

        # Compter recettes complétées
        if session.etapes:
            session.nb_recettes_completees = len(
                {
                    e.recette_id
                    for e in session.etapes
                    if e.recette_id and e.statut == StatutEtapeEnum.TERMINEE.value
                }
            )

        db.commit()
        db.refresh(session)

        # Invalider cache
        Cache.invalider(pattern="batch_session")

        logger.info(f"✅ Session batch cooking terminée: {session_id}")
        return session

    # ═══════════════════════════════════════════════════════════
    # SECTION 3: GESTION DES ÉTAPES
    # ═══════════════════════════════════════════════════════════

    @avec_gestion_erreurs(default_return=None)
    @avec_session_db
    def ajouter_etapes(
        self,
        session_id: int,
        etapes: list[dict[str, Any]],
        db: Session | None = None,
    ) -> SessionBatchCooking | None:
        """Ajoute des étapes à une session."""
        session = db.query(SessionBatchCooking).filter_by(id=session_id).first()
        if not session:
            raise ErreurNonTrouve(f"Session {session_id} non trouvée")

        for i, etape_data in enumerate(etapes, start=1):
            etape = EtapeBatchCooking(
                session_id=session_id,
                recette_id=etape_data.get("recette_id"),
                ordre=etape_data.get("ordre", i),
                groupe_parallele=etape_data.get("groupe_parallele", 0),
                titre=etape_data["titre"],
                description=etape_data.get("description"),
                duree_minutes=etape_data.get("duree_minutes", 10),
                robots_requis=etape_data.get("robots", []),
                est_supervision=etape_data.get("est_supervision", False),
                alerte_bruit=etape_data.get("alerte_bruit", False),
                temperature=etape_data.get("temperature"),
            )
            db.add(etape)

        # Estimer durée totale
        session.duree_estimee = sum(e.get("duree_minutes", 10) for e in etapes)

        db.commit()
        db.refresh(session)

        logger.info(f"✅ {len(etapes)} étapes ajoutées à la session {session_id}")
        return session

    @avec_gestion_erreurs(default_return=None)
    @avec_session_db
    def demarrer_etape(self, etape_id: int, db: Session | None = None) -> EtapeBatchCooking | None:
        """Démarre une étape (active le timer)."""
        etape = db.query(EtapeBatchCooking).filter_by(id=etape_id).first()
        if not etape:
            raise ErreurNonTrouve(f"Étape {etape_id} non trouvée")

        etape.statut = StatutEtapeEnum.EN_COURS.value
        etape.heure_debut = datetime.now()
        etape.timer_actif = True

        db.commit()
        db.refresh(etape)

        logger.info(f"✅ Étape démarrée: {etape_id}")
        return etape

    @avec_gestion_erreurs(default_return=None)
    @avec_session_db
    def terminer_etape(self, etape_id: int, db: Session | None = None) -> EtapeBatchCooking | None:
        """Termine une étape."""
        etape = db.query(EtapeBatchCooking).filter_by(id=etape_id).first()
        if not etape:
            raise ErreurNonTrouve(f"Étape {etape_id} non trouvée")

        etape.statut = StatutEtapeEnum.TERMINEE.value
        etape.heure_fin = datetime.now()
        etape.timer_actif = False

        # Calculer durée réelle
        if etape.heure_debut:
            etape.duree_reelle = int((etape.heure_fin - etape.heure_debut).total_seconds() / 60)

        db.commit()
        db.refresh(etape)

        logger.info(f"✅ Étape terminée: {etape_id}")
        return etape

    @avec_gestion_erreurs(default_return=None)
    @avec_session_db
    def passer_etape(self, etape_id: int, db: Session | None = None) -> EtapeBatchCooking | None:
        """Passe (saute) une étape."""
        etape = db.query(EtapeBatchCooking).filter_by(id=etape_id).first()
        if not etape:
            raise ErreurNonTrouve(f"Étape {etape_id} non trouvée")

        etape.statut = StatutEtapeEnum.PASSEE.value
        etape.timer_actif = False

        db.commit()
        db.refresh(etape)

        logger.info(f"✅ Étape passée: {etape_id}")
        return etape


# ═══════════════════════════════════════════════════════════
# ALIAS POUR RÉTROCOMPATIBILITÉ
# ═══════════════════════════════════════════════════════════
# INSTANCE SINGLETON - LAZY LOADING
# ═══════════════════════════════════════════════════════════

from src.services.core.registry import service_factory


@service_factory("batch_cooking", tags={"cuisine", "ia"})
def obtenir_service_batch_cooking() -> ServiceBatchCooking:
    """Obtient l'instance ServiceBatchCooking (thread-safe via registre)."""
    return ServiceBatchCooking()


def get_batch_cooking_service() -> ServiceBatchCooking:
    """Factory for batch cooking service (English alias)."""
    return obtenir_service_batch_cooking()


__all__ = [
    "ServiceBatchCooking",
    "obtenir_service_batch_cooking",
    "get_batch_cooking_service",
]
