"""
Service Génération Planning - IA Isolée
Toute la logique de génération automatique de planning
"""
import asyncio
import json
import logging
from typing import List, Dict, Optional
from datetime import date, timedelta
from pydantic import BaseModel, Field, validator

from src.core.ai_agent import AgentIA
from src.core.ai_cache import AICache, RateLimiter
from src.core.database import get_db_context
from src.core.models import (
    Recette, ConfigPlanningUtilisateur,
    TypeRepasEnum, TypeVersionRecetteEnum
)

logger = logging.getLogger(__name__)


# ===================================
# SCHÉMAS PYDANTIC
# ===================================

class RepasGenere(BaseModel):
    """Repas généré par IA"""
    type: str = Field(..., pattern="^(petit_déjeuner|déjeuner|dîner|goûter|bébé|batch_cooking)$")
    recette_nom: str = Field(..., min_length=2)
    portions: int = Field(4, gt=0, le=20)
    adapte_bebe: bool = False
    est_batch: bool = False
    raison: Optional[str] = None
    heure_suggeree: Optional[str] = None

    @validator('recette_nom')
    def clean_nom(cls, v):
        return v.strip()


class JourPlanning(BaseModel):
    """Planning d'un jour"""
    jour: int = Field(..., ge=0, le=6)  # 0=lundi, 6=dimanche
    repas: List[RepasGenere] = Field(..., min_items=1)
    conseils_jour: Optional[List[str]] = Field(default_factory=list)


class PlanningGenere(BaseModel):
    """Planning complet généré"""
    planning: List[JourPlanning] = Field(..., min_items=7, max_items=7)
    conseils_globaux: List[str] = Field(default_factory=list)
    score_equilibre: int = Field(0, ge=0, le=100)
    score_variete: int = Field(0, ge=0, le=100)


# ===================================
# SERVICE
# ===================================

