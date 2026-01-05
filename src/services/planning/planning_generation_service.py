"""
Service Génération Planning IA

Service IA pour générer des plannings hebdomadaires optimisés avec :
1. Variété (pas 2x même recette)
2. Équilibre nutritionnel (viandes/poissons/végétarien)
3. Batch cooking (1-2 repas batch par semaine)
4. Temps limité en semaine (< 45min le soir)
5. Adaptations bébé automatiques
6. Utilisation inventaire disponible
"""
import logging
from typing import Dict, List, Optional
from datetime import date, timedelta
from pydantic import BaseModel, Field, validator

from src.core.ai import AIClient, get_ai_client
from src.services.base_ai_service import BaseAIService, PlanningAIMixin
from src.core.errors import handle_errors

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# MODÈLES PYDANTIC
# ═══════════════════════════════════════════════════════════

class RepasPlanning(BaseModel):
    """Un repas dans le planning."""
    type: str = Field(..., pattern="^(petit_déjeuner|déjeuner|dîner|goûter)$")
    recette_nom: str = Field(..., min_length=3)
    recette_id: Optional[int] = None  # Sera résolu après
    portions: int = Field(4, ge=1, le=20)
    temps_total: int = Field(..., ge=5, le=300)
    est_adapte_bebe: bool = False
    est_batch: bool = False
    notes: Optional[str] = None


class JourPlanning(BaseModel):
    """Un jour du planning."""
    jour: int = Field(..., ge=0, le=6)  # 0=Lundi, 6=Dimanche
    repas: List[RepasPlanning] = Field(..., min_length=1)

    @validator("repas")
    def validate_repas(cls, v):
        """Valide qu'il n'y a pas 2 repas du même type."""
        types = [r.type for r in v]
        if len(types) != len(set(types)):
            raise ValueError("Pas de doublons de type repas dans un jour")
        return v


class PlanningSemaine(BaseModel):
    """Planning hebdomadaire complet."""
    semaine_debut: Optional[date] = None
    jours: List[JourPlanning] = Field(..., min_length=7, max_length=7)
    resume: Optional[Dict] = None

    @validator("jours")
    def validate_jours(cls, v):
        """Valide que les 7 jours sont présents."""
        if len(v) != 7:
            raise ValueError("Planning doit contenir exactement 7 jours")

        # Vérifier que les jours sont uniques et dans l'ordre
        jours_indices = [j.jour for j in v]
        if sorted(jours_indices) != list(range(7)):
            raise ValueError("Jours doivent être 0-6 sans doublon")

        return v


# ═══════════════════════════════════════════════════════════
# SERVICE GÉNÉRATION PLANNING
# ═══════════════════════════════════════════════════════════

