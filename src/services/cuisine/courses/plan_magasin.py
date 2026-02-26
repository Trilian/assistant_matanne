"""
Mode rapide magasin — Liste triée par rayon pour courses efficaces.

Organise la liste de courses par rayon, avec checklist interactive
et estimation du temps de parcours.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

from sqlalchemy.orm import Session

from src.core.decorators import avec_session_db

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# TYPES
# ═══════════════════════════════════════════════════════════

# Ordre standard des rayons en supermarché français
ORDRE_RAYONS: dict[str, int] = {
    "Fruits et Légumes": 1,
    "Boulangerie": 2,
    "Boucherie": 3,
    "Poissonnerie": 4,
    "Charcuterie": 5,
    "Fromage": 6,
    "Crèmerie": 7,
    "Frais": 8,
    "Surgelés": 9,
    "Épicerie salée": 10,
    "Épicerie sucrée": 11,
    "Boissons": 12,
    "Conserves": 13,
    "Condiments": 14,
    "Petit-déjeuner": 15,
    "Hygiène": 16,
    "Entretien": 17,
    "Bébé": 18,
    "Bio": 19,
    "Autre": 99,
}

# Mapping ingrédients → rayons par défaut
MAPPING_RAYON: dict[str, str] = {
    # Fruits et légumes
    "tomate": "Fruits et Légumes",
    "carotte": "Fruits et Légumes",
    "courgette": "Fruits et Légumes",
    "oignon": "Fruits et Légumes",
    "ail": "Fruits et Légumes",
    "pomme de terre": "Fruits et Légumes",
    "pomme": "Fruits et Légumes",
    "banane": "Fruits et Légumes",
    "salade": "Fruits et Légumes",
    "concombre": "Fruits et Légumes",
    "poivron": "Fruits et Légumes",
    "aubergine": "Fruits et Légumes",
    "champignon": "Fruits et Légumes",
    "poireau": "Fruits et Légumes",
    "chou": "Fruits et Légumes",
    "épinard": "Fruits et Légumes",
    "haricot vert": "Fruits et Légumes",
    "brocoli": "Fruits et Légumes",
    "citron": "Fruits et Légumes",
    "orange": "Fruits et Légumes",
    "fraise": "Fruits et Légumes",
    "herbes": "Fruits et Légumes",
    "persil": "Fruits et Légumes",
    "coriandre": "Fruits et Légumes",
    "basilic": "Fruits et Légumes",
    "menthe": "Fruits et Légumes",
    # Boulangerie
    "pain": "Boulangerie",
    "baguette": "Boulangerie",
    # Boucherie / Protéines
    "poulet": "Boucherie",
    "boeuf": "Boucherie",
    "veau": "Boucherie",
    "porc": "Boucherie",
    "agneau": "Boucherie",
    "dinde": "Boucherie",
    "steak": "Boucherie",
    "escalope": "Boucherie",
    # Poissonnerie
    "saumon": "Poissonnerie",
    "cabillaud": "Poissonnerie",
    "thon": "Poissonnerie",
    "crevette": "Poissonnerie",
    "moule": "Poissonnerie",
    # Charcuterie
    "jambon": "Charcuterie",
    "lardon": "Charcuterie",
    "saucisse": "Charcuterie",
    # Crèmerie / Frais
    "lait": "Crèmerie",
    "beurre": "Crèmerie",
    "crème": "Crèmerie",
    "yaourt": "Crèmerie",
    "fromage": "Fromage",
    "oeuf": "Crèmerie",
    "œuf": "Crèmerie",
    # Épicerie
    "farine": "Épicerie sucrée",
    "sucre": "Épicerie sucrée",
    "chocolat": "Épicerie sucrée",
    "pâtes": "Épicerie salée",
    "riz": "Épicerie salée",
    "huile": "Épicerie salée",
    "vinaigre": "Condiments",
    "moutarde": "Condiments",
    "sauce soja": "Condiments",
    "sel": "Épicerie salée",
    "poivre": "Épicerie salée",
    "épice": "Épicerie salée",
    "cumin": "Épicerie salée",
    "paprika": "Épicerie salée",
    # Conserves
    "tomate pelée": "Conserves",
    "conserve": "Conserves",
    "haricot": "Conserves",
    "pois chiche": "Conserves",
    "lentille": "Conserves",
    "maïs": "Conserves",
    # Petit-déjeuner
    "céréale": "Petit-déjeuner",
    "confiture": "Petit-déjeuner",
    "miel": "Petit-déjeuner",
    # Boissons
    "jus": "Boissons",
    "eau": "Boissons",
    # Bio
    "tofu": "Bio",
    "lait d'avoine": "Bio",
    "lait de soja": "Bio",
    "tempeh": "Bio",
}


@dataclass
class ArticleRayon:
    """Article de courses positionné dans un rayon."""

    nom: str
    quantite: float
    unite: str
    rayon: str
    ingredient_id: int | None = None
    achete: bool = False
    ordre_rayon: int = 99
    notes: str = ""


@dataclass
class ListeModeRapide:
    """Liste de courses organisée par rayon pour le mode rapide."""

    par_rayon: dict[str, list[ArticleRayon]] = field(default_factory=dict)
    nb_articles_total: int = 0
    nb_articles_achetes: int = 0
    temps_estime_min: int = 0  # Minutes estimées en magasin
    rayons_ordonnes: list[str] = field(default_factory=list)

    @property
    def progression(self) -> float:
        if self.nb_articles_total == 0:
            return 100.0
        return round(self.nb_articles_achetes / self.nb_articles_total * 100, 1)


# ═══════════════════════════════════════════════════════════
# FONCTIONS
# ═══════════════════════════════════════════════════════════


def deviner_rayon(nom_ingredient: str) -> str:
    """Devine le rayon d'un ingrédient à partir du mapping."""
    nom_lower = nom_ingredient.lower()

    # Correspondance exacte
    if nom_lower in MAPPING_RAYON:
        return MAPPING_RAYON[nom_lower]

    # Correspondance partielle
    for key, rayon in MAPPING_RAYON.items():
        if key in nom_lower or nom_lower in key:
            return rayon

    return "Autre"


