"""
Services IA Refactorisés - Héritent tous de BaseAIService
"""
import logging
from typing import Dict, List, Optional
from datetime import date
from pydantic import BaseModel, Field

from src.core.ai import AIClient
from src.services.base_ai_service import BaseAIService, RecipeAIMixin, PlanningAIMixin, InventoryAIMixin
from src.core.validation import validate_model, RecetteInput, ArticleCoursesInput, ArticleInventaireInput

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# SCHÉMAS PYDANTIC
# ═══════════════════════════════════════════════════════════

class RecetteSuggestion(BaseModel):
    """Suggestion de recette générée par IA"""
    nom: str = Field(..., min_length=3, max_length=200)
    description: str = Field(..., min_length=10)
    temps_preparation: int = Field(..., gt=0, le=300)
    temps_cuisson: int = Field(..., ge=0, le=300)
    portions: int = Field(4, gt=0, le=20)
    difficulte: str = Field("moyen", pattern="^(facile|moyen|difficile)$")
    ingredients: List[Dict] = Field(..., min_length=1)
    etapes: List[Dict] = Field(..., min_length=1)


class CoursesSuggestion(BaseModel):
    """Suggestion d'articles courses"""
    nom: str = Field(..., min_length=2)
    quantite: float = Field(..., gt=0)
    unite: str = Field(..., min_length=1)
    priorite: str = Field("moyenne", pattern="^(haute|moyenne|basse)$")
    raison: str = Field("", max_length=500)


class InventaireSuggestion(BaseModel):
    """Suggestion inventaire"""
    nom: str = Field(..., min_length=2)
    categorie: str
    quantite_recommandee: float = Field(..., gt=0)
    unite: str
    raison: str = Field("", max_length=500)


class PlanningSemaine(BaseModel):
    """Planning hebdomadaire généré"""
    jours: List[Dict] = Field(..., min_length=7, max_length=7)


# ═══════════════════════════════════════════════════════════
# SERVICE RECETTES IA
# ═══════════════════════════════════════════════════════════