class PlanningGenerationService(BaseAIService, PlanningAIMixin):
    """
    Service IA pour génération de plannings hebdomadaires optimisés.

    Utilise des contraintes intelligentes pour équilibrer :
    - Nutrition (viandes/poissons/végétarien)
    - Temps (rapide en semaine, élaboré week-end)
    - Variété (rotation ingrédients)
    - Praticité (batch cooking, restes)
    """

    def __init__(self, client: AIClient = None):
        """Initialise le service IA planning."""
        super().__init__(
            client=client or get_ai_client(),
            cache_prefix="planning_ai",
            default_ttl=1800,  # 30min
            default_temperature=0.8  # Créatif mais structuré
        )

    # ═══════════════════════════════════════════════════════════
    # GÉNÉRATION PLANNING COMPLET
    # ═══════════════════════════════════════════════════════════

    @handle_errors(show_in_ui=True, fallback_value=None)
    async def generer_planning_semaine(
            self,
            config: Dict,
            semaine_debut: date,
            contraintes: Optional[List[str]] = None,
            inventaire: Optional[List[Dict]] = None
    ) -> Optional[PlanningSemaine]:
        """
        Génère un planning hebdomadaire optimisé.

        Args:
            config: Configuration foyer
                {
                    "nb_adultes": 2,
                    "nb_enfants": 1,
                    "a_bebe": False,
                    "batch_cooking_actif": True,
                    "preferences": ["pas de poisson le lundi"]
                }
            semaine_debut: Date de début (lundi)
            contraintes: Contraintes supplémentaires
            inventaire: Inventaire disponible (utiliser en priorité)

        Returns:
            Planning complet ou None si erreur

        Example:
            >>> planning = await service.generer_planning_semaine(
            ...     config={"nb_adultes": 2, "nb_enfants": 1, "batch_cooking_actif": True},
            ...     semaine_debut=date(2025, 1, 6)
            ... )
            >>> print(f"Planning de {len(planning.jours)} jours généré")
        """
        logger.info(f"🗓️ Génération planning semaine du {semaine_debut.strftime('%d/%m/%Y')}")

        # Construire contexte avec mixin
        context = self.build_planning_context(config, semaine_debut.strftime("%d/%m/%Y"))

        # Ajouter inventaire si disponible
        if inventaire:
            context += self._add_inventaire_context(inventaire)

        # Contraintes automatiques + manuelles
        all_contraintes = self._build_contraintes(config, contraintes)

        # Prompt structuré
        prompt = self.build_json_prompt(
            context=context,
            task="Génère un planning hebdomadaire équilibré et réaliste",
            json_schema=self._get_schema_planning(),
            constraints=all_contraintes
        )

        try:
            planning = await self.call_with_parsing(
                prompt=prompt,
                response_model=PlanningSemaine,
                temperature=0.8,
                max_tokens=3500,
                use_cache=True
            )

            # Post-traitement
            planning.semaine_debut = semaine_debut
            planning = self._post_process_planning(planning, config)

            logger.info(
                f"✅ Planning généré: "
                f"{sum(len(j.repas) for j in planning.jours)} repas"
            )

            return planning

        except Exception as e:
            logger.error(f"Erreur génération planning: {e}")
            return self._get_fallback_planning(semaine_debut, config)

    # ═══════════════════════════════════════════════════════════
    # OPTIMISATION PLANNING
    # ═══════════════════════════════════════════════════════════

    @handle_errors(show_in_ui=True, fallback_value=None)
    async def optimiser_planning_existant(
            self,
            planning_actuel: Dict,
            axes_optimisation: List[str]
    ) -> Optional[PlanningSemaine]:
        """
        Optimise un planning existant selon axes donnés.

        Args:
            planning_actuel: Planning à optimiser
            axes_optimisation: ["temps", "equilibre", "variete", "budget"]

        Returns:
            Planning optimisé
        """
        logger.info(f"⚡ Optimisation planning selon {axes_optimisation}")

        # Analyser planning actuel
        analyse = self._analyser_planning(planning_actuel)

        context = f"""PLANNING ACTUEL:
{self._format_planning_actuel(planning_actuel)}

ANALYSE:
{analyse}

AXES D'OPTIMISATION:
{', '.join(axes_optimisation)}

Tâche: Propose un planning optimisé selon ces axes."""

        prompt = self.build_json_prompt(
            context=context,
            task="Optimise le planning existant",
            json_schema=self._get_schema_planning(),
            constraints=[
                "Garder structure générale si satisfaisante",
                "Optimiser selon axes demandés",
                "Proposer alternatives concrètes"
            ]
        )

        try:
            planning_optimise = await self.call_with_parsing(
                prompt=prompt,
                response_model=PlanningSemaine,
                temperature=0.7,
                max_tokens=3000,
                use_cache=False  # Pas de cache pour optimisation
            )

            logger.info("✅ Planning optimisé")
            return planning_optimise

        except Exception as e:
            logger.error(f"Erreur optimisation: {e}")
            return None

    # ═══════════════════════════════════════════════════════════
    # SUGGESTIONS REPAS UNIQUE
    # ═══════════════════════════════════════════════════════════

    @handle_errors(show_in_ui=True, fallback_value=[])
    async def suggerer_repas(
            self,
            type_repas: str,
            jour_semaine: int,
            config: Dict,
            nb_suggestions: int = 3
    ) -> List[RepasPlanning]:
        """
        Suggère des repas pour un créneau spécifique.

        Args:
            type_repas: "déjeuner" / "dîner" / etc.
            jour_semaine: 0-6 (lundi-dimanche)
            config: Config foyer
            nb_suggestions: Nombre de suggestions

        Returns:
            Liste de suggestions de repas
        """
        logger.info(f"💡 Suggestions repas: {type_repas} jour {jour_semaine}")

        jours = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
        jour_nom = jours[jour_semaine]

        # Contraintes selon jour et type
        contraintes = []

        # Semaine = rapide
        if jour_semaine < 5:  # Lun-Ven
            contraintes.append("Temps max 45min (jour de semaine)")

        # Dîner = plus léger
        if type_repas == "dîner":
            contraintes.append("Repas léger et digeste")

        context = f"""CONTEXTE:
- Jour: {jour_nom}
- Type repas: {type_repas}
- Foyer: {config.get('nb_adultes', 2)} adultes, {config.get('nb_enfants', 0)} enfants
- Bébé: {"Oui" if config.get('a_bebe') else "Non"}

Tâche: Suggère {nb_suggestions} recettes adaptées."""

        prompt = self.build_json_prompt(
            context=context,
            task=f"Suggère {nb_suggestions} repas variés",
            json_schema=self._get_schema_repas(),
            constraints=contraintes
        )

        try:
            suggestions = await self.call_with_list_parsing(
                prompt=prompt,
                item_model=RepasPlanning,
                list_key="repas",
                temperature=0.8,
                max_tokens=1500,
                use_cache=True,
                max_items=nb_suggestions
            )

            logger.info(f"✅ {len(suggestions)} suggestions générées")
            return suggestions

        except Exception as e:
            logger.error(f"Erreur suggestions repas: {e}")
            return []

    # ═══════════════════════════════════════════════════════════
    # HELPERS PRIVÉS
    # ═══════════════════════════════════════════════════════════

    def _build_contraintes(
            self,
            config: Dict,
            contraintes_user: Optional[List[str]]
    ) -> List[str]:
        """Construit liste complète de contraintes."""
        contraintes = []

        # 1. Variété
        contraintes.append("Variété: pas 2 fois la même recette dans la semaine")
        contraintes.append("Rotation protéines: viande/poisson/végétarien")

        # 2. Temps
        contraintes.append("Soirs de semaine (L-V): max 45min de préparation")
        contraintes.append("Week-end: peut être plus élaboré (max 2h)")

        # 3. Équilibre
        contraintes.append("Équilibre hebdo: 3-4 viandes, 2 poissons, 1-2 végétariens")
        contraintes.append("Alterner féculents/légumes en accompagnement")

        # 4. Batch cooking
        if config.get("batch_cooking_actif"):
            contraintes.append("1-2 repas batch cooking (préparer en avance, portions x2)")

        # 5. Bébé
        if config.get("a_bebe"):
            contraintes.append("Indiquer si recette adaptable bébé (texture/ingrédients)")

        # 6. Préférences utilisateur
        if config.get("preferences"):
            for pref in config["preferences"]:
                contraintes.append(f"Préférence: {pref}")

        # 7. Contraintes custom
        if contraintes_user:
            contraintes.extend(contraintes_user)

        return contraintes

    def _add_inventaire_context(self, inventaire: List[Dict]) -> str:
        """Ajoute contexte inventaire."""
        context = "\n\n📦 INVENTAIRE DISPONIBLE:\n"
        context += "Privilégier ces ingrédients en priorité:\n"

        # Filtrer articles avec bon stock
        articles_dispo = [
            a for a in inventaire
            if a.get("statut") == "ok" and a.get("quantite", 0) > 0
        ][:15]

        for art in articles_dispo:
            context += f"- {art['nom']}: {art['quantite']} {art['unite']}\n"

        return context

    def _post_process_planning(
            self,
            planning: PlanningSemaine,
            config: Dict
    ) -> PlanningSemaine:
        """Post-traitement du planning."""
        # Calculer résumé
        total_repas = sum(len(j.repas) for j in planning.jours)
        batch_repas = sum(1 for j in planning.jours for r in j.repas if r.est_batch)
        bebe_repas = sum(1 for j in planning.jours for r in j.repas if r.est_adapte_bebe)

        planning.resume = {
            "total_repas": total_repas,
            "batch_cooking": batch_repas,
            "adaptes_bebe": bebe_repas,
            "temps_total_estime": sum(
                r.temps_total for j in planning.jours for r in j.repas
            )
        }

        return planning

    def _analyser_planning(self, planning: Dict) -> str:
        """Analyse un planning existant."""
        analyses = []

        total_repas = sum(len(j.get("repas", [])) for j in planning.get("jours", []))
        analyses.append(f"Total: {total_repas} repas")

        # Analyser variété (à améliorer avec vraies données)
        analyses.append("Variété: à analyser")

        return "\n".join(analyses)

    def _format_planning_actuel(self, planning: Dict) -> str:
        """Formate planning pour prompt."""
        lines = []

        for jour in planning.get("jours", []):
            lines.append(f"\n{jour.get('nom_jour')}:")
            for repas in jour.get("repas", []):
                recette_nom = repas.get("recette", {}).get("nom", "?")
                lines.append(f"  - {repas.get('type')}: {recette_nom}")

        return "\n".join(lines)

    def _get_schema_planning(self) -> str:
        """Schéma JSON planning complet."""
        return """
{
  "jours": [
    {
      "jour": 0,
      "repas": [
        {
          "type": "déjeuner",
          "recette_nom": "Pâtes carbonara",
          "portions": 4,
          "temps_total": 30,
          "est_adapte_bebe": false,
          "est_batch": false,
          "notes": "Recette familiale classique"
        }
      ]
    }
  ]
}
"""

    def _get_schema_repas(self) -> str:
        """Schéma JSON liste repas."""
        return """
{
  "repas": [
    {
      "type": "déjeuner",
      "recette_nom": "Nom recette",
      "portions": 4,
      "temps_total": 30,
      "est_adapte_bebe": false
    }
  ]
}
"""

    def _get_fallback_planning(
            self,
            semaine_debut: date,
            config: Dict
    ) -> PlanningSemaine:
        """Planning de secours basique."""
        jours = []

        for jour_idx in range(7):
            # Repas simple par jour
            repas = [
                RepasPlanning(
                    type="déjeuner" if jour_idx < 5 else "dîner",
                    recette_nom=f"Repas simple jour {jour_idx+1}",
                    portions=config.get("nb_adultes", 2) + config.get("nb_enfants", 0),
                    temps_total=30,
                    est_adapte_bebe=config.get("a_bebe", False)
                )
            ]

            jours.append(JourPlanning(jour=jour_idx, repas=repas))

        return PlanningSemaine(
            semaine_debut=semaine_debut,
            jours=jours,
            resume={
                "total_repas": len(jours),
                "note": "Planning de secours - Génération IA échouée"
            }
        )


# ═══════════════════════════════════════════════════════════
# FACTORY
# ═══════════════════════════════════════════════════════════

def create_planning_generation_service(client: AIClient = None) -> PlanningGenerationService:
    """
    Factory pour créer service génération planning.

    Args:
        client: Client IA optionnel

    Returns:
        Instance PlanningGenerationService
    """
    return PlanningGenerationService(client or get_ai_client())