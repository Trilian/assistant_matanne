"""
Service Recettes Unifié (REFACTORING v2.1)

Service complet pour les recettes fusionnant :
- recette_service.py (CRUD + recherche)
- recette_ai_service.py (Génération IA)
- recette_io_service.py (Import/Export)
- recette_version_service.py (Versions bébé/batch)
- recette_scraper_service.py (Web scraping)

Architecture simplifiée : Tout en 1 seul fichier, 0 duplication.
"""
import logging
from typing import Dict, List, Optional, Tuple
from sqlalchemy.orm import joinedload, Session
from pydantic import BaseModel, Field
import csv
import json
from io import StringIO

from src.core.database import obtenir_contexte_db
from src.core.cache import Cache
from src.core.errors import gerer_erreurs
from src.core.models import (
    Recette,
    RecetteIngredient,
    EtapeRecette,
    VersionRecette,
    Ingredient,
)
from src.core.ai import obtenir_client_ia
from src.services.base_service import BaseService

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# SCHÉMAS PYDANTIC (Validation IA)
# ═══════════════════════════════════════════════════════════

class RecetteSuggestion(BaseModel):
    """Recette suggérée par l'IA"""
    nom: str = Field(..., min_length=3, max_length=200)
    description: str = Field(..., min_length=10)
    temps_preparation: int = Field(..., gt=0, le=300)
    temps_cuisson: int = Field(..., ge=0, le=300)
    portions: int = Field(4, gt=0, le=20)
    difficulte: str = Field("moyen", pattern="^(facile|moyen|difficile)$")
    type_repas: str
    saison: str = "toute_année"
    ingredients: List[Dict]
    etapes: List[Dict]


class VersionBebeGeneree(BaseModel):
    """Version bébé générée"""
    instructions_modifiees: str
    notes_bebe: str
    age_minimum_mois: int = Field(6, ge=6, le=36)


class VersionBatchGeneree(BaseModel):
    """Version batch cooking générée"""
    etapes_paralleles: List[str]
    temps_optimise: int
    conseils_batch: str
    portions_recommandees: int = Field(8, ge=4, le=20)


# ═══════════════════════════════════════════════════════════
# SERVICE RECETTES UNIFIÉ
# ═══════════════════════════════════════════════════════════