class AIRecetteService(BaseAIService, RecipeAIMixin):
    """Service IA pour recettes - Version refactorisée"""

    def __init__(self, client: AIClient):
        super().__init__(
            client=client,
            cache_prefix="recettes_ai",
            default_ttl=3600,  # 1h pour recettes
            default_temperature=0.8  # Plus créatif
        )

    async def generer_recettes(
            self,
            filters: Dict,
            ingredients_dispo: Optional[List[str]] = None,
            nb_recettes: int = 3
    ) -> List[RecetteSuggestion]:
        """
        Génère des suggestions de recettes

        🆕 Avec feedback temps réel et validation stricte
        """
        import streamlit as st

        # Feedback utilisateur
        with st.spinner(f"🤖 Génération de {nb_recettes} recettes..."):
            # Construire contexte
            context = self.build_recipe_context(filters, ingredients_dispo, nb_recettes)

            # Construire prompt structuré
            prompt = self.build_json_prompt(
                context=context,
                task=f"Génère {nb_recettes} recettes originales et réalisables",
                json_schema=self._get_recettes_schema(),
                constraints=[
                    "Ingrédients facilement trouvables",
                    "Instructions claires et détaillées",
                    "Temps réalistes",
                    "Portions adaptées à une famille"
                ]
            )

            # Appel IA avec parsing
            try:
                recettes = await self.call_with_list_parsing(
                    prompt=prompt,
                    item_model=RecetteSuggestion,
                    list_key="recettes",
                    temperature=0.8,
                    max_tokens=3000,
                    use_cache=True,
                    max_items=nb_recettes
                )

                # Validation métier supplémentaire
                recettes_valides = []
                for recette in recettes:
                    is_valid, error_msg, validated = validate_model(
                        RecetteInput,
                        {
                            **recette.dict(),
                            "type_repas": filters.get("type_repas", "dîner"),
                            "saison": filters.get("saison", "toute_année")
                        }
                    )

                    if is_valid:
                        recettes_valides.append(recette)
                    else:
                        logger.warning(f"Recette invalide ignorée: {error_msg}")

                st.success(f"✅ {len(recettes_valides)} recettes générées !")
                return recettes_valides

            except Exception as e:
                st.error(f"❌ Erreur génération: {str(e)}")
                logger.exception("Erreur génération recettes")
                return self._get_fallback_recettes(nb_recettes)

    async def adapter_recette_bebe(self, recette_id: int) -> Optional[Dict]:
        """Adapte recette pour bébé avec validation stricte"""
        import streamlit as st

        with st.spinner("👶 Adaptation en cours..."):
            from src.services.recettes import recette_service
            recette = recette_service.get_by_id_full(recette_id)

            if not recette:
                st.error("Recette introuvable")
                return None

            prompt = self._build_prompt_bebe(recette)

            try:
                result = await self.call_with_parsing(
                    prompt=prompt,
                    response_model=VersionBebeGeneree,
                    temperature=0.7,
                    max_tokens=1500,
                    use_cache=True
                )

                st.success("✅ Version bébé prête !")
                return result.dict()

            except Exception as e:
                st.error(f"❌ Erreur adaptation: {str(e)}")
                return None

    def _get_recettes_schema(self) -> str:
        """Schéma JSON pour recettes"""
        return """
{
  "recettes": [
    {
      "nom": "Nom de la recette",
      "description": "Description appétissante",
      "temps_preparation": 20,
      "temps_cuisson": 30,
      "portions": 4,
      "difficulte": "facile|moyen|difficile",
      "ingredients": [
        {"nom": "Tomates", "quantite": 3, "unite": "pcs", "optionnel": false}
      ],
      "etapes": [
        {"ordre": 1, "description": "Étape détaillée", "duree": 10}
      ]
    }
  ]
}
"""

    def _get_fallback_recettes(self, nb: int) -> List[RecetteSuggestion]:
        """Fallback en cas d'erreur"""
        return [
            RecetteSuggestion(
                nom=f"Recette Simple {i+1}",
                description="Recette de secours",
                temps_preparation=15,
                temps_cuisson=20,
                portions=4,
                difficulte="facile",
                ingredients=[{"nom": "Ingrédient", "quantite": 1, "unite": "pcs"}],
                etapes=[{"ordre": 1, "description": "Préparer", "duree": 15}]
            )
            for i in range(nb)
        ]

    def _build_prompt_bebe(self, recette) -> str:
        """Prompt pour adaptation bébé"""
        ingredients_str = "\n".join([
            f"- {ing.quantite} {ing.unite} {ing.ingredient.nom}"
            for ing in recette.ingredients
        ])

        return f"""Adapte cette recette pour BÉBÉ 6-18 mois.

RECETTE: {recette.nom}

INGRÉDIENTS:
{ingredients_str}

CONTRAINTES STRICTES:
- AUCUN sel, sucre, miel
- Texture adaptée (purée/morceaux selon âge)
- Cuisson complète obligatoire
- Identifie allergènes

FORMAT JSON:
{{
  "instructions_modifiees": "Instructions adaptées bébé",
  "notes_bebe": "Précautions allergènes, âge minimum",
  "age_minimum_mois": 8
}}

UNIQUEMENT JSON !"""


# ═══════════════════════════════════════════════════════════
# SERVICE COURSES IA
# ═══════════════════════════════════════════════════════════

