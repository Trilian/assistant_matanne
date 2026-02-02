"""
Service d'intégration avec les enseignes de courses.

NOTE IMPORTANTE sur les APIs:
================================

**Carrefour Drive / Carrefour API:**
- ❌ PAS d'API publique officielle pour les particuliers
- Carrefour propose une API B2B pour partenaires uniquement
- Des solutions non-officielles existent (scraping) mais violent les CGU

**Alternatives explorées:**
- Open Food Facts: ✅ API gratuite (infos produits, pas prix/stock)
- Picard: ❌ Pas d'API
- Thiriet: ❌ Pas d'API  
- Grand Frais: ❌ Pas d'API
- Bio Coop: ❌ Pas d'API

**Solutions implémentées:**
1. Liste de courses manuelle avec organisation par magasin
2. Export vers applications tierces (Bring!, AnyList)
3. Génération de PDF imprimable par rayon
4. (Optionnel) Scraping non-officiel avec consentement utilisateur

Ce module fournit des helpers pour organiser les courses par magasin
et des exports compatibles avec les apps de liste de courses.
"""

import logging
from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# CONSTANTES
# ═══════════════════════════════════════════════════════════


class Magasin(str, Enum):
    """Magasins supportés (organisation manuelle)."""
    CARREFOUR = "carrefour"
    CARREFOUR_DRIVE = "carrefour_drive"
    BIO_COOP = "bio_coop"
    GRAND_FRAIS = "grand_frais"
    THIRIET = "thiriet"
    PICARD = "picard"
    LIDL = "lidl"
    AUCHAN = "auchan"
    INTERMARCHE = "intermarche"
    LECLERC = "leclerc"
    AUTRE = "autre"


# Jours de courses suggérés par magasin (basé sur profil utilisateur)
JOURS_COURSES_DEFAUT = {
    Magasin.CARREFOUR_DRIVE: "samedi",  # Drive le samedi
    Magasin.THIRIET: "samedi",  # Surgelés avec Carrefour
    Magasin.BIO_COOP: "mercredi",  # Bio le mercredi
    Magasin.GRAND_FRAIS: "mercredi",  # Frais le mercredi
}


# Organisation des rayons par magasin
RAYONS_PAR_MAGASIN = {
    Magasin.CARREFOUR_DRIVE: [
        "Fruits et Légumes",
        "Boucherie - Volaille",
        "Poissonnerie",
        "Crèmerie - Œufs",
        "Épicerie salée",
        "Épicerie sucrée",
        "Boissons",
        "Surgelés",
        "Hygiène - Beauté",
        "Entretien - Maison",
        "Bébé",
    ],
    Magasin.BIO_COOP: [
        "Fruits et Légumes Bio",
        "Vrac",
        "Épicerie",
        "Frais",
        "Surgelés Bio",
        "Hygiène naturelle",
        "Compléments",
    ],
    Magasin.GRAND_FRAIS: [
        "Fruits",
        "Légumes",
        "Herbes fraîches",
        "Fromagerie",
        "Charcuterie",
        "Traiteur",
        "Épicerie fine",
    ],
    Magasin.THIRIET: [
        "Surgelés salés",
        "Surgelés sucrés",
        "Glaces",
        "Plats préparés",
    ],
}


# ═══════════════════════════════════════════════════════════
# DATACLASSES
# ═══════════════════════════════════════════════════════════


@dataclass
class ArticleCourse:
    """Article dans une liste de courses."""
    nom: str
    quantite: float = 1
    unite: str = ""
    rayon: str = ""
    magasin_prefere: Optional[Magasin] = None
    prix_estime: Optional[float] = None
    est_bio: bool = False
    est_urgent: bool = False
    notes: str = ""
    coche: bool = False


