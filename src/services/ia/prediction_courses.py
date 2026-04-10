"""
Service IA — Prédiction intelligente de courses.

Analyse l'historique des achats pour pré-remplir la prochaine liste de courses
basée sur les fréquences d'achat détectées (B4.1 / B5.4 / IA1).
"""

import logging
from datetime import date, timedelta

from sqlalchemy import func
from sqlalchemy.orm import Session

from src.core.decorators import avec_gestion_erreurs, avec_session_db
from src.services.core.registry import service_factory

logger = logging.getLogger(__name__)


class PredictionCoursesService:
    """Service de prédiction de courses basé sur l'historique d'achats."""

    @avec_gestion_erreurs(default_return=[])
    @avec_session_db
    def predire_prochaine_liste(self, limite: int = 30, db: Session | None = None) -> list[dict]:
        """Prédit les articles à acheter en analysant la fréquence d'achat.

        Algorithme :
        1. Récupère l'historique des achats avec fréquence
        2. Calcule la prochaine date estimée d'achat
        3. Retourne les articles dont la date estimée tombe cette semaine

        Returns:
            Liste de dicts {nom, categorie, rayon, frequence_jours, dernier_achat, confiance}
        """
        from src.core.models.courses import HistoriqueAchats

        aujourd_hui = date.today()
        seuil_semaine = aujourd_hui + timedelta(days=7)

        # Articles avec fréquence connue
        historique = (
            db.query(HistoriqueAchats)
            .filter(
                HistoriqueAchats.frequence_jours.isnot(None),
                HistoriqueAchats.frequence_jours > 0,
                HistoriqueAchats.nb_achats >= 2,  # Au moins 2 achats pour être fiable
            )
            .order_by(HistoriqueAchats.nb_achats.desc())
            .all()
        )

        predictions = []
        for h in historique:
            if not h.derniere_achat or not h.frequence_jours:
                continue

            derniere = (
                h.derniere_achat.date() if hasattr(h.derniere_achat, "date") else h.derniere_achat
            )
            prochaine_date_estimee = derniere + timedelta(days=h.frequence_jours)

            # Article à acheter cette semaine ou déjà en retard
            if prochaine_date_estimee <= seuil_semaine:
                jours_retard = (aujourd_hui - prochaine_date_estimee).days
                confiance = min(0.95, 0.5 + (h.nb_achats * 0.05))

                predictions.append(
                    {
                        "nom": h.article_nom,
                        "categorie": h.categorie or "Autre",
                        "rayon": h.rayon_magasin or "Autre",
                        "frequence_jours": h.frequence_jours,
                        "dernier_achat": str(derniere),
                        "prochaine_date_estimee": str(prochaine_date_estimee),
                        "jours_retard": max(0, jours_retard),
                        "confiance": round(confiance, 2),
                        "nb_achats": h.nb_achats,
                    }
                )

        # Trier par confiance décroissante puis retard
        predictions.sort(key=lambda x: (-x["confiance"], -x["jours_retard"]))
        return predictions[:limite]

    @avec_gestion_erreurs(default_return={})
    @avec_session_db
    def analyser_habitudes(self, db: Session | None = None) -> dict:
        """Analyse les habitudes d'achat et retourne des statistiques.

        Returns:
            Dict avec nb_articles_suivis, freq_moyenne, top_categories
        """
        from src.core.models.courses import HistoriqueAchats

        total = db.query(func.count(HistoriqueAchats.id)).scalar() or 0
        avec_frequence = (
            db.query(func.count(HistoriqueAchats.id))
            .filter(HistoriqueAchats.frequence_jours.isnot(None))
            .scalar()
            or 0
        )
        freq_moyenne = (
            db.query(func.avg(HistoriqueAchats.frequence_jours))
            .filter(HistoriqueAchats.frequence_jours.isnot(None))
            .scalar()
        )

        # Top catégories
        top_categories = (
            db.query(
                HistoriqueAchats.categorie,
                func.count(HistoriqueAchats.id).label("nb"),
            )
            .filter(HistoriqueAchats.categorie.isnot(None))
            .group_by(HistoriqueAchats.categorie)
            .order_by(func.count(HistoriqueAchats.id).desc())
            .limit(10)
            .all()
        )

        return {
            "nb_articles_suivis": total,
            "nb_avec_frequence": avec_frequence,
            "frequence_moyenne_jours": round(float(freq_moyenne), 1) if freq_moyenne else None,
            "top_categories": [{"categorie": cat, "nb_articles": nb} for cat, nb in top_categories],
        }

    @avec_gestion_erreurs(default_return=None)
    @avec_session_db
    def enregistrer_achat(
        self,
        article_nom: str,
        categorie: str | None = None,
        rayon: str | None = None,
        db: Session | None = None,
    ) -> dict | None:
        """Enregistre un achat et met à jour la fréquence d'achat.

        Returns:
            Dict avec les infos mises à jour
        """
        from datetime import UTC, datetime

        from src.core.models.courses import HistoriqueAchats

        existant = (
            db.query(HistoriqueAchats).filter(HistoriqueAchats.article_nom == article_nom).first()
        )

        maintenant = datetime.now(UTC)

        if existant:
            # Calculer la fréquence mise à jour
            if existant.derniere_achat:
                jours_depuis = (maintenant - existant.derniere_achat).days
                if existant.frequence_jours:
                    # Moyenne pondérée (70% ancienne, 30% nouvelle)
                    existant.frequence_jours = round(
                        existant.frequence_jours * 0.7 + jours_depuis * 0.3
                    )
                else:
                    existant.frequence_jours = jours_depuis

            existant.derniere_achat = maintenant
            existant.nb_achats += 1
            if categorie:
                existant.categorie = categorie
            if rayon:
                existant.rayon_magasin = rayon
            db.commit()

            return {
                "article": article_nom,
                "nb_achats": existant.nb_achats,
                "frequence_jours": existant.frequence_jours,
            }
        else:
            nouvel_historique = HistoriqueAchats(
                article_nom=article_nom,
                categorie=categorie,
                rayon_magasin=rayon,
                derniere_achat=maintenant,
                nb_achats=1,
            )
            db.add(nouvel_historique)
            db.commit()

            return {
                "article": article_nom,
                "nb_achats": 1,
                "frequence_jours": None,
            }


# ═══════════════════════════════════════════════════════════
# FACTORY
# ═══════════════════════════════════════════════════════════


@service_factory("prediction_courses", tags={"courses", "ia"})
def obtenir_service_prediction_courses() -> PredictionCoursesService:
    """Factory singleton pour le service de prédiction de courses."""
    return PredictionCoursesService()
