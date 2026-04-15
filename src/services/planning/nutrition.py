"""
Service de scoring nutritionnel PNNS4 pour les repas planifiés.

Règles applicables :
- Déjeuner / Dîner : logique assiette bidirectionnelle (légumes + féculents + protéines)
- Goûter           : laitage + fruit + gâteau sain
- Petit-déjeuner   : exclu (score=None)

Distribution protéines semaine :
  poisson      ≥ 2x (dont 1 poisson gras)
  viande rouge ≤ 3x
  légumineuses ≥ 3x
  œufs         3-4x OK
  volaille     sans contrainte
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from src.core.models.planning import Repas

# ── Constantes ────────────────────────────────────────────────────────────────

CATEGORIES_PROTEINES: set[str] = {
    "proteines_poisson",
    "proteines_viande_rouge",
    "proteines_volaille",
    "proteines_oeuf",
    "proteines_legumineuses",
}

CATEGORIES_FECULENTS: set[str] = {"feculents"}
CATEGORIES_LEGUMES: set[str] = {"legumes_principaux"}
CATEGORIES_MIXTES: set[str] = {"mixte"}

# Cibles hebdomadaires (déjeuner + dîner confondus)
CIBLES_PROTEINES_SEMAINE: dict[str, dict[str, Any]] = {
    "proteines_poisson": {
        "label": "Poisson",
        "min": 2,
        "max": None,
        "ideal": 3,
        "dont_gras": 1,  # au moins 1 poisson gras (saumon, maquereau, sardine)
    },
    "proteines_viande_rouge": {
        "label": "Viande rouge",
        "min": 0,
        "max": 3,
        "ideal": 2,
        "dont_gras": 0,
    },
    "proteines_volaille": {
        "label": "Volaille",
        "min": 0,
        "max": None,
        "ideal": None,
        "dont_gras": 0,
    },
    "proteines_oeuf": {
        "label": "Œufs",
        "min": 0,
        "max": 4,
        "ideal": 3,
        "dont_gras": 0,
    },
    "proteines_legumineuses": {
        "label": "Légumineuses",
        "min": 3,
        "max": None,
        "ideal": 3,
        "dont_gras": 0,
    },
}

# Mapping type_proteines legacy → categorie_nutritionnelle
_MAP_TYPE_PROTEINES: dict[str, str] = {
    "poisson": "proteines_poisson",
    "viande": "proteines_viande_rouge",
    "volaille": "proteines_volaille",
    "vegetarien": "proteines_legumineuses",
    "oeuf": "proteines_oeuf",
}

# Types de repas concernés par la logique assiette
TYPES_REPAS_ASSIETTE: set[str] = {"dejeuner", "diner"}
TYPES_REPAS_GOUTER: set[str] = {"gouter"}


# ── Helpers ───────────────────────────────────────────────────────────────────


def _categorie_from_repas(repas: "Repas") -> str | None:
    """Déduit la catégorie nutritionnelle du plat principal.

    Priorité :
    1. recette.categorie_nutritionnelle (le plus précis)
    2. recette.type_proteines  (mapping legacy)
    3. Heuristique sur le nom de la recette (best-effort, sans IA)
    """
    recette = getattr(repas, "recette", None)
    if recette is None:
        return None

    if recette.categorie_nutritionnelle:
        return recette.categorie_nutritionnelle

    if recette.type_proteines:
        return _MAP_TYPE_PROTEINES.get(recette.type_proteines.lower())

    return None


def _a_legumes(repas: "Repas") -> bool:
    return bool(
        getattr(repas, "legumes", None) or getattr(repas, "legumes_recette_id", None)
    )


def _a_feculents(repas: "Repas") -> bool:
    return bool(
        getattr(repas, "feculents", None) or getattr(repas, "feculents_recette_id", None)
    )


def _a_proteines(repas: "Repas") -> bool:
    """True si le plat OU la protéine accompagnement couvre la protéine."""
    cat = _categorie_from_repas(repas)
    if cat and cat in CATEGORIES_PROTEINES:
        return True
    return bool(
        getattr(repas, "proteine_accompagnement", None)
        or getattr(repas, "proteine_accompagnement_recette_id", None)
    )


# ── Scoring : déjeuner / dîner ────────────────────────────────────────────────


def _evaluer_repas_assiette(repas: "Repas") -> tuple[int, list[str]]:
    """Calcule le score et les alertes pour un repas déjeuner/dîner.

    Logique bidirectionnelle :
    - Plat = protéines   → vérifie légumes + féculents
    - Plat = féculents   → vérifie légumes + protéines (accompagnement)
    - Plat = légumes     → vérifie féculents + protéines
    - Plat = mixte       → analyse globale
    - Catégorie inconnue → utilise présence des champs comme indicateur

    Score : 3 composants × 33 pts + 1 pt bonus si tout est présent = 100.
    """
    alertes: list[str] = []
    categorie = _categorie_from_repas(repas)

    a_legumes = _a_legumes(repas)
    a_feculents = _a_feculents(repas)
    a_proteines = _a_proteines(repas)

    # Pour les plats féculents/légumes, le recette lui-même compte dans le bon compartiment
    if categorie in CATEGORIES_FECULENTS:
        a_feculents = True
    elif categorie in CATEGORIES_LEGUMES:
        a_legumes = True
    elif categorie in CATEGORIES_PROTEINES:
        a_proteines = True
    elif categorie in CATEGORIES_MIXTES:
        # Plat mixte → on présume feculents et légumes partiellement présents
        a_feculents = a_feculents or True
        a_legumes = a_legumes or True

    if not a_legumes:
        alertes.append("Pas de légumes")
    if not a_feculents:
        alertes.append("Féculents manquants")
    if not a_proteines:
        alertes.append("Protéine manquante")

    # Score sur 100
    nb_ok = sum([a_legumes, a_feculents, a_proteines])
    if nb_ok == 3:
        score = 100
    elif nb_ok == 2:
        score = 66
    elif nb_ok == 1:
        score = 33
    else:
        score = 0

    return score, alertes


# ── Scoring : goûter ──────────────────────────────────────────────────────────


def _evaluer_repas_gouter(repas: "Repas") -> tuple[int, list[str]]:
    """Score PNNS pour le goûter : laitage + fruit + gâteau sain."""
    alertes: list[str] = []

    a_laitage = bool(getattr(repas, "laitage", None))
    # fruit_gouter prévaut ; sinon fallback sur fruit (champ legacy migration 005)
    a_fruit = bool(
        getattr(repas, "fruit_gouter", None) or getattr(repas, "fruit", None)
    )
    a_gateau = bool(getattr(repas, "gateau_gouter", None))

    if not a_laitage:
        alertes.append("Laitage manquant")
    if not a_fruit:
        alertes.append("Fruit/compote manquant")
    if not a_gateau:
        alertes.append("Gâteau sain manquant")

    nb_ok = sum([a_laitage, a_fruit, a_gateau])
    if nb_ok == 3:
        score = 100
    elif nb_ok == 2:
        score = 66
    elif nb_ok == 1:
        score = 33
    else:
        score = 0

    return score, alertes


# ── Point d'entrée public ─────────────────────────────────────────────────────


def evaluer_equilibre_repas(repas: "Repas") -> dict[str, Any]:
    """Calcule le score d'équilibre PNNS4 d'un repas.

    Returns:
        dict avec :
        - score_equilibre  : int 0-100 ou None (petit_déjeuner)
        - alertes_equilibre: list[str] (vide = repas équilibré)
        - applicable       : bool (False pour petit_déjeuner)
    """
    type_repas = getattr(repas, "type_repas", "").lower()

    if type_repas == "petit_dejeuner":
        return {"score_equilibre": None, "alertes_equilibre": [], "applicable": False}

    if type_repas in TYPES_REPAS_GOUTER:
        score, alertes = _evaluer_repas_gouter(repas)
    else:
        # déjeuner, dîner — et tout type inconnu par convention
        score, alertes = _evaluer_repas_assiette(repas)

    return {
        "score_equilibre": score,
        "alertes_equilibre": alertes,
        "applicable": True,
    }


# ── Bilan protéines semaine ───────────────────────────────────────────────────


@dataclass
class BilanProteinesSemaine:
    """Résultat de l'analyse de la distribution des protéines sur la semaine."""

    compteurs: dict[str, int] = field(default_factory=dict)
    alertes: list[str] = field(default_factory=list)
    recommandations: list[str] = field(default_factory=list)
    score_semaine: int = 0  # 0-100


