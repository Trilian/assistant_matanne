"""
Mixins IA spécialisés par domaine métier

Ces mixins fournissent des méthodes de construction de contexte IA
spécifiques à chaque domaine (recettes, planning, inventaire).
Ils sont conçus pour être combinés avec BaseAIService via héritage multiple.

Exemples d'utilisation:
    class MonService(BaseAIService, RecipeAIMixin):
        pass
"""

from __future__ import annotations

import logging
from collections import defaultdict

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# MIXIN RECETTES
# ═══════════════════════════════════════════════════════════


class RecipeAIMixin:
    """Mixin pour fonctionnalités IA recettes"""

    def build_recipe_context(
        self, filters: dict, ingredients_dispo: list[str] | None = None, nb_recettes: int = 3
    ) -> str:
        """Construit contexte pour génération recettes"""
        context = f"Génère {nb_recettes} recettes avec les critères suivants:\n\n"

        if filters.get("saison"):
            context += f"- Saison: {filters['saison']}\n"
        if filters.get("type_repas"):
            context += f"- Type de repas: {filters['type_repas']}\n"
        if filters.get("difficulte"):
            context += f"- Difficulté max: {filters['difficulte']}\n"
        if filters.get("is_quick"):
            context += "- Temps max: 30 minutes\n"

        if ingredients_dispo:
            context += "\nINGRÉDIENTS DISPONIBLES:\n"
            for ing in ingredients_dispo[:10]:
                context += f"- {ing}\n"
            context += "\nPrivilégier ces ingrédients si possible.\n"

        return context


# ═══════════════════════════════════════════════════════════
# MIXIN PLANNING
# ═══════════════════════════════════════════════════════════


class PlanningAIMixin:
    """Mixin pour fonctionnalités IA planning"""

    def build_planning_context(self, config: dict, semaine_debut: str) -> str:
        """Construit contexte pour génération planning"""
        context = f"Génère un planning hebdomadaire pour la semaine du {semaine_debut}.\n\n"

        context += "CONFIGURATION FOYER:\n"
        context += f"- {config.get('nb_adultes', 2)} adultes\n"
        context += f"- {config.get('nb_enfants', 0)} enfants\n"

        if config.get("a_bebe"):
            context += "- Présence d'un jeune enfant (adapter certaines recettes pour texture/allergènes)\n"

        if config.get("batch_cooking_actif"):
            context += "- Batch cooking activé (optimiser temps)\n"

        return context


# ═══════════════════════════════════════════════════════════
# MIXIN INVENTAIRE
# ═══════════════════════════════════════════════════════════


class InventoryAIMixin:
    """Mixin pour fonctionnalités IA inventaire"""

    def build_inventory_summary(self, inventaire: list[dict]) -> str:
        """Construit résumé inventaire pour IA"""
        summary = f"INVENTAIRE ({len(inventaire)} articles):\n\n"

        # Grouper par catégorie
        categories = defaultdict(list)
        for article in inventaire:
            cat = article.get("categorie", "Autre")
            categories[cat].append(article)

        # Résumer par catégorie
        for cat, articles in categories.items():
            summary += f"{cat}:\n"
            for art in articles[:5]:  # Max 5 par catégorie
                statut = art.get("statut", "ok")
                icon = "🔴" if statut == "critique" else "⚠️" if statut == "sous_seuil" else "✅"
                summary += f"  {icon} {art['nom']}: {art['quantite']} {art['unite']}\n"

            if len(articles) > 5:
                summary += f"  ... et {len(articles) - 5} autres\n"
            summary += "\n"

        # Résumé statuts
        critiques = len([a for a in inventaire if a.get("statut") == "critique"])
        sous_seuil = len([a for a in inventaire if a.get("statut") == "sous_seuil"])

        summary += "STATUTS:\n"
        summary += f"- {critiques} articles critiques\n"
        summary += f"- {sous_seuil} articles sous le seuil\n"

        return summary
