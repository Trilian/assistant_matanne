"""
Service IA Courses OPTIMISÉ
Utilise AIJsonParser + Cache

"""
import asyncio
import logging
from typing import List, Dict, Optional
from pydantic import BaseModel, Field, field_validator

from src.core.ai_agent import AgentIA
from src.core.ai_json_parser import AIJsonParser
from src.core.cache import Cache, RateLimit  # ✅ CORRIGÉ
from src.core.exceptions import AIServiceError, handle_errors

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════
# SCHÉMAS PYDANTIC
# ═══════════════════════════════════════════════════════════════

class ArticleOptimise(BaseModel):
    """Article optimisé par IA"""
    article: str = Field(..., min_length=2)
    quantite: float = Field(..., gt=0)
    unite: str
    priorite: str = Field("moyenne", pattern="^(haute|moyenne|basse)$")
    prix_estime: Optional[float] = Field(None, ge=0)
    rayon: Optional[str] = None
    alternatives: List[str] = Field(default_factory=list)
    conseil: Optional[str] = None

    @field_validator('article')
    @classmethod
    def clean_article(cls, v):
        return v.strip()

class ListeOptimisee(BaseModel):
    """Résultat complet de l'optimisation IA"""
    par_rayon: Dict[str, List[ArticleOptimise]]
    doublons_detectes: List[Dict[str, str]] = Field(default_factory=list)
    budget_estime: float = Field(0.0, ge=0)
    depasse_budget: bool = False
    economies_possibles: float = Field(0.0, ge=0)
    conseils_globaux: List[str] = Field(default_factory=list)

# ═══════════════════════════════════════════════════════════════
# SERVICE IA OPTIMISÉ
# ═══════════════════════════════════════════════════════════════