class RecetteService(BaseService[Recette]):
    """
    Service complet pour les recettes.

    Fonctionnalités :
    - CRUD optimisé avec cache
    - Génération IA (recettes, versions bébé/batch)
    - Import/Export (CSV, JSON)
    - Web scraping
    - Recherche avancée
    - Statistiques
    """

    def __init__(self):
        super().__init__(Recette, cache_ttl=3600)
        self.ai_client = None  # Lazy loading

    # ═══════════════════════════════════════════════════════════
    # SECTION 1 : CRUD OPTIMISÉ
    # ═══════════════════════════════════════════════════════════

    @gerer_erreurs(afficher_dans_ui=False, valeur_fallback=None)
    def get_by_id_full(self, recette_id: int) -> Optional[Recette]:
        """
        Récupère une recette avec toutes ses relations (optimisé).

        Args:
            recette_id: ID de la recette

        Returns:
            Recette complète avec ingrédients et étapes
        """
        cache_key = f"recette_full_{recette_id}"
        cached = Cache.obtenir(cache_key, ttl=self.cache_ttl)
        if cached:
            return cached

        with obtenir_contexte_db() as db:
            recette = (
                db.query(Recette)
                .options(
                    joinedload(Recette.ingredients).joinedload(RecetteIngredient.ingredient),
                    joinedload(Recette.etapes),
                    joinedload(Recette.versions)
                )
                .filter(Recette.id == recette_id)
                .first()
            )

            if recette:
                Cache.definir(
                    cache_key, recette, ttl=self.cache_ttl,
                    dependencies=[f"recette_{recette_id}", "recettes"]
                )
            return recette

    @gerer_erreurs(afficher_dans_ui=True)
    def create_complete(self, data: Dict) -> Recette:
        """
        Crée une recette complète (recette + ingrédients + étapes).

        Args:
            data: {
                "nom": str,
                "description": str,
                ...
                "ingredients": [{"nom": str, "quantite": float, "unite": str}, ...],
                "etapes": [{"ordre": int, "description": str}, ...]
            }

        Returns:
            Recette créée avec toutes ses relations
        """
        with obtenir_contexte_db() as db:
            # Extraire relations
            ingredients_data = data.pop("ingredients", [])
            etapes_data = data.pop("etapes", [])

            # Créer recette
            recette = Recette(**data)
            db.add(recette)
            db.flush()  # Pour obtenir l'ID

            # Créer ingrédients
            for ing_data in ingredients_data:
                ingredient = self._find_or_create_ingredient(db, ing_data["nom"])
                recette_ing = RecetteIngredient(
                    recette_id=recette.id,
                    ingredient_id=ingredient.id,
                    quantite=ing_data.get("quantite", 1.0),
                    unite=ing_data.get("unite", "pcs"),
                    optionnel=ing_data.get("optionnel", False)
                )
                db.add(recette_ing)

            # Créer étapes
            for etape_data in etapes_data:
                etape = EtapeRecette(
                    recette_id=recette.id,
                    ordre=etape_data["ordre"],
                    description=etape_data["description"],
                    duree=etape_data.get("duree")
                )
                db.add(etape)

            db.commit()
            db.refresh(recette)

            # Invalider cache
            Cache.invalider(pattern="recettes")

            logger.info(f"✅ Recette créée : {recette.nom} (ID: {recette.id})")
            return recette

    @gerer_erreurs(afficher_dans_ui=False, valeur_fallback=[])
    def search_advanced(
            self,
            term: Optional[str] = None,
            type_repas: Optional[str] = None,
            saison: Optional[str] = None,
            difficulte: Optional[str] = None,
            temps_max: Optional[int] = None,
            compatible_bebe: Optional[bool] = None,
            limit: int = 100
    ) -> List[Recette]:
        """
        Recherche avancée multi-critères.

        Args:
            term: Terme de recherche (nom, description)
            type_repas: Type de repas
            saison: Saison
            difficulte: Difficulté
            temps_max: Temps total maximum (minutes)
            compatible_bebe: Compatible bébé
            limit: Limite résultats

        Returns:
            Liste de recettes filtrées
        """
        filters = {}
        if type_repas:
            filters["type_repas"] = type_repas
        if saison:
            filters["saison"] = saison
        if difficulte:
            filters["difficulte"] = difficulte
        if compatible_bebe is not None:
            filters["compatible_bebe"] = compatible_bebe

        search_fields = ["nom", "description"] if term else None

        return self.advanced_search(
            search_term=term,
            search_fields=search_fields,
            filters=filters,
            sort_by="nom",
            limit=limit
        )

    # ═══════════════════════════════════════════════════════════
    # SECTION 2 : GÉNÉRATION IA
    # ═══════════════════════════════════════════════════════════

    def _ensure_ai_client(self):
        """Initialise le client IA si nécessaire (lazy loading)"""
        if self.ai_client is None:
            self.ai_client = obtenir_client_ia()

    @gerer_erreurs(afficher_dans_ui=True, valeur_fallback=[])
    def generer_recettes_ia(
            self,
            type_repas: str,
            saison: str,
            difficulte: str = "moyen",
            ingredients_dispo: Optional[List[str]] = None,
            nb_recettes: int = 3
    ) -> List[Dict]:
        """
        Génère des recettes avec l'IA.

        Args:
            type_repas: Type de repas souhaité
            saison: Saison
            difficulte: Difficulté
            ingredients_dispo: Ingrédients disponibles (optionnel)
            nb_recettes: Nombre de recettes à générer

        Returns:
            Liste de recettes générées
        """
        self._ensure_ai_client()

        # Vérifier rate limit
        from src.core.cache import LimiteDebit
        autorise, msg = LimiteDebit.peut_appeler()
        if not autorise:
            logger.warning(msg)
            return []

        # Construire prompt
        prompt = self._build_recipe_prompt(
            type_repas, saison, difficulte, ingredients_dispo, nb_recettes
        )

        # Vérifier cache IA
        from src.core.ai.cache import CacheIA
        cached = CacheIA.obtenir(prompt=prompt)
        if cached:
            logger.info("✅ Recettes IA depuis cache")
            return self._parse_ai_response(cached)

        # Appeler IA (version synchrone pour compatibilité)
        try:
            import asyncio
            response = asyncio.run(self.ai_client.appeler(
                prompt=prompt,
                prompt_systeme="Tu es un chef cuisinier expert.",
                temperature=0.8,
                max_tokens=2000
            ))

            # Parser réponse
            recettes = self._parse_ai_response(response)

            # Cacher + enregistrer appel
            CacheIA.definir(prompt=prompt, reponse=response)
            LimiteDebit.enregistrer_appel()

            logger.info(f"✅ {len(recettes)} recettes générées par IA")
            return recettes

        except Exception as e:
            logger.error(f"❌ Erreur génération IA : {e}")
            return []

    @gerer_erreurs(afficher_dans_ui=True, valeur_fallback=None)
    def generer_version_bebe(self, recette_id: int) -> Optional[VersionRecette]:
        """
        Génère une version bébé d'une recette avec l'IA.

        Args:
            recette_id: ID de la recette

        Returns:
            VersionRecette créée ou None
        """
        self._ensure_ai_client()

        recette = self.get_by_id_full(recette_id)
        if not recette:
            return None

        # Vérifier si version existe déjà
        with obtenir_contexte_db() as db:
            existing = (
                db.query(VersionRecette)
                .filter(
                    VersionRecette.recette_base_id == recette_id,
                    VersionRecette.type_version == "bébé"
                )
                .first()
            )
            if existing:
                return existing

        # Vérifier rate limit
        from src.core.cache import LimiteDebit
        autorise, msg = LimiteDebit.peut_appeler()
        if not autorise:
            logger.warning(msg)
            return None

        # Prompt IA
        prompt = f"""Adapte cette recette pour un bébé de 12 mois :

Recette : {recette.nom}
Ingrédients : {', '.join([ri.ingredient.nom for ri in recette.ingredients])}
Étapes : {len(recette.etapes)} étapes

Génère une adaptation en JSON avec :
- instructions_modifiees (texte)
- notes_bebe (conseils)
- age_minimum_mois (6-36)"""

        try:
            import asyncio
            response = asyncio.run(self.ai_client.appeler(
                prompt=prompt,
                prompt_systeme="Tu es un pédiatre nutritionniste.",
                temperature=0.7
            ))

            # Parser et créer version
            data = self._parse_version_bebe(response)

            with obtenir_contexte_db() as db:
                version = VersionRecette(
                    recette_base_id=recette_id,
                    type_version="bébé",
                    instructions_modifiees=data["instructions_modifiees"],
                    notes_bebe=data["notes_bebe"]
                )
                db.add(version)
                db.commit()
                db.refresh(version)

            LimiteDebit.enregistrer_appel()
            logger.info(f"✅ Version bébé créée pour recette {recette_id}")
            return version

        except Exception as e:
            logger.error(f"❌ Erreur génération version bébé : {e}")
            return None

    # ═══════════════════════════════════════════════════════════
    # SECTION 3 : IMPORT/EXPORT
    # ═══════════════════════════════════════════════════════════

    def export_to_csv(self, recettes: List[Recette]) -> str:
        """
        Exporte des recettes en CSV.

        Args:
            recettes: Liste de recettes

        Returns:
            Contenu CSV
        """
        output = StringIO()
        writer = csv.DictWriter(
            output,
            fieldnames=["nom", "description", "temps_preparation", "temps_cuisson",
                        "portions", "difficulte", "type_repas", "saison"]
        )

        writer.writeheader()
        for r in recettes:
            writer.writerow({
                "nom": r.nom,
                "description": r.description or "",
                "temps_preparation": r.temps_preparation,
                "temps_cuisson": r.temps_cuisson,
                "portions": r.portions,
                "difficulte": r.difficulte,
                "type_repas": r.type_repas,
                "saison": r.saison
            })

        return output.getvalue()

    def export_to_json(self, recettes: List[Recette], indent: int = 2) -> str:
        """
        Exporte des recettes en JSON.

        Args:
            recettes: Liste de recettes
            indent: Indentation JSON

        Returns:
            Contenu JSON
        """
        data = []
        for r in recettes:
            data.append({
                "nom": r.nom,
                "description": r.description,
                "temps_preparation": r.temps_preparation,
                "temps_cuisson": r.temps_cuisson,
                "portions": r.portions,
                "difficulte": r.difficulte,
                "type_repas": r.type_repas,
                "saison": r.saison,
                "ingredients": [
                    {
                        "nom": ri.ingredient.nom,
                        "quantite": ri.quantite,
                        "unite": ri.unite
                    }
                    for ri in r.ingredients
                ],
                "etapes": [
                    {
                        "ordre": e.ordre,
                        "description": e.description
                    }
                    for e in r.etapes
                ]
            })

        return json.dumps(data, indent=indent, ensure_ascii=False)

    # ═══════════════════════════════════════════════════════════
    # HELPERS PRIVÉS
    # ═══════════════════════════════════════════════════════════

    def _find_or_create_ingredient(self, db: Session, nom: str) -> Ingredient:
        """Trouve ou crée un ingrédient"""
        ingredient = db.query(Ingredient).filter(Ingredient.nom == nom).first()
        if not ingredient:
            ingredient = Ingredient(nom=nom, unite="pcs")
            db.add(ingredient)
            db.flush()
        return ingredient

    def _build_recipe_prompt(
            self,
            type_repas: str,
            saison: str,
            difficulte: str,
            ingredients: Optional[List[str]],
            nb: int
    ) -> str:
        """Construit le prompt pour génération recettes"""
        base = f"""Génère {nb} recettes pour {type_repas} de saison {saison}, 
difficulté {difficulte}."""

        if ingredients:
            base += f"\nUtilise ces ingrédients : {', '.join(ingredients)}"

        base += "\n\nRéponds en JSON avec : nom, description, temps_preparation, temps_cuisson, portions, ingredients[], etapes[]"
        return base

    def _parse_ai_response(self, content: str) -> List[Dict]:
        """Parse la réponse IA en liste de recettes"""
        try:
            # Extraire JSON de la réponse
            start = content.find("[")
            end = content.rfind("]") + 1
            if start == -1 or end == 0:
                return []

            json_str = content[start:end]
            return json.loads(json_str)
        except Exception as e:
            logger.error(f"Erreur parsing IA : {e}")
            return []

    def _parse_version_bebe(self, content: str) -> Dict:
        """Parse la réponse IA version bébé"""
        try:
            start = content.find("{")
            end = content.rfind("}") + 1
            json_str = content[start:end]
            return json.loads(json_str)
        except:
            return {
                "instructions_modifiees": content,
                "notes_bebe": "Consultez un pédiatre"
            }


# ═══════════════════════════════════════════════════════════
# INSTANCE SINGLETON
# ═══════════════════════════════════════════════════════════

recette_service = RecetteService()


# ═══════════════════════════════════════════════════════════
# EXPORTS
# ═══════════════════════════════════════════════════════════

__all__ = [
    "RecetteService",
    "recette_service",
    "RecetteSuggestion",
    "VersionBebeGeneree",
    "VersionBatchGeneree",
]