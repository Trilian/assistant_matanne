"""
Service Batch Cooking - Gestion des sessions de préparation de repas en lot.

Ce service gère :
- Configuration du batch cooking (jours, robots, préférences)
- Sessions de batch cooking (planification, exécution, suivi)
- Génération IA des plans optimisés
- Gestion des préparations stockées

✅ Utilise @avec_session_db et @avec_cache
✅ Validation Pydantic centralisée
✅ Intégration IA pour optimisation
"""

import logging
from datetime import date, datetime, time, timedelta
from typing import Any

from pydantic import BaseModel, Field
from sqlalchemy.orm import Session, joinedload

from src.core.ai import obtenir_client_ia
from src.core.cache import Cache
from src.core.database import obtenir_contexte_db
from src.core.decorators import avec_session_db, avec_cache, avec_gestion_erreurs
from src.core.errors_base import ErreurValidation, ErreurNonTrouve
from src.core.models import (
    ConfigBatchCooking,
    SessionBatchCooking,
    EtapeBatchCooking,
    PreparationBatch,
    Recette,
    Planning,
    Repas,
    StatutSessionEnum,
    StatutEtapeEnum,
    TypeRobotEnum,
    LocalisationStockageEnum,
)
from src.services.base_ai_service import BaseAIService
from src.services.types import BaseService

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# SCHÉMAS PYDANTIC
# ═══════════════════════════════════════════════════════════


class EtapeBatchIA(BaseModel):
    """Étape générée par l'IA pour une session batch cooking."""
    ordre: int = Field(..., ge=1)
    titre: str = Field(..., min_length=3, max_length=200)
    description: str = Field(..., min_length=5)
    duree_minutes: int = Field(..., ge=1, le=180)
    robots: list[str] = Field(default_factory=list)
    groupe_parallele: int = Field(default=0, ge=0)
    est_supervision: bool = Field(default=False)
    alerte_bruit: bool = Field(default=False)
    temperature: int | None = Field(default=None, ge=0, le=300)
    recette_nom: str | None = Field(default=None)


class SessionBatchIA(BaseModel):
    """Session batch cooking générée par l'IA."""
    recettes: list[str] = Field(..., min_length=1)
    duree_totale_estimee: int = Field(..., ge=5, le=480)
    etapes: list[EtapeBatchIA] = Field(..., min_length=1)
    conseils_jules: list[str] = Field(default_factory=list)
    ordre_optimal: str = Field(default="")


class PreparationIA(BaseModel):
    """Préparation générée par l'IA."""
    nom: str = Field(..., min_length=3, max_length=200)
    portions: int = Field(..., ge=1, le=20)
    conservation_jours: int = Field(..., ge=1, le=90)
    localisation: str = Field(default="frigo")
    container_suggere: str = Field(default="")


# ═══════════════════════════════════════════════════════════
# CONSTANTES
# ═══════════════════════════════════════════════════════════


JOURS_SEMAINE = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]

ROBOTS_DISPONIBLES = {
    "cookeo": {"nom": "Cookeo", "emoji": "🍲", "parallele": True},
    "monsieur_cuisine": {"nom": "Monsieur Cuisine", "emoji": "🤖", "parallele": True},
    "airfryer": {"nom": "Airfryer", "emoji": "🍟", "parallele": True},
    "multicooker": {"nom": "Multicooker", "emoji": "♨️", "parallele": True},
    "four": {"nom": "Four", "emoji": "🔥", "parallele": True},
    "plaques": {"nom": "Plaques", "emoji": "🍳", "parallele": False},
    "robot_patissier": {"nom": "Robot Pâtissier", "emoji": "🎂", "parallele": True},
    "mixeur": {"nom": "Mixeur", "emoji": "🥤", "parallele": False},
    "hachoir": {"nom": "Hachoir", "emoji": "🔪", "parallele": False},
}


# ═══════════════════════════════════════════════════════════
# SERVICE BATCH COOKING
# ═══════════════════════════════════════════════════════════


