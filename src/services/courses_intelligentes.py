"""
Service Courses Intelligentes - Génération de liste de courses depuis planning repas.

Fonctionnalités:
- Analyse du planning semaine (repas planifiés)
- Extraction des ingrédients par recette
- Comparaison avec inventaire existant
- Génération liste optimisée avec quantités agrégées
- Suggestions substitutions / alternatives
"""

import logging
from datetime import date, timedelta
from typing import Optional
from collections import defaultdict
from pydantic import BaseModel, Field

from src.core.ai import obtenir_client_ia
from src.core.database import obtenir_contexte_db
from src.core.decorators import avec_session_db, avec_gestion_erreurs
from src.core.models import Planning, Repas, Recette, Ingredient, RecetteIngredient, ArticleCourses, ArticleInventaire
from src.services.base_ai_service import BaseAIService
from src.services.courses import get_courses_service

from sqlalchemy.orm import Session, selectinload

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# MODÈLES DE DONNÉES
# ═══════════════════════════════════════════════════════════

class ArticleCourse(BaseModel):
    """Article à ajouter à la liste de courses."""
    nom: str = Field(description="Nom de l'ingrédient")
    quantite: float = Field(description="Quantité nécessaire")
    unite: str = Field(default="", description="Unité de mesure")
    rayon: str = Field(default="Autre", description="Rayon du magasin")
    recettes_source: list[str] = Field(default_factory=list, description="Recettes nécessitant cet ingrédient")
    priorite: int = Field(default=2, description="Priorité 1-3")
    en_stock: float = Field(default=0, description="Quantité déjà en stock")
    a_acheter: float = Field(default=0, description="Quantité à acheter")
    notes: str = Field(default="", description="Notes")


class ListeCoursesIntelligente(BaseModel):
    """Liste de courses générée intelligemment."""
    articles: list[ArticleCourse] = Field(default_factory=list)
    total_articles: int = Field(default=0)
    recettes_couvertes: list[str] = Field(default_factory=list)
    estimation_budget: Optional[float] = Field(default=None)
    alertes: list[str] = Field(default_factory=list)


class SuggestionSubstitution(BaseModel):
    """Suggestion de substitution d'ingrédient."""
    ingredient_original: str
    suggestion: str
    raison: str
    economie_estimee: Optional[float] = None


# ═══════════════════════════════════════════════════════════
# CONSTANTES
# ═══════════════════════════════════════════════════════════

MAPPING_RAYONS = {
    # Fruits & Légumes
    "tomate": "Fruits & Légumes",
    "carotte": "Fruits & Légumes", 
    "oignon": "Fruits & Légumes",
    "ail": "Fruits & Légumes",
    "pomme de terre": "Fruits & Légumes",
    "courgette": "Fruits & Légumes",
    "poivron": "Fruits & Légumes",
    "salade": "Fruits & Légumes",
    "haricot": "Fruits & Légumes",
    
    # Viandes
    "poulet": "Boucherie",
    "boeuf": "Boucherie",
    "porc": "Boucherie",
    "veau": "Boucherie",
    "agneau": "Boucherie",
    "steak": "Boucherie",
    "escalope": "Boucherie",
    
    # Poissons
    "saumon": "Poissonnerie",
    "cabillaud": "Poissonnerie",
    "crevette": "Poissonnerie",
    "thon": "Poissonnerie",
    
    # Crèmerie
    "lait": "Crèmerie",
    "beurre": "Crèmerie",
    "crème": "Crèmerie",
    "fromage": "Crèmerie",
    "yaourt": "Crèmerie",
    "œuf": "Crèmerie",
    "oeuf": "Crèmerie",
    
    # Epicerie
    "pâtes": "Épicerie",
    "riz": "Épicerie",
    "huile": "Épicerie",
    "vinaigre": "Épicerie",
    "sel": "Épicerie",
    "poivre": "Épicerie",
    "farine": "Épicerie",
    "sucre": "Épicerie",
    "conserve": "Épicerie",
    
    # Surgelés
    "surgelé": "Surgelés",
    "glace": "Surgelés",
}

PRIORITES = {
    "Boucherie": 1,  # Priorité haute (périmé vite)
    "Poissonnerie": 1,
    "Crèmerie": 1,
    "Fruits & Légumes": 2,
    "Surgelés": 2,
    "Épicerie": 3,  # Priorité basse (se conserve)
    "Autre": 3,
}


# ═══════════════════════════════════════════════════════════
# SERVICE COURSES INTELLIGENTES
# ═══════════════════════════════════════════════════════════