@avec_session_db
def construire_liste_rapide(
    liste_id: int,
    *,
    db: Session,
) -> ListeModeRapide:
    """
    Construit une liste de courses optimisée par rayon.

    Args:
        liste_id: ID de la liste de courses
        db: Session SQLAlchemy

    Returns:
        ListeModeRapide triée par ordre de rayon
    """
    from src.core.models.courses import ArticleCourses
    from src.core.models.recettes import Ingredient

    articles_db = (
        db.query(ArticleCourses, Ingredient)
        .outerjoin(Ingredient, ArticleCourses.ingredient_id == Ingredient.id)
        .filter(ArticleCourses.liste_id == liste_id)
        .all()
    )

    par_rayon: dict[str, list[ArticleRayon]] = {}
    nb_total = 0
    nb_achetes = 0

    for article, ingredient in articles_db:
        nom = ingredient.nom if ingredient else f"Article #{article.id}"

        # Rayon: utiliser celui de l'article s'il existe, sinon deviner
        rayon = article.rayon_magasin or deviner_rayon(nom)
        ordre = ORDRE_RAYONS.get(rayon, 99)

        art = ArticleRayon(
            nom=nom,
            quantite=article.quantite_necessaire,
            unite="pièce",
            rayon=rayon,
            ingredient_id=article.ingredient_id,
            achete=article.achete,
            ordre_rayon=ordre,
            notes=article.notes or "",
        )

        par_rayon.setdefault(rayon, []).append(art)
        nb_total += 1
        if article.achete:
            nb_achetes += 1

    # Trier les rayons
    rayons_ordonnes = sorted(par_rayon.keys(), key=lambda r: ORDRE_RAYONS.get(r, 99))

    # Estimer le temps:  ~2min/rayon + ~15s/article
    temps_estime = len(par_rayon) * 2 + (nb_total - nb_achetes) * 0.25
    temps_estime = max(5, int(temps_estime))

    return ListeModeRapide(
        par_rayon=par_rayon,
        nb_articles_total=nb_total,
        nb_articles_achetes=nb_achetes,
        temps_estime_min=temps_estime,
        rayons_ordonnes=rayons_ordonnes,
    )


def reorganiser_par_rayon(articles: list[dict]) -> dict[str, list[dict]]:
    """
    Organise une liste brute d'articles par rayon.

    Args:
        articles: list de dicts {nom, quantite, unite, rayon?}

    Returns:
        Dict rayon → articles triés
    """
    par_rayon: dict[str, list[dict]] = {}

    for art in articles:
        rayon = art.get("rayon") or deviner_rayon(art.get("nom", ""))
        par_rayon.setdefault(rayon, []).append({**art, "rayon": rayon})

    # Trier les rayons
    return dict(sorted(par_rayon.items(), key=lambda kv: ORDRE_RAYONS.get(kv[0], 99)))


__all__ = [
    "ArticleRayon",
    "ListeModeRapide",
    "ORDRE_RAYONS",
    "MAPPING_RAYON",
    "deviner_rayon",
    "construire_liste_rapide",
    "reorganiser_par_rayon",
]
