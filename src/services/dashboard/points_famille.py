"""Gamification famille: points sport + alimentation + anti-gaspi."""

from __future__ import annotations

from datetime import date, timedelta
from typing import Any

from sqlalchemy import func
from sqlalchemy.orm import Session

from src.core.decorators import avec_gestion_erreurs, avec_session_db
from src.services.core.registry import service_factory


class PointsFamilleService:
    """Calcule des points famille consolidés pour le dashboard."""

    @avec_gestion_erreurs(default_return={})
    @avec_session_db
    def calculer_points(self, db: Session | None = None) -> dict[str, Any]:
        if db is None:
            return {}

        from src.core.models import ArticleInventaire
        from src.core.models import BadgeUtilisateur, PointsUtilisateur, ProfilUtilisateur
        from src.core.models.users import ActiviteGarmin, ResumeQuotidienGarmin
        from src.services.dashboard.score_bienetre import obtenir_score_bien_etre_service

        aujourd_hui = date.today()
        debut = aujourd_hui - timedelta(days=6)

        activites = (
            db.query(ActiviteGarmin)
            .filter(ActiviteGarmin.date_debut >= debut)
            .all()
        )
        resumes = (
            db.query(ResumeQuotidienGarmin)
            .filter(ResumeQuotidienGarmin.date >= debut)
            .all()
        )
        articles_risque = (
            db.query(func.count(ArticleInventaire.id))
            .filter(
                ArticleInventaire.date_peremption.isnot(None),
                ArticleInventaire.date_peremption >= aujourd_hui - timedelta(days=3),
                ArticleInventaire.date_peremption <= aujourd_hui + timedelta(days=3),
            )
            .scalar()
            or 0
        )

        total_pas = sum(item.pas for item in resumes)
        total_calories = sum(item.calories_actives for item in resumes)
        points_sport = min(300, len(activites) * 40 + total_calories // 20 + total_pas // 1000)

        score_bien_etre = obtenir_score_bien_etre_service().calculer_score() or {}
        score_global = int(score_bien_etre.get("score_global", 0))
        points_alimentation = min(300, score_global * 3)
        points_anti_gaspi = max(0, 200 - int(articles_risque) * 15)

        total = points_sport + points_alimentation + points_anti_gaspi
        badges: list[str] = []
        if points_sport >= 180:
            badges.append("Bougeotte")
        if points_alimentation >= 220:
            badges.append("Assiette futée")
        if points_anti_gaspi >= 170:
            badges.append("Zéro gaspi")

        # LT-02: persister un snapshot hebdomadaire par utilisateur.
        self._sauvegarder_points_hebdo(
            db=db,
            semaine_debut=debut,
            points_sport=int(points_sport),
            points_alimentation=int(points_alimentation),
            points_anti_gaspi=int(points_anti_gaspi),
            total=int(total),
            badges=badges,
            details={
                "activites_garmin": len(activites),
                "total_pas": total_pas,
                "total_calories": total_calories,
                "score_bien_etre": score_global,
                "articles_a_risque": int(articles_risque),
            },
            profils=db.query(ProfilUtilisateur).all(),
            points_model=PointsUtilisateur,
            badge_model=BadgeUtilisateur,
        )

        return {
            "total_points": total,
            "sport": points_sport,
            "alimentation": points_alimentation,
            "anti_gaspi": points_anti_gaspi,
            "badges": badges,
            "details": {
                "activites_garmin": len(activites),
                "total_pas": total_pas,
                "total_calories": total_calories,
                "score_bien_etre": score_global,
                "articles_a_risque": int(articles_risque),
            },
        }

    def _sauvegarder_points_hebdo(
        self,
        *,
        db: Session,
        semaine_debut: date,
        points_sport: int,
        points_alimentation: int,
        points_anti_gaspi: int,
        total: int,
        badges: list[str],
        details: dict[str, Any],
        profils: list,
        points_model,
        badge_model,
    ) -> None:
        if not profils:
            return

        for profil in profils:
            snapshot = (
                db.query(points_model)
                .filter(
                    points_model.user_id == profil.id,
                    points_model.semaine_debut == semaine_debut,
                )
                .first()
            )
            if snapshot is None:
                snapshot = points_model(user_id=profil.id, semaine_debut=semaine_debut)
                db.add(snapshot)

            snapshot.points_sport = points_sport
            snapshot.points_alimentation = points_alimentation
            snapshot.points_anti_gaspi = points_anti_gaspi
            snapshot.total_points = total
            snapshot.details = details

            for badge in badges:
                deja = (
                    db.query(badge_model)
                    .filter(
                        badge_model.user_id == profil.id,
                        badge_model.badge_type == badge.lower().replace(" ", "_"),
                        badge_model.acquis_le == date.today(),
                    )
                    .first()
                )
                if deja is None:
                    db.add(
                        badge_model(
                            user_id=profil.id,
                            badge_type=badge.lower().replace(" ", "_"),
                            badge_label=badge,
                            acquis_le=date.today(),
                        )
                    )

        db.commit()


@service_factory("points_famille", tags={"dashboard", "gamification", "famille"})
def obtenir_points_famille_service() -> PointsFamilleService:
    return PointsFamilleService()


# ─── Aliases rétrocompatibilité  ───────────────────────────────
obtenir_points_famille_service = obtenir_points_famille_service  # alias rétrocompatibilité 
