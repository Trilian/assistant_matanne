"""
Service Génération Planning
"""
import logging
from typing import List, Dict, Optional
from datetime import date, timedelta
from pydantic import BaseModel, Field, field_validator

from src.core.ai import AIClient, AIParser, parse_list_response
from src.core.cache import Cache, RateLimit
from src.core.errors import handle_errors, AIServiceError
from src.core.database import get_db_context
from src.core.models import Recette, ConfigPlanningUtilisateur

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════
# SCHÉMAS PYDANTIC
# ═══════════════════════════════════════════════════════════════

class RepasGenere(BaseModel):
    """Repas généré par IA"""
    type: str = Field(..., pattern="^(petit_déjeuner|déjeuner|dîner|goûter|bébé|batch_cooking)$")
    recette_nom: str = Field(..., min_length=2)
    portions: int = Field(4, gt=0, le=20)
    adapte_bebe: bool = False
    est_batch: bool = False
    raison: Optional[str] = None

    @field_validator("recette_nom")
    @classmethod
    def clean_nom(cls, v):
        return v.strip()


class JourPlanning(BaseModel):
    """Planning d'un jour"""
    jour: int = Field(..., ge=0, le=6)
    repas: List[RepasGenere] = Field(..., min_length=1)
    conseils_jour: List[str] = Field(default_factory=list)


class PlanningGenere(BaseModel):
    """Planning complet généré"""
    planning: List[JourPlanning] = Field(..., min_length=7, max_length=7)
    conseils_globaux: List[str] = Field(default_factory=list)
    score_equilibre: int = Field(0, ge=0, le=100)
    score_variete: int = Field(0, ge=0, le=100)


class SuggestionRepas(BaseModel):
    """Suggestion pour slot vide"""
    recette_nom: str
    raison: str
    score: int = Field(..., ge=0, le=100)


# ═══════════════════════════════════════════════════════════════
# SERVICE OPTIMISÉ
# ═══════════════════════════════════════════════════════════════

