"""
Générateur de liens d'achat par catégorie de produit.
Fournit des URLs directes vers les marchands spécialisés selon la catégorie.
"""

from urllib.parse import quote

# Magasins et URL de recherche par catégorie
MAGASINS_PAR_CATEGORIE: dict[str, list[tuple[str, str]]] = {
    "bricolage": [
        ("Leroy Merlin", "https://www.leroymerlin.fr/catalogue/recherche/{q}"),
        ("Castorama", "https://www.castorama.fr/search?q={q}"),
        ("Amazon", "https://www.amazon.fr/s?k={q}"),
    ],
    "jardinage": [
        ("Leroy Merlin", "https://www.leroymerlin.fr/catalogue/recherche/{q}"),
        ("Jardiland", "https://www.jardiland.com/search?query={q}"),
        ("Amazon", "https://www.amazon.fr/s?k={q}&i=lawngarden"),
    ],
    "electromenager": [
        ("Darty", "https://www.darty.com/nav/extra/search?text={q}"),
        ("Boulanger", "https://www.boulanger.com/recherche/{q}"),
        ("Amazon", "https://www.amazon.fr/s?k={q}&i=appliances"),
    ],
    "domotique": [
        ("Amazon", "https://www.amazon.fr/s?k={q}&i=electronics"),
        ("Boulanger", "https://www.boulanger.com/recherche/{q}"),
        ("Fnac", "https://www.fnac.com/SearchResult/ResultList.aspx?SCat=0&Search={q}"),
    ],
    "meubles": [
        ("IKEA", "https://www.ikea.com/fr/fr/search/?q={q}"),
        ("But", "https://www.but.fr/recherche/?text={q}"),
        ("Amazon", "https://www.amazon.fr/s?k={q}&i=furniture"),
    ],
    "entretien": [
        ("Amazon", "https://www.amazon.fr/s?k={q}"),
        ("Cdiscount", "https://www.cdiscount.com/search/10/{q}.html"),
        ("Leroy Merlin", "https://www.leroymerlin.fr/catalogue/recherche/{q}"),
    ],
    "alimentation": [
        ("Amazon Fresh", "https://www.amazon.fr/s?k={q}&i=grocery"),
        ("Cdiscount", "https://www.cdiscount.com/search/10/{q}.html"),
    ],
    "outillage": [
        ("Leroy Merlin", "https://www.leroymerlin.fr/catalogue/recherche/{q}"),
        ("Brico Dépôt", "https://www.bricodepot.fr/catalogsearch/result/?q={q}"),
        ("Amazon", "https://www.amazon.fr/s?k={q}"),
    ],
    "securite": [
        ("Amazon", "https://www.amazon.fr/s?k={q}"),
        ("Castorama", "https://www.castorama.fr/search?q={q}"),
        ("Boulanger", "https://www.boulanger.com/recherche/{q}"),
    ],
    "default": [
        ("Amazon", "https://www.amazon.fr/s?k={q}"),
        ("Cdiscount", "https://www.cdiscount.com/search/10/{q}.html"),
        ("Leroy Merlin", "https://www.leroymerlin.fr/catalogue/recherche/{q}"),
    ],
}


def generer_liens_achat(
    produit: str,
    categorie: str = "default",
    max_magasins: int = 3,
) -> list[dict[str, str]]:
    """
    Génère une liste de liens d'achat pour un produit selon sa catégorie.

    Args:
        produit: Nom du produit à rechercher.
        categorie: Catégorie du produit (bricolage, meubles, etc.).
        max_magasins: Nombre maximum de magasins à retourner.

    Returns:
        Liste de dicts {magasin, url} pour chaque marchand.
    """
    q = quote(produit, safe="")
    magasins = MAGASINS_PAR_CATEGORIE.get(categorie, MAGASINS_PAR_CATEGORIE["default"])
    return [
        {"magasin": nom, "url": url_template.format(q=q)}
        for nom, url_template in magasins[:max_magasins]
    ]


def categories_disponibles() -> list[str]:
    """Retourne la liste des catégories supportées."""
    return [k for k in MAGASINS_PAR_CATEGORIE if k != "default"]
