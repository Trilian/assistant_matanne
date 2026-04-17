"""
Service de scoring nutritionnel PNNS4 pour les repas planifiés.

Règles applicables :
- Déjeuner  : 5 composants × 20 pts = 100 (légumes + féculents + protéines + laitage + fruit)
- Dîner     : 4 composants × 25 pts = 100 (légumes + féculents + protéines + laitage)
             Le soir : jamais de dessert, uniquement du fromage (laitage), pas de fruit
- Goûter    : laitage + fruit + gâteau sain
- Petit-déjeuner : exclu (score=None)
- Reste     : protéines implicitement présentes (repas complet réutilisé)

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
    "viande_rouge": "proteines_viande_rouge",  # alias explicite retourné par l'IA
    "volaille": "proteines_volaille",
    "vegetarien": "proteines_legumineuses",
    "oeuf": "proteines_oeuf",
}

# Types de repas concernés par la logique assiette
TYPES_REPAS_ASSIETTE: set[str] = {"dejeuner", "diner"}
TYPES_REPAS_GOUTER: set[str] = {"gouter"}

_TEXTES_ABSENTS: set[str] = {
    "",
    "-",
    "--",
    "aucun",
    "aucune",
    "none",
    "null",
    "n/a",
    "na",
    "pas de feculent",
    "pas de feculents",
    "pas de féculent",
    "pas de féculents",
    "pas de féculent",
    "pas de féculents",
    "sans feculent",
    "sans feculents",
    "sans féculent",
    "sans féculents",
    "pas de legume",
    "pas de legumes",
    "pas de légume",
    "pas de légumes",
    "sans legume",
    "sans legumes",
    "sans légume",
    "sans légumes",
    "rien",
}


# ── Helpers ───────────────────────────────────────────────────────────────────


_HEURISTIQUES_PROTEINES: list[tuple[str, list[str]]] = [
    ("proteines_oeuf", ["omelette", "œuf", "oeuf", "quiche", "frittata", "tortilla"]),
    (
        "proteines_poisson",
        [
            "saumon", "colin", "cabillaud", "thon", "truite", "sardine", "maquereau",
            "merlu", "lieu", "sole", "turbot", "bar ", "dorade", "daurade", "crevette",
            "moule", "coquille", "poulpe", "calmar", "seiche", "langoustine", "homard",
            "poisson",
        ],
    ),
    (
        "proteines_volaille",
        [
            "poulet", "dinde", "canard", "lapin", "pintade", "caille", "chapon",
            "volaille",
        ],
    ),
    (
        "proteines_viande_rouge",
        [
            "bœuf", "boeuf", "agneau", "porc", "veau", "steak", "côtelette",
            "cotelette", "côte de", "rôti", "roti", "entrecôte", "bavette",
            "gigot", "carré d'agneau", "saucisse", "merguez", "chipolata",
            "carbonara", "bolognaise", "bourguignon", "blanquette",
        ],
    ),
    (
        "proteines_legumineuses",
        [
            "lentille", "pois chiche", "haricot rouge", "haricot blanc", "flageolet",
            "soja", "tofu", "tempeh", "edamame", "falafel", "dal", "dahl",
            "curry de lentilles", "curry de pois",
        ],
    ),
]

# Mots-clés pour détecter des légumes implicitement présents dans le nom du plat
# (utilisé quand le champ legumes a été vidé via _nettoyer_si_inclus_dans_nom)
_MOTS_LEGUMES_IMPLICITES: list[str] = [
    "légume", "legume", "ratatouille", "épinard", "epinard", "courgette",
    "champignon", "tomate", "poivron", "aubergine", "carotte", "haricot",
    "brocoli", "brocolis", "chou", "poireau", "asperge", "céleri", "celeri",
    "pois", "potiron", "courge", "fenouil", "radis", "navet", "endive",
    "betterave", "concombre", "salade verte", "jardinière", "printanière",
    "tajine", "wok de", "poêlée", "grillés", "gratinés", "mijotés",
    "plancha", "vapeur de", "provençale", "ratatouille",
]

# Mots-clés pour détecter des féculents implicitement présents dans le nom du plat
_MOTS_FECULENTS_IMPLICITES: list[str] = [
    "pâtes", "pates", " riz", "semoule", "pomme de terre", "patate",
    "quinoa", "boulgour", "bulgur", "blé", "ble", "épeautre", "epeautre",
    "orge", "polenta", "fécule", "fecule", "maïs", "mais",
    "gratin", "risotto", "lasagne", "ravioli", "gnocchi",
    "tagliatelle", "spaghetti", "linguine", "fusilli", "penne",
    "rigatoni", "farfalle", "macaroni", "purée", "puree",
    "frites", "hachis parmentier", "carbonara", "bolognaise",
    # Plats avec pâte brisée / feuilletée / à pizza (féculent intrinsèque)
    "quiche", "pizza", "tarte salée", "tourte", "flamiche",
    # Légumineuses : féculent + protéine simultanément (PNNS4)
    # Quand c'est le plat principal, le féculent est la légumineuse elle-même
    "lentille", "pois chiche", "haricot rouge", "haricot blanc", "flageolet",
    "fève", "feve", "dal", "dahl",
]

# Mots-clés pour détecter du laitage implicitement présent dans le nom du plat
# (plats où le lait / crème / fromage est un ingrédient structurant de la recette)
_MOTS_LAITAGE_IMPLICITES: list[str] = [
    "gratin",              # crème + fromage (gratin dauphinois, gratin de légumes…)
    "lasagne",             # béchamel au lait
    "béchamel", "bechamel",
    "croque-monsieur", "croque monsieur", "croque-madame", "croque madame",
    "soufflé", "souffle",  # fromage intégré
    "quiche",              # appareil crème fraîche
    "flamiche",            # crème + poireaux
    "tartiflette",         # reblochon
    "raclette",
    "fondue",
]


def _categorie_from_repas(repas: "Repas") -> str | None:
    """Déduit la catégorie nutritionnelle du plat principal.

    Priorité :
    1. recette.categorie_nutritionnelle (le plus précis)
    2. recette.type_proteines  (mapping legacy)
    3. Heuristique sur le nom de la recette ou notes du repas (best-effort, sans IA)
    """
    recette = getattr(repas, "recette", None)
    if recette is not None:
        if recette.categorie_nutritionnelle:
            return recette.categorie_nutritionnelle
        if recette.type_proteines:
            return _MAP_TYPE_PROTEINES.get(recette.type_proteines.lower())
        nom_recette = (recette.nom or "").lower()
        if nom_recette:
            for categorie, mots_cles in _HEURISTIQUES_PROTEINES:
                for mot in mots_cles:
                    if mot in nom_recette:
                        return categorie

    # Fallback sur repas.notes (nom du plat) quand la recette n'est pas chargée —
    # typiquement lors de la génération IA avant flush de la session SQLAlchemy.
    notes = (getattr(repas, "notes", None) or "").lower()
    if notes:
        for categorie, mots_cles in _HEURISTIQUES_PROTEINES:
            for mot in mots_cles:
                if mot in notes:
                    return categorie

    return None


def _valeur_repas_presente(valeur: object) -> bool:
    """Détermine si une valeur textuelle représente un vrai contenu nutritionnel."""
    if valeur is None:
        return False
    if isinstance(valeur, str):
        normalise = " ".join(valeur.strip().lower().split())
        return bool(normalise) and normalise not in _TEXTES_ABSENTS
    return bool(valeur)


def _a_legumes(repas: "Repas") -> bool:
    """True si le repas contient des légumes (champ, recette liée, entrée, ou implicites dans le nom)."""
    if (
        _valeur_repas_presente(getattr(repas, "legumes", None))
        or bool(getattr(repas, "legumes_recette_id", None))
        # L'entrée (soupe, salade…) compte comme légumes
        or _valeur_repas_presente(getattr(repas, "entree", None))
        or bool(getattr(repas, "entree_recette_id", None))
    ):
        return True
    # Détection implicite : légumes déjà dans le nom du plat (champ vidé par _nettoyer_si_inclus_dans_nom)
    notes = (getattr(repas, "notes", None) or "").lower()
    return bool(notes) and any(mot in notes for mot in _MOTS_LEGUMES_IMPLICITES)


def _a_feculents(repas: "Repas") -> bool:
    """True si le repas contient des féculents (champ, recette liée, ou implicites dans le nom)."""
    if _valeur_repas_presente(getattr(repas, "feculents", None)) or bool(
        getattr(repas, "feculents_recette_id", None)
    ):
        return True
    # Détection implicite : féculents déjà dans le nom du plat (champ vidé par _nettoyer_si_inclus_dans_nom)
    notes = (getattr(repas, "notes", None) or "").lower()
    return bool(notes) and any(mot in notes for mot in _MOTS_FECULENTS_IMPLICITES)


def _a_laitage(repas: "Repas") -> bool:
    """True si le repas inclut un laitage (champ explicite ou implicite dans le nom du plat).

    La détection implicite couvre les plats où le lait / crème / fromage est
    un ingrédient structurant (gratin, quiche, lasagne, béchamel…). Elle ne
    s'applique pas au goûter — utiliser directement le champ ``laitage`` pour
    les collations où un laitage séparé est attendu.
    """
    if bool(getattr(repas, "laitage", None)):
        return True
    notes = (getattr(repas, "notes", None) or "").lower()
    return bool(notes) and any(mot in notes for mot in _MOTS_LAITAGE_IMPLICITES)


def _a_proteines(repas: "Repas") -> bool:
    """True si le plat OU la protéine accompagnement couvre la protéine.

    Pour les restes, la protéine doit être détectable dans le nom du plat
    (heuristique) ou via le champ proteine_accompagnement — elle n'est plus
    considérée implicitement présente, car le plat d'origine peut lui-même
    être dépourvu de protéine (ex : gratin dauphinois, risotto, pasta).
    """
    cat = _categorie_from_repas(repas)
    if cat and cat in CATEGORIES_PROTEINES:
        return True
    return _valeur_repas_presente(getattr(repas, "proteine_accompagnement", None)) or bool(
        getattr(repas, "proteine_accompagnement_recette_id", None)
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
    - Reste              → légumes/féculents via fallbacks DB, protéine vérifiée réellement

    Score déjeuner : 5 composants × 20 pts = 100 (légumes + féculents + protéines + laitage + fruit).
    Score dîner    : 4 composants × 25 pts = 100 (légumes + féculents + protéines + laitage).

    Pour les restes (est_reste=True) : légumes et féculents proviennent des
    champs DB remplis par le générateur IA (fallbacks « Légumes de saison » /
    « Riz vapeur »), donc détectés normalement via _a_legumes / _a_feculents.
    La protéine est vérifiée via le nom du plat ou proteine_accompagnement.
    """
    alertes: list[str] = []
    categorie = _categorie_from_repas(repas)
    type_repas = getattr(repas, "type_repas", "").lower()
    est_diner = type_repas == "diner"
    est_dejeuner = type_repas == "dejeuner"

    a_legumes = _a_legumes(repas)
    a_feculents = _a_feculents(repas)
    a_proteines = _a_proteines(repas)

    # Pour les plats féculents/légumes, la recette elle-même compte dans le bon compartiment
    if categorie in CATEGORIES_FECULENTS:
        a_feculents = True
    elif categorie in CATEGORIES_LEGUMES:
        a_legumes = True
    elif categorie in CATEGORIES_PROTEINES:
        a_proteines = True
    elif categorie in CATEGORIES_MIXTES:
        # Plat mixte: ne pas attribuer automatiquement de points.
        # On conserve uniquement les champs réellement renseignés.
        pass

    if not a_legumes:
        alertes.append("Pas de légumes")
    if not a_feculents:
        alertes.append("Féculents manquants")
    if not a_proteines:
        alertes.append("Protéine manquante")

    if est_diner:
        # Dîner : 4 composants × 25 pts — le laitage (fromage) remplace le dessert, pas de fruit
        a_laitage = _a_laitage(repas)
        if not a_laitage:
            alertes.append("Laitage manquant")
        nb_ok = sum([a_legumes, a_feculents, a_proteines, a_laitage])
        score = nb_ok * 25
    elif est_dejeuner:
        # Déjeuner : 5 composants × 20 pts (PNNS4 complet)
        a_laitage = _a_laitage(repas)
        # Le dessert (compote, fruit, yaourt aux fruits…) compte comme fruit/dessert.
        # Champ ``fruit`` conservé pour rétro-compat migration 005 ; ``dessert`` est le
        # champ canonique utilisé par le générateur IA et le formulaire manuel.
        a_fruit = (
            _valeur_repas_presente(getattr(repas, "fruit", None))
            or _valeur_repas_presente(getattr(repas, "dessert", None))
            or bool(getattr(repas, "dessert_recette_id", None))
        )
        if not a_laitage:
            alertes.append("Laitage manquant")
        if not a_fruit:
            alertes.append("Fruit / dessert manquant")
        nb_ok = sum([a_legumes, a_feculents, a_proteines, a_laitage, a_fruit])
        score = nb_ok * 20
    else:
        # Autres types (type inconnu) : 3 composants × 33 pts + 1 pt bonus
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


def analyser_distribution_proteines_semaine(
    repas_list: list["Repas"],
    nb_vegetarien_min: int | None = None,
) -> BilanProteinesSemaine:
    """Analyse la distribution des protéines sur la semaine (déj + dîner seulement).

    Args:
        repas_list: Liste de tous les repas de la semaine (tous types).
        nb_vegetarien_min: Seuil minimum de repas légumineuses/végétarien configuré
            par l'utilisateur. Remplace la valeur par défaut de CIBLES_PROTEINES_SEMAINE
            (3) pour refléter les préférences réelles. None = utiliser la constante.

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
        # Surcharge du seuil minimum légumineuses si l'utilisateur en a configuré un
        if cat == "proteines_legumineuses" and nb_vegetarien_min is not None:
            min_v = nb_vegetarien_min
        else:
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
