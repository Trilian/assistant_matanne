"""
Modules combinatoires de recettes pour Batch Cooking.

Système de «recettes modulaires» où les bases (riz, pâtes, légumes rôtis)
sont combinées avec des protéines et sauces pour créer des repas variés
à partir d'un minimum de préparations.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from itertools import product as itertools_product

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# TYPES
# ═══════════════════════════════════════════════════════════


@dataclass
class ModuleRecette:
    """Un module combinable (base, protéine, sauce, topping)."""

    nom: str
    type_module: str  # base, proteine, sauce, legume, topping
    temps_prep_min: int = 0
    portions: int = 4
    tags: list[str] = field(default_factory=list)  # vegan, sans_gluten, rapide
    recette_id: int | None = None  # Lien vers recette existante


@dataclass
class CombiRecette:
    """Combinaison de modules formant un repas complet."""

    nom_genere: str
    base: ModuleRecette
    proteine: ModuleRecette | None = None
    sauce: ModuleRecette | None = None
    legume: ModuleRecette | None = None
    topping: ModuleRecette | None = None

    @property
    def modules(self) -> list[ModuleRecette]:
        return [m for m in [self.base, self.proteine, self.sauce, self.legume, self.topping] if m]

    @property
    def temps_total(self) -> int:
        return max(m.temps_prep_min for m in self.modules) if self.modules else 0

    @property
    def tags_cumules(self) -> set[str]:
        tags = set()
        for m in self.modules:
            tags.update(m.tags)
        return tags


@dataclass
class PlanCombinatoire:
    """Plan de batch cooking avec modules combinatoires."""

    modules_a_preparer: list[ModuleRecette]
    combinaisons_possibles: list[CombiRecette]
    nb_repas_generes: int = 0
    temps_prep_total: int = 0  # Temps de préparation des modules
    nb_repas_par_module: float = 0.0  # Ratio repas/modules


# ═══════════════════════════════════════════════════════════
# MODULES DE BASE PRÉDÉFINIS
# ═══════════════════════════════════════════════════════════

MODULES_DEFAUT: dict[str, list[ModuleRecette]] = {
    "base": [
        ModuleRecette("Riz basmati", "base", 15, 6, ["sans_gluten"]),
        ModuleRecette("Pâtes complètes", "base", 12, 6),
        ModuleRecette("Quinoa", "base", 15, 4, ["sans_gluten", "vegan"]),
        ModuleRecette("Semoule", "base", 5, 4),
        ModuleRecette("Pommes de terre rôties", "base", 35, 4, ["sans_gluten", "vegan"]),
        ModuleRecette("Boulgour", "base", 12, 4),
        ModuleRecette("Lentilles corail", "base", 20, 4, ["sans_gluten", "vegan"]),
        ModuleRecette("Polenta", "base", 20, 4, ["sans_gluten"]),
    ],
    "proteine": [
        ModuleRecette("Poulet grillé émincé", "proteine", 20, 4),
        ModuleRecette("Bœuf haché assaisonné", "proteine", 15, 4),
        ModuleRecette("Saumon mariné", "proteine", 15, 4, ["sans_gluten"]),
        ModuleRecette("Tofu mariné grillé", "proteine", 20, 4, ["vegan", "sans_gluten"]),
        ModuleRecette("Pois chiches rôtis", "proteine", 30, 4, ["vegan", "sans_gluten"]),
        ModuleRecette("Œufs durs", "proteine", 12, 6, ["sans_gluten"]),
        ModuleRecette("Crevettes sautées", "proteine", 10, 4, ["sans_gluten"]),
        ModuleRecette("Lardons/jambon", "proteine", 8, 4),
    ],
    "sauce": [
        ModuleRecette("Sauce tomate maison", "sauce", 25, 8, ["vegan", "sans_gluten"]),
        ModuleRecette("Pesto basilic", "sauce", 10, 6),
        ModuleRecette("Sauce curry coco", "sauce", 15, 6, ["vegan", "sans_gluten"]),
        ModuleRecette("Vinaigrette moutarde", "sauce", 5, 10, ["vegan", "sans_gluten"]),
        ModuleRecette("Sauce soja-gingembre", "sauce", 5, 8, ["vegan"]),
        ModuleRecette("Béchamel", "sauce", 15, 6),
        ModuleRecette("Sauce yaourt-herbes", "sauce", 5, 6, ["sans_gluten"]),
        ModuleRecette("Houmous", "sauce", 10, 6, ["vegan", "sans_gluten"]),
    ],
    "legume": [
        ModuleRecette(
            "Légumes rôtis (courgette, poivron, oignon)", "legume", 30, 6, ["vegan", "sans_gluten"]
        ),
        ModuleRecette("Carottes glacées", "legume", 20, 4, ["sans_gluten"]),
        ModuleRecette("Brocoli vapeur", "legume", 10, 4, ["vegan", "sans_gluten"]),
        ModuleRecette("Épinards sautés ail", "legume", 8, 4, ["vegan", "sans_gluten"]),
        ModuleRecette("Haricots verts persillés", "legume", 12, 4, ["vegan", "sans_gluten"]),
        ModuleRecette("Ratatouille", "legume", 40, 6, ["vegan", "sans_gluten"]),
        ModuleRecette("Salade composée", "legume", 10, 4, ["vegan", "sans_gluten"]),
    ],
    "topping": [
        ModuleRecette("Graines (sésame, courge, lin)", "topping", 2, 10, ["vegan", "sans_gluten"]),
        ModuleRecette("Feta émiettée", "topping", 2, 6, ["sans_gluten"]),
        ModuleRecette("Noix concassées", "topping", 2, 10, ["vegan", "sans_gluten"]),
        ModuleRecette("Parmesan râpé", "topping", 2, 6, ["sans_gluten"]),
        ModuleRecette("Herbes fraîches ciselées", "topping", 5, 8, ["vegan", "sans_gluten"]),
        ModuleRecette("Oignons frits croustillants", "topping", 10, 6, ["vegan"]),
    ],
}


# ═══════════════════════════════════════════════════════════
# FONCTIONS
# ═══════════════════════════════════════════════════════════


def generer_combinaisons(
    bases: list[ModuleRecette],
    proteines: list[ModuleRecette],
    sauces: list[ModuleRecette],
    legumes: list[ModuleRecette] | None = None,
    max_combis: int = 20,
    tags_requis: list[str] | None = None,
) -> list[CombiRecette]:
    """
    Génère des combinaisons possibles de modules.

    Args:
        bases: Modules de base préparés
        proteines: Modules protéines préparés
        sauces: Modules sauces préparés
        legumes: Modules légumes (optionnel)
        max_combis: Nombre max de combinaisons à retourner
        tags_requis: Filtrer par tags (vegan, sans_gluten, etc.)

    Returns:
        Liste de CombiRecette
    """
    if not legumes:
        legumes = [None]  # type: ignore[list-item]

    combinaisons = []
    for base, prot, sauce in itertools_product(bases, proteines, sauces):
        for legume in legumes:
            combi = CombiRecette(
                nom_genere=_generer_nom(base, prot, sauce),
                base=base,
                proteine=prot,
                sauce=sauce,
                legume=legume,
            )

            # Filtrage par tags
            if tags_requis:
                tags = combi.tags_cumules
                if not all(t in tags for t in tags_requis):
                    continue

            combinaisons.append(combi)

            if len(combinaisons) >= max_combis:
                return combinaisons

    return combinaisons


def _generer_nom(base: ModuleRecette, proteine: ModuleRecette, sauce: ModuleRecette) -> str:
    """Génère un nom descriptif pour une combinaison."""
    return f"{base.nom} + {proteine.nom}, {sauce.nom}"


def planifier_batch_modulaire(
    nb_repas_souhaites: int = 10,
    tags_requis: list[str] | None = None,
    modules_custom: dict[str, list[ModuleRecette]] | None = None,
) -> PlanCombinatoire:
    """
    Planifie un batch cooking modulaire.

    Choisit le minimum de modules à préparer pour générer
    le maximum de repas différents.

    Args:
        nb_repas_souhaites: Cible de repas variés
        tags_requis: Contraintes alimentaires
        modules_custom: Modules personnalisés (sinon défaut)

    Returns:
        PlanCombinatoire
    """
    modules = modules_custom or MODULES_DEFAUT

    # Stratégie: 2 bases × 2 protéines × 2 sauces = 8 repas min
    # 3 × 3 × 2 = 18 repas
    import math

    cube_root = math.ceil(nb_repas_souhaites ** (1 / 3))
    nb_bases = max(2, min(cube_root, len(modules.get("base", []))))
    nb_prots = max(2, min(cube_root, len(modules.get("proteine", []))))
    nb_sauces = max(2, min(cube_root, len(modules.get("sauce", []))))

    bases = modules.get("base", [])[:nb_bases]
    proteines = modules.get("proteine", [])[:nb_prots]
    sauces = modules.get("sauce", [])[:nb_sauces]
    legumes = modules.get("legume", [])[:2]

    # Filtrer par tags si nécessaire
    if tags_requis:
        bases = [b for b in bases if all(t in b.tags for t in tags_requis)] or bases[:1]
        proteines = [p for p in proteines if all(t in p.tags for t in tags_requis)] or proteines[:1]
        sauces = [s for s in sauces if all(t in s.tags for t in tags_requis)] or sauces[:1]

    combinaisons = generer_combinaisons(
        bases, proteines, sauces, legumes, nb_repas_souhaites, tags_requis
    )

    modules_a_preparer = bases + proteines + sauces + legumes
    temps_total = sum(m.temps_prep_min for m in modules_a_preparer)
    nb_modules = len(modules_a_preparer)

    return PlanCombinatoire(
        modules_a_preparer=modules_a_preparer,
        combinaisons_possibles=combinaisons,
        nb_repas_generes=len(combinaisons),
        temps_prep_total=temps_total,
        nb_repas_par_module=round(len(combinaisons) / max(nb_modules, 1), 1),
    )


def lister_modules_disponibles(
    type_module: str | None = None,
) -> dict[str, list[ModuleRecette]]:
    """
    Liste les modules de recettes disponibles.

    Args:
        type_module: Filtrer par type (base, proteine, sauce, legume, topping)
    """
    if type_module:
        return {type_module: MODULES_DEFAUT.get(type_module, [])}
    return MODULES_DEFAUT.copy()


__all__ = [
    "ModuleRecette",
    "CombiRecette",
    "PlanCombinatoire",
    "MODULES_DEFAUT",
    "generer_combinaisons",
    "planifier_batch_modulaire",
    "lister_modules_disponibles",
]
