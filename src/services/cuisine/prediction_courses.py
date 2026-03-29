"""Service de prediction de courses a partir de l'historique d'achats (IA2)."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from sqlalchemy.orm import Session

from src.core.decorators import avec_gestion_erreurs, avec_session_db
from src.services.core.registry import service_factory


class ServicePredictionCourses:
    """Predictions d'articles recurrents avec score de confiance."""

    @avec_gestion_erreurs(default_return=[])
    @avec_session_db
    def predire_articles(
        self,
        limite: int = 25,
        inclure_deja_sur_liste: bool = False,
        *,
        db: Session | None = None,
    ) -> list[dict[str, Any]]:
        """Retourne les articles habituels a pre-completer dans la liste courses."""
        if db is None:
            return []

        from src.core.models.courses import ArticleCourses, HistoriqueAchats, ListeCourses
        from src.core.models.recettes import Ingredient

        now = datetime.now(UTC)

        historiques = (
            db.query(HistoriqueAchats)
            .filter(HistoriqueAchats.nb_achats >= 2, HistoriqueAchats.frequence_jours.isnot(None))
            .all()
        )

        deja_sur_liste: set[str] = set()
        articles_actifs = (
            db.query(ArticleCourses)
            .join(ListeCourses)
            .filter(ArticleCourses.achete.is_(False), ListeCourses.archivee.is_(False))
            .all()
        )
        for article in articles_actifs:
            nom = article.ingredient.nom if getattr(article, "ingredient", None) else None
            if nom:
                deja_sur_liste.add(nom.lower())

        predictions: list[dict[str, Any]] = []
        for h in historiques:
            if not h.derniere_achat or not h.frequence_jours:
                continue

            jours_depuis = (now - h.derniere_achat).days
            frequence = max(1, int(h.frequence_jours))

            # Fenetre de prediction: on commence a proposer avant l'echeance.
            if jours_depuis < int(frequence * 0.7):
                continue

            nom = (h.article_nom or "").strip()
            if not nom:
                continue

            nom_lower = nom.lower()
            sur_liste = nom_lower in deja_sur_liste
            if sur_liste and not inclure_deja_sur_liste:
                continue

            # Score de confiance combine:
            # - retard par rapport a la frequence habituelle
            # - fiabilite de l'historique (nb_achats)
            retard_ratio = min(1.0, max(0.0, jours_depuis / frequence))
            fiabilite = min(1.0, (h.nb_achats or 0) / 10.0)
            confiance = round((retard_ratio * 0.7) + (fiabilite * 0.3), 3)

            ingredient = db.query(Ingredient).filter(Ingredient.nom.ilike(nom)).first()

            predictions.append(
                {
                    "article_nom": nom,
                    "categorie": h.categorie,
                    "rayon_magasin": h.rayon_magasin,
                    "frequence_jours": frequence,
                    "jours_depuis_dernier_achat": jours_depuis,
                    "retard_jours": max(0, jours_depuis - frequence),
                    "confiance": confiance,
                    "sur_liste_active": sur_liste,
                    "ingredient_id": ingredient.id if ingredient else None,
                    "quantite_suggeree": 1.0,
                    "unite_suggeree": ingredient.unite if ingredient else "pcs",
                }
            )

        predictions.sort(
            key=lambda item: (
                item["confiance"],
                item["retard_jours"],
                item["jours_depuis_dernier_achat"],
            ),
            reverse=True,
        )

        return predictions[: max(1, limite)]

    @avec_gestion_erreurs(default_return=False)
    @avec_session_db
    def enregistrer_feedback(
        self,
        article_nom: str,
        accepte: bool,
        *,
        db: Session | None = None,
    ) -> bool:
        """Met a jour le modele de frequence selon feedback utilisateur.

        - accepte=True  : renforce la prediction (dernier achat = maintenant)
        - accepte=False : espace la frequence pour reduire les faux positifs
        """
        if db is None:
            return False

        from src.core.models.courses import HistoriqueAchats

        hist = (
            db.query(HistoriqueAchats)
            .filter(HistoriqueAchats.article_nom.ilike(article_nom.strip()))
            .first()
        )
        if hist is None:
            return False

        now = datetime.now(UTC)
        freq = max(1, int(hist.frequence_jours or 7))

        if accepte:
            hist.nb_achats = int(hist.nb_achats or 0) + 1
            hist.derniere_achat = now
            # Stabiliser la frequence vers la valeur actuelle
            hist.frequence_jours = max(1, int((freq * 0.8) + 1))
        else:
            # Prediction refusee -> on espace la frequence
            hist.frequence_jours = max(2, int((freq * 1.2) + 1))

        db.commit()
        return True


@service_factory("prediction_courses", tags={"cuisine", "courses", "ia"})
def obtenir_service_prediction_courses() -> ServicePredictionCourses:
    """Factory singleton du service prediction courses."""
    return ServicePredictionCourses()


get_prediction_courses_service = obtenir_service_prediction_courses