class CoursesAIService(BaseAIService):
    """Service IA pour courses - Version refactorisée"""

    def __init__(self, client: AIClient):
        super().__init__(
            client=client,
            cache_prefix="courses_ai",
            default_ttl=1800,  # 30min
            default_temperature=0.7
        )

    async def generer_liste_courses(
            self,
            planning_semaine: Dict,
            inventaire: List[Dict]
    ) -> List[CoursesSuggestion]:
        """
        Génère liste de courses intelligente

        🆕 Avec analyse inventaire et optimisation magasins
        """
        import streamlit as st

        with st.spinner("🛒 Analyse des besoins..."):
            # Construire contexte
            context = self._build_courses_context(planning_semaine, inventaire)

            prompt = self.build_json_prompt(
                context=context,
                task="Génère liste de courses optimisée",
                json_schema=self._get_courses_schema(),
                constraints=[
                    "Éviter doublons avec inventaire",
                    "Grouper par magasin",
                    "Prioriser selon urgence",
                    "Quantités réalistes"
                ]
            )

            try:
                courses = await self.call_with_list_parsing(
                    prompt=prompt,
                    item_model=CoursesSuggestion,
                    list_key="articles",
                    temperature=0.7,
                    max_tokens=2000,
                    use_cache=True
                )

                # Validation
                courses_valides = []
                for article in courses:
                    is_valid, _, validated = validate_model(
                        ArticleCoursesInput,
                        article.dict()
                    )
                    if is_valid:
                        courses_valides.append(article)

                st.success(f"✅ {len(courses_valides)} articles suggérés !")
                return courses_valides

            except Exception as e:
                st.error(f"❌ Erreur génération: {str(e)}")
                return []

    def _build_courses_context(self, planning: Dict, inventaire: List[Dict]) -> str:
        """Contexte pour génération courses"""
        nb_repas = sum(len(j.get("repas", [])) for j in planning.get("jours", []))

        stock_bas = [
            art for art in inventaire
            if art.get("statut") in ["sous_seuil", "critique"]
        ]

        context = f"Planning: {nb_repas} repas cette semaine\n"
        context += f"Inventaire: {len(inventaire)} articles\n"
        context += f"Stock bas: {len(stock_bas)} articles\n\n"

        if stock_bas:
            context += "ARTICLES MANQUANTS:\n"
            for art in stock_bas[:10]:
                context += f"- {art['nom']} ({art['quantite']} {art['unite']} restants)\n"

        return context

    def _get_courses_schema(self) -> str:
        return """
{
  "articles": [
    {
      "nom": "Nom article",
      "quantite": 2.5,
      "unite": "kg",
      "priorite": "haute|moyenne|basse",
      "raison": "Pourquoi cet article"
    }
  ]
}
"""


# ═══════════════════════════════════════════════════════════
# SERVICE INVENTAIRE IA
# ═══════════════════════════════════════════════════════════

class InventaireAIService(BaseAIService, InventoryAIMixin):
    """Service IA pour inventaire - Version refactorisée"""

    def __init__(self, client: AIClient):
        super().__init__(
            client=client,
            cache_prefix="inventaire_ai",
            default_ttl=1800,
            default_temperature=0.7
        )

    async def analyser_inventaire(self, inventaire: List[Dict]) -> Dict:
        """
        Analyse intelligente de l'inventaire

        🆕 Détection tendances et suggestions
        """
        import streamlit as st

        with st.spinner("📊 Analyse en cours..."):
            summary = self.build_inventory_summary(inventaire)

            prompt = f"""{summary}

Analyse cet inventaire et fournis:
1. Produits à commander en priorité
2. Produits proches péremption
3. Suggestions optimisation

FORMAT JSON:
{{
  "articles_prioritaires": [
    {{"nom": "...", "raison": "..."}}
  ],
  "alertes_peremption": [
    {{"nom": "...", "jours_restants": 3}}
  ],
  "suggestions": ["suggestion 1", "suggestion 2"]
}}

UNIQUEMENT JSON !"""

            try:
                from pydantic import BaseModel

                class AnalyseInventaire(BaseModel):
                    articles_prioritaires: List[Dict]
                    alertes_peremption: List[Dict]
                    suggestions: List[str]

                result = await self.call_with_parsing(
                    prompt=prompt,
                    response_model=AnalyseInventaire,
                    temperature=0.7,
                    max_tokens=1500,
                    use_cache=True
                )

                st.success("✅ Analyse terminée !")
                return result.dict()

            except Exception as e:
                st.error(f"❌ Erreur analyse: {str(e)}")
                return {
                    "articles_prioritaires": [],
                    "alertes_peremption": [],
                    "suggestions": []
                }


