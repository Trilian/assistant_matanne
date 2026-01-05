"""
Service IA Courses - Suggestions Intelligentes

Service IA pour générer des listes de courses optimisées :
1. Analyse planning + inventaire
2. Optimisation par magasin/rayon
3. Priorisation selon urgence (stock critique > planning)
4. Détection doublons avec inventaire
"""
import logging
from typing import Dict, List, Optional
from collections import defaultdict
from pydantic import BaseModel, Field

from src.core.ai import AIClient, get_ai_client
from src.services.base_ai_service import BaseAIService
from src.core.errors import handle_errors

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# MODÈLES PYDANTIC
# ═══════════════════════════════════════════════════════════

class CoursesSuggestion(BaseModel):
    """Suggestion d'article à acheter."""
    nom: str = Field(..., min_length=2, max_length=200)
    quantite: float = Field(..., gt=0)
    unite: str = Field(..., min_length=1)
    priorite: str = Field("moyenne", pattern="^(haute|moyenne|basse)$")
    raison: str = Field("", max_length=500, description="Pourquoi cet article")
    magasin: Optional[str] = None
    rayon: Optional[str] = None
    source: str = Field("ia", description="planning/inventaire/ia")


class ListeCoursesOptimisee(BaseModel):
    """Liste de courses complète optimisée."""
    articles: List[CoursesSuggestion] = Field(..., min_length=1)
    total_articles: int = Field(..., ge=1)
    repartition_magasins: Optional[Dict[str, int]] = None
    conseils: List[str] = Field(default_factory=list)


# ═══════════════════════════════════════════════════════════
# SERVICE IA COURSES
# ═══════════════════════════════════════════════════════════