class CoursesAIService:
    """
    Service IA pour courses

    ✅ Utilise AIJsonParser (pas de parsing manuel)
    ✅ Utilise Cache
    ✅ Code divisé par 2
    """

    def __init__(self, agent: AgentIA):
        self.agent = agent

    @handle_errors(show_in_ui=True)
    @Cache.cached(ttl=1800, key="courses_ai_generation")  # ✅ CORRIGÉ
    async def generer_liste_optimisee(
            self,
            articles_base: List[Dict],
            magasin: str,
            rayons_disponibles: List[str],
            budget_max: float,
            preferences: Optional[Dict] = None
    ) -> ListeOptimisee:
        """
        Génère une liste optimisée avec l'IA

        ✅ Utilise AIJsonParser pour parsing robuste
        ✅ Cache intelligent
        """
        logger.info(f"Génération liste IA: {len(articles_base)} articles, magasin={magasin}")

        # Vérifier rate limit
        can_call, error = RateLimit.can_call()  # ✅ CORRIGÉ
        if not can_call:
            raise AIServiceError(error, user_message=error)

        # Consolider doublons
        consolides = self._consolider_doublons(articles_base)

        # Construire prompt
        prompt = self._build_prompt_optimisation(
            consolides,
            magasin,
            rayons_disponibles,
            budget_max,
            preferences
        )

        # Appel IA
        response = await self._call_with_retry(
            prompt,
            system_prompt="Expert en courses alimentaires. Réponds UNIQUEMENT en JSON valide.",
            max_tokens=2000
        )

        # ✅ Parser avec AIJsonParser (robuste)
        try:
            result = AIJsonParser.parse(
                response,
                ListeOptimisee,
                fallback=self._get_fallback_liste(consolides, rayons_disponibles),
                strict=False
            )

            logger.info(f"✅ Liste optimisée générée")
            return result

        except Exception as e:
            logger.error(f"Erreur parsing: {e}")
            # Fallback si parsing échoue
            return self._get_fallback_liste(consolides, rayons_disponibles)

    # ═══════════════════════════════════════════════════════════════
    # HELPERS
    # ═══════════════════════════════════════════════════════════════

    def _consolider_doublons(self, articles: List[Dict]) -> List[Dict]:
        """Consolide les doublons AVANT l'appel IA"""
        consolidation = {}

        for art in articles:
            key = art["nom"].lower().strip()
            if key in consolidation:
                # Garder la plus grosse quantité
                consolidation[key]["quantite"] = max(
                    consolidation[key]["quantite"],
                    art["quantite"]
                )
                # Garder la plus haute priorité
                priorites = {"basse": 1, "moyenne": 2, "haute": 3}
                if priorites.get(art.get("priorite", "moyenne"), 2) > priorites.get(consolidation[key]["priorite"], 2):
                    consolidation[key]["priorite"] = art.get("priorite", "moyenne")
            else:
                consolidation[key] = art

        return list(consolidation.values())

    def _build_prompt_optimisation(
            self,
            articles: List[Dict],
            magasin: str,
            rayons: List[str],
            budget: float,
            preferences: Optional[Dict]
    ) -> str:
        """Construit le prompt d'optimisation"""
        import json

        pref_text = ""
        if preferences:
            if preferences.get("bio"):
                pref_text += "- Privilégier BIO\n"
            if preferences.get("local"):
                pref_text += "- Privilégier produits locaux\n"
            if preferences.get("economique"):
                pref_text += "- Optimiser coûts\n"

        return f"""Optimise cette liste de courses pour {magasin}.

ARTICLES ({len(articles)}):
{json.dumps(articles[:30], indent=2, ensure_ascii=False)}

RAYONS DISPONIBLES: {', '.join(rayons)}

BUDGET MAXIMUM: {budget}€

{f"PRÉFÉRENCES:\n{pref_text}" if pref_text else ""}

TÂCHES:
1. Classe chaque article dans le bon rayon
2. Estime le prix de chaque article (réaliste pour {magasin})
3. Propose 1-2 alternatives économiques PAR ARTICLE si pertinent
4. Détecte les doublons restants
5. Calcule le budget total
6. Donne 3 conseils d'optimisation

FORMAT JSON STRICT:
{{
  "par_rayon": {{
    "Rayon1": [
      {{
        "article": "nom exact",
        "quantite": 1.0,
        "unite": "kg",
        "priorite": "moyenne",
        "prix_estime": 2.5,
        "rayon": "Rayon1",
        "alternatives": ["Alternative 1", "Alternative 2"],
        "conseil": "Format familial recommandé"
      }}
    ]
  }},
  "doublons_detectes": [
    {{"articles": ["art1", "art2"], "conseil": "Grouper"}}
  ],
  "budget_estime": 45.5,
  "depasse_budget": false,
  "economies_possibles": 8.0,
  "conseils_globaux": [
    "Acheter en vrac pour économiser",
    "Privilégier marques distributeur",
    "Grouper surgelés et frais"
  ]
}}

UNIQUEMENT le JSON, aucun texte !"""

    async def _call_with_retry(
            self,
            prompt: str,
            system_prompt: str,
            max_tokens: int,
            max_retries: int = 3
    ) -> str:
        """Appel IA avec retry automatique"""
        for attempt in range(max_retries):
            try:
                response = await self.agent._call_mistral(
                    prompt=prompt,
                    system_prompt=system_prompt,
                    temperature=0.7,
                    max_tokens=max_tokens
                )
                RateLimit.record_call()  # ✅ CORRIGÉ
                return response
            except Exception as e:
                if attempt == max_retries - 1:
                    logger.error(f"IA failed after {max_retries} attempts: {e}")
                    raise
                await asyncio.sleep(2 ** attempt)

    def _get_fallback_liste(
            self,
            articles: List[Dict],
            rayons: List[str]
    ) -> Dict:
        """Liste de fallback si IA échoue"""
        logger.warning("Utilisation du fallback (IA indisponible)")

        par_rayon = {rayons[0]: []}

        for art in articles:
            par_rayon[rayons[0]].append({
                "article": art["nom"],
                "quantite": art["quantite"],
                "unite": art["unite"],
                "priorite": art.get("priorite", "moyenne"),
                "prix_estime": None,
                "rayon": rayons[0],
                "alternatives": [],
                "conseil": None
            })

        return {
            "par_rayon": par_rayon,
            "doublons_detectes": [],
            "budget_estime": 0.0,
            "depasse_budget": False,
            "economies_possibles": 0.0,
            "conseils_globaux": ["Service IA temporairement indisponible"]
        }

# Factory
def create_courses_ai_service(agent: AgentIA) -> CoursesAIService:
    """Factory pour créer le service IA"""
    return CoursesAIService(agent)