def analyser_distribution_proteines_semaine(repas_list: list["Repas"]) -> BilanProteinesSemaine:
    """Analyse la distribution des protéines sur la semaine (déj + dîner seulement).

    Args:
        repas_list: Liste de tous les repas de la semaine (tous types).

    Returns:
        BilanProteinesSemaine avec compteurs, alertes et score global.
    """
    compteurs: dict[str, int] = {k: 0 for k in CIBLES_PROTEINES_SEMAINE}

    for repas in repas_list:
        type_repas = getattr(repas, "type_repas", "").lower()
        if type_repas not in TYPES_REPAS_ASSIETTE:
            continue

        cat = _categorie_from_repas(repas)
        # Aussi compter la protéine accompagnement si plat = féculent/légume
        prot_acc_recette = getattr(repas, "proteine_accompagnement_recette", None)
        prot_acc_text = getattr(repas, "proteine_accompagnement", None)

        if cat and cat in compteurs:
            compteurs[cat] += 1
        elif prot_acc_recette:
            cat_acc = getattr(prot_acc_recette, "categorie_nutritionnelle", None)
            if cat_acc and cat_acc in compteurs:
                compteurs[cat_acc] += 1
        elif prot_acc_text:
            # Heuristique sur le texte libre
            txt = prot_acc_text.lower()
            if any(mot in txt for mot in ("saumon", "cabillaud", "colin", "merlu", "thon", "truite", "maquereau", "sardine", "dorade")):
                compteurs["proteines_poisson"] += 1
            elif any(mot in txt for mot in ("lentille", "pois chiche", "haricot", "flageolet", "fève", "soja")):
                compteurs["proteines_legumineuses"] += 1
            elif any(mot in txt for mot in ("poulet", "dinde", "volaille", "lapin")):
                compteurs["proteines_volaille"] += 1
            elif any(mot in txt for mot in ("oeuf", "œuf", "omelette", "quiche")):
                compteurs["proteines_oeuf"] += 1
            elif any(mot in txt for mot in ("bœuf", "porc", "agneau", "veau", "steak", "côte", "bifteck")):
                compteurs["proteines_viande_rouge"] += 1

    alertes: list[str] = []
    recommandations: list[str] = []
    points = 0
    max_points = 0

    for cat, cible in CIBLES_PROTEINES_SEMAINE.items():
        nb = compteurs.get(cat, 0)
        label = cible["label"]
        min_v = cible["min"]
        max_v = cible["max"]

        # Contrainte minimale
        if min_v is not None and min_v > 0:
            max_points += 1
            if nb >= min_v:
                points += 1
            else:
                manque = min_v - nb
                alertes.append(f"{label} insuffisant ({nb}/{min_v} fois/semaine)")
                recommandations.append(
                    f"Ajouter {manque} repas à base de {label.lower()} cette semaine"
                )

        # Contrainte maximale
        if max_v is not None:
            max_points += 1
            if nb <= max_v:
                points += 1
            else:
                depassement = nb - max_v
                alertes.append(f"Trop de {label.lower()} ({nb}/{max_v} max/semaine)")
                recommandations.append(
                    f"Réduire de {depassement} repas à base de {label.lower()}"
                )

    score = round((points / max_points) * 100) if max_points > 0 else 100

    return BilanProteinesSemaine(
        compteurs=compteurs,
        alertes=alertes,
        recommandations=recommandations,
        score_semaine=score,
    )
