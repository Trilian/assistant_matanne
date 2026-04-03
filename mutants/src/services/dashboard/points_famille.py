"""Gamification famille: points sport + alimentation + anti-gaspi."""

from __future__ import annotations

from datetime import date, timedelta
from typing import Any

from sqlalchemy import func
from sqlalchemy.orm import Session

from src.core.decorators import avec_gestion_erreurs, avec_session_db
from src.services.core.registry import service_factory
from typing import Annotated
from typing import Callable
from typing import ClassVar

MutantDict = Annotated[dict[str, Callable], "Mutant"] # type: ignore


def _mutmut_trampoline(orig, mutants, call_args, call_kwargs, self_arg = None): # type: ignore
    """Forward call to original or mutated function, depending on the environment"""
    import os # type: ignore
    mutant_under_test = os.environ['MUTANT_UNDER_TEST'] # type: ignore
    if mutant_under_test == 'fail': # type: ignore
        from mutmut.__main__ import MutmutProgrammaticFailException # type: ignore
        raise MutmutProgrammaticFailException('Failed programmatically')       # type: ignore
    elif mutant_under_test == 'stats': # type: ignore
        from mutmut.__main__ import record_trampoline_hit # type: ignore
        record_trampoline_hit(orig.__module__ + '.' + orig.__name__) # type: ignore
        # (for class methods, orig is bound and thus does not need the explicit self argument)
        result = orig(*call_args, **call_kwargs) # type: ignore
        return result # type: ignore
    prefix = orig.__module__ + '.' + orig.__name__ + '__mutmut_' # type: ignore
    if not mutant_under_test.startswith(prefix): # type: ignore
        result = orig(*call_args, **call_kwargs) # type: ignore
        return result # type: ignore
    mutant_name = mutant_under_test.rpartition('.')[-1] # type: ignore
    if self_arg is not None: # type: ignore
        # call to a class method where self is not bound
        result = mutants[mutant_name](self_arg, *call_args, **call_kwargs) # type: ignore
    else:
        result = mutants[mutant_name](*call_args, **call_kwargs) # type: ignore
    return result # type: ignore


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
        from src.services.dashboard.score_bienetre import get_score_bien_etre_service

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

        score_bien_etre = get_score_bien_etre_service().calculer_score() or {}
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
        args = []# type: ignore
        kwargs = {'db': db, 'semaine_debut': semaine_debut, 'points_sport': points_sport, 'points_alimentation': points_alimentation, 'points_anti_gaspi': points_anti_gaspi, 'total': total, 'badges': badges, 'details': details, 'profils': profils, 'points_model': points_model, 'badge_model': badge_model}# type: ignore
        return _mutmut_trampoline(object.__getattribute__(self, 'xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo__mutmut_orig'), object.__getattribute__(self, 'xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo__mutmut_mutants'), args, kwargs, self)

    def xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo__mutmut_orig(
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

    def xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo__mutmut_1(
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
        if profils:
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

    def xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo__mutmut_2(
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
            snapshot = None
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

    def xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo__mutmut_3(
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
                    None,
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

    def xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo__mutmut_4(
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
                    None,
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

    def xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo__mutmut_5(
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

    def xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo__mutmut_6(
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

    def xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo__mutmut_7(
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
                db.query(None)
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

    def xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo__mutmut_8(
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
                    points_model.user_id != profil.id,
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

    def xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo__mutmut_9(
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
                    points_model.semaine_debut != semaine_debut,
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

    def xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo__mutmut_10(
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
            if snapshot is not None:
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

    def xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo__mutmut_11(
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
                snapshot = None
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

    def xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo__mutmut_12(
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
                snapshot = points_model(user_id=None, semaine_debut=semaine_debut)
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

    def xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo__mutmut_13(
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
                snapshot = points_model(user_id=profil.id, semaine_debut=None)
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

    def xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo__mutmut_14(
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
                snapshot = points_model(semaine_debut=semaine_debut)
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

    def xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo__mutmut_15(
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
                snapshot = points_model(user_id=profil.id, )
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

    def xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo__mutmut_16(
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
                db.add(None)

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

    def xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo__mutmut_17(
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

            snapshot.points_sport = None
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

    def xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo__mutmut_18(
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
            snapshot.points_alimentation = None
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

    def xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo__mutmut_19(
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
            snapshot.points_anti_gaspi = None
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

    def xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo__mutmut_20(
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
            snapshot.total_points = None
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

    def xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo__mutmut_21(
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
            snapshot.details = None

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

    def xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo__mutmut_22(
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
                deja = None
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

    def xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo__mutmut_23(
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
                        None,
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

    def xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo__mutmut_24(
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
                        None,
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

    def xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo__mutmut_25(
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
                        None,
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

    def xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo__mutmut_26(
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

    def xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo__mutmut_27(
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

    def xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo__mutmut_28(
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

    def xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo__mutmut_29(
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
                    db.query(None)
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

    def xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo__mutmut_30(
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
                        badge_model.user_id != profil.id,
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

    def xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo__mutmut_31(
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
                        badge_model.badge_type != badge.lower().replace(" ", "_"),
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

    def xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo__mutmut_32(
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
                        badge_model.badge_type == badge.lower().replace(None, "_"),
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

    def xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo__mutmut_33(
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
                        badge_model.badge_type == badge.lower().replace(" ", None),
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

    def xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo__mutmut_34(
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
                        badge_model.badge_type == badge.lower().replace("_"),
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

    def xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo__mutmut_35(
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
                        badge_model.badge_type == badge.lower().replace(" ", ),
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

    def xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo__mutmut_36(
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
                        badge_model.badge_type == badge.upper().replace(" ", "_"),
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

    def xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo__mutmut_37(
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
                        badge_model.badge_type == badge.lower().replace("XX XX", "_"),
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

    def xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo__mutmut_38(
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
                        badge_model.badge_type == badge.lower().replace(" ", "XX_XX"),
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

    def xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo__mutmut_39(
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
                        badge_model.acquis_le != date.today(),
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

    def xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo__mutmut_40(
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
                if deja is not None:
                    db.add(
                        badge_model(
                            user_id=profil.id,
                            badge_type=badge.lower().replace(" ", "_"),
                            badge_label=badge,
                            acquis_le=date.today(),
                        )
                    )

        db.commit()

    def xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo__mutmut_41(
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
                        None
                    )

        db.commit()

    def xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo__mutmut_42(
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
                            user_id=None,
                            badge_type=badge.lower().replace(" ", "_"),
                            badge_label=badge,
                            acquis_le=date.today(),
                        )
                    )

        db.commit()

    def xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo__mutmut_43(
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
                            badge_type=None,
                            badge_label=badge,
                            acquis_le=date.today(),
                        )
                    )

        db.commit()

    def xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo__mutmut_44(
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
                            badge_label=None,
                            acquis_le=date.today(),
                        )
                    )

        db.commit()

    def xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo__mutmut_45(
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
                            acquis_le=None,
                        )
                    )

        db.commit()

    def xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo__mutmut_46(
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
                            badge_type=badge.lower().replace(" ", "_"),
                            badge_label=badge,
                            acquis_le=date.today(),
                        )
                    )

        db.commit()

    def xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo__mutmut_47(
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
                            badge_label=badge,
                            acquis_le=date.today(),
                        )
                    )

        db.commit()

    def xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo__mutmut_48(
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
                            acquis_le=date.today(),
                        )
                    )

        db.commit()

    def xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo__mutmut_49(
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
                            )
                    )

        db.commit()

    def xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo__mutmut_50(
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
                            badge_type=badge.lower().replace(None, "_"),
                            badge_label=badge,
                            acquis_le=date.today(),
                        )
                    )

        db.commit()

    def xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo__mutmut_51(
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
                            badge_type=badge.lower().replace(" ", None),
                            badge_label=badge,
                            acquis_le=date.today(),
                        )
                    )

        db.commit()

    def xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo__mutmut_52(
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
                            badge_type=badge.lower().replace("_"),
                            badge_label=badge,
                            acquis_le=date.today(),
                        )
                    )

        db.commit()

    def xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo__mutmut_53(
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
                            badge_type=badge.lower().replace(" ", ),
                            badge_label=badge,
                            acquis_le=date.today(),
                        )
                    )

        db.commit()

    def xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo__mutmut_54(
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
                            badge_type=badge.upper().replace(" ", "_"),
                            badge_label=badge,
                            acquis_le=date.today(),
                        )
                    )

        db.commit()

    def xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo__mutmut_55(
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
                            badge_type=badge.lower().replace("XX XX", "_"),
                            badge_label=badge,
                            acquis_le=date.today(),
                        )
                    )

        db.commit()

    def xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo__mutmut_56(
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
                            badge_type=badge.lower().replace(" ", "XX_XX"),
                            badge_label=badge,
                            acquis_le=date.today(),
                        )
                    )

        db.commit()
    
    xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo__mutmut_mutants : ClassVar[MutantDict] = { # type: ignore
    'xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo__mutmut_1': xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo__mutmut_1, 
        'xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo__mutmut_2': xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo__mutmut_2, 
        'xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo__mutmut_3': xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo__mutmut_3, 
        'xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo__mutmut_4': xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo__mutmut_4, 
        'xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo__mutmut_5': xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo__mutmut_5, 
        'xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo__mutmut_6': xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo__mutmut_6, 
        'xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo__mutmut_7': xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo__mutmut_7, 
        'xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo__mutmut_8': xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo__mutmut_8, 
        'xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo__mutmut_9': xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo__mutmut_9, 
        'xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo__mutmut_10': xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo__mutmut_10, 
        'xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo__mutmut_11': xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo__mutmut_11, 
        'xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo__mutmut_12': xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo__mutmut_12, 
        'xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo__mutmut_13': xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo__mutmut_13, 
        'xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo__mutmut_14': xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo__mutmut_14, 
        'xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo__mutmut_15': xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo__mutmut_15, 
        'xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo__mutmut_16': xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo__mutmut_16, 
        'xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo__mutmut_17': xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo__mutmut_17, 
        'xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo__mutmut_18': xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo__mutmut_18, 
        'xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo__mutmut_19': xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo__mutmut_19, 
        'xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo__mutmut_20': xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo__mutmut_20, 
        'xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo__mutmut_21': xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo__mutmut_21, 
        'xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo__mutmut_22': xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo__mutmut_22, 
        'xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo__mutmut_23': xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo__mutmut_23, 
        'xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo__mutmut_24': xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo__mutmut_24, 
        'xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo__mutmut_25': xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo__mutmut_25, 
        'xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo__mutmut_26': xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo__mutmut_26, 
        'xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo__mutmut_27': xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo__mutmut_27, 
        'xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo__mutmut_28': xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo__mutmut_28, 
        'xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo__mutmut_29': xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo__mutmut_29, 
        'xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo__mutmut_30': xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo__mutmut_30, 
        'xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo__mutmut_31': xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo__mutmut_31, 
        'xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo__mutmut_32': xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo__mutmut_32, 
        'xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo__mutmut_33': xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo__mutmut_33, 
        'xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo__mutmut_34': xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo__mutmut_34, 
        'xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo__mutmut_35': xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo__mutmut_35, 
        'xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo__mutmut_36': xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo__mutmut_36, 
        'xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo__mutmut_37': xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo__mutmut_37, 
        'xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo__mutmut_38': xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo__mutmut_38, 
        'xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo__mutmut_39': xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo__mutmut_39, 
        'xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo__mutmut_40': xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo__mutmut_40, 
        'xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo__mutmut_41': xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo__mutmut_41, 
        'xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo__mutmut_42': xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo__mutmut_42, 
        'xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo__mutmut_43': xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo__mutmut_43, 
        'xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo__mutmut_44': xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo__mutmut_44, 
        'xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo__mutmut_45': xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo__mutmut_45, 
        'xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo__mutmut_46': xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo__mutmut_46, 
        'xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo__mutmut_47': xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo__mutmut_47, 
        'xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo__mutmut_48': xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo__mutmut_48, 
        'xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo__mutmut_49': xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo__mutmut_49, 
        'xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo__mutmut_50': xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo__mutmut_50, 
        'xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo__mutmut_51': xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo__mutmut_51, 
        'xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo__mutmut_52': xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo__mutmut_52, 
        'xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo__mutmut_53': xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo__mutmut_53, 
        'xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo__mutmut_54': xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo__mutmut_54, 
        'xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo__mutmut_55': xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo__mutmut_55, 
        'xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo__mutmut_56': xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo__mutmut_56
    }
    xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo__mutmut_orig.__name__ = 'xǁPointsFamilleServiceǁ_sauvegarder_points_hebdo'


@service_factory("points_famille", tags={"dashboard", "gamification", "famille"})
def obtenir_points_famille_service() -> PointsFamilleService:
    return PointsFamilleService()


# ─── Aliases rétrocompatibilité  ───────────────────────────────
get_points_famille_service = obtenir_points_famille_service  # alias rétrocompatibilité 