class BatchCookingService(BaseService[SessionBatchCooking], BaseAIService):
    """
    Service complet pour le batch cooking.
    
    Fonctionnalités:
    - Configuration utilisateur (jours, robots, préférences)
    - Sessions batch cooking (création, exécution, suivi)
    - Génération IA de plans optimisés
    - Gestion des préparations stockées
    - Intégration avec le planning hebdomadaire
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

    @avec_cache(ttl=3600, key_func=lambda self: "batch_config")
    @avec_gestion_erreurs(default_return=None)
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

    @avec_cache(ttl=600, key_func=lambda self, session_id: f"batch_session_{session_id}")
    @avec_gestion_erreurs(default_return=None)
    @avec_session_db
    def get_session(self, session_id: int, db: Session | None = None) -> SessionBatchCooking | None:
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

    @avec_cache(ttl=600, key_func=lambda self: "batch_session_active")
    @avec_gestion_erreurs(default_return=None)
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
    def get_sessions_planifiees(
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
            robots_utilises=robots or (config.robots_disponibles if config else ["four", "plaques"]),
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
    def demarrer_session(self, session_id: int, db: Session | None = None) -> SessionBatchCooking | None:
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
            session.nb_recettes_completees = len(set(
                e.recette_id for e in session.etapes 
                if e.recette_id and e.statut == StatutEtapeEnum.TERMINEE.value
            ))
        
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
    # SECTION 4: PRÉPARATIONS STOCKÉES
    # ═══════════════════════════════════════════════════════════

    @avec_cache(ttl=600, key_func=lambda self, consommees=False, localisation=None: f"preparations_{consommees}_{localisation}")
    @avec_gestion_erreurs(default_return=[])
    @avec_session_db
    def get_preparations(
        self,
        consommees: bool = False,
        localisation: str | None = None,
        db: Session | None = None,
    ) -> list[PreparationBatch]:
        """Récupère les préparations stockées."""
        query = db.query(PreparationBatch).filter(PreparationBatch.consomme == consommees)
        
        if localisation:
            query = query.filter(PreparationBatch.localisation == localisation)
            
        return query.order_by(PreparationBatch.date_peremption).all()

    @avec_gestion_erreurs(default_return=[])
    @avec_session_db
    def get_preparations_alertes(self, db: Session | None = None) -> list[PreparationBatch]:
        """Récupère les préparations proches de la péremption."""
        limite = date.today() + timedelta(days=3)
        return (
            db.query(PreparationBatch)
            .filter(
                PreparationBatch.consomme == False,
                PreparationBatch.date_peremption <= limite,
            )
            .order_by(PreparationBatch.date_peremption)
            .all()
        )

    @avec_gestion_erreurs(default_return=None)
    @avec_session_db
    def creer_preparation(
        self,
        nom: str,
        portions: int,
        date_preparation: date,
        conservation_jours: int,
        localisation: str = "frigo",
        session_id: int | None = None,
        recette_id: int | None = None,
        container: str | None = None,
        notes: str | None = None,
        db: Session | None = None,
    ) -> PreparationBatch | None:
        """Crée une nouvelle préparation stockée."""
        preparation = PreparationBatch(
            session_id=session_id,
            recette_id=recette_id,
            nom=nom,
            portions_initiales=portions,
            portions_restantes=portions,
            date_preparation=date_preparation,
            date_peremption=date_preparation + timedelta(days=conservation_jours),
            localisation=localisation,
            container=container,
            notes=notes,
        )
        
        db.add(preparation)
        db.commit()
        db.refresh(preparation)
        
        # Invalider cache
        Cache.invalider(pattern="preparations")
        
        logger.info(f"✅ Préparation créée: {preparation.id}")
        return preparation

    @avec_gestion_erreurs(default_return=None)
    @avec_session_db
    def consommer_preparation(
        self,
        preparation_id: int,
        portions: int = 1,
        db: Session | None = None,
    ) -> PreparationBatch | None:
        """Consomme des portions d'une préparation."""
        preparation = db.query(PreparationBatch).filter_by(id=preparation_id).first()
        if not preparation:
            raise ErreurNonTrouve(f"Préparation {preparation_id} non trouvée")

        preparation.consommer_portion(portions)
        
        db.commit()
        db.refresh(preparation)
        
        # Invalider cache
        Cache.invalider(pattern="preparations")
        
        logger.info(f"✅ {portions} portion(s) consommée(s): {preparation_id}")
        return preparation

    # ═══════════════════════════════════════════════════════════
    # SECTION 5: GÉNÉRATION IA
    # ═══════════════════════════════════════════════════════════

    @avec_cache(ttl=3600, key_func=lambda self, recettes_ids, robots_disponibles, avec_jules=False: 
                f"batch_plan_{'-'.join(map(str, recettes_ids))}_{avec_jules}")
    @avec_gestion_erreurs(default_return=None)
    @avec_session_db
    def generer_plan_ia(
        self,
        recettes_ids: list[int],
        robots_disponibles: list[str],
        avec_jules: bool = False,
        db: Session | None = None,
    ) -> SessionBatchIA | None:
        """Génère un plan de batch cooking optimisé avec l'IA.
        
        L'IA optimise :
        - L'ordre des étapes pour paralléliser au maximum
        - L'utilisation des robots pour gagner du temps
        - Les conseils pour cuisiner avec un enfant présent
        """
        # Récupérer les recettes
        recettes = db.query(Recette).filter(Recette.id.in_(recettes_ids)).all()
        if not recettes:
            raise ErreurValidation("Aucune recette trouvée")

        # Construire le contexte
        recettes_context = []
        for r in recettes:
            etapes_text = ""
            if r.etapes:
                etapes_text = "\n".join([f"  {e.ordre}. {e.description} ({e.duree or '?'} min)" for e in r.etapes])
            
            recettes_context.append(f"""
Recette: {r.nom}
- Temps préparation: {r.temps_preparation} min
- Temps cuisson: {r.temps_cuisson} min
- Portions: {r.portions}
- Compatible batch: {r.compatible_batch}
- Congelable: {r.congelable}
- Robots: {', '.join(r.robots_compatibles) if r.robots_compatibles else 'Aucun'}
- Étapes:
{etapes_text}
""")

        robots_text = ", ".join([ROBOTS_DISPONIBLES.get(r, {}).get("nom", r) for r in robots_disponibles])
        jules_context = """
⚠️ IMPORTANT - JULES (bébé 19 mois) sera présent !
- Éviter les étapes bruyantes pendant la sieste (13h-15h)
- Prévoir des moments calmes où il peut observer/aider
- Signaler les étapes dangereuses (four chaud, friture, couteaux)
- Optimiser pour terminer avant 12h si possible
""" if avec_jules else ""

        prompt = f"""GÉNÈRE UN PLAN DE BATCH COOKING OPTIMISÉ EN JSON UNIQUEMENT.

RECETTES À PRÉPARER:
{''.join(recettes_context)}

ÉQUIPEMENTS DISPONIBLES:
{robots_text}

{jules_context}

OBJECTIF:
1. Optimiser le temps total en parallélisant les tâches
2. Regrouper les étapes par robot/équipement
3. Prévoir les temps de supervision (cuisson four, etc.)
4. Indiquer clairement les étapes bruyantes

RETOURNE UNIQUEMENT CE JSON (pas de markdown, pas d'explication):
{{
    "recettes": ["Nom recette 1", "Nom recette 2"],
    "duree_totale_estimee": 120,
    "etapes": [
        {{
            "ordre": 1,
            "titre": "Préparer les légumes",
            "description": "Éplucher et couper les carottes, pommes de terre et oignons",
            "duree_minutes": 15,
            "robots": ["hachoir"],
            "groupe_parallele": 0,
            "est_supervision": false,
            "alerte_bruit": true,
            "temperature": null,
            "recette_nom": "Boeuf bourguignon"
        }}
    ],
    "conseils_jules": ["Moment idéal pour Jules: étape 3 (mélanger les ingrédients)"],
    "ordre_optimal": "Commencer par les cuissons longues au four, puis préparer les plats rapides en parallèle"
}}

RÈGLES:
- Les étapes avec le même groupe_parallele peuvent être faites simultanément
- est_supervision=true pour les étapes passives (surveiller la cuisson)
- alerte_bruit=true pour mixeur, hachoir, robot bruyant
- Grouper intelligemment pour minimiser le temps total
"""

        logger.info(f"🤖 Génération plan batch cooking IA ({len(recettes)} recettes)")

        result = self.call_with_json_parsing_sync(
            prompt=prompt,
            response_model=SessionBatchIA,
            system_prompt="Tu es un chef expert en batch cooking et organisation de cuisine. Retourne UNIQUEMENT du JSON valide, sans aucun texte avant ou après.",
            temperature=0.5,
            max_tokens=4000,
        )

        if result:
            logger.info(f"✅ Plan batch cooking généré: {result.duree_totale_estimee} min estimées")
        
        return result

    @avec_gestion_erreurs(default_return=[])
    @avec_session_db
    def suggerer_recettes_batch(
        self,
        nb_recettes: int = 4,
        robots_disponibles: list[str] | None = None,
        avec_jules: bool = False,
        planning_id: int | None = None,
        db: Session | None = None,
    ) -> list[Recette]:
        """Suggère des recettes adaptées au batch cooking."""
        query = db.query(Recette).filter(Recette.compatible_batch == True)
        
        # Filtrer par robots si spécifié
        if robots_disponibles:
            # Filtre complexe sur les robots
            for robot in robots_disponibles:
                if robot == "cookeo":
                    query = query.filter(Recette.compatible_cookeo == True)
                elif robot == "monsieur_cuisine":
                    query = query.filter(Recette.compatible_monsieur_cuisine == True)
                elif robot == "airfryer":
                    query = query.filter(Recette.compatible_airfryer == True)
        
        # Filtrer pour bébé si Jules présent
        if avec_jules:
            query = query.filter(Recette.compatible_bebe == True)
        
        # Prioriser les recettes congelables
        recettes = query.order_by(Recette.congelable.desc()).limit(nb_recettes * 2).all()
        
        # Retourner un échantillon varié
        return recettes[:nb_recettes]

    # ═══════════════════════════════════════════════════════════
    # SECTION 6: INTÉGRATION PLANNING
    # ═══════════════════════════════════════════════════════════

    @avec_gestion_erreurs(default_return=None)
    @avec_session_db
    def attribuer_preparations_planning(
        self,
        session_id: int,
        db: Session | None = None,
    ) -> dict[str, Any] | None:
        """Attribue automatiquement les préparations aux repas du planning."""
        session = (
            db.query(SessionBatchCooking)
            .options(joinedload(SessionBatchCooking.preparations))
            .filter_by(id=session_id)
            .first()
        )
        if not session or not session.planning_id:
            return None

        planning = (
            db.query(Planning)
            .options(joinedload(Planning.repas))
            .filter_by(id=session.planning_id)
            .first()
        )
        if not planning:
            return None

        # Attribuer les préparations aux repas
        attributions = []
        for preparation in session.preparations:
            if preparation.consomme:
                continue
                
            # Trouver les repas sans recette
            repas_libres = [r for r in planning.repas if not r.recette_id and not r.notes]
            
            # Attribuer à des repas
            nb_attribue = min(preparation.portions_restantes, len(repas_libres))
            for i, repas in enumerate(repas_libres[:nb_attribue]):
                repas.notes = f"🍱 {preparation.nom}"
                
                if preparation.repas_attribues is None:
                    preparation.repas_attribues = []
                preparation.repas_attribues.append(repas.id)
                
                attributions.append({
                    "preparation": preparation.nom,
                    "repas_id": repas.id,
                    "date": repas.date_repas.isoformat(),
                })

        db.commit()
        
        logger.info(f"✅ {len(attributions)} attributions créées")
        return {
            "session_id": session_id,
            "planning_id": planning.id,
            "attributions": attributions,
        }


# ═══════════════════════════════════════════════════════════
# INSTANCE SINGLETON - LAZY LOADING
# ═══════════════════════════════════════════════════════════

_batch_cooking_service: BatchCookingService | None = None


def get_batch_cooking_service() -> BatchCookingService:
    """Get or create the global BatchCookingService instance."""
    global _batch_cooking_service
    if _batch_cooking_service is None:
        _batch_cooking_service = BatchCookingService()
    return _batch_cooking_service


__all__ = [
    "BatchCookingService",
    "get_batch_cooking_service",
    "ROBOTS_DISPONIBLES",
    "JOURS_SEMAINE",
]

