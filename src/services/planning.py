"""
]
    "planning_service",
    "PlanningService",
__all__ = [

# ═══════════════════════════════════════════════════════════
# EXPORTS
# ═══════════════════════════════════════════════════════════


planning_service = PlanningService()

# ═══════════════════════════════════════════════════════════
# INSTANCE SINGLETON
# ═══════════════════════════════════════════════════════════


            return planning

            db.refresh(planning)
            db.commit()

                    db.add(repas_din)
                    )
                        notes=jour_data["diner"]
                        type_repas="dîner",
                        date_repas=date_jour,
                        planning_id=planning.id,
                    repas_din = Repas(
                if "diner" in jour_data:
                # Dîner
                
                    db.add(repas_dej)
                    )
                        notes=jour_data["dejeuner"]
                        type_repas="déjeuner",
                        date_repas=date_jour,
                        planning_id=planning.id,
                    repas_dej = Repas(
                if "dejeuner" in jour_data:
                # Déjeuner
                
                date_jour = semaine_debut + timedelta(days=idx)
            for idx, jour_data in enumerate(data):
            # Créer repas (simplifié - sans recherche recettes pour l'instant)

            db.flush()
            db.add(planning)
            )
                genere_par_ia=True
                actif=True,
                semaine_fin=semaine_fin,
                semaine_debut=semaine_debut,
                nom=f"Planning semaine {semaine_debut.strftime('%d/%m')}",
            planning = Planning(
            semaine_fin = semaine_debut + timedelta(days=6)
            # Créer planning
        with obtenir_contexte_db() as db:
        """Crée un planning depuis les données IA"""
    def _create_planning_from_data(self, semaine_debut: date, data: List[Dict]) -> Optional[Planning]:

            return []
        except:
            return json.loads(json_str)
            json_str = content[start:end]
                return []
            if start == -1:
            end = content.rfind("]") + 1
            start = content.find("[")
            import json
        try:
        """Parse la réponse IA planning"""
    def _parse_planning_ia(self, content: str) -> List[Dict]:

        return prompt
        prompt += "\n\nRéponds en JSON : [{\"jour\": \"lundi\", \"dejeuner\": \"recette\", \"diner\": \"recette\"}, ...]"

            prompt += f"\n\nPréférences : {preferences}"
        if preferences:

- Plus élaboré le weekend"""
- Facile à préparer en semaine
- Équilibré et varié
Critères :