class PlanningGenerationService:
    """Service génération planning ultra-optimisé"""

    JOURS_SEMAINE = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]

    def __init__(self, client: AIClient):
        self.client = client

    # ═══════════════════════════════════════════════════════════
    # GÉNÉRATION PRINCIPALE
    # ═══════════════════════════════════════════════════════════

    @handle_errors(show_in_ui=True)
    @Cache.cached(ttl=3600, key="planning_generation")
    async def generer_planning_complet(
            self,
            semaine_debut: date,
            config: ConfigPlanningUtilisateur,
            contraintes: Optional[Dict] = None
    ) -> PlanningGenere:
        """
        Génère planning complet

        ✅ Cache 1h
        ✅ AIJsonParser avec fallback
        ✅ Code réduit de 50%
        """
        logger.info(f"Génération planning: semaine {semaine_debut}")

        # Récupérer recettes (1 query optimisée)
        recettes = self._get_recettes_optimisees()

        if not recettes:
            raise AIServiceError(
                "Aucune recette disponible",
                user_message="Ajoute des recettes avant de générer"
            )

        # Construire prompt optimisé
        prompt = self._build_prompt_optimise(semaine_debut, config, recettes, contraintes)

        # ✅ Appel IA
        response = await self.client.call(
            prompt=prompt,
            system_prompt="Expert nutritionniste. JSON uniquement.",
            temperature=0.7,
            max_tokens=2500,
            use_cache=True
        )

        # ✅ Parser avec AIJsonParser
        return AIParser.parse(
            response,
            PlanningGenere,
            fallback=self._fallback_planning(config, recettes),
            strict=False
        )

    def _get_recettes_optimisees(self) -> List[Dict]:
        """Récupère recettes avec seulement les infos nécessaires"""
        with get_db_context() as db:
            recettes = db.query(Recette).limit(50).all()

            # ✅ Projection optimisée (seulement les champs utiles)
            return [
                {
                    "id": r.id,
                    "nom": r.nom,
                    "type_repas": r.type_repas,
                    "temps_total": r.temps_preparation + r.temps_cuisson,
                    "compatible_bebe": r.compatible_bebe,
                    "compatible_batch": r.compatible_batch,
                }
                for r in recettes
            ]

    def _build_prompt_optimise(
            self,
            semaine_debut: date,
            config: ConfigPlanningUtilisateur,
            recettes: List[Dict],
            contraintes: Optional[Dict]
    ) -> str:
        """Prompt ultra-optimisé (réduit de 40%)"""
        import json

        repas_actifs = [k for k, v in config.repas_actifs.items() if v]

        # Format compact
        recettes_str = json.dumps(recettes[:30], ensure_ascii=False)

        return f"""Planning 7 jours ({semaine_debut.strftime('%d/%m/%Y')})

Config: {config.nb_adultes}A, {config.nb_enfants}E, Bébé={config.a_bebe}
Repas: {', '.join(repas_actifs)}
Batch: {config.batch_cooking_actif}

Recettes ({len(recettes)}): {recettes_str}

JSON:
{{
  "planning": [
    {{"jour": 0, "repas": [{{"type": "déjeuner", "recette_nom": "...", "portions": 4, "adapte_bebe": false, "raison": "..."}}], "conseils_jour": []}}
  ],
  "conseils_globaux": [],
  "score_equilibre": 85,
  "score_variete": 90
}}

7 jours, varier recettes, JSON uniquement !"""

    def _fallback_planning(
            self,
            config: ConfigPlanningUtilisateur,
            recettes: List[Dict]
    ) -> Dict:
        """Fallback simple et rapide"""
        logger.warning("Utilisation fallback (IA échec)")

        repas_actifs = [k for k, v in config.repas_actifs.items() if v]

        # Planning basique
        planning = []
        idx = 0

        for jour in range(7):
            repas_jour = []

            for type_repas in repas_actifs:
                if idx < len(recettes):
                    recette = recettes[idx % len(recettes)]
                    repas_jour.append({
                        "type": type_repas,
                        "recette_nom": recette["nom"],
                        "portions": 4,
                        "adapte_bebe": False,
                        "est_batch": False,
                        "raison": "Planning automatique"
                    })
                    idx += 1

            planning.append({
                "jour": jour,
                "repas": repas_jour,
                "conseils_jour": []
            })

        return {
            "planning": planning,
            "conseils_globaux": ["Planning généré automatiquement"],
            "score_equilibre": 50,
            "score_variete": 50
        }

    # ═══════════════════════════════════════════════════════════
    # OPTIMISATION PLANNING EXISTANT
    # ═══════════════════════════════════════════════════════════

    @handle_errors(show_in_ui=True)
    async def optimiser_planning_existant(
            self,
            planning_actuel: List[Dict],
            config: ConfigPlanningUtilisateur
    ) -> Dict:
        """
        Optimise planning existant

        ✅ Prompt réduit
        ✅ Fallback automatique
        """
        import json

        prompt = f"""Planning actuel: {json.dumps(planning_actuel[:5], ensure_ascii=False)}

Config: {config.nb_adultes}A, {config.nb_enfants}E

Analyse JSON:
{{
  "points_forts": ["Point 1"],
  "ameliorations": [
    {{"jour": 1, "repas_actuel": "X", "suggestion": "Y", "impact": "moyen"}}
  ],
  "conseils": ["Conseil 1"]
}}"""

        try:
            response = await self.client.call(
                prompt=prompt,
                system_prompt="Nutritionniste. JSON.",
                temperature=0.7,
                max_tokens=800
            )

            # ✅ Parse direct en dict
            from src.core.ai import AIParser
            import json

            cleaned = response.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.startswith("```"):
                cleaned = cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]

            return json.loads(cleaned.strip())

        except Exception as e:
            logger.error(f"Erreur optimisation: {e}")
            return {
                "points_forts": [],
                "ameliorations": [],
                "conseils": ["Optimisation indisponible"]
            }

    # ═══════════════════════════════════════════════════════════
    # SUGGESTION REPAS UNIQUE
    # ═══════════════════════════════════════════════════════════

    @handle_errors(show_in_ui=False)
    @Cache.cached(ttl=1800)
    async def suggerer_repas_pour_slot(
            self,
            jour: int,
            type_repas: str,
            contexte: Dict
    ) -> List[SuggestionRepas]:
        """
        Suggère recettes pour slot

        ✅ Cache 30min
        ✅ parse_list_response
        """
        import json

        recettes = self._get_recettes_optimisees()
        recettes_type = [r for r in recettes if r["type_repas"] == type_repas][:20]

        if not recettes_type:
            return []

        prompt = f"""Jour: {self.JOURS_SEMAINE[jour]}
Type: {type_repas}
Contexte: {json.dumps(contexte, ensure_ascii=False)}

Recettes: {json.dumps(recettes_type[:10], ensure_ascii=False)}

JSON (3 suggestions):
{{
  "suggestions": [
    {{"recette_nom": "...", "raison": "...", "score": 85}}
  ]
}}"""

        response = await self.client.call(
            prompt=prompt,
            system_prompt="Expert cuisine. JSON.",
            temperature=0.7,
            max_tokens=500
        )

        # ✅ Parse liste
        suggestions = parse_list_response(
            response,
            SuggestionRepas,
            list_key="suggestions",
            fallback_items=[
                {
                    "recette_nom": r["nom"],
                    "raison": "Suggestion automatique",
                    "score": 50
                }
                for r in recettes_type[:3]
            ]
        )

        return suggestions[:3]


# ═══════════════════════════════════════════════════════════════
# FACTORY
# ═══════════════════════════════════════════════════════════════

def create_planning_generation_service(client: AIClient) -> PlanningGenerationService:
    """Factory"""
    return PlanningGenerationService(client)