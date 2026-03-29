"""Service de prediction de peremption personnalisee (IA7)."""

from __future__ import annotations

from collections import defaultdict
from datetime import date, timedelta
from typing import Any

from sqlalchemy.orm import Session

from src.core.decorators import avec_gestion_erreurs, avec_session_db
from src.services.core.registry import service_factory


_FACTEURS_CONSERVATION = {
    "congel": 1.8,
    "frigo": 1.0,
    "placard": 1.25,
    "cave": 1.4,
}


class ServicePredictionPeremption:
    """Predictions basees sur duree de vie observee + facteur conservation."""

    def _facteur_conservation(self, emplacement: str | None) -> float:
        em = (emplacement or "").lower()
        for key, facteur in _FACTEURS_CONSERVATION.items():
            if key in em:
                return facteur
        return 1.0

    @avec_gestion_erreurs(default_return={})
    @avec_session_db
    def calculer_durees_vie_moyennes(self, *, db: Session | None = None) -> dict[str, float]:
        """Estime une duree de vie moyenne (jours) par categorie depuis l'historique inventaire."""
        if db is None:
            return {}

        from src.core.models.inventaire import ArticleInventaire, HistoriqueInventaire

        historiques = (
            db.query(HistoriqueInventaire)
            .order_by(HistoriqueInventaire.article_id.asc(), HistoriqueInventaire.date_modification.asc())
            .all()
        )

        dates_ajout: dict[int, date] = {}
        durees_par_categorie: dict[str, list[int]] = defaultdict(list)

        # Mapper article -> categorie ingredient
        articles = db.query(ArticleInventaire).all()
        categorie_par_article: dict[int, str] = {}
        for article in articles:
            categorie_par_article[article.id] = (article.categorie or "autre").lower()

        for h in historiques:
            article_id = int(h.article_id)
            type_modif = (h.type_modification or "").lower()
            d_modif = h.date_modification.date()

            if type_modif == "ajout":
                dates_ajout[article_id] = d_modif
                continue

            # Considere une consommation complete quand quantite_apres est nulle
            quantite_apres = h.quantite_apres
            est_consomme = type_modif == "suppression" or (
                quantite_apres is not None and float(quantite_apres) <= 0
            )
            if not est_consomme:
                continue

            d_ajout = dates_ajout.get(article_id)
            if d_ajout is None:
                continue

            delta = (d_modif - d_ajout).days
            if delta <= 0:
                continue

            categorie = categorie_par_article.get(article_id, "autre")
            durees_par_categorie[categorie].append(delta)

        moyennes: dict[str, float] = {}
        for categorie, valeurs in durees_par_categorie.items():
            if valeurs:
                moyennes[categorie] = round(sum(valeurs) / len(valeurs), 1)

        # Fallback global si peu d'historique
        if not moyennes:
            moyennes = {
                "fruits": 6.0,
                "legumes": 7.0,
                "produits laitiers": 5.0,
                "viandes": 4.0,
                "autre": 7.0,
            }

        return moyennes

    @avec_gestion_erreurs(default_return={"items": [], "total": 0})
    @avec_session_db
    def predire_peremptions_personnalisees(
        self,
        horizon_jours: int = 7,
        *,
        db: Session | None = None,
    ) -> dict[str, Any]:
        """Retourne les alertes proactives basees sur prediction personnalisee."""
        if db is None:
            return {"items": [], "total": 0}

        from src.core.models.inventaire import ArticleInventaire

        today = date.today()
        horizon = today + timedelta(days=horizon_jours)
        moyennes = self.calculer_durees_vie_moyennes(db=db)

        rows = (
            db.query(ArticleInventaire)
            .filter(ArticleInventaire.quantite > 0)
            .all()
        )

        items: list[dict[str, Any]] = []
        for article in rows:
            categorie = (article.categorie or "autre").lower()
            duree_ref = float(moyennes.get(categorie, moyennes.get("autre", 7.0)))
            facteur = self._facteur_conservation(article.emplacement)

            # Approximation age produit: depuis derniere mise a jour inventaire.
            age_jours = 0
            if article.derniere_maj:
                age_jours = max(0, (today - article.derniere_maj.date()).days)

            jours_restants_predits = int(max(0.0, (duree_ref * facteur) - age_jours))
            date_predite = today + timedelta(days=jours_restants_predits)

            if date_predite > horizon:
                continue

            niveau = "moyenne"
            if jours_restants_predits <= 2:
                niveau = "haute"
            if jours_restants_predits <= 1:
                niveau = "critique"

            items.append(
                {
                    "article_id": article.id,
                    "nom": article.nom,
                    "categorie": categorie,
                    "emplacement": article.emplacement,
                    "date_peremption_db": article.date_peremption.isoformat()
                    if article.date_peremption
                    else None,
                    "date_peremption_predite": date_predite.isoformat(),
                    "jours_restants_predits": jours_restants_predits,
                    "niveau": niveau,
                }
            )

        items.sort(key=lambda x: (x["jours_restants_predits"], x["nom"] or ""))
        return {"items": items, "total": len(items)}


@service_factory("prediction_peremption", tags={"cuisine", "anti_gaspillage", "ia"})
def obtenir_service_prediction_peremption() -> ServicePredictionPeremption:
    """Factory singleton du service prediction peremption."""
    return ServicePredictionPeremption()


get_prediction_peremption_service = obtenir_service_prediction_peremption
