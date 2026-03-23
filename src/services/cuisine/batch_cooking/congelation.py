"""
Planificateur de congélation — Suivi du stock congélateur.

Gère la durée de conservation, les alertes de décongélation
et les suggestions pour utiliser les plats congelés.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import date, timedelta

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# TYPES
# ═══════════════════════════════════════════════════════════


@dataclass
class ArticleCongele:
    """Article stocké au congélateur."""

    nom: str
    date_congelation: date
    date_limite: date
    portions: int = 1
    categorie: str = ""  # plat, viande, légume, sauce, pain, dessert
    recette_id: int | None = None
    notes: str = ""

    @property
    def jours_restants(self) -> int:
        return (self.date_limite - date.today()).days

    @property
    def urgence(self) -> int:
        """0=expiré, 1=urgent (<7j), 2=bientôt (<30j), 3=ok."""
        j = self.jours_restants
        if j < 0:
            return 0
        if j < 7:
            return 1
        if j < 30:
            return 2
        return 3


@dataclass
class PlanDecongel:
    """Plan de décongélation pour la semaine."""

    articles_a_sortir: list[ArticleCongele]
    articles_urgents: list[ArticleCongele]
    articles_expires: list[ArticleCongele]
    stock_total: int = 0


# Durées de conservation par catégorie (en jours)
DUREE_CONSERVATION: dict[str, int] = {
    "plat cuisiné": 90,
    "plat": 90,
    "viande crue": 180,
    "viande cuite": 90,
    "volaille crue": 270,
    "volaille cuite": 120,
    "poisson cru": 90,
    "poisson cuit": 90,
    "légume blanchi": 300,
    "légume cru": 240,
    "fruit": 300,
    "sauce": 120,
    "bouillon": 120,
    "pain": 90,
    "pâte": 90,
    "dessert": 90,
    "fromage": 60,
    "beurre": 180,
    "herbes": 180,
    "autre": 90,
}


# ═══════════════════════════════════════════════════════════
# FONCTIONS
# ═══════════════════════════════════════════════════════════


def calculer_date_limite(date_congelation: date, categorie: str = "autre") -> date:
    """Calcule la date limite de conservation au congélateur."""
    jours = DUREE_CONSERVATION.get(categorie.lower(), 90)
    return date_congelation + timedelta(days=jours)


def creer_article_congele(
    nom: str,
    categorie: str = "plat",
    portions: int = 1,
    date_congel: date | None = None,
    recette_id: int | None = None,
    notes: str = "",
) -> ArticleCongele:
    """Crée un article congelé avec date limite auto-calculée."""
    dt = date_congel or date.today()
    limite = calculer_date_limite(dt, categorie)

    return ArticleCongele(
        nom=nom,
        date_congelation=dt,
        date_limite=limite,
        portions=portions,
        categorie=categorie,
        recette_id=recette_id,
        notes=notes,
    )


def trier_par_urgence(articles: list[ArticleCongele]) -> list[ArticleCongele]:
    """Trie les articles congelés par urgence (les plus urgents en premier)."""
    return sorted(articles, key=lambda a: a.jours_restants)


def generer_plan_decongelation(
    stock: list[ArticleCongele],
    jours_avance: int = 7,
) -> PlanDecongel:
    """
    Génère un plan de décongélation pour la semaine.

    Args:
        stock: Stock actuel du congélateur
        jours_avance: Horizon de planification

    Returns:
        PlanDecongel avec articles à sortir et alertes
    """
    aujourd_hui = date.today()
    horizon = aujourd_hui + timedelta(days=jours_avance)

    expires = [a for a in stock if a.jours_restants < 0]
    urgents = [a for a in stock if 0 <= a.jours_restants < 7]
    a_sortir = [a for a in stock if 7 <= a.jours_restants < jours_avance]

    return PlanDecongel(
        articles_a_sortir=trier_par_urgence(a_sortir),
        articles_urgents=trier_par_urgence(urgents),
        articles_expires=expires,
        stock_total=len(stock),
    )


def generer_etiquette_texte(article: ArticleCongele) -> str:
    """
    Génère le texte d'une étiquette de congélation.

    Format:
    ┌─────────────────────────┐
    │  Nom du plat            │
    │  Congelé: 15/01/2025    │
    │  Limite: 15/04/2025     │
    │  Portions: 4            │
    │  Catégorie: plat        │
    └─────────────────────────┘
    """
    lignes = [
        f"🧊 {article.nom}",
        f"📅 Congelé: {article.date_congelation.strftime('%d/%m/%Y')}",
        f"⏰ Limite: {article.date_limite.strftime('%d/%m/%Y')}",
        f"🍽️ Portions: {article.portions}",
    ]
    if article.categorie:
        lignes.append(f"📂 {article.categorie.capitalize()}")
    if article.notes:
        lignes.append(f"📝 {article.notes}")

    return "\n".join(lignes)


def generer_etiquettes_html(articles: list[ArticleCongele]) -> str:
    """
    Génère des étiquettes HTML imprimables pour les articles congelés.

    Returns:
        HTML avec CSS print optimisé (5x3 par page A4)
    """
    style = """
    <style>
    @media print {
        @page { margin: 5mm; }
        .etiquette-container { page-break-inside: avoid; }
    }
    .etiquette-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 4mm;
        font-family: Arial, sans-serif;
    }
    .etiquette {
        border: 1px solid #333;
        border-radius: 4px;
        padding: 4mm;
        font-size: 10pt;
        page-break-inside: avoid;
    }
    .etiquette h3 {
        margin: 0 0 2mm;
        font-size: 11pt;
        border-bottom: 1px solid #ccc;
        padding-bottom: 1mm;
    }
    .etiquette p {
        margin: 1mm 0;
        font-size: 9pt;
    }
    .urgence-0 { background: #ffcccc; }
    .urgence-1 { background: #fff3cd; }
    .urgence-2 { background: #d4edda; }
    .urgence-3 { background: #ffffff; }
    </style>
    """

    etiquettes = []
    for art in articles:
        cls = f"urgence-{art.urgence}"
        etiquettes.append(
            f"""
        <div class="etiquette {cls}">
            <h3>🧊 {art.nom}</h3>
            <p>📅 Congelé: {art.date_congelation.strftime("%d/%m/%Y")}</p>
            <p>⏰ Limite: {art.date_limite.strftime("%d/%m/%Y")}</p>
            <p>🍽️ {art.portions} portion(s) — {art.categorie}</p>
            {f"<p>📝 {art.notes}</p>" if art.notes else ""}
        </div>"""
        )

    return f"""
    {style}
    <div class="etiquette-grid">
        {"".join(etiquettes)}
    </div>
    """


__all__ = [
    "ArticleCongele",
    "PlanDecongel",
    "DUREE_CONSERVATION",
    "calculer_date_limite",
    "creer_article_congele",
    "trier_par_urgence",
    "generer_plan_decongelation",
    "generer_etiquette_texte",
    "generer_etiquettes_html",
    "lister_articles_congeles",
    "ajouter_article_congele",
]


# ═══════════════════════════════════════════════════════════
# PERSISTENCE SESSION_STATE (en attendant table SQL)
# ═══════════════════════════════════════════════════════════

_KEY_CONGELATEUR = "congelateur_stock"
_CONGELATEUR_STORE: list[ArticleCongele] = []


def _obtenir_stock() -> list[ArticleCongele]:
    """Récupère le stock congélateur depuis le store en mémoire."""
    return list(_CONGELATEUR_STORE)


def _sauvegarder_stock(stock: list[ArticleCongele]) -> None:
    """Persiste le stock congélateur dans le store en mémoire."""
    _CONGELATEUR_STORE.clear()
    _CONGELATEUR_STORE.extend(stock)


def lister_articles_congeles() -> list[ArticleCongele]:
    """Liste tous les articles du congélateur, triés par urgence."""
    return trier_par_urgence(_obtenir_stock())


def ajouter_article_congele(
    nom: str,
    categorie: str = "plat",
    quantite: str = "",
    portions: int = 1,
    **kwargs,
) -> ArticleCongele:
    """Ajoute un article au congélateur et persiste."""
    article = creer_article_congele(
        nom=nom,
        categorie=categorie,
        portions=portions,
        **kwargs,
    )
    article.notes = quantite or article.notes
    stock = _obtenir_stock()
    stock.append(article)
    _sauvegarder_stock(stock)
    return article