class CoursesAIService(BaseAIService):
    """
    Service IA pour génération intelligente de listes de courses.

    Stratégies :
    1. Prioriser stock critique (inventaire)
    2. Ajouter ingrédients manquants (planning)
    3. Optimiser par magasin/rayon
    4. Éviter doublons avec inventaire actuel
    """

    def __init__(self, client: AIClient = None):
        """Initialise le service IA courses."""
        super().__init__(
            client=client or get_ai_client(),
            cache_prefix="courses_ai",
            default_ttl=900,  # 15min (données volatiles)
            default_temperature=0.7
        )

    # ═══════════════════════════════════════════════════════════
    # GÉNÉRATION LISTE COMPLÈTE
    # ═══════════════════════════════════════════════════════════

    @handle_errors(show_in_ui=True, fallback_value=None)
    async def generer_liste_courses(
            self,
            planning_semaine: Optional[Dict] = None,
            inventaire: Optional[List[Dict]] = None,
            config: Optional[Dict] = None
    ) -> Optional[ListeCoursesOptimisee]:
        """
        Génère liste de courses optimisée complète.

        Args:
            planning_semaine: Planning hebdomadaire (structure complète)
            inventaire: Inventaire actuel
            config: Configuration optionnelle
                {
                    "magasins_preferes": ["Grand Frais", "Thiriet"],
                    "budget_max": 150.0,
                    "eviter_ingredients": ["gluten"],
                }

        Returns:
            Liste optimisée avec répartition magasins

        Example:
            >>> liste = await ai_service.generer_liste_courses(
            ...     planning_semaine=planning,
            ...     inventaire=inventaire
            ... )
            >>> print(f"{liste.total_articles} articles répartis dans {len(liste.repartition_magasins)} magasins")
        """
        logger.info("🛒 Génération liste courses complète")

        # Construire contexte complet
        context = self._build_context_complet(planning_semaine, inventaire, config)

        # Prompt structuré
        prompt = self.build_json_prompt(
            context=context,
            task="Génère une liste de courses optimisée et réaliste",
            json_schema=self._get_schema_liste_complete(),
            constraints=[
                "Éviter doublons avec inventaire existant",
                "Prioriser articles en stock critique (priorite=haute)",
                "Grouper par magasin recommandé",
                "Quantités réalistes pour une semaine",
                "Inclure raison d'achat pour chaque article",
                "Maximum 30 articles au total"
            ]
        )

        try:
            liste = await self.call_with_parsing(
                prompt=prompt,
                response_model=ListeCoursesOptimisee,
                temperature=0.7,
                max_tokens=2500,
                use_cache=True
            )

            # Post-traitement : répartition magasins
            liste.repartition_magasins = self._calculer_repartition(liste.articles)

            logger.info(
                f"✅ Liste générée: {liste.total_articles} articles, "
                f"{len(liste.repartition_magasins)} magasins"
            )

            return liste

        except Exception as e:
            logger.error(f"Erreur génération liste: {e}")
            return self._get_fallback_liste(planning_semaine, inventaire)

    # ═══════════════════════════════════════════════════════════
    # SUGGESTIONS PAR SOURCE
    # ═══════════════════════════════════════════════════════════

    @handle_errors(show_in_ui=True, fallback_value=[])
    async def suggerer_depuis_planning(
            self,
            planning_semaine: Dict
    ) -> List[CoursesSuggestion]:
        """
        Suggère articles depuis le planning uniquement.

        Args:
            planning_semaine: Planning avec recettes

        Returns:
            Articles nécessaires pour les recettes prévues
        """
        logger.info("📅 Suggestions depuis planning")

        # Extraire ingrédients du planning
        ingredients_planning = self._extraire_ingredients_planning(planning_semaine)

        if not ingredients_planning:
            logger.warning("Aucun ingrédient extrait du planning")
            return []

        context = f"""PLANNING SEMAINE:
{len(planning_semaine.get('jours', []))} jours planifiés

INGRÉDIENTS NÉCESSAIRES:
{self._format_ingredients_list(ingredients_planning)}

Tâche: Liste les articles à acheter pour réaliser ce planning."""

        prompt = self.build_json_prompt(
            context=context,
            task="Génère liste d'achats pour le planning",
            json_schema=self._get_schema_articles(),
            constraints=[
                "Quantités adaptées au nombre de repas",
                "Priorité moyenne (planning anticipé)",
                "Source: planning"
            ]
        )

        try:
            suggestions = await self.call_with_list_parsing(
                prompt=prompt,
                item_model=CoursesSuggestion,
                list_key="articles",
                temperature=0.7,
                max_tokens=1500,
                use_cache=True,
                max_items=20
            )

            # Marquer source
            for sugg in suggestions:
                sugg.source = "planning"

            logger.info(f"✅ {len(suggestions)} suggestions depuis planning")
            return suggestions

        except Exception as e:
            logger.error(f"Erreur suggestions planning: {e}")
            return []

    @handle_errors(show_in_ui=True, fallback_value=[])
    async def suggerer_depuis_inventaire(
            self,
            inventaire: List[Dict]
    ) -> List[CoursesSuggestion]:
        """
        Suggère articles depuis inventaire (stock bas/critique).

        Args:
            inventaire: Inventaire actuel

        Returns:
            Articles en alerte à racheter prioritairement
        """
        logger.info("📦 Suggestions depuis inventaire")

        # Filtrer articles en alerte
        articles_alerte = [
            a for a in inventaire
            if a.get("statut") in ["critique", "sous_seuil"]
        ]

        if not articles_alerte:
            logger.info("Aucun article en alerte")
            return []

        context = f"""INVENTAIRE - ALERTES STOCK:
{len(articles_alerte)} articles nécessitent réapprovisionnement

ARTICLES EN ALERTE:
{self._format_inventaire_alerte(articles_alerte)}

Tâche: Génère liste prioritaire d'achats pour réapprovisionner."""

        prompt = self.build_json_prompt(
            context=context,
            task="Génère liste d'achats prioritaires depuis inventaire",
            json_schema=self._get_schema_articles(),
            constraints=[
                "Priorité haute pour stock critique",
                "Priorité moyenne pour stock bas",
                "Quantités pour atteindre niveau optimal",
                "Source: inventaire"
            ]
        )

        try:
            suggestions = await self.call_with_list_parsing(
                prompt=prompt,
                item_model=CoursesSuggestion,
                list_key="articles",
                temperature=0.6,  # Plus déterministe pour inventaire
                max_tokens=1500,
                use_cache=True,
                max_items=15
            )

            # Marquer source et forcer priorité
            for sugg in suggestions:
                sugg.source = "inventaire"

                # Trouver article original pour priorité exacte
                article_original = next(
                    (a for a in articles_alerte if a["nom"].lower() == sugg.nom.lower()),
                    None
                )

                if article_original:
                    if article_original.get("statut") == "critique":
                        sugg.priorite = "haute"
                    elif article_original.get("statut") == "sous_seuil":
                        sugg.priorite = "moyenne"

            logger.info(f"✅ {len(suggestions)} suggestions depuis inventaire")
            return suggestions

        except Exception as e:
            logger.error(f"Erreur suggestions inventaire: {e}")
            return []

    # ═══════════════════════════════════════════════════════════
    # OPTIMISATION MAGASIN
    # ═══════════════════════════════════════════════════════════

    @handle_errors(show_in_ui=False, fallback_value={})
    def optimiser_par_magasin(
            self,
            articles: List[CoursesSuggestion],
            magasins_config: Optional[Dict] = None
    ) -> Dict[str, List[CoursesSuggestion]]:
        """
        Optimise répartition par magasin.

        Args:
            articles: Articles à répartir
            magasins_config: Config magasins disponibles

        Returns:
            {magasin: [articles]}

        Example:
            >>> repartition = ai_service.optimiser_par_magasin(suggestions)
            >>> for magasin, articles in repartition.items():
            ...     print(f"{magasin}: {len(articles)} articles")
        """
        if not magasins_config:
            from src.services.courses import MAGASINS_CONFIG
            magasins_config = MAGASINS_CONFIG

        repartition = defaultdict(list)

        for article in articles:
            # Si magasin déjà défini, utiliser
            if article.magasin:
                repartition[article.magasin].append(article)
                continue

            # Sinon, deviner selon catégorie/nom
            magasin = self._deviner_magasin(article, magasins_config)
            article.magasin = magasin
            repartition[magasin].append(article)

        logger.info(f"Répartition: {dict((k, len(v)) for k, v in repartition.items())}")
        return dict(repartition)

    def _deviner_magasin(
            self,
            article: CoursesSuggestion,
            magasins_config: Dict
    ) -> str:
        """Devine le meilleur magasin pour un article."""
        nom_lower = article.nom.lower()

        # Règles heuristiques
        if any(kw in nom_lower for kw in ["légume", "fruit", "tomate", "salade"]):
            return "Grand Frais"

        if any(kw in nom_lower for kw in ["surgelé", "glace", "plat cuisiné"]):
            return "Thiriet"

        # Par défaut, supermarché généraliste
        return "Cora"

    # ═══════════════════════════════════════════════════════════
    # DÉTECTION DOUBLONS
    # ═══════════════════════════════════════════════════════════

    def filtrer_doublons_inventaire(
            self,
            suggestions: List[CoursesSuggestion],
            inventaire: List[Dict],
            seuil_suffisant: float = 0.8
    ) -> List[CoursesSuggestion]:
        """
        Filtre articles déjà en stock suffisant.

        Args:
            suggestions: Articles suggérés
            inventaire: Inventaire actuel
            seuil_suffisant: Ratio quantité/seuil considéré suffisant

        Returns:
            Articles à acheter (stock insuffisant)
        """
        articles_filtres = []

        # Map inventaire par nom (insensible casse)
        inv_map = {
            a["nom"].lower(): a
            for a in inventaire
        }

        for sugg in suggestions:
            nom_lower = sugg.nom.lower()

            # Vérifier si existe en inventaire
            if nom_lower in inv_map:
                article_inv = inv_map[nom_lower]

                # Calculer stock actuel vs besoin
                stock_actuel = article_inv.get("quantite", 0)
                seuil = article_inv.get("quantite_min", 1.0)

                # Stock suffisant ?
                if stock_actuel >= (seuil * seuil_suffisant):
                    logger.debug(
                        f"Article '{sugg.nom}' filtré (stock={stock_actuel}, seuil={seuil})"
                    )
                    continue

            # Ajouter à la liste
            articles_filtres.append(sugg)

        logger.info(
            f"Filtrage doublons: {len(suggestions)} -> {len(articles_filtres)} articles"
        )

        return articles_filtres

    # ═══════════════════════════════════════════════════════════
    # HELPERS PRIVÉS
    # ═══════════════════════════════════════════════════════════

    def _build_context_complet(
            self,
            planning: Optional[Dict],
            inventaire: Optional[List[Dict]],
            config: Optional[Dict]
    ) -> str:
        """Construit contexte pour génération complète."""
        context = "GÉNÉRATION LISTE DE COURSES OPTIMISÉE\n\n"

        # Planning
        if planning:
            nb_repas = sum(len(j.get("repas", [])) for j in planning.get("jours", []))
            context += f"📅 PLANNING:\n- {nb_repas} repas prévus cette semaine\n"

            # Extraire recettes
            recettes = []
            for jour in planning.get("jours", []):
                for repas in jour.get("repas", []):
                    if repas.get("recette"):
                        recettes.append(repas["recette"].get("nom", "?"))

            if recettes:
                context += f"- Recettes: {', '.join(recettes[:5])}"
                if len(recettes) > 5:
                    context += f" (+{len(recettes)-5})"
                context += "\n"

        # Inventaire
        if inventaire:
            context += f"\n📦 INVENTAIRE:\n- {len(inventaire)} articles en stock\n"

            alertes = [a for a in inventaire if a.get("statut") in ["critique", "sous_seuil"]]
            if alertes:
                context += f"- ⚠️ {len(alertes)} articles en alerte:\n"
                for art in alertes[:5]:
                    context += f"  • {art['nom']}: {art['quantite']} {art['unite']} (statut: {art['statut']})\n"

        # Config
        if config:
            context += "\n⚙️ PRÉFÉRENCES:\n"
            if config.get("magasins_preferes"):
                context += f"- Magasins préférés: {', '.join(config['magasins_preferes'])}\n"
            if config.get("budget_max"):
                context += f"- Budget max: {config['budget_max']}€\n"

        return context

    def _extraire_ingredients_planning(self, planning: Dict) -> List[Dict]:
        """Extrait tous les ingrédients du planning."""
        ingredients = []

        for jour in planning.get("jours", []):
            for repas in jour.get("repas", []):
                if repas.get("recette"):
                    # Note: Dans un vrai système, on chargerait les ingrédients de la recette
                    recette_nom = repas["recette"].get("nom", "")
                    ingredients.append({
                        "recette": recette_nom,
                        "jour": jour.get("nom_jour"),
                        "type": repas.get("type")
                    })

        return ingredients

    def _format_ingredients_list(self, ingredients: List[Dict]) -> str:
        """Formate liste ingrédients pour prompt."""
        if not ingredients:
            return "Aucun ingrédient"

        lines = []
        for ing in ingredients[:10]:
            lines.append(f"- {ing.get('recette')} ({ing.get('jour')})")

        return "\n".join(lines)

    def _format_inventaire_alerte(self, articles: List[Dict]) -> str:
        """Formate articles en alerte pour prompt."""
        lines = []

        for art in articles[:10]:
            statut_icon = "🔴" if art.get("statut") == "critique" else "⚠️"
            lines.append(
                f"{statut_icon} {art['nom']}: {art['quantite']} {art['unite']} "
                f"(seuil: {art.get('quantite_min', '?')})"
            )

        return "\n".join(lines)

    def _calculer_repartition(self, articles: List[CoursesSuggestion]) -> Dict[str, int]:
        """Calcule répartition par magasin."""
        repartition = defaultdict(int)

        for article in articles:
            magasin = article.magasin or "Non défini"
            repartition[magasin] += 1

        return dict(repartition)

    def _get_schema_liste_complete(self) -> str:
        """Schéma JSON liste complète."""
        return """
{
  "articles": [
    {
      "nom": "Tomates",
      "quantite": 1.5,
      "unite": "kg",
      "priorite": "haute",
      "raison": "Stock critique + recette prévue mardi",
      "magasin": "Grand Frais",
      "rayon": "Fruits & Légumes"
    }
  ],
  "total_articles": 15,
  "conseils": [
    "Commencer par Grand Frais pour le frais",
    "Vérifier dates de péremption courtes"
  ]
}
"""

    def _get_schema_articles(self) -> str:
        """Schéma JSON articles simples."""
        return """
{
  "articles": [
    {
      "nom": "Article",
      "quantite": 2.0,
      "unite": "kg",
      "priorite": "moyenne",
      "raison": "Raison de l'achat"
    }
  ]
}
"""

    def _get_fallback_liste(
            self,
            planning: Optional[Dict],
            inventaire: Optional[List[Dict]]
    ) -> ListeCoursesOptimisee:
        """Liste de secours basique."""
        articles = []

        # Articles depuis inventaire critique
        if inventaire:
            for art in inventaire:
                if art.get("statut") == "critique":
                    articles.append(CoursesSuggestion(
                        nom=art["nom"],
                        quantite=art.get("quantite_min", 1.0),
                        unite=art["unite"],
                        priorite="haute",
                        raison="Stock critique",
                        source="inventaire"
                    ))

        # Si rien, article générique
        if not articles:
            articles.append(CoursesSuggestion(
                nom="Pain",
                quantite=1,
                unite="pcs",
                priorite="moyenne",
                raison="Article de base"
            ))

        return ListeCoursesOptimisee(
            articles=articles,
            total_articles=len(articles),
            conseils=["Liste de secours - Génération IA échouée"]
        )


# ═══════════════════════════════════════════════════════════
# FACTORY
# ═══════════════════════════════════════════════════════════

def create_courses_ai_service(client: AIClient = None) -> CoursesAIService:
    """
    Factory pour créer service IA courses.

    Args:
        client: Client IA optionnel

    Returns:
        Instance CoursesAIService
    """
    return CoursesAIService(client or get_ai_client())