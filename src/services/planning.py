"""
Service Planning Unifié (REFACTORING v2.1)

Service complet pour le planning fusionnant :
- planning_service.py (CRUD)
- planning_generation_service.py (Génération IA)
- repas_service.py (Gestion repas)

Architecture simplifiée : Tout en 1 seul fichier.
"""
import logging
from typing import Dict, List, Optional
from datetime import date, timedelta
from sqlalchemy.orm import joinedload, Session

from src.services.types import BaseService

from src.core.database import obtenir_contexte_db
from src.core.errors import gerer_erreurs
from src.core.cache import Cache
from src.core.models import Planning, Repas, Recette
from src.core.ai import get_ai_client

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# SERVICE PLANNING UNIFIÉ
# ═══════════════════════════════════════════════════════════

class PlanningService(BaseService[Planning]):
    """
    Service complet pour le planning hebdomadaire.

    Fonctionnalités :
    - CRUD planning + repas
    - Génération automatique IA
    - Équilibrage nutritionnel
    - Export/Import
    - Statistiques
    """

    def __init__(self):
        super().__init__(Planning, cache_ttl=1800)
        self.ai_client = None

    # ═══════════════════════════════════════════════════════════
    # SECTION 1 : CRUD PLANNING
    # ═══════════════════════════════════════════════════════════

    @gerer_erreurs(afficher_dans_ui=False, valeur_fallback=None)
    def get_planning_complet(self, planning_id: int) -> Optional[Dict]:
        """
        Récupère un planning avec tous ses repas.

        Args:
            planning_id: ID du planning

        Returns:
            Planning complet avec repas groupés par jour
        """
        cache_key = f"planning_full_{planning_id}"
        cached = Cache.obtenir(cache_key, ttl=self.cache_ttl)
        if cached:
            return cached

        with obtenir_contexte_db() as db:
            planning = (
                db.query(Planning)
                .options(
                    joinedload(Planning.repas).joinedload(Repas.recette)
                )
                .filter(Planning.id == planning_id)
                .first()
            )

            if not planning:
                return None

            # Grouper repas par jour
            repas_par_jour = {}
            for repas in planning.repas:
                jour_str = repas.date_repas.strftime("%Y-%m-%d")
                if jour_str not in repas_par_jour:
                    repas_par_jour[jour_str] = []

                repas_par_jour[jour_str].append({
                    "id": repas.id,
                    "type_repas": repas.type_repas,
                    "recette_id": repas.recette_id,
                    "recette_nom": repas.recette.nom if repas.recette else None,
                    "prepare": repas.prepare,
                    "notes": repas.notes
                })

            result = {
                "id": planning.id,
                "nom": planning.nom,
                "semaine_debut": planning.semaine_debut,
                "semaine_fin": planning.semaine_fin,
                "actif": planning.actif,
                "genere_par_ia": planning.genere_par_ia,
                "repas_par_jour": repas_par_jour
            }

            Cache.definir(cache_key, result, ttl=self.cache_ttl,
                          dependencies=[f"planning_{planning_id}", "plannings"])

            return result

    @gerer_erreurs(afficher_dans_ui=False, valeur_fallback=None)
    def get_planning_semaine(self, semaine_debut: date) -> Optional[Dict]:
        """
        Récupère le planning pour une semaine donnée.

        Args:
            semaine_debut: Date de début (lundi)

        Returns:
            Planning de la semaine ou None
        """
        with obtenir_contexte_db() as db:
            planning = (
                db.query(Planning)
                .filter(Planning.semaine_debut == semaine_debut)
                .first()
            )

            if planning:
                return self.get_planning_complet(planning.id)

            return None

    # ═══════════════════════════════════════════════════════════
    # SECTION 2 : GESTION REPAS
    # ═══════════════════════════════════════════════════════════

    @gerer_erreurs(afficher_dans_ui=True)
    def ajouter_repas(
            self,
            planning_id: int,
            date_repas: date,
            type_repas: str,
            recette_id: Optional[int] = None
    ) -> Optional[Repas]:
        """
        Ajoute un repas au planning.

        Args:
            planning_id: ID du planning
            date_repas: Date du repas
            type_repas: Type ("déjeuner", "dîner", etc.)
            recette_id: ID de la recette (optionnel)

        Returns:
            Repas créé
        """
        with obtenir_contexte_db() as db:
            # Vérifier si planning existe
            planning = db.query(Planning).get(planning_id)
            if not planning:
                return None

            # Créer repas
            repas = Repas(
                planning_id=planning_id,
                date_repas=date_repas,
                type_repas=type_repas,
                recette_id=recette_id,
                prepare=False
            )
            db.add(repas)
            db.commit()
            db.refresh(repas)

            # Invalider cache
            Cache.invalider(dependencies=[f"planning_{planning_id}"])

            logger.info(f"✅ Repas ajouté : {type_repas} le {date_repas}")

            return repas

    @gerer_erreurs(afficher_dans_ui=True, valeur_fallback=False)
    def marquer_repas_prepare(self, repas_id: int, prepare: bool = True) -> bool:
        """
        Marque un repas comme préparé ou non.

        Args:
            repas_id: ID du repas
            prepare: État préparé

        Returns:
            True si succès
        """
        with obtenir_contexte_db() as db:
            repas = db.query(Repas).get(repas_id)
            if not repas:
                return False

            repas.prepare = prepare
            db.commit()

            # Invalider cache
            Cache.invalider(dependencies=[f"planning_{repas.planning_id}"])

            return True

    # ═══════════════════════════════════════════════════════════
    # SECTION 3 : GÉNÉRATION IA
    # ═══════════════════════════════════════════════════════════

    def _ensure_ai_client(self):
        """Initialise le client IA si nécessaire"""
        if self.ai_client is None:
            self.ai_client = get_ai_client()

    @gerer_erreurs(afficher_dans_ui=True, valeur_fallback=None)
    def generer_planning_ia(
            self,
            semaine_debut: date,
            preferences: Optional[Dict] = None
    ) -> Optional[Planning]:
        """
        Génère un planning hebdomadaire avec l'IA.

        Args:
            semaine_debut: Date de début (lundi)
            preferences: Préférences utilisateur (types repas, restrictions, etc.)

        Returns:
            Planning créé avec repas
        """
        self._ensure_ai_client()

        # Vérifier rate limit
        autorise, msg = Cache.peut_appeler_ia()
        if not autorise:
            logger.warning(msg)
            return None

        # Construire prompt
        prompt = self._build_planning_prompt(semaine_debut, preferences)

        # Vérifier cache
        cached = Cache.obtenir_ia(prompt)
        if cached:
            return self._create_planning_from_data(semaine_debut, cached)

        # Appeler IA
        try:
            response = self.ai_client.chat.complete(
                model="mistral-small-latest",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )

            # Parser réponse
            planning_data = self._parse_planning_ia(response.choices[0].message.content)

            # Cacher
            Cache.definir_ia(prompt, planning_data)
            Cache.enregistrer_appel_ia()

            # Créer planning
            planning = self._create_planning_from_data(semaine_debut, planning_data)

            logger.info(f"✅ Planning IA généré pour semaine du {semaine_debut}")

            return planning

        except Exception as e:
            logger.error(f"❌ Erreur génération planning IA : {e}")
            return None

    # ═══════════════════════════════════════════════════════════
    # SECTION 4 : STATISTIQUES
    # ═══════════════════════════════════════════════════════════

    @gerer_erreurs(afficher_dans_ui=False, valeur_fallback={})
    def get_statistiques_planning(self, planning_id: int) -> Dict:
        """
        Calcule des statistiques sur un planning.

        Args:
            planning_id: ID du planning

        Returns:
            Dict avec métriques
        """
        planning = self.get_planning_complet(planning_id)

        if not planning:
            return {}

        total_repas = sum(len(repas) for repas in planning["repas_par_jour"].values())
        prepares = 0
        avec_recette = 0

        for repas_list in planning["repas_par_jour"].values():
            for repas in repas_list:
                if repas["prepare"]:
                    prepares += 1
                if repas["recette_id"]:
                    avec_recette += 1

        return {
            "total_repas": total_repas,
            "prepares": prepares,
            "restants": total_repas - prepares,
            "avec_recette": avec_recette,
            "sans_recette": total_repas - avec_recette,
            "taux_preparation": (prepares / total_repas * 100) if total_repas > 0 else 0
        }

    # ═══════════════════════════════════════════════════════════
    # HELPERS PRIVÉS
    # ═══════════════════════════════════════════════════════════

    def _build_planning_prompt(self, semaine_debut: date, preferences: Optional[Dict]) -> str:
        """Construit le prompt pour génération planning"""
        semaine_fin = semaine_debut + timedelta(days=6)

        prompt = f"""Génère un planning de repas pour la semaine du {semaine_debut} au {semaine_fin}.

Pour chaque jour (lundi à dimanche), suggère :
- Déjeuner (midi)
- Dîner (soir)

Critères :
- Équilibré et varié
- Facile à préparer en semaine
- Plus élaboré le weekend"""

        if preferences:
            prompt += f"\n\nPréférences : {preferences}"

        prompt += "\n\nRéponds en JSON : [{\"jour\": \"lundi\", \"dejeuner\": \"recette\", \"diner\": \"recette\"}, ...]"

        return prompt

    def _parse_planning_ia(self, content: str) -> List[Dict]:
        """Parse la réponse IA planning"""
        try:
            import json
            start = content.find("[")
            end = content.rfind("]") + 1
            if start == -1:
                return []
            json_str = content[start:end]
            return json.loads(json_str)
        except:
            return []

    def _create_planning_from_data(self, semaine_debut: date, data: List[Dict]) -> Optional[Planning]:
        """Crée un planning depuis les données IA"""
        with obtenir_contexte_db() as db:
            semaine_fin = semaine_debut + timedelta(days=6)

            # Créer planning
            planning = Planning(
                nom=f"Planning semaine {semaine_debut.strftime('%d/%m')}",
                semaine_debut=semaine_debut,
                semaine_fin=semaine_fin,
                actif=True,
                genere_par_ia=True
            )
            db.add(planning)
            db.flush()

            # Créer repas (simplifié - sans recherche recettes pour l'instant)
            for idx, jour_data in enumerate(data):
                date_jour = semaine_debut + timedelta(days=idx)

                # Déjeuner
                if "dejeuner" in jour_data:
                    repas_dej = Repas(
                        planning_id=planning.id,
                        date_repas=date_jour,
                        type_repas="déjeuner",
                        notes=jour_data["dejeuner"]
                    )
                    db.add(repas_dej)

                # Dîner
                if "diner" in jour_data:
                    repas_din = Repas(
                        planning_id=planning.id,
                        date_repas=date_jour,
                        type_repas="dîner",
                        notes=jour_data["diner"]
                    )
                    db.add(repas_din)

            db.commit()
            db.refresh(planning)

            return planning


# ═══════════════════════════════════════════════════════════
# INSTANCE SINGLETON
# ═══════════════════════════════════════════════════════════

planning_service = PlanningService()

# ═══════════════════════════════════════════════════════════
# EXPORTS
# ═══════════════════════════════════════════════════════════

__all__ = [
    "planning_service",
    "PlanningService",
]