- Dîner (soir)
- Déjeuner (midi)
Pour chaque jour (lundi à dimanche), suggère :

        prompt = f"""Génère un planning de repas pour la semaine du {semaine_debut} au {semaine_fin}.
        
        semaine_fin = semaine_debut + timedelta(days=6)
        """Construit le prompt pour génération planning"""
    def _build_planning_prompt(self, semaine_debut: date, preferences: Optional[Dict]) -> str:

    # ═══════════════════════════════════════════════════════════
    # HELPERS PRIVÉS
    # ═══════════════════════════════════════════════════════════

        }
            "taux_preparation": (prepares / total_repas * 100) if total_repas > 0 else 0
            "sans_recette": total_repas - avec_recette,
            "avec_recette": avec_recette,
            "restants": total_repas - prepares,
            "prepares": prepares,
            "total_repas": total_repas,
        return {

                    avec_recette += 1
                if repas["recette_id"]:
                    prepares += 1
                if repas["prepare"]:
            for repas in repas_list:
        for repas_list in planning["repas_par_jour"].values():

        avec_recette = 0
        prepares = 0
        total_repas = sum(len(repas) for repas in planning["repas_par_jour"].values())

            return {}
        if not planning:
        planning = self.get_planning_complet(planning_id)
        """
            Dict avec métriques
        Returns:

            planning_id: ID du planning
        Args:

        Calcule des statistiques sur un planning.
        """
    def get_statistiques_planning(self, planning_id: int) -> Dict:
    @handle_errors(show_in_ui=False, fallback_value={})

    # ═══════════════════════════════════════════════════════════
    # SECTION 4 : STATISTIQUES
    # ═══════════════════════════════════════════════════════════

            return None
            logger.error(f"❌ Erreur génération planning IA : {e}")
        except Exception as e:

            return planning
            logger.info(f"✅ Planning IA généré pour semaine du {semaine_debut}")

            planning = self._create_planning_from_data(semaine_debut, planning_data)
            # Créer planning

            Cache.enregistrer_appel_ia()
            Cache.definir_ia(prompt, planning_data)
            # Cacher

            planning_data = self._parse_planning_ia(response.choices[0].message.content)
            # Parser réponse

            )
                temperature=0.7
                messages=[{"role": "user", "content": prompt}],
                model="mistral-small-latest",
            response = self.ai_client.chat.complete(
        try:
        # Appeler IA

            return self._create_planning_from_data(semaine_debut, cached)
        if cached:
        cached = Cache.obtenir_ia(prompt)
        # Vérifier cache

        prompt = self._build_planning_prompt(semaine_debut, preferences)
        # Construire prompt

            return None
            logger.warning(msg)
        if not autorise:
        autorise, msg = Cache.peut_appeler_ia()
        # Vérifier rate limit

        self._ensure_ai_client()
        """
            Planning créé avec repas
        Returns:

            preferences: Préférences utilisateur (types repas, restrictions, etc.)
            semaine_debut: Date de début (lundi)
        Args:

        Génère un planning hebdomadaire avec l'IA.
        """
    ) -> Optional[Planning]:
        preferences: Optional[Dict] = None
        semaine_debut: date,
        self,
    def generer_planning_ia(
    @handle_errors(show_in_ui=True, fallback_value=None)

            self.ai_client = get_ai_client()
        if self.ai_client is None:
        """Initialise le client IA si nécessaire"""
    def _ensure_ai_client(self):

    # ═══════════════════════════════════════════════════════════
    # SECTION 3 : GÉNÉRATION IA
    # ═══════════════════════════════════════════════════════════

            return True

            Cache.invalider(dependencies=[f"planning_{repas.planning_id}"])
            # Invalider cache

            db.commit()
            repas.prepare = prepare

                return False
            if not repas:
            repas = db.query(Repas).get(repas_id)
        with obtenir_contexte_db() as db:
        """
            True si succès
        Returns:

            prepare: État préparé
            repas_id: ID du repas
        Args:

        Marque un repas comme préparé ou non.
        """
    def marquer_repas_prepare(self, repas_id: int, prepare: bool = True) -> bool:
    @handle_errors(show_in_ui=True, fallback_value=False)

            return repas
            logger.info(f"✅ Repas ajouté : {type_repas} le {date_repas}")

            Cache.invalider(dependencies=[f"planning_{planning_id}"])
            # Invalider cache

            db.refresh(repas)
            db.commit()
            db.add(repas)
            )
                prepare=False
                recette_id=recette_id,
                type_repas=type_repas,
                date_repas=date_repas,
                planning_id=planning_id,
            repas = Repas(
            # Créer repas

                return None
            if not planning:
            planning = db.query(Planning).get(planning_id)
            # Vérifier si planning existe
        with obtenir_contexte_db() as db:
        """
            Repas créé
        Returns:

            recette_id: ID de la recette (optionnel)
            type_repas: Type ("déjeuner", "dîner", etc.)
            date_repas: Date du repas
            planning_id: ID du planning
        Args:

        Ajoute un repas au planning.
        """
    ) -> Optional[Repas]:
        recette_id: Optional[int] = None
        type_repas: str,
        date_repas: date,
        planning_id: int,
        self,
    def ajouter_repas(
    @handle_errors(show_in_ui=True)

    # ═══════════════════════════════════════════════════════════
    # SECTION 2 : GESTION REPAS
    # ═══════════════════════════════════════════════════════════

            return None
                return self.get_planning_complet(planning.id)
            if planning:

            )
                .first()
                .filter(Planning.semaine_debut == semaine_debut)
                db.query(Planning)
            planning = (
        with obtenir_contexte_db() as db:
        """
            Planning de la semaine ou None
        Returns:

            semaine_debut: Date de début (lundi)
        Args:

        Récupère le planning pour une semaine donnée.
        """
    def get_planning_semaine(self, semaine_debut: date) -> Optional[Dict]:
    @handle_errors(show_in_ui=False, fallback_value=None)

            return result
                         dependencies=[f"planning_{planning_id}", "plannings"])
            Cache.definir(cache_key, result, ttl=self.cache_ttl, 

            }
                "repas_par_jour": repas_par_jour
                "genere_par_ia": planning.genere_par_ia,
                "actif": planning.actif,
                "semaine_fin": planning.semaine_fin,
                "semaine_debut": planning.semaine_debut,
                "nom": planning.nom,
                "id": planning.id,
            result = {

                })
                    "notes": repas.notes
                    "prepare": repas.prepare,
                    "recette_nom": repas.recette.nom if repas.recette else None,
                    "recette_id": repas.recette_id,
                    "type_repas": repas.type_repas,
                    "id": repas.id,
                repas_par_jour[jour_str].append({
                
                    repas_par_jour[jour_str] = []
                if jour_str not in repas_par_jour:
                jour_str = repas.date_repas.strftime("%Y-%m-%d")
            for repas in planning.repas:
            repas_par_jour = {}
            # Grouper repas par jour

                return None
            if not planning:

            )
                .first()
                .filter(Planning.id == planning_id)
                )
                    joinedload(Planning.repas).joinedload(Repas.recette)
                .options(
                db.query(Planning)
            planning = (
        with obtenir_contexte_db() as db:

            return cached
        if cached:
        cached = Cache.obtenir(cache_key, ttl=self.cache_ttl)
        cache_key = f"planning_full_{planning_id}"
        """
            Planning complet avec repas groupés par jour
        Returns:

            planning_id: ID du planning
        Args:

        Récupère un planning avec tous ses repas.
        """
    def get_planning_complet(self, planning_id: int) -> Optional[Dict]:
    @handle_errors(show_in_ui=False, fallback_value=None)

    # ═══════════════════════════════════════════════════════════
    # SECTION 1 : CRUD PLANNING
    # ═══════════════════════════════════════════════════════════

        self.ai_client = None
        super().__init__(Planning, cache_ttl=1800)
    def __init__(self):

    """
    - Statistiques
    - Export/Import
    - Équilibrage nutritionnel
    - Génération automatique IA
    - CRUD planning + repas
    Fonctionnalités :

    Service complet pour le planning hebdomadaire.
    """
class PlanningService(BaseService[Planning]):

# ═══════════════════════════════════════════════════════════
# SERVICE PLANNING UNIFIÉ
# ═══════════════════════════════════════════════════════════


logger = logging.getLogger(__name__)

from src.core.ai import get_ai_client
from src.core.models import Planning, Repas, Recette
)
    Cache,
    handle_errors,
    get_db_context as obtenir_contexte_db,
    BaseService,
from src.core import (

from sqlalchemy.orm import joinedload, Session
from typing import Dict, List, Optional
from datetime import date, timedelta
import logging
"""
Architecture simplifiée : Tout en 1 seul fichier.

- repas_service.py (Gestion repas)
- planning_generation_service.py (Génération IA)
- planning_service.py (CRUD)
Service complet pour le planning fusionnant :

Service Planning Unifié (REFACTORING v2.1)

