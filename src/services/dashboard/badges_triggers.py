"""
Triggers de badges gamification sport + nutrition.

Évalue les conditions d'obtention des badges et persiste
les badges débloqués dans badges_utilisateurs.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import date, timedelta
from typing import Any

from sqlalchemy import func
from sqlalchemy.orm import Session

from src.core.decorators import avec_gestion_erreurs, avec_session_db
from src.services.core.registry import service_factory

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# CATALOGUE DE BADGES
# ═══════════════════════════════════════════════════════════


@dataclass(frozen=True)
class DefinitionBadge:
    """Définition d'un badge gamification."""

    badge_type: str
    badge_label: str
    categorie: str  # "sport" | "nutrition"
    emoji: str
    description: str
    seuil: int | float
    unite: str


# ─── Badges Sport ────────────────────────────────────────────────
BADGES_SPORT: list[DefinitionBadge] = [
    DefinitionBadge(
        badge_type="marcheur_regulier",
        badge_label="Marcheur régulier",
        categorie="sport",
        emoji="🚶",
        description="Atteindre 8 000 pas/jour pendant 7 jours consécutifs",
        seuil=7,
        unite="jours consécutifs ≥ 8 000 pas",
    ),
    DefinitionBadge(
        badge_type="marathonien",
        badge_label="Marathonien",
        categorie="sport",
        emoji="🏃",
        description="Atteindre 12 000 pas/jour pendant 7 jours consécutifs",
        seuil=7,
        unite="jours consécutifs ≥ 12 000 pas",
    ),
    DefinitionBadge(
        badge_type="sportif_hebdo",
        badge_label="Sportif assidu",
        categorie="sport",
        emoji="💪",
        description="Réaliser au moins 4 sessions de sport dans la semaine",
        seuil=4,
        unite="sessions/semaine",
    ),
    DefinitionBadge(
        badge_type="bruleur_calories",
        badge_label="Brûleur de calories",
        categorie="sport",
        emoji="🔥",
        description="Brûler au moins 2 500 calories actives dans la semaine",
        seuil=2500,
        unite="calories actives/semaine",
    ),
    DefinitionBadge(
        badge_type="athlete_complet",
        badge_label="Athlète complet",
        categorie="sport",
        emoji="🏅",
        description="Pratiquer au moins 3 types d'activités différentes dans la semaine",
        seuil=3,
        unite="types d'activités/semaine",
    ),
    DefinitionBadge(
        badge_type="bougeotte",
        badge_label="Bougeotte",
        categorie="sport",
        emoji="⚡",
        description="Obtenir 180+ points sport dans la semaine",
        seuil=180,
        unite="points sport",
    ),
]

# ─── Badges Nutrition ────────────────────────────────────────────
BADGES_NUTRITION: list[DefinitionBadge] = [
    DefinitionBadge(
        badge_type="planning_equilibre",
        badge_label="Planning équilibré",
        categorie="nutrition",
        emoji="🥗",
        description="Planning repas couvrant 5 jours ou plus dans la semaine",
        seuil=5,
        unite="jours avec repas planifiés",
    ),
    DefinitionBadge(
        badge_type="nutritionniste",
        badge_label="Nutritionniste",
        categorie="nutrition",
        emoji="🍎",
        description="Score bien-être nutritionnel ≥ 75 sur la semaine",
        seuil=75,
        unite="score bien-être",
    ),
    DefinitionBadge(
        badge_type="assiette_futee",
        badge_label="Assiette futée",
        categorie="nutrition",
        emoji="🧠",
        description="Obtenir 220+ points alimentation dans la semaine",
        seuil=220,
        unite="points alimentation",
    ),
    DefinitionBadge(
        badge_type="zero_gaspi",
        badge_label="Zéro gaspi",
        categorie="nutrition",
        emoji="♻️",
        description="Aucun article expiré dans la semaine (0 articles à risque)",
        seuil=0,
        unite="articles expirés",
    ),
    DefinitionBadge(
        badge_type="diversite_alimentaire",
        badge_label="Diversité alimentaire",
        categorie="nutrition",
        emoji="🌈",
        description="Utiliser au moins 5 catégories d'aliments différentes dans la semaine",
        seuil=5,
        unite="catégories d'aliments",
    ),
    DefinitionBadge(
        badge_type="anti_gaspi_champion",
        badge_label="Champion anti-gaspi",
        categorie="nutrition",
        emoji="🏆",
        description="Obtenir 170+ points anti-gaspi dans la semaine",
        seuil=170,
        unite="points anti-gaspi",
    ),
]

TOUS_LES_BADGES = BADGES_SPORT + BADGES_NUTRITION