@dataclass
class ListeCoursesMagasin:
    """Liste de courses pour un magasin spécifique."""
    magasin: Magasin
    date_prevue: Optional[datetime] = None
    articles: list[ArticleCourse] = field(default_factory=list)
    total_estime: float = 0.0
    
    def ajouter_article(self, article: ArticleCourse):
        """Ajoute un article et recalcule le total."""
        self.articles.append(article)
        if article.prix_estime:
            self.total_estime += article.prix_estime * article.quantite
    
    def par_rayon(self) -> dict[str, list[ArticleCourse]]:
        """Groupe les articles par rayon."""
        rayons = {}
        for art in self.articles:
            rayon = art.rayon or "Autres"
            if rayon not in rayons:
                rayons[rayon] = []
            rayons[rayon].append(art)
        return rayons


# ═══════════════════════════════════════════════════════════
# SERVICE ORGANISATION COURSES
# ═══════════════════════════════════════════════════════════


class CoursesOrganisationService:
    """
    Service d'organisation des courses par magasin.
    
    Pas d'API directe avec les enseignes mais:
    - Organisation intelligente par rayon
    - Suggestion du magasin optimal par produit
    - Export vers apps tierces (Bring!, AnyList)
    - Génération PDF par magasin
    """
    
    def __init__(self):
        self.preferences_magasins = {}  # {categorie: magasin_prefere}
    
    def suggerer_magasin(self, article: str, est_bio: bool = False) -> Magasin:
        """
        Suggère le meilleur magasin pour un article.
        
        Args:
            article: Nom de l'article
            est_bio: Si produit bio souhaité
            
        Returns:
            Magasin suggéré
        """
        article_lower = article.lower()
        
        # Bio -> Bio Coop
        if est_bio:
            return Magasin.BIO_COOP
        
        # Surgelés -> Thiriet ou Picard
        if any(mot in article_lower for mot in ["surgelé", "glace", "congelé"]):
            return Magasin.THIRIET
        
        # Frais, herbes -> Grand Frais
        if any(mot in article_lower for mot in ["frais", "herbe", "basilic", "persil", "coriandre"]):
            return Magasin.GRAND_FRAIS
        
        # Par défaut -> Carrefour Drive (plus complet)
        return Magasin.CARREFOUR_DRIVE
    
    def organiser_liste(
        self, 
        articles: list[ArticleCourse],
    ) -> dict[Magasin, ListeCoursesMagasin]:
        """
        Organise une liste d'articles par magasin.
        
        Args:
            articles: Liste d'articles à acheter
            
        Returns:
            Dict {magasin: liste_courses}
        """
        listes = {}
        
        for article in articles:
            # Déterminer le magasin
            magasin = article.magasin_prefere or self.suggerer_magasin(
                article.nom, 
                article.est_bio
            )
            
            # Créer la liste si nécessaire
            if magasin not in listes:
                listes[magasin] = ListeCoursesMagasin(
                    magasin=magasin,
                    date_prevue=datetime.now(),
                )
            
            # Assigner le rayon
            if not article.rayon:
                article.rayon = self._detecter_rayon(article.nom, magasin)
            
            listes[magasin].ajouter_article(article)
        
        return listes
    
    def _detecter_rayon(self, article: str, magasin: Magasin) -> str:
        """Détecte le rayon probable d'un article."""
        article_lower = article.lower()
        
        # Mapping simple
        if any(mot in article_lower for mot in ["pomme", "banane", "orange", "fruit"]):
            return "Fruits et Légumes" if magasin != Magasin.GRAND_FRAIS else "Fruits"
        
        if any(mot in article_lower for mot in ["carotte", "tomate", "salade", "légume", "courgette"]):
            return "Fruits et Légumes" if magasin != Magasin.GRAND_FRAIS else "Légumes"
        
        if any(mot in article_lower for mot in ["poulet", "boeuf", "porc", "viande"]):
            return "Boucherie - Volaille"
        
        if any(mot in article_lower for mot in ["saumon", "poisson", "cabillaud"]):
            return "Poissonnerie"
        
        if any(mot in article_lower for mot in ["lait", "yaourt", "fromage", "beurre", "crème"]):
            return "Crèmerie - Œufs" if magasin == Magasin.CARREFOUR_DRIVE else "Frais"
        
        if any(mot in article_lower for mot in ["pâtes", "riz", "huile", "conserve"]):
            return "Épicerie salée" if magasin == Magasin.CARREFOUR_DRIVE else "Épicerie"
        
        if any(mot in article_lower for mot in ["biscuit", "chocolat", "confiture", "sucre"]):
            return "Épicerie sucrée" if magasin == Magasin.CARREFOUR_DRIVE else "Épicerie"
        
        if any(mot in article_lower for mot in ["surgelé", "glace", "congelé"]):
            return "Surgelés"
        
        return "Autres"
    
    def exporter_bring(self, liste: ListeCoursesMagasin) -> str:
        """
        Exporte au format compatible Bring! (copier-coller).
        
        Bring! accepte une liste textuelle simple.
        """
        lignes = [f"# {liste.magasin.value.replace('_', ' ').title()}"]
        lignes.append("")
        
        for rayon, articles in liste.par_rayon().items():
            lignes.append(f"## {rayon}")
            for art in articles:
                qty = f"{art.quantite} {art.unite}" if art.unite else f"{int(art.quantite)}"
                lignes.append(f"- {art.nom} ({qty})")
            lignes.append("")
        
        return "\n".join(lignes)
    
    def exporter_json_anylist(self, liste: ListeCoursesMagasin) -> dict:
        """
        Exporte au format JSON pour AnyList ou autres apps.
        """
        return {
            "name": f"Courses {liste.magasin.value.replace('_', ' ').title()}",
            "items": [
                {
                    "name": art.nom,
                    "quantity": f"{art.quantite} {art.unite}".strip(),
                    "category": art.rayon,
                    "checked": art.coche,
                    "notes": art.notes,
                }
                for art in liste.articles
            ]
        }
    
    def generer_html_imprimable(self, listes: dict[Magasin, ListeCoursesMagasin]) -> str:
        """Génère un HTML imprimable avec toutes les listes."""
        
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Liste de Courses</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                .magasin { page-break-after: always; margin-bottom: 30px; }
                .magasin:last-child { page-break-after: avoid; }
                h1 { color: #2d4d36; border-bottom: 2px solid #4caf50; }
                h2 { color: #5e7a6a; margin-top: 20px; }
                ul { list-style: none; padding: 0; }
                li { padding: 8px 0; border-bottom: 1px dotted #ddd; }
                li::before { content: "☐ "; font-size: 1.2em; }
                .quantite { color: #888; font-size: 0.9em; }
                .total { font-weight: bold; margin-top: 20px; padding: 10px; background: #f5f5f5; }
                @media print {
                    .no-print { display: none; }
                }
            </style>
        </head>
        <body>
        """
        
        for magasin, liste in listes.items():
            html += f"""
            <div class="magasin">
                <h1>🛒 {magasin.value.replace('_', ' ').title()}</h1>
            """
            
            for rayon, articles in liste.par_rayon().items():
                html += f"<h2>{rayon}</h2><ul>"
                for art in articles:
                    qty = f"{art.quantite} {art.unite}" if art.unite else ""
                    html += f'<li>{art.nom} <span class="quantite">{qty}</span></li>'
                html += "</ul>"
            
            if liste.total_estime > 0:
                html += f'<div class="total">Total estimé: {liste.total_estime:.2f} €</div>'
            
            html += "</div>"
        
        html += "</body></html>"
        return html


# ═══════════════════════════════════════════════════════════
# SINGLETON
# ═══════════════════════════════════════════════════════════

_service_instance: Optional[CoursesOrganisationService] = None


def get_courses_organisation_service() -> CoursesOrganisationService:
    """Factory pour obtenir le service d'organisation des courses."""
    global _service_instance
    if _service_instance is None:
        _service_instance = CoursesOrganisationService()
    return _service_instance