class CoursesIntelligentesService(BaseAIService):
    """Service pour générer des listes de courses intelligentes depuis le planning."""
    
    def __init__(self):
        client = obtenir_client_ia()
        if client is None:
            raise RuntimeError("Client IA non disponible")
        super().__init__(
            client=client,
            cache_prefix="courses_intel",
            default_ttl=1800,
            service_name="courses_intelligentes"
        )
    
    def _determiner_rayon(self, nom_ingredient: str) -> str:
        """Détermine le rayon d'un ingrédient."""
        nom_lower = nom_ingredient.lower()
        for mot_cle, rayon in MAPPING_RAYONS.items():
            if mot_cle in nom_lower:
                return rayon
        return "Autre"
    
    def _determiner_priorite(self, rayon: str) -> int:
        """Détermine la priorité basée sur le rayon."""
        return PRIORITES.get(rayon, 3)
    
    @avec_gestion_erreurs(default_return=None)
    @avec_session_db
    def obtenir_planning_actif(self, db: Session | None = None) -> Optional[Planning]:
        """Récupère le planning actif avec ses repas et recettes."""
        planning = (
            db.query(Planning)
            .options(
                selectinload(Planning.repas)
                .selectinload(Repas.recette)
                .selectinload(Recette.ingredients)
            )
            .filter(Planning.actif == True)
            .first()
        )
        return planning
    
    @avec_gestion_erreurs(default_return={})
    @avec_session_db
    def obtenir_stock_actuel(self, db: Session | None = None) -> dict[str, float]:
        """Récupère le stock actuel sous forme de dictionnaire {nom: quantite}."""
        stocks = (
            db.query(ArticleInventaire)
            .options(selectinload(ArticleInventaire.ingredient))
            .filter(ArticleInventaire.quantite > 0)
            .all()
        )
        return {
            stock.ingredient.nom.lower(): stock.quantite 
            for stock in stocks
            if stock.ingredient
        }
    
    def extraire_ingredients_planning(self, planning: Planning) -> list[ArticleCourse]:
        """Extrait tous les ingrédients des recettes du planning."""
        from typing import Any
        
        # Agrégateur: {nom_ingredient: {quantite, unite, recettes}}
        agregat: dict[str, dict[str, Any]] = defaultdict(lambda: {
            "quantite": 0.0,
            "unite": "",
            "recettes": set()
        })
        
        recettes_traitees: set[str] = set()
        
        for repas in planning.repas:
            if not repas.recette:
                continue
            
            recette = repas.recette
            recettes_traitees.add(recette.nom)
            
            # Parcourir les ingrédients de la recette (relation "ingredients")
            for ing_recette in recette.ingredients:
                if not ing_recette.ingredient:
                    continue
                
                nom = ing_recette.ingredient.nom.lower()
                agregat[nom]["quantite"] += float(ing_recette.quantite or 1)
                agregat[nom]["unite"] = ing_recette.unite or ""
                agregat[nom]["recettes"].add(recette.nom)
        
        # Construire la liste d'articles
        articles: list[ArticleCourse] = []
        for nom, data in agregat.items():
            rayon = self._determiner_rayon(nom)
            recettes_set: set[str] = data["recettes"]
            articles.append(ArticleCourse(
                nom=nom.capitalize(),
                quantite=float(data["quantite"]),
                unite=str(data["unite"]),
                rayon=rayon,
                recettes_source=list(recettes_set),
                priorite=self._determiner_priorite(rayon)
            ))
        
        return articles
    
    def comparer_avec_stock(
        self, 
        articles: list[ArticleCourse], 
        stock: dict[str, float]
    ) -> list[ArticleCourse]:
        """Compare les besoins avec le stock et calcule ce qu'il faut acheter."""
        articles_ajustes: list[ArticleCourse] = []
        
        for article in articles:
            nom_lower = article.nom.lower()
            en_stock = stock.get(nom_lower, 0.0)
            
            article.en_stock = en_stock
            article.a_acheter = max(0.0, article.quantite - en_stock)
            
            # Ne garder que les articles à acheter
            if article.a_acheter > 0:
                articles_ajustes.append(article)
        
        return articles_ajustes
    
    def generer_liste_courses(self) -> ListeCoursesIntelligente:
        """
        Génère une liste de courses complète depuis le planning actif.
        
        Returns:
            ListeCoursesIntelligente avec les articles optimisés
        """
        alertes: list[str] = []
        
        # 1. Récupérer planning actif
        planning = self.obtenir_planning_actif()
        if not planning:
            return ListeCoursesIntelligente(
                alertes=["Aucun planning actif trouvé. Créez d'abord un planning de repas."]
            )
        
        # 2. Extraire les ingrédients
        articles = self.extraire_ingredients_planning(planning)
        if not articles:
            return ListeCoursesIntelligente(
                alertes=["Aucune recette avec ingrédients dans le planning."]
            )
        
        # 3. Comparer avec stock
        stock = self.obtenir_stock_actuel()
        articles_a_acheter = self.comparer_avec_stock(articles, stock)
        
        # 4. Trier par rayon puis priorité
        articles_a_acheter.sort(key=lambda a: (a.rayon, a.priorite, a.nom))
        
        # 5. Récupérer les recettes couvertes
        recettes_couvertes: set[str] = set()
        for article in articles:
            recettes_couvertes.update(article.recettes_source)
        
        # 6. Générer alertes
        if len(articles_a_acheter) == 0:
            alertes.append("✅ Tous les ingrédients sont en stock!")
        elif len(stock) == 0:
            alertes.append("⚠️ Inventaire vide - liste complète générée")
        
        return ListeCoursesIntelligente(
            articles=articles_a_acheter,
            total_articles=len(articles_a_acheter),
            recettes_couvertes=list(recettes_couvertes),
            alertes=alertes
        )
    
    @avec_gestion_erreurs(default_return=[])
    @avec_session_db
    def ajouter_a_liste_courses(
        self, 
        articles: list[ArticleCourse],
        db: Session | None = None
    ) -> list[int]:
        """
        Ajoute les articles générés à la liste de courses.
        
        Utilise le système de liste ArticleCourses qui référence les ingrédients.
        Si l'ingrédient n'existe pas, il est créé.
        
        Args:
            articles: Articles à ajouter
            db: Session DB
            
        Returns:
            Liste des IDs créés
        """
        ids_crees: list[int] = []
        
        for article in articles:
            # Chercher ou créer l'ingrédient
            ingredient = db.query(Ingredient).filter(
                Ingredient.nom.ilike(f"%{article.nom}%")
            ).first()
            
            if not ingredient:
                # Créer l'ingrédient
                ingredient = Ingredient(
                    nom=article.nom,
                    categorie=article.rayon,
                    unite=article.unite or "pcs"
                )
                db.add(ingredient)
                db.flush()
            
            # Vérifier si déjà dans la liste de courses
            existant = db.query(ArticleCourses).filter(
                ArticleCourses.ingredient_id == ingredient.id,
                ArticleCourses.achete == False
            ).first()
            
            if existant:
                # Mettre à jour quantité
                existant.quantite_necessaire = (existant.quantite_necessaire or 0) + article.a_acheter
                existant.notes = f"{existant.notes or ''} + planning".strip()
                ids_crees.append(existant.id)
            else:
                # Créer nouvel article courses
                item = ArticleCourses(
                    ingredient_id=ingredient.id,
                    quantite_necessaire=article.a_acheter,
                    priorite={1: "haute", 2: "moyenne", 3: "basse"}.get(article.priorite, "moyenne"),
                    rayon_magasin=article.rayon,
                    notes=f"Depuis planning: {', '.join(article.recettes_source[:2])}",
                    achete=False,
                    suggere_par_ia=True
                )
                db.add(item)
                db.flush()
                ids_crees.append(item.id)
        
        db.commit()
        logger.info(f"✅ {len(ids_crees)} articles ajoutés à la liste de courses")
        return ids_crees
    
    async def suggerer_substitutions(
        self, 
        articles: list[ArticleCourse]
    ) -> list[SuggestionSubstitution]:
        """
        Suggère des substitutions économiques ou de saison.
        
        Args:
            articles: Liste d'articles
            
        Returns:
            Suggestions de substitutions
        """
        # Filtrer articles coûteux ou hors saison
        articles_a_evaluer = [a for a in articles if a.priorite <= 2][:5]
        
        if not articles_a_evaluer:
            return []
        
        noms = ", ".join([a.nom for a in articles_a_evaluer])
        
        prompt = f"""Pour ces ingrédients de liste de courses: {noms}

Suggère des substitutions économiques ou de saison (max 3).
Format JSON:
[
    {{"ingredient_original": "...", "suggestion": "...", "raison": "..."}}
]

Critères:
- Moins cher en ce moment
- De saison (nous sommes en {date.today().strftime('%B')})
- Équivalent nutritionnel

Réponds UNIQUEMENT avec le JSON."""

        try:
            response = await self.client.appeler(prompt)
            import json
            data = json.loads(response.strip().replace("```json", "").replace("```", ""))
            return [SuggestionSubstitution(**item) for item in data]
        except Exception as e:
            logger.error(f"Erreur suggestions: {e}")
            return []


# ═══════════════════════════════════════════════════════════
# FACTORY FUNCTION
# ═══════════════════════════════════════════════════════════

def get_courses_intelligentes_service() -> CoursesIntelligentesService:
    """Factory pour le service courses intelligentes."""
    return CoursesIntelligentesService()