def obtenir_catalogue_badges() -> list[dict[str, Any]]:
    """Retourne le catalogue complet des badges avec métadonnées."""
    return [
        {
            "badge_type": b.badge_type,
            "badge_label": b.badge_label,
            "categorie": b.categorie,
            "emoji": b.emoji,
            "description": b.description,
            "seuil": b.seuil,
            "unite": b.unite,
        }
        for b in TOUS_LES_BADGES
    ]


# ═══════════════════════════════════════════════════════════
# SERVICE DE TRIGGERS
# ═══════════════════════════════════════════════════════════


class BadgesTriggersService:
    """Évalue les conditions d'obtention de badges sport + nutrition."""

    @avec_gestion_erreurs(default_return=[])
    @avec_session_db
    def evaluer_et_attribuer(self, db: Session | None = None) -> list[dict[str, Any]]:
        """Évalue tous les triggers et attribue les badges mérités.

        Returns:
            Liste des badges nouvellement attribués.
        """
        if db is None:
            return []

        from src.core.models import BadgeUtilisateur, ProfilUtilisateur
        from src.core.models.users import ActiviteGarmin, ResumeQuotidienGarmin

        profils = db.query(ProfilUtilisateur).all()
        if not profils:
            return []

        aujourd_hui = date.today()
        debut_semaine = aujourd_hui - timedelta(days=6)

        # ─── Données Garmin (sport) ────────────────────────────
        resumes = (
            db.query(ResumeQuotidienGarmin)
            .filter(ResumeQuotidienGarmin.date >= debut_semaine)
            .order_by(ResumeQuotidienGarmin.date)
            .all()
        )
        activites = (
            db.query(ActiviteGarmin)
            .filter(ActiviteGarmin.date_debut >= debut_semaine)
            .all()
        )

        # ─── Données nutrition ─────────────────────────────────
        from src.core.models import ArticleInventaire
        from src.core.models.planning import Repas
        from src.services.dashboard.score_bienetre import obtenir_score_bien_etre_service

        articles_risque = int(
            db.query(func.count(ArticleInventaire.id))
            .filter(
                ArticleInventaire.date_peremption.isnot(None),
                ArticleInventaire.date_peremption >= aujourd_hui - timedelta(days=3),
                ArticleInventaire.date_peremption <= aujourd_hui + timedelta(days=3),
            )
            .scalar()
            or 0
        )

        jours_avec_repas = int(
            db.query(func.count(func.distinct(Repas.date_repas)))
            .filter(
                Repas.date_repas >= debut_semaine,
                Repas.date_repas <= aujourd_hui,
            )
            .scalar()
            or 0
        )

        score_bien_etre = obtenir_score_bien_etre_service().calculer_score() or {}
        score_global = int(score_bien_etre.get("score_global", 0))

        # Diversité alimentaire
        categories_aliments = set()
        repas_semaine = (
            db.query(Repas)
            .filter(
                Repas.date_repas >= debut_semaine,
                Repas.date_repas <= aujourd_hui,
            )
            .all()
        )
        for repas in repas_semaine:
            if repas.type_repas:
                categories_aliments.add(repas.type_repas)

        # ─── Calcul des métriques sport ────────────────────────
        total_pas = sum(r.pas for r in resumes)
        total_calories = sum(r.calories_actives for r in resumes)
        nb_sessions = len(activites)
        types_activites = {a.type_activite for a in activites if a.type_activite}
        points_sport = min(300, nb_sessions * 40 + total_calories // 20 + total_pas // 1000)
        points_alimentation = min(300, score_global * 3)
        points_anti_gaspi = max(0, 200 - articles_risque * 15)

        # Jours consécutifs avec ≥ 8000 pas
        jours_8000 = self._jours_consecutifs_pas(resumes, seuil=8000)
        jours_12000 = self._jours_consecutifs_pas(resumes, seuil=12000)

        # ─── Évaluation des triggers ──────────────────────────
        metriques = {
            "marcheur_regulier": jours_8000,
            "marathonien": jours_12000,
            "sportif_hebdo": nb_sessions,
            "bruleur_calories": total_calories,
            "athlete_complet": len(types_activites),
            "bougeotte": points_sport,
            "planning_equilibre": jours_avec_repas,
            "nutritionniste": score_global,
            "assiette_futee": points_alimentation,
            "zero_gaspi": articles_risque,  # inversé: 0 = badge obtenu
            "diversite_alimentaire": len(categories_aliments),
            "anti_gaspi_champion": points_anti_gaspi,
        }

        nouveaux_badges: list[dict[str, Any]] = []

        for profil in profils:
            for badge_def in TOUS_LES_BADGES:
                valeur = metriques.get(badge_def.badge_type, 0)

                # Logique inversée pour zero_gaspi (0 articles = succès)
                if badge_def.badge_type == "zero_gaspi":
                    badge_atteint = valeur <= badge_def.seuil
                else:
                    badge_atteint = valeur >= badge_def.seuil

                if not badge_atteint:
                    continue

                # Vérifier si déjà attribué aujourd'hui
                deja = (
                    db.query(BadgeUtilisateur)
                    .filter(
                        BadgeUtilisateur.user_id == profil.id,
                        BadgeUtilisateur.badge_type == badge_def.badge_type,
                        BadgeUtilisateur.acquis_le == aujourd_hui,
                    )
                    .first()
                )
                if deja:
                    continue

                db.add(
                    BadgeUtilisateur(
                        user_id=profil.id,
                        badge_type=badge_def.badge_type,
                        badge_label=badge_def.badge_label,
                        acquis_le=aujourd_hui,
                        meta={
                            "valeur": valeur,
                            "seuil": badge_def.seuil,
                            "emoji": badge_def.emoji,
                            "categorie": badge_def.categorie,
                        },
                    )
                )
                nouveaux_badges.append(
                    {
                        "user_id": profil.id,
                        "badge_type": badge_def.badge_type,
                        "badge_label": badge_def.badge_label,
                        "emoji": badge_def.emoji,
                        "categorie": badge_def.categorie,
                    }
                )

        if nouveaux_badges:
            db.commit()
            logger.info("Badges attribués: %d", len(nouveaux_badges))

        return nouveaux_badges

    @avec_gestion_erreurs(default_return=[])
    @avec_session_db
    def obtenir_badges_utilisateur(
        self, user_id: int, db: Session | None = None
    ) -> list[dict[str, Any]]:
        """Retourne les badges d'un utilisateur avec leur progression."""
        if db is None:
            return []

        from src.core.models import BadgeUtilisateur

        badges_obtenus = (
            db.query(BadgeUtilisateur)
            .filter(BadgeUtilisateur.user_id == user_id)
            .order_by(BadgeUtilisateur.acquis_le.desc())
            .all()
        )

        types_obtenus = {b.badge_type for b in badges_obtenus}

        resultat = []
        for badge_def in TOUS_LES_BADGES:
            obtenu = badge_def.badge_type in types_obtenus
            derniere_date = None
            nb_obtenu = 0

            for b in badges_obtenus:
                if b.badge_type == badge_def.badge_type:
                    nb_obtenu += 1
                    if derniere_date is None:
                        derniere_date = b.acquis_le

            resultat.append(
                {
                    "badge_type": badge_def.badge_type,
                    "badge_label": badge_def.badge_label,
                    "categorie": badge_def.categorie,
                    "emoji": badge_def.emoji,
                    "description": badge_def.description,
                    "seuil": badge_def.seuil,
                    "unite": badge_def.unite,
                    "obtenu": obtenu,
                    "nb_obtenu": nb_obtenu,
                    "derniere_date": str(derniere_date) if derniere_date else None,
                }
            )

        return resultat

    @avec_gestion_erreurs(default_return=[])
    @avec_session_db
    def obtenir_historique_points(
        self,
        user_id: int,
        nb_semaines: int = 8,
        db: Session | None = None,
    ) -> list[dict[str, Any]]:
        """Retourne l'historique des points sur N semaines."""
        if db is None:
            return []

        from src.core.models import PointsUtilisateur

        historique = (
            db.query(PointsUtilisateur)
            .filter(PointsUtilisateur.user_id == user_id)
            .order_by(PointsUtilisateur.semaine_debut.desc())
            .limit(nb_semaines)
            .all()
        )

        return [
            {
                "semaine_debut": str(h.semaine_debut),
                "points_sport": h.points_sport,
                "points_alimentation": h.points_alimentation,
                "points_anti_gaspi": h.points_anti_gaspi,
                "total_points": h.total_points,
                "details": h.details or {},
            }
            for h in reversed(historique)
        ]

    @staticmethod
    def _jours_consecutifs_pas(
        resumes: list,
        seuil: int,
    ) -> int:
        """Calcule le nombre max de jours consécutifs avec ≥ seuil pas."""
        if not resumes:
            return 0

        resumes_tries = sorted(resumes, key=lambda r: r.date)
        max_consecutifs = 0
        consecutifs = 0
        prev_date = None

        for r in resumes_tries:
            if r.pas >= seuil:
                if prev_date is not None and (r.date - prev_date).days == 1:
                    consecutifs += 1
                else:
                    consecutifs = 1
            else:
                consecutifs = 0

            max_consecutifs = max(max_consecutifs, consecutifs)
            prev_date = r.date

        return max_consecutifs


@service_factory("badges_triggers", tags={"gamification", "sport", "nutrition"})
def obtenir_badges_triggers_service() -> BadgesTriggersService:
    return BadgesTriggersService()


# ─── Alias rétrocompatibilité ─────────────────────────────────────
obtenir_badges_triggers_service = obtenir_badges_triggers_service