class PlanningGenerationService:
    """Service de génération automatique de planning"""

    JOURS_SEMAINE = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]

    def __init__(self, agent: AgentIA):
        self.agent = agent

    # ===================================
    # GÉNÉRATION PRINCIPALE
    # ===================================

    async def generer_planning_complet(
            self,
            semaine_debut: date,
            config: ConfigPlanningUtilisateur,
            contraintes: Optional[Dict] = None
    ) -> PlanningGenere:
        """
        Génère un planning complet pour une semaine

        Args:
            semaine_debut: Date du lundi
            config: Configuration utilisateur
            contraintes: Contraintes optionnelles (événements, préférences)

        Returns:
            PlanningGenere validé par Pydantic
        """
        logger.info(f"Génération planning IA: semaine du {semaine_debut}")

        # Vérifier rate limit
        can_call, error = RateLimiter.can_call()
        if not can_call:
            raise ValueError(error)

        # Récupérer recettes disponibles
        recettes = self._get_recettes_disponibles()

        if not recettes:
            raise ValueError("Aucune recette disponible pour générer le planning")

        # Construire prompt
        prompt = self._build_prompt_generation(
            semaine_debut,
            config,
            recettes,
            contraintes
        )

        # Appel IA avec retry
        response = await self._call_with_retry(
            prompt,
            system_prompt="Expert nutritionniste et planification de repas. Réponds UNIQUEMENT en JSON valide.",
            max_tokens=2500
        )

        # Parser et valider
        try:
            data = self._parse_json_response(response)
            return PlanningGenere(**data)
        except Exception as e:
            logger.error(f"Erreur parsing planning IA: {e}")
            # Fallback basique
            return self._fallback_planning(config, recettes)

    def _get_recettes_disponibles(self) -> List[Dict]:
        """Récupère toutes les recettes avec infos pertinentes"""
        with get_db_context() as db:
            recettes = db.query(Recette).all()

            return [{
                "id": r.id,
                "nom": r.nom,
                "type_repas": r.type_repas,
                "temps_total": r.temps_preparation + r.temps_cuisson,
                "difficulte": r.difficulte,
                "saison": r.saison,
                "est_rapide": r.est_rapide,
                "est_equilibre": r.est_equilibre,
                "compatible_bebe": r.compatible_bebe,
                "compatible_batch": r.compatible_batch,
                "congelable": r.congelable,
                "a_version_bebe": any(
                    v.type_version == TypeVersionRecetteEnum.BEBE
                    for v in r.versions
                ),
                "a_version_batch": any(
                    v.type_version == TypeVersionRecetteEnum.BATCH_COOKING
                    for v in r.versions
                )
            } for r in recettes]

    def _build_prompt_generation(
            self,
            semaine_debut: date,
            config: ConfigPlanningUtilisateur,
            recettes: List[Dict],
            contraintes: Optional[Dict]
    ) -> str:
        """Construit le prompt de génération"""

        # Types de repas actifs
        repas_actifs = [k for k, v in config.repas_actifs.items() if v]

        # Info bébé
        info_bebe = ""
        if config.a_bebe:
            info_bebe = f"""
BÉBÉ DANS LE FOYER:
- Privilégier recettes compatibles bébé
- Utiliser versions bébé si disponibles
- Adapter textures et portions
"""

        # Info batch cooking
        info_batch = ""
        if config.batch_cooking_actif and config.jours_batch:
            jours_batch_str = ", ".join([self.JOURS_SEMAINE[j] for j in config.jours_batch])
            info_batch = f"""
BATCH COOKING:
- Sessions prévues: {jours_batch_str}
- Privilégier recettes compatibles batch
- Optimiser le temps de préparation
"""

        # Contraintes externes
        info_contraintes = ""
        if contraintes:
            if contraintes.get("evenements"):
                info_contraintes += f"\nÉvénements: {contraintes['evenements']}"
            if contraintes.get("invites"):
                info_contraintes += f"\nInvités prévus: {contraintes['invites']}"

        # Limiter recettes dans le prompt (top 50)
        recettes_sample = recettes[:50]

        return f"""Génère un planning de repas pour 7 jours (semaine du {semaine_debut.strftime('%d/%m/%Y')}).

CONFIGURATION FOYER:
- Adultes: {config.nb_adultes}
- Enfants: {config.nb_enfants}
- Repas à planifier: {', '.join(repas_actifs)}

{info_bebe}
{info_batch}
{info_contraintes}

RECETTES DISPONIBLES ({len(recettes)} total, {len(recettes_sample)} échantillon):
{json.dumps(recettes_sample, indent=2, ensure_ascii=False)}

CONTRAINTES:
1. VARIER les recettes (pas 2 fois la même dans la semaine)
2. ÉQUILIBRER rapide/complexe (au moins 3 repas rapides)
3. ADAPTER les portions selon le foyer
4. Si bébé: privilégier recettes compatibles
5. Si batch: optimiser temps de préparation
6. Respecter saisons si possible

FORMAT JSON STRICT:
{{
  "planning": [
    {{
      "jour": 0,
      "repas": [
        {{
          "type": "déjeuner",
          "recette_nom": "Nom EXACT de la recette",
          "portions": 4,
          "adapte_bebe": false,
          "est_batch": false,
          "raison": "Pourquoi cette recette ce jour",
          "heure_suggeree": "12:30"
        }}
      ],
      "conseils_jour": ["Conseil du jour"]
    }}
  ],
  "conseils_globaux": [
    "Conseil 1 pour la semaine",
    "Conseil 2"
  ],
  "score_equilibre": 85,
  "score_variete": 90
}}

IMPORTANT:
- Génère EXACTEMENT 7 jours (jour: 0 à 6)
- Utilise les NOMS EXACTS des recettes (vérifier dans la liste)
- Un planning pour {', '.join(repas_actifs)}

UNIQUEMENT le JSON !"""

    async def _call_with_retry(
            self,
            prompt: str,
            system_prompt: str,
            max_tokens: int,
            max_retries: int = 3
    ) -> str:
        """Appel IA avec retry"""
        for attempt in range(max_retries):
            try:
                response = await self.agent._call_mistral(
                    prompt=prompt,
                    system_prompt=system_prompt,
                    temperature=0.7,
                    max_tokens=max_tokens
                )
                RateLimiter.record_call()
                return response
            except Exception as e:
                if attempt == max_retries - 1:
                    logger.error(f"IA failed after {max_retries} attempts: {e}")
                    raise
                await asyncio.sleep(2 ** attempt)

    def _parse_json_response(self, response: str) -> Dict:
        """Parse réponse JSON"""
        cleaned = response.strip()

        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        if cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]

        cleaned = cleaned.strip()
        return json.loads(cleaned)

    def _fallback_planning(
            self,
            config: ConfigPlanningUtilisateur,
            recettes: List[Dict]
    ) -> PlanningGenere:
        """Planning de fallback si IA échoue"""
        logger.warning("Utilisation du fallback planning (IA indisponible)")

        repas_actifs = [k for k, v in config.repas_actifs.items() if v]

        # Sélection simple de recettes variées
        recettes_selectionnees = []
        for type_repas in repas_actifs:
            recettes_type = [r for r in recettes if r["type_repas"] == type_repas]
            if recettes_type:
                # Prendre les 7 premières variées
                recettes_selectionnees.extend(recettes_type[:7])

        # Créer planning basique
        planning = []
        idx = 0

        for jour in range(7):
            repas_jour = []

            for type_repas in repas_actifs:
                if idx < len(recettes_selectionnees):
                    recette = recettes_selectionnees[idx]
                    repas_jour.append(
                        RepasGenere(
                            type=type_repas,
                            recette_nom=recette["nom"],
                            portions=4,
                            raison="Planning automatique (IA indisponible)"
                        )
                    )
                    idx += 1

            planning.append(
                JourPlanning(
                    jour=jour,
                    repas=repas_jour
                )
            )

        return PlanningGenere(
            planning=planning,
            conseils_globaux=["Planning généré automatiquement - IA temporairement indisponible"],
            score_equilibre=50,
            score_variete=50
        )

    # ===================================
    # OPTIMISATION PLANNING EXISTANT
    # ===================================

    async def optimiser_planning_existant(
            self,
            planning_actuel: List[Dict],
            config: ConfigPlanningUtilisateur
    ) -> Dict[str, List[str]]:
        """
        Analyse un planning existant et propose des améliorations

        Args:
            planning_actuel: Planning actuel (liste de repas)
            config: Config utilisateur

        Returns:
            Dict avec suggestions d'amélioration
        """
        logger.info("Optimisation planning existant par IA")

        prompt = f"""Analyse ce planning de repas existant:

PLANNING ACTUEL:
{json.dumps(planning_actuel, indent=2, ensure_ascii=False)}

CONFIG:
- Adultes: {config.nb_adultes}
- Enfants: {config.nb_enfants}
- Bébé: {config.a_bebe}

ANALYSE:
1. Variété (répétitions, équilibre)
2. Équilibre nutritionnel
3. Complexité (trop de plats complexes?)
4. Optimisation temps

FORMAT JSON:
{{
  "points_forts": ["Point 1", "Point 2"],
  "ameliorations": [
    {{
      "jour": 1,
      "repas_actuel": "Nom",
      "suggestion": "Remplacer par X car...",
      "impact": "moyen"
    }}
  ],
  "conseils": ["Conseil 1", "Conseil 2"]
}}

JSON uniquement !"""

        try:
            response = await self._call_with_retry(
                prompt,
                "Expert nutritionniste. JSON uniquement.",
                1000
            )

            data = self._parse_json_response(response)
            return data

        except Exception as e:
            logger.error(f"Erreur optimisation: {e}")
            return {
                "points_forts": [],
                "ameliorations": [],
                "conseils": ["Optimisation indisponible"]
            }

    # ===================================
    # SUGGESTION REPAS UNIQUE
    # ===================================

    async def suggerer_repas_pour_slot(
            self,
            jour: int,
            type_repas: str,
            contexte: Dict
    ) -> List[Dict]:
        """
        Suggère des recettes pour un slot vide

        Args:
            jour: Jour de la semaine (0-6)
            type_repas: Type de repas
            contexte: Contexte (autres repas de la semaine, météo, etc.)

        Returns:
            Liste de suggestions avec raisons
        """
        logger.info(f"Suggestion repas: {self.JOURS_SEMAINE[jour]} - {type_repas}")

        recettes = self._get_recettes_disponibles()
        recettes_type = [r for r in recettes if r["type_repas"] == type_repas]

        if not recettes_type:
            return []

        prompt = f"""Suggère 3 recettes pour ce slot:

JOUR: {self.JOURS_SEMAINE[jour]}
TYPE: {type_repas}

CONTEXTE:
{json.dumps(contexte, indent=2, ensure_ascii=False)}

RECETTES DISPONIBLES ({len(recettes_type)}):
{json.dumps(recettes_type[:20], indent=2, ensure_ascii=False)}

FORMAT JSON:
{{
  "suggestions": [
    {{
      "recette_nom": "Nom",
      "raison": "Pourquoi cette recette",
      "score": 85
    }}
  ]
}}

JSON uniquement !"""

        try:
            response = await self._call_with_retry(
                prompt,
                "Expert cuisine. JSON.",
                600
            )

            data = self._parse_json_response(response)
            return data.get("suggestions", [])

        except Exception as e:
            logger.error(f"Erreur suggestion: {e}")
            # Fallback: prendre 3 recettes aléatoires
            import random
            return [
                {
                    "recette_nom": r["nom"],
                    "raison": "Suggestion automatique",
                    "score": 50
                }
                for r in random.sample(recettes_type, min(3, len(recettes_type)))
            ]


# ===================================
# FACTORY
# ===================================

def create_planning_generation_service(agent: AgentIA) -> PlanningGenerationService:
    """Factory pour créer le service"""
    return PlanningGenerationService(agent)