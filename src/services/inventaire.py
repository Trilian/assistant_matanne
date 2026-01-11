"""
Service Inventaire Unifié (REFACTORING v2.1)

Service complet pour l'inventaire fusionnant :
- inventaire_service.py (CRUD + statuts)
- inventaire_ai_service.py (Suggestions IA)
- inventaire_io_service.py (Import/Export)

Architecture simplifiée : Tout en 1 seul fichier.
"""
import logging
from datetime import date, timedelta
from typing import Dict, List, Optional
from sqlalchemy.orm import joinedload, Session
import csv
import json
from io import StringIO

# ✅ Import BaseService depuis types.py pour éviter le cycle
from src.services.types import BaseService

from src.core.database import obtenir_contexte_db
from src.core.errors import gerer_erreurs
from src.core.cache import Cache, LimiteDebit
from src.core.models import ArticleInventaire, Ingredient
from src.core.ai import obtenir_client_ia
from src.core.ai.cache import CacheIA

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# CONSTANTES
# ═══════════════════════════════════════════════════════════

CATEGORIES = ["Légumes", "Fruits", "Féculents", "Protéines", "Laitier",
              "Épices & Condiments", "Conserves", "Surgelés", "Autre"]

EMPLACEMENTS = ["Frigo", "Congélateur", "Placard", "Cave", "Garde-manger"]


# ═══════════════════════════════════════════════════════════
# SERVICE INVENTAIRE UNIFIÉ
# ═══════════════════════════════════════════════════════════

class InventaireService(BaseService[ArticleInventaire]):
    """
    Service complet pour l'inventaire.

    Fonctionnalités :
    - CRUD optimisé avec statuts auto
    - Alertes stock bas / péremption
    - Suggestions IA pour courses
    - Import/Export (CSV, JSON)
    - Statistiques enrichies
    """

    def __init__(self):
        super().__init__(ArticleInventaire, cache_ttl=1800)
        self.ai_client = None

    # ═══════════════════════════════════════════════════════════
    # SECTION 1 : CRUD AVEC STATUTS
    # ═══════════════════════════════════════════════════════════

    @gerer_erreurs(afficher_dans_ui=False, valeur_fallback=[])
    def get_inventaire_complet(
            self,
            emplacement: Optional[str] = None,
            categorie: Optional[str] = None,
            include_ok: bool = True
    ) -> List[Dict]:
        """
        Récupère l'inventaire complet avec statuts calculés.

        Args:
            emplacement: Filtrer par emplacement
            categorie: Filtrer par catégorie
            include_ok: Inclure articles OK ou seulement alertes

        Returns:
            Liste articles enrichis avec statuts
        """
        cache_key = f"inventaire_{emplacement}_{categorie}_{include_ok}"
        cached = Cache.obtenir(cache_key, ttl=self.cache_ttl)
        if cached:
            return cached

        with obtenir_contexte_db() as db:
            query = (
                db.query(ArticleInventaire)
                .options(joinedload(ArticleInventaire.ingredient))
            )

            if emplacement:
                query = query.filter(ArticleInventaire.emplacement == emplacement)

            articles = query.all()

            result = []
            today = date.today()

            for article in articles:
                # Calculer statut
                statut = self._calculer_statut(article, today)

                # Filtrer si nécessaire
                if not include_ok and statut == "ok":
                    continue

                # Filtrer par catégorie ingrédient
                if categorie and article.ingredient.categorie != categorie:
                    continue

                result.append({
                    "id": article.id,
                    "ingredient_id": article.ingredient_id,
                    "ingredient_nom": article.ingredient.nom,
                    "ingredient_categorie": article.ingredient.categorie,
                    "quantite": article.quantite,
                    "quantite_min": article.quantite_min,
                    "unite": article.ingredient.unite,
                    "emplacement": article.emplacement,
                    "date_peremption": article.date_peremption,
                    "statut": statut,
                    "jours_avant_peremption": self._jours_avant_peremption(article, today)
                })

            Cache.definir(cache_key, result, ttl=self.cache_ttl, dependencies=["inventaire"])
            return result

    @gerer_erreurs(afficher_dans_ui=False, valeur_fallback=[])
    def get_alertes(self) -> Dict[str, List[Dict]]:
        """
        Récupère toutes les alertes (stock bas + péremption proche).

        Returns:
            Dict avec "stock_bas", "critique", "peremption_proche"
        """
        inventaire = self.get_inventaire_complet(include_ok=False)

        alertes = {
            "stock_bas": [],
            "critique": [],
            "peremption_proche": []
        }

        for article in inventaire:
            if article["statut"] == "critique":
                alertes["critique"].append(article)
            elif article["statut"] == "stock_bas":
                alertes["stock_bas"].append(article)
            elif article["statut"] == "peremption_proche":
                alertes["peremption_proche"].append(article)

        return alertes

    @gerer_erreurs(afficher_dans_ui=True)
    def ajuster_quantite(
            self,
            article_id: int,
            delta: float,
            action: str = "ajout"
    ) -> Optional[ArticleInventaire]:
        """
        Ajuste la quantité d'un article.

        Args:
            article_id: ID de l'article
            delta: Quantité à ajouter/retirer
            action: "ajout" ou "retrait"

        Returns:
            Article mis à jour
        """
        with obtenir_contexte_db() as db:
            article = db.query(ArticleInventaire).get(article_id)
            if not article:
                return None

            if action == "ajout":
                article.quantite += delta
            else:
                article.quantite = max(0, article.quantite - delta)

            db.commit()
            db.refresh(article)

            # Invalider cache
            Cache.invalider(pattern="inventaire")

            logger.info(f"✅ Quantité ajustée : {article.ingredient.nom} ({action} {delta})")
            return article

    # ═══════════════════════════════════════════════════════════
    # SECTION 2 : SUGGESTIONS IA
    # ═══════════════════════════════════════════════════════════

    def _ensure_ai_client(self):
        """Initialise le client IA si nécessaire"""
        if self.ai_client is None:
            self.ai_client = obtenir_client_ia()

    @gerer_erreurs(afficher_dans_ui=True, valeur_fallback=[])
    def suggerer_courses_ia(self) -> List[Dict]:
        """
        Suggère des articles à ajouter aux courses via IA.

        Analyse :
        - Stock bas / critique
        - Historique consommation
        - Saison actuelle

        Returns:
            Liste de suggestions avec quantités
        """
        self._ensure_ai_client()

        # Vérifier rate limit
        autorise, msg = LimiteDebit.peut_appeler()
        if not autorise:
            logger.warning(msg)
            return []

        # Récupérer alertes
        alertes = self.get_alertes()

        # Construire prompt
        prompt = f"""Analyse cet inventaire et suggère des articles à acheter :

Stock bas ({len(alertes['stock_bas'])} articles):
{', '.join([a['ingredient_nom'] for a in alertes['stock_bas'][:10]])}

Stock critique ({len(alertes['critique'])} articles):
{', '.join([a['ingredient_nom'] for a in alertes['critique'][:10]])}

Suggère 10 articles prioritaires à acheter avec quantités recommandées.
Réponds en JSON : [{"nom": str, "quantite": float, "unite": str, "priorite": "haute|moyenne|basse"}]"""

        # Vérifier cache (cache sémantique IA)
        cached = CacheIA.obtenir(prompt=prompt)
        if cached:
            return cached

        # Appel IA (uniformisé, utilise le client wrapper)
        try:
            import asyncio

            response = asyncio.run(self.ai_client.appeler(
                prompt=prompt,
                prompt_systeme="Tu es un chef cuisinier expert.",
                temperature=0.7,
                max_tokens=1000
            ))

            # Parser réponse (attend une chaîne)
            suggestions = self._parse_ai_suggestions(response)

            # Cacher et enregistrer l'appel
            CacheIA.definir(prompt=prompt, reponse=suggestions)
            LimiteDebit.enregistrer_appel()

            logger.info(f"✅ {len(suggestions)} suggestions IA générées")
            return suggestions

        except Exception as e:
            logger.error(f"❌ Erreur suggestions IA : {e}")
            return []

    # ═══════════════════════════════════════════════════════════
    # SECTION 3 : IMPORT/EXPORT
    # ═══════════════════════════════════════════════════════════

    def export_to_csv(self, articles: List[Dict]) -> str:
        """
        Exporte l'inventaire en CSV.

        Args:
            articles: Liste articles

        Returns:
            Contenu CSV
        """
        output = StringIO()
        writer = csv.DictWriter(
            output,
            fieldnames=["ingredient_nom", "quantite", "unite", "quantite_min",
                        "emplacement", "date_peremption", "statut"]
        )

        writer.writeheader()
        for a in articles:
            writer.writerow({
                "ingredient_nom": a["ingredient_nom"],
                "quantite": a["quantite"],
                "unite": a["unite"],
                "quantite_min": a["quantite_min"],
                "emplacement": a["emplacement"] or "",
                "date_peremption": a["date_peremption"] or "",
                "statut": a["statut"]
            })

        return output.getvalue()

    def export_to_json(self, articles: List[Dict], indent: int = 2) -> str:
        """
        Exporte l'inventaire en JSON.

        Args:
            articles: Liste articles
            indent: Indentation

        Returns:
            Contenu JSON
        """
        return json.dumps(articles, indent=indent, ensure_ascii=False, default=str)

    # ═══════════════════════════════════════════════════════════
    # SECTION 4 : STATISTIQUES
    # ═══════════════════════════════════════════════════════════

    @gerer_erreurs(afficher_dans_ui=False, valeur_fallback={})
    def get_statistiques(self) -> Dict:
        """
        Calcule des statistiques sur l'inventaire.

        Returns:
            Dict avec métriques
        """
        inventaire = self.get_inventaire_complet()
        alertes = self.get_alertes()

        # Grouper par catégorie
        par_categorie = {}
        for article in inventaire:
            cat = article["ingredient_categorie"] or "Autre"
            if cat not in par_categorie:
                par_categorie[cat] = 0
            par_categorie[cat] += 1

        # Grouper par emplacement
        par_emplacement = {}
        for article in inventaire:
            emp = article["emplacement"] or "Non défini"
            if emp not in par_emplacement:
                par_emplacement[emp] = 0
            par_emplacement[emp] += 1

        return {
            "total_articles": len(inventaire),
            "stock_bas": len(alertes["stock_bas"]),
            "critique": len(alertes["critique"]),
            "peremption_proche": len(alertes["peremption_proche"]),
            "par_categorie": par_categorie,
            "par_emplacement": par_emplacement,
        }

    # ═══════════════════════════════════════════════════════════
    # HELPERS PRIVÉS
    # ═══════════════════════════════════════════════════════════

    def _calculer_statut(self, article: ArticleInventaire, today: date) -> str:
        """Calcule le statut d'un article"""
        # Péremption proche (< 7 jours)
        if article.date_peremption and (article.date_peremption - today).days <= 7:
            return "peremption_proche"

        # Stock critique (< 50% du seuil)
        if article.quantite < (article.quantite_min * 0.5):
            return "critique"

        # Stock bas (< seuil)
        if article.quantite < article.quantite_min:
            return "stock_bas"

        return "ok"

    def _jours_avant_peremption(self, article: ArticleInventaire, today: date) -> Optional[int]:
        """Calcule jours avant péremption"""
        if not article.date_peremption:
            return None
        return (article.date_peremption - today).days

    def _parse_ai_suggestions(self, content: str) -> List[Dict]:
        """Parse les suggestions IA"""
        try:
            start = content.find("[")
            end = content.rfind("]") + 1
            if start == -1:
                return []
            json_str = content[start:end]
            return json.loads(json_str)
        except:
            return []


# ═══════════════════════════════════════════════════════════
# INSTANCE SINGLETON
# ═══════════════════════════════════════════════════════════

inventaire_service = InventaireService()


# ═══════════════════════════════════════════════════════════
# EXPORTS
# ═══════════════════════════════════════════════════════════

__all__ = [
    "InventaireService",
    "inventaire_service",
    "CATEGORIES",
    "EMPLACEMENTS",
]