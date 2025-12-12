"""
Service IA Courses - Génération et Optimisation
Toute la logique IA isolée dans ce service
"""
import asyncio
import json
import logging
from typing import List, Dict, Optional
from pydantic import BaseModel, Field, validator

from src.core.ai_agent import AgentIA
from src.core.ai_cache import AICache, RateLimiter

logger = logging.getLogger(__name__)


# ===================================
# SCHÉMAS PYDANTIC
# ===================================

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

    @validator('article')
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


class Alternative(BaseModel):
    """Alternative pour un article"""
    nom: str
    raison: str
    prix_relatif: Optional[str] = None
    disponibilite: str = "haute"


# ===================================
# SERVICE IA
# ===================================

class CoursesAIService:
    """Service dédié aux fonctionnalités IA du module courses"""

    def __init__(self, agent: AgentIA):
        self.agent = agent

    # ===================================
    # GÉNÉRATION LISTE OPTIMISÉE
    # ===================================

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

        Args:
            articles_base: Articles bruts à optimiser
            magasin: Nom du magasin cible
            rayons_disponibles: Liste des rayons du magasin
            budget_max: Budget maximum en €
            preferences: Dict optionnel de préférences (bio, local, etc.)

        Returns:
            ListeOptimisee validée par Pydantic
        """
        logger.info(f"Génération liste IA: {len(articles_base)} articles, magasin={magasin}")

        # Vérifier rate limit
        can_call, error = RateLimiter.can_call()
        if not can_call:
            raise ValueError(error)

        # Consolider doublons AVANT l'IA
        consolides = self._consolider_doublons(articles_base)

        # Construire prompt
        prompt = self._build_prompt_optimisation(
            consolides,
            magasin,
            rayons_disponibles,
            budget_max,
            preferences
        )

        # Appel IA avec retry
        response = await self._call_with_retry(
            prompt,
            system_prompt="Expert en courses alimentaires. Réponds UNIQUEMENT en JSON valide.",
            max_tokens=2000
        )

        # Parser et valider
        try:
            data = self._parse_json_response(response)
            return ListeOptimisee(**data)
        except Exception as e:
            logger.error(f"Erreur parsing réponse IA: {e}")
            # Fallback simple
            return self._fallback_liste(consolides, rayons_disponibles)

    def _consolider_doublons(self, articles: List[Dict]) -> List[Dict]:
        """Consolide les doublons AVANT l'appel IA"""
        consolidation = {}

        for art in articles:
            key = art["nom"].lower().strip()
            if key in consolidation:
                # Fusion
                consolidation[key]["quantite"] = max(
                    consolidation[key]["quantite"],
                    art["quantite"]
                )
                # Upgrade priorité
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
                RateLimiter.record_call()
                return response
            except Exception as e:
                if attempt == max_retries - 1:
                    logger.error(f"IA failed after {max_retries} attempts: {e}")
                    raise
                await asyncio.sleep(2 ** attempt)  # Exponential backoff

    def _parse_json_response(self, response: str) -> Dict:
        """Parse la réponse JSON de l'IA"""
        # Nettoyer
        cleaned = response.strip()

        # Supprimer markdown
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        if cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]

        cleaned = cleaned.strip()

        # Parser
        return json.loads(cleaned)

    def _fallback_liste(
            self,
            articles: List[Dict],
            rayons: List[str]
    ) -> ListeOptimisee:
        """Liste de fallback si IA échoue"""
        logger.warning("Utilisation du fallback (IA indisponible)")

        # Organisation basique par catégorie
        par_rayon = {rayons[0]: []}

        for art in articles:
            par_rayon[rayons[0]].append(
                ArticleOptimise(
                    article=art["nom"],
                    quantite=art["quantite"],
                    unite=art["unite"],
                    priorite=art.get("priorite", "moyenne")
                )
            )

        return ListeOptimisee(
            par_rayon=par_rayon,
            conseils_globaux=["Service IA temporairement indisponible"]
        )

    # ===================================
    # ALTERNATIVES
    # ===================================

    async def proposer_alternatives(
            self,
            article: str,
            magasin: str,
            contexte: Optional[str] = None
    ) -> List[Alternative]:
        """
        Propose des alternatives pour un article

        Args:
            article: Nom de l'article
            magasin: Magasin cible
            contexte: Contexte optionnel (ex: "pour un gâteau")

        Returns:
            Liste d'alternatives
        """
        logger.info(f"Recherche alternatives: {article} @ {magasin}")

        prompt = f"""Propose 3 alternatives pour cet article dans {magasin}:

ARTICLE: {article}
{f"CONTEXTE: {contexte}" if contexte else ""}

CRITÈRES:
- Prix similaire ou inférieur
- Même utilisation culinaire
- Disponible en {magasin}

FORMAT JSON:
{{
  "alternatives": [
    {{
      "nom": "Alternative 1",
      "raison": "Moins cher et équivalent",
      "prix_relatif": "-20%",
      "disponibilite": "haute"
    }}
  ]
}}

UNIQUEMENT JSON !"""

        try:
            response = await self._call_with_retry(
                prompt,
                "Expert courses. JSON uniquement.",
                500
            )

            data = self._parse_json_response(response)
            return [Alternative(**alt) for alt in data.get("alternatives", [])]

        except Exception as e:
            logger.error(f"Erreur alternatives: {e}")
            return []

    # ===================================
    # ANALYSE HABITUDES
    # ===================================

    async def analyser_habitudes(
            self,
            historique: List[Dict],
            stats: Dict
    ) -> Dict[str, List[str]]:
        """
        Analyse les habitudes d'achat

        Args:
            historique: Liste articles achetés
            stats: Stats globales

        Returns:
            Dict avec {conseils: [...], opportunites: [...]}
        """
        logger.info("Analyse habitudes d'achat par IA")

        articles_freq = stats.get("articles_frequents", {})
        top10 = list(articles_freq.items())[:10]

        prompt = f"""Analyse ces habitudes d'achat:

TOP 10 ARTICLES: {top10}
TOTAL ACHATS: {stats.get('total_achetes', 0)}
PART IA: {stats.get('part_ia_achetes', 0)}
MOYENNE/SEMAINE: {stats.get('moyenne_semaine', 0):.1f}

FOURNIS:
1. 5 conseils personnalisés (optimisation, économie, planification)
2. 3 opportunités détectées

FORMAT JSON:
{{
  "conseils": [
    {{
      "type": "optimisation",
      "conseil": "Grouper les courses hebdomadaires",
      "impact": "moyen"
    }}
  ],
  "opportunites": [
    "Acheter en vrac pour X article",
    "Profiter des promos sur Y"
  ]
}}

JSON uniquement !"""

        try:
            response = await self._call_with_retry(
                prompt,
                "Expert gestion courses. JSON.",
                800
            )

            data = self._parse_json_response(response)
            return data

        except Exception as e:
            logger.error(f"Erreur analyse habitudes: {e}")
            return {
                "conseils": [],
                "opportunites": ["Analyse IA indisponible"]
            }


# ===================================
# HELPER INSTANTIATION
# ===================================

def create_courses_ai_service(agent: AgentIA) -> CoursesAIService:
    """Factory pour créer le service IA"""
    return CoursesAIService(agent)