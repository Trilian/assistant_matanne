"""
Service Planning Unifié (REFACTORING PHASE 2)

✅ Utilise @with_db_session et @with_cache (Phase 1)
✅ Validation Pydantic centralisée
✅ Type hints complets pour meilleur IDE support
✅ Services testables sans Streamlit
"""

import logging
from datetime import date, timedelta
from typing import Any

from pydantic import BaseModel, Field
from sqlalchemy.orm import Session, joinedload

from src.core.ai import obtenir_client_ia
from src.core.cache import Cache
from src.core.database import obtenir_contexte_db
from src.core.decorators import with_db_session, with_cache, with_error_handling
from src.core.errors_base import ErreurNonTrouve
from src.core.models import Planning, Repas
from src.services.base_ai_service import BaseAIService, PlanningAIMixin
from src.services.types import BaseService

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════
# SCHÉMAS PYDANTIC
# ═══════════════════════════════════════════════════════════

class JourPlanning(BaseModel):
    """Jour du planning généré par l'IA"""
    jour: str = Field(..., min_length=6, max_length=10)
    dejeuner: str = Field(..., min_length=3)
    diner: str = Field(..., min_length=3)


class SuggestionRecettesDay(BaseModel):
    """Suggestions de recettes pour un jour (3 options)"""
    jour_name: str  # Lundi, Mardi, etc.
    type_repas: str  # déjeuner, dîner
    suggestions: list[dict] = Field(..., min_items=1, max_items=3)  # [{nom, description, type_proteines}]


class ParametresEquilibre(BaseModel):
    """Paramètres pour l'équilibre de la semaine"""
    poisson_jours: list[str] = Field(default_factory=lambda: ["lundi", "jeudi"])  # Jours avec poisson
    viande_rouge_jours: list[str] = Field(default_factory=lambda: ["mardi"])  # Jours avec viande rouge
    vegetarien_jours: list[str] = Field(default_factory=lambda: ["mercredi"])  # Jours végé
    pates_riz_count: int = Field(default=3, ge=1, le=5)  # Combien de fois pâtes/riz
    ingredients_exclus: list[str] = Field(default_factory=list)  # Allergies, phobies
    preferences_extras: dict = Field(default_factory=dict)  # Autres contraintes


# ═══════════════════════════════════════════════════════════
# SERVICE PLANNING UNIFIÉ
# ═══════════════════════════════════════════════════════════


class PlanningService(BaseService[Planning], BaseAIService, PlanningAIMixin):
    """
    Service complet pour le planning hebdomadaire.

    ✅ Héritage multiple :
    - BaseService → CRUD optimisé
    - BaseAIService → IA avec rate limiting auto
    - PlanningAIMixin → Contextes métier planning

    Fonctionnalités:
    - CRUD optimisé avec cache
    - Génération IA planning hebdomadaire
    - Gestion repas par jour
    """

    def __init__(self):
        BaseService.__init__(self, Planning, cache_ttl=1800)
        BaseAIService.__init__(
            self,
            client=obtenir_client_ia(),
            cache_prefix="planning",
            default_ttl=1800,
            default_temperature=0.7,
            service_name="planning",
        )

    # ═══════════════════════════════════════════════════════════
    # SECTION 1: CRUD & PLANNING (REFACTORED)
    # ═══════════════════════════════════════════════════════════

    @with_cache(ttl=1800, key_func=lambda self, pid=None: f"planning_active")
    @with_error_handling(default_return=None)
    @with_db_session
    def get_planning(self, planning_id: int | None = None, db: Session | None = None) -> Planning | None:
        """Get the active or specified planning with eager loading of meals.

        Args:
            planning_id: Specific planning ID, or None to get active planning
            db: Database session (injected by @with_db_session)

        Returns:
            Planning object with repas eagerly loaded, or None if not found
        """
        if planning_id:
            planning = (
                db.query(Planning)
                .options(
                    joinedload(Planning.repas).joinedload(Repas.recette)
                )
                .filter(Planning.id == planning_id)
                .first()
            )
        else:
            planning = (
                db.query(Planning)
                .options(
                    joinedload(Planning.repas).joinedload(Repas.recette)
                )
                .filter(Planning.actif == True)
                .first()
            )
        
        if not planning:
            logger.debug(f"ℹ️ Planning not found")
            return None
        
        return planning

    @with_cache(ttl=1800, key_func=lambda self, pid: f"planning_full_{pid}")
    @with_error_handling(default_return=None)
    @with_db_session
    def get_planning_complet(self, planning_id: int, db: Session | None = None) -> dict[str, Any] | None:
        """Récupère un planning avec tous ses repas.

        Retrieves complete planning with all meals organized by day.
        Results are cached for 30 minutes.

        Args:
            planning_id: ID of the planning to retrieve
            db: Database session (injected by @with_db_session)

        Returns:
            Dict with planning data and meals organized by date, or None if not found
        """
        planning = (
            db.query(Planning)
            .options(
                joinedload(Planning.repas).joinedload(Repas.recette)
            )
            .filter(Planning.id == planning_id)
            .first()
        )

        if not planning:
            logger.warning(f"⚠️ Planning {planning_id} not found")
            return None

        repas_par_jour = {}
        for repas in planning.repas:
            jour_str = repas.date_repas.strftime("%Y-%m-%d")
            if jour_str not in repas_par_jour:
                repas_par_jour[jour_str] = []

            repas_par_jour[jour_str].append(
                {
                    "id": repas.id,
                    "type_repas": repas.type_repas,
                    "recette_id": repas.recette_id,
                    "recette_nom": repas.recette.nom if repas.recette else None,
                    "prepare": repas.prepare,
                    "notes": repas.notes,
                }
            )

        result = {
            "id": planning.id,
            "nom": planning.nom,
            "semaine_debut": planning.semaine_debut.isoformat(),
            "semaine_fin": planning.semaine_fin.isoformat(),
            "actif": planning.actif,
            "genere_par_ia": planning.genere_par_ia,
            "repas_par_jour": repas_par_jour,
        }

        logger.info(f"✅ Retrieved planning {planning_id} with {len(repas_par_jour)} days")
        return result

    # ═══════════════════════════════════════════════════════════
    # SECTION 2: SUGGESTIONS ÉQUILIBRÉES (NOUVEAU)
    # ═══════════════════════════════════════════════════════════

    @with_error_handling(default_return=[])
    @with_db_session
    def suggerer_recettes_equilibrees(
        self,
        semaine_debut: date,
        parametres: ParametresEquilibre,
        db: Session | None = None,
    ) -> list[dict]:
        """Suggère des recettes équilibrées pour chaque jour.
        
        Retourne 3 options par jour avec score d'équilibre.
        
        Args:
            semaine_debut: Date de début de semaine
            parametres: Contraintes d'équilibre
            db: Database session
            
        Returns:
            List de dicts {jour, type_repas, suggestions: [{nom, description, raison}]}
        """
        from src.core.models import Recette
        
        jours_semaine = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
        suggestions_globales = []
        
        for idx, jour_name in enumerate(jours_semaine):
            jour_lower = jour_name.lower()
            date_jour = semaine_debut + timedelta(days=idx)
            
            # Déterminer le type de protéine pour ce jour
            type_proteine = "autre"
            raison_jour = ""
            
            if jour_lower in parametres.poisson_jours:
                type_proteine = "poisson"
                raison_jour = "🐟 Jour poisson"
            elif jour_lower in parametres.viande_rouge_jours:
                type_proteine = "viande_rouge"
                raison_jour = "🥩 Jour viande rouge"
            elif jour_lower in parametres.vegetarien_jours:
                type_proteine = "vegetarien"
                raison_jour = "🥬 Jour végétarien"
            else:
                type_proteine = "volaille"
                raison_jour = "🍗 Jour volaille"
            
            # Requête base pour récupérer 3 recettes de ce type
            query = db.query(Recette).filter(Recette.est_equilibre == True)
            
            # Filtrer par type de protéine
            if type_proteine == "poisson":
                query = query.filter(Recette.type_proteines.ilike("%poisson%"))
            elif type_proteine == "viande_rouge":
                query = query.filter(Recette.type_proteines.ilike("%viande%"))
            elif type_proteine == "vegetarien":
                query = query.filter(Recette.est_vegetarien == True)
            
            # Exclure les ingrédients interdits
            for ingredient_exc in parametres.ingredients_exclus:
                # Filtre basique (devrait utiliser une vraie relation en prod)
                query = query.filter(~Recette.description.ilike(f"%{ingredient_exc}%"))
            
            # Récupérer 3 suggestions
            recettes = query.limit(3).all()
            
            suggestions_jour = []
            for recette in recettes:
                suggestions_jour.append({
                    "id": recette.id,
                    "nom": recette.nom,
                    "description": recette.description,
                    "temps_total": (recette.temps_preparation or 0) + (recette.temps_cuisson or 0),
                    "type_repas": "déjeuner" if idx % 2 == 0 else "dîner",
                    "raison": raison_jour,
                    "type_proteines": recette.type_proteines,
                })
            
            # Si pas assez, ajouter des recettes équilibrées quelconques
            if len(suggestions_jour) < 3:
                autres = db.query(Recette).filter(
                    Recette.id.notin_([s["id"] for s in suggestions_jour])
                ).limit(3 - len(suggestions_jour)).all()
                
                for recette in autres:
                    suggestions_jour.append({
                        "id": recette.id,
                        "nom": recette.nom,
                        "description": recette.description,
                        "temps_total": (recette.temps_preparation or 0) + (recette.temps_cuisson or 0),
                        "type_repas": "déjeuner" if idx % 2 == 0 else "dîner",
                        "raison": "📝 Alternative équilibrée",
                        "type_proteines": getattr(recette, 'type_proteines', 'mixte'),
                    })
            
            suggestions_globales.append({
                "jour": jour_name,
                "jour_index": idx,
                "date": date_jour.isoformat(),
                "raison_jour": raison_jour,
                "suggestions": suggestions_jour[:3],
            })
        
        logger.info(f"✅ Generated {len(suggestions_globales)} days of balanced suggestions")
        return suggestions_globales

    # ═══════════════════════════════════════════════════════════
    # SECTION 3: GÉNÉRATION AVEC CHOIX (NOUVEAU)
    # ═══════════════════════════════════════════════════════════

    @with_error_handling(default_return=None)
    @with_db_session
    def creer_planning_avec_choix(
        self,
        semaine_debut: date,
        recettes_selection: dict[str, int],  # {jour_index: recette_id}
        enfants_adaptes: list[int] | None = None,
        db: Session | None = None,
    ) -> Planning | None:
        """Crée un planning à partir des choix de l'utilisateur.
        
        Args:
            semaine_debut: Date de début
            recettes_selection: Mapping jour → recette_id choisi
            enfants_adaptes: IDs des enfants pour adapter (Jules, etc.)
            db: Database session
            
        Returns:
            Planning créé avec tous les repas
        """
        from src.core.models import Recette
        
        semaine_fin = semaine_debut + timedelta(days=6)
        
        planning = Planning(
            nom=f"Planning {semaine_debut.strftime('%d/%m')}",
            semaine_debut=semaine_debut,
            semaine_fin=semaine_fin,
            actif=True,
            genere_par_ia=False,
        )
        db.add(planning)
        db.flush()
        
        jours_semaine = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
        
        for idx, jour_name in enumerate(jours_semaine):
            date_jour = semaine_debut + timedelta(days=idx)
            jour_key = f"jour_{idx}"
            
            # Récupérer la recette sélectionnée
            recette_id = recettes_selection.get(jour_key)
            if not recette_id:
                logger.warning(f"⚠️ No recipe selected for {jour_name}")
                continue
            
            recette = db.query(Recette).filter(Recette.id == recette_id).first()
            if not recette:
                logger.warning(f"⚠️ Recipe {recette_id} not found for {jour_name}")
                continue
            
            # Créer repas (on crée juste le dîner pour simplifier en départ)
            repas = Repas(
                planning_id=planning.id,
                recette_id=recette.id,
                date_repas=date_jour,
                type_repas="dîner",
                notes=f"Repas du {jour_name}",
            )
            db.add(repas)
        
        db.commit()
        db.refresh(planning)
        
        logger.info(f"✅ Created custom planning for {semaine_debut}")
        return planning

    # ═══════════════════════════════════════════════════════════
    # SECTION 3: AGRÉGATION COURSES (NOUVEAU)
    # ═══════════════════════════════════════════════════════════

    @with_error_handling(default_return=[])
    @with_db_session
    def agréger_courses_pour_planning(
        self,
        planning_id: int,
        db: Session | None = None,
    ) -> list[dict]:
        """Agrège les ingrédients de toutes les recettes du planning.
        
        Retourne une liste d'ingrédients uniques avec quantités totales.
        
        Args:
            planning_id: ID du planning
            db: Database session
            
        Returns:
            List de dicts {ingredient, quantite, unite, rayon, priorite}
        """
        from src.core.models import (
            Planning, Repas, Recette, RecetteIngredient, Ingredient
        )
        
        # Récupérer le planning avec tous ses repas et recettes
        planning = (
            db.query(Planning)
            .filter(Planning.id == planning_id)
            .first()
        )
        
        if not planning or not planning.repas:
            logger.warning(f"⚠️ Planning {planning_id} pas trouvé ou pas de repas")
            return []
        
        # Agréger les ingrédients
        ingredients_aggregated = {}  # {nom: {quantite: 0, unite, rayon, priorite}}
        
        for repas in planning.repas:
            if not repas.recette_id:
                continue
            
            # Charger la recette avec ses ingrédients
            recette = (
                db.query(Recette)
                .filter(Recette.id == repas.recette_id)
                .first()
            )
            
            if not recette or not recette.ingredients:
                continue
            
            # Parcourir les ingrédients de cette recette
            for recette_ingredient in recette.ingredients:
                ingredient = recette_ingredient.ingredient
                if not ingredient:
                    continue
                
                nom = ingredient.nom
                quantite = recette_ingredient.quantite or 1
                unite = recette_ingredient.unite or ingredient.unite or "pcs"
                rayon = ingredient.categorie or "autre"
                
                # Agréger
                if nom not in ingredients_aggregated:
                    ingredients_aggregated[nom] = {
                        "nom": nom,
                        "quantite": quantite,
                        "unite": unite,
                        "rayon": rayon,
                        "priorite": "moyenne",  # Par défaut
                        "repas_count": 1,
                    }
                else:
                    # Augmenter la quantité (même unité supposée)
                    if ingredients_aggregated[nom]["unite"] == unite:
                        ingredients_aggregated[nom]["quantite"] += quantite
                    ingredients_aggregated[nom]["repas_count"] += 1
        
        # Trier par priorité (rayon) et quantité
        courses_list = sorted(
            ingredients_aggregated.values(),
            key=lambda x: (x["rayon"], -x["quantite"])
        )
        
        logger.info(f"✅ Agrégé {len(courses_list)} ingrédients pour planning {planning_id}")
        return courses_list

    # ═══════════════════════════════════════════════════════════
    # SECTION 4: GÉNÉRATION IA (REFACTORED)
    # ═══════════════════════════════════════════════════════════

    @with_cache(
        ttl=3600,
        key_func=lambda self, semaine_debut, preferences=None: f"planning_ia_{semaine_debut.isoformat()}",
    )
    @with_error_handling(default_return=None)
    @with_db_session
    def generer_planning_ia(
        self,
        semaine_debut: date,
        preferences: dict[str, Any] | None = None,
        db: Session | None = None,
    ) -> Planning | None:
        """Génère un planning hebdomadaire avec l'IA.

        Generates a complete weekly meal plan using Mistral AI.
        Includes breakfast/lunch/dinner organization.

        Args:
            semaine_debut: Start date of the week (Monday)
            preferences: Optional preferences dict for meal types, dietary restrictions, etc.
            db: Database session (injected by @with_db_session)

        Returns:
            Planning object with generated meals, or None if generation fails
        """
        # Utilisation du Mixin pour contexte planning
        context = self.build_planning_context(
            config=preferences or {},
            semaine_debut=semaine_debut.strftime("%d/%m/%Y"),
        )

        semaine_fin = semaine_debut + timedelta(days=6)

        # Construire prompt ultra-direct (comme pour recettes)
        prompt = f"""GENERATE A 7-DAY MEAL PLAN (MONDAY-SUNDAY) IN JSON FORMAT ONLY.

CONTEXT:
{context}

OUTPUT ONLY THIS JSON STRUCTURE (no other text, no markdown, no code blocks):
{{"items": [
  {{"jour": "Lundi", "dejeuner": "Pâtes carbonara", "diner": "Salade niçoise"}},
  {{"jour": "Mardi", "dejeuner": "Riz et poulet", "diner": "Soupe de légumes"}}
]}}

RULES:
1. Return ONLY valid JSON array with exactly 7 items (one per day)
2. jour values: Lundi, Mardi, Mercredi, Jeudi, Vendredi, Samedi, Dimanche
3. dejeuner and diner: recipe names or meal descriptions (3-50 chars)
4. Ensure variety throughout the week
5. Adapt to family preferences and dietary restrictions
6. No explanations, no text, ONLY JSON"""

        logger.info(f"🤖 Generating AI weekly plan starting {semaine_debut}")

        # Appel IA avec auto rate limiting & parsing
        planning_data = self.call_with_list_parsing_sync(
            prompt=prompt,
            item_model=JourPlanning,
            system_prompt="Return ONLY valid JSON. No text before or after JSON. Never use markdown code blocks.",
            max_items=7,
            temperature=0.5,
            max_tokens=2000,
        )

        # Log de debug pour voir la réponse
        if not planning_data:
            logger.warning(f"⚠️ Failed to generate planning for {semaine_debut} - no data returned")
            logger.debug(f"Checking if we can create default planning instead...")
            
            # Créer un planning par défaut avec des repas simples
            planning = Planning(
                nom=f"Planning {semaine_debut.strftime('%d/%m/%Y')}",
                semaine_debut=semaine_debut,
                semaine_fin=semaine_fin,
                actif=True,
                genere_par_ia=False,  # Non généré par IA car fallback
            )
            db.add(planning)
            db.flush()

            # Créer repas par défaut (simplement lundi à dimanche)
            jours_semaine = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
            for idx, jour_name in enumerate(jours_semaine):
                date_jour = semaine_debut + timedelta(days=idx)
                
                repas = Repas(
                    planning_id=planning.id,
                    date_repas=date_jour,
                    type_repas="dejeuner",
                    notes=f"Repas du {jour_name} - À remplir manuellement",
                )
                db.add(repas)
            
            db.commit()
            logger.info(f"✅ Created default planning for {semaine_debut} with 7 days")
            return planning
        
        # Planning IA réussi
        logger.info(f"✅ Generated planning with {len(planning_data)} days using AI")

        # Créer planning en DB
        planning = Planning(
            nom=f"Planning {semaine_debut.strftime('%d/%m/%Y')}",
            semaine_debut=semaine_debut,
            semaine_fin=semaine_fin,
            actif=True,
            genere_par_ia=True,
        )
        db.add(planning)
        db.flush()

        # Créer repas pour chaque jour
        for idx, jour_data in enumerate(planning_data):
            date_jour = semaine_debut + timedelta(days=idx)

            # Déjeuner
            repas_dej = Repas(
                planning_id=planning.id,
                date_repas=date_jour,
                type_repas="déjeuner",
                notes=jour_data.dejeuner,
            )
            db.add(repas_dej)

            # Dîner
            repas_din = Repas(
                planning_id=planning.id,
                date_repas=date_jour,
                type_repas="dîner",
                notes=jour_data.diner,
            )
            db.add(repas_din)

        db.commit()
        db.refresh(planning)

        # Invalider cache
        Cache.invalider(pattern="planning")

        logger.info(f"✅ Generated AI planning for week starting {semaine_debut}")
        return planning


# INSTANCE SINGLETON - LAZY LOADING
_planning_service = None

def get_planning_service() -> PlanningService:
    """Get or create the global PlanningService instance."""
    global _planning_service
    if _planning_service is None:
        _planning_service = PlanningService()
    return _planning_service

planning_service = None

__all__ = ["PlanningService", "planning_service", "get_planning_service"]