# ═══════════════════════════════════════════════════════════
# SERVICE PLANNING IA
# ═══════════════════════════════════════════════════════════

class PlanningGenerationService(BaseAIService, PlanningAIMixin):
    """Service IA pour planning - Version refactorisée"""

    def __init__(self, client: AIClient):
        super().__init__(
            client=client,
            cache_prefix="planning_ai",
            default_ttl=3600,
            default_temperature=0.8
        )

    async def generer_planning_semaine(
            self,
            config: Dict,
            semaine_debut: date,
            contraintes: Optional[List[str]] = None
    ) -> Optional[PlanningSemaine]:
        """
        Génère planning hebdomadaire optimisé

        🆕 Avec équilibrage nutritionnel et variété
        """
        import streamlit as st

        with st.spinner("📅 Génération du planning..."):
            context = self.build_planning_context(config, semaine_debut.strftime("%d/%m/%Y"))

            if contraintes:
                context += "\nCONTRAINTES:\n" + "\n".join(f"- {c}" for c in contraintes)

            prompt = self.build_json_prompt(
                context=context,
                task="Génère planning équilibré pour la semaine",
                json_schema=self._get_planning_schema(),
                constraints=[
                    "Variété des plats (pas 2x même recette)",
                    "Équilibre nutritionnel",
                    "Temps réaliste (soirs < 45min)",
                    "1-2 repas batch cooking"
                ]
            )

            try:
                result = await self.call_with_parsing(
                    prompt=prompt,
                    response_model=PlanningSemaine,
                    temperature=0.8,
                    max_tokens=3000,
                    use_cache=True
                )

                st.success("✅ Planning généré !")
                return result

            except Exception as e:
                st.error(f"❌ Erreur génération: {str(e)}")
                return None

    def _get_planning_schema(self) -> str:
        return """
{
  "jours": [
    {
      "jour": "Lundi",
      "repas": [
        {
          "type": "déjeuner",
          "nom_recette": "Nom",
          "temps_total": 45,
          "portions": 4
        }
      ]
    }
  ]
}
"""


# ═══════════════════════════════════════════════════════════
# FACTORIES (inchangées)
# ═══════════════════════════════════════════════════════════

def create_ai_recette_service(client: AIClient = None) -> AIRecetteService:
    """Factory pour service recettes IA"""
    from src.core.ai import get_ai_client
    return AIRecetteService(client or get_ai_client())


def create_courses_ai_service(client: AIClient = None) -> CoursesAIService:
    """Factory pour service courses IA"""
    from src.core.ai import get_ai_client
    return CoursesAIService(client or get_ai_client())


def create_inventaire_ai_service(client: AIClient = None) -> InventaireAIService:
    """Factory pour service inventaire IA"""
    from src.core.ai import get_ai_client
    return InventaireAIService(client or get_ai_client())


def create_planning_generation_service(client: AIClient = None) -> PlanningGenerationService:
    """Factory pour service planning IA"""
    from src.core.ai import get_ai_client
    return PlanningGenerationService(client or get_ai_client())


# ═══════════════════════════════════════════════════════════
# CLASSE TEMPORAIRE POUR RÉTROCOMPATIBILITÉ
# ═══════════════════════════════════════════════════════════

class VersionBebeGeneree(BaseModel):
    """Version bébé générée par IA"""
    instructions_modifiees: str = Field(..., min_length=10)
    notes_bebe: str = Field(..., min_length=10)
    age_minimum_mois: int = Field(6, ge=6, le=36)