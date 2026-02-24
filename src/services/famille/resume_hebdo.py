"""
Service de résumé hebdomadaire IA.

Génère automatiquement un résumé de la semaine écoulée chaque lundi,
couvrant:
- Repas planifiés et réalisés
- Budget et dépenses
- Activités familiales
- Tâches d'entretien réalisées
- Métriques clés et recommandations

Usage:
    from src.services.famille.resume_hebdo import obtenir_service_resume_hebdo

    service = obtenir_service_resume_hebdo()
    resume = service.generer_resume_semaine_sync()
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from typing import Any

from pydantic import BaseModel, Field

from src.core.ai import ClientIA
from src.core.decorators import avec_cache, avec_gestion_erreurs
from src.services.core.base import BaseAIService
from src.services.core.registry import service_factory

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# SCHÉMAS PYDANTIC
# ═══════════════════════════════════════════════════════════


class ResumeRepas(BaseModel):
    """Résumé des repas de la semaine."""

    nb_repas_planifies: int = 0
    nb_repas_realises: int = 0
    recettes_populaires: list[str] = Field(default_factory=list)
    taux_realisation: float = 0.0
    commentaire: str = ""


class ResumeBudget(BaseModel):
    """Résumé du budget de la semaine."""

    total_depenses: float = 0.0
    top_categories: list[dict[str, Any]] = Field(default_factory=list)
    budget_restant: float | None = None
    tendance: str = "stable"  # "hausse", "baisse", "stable"
    commentaire: str = ""


class ResumeActivites(BaseModel):
    """Résumé des activités familiales."""

    nb_activites: int = 0
    activites_realisees: list[str] = Field(default_factory=list)
    temps_total_heures: float = 0.0
    commentaire: str = ""


class ResumeTaches(BaseModel):
    """Résumé des tâches d'entretien."""

    nb_taches_realisees: int = 0
    nb_taches_en_retard: int = 0
    prochaines_echeances: list[str] = Field(default_factory=list)
    commentaire: str = ""


class ResumeHebdomadaire(BaseModel):
    """Résumé hebdomadaire complet."""

    semaine: str = ""  # "2026-W08"
    date_debut: date | None = None
    date_fin: date | None = None
    repas: ResumeRepas = Field(default_factory=ResumeRepas)
    budget: ResumeBudget = Field(default_factory=ResumeBudget)
    activites: ResumeActivites = Field(default_factory=ResumeActivites)
    taches: ResumeTaches = Field(default_factory=ResumeTaches)
    resume_narratif: str = ""
    recommandations: list[str] = Field(default_factory=list)
    score_semaine: int = 0  # 0-100
    genere_le: datetime | None = None


# ═══════════════════════════════════════════════════════════
# SERVICE
# ═══════════════════════════════════════════════════════════


class ServiceResumeHebdo(BaseAIService):
    """
    Service de génération de résumés hebdomadaires IA.

    Hérite de BaseAIService pour bénéficier automatiquement de:
    - Rate limiting + cache sémantique
    - Circuit breaker
    - Parsing JSON robuste

    Collecte les données de la semaine écoulée et génère
    un résumé narratif avec recommandations via IA.
    """

    SYSTEM_PROMPT = """Tu es un assistant familial bienveillant et organisé.
Tu génères des résumés hebdomadaires pour une famille (Anne et Jules, 19 mois).

Ton style:
- Chaleureux mais concis
- Tu utilises des emojis pour structurer
- Tu donnes des recommandations pratiques
- Tu notes ce qui va bien ET ce qui peut être amélioré
- Tu adaptes tes conseils au contexte familial (enfant en bas âge)

Format du résumé en Markdown:
## 📊 Bilan de la Semaine {semaine}

### 🍽️ Repas
- {statistiques repas}

### 💰 Budget
- {statistiques budget}

### 🎯 Activités
- {statistiques activités}

### ✅ Tâches Maison
- {statistiques tâches}

### 💡 Recommandations
1. {recommandation 1}
2. {recommandation 2}
3. {recommandation 3}

### 🎯 Score de la semaine: {score}/100
"""

    def __init__(self, client: ClientIA | None = None):
        """Initialise le service de résumé hebdomadaire."""
        if client is None:
            try:
                from src.core.ai.client import obtenir_client_ia

                client = obtenir_client_ia()
            except Exception:
                client = None

        if client is not None:
            super().__init__(
                client=client,
                cache_prefix="resume_hebdo",
                default_ttl=86400,  # 24h cache
                default_temperature=0.7,
                service_name="resume_hebdo",
            )
        else:
            # Mode dégradé sans IA
            self.client = None
            self.cache_prefix = "resume_hebdo"
            self.service_name = "resume_hebdo"

    # ═══════════════════════════════════════════════════════════
    # COLLECTE DES DONNÉES
    # ═══════════════════════════════════════════════════════════

    @avec_gestion_erreurs(default_return={})
    def _collecter_donnees_repas(self, date_debut: date, date_fin: date) -> dict:
        """Collecte les données de repas de la semaine."""
        try:
            from src.services.cuisine.planning import obtenir_service_planning
            from src.services.cuisine.recettes import obtenir_service_recettes

            service_planning = obtenir_service_planning()
            service_recettes = obtenir_service_recettes()

            stats_planning = {}
            if service_planning:
                planning = service_planning.get_planning()
                if planning and planning.repas:
                    repas_semaine = [
                        r
                        for r in planning.repas
                        if hasattr(r, "date") and r.date and date_debut <= r.date <= date_fin
                    ]
                    stats_planning = {
                        "nb_planifies": len(planning.repas),
                        "nb_realises": len(
                            [r for r in repas_semaine if getattr(r, "realise", False)]
                        ),
                        "recettes": [
                            getattr(r, "recette_nom", "Inconnu") for r in repas_semaine[:5]
                        ],
                    }

            stats_recettes = {}
            if service_recettes:
                stats_recettes = service_recettes.get_stats() or {}

            return {**stats_planning, **stats_recettes}
        except Exception as e:
            logger.warning(f"Erreur collecte repas: {e}")
            return {}

    @avec_gestion_erreurs(default_return={})
    def _collecter_donnees_budget(self, date_debut: date, date_fin: date) -> dict:
        """Collecte les données de budget de la semaine."""
        try:
            from src.services.famille.budget import obtenir_service_budget

            service = obtenir_service_budget()
            if service is None:
                return {}

            depenses = service.get_depenses_periode(date_debut, date_fin)
            if not depenses:
                return {"total": 0, "categories": {}}

            # Agréger par catégorie
            par_categorie: dict[str, float] = {}
            total = 0.0
            for dep in depenses:
                montant = float(getattr(dep, "montant", 0))
                cat = getattr(dep, "categorie", "Autre")
                par_categorie[cat] = par_categorie.get(cat, 0) + montant
                total += montant

            return {
                "total": total,
                "categories": par_categorie,
                "nb_depenses": len(depenses),
            }
        except Exception as e:
            logger.warning(f"Erreur collecte budget: {e}")
            return {}

    @avec_gestion_erreurs(default_return={})
    def _collecter_donnees_activites(self, date_debut: date, date_fin: date) -> dict:
        """Collecte les données d'activités de la semaine."""
        try:
            from src.services.famille.activites import obtenir_service_activites

            service = obtenir_service_activites()
            if service is None:
                return {}

            activites = service.lister_par_periode(date_debut, date_fin)
            if not activites:
                return {"nb_activites": 0}

            return {
                "nb_activites": len(activites),
                "noms": [getattr(a, "nom", "Activité") for a in activites[:5]],
            }
        except Exception as e:
            logger.warning(f"Erreur collecte activités: {e}")
            return {}

    @avec_gestion_erreurs(default_return={})
    def _collecter_donnees_taches(self, date_debut: date, date_fin: date) -> dict:
        """Collecte les données de tâches d'entretien de la semaine."""
        try:
            from src.services.maison.entretien_service import obtenir_service_entretien

            service = obtenir_service_entretien()
            if service is None:
                return {}

            taches = service.get_taches_periode(date_debut, date_fin)
            return {
                "nb_realisees": len([t for t in taches if getattr(t, "fait", False)]),
                "nb_en_retard": len([t for t in taches if getattr(t, "en_retard", False)]),
            }
        except Exception as e:
            logger.warning(f"Erreur collecte tâches: {e}")
            return {}

    # ═══════════════════════════════════════════════════════════
    # GÉNÉRATION DU RÉSUMÉ
    # ═══════════════════════════════════════════════════════════

    def _calculer_dates_semaine(self, reference: date | None = None) -> tuple[date, date]:
        """Calcule les dates de début et fin de la semaine précédente."""
        ref = reference or date.today()
        # Lundi de cette semaine
        lundi_courant = ref - timedelta(days=ref.weekday())
        # Semaine précédente
        date_debut = lundi_courant - timedelta(days=7)
        date_fin = lundi_courant - timedelta(days=1)
        return date_debut, date_fin

    @avec_cache(ttl=86400)  # Cache 24h — un seul résumé par semaine
    def generer_resume_semaine_sync(
        self,
        reference: date | None = None,
    ) -> ResumeHebdomadaire:
        """
        Génère le résumé hebdomadaire complet (version synchrone).

        Collecte les données de toutes les sources et génère
        un résumé narratif via IA.

        Args:
            reference: Date de référence (défaut: aujourd'hui).
                       Le résumé couvre la semaine précédente.

        Returns:
            ResumeHebdomadaire complet
        """
        date_debut, date_fin = self._calculer_dates_semaine(reference)
        semaine_str = date_debut.strftime("%Y-W%W")

        # Collecter toutes les données
        donnees_repas = self._collecter_donnees_repas(date_debut, date_fin)
        donnees_budget = self._collecter_donnees_budget(date_debut, date_fin)
        donnees_activites = self._collecter_donnees_activites(date_debut, date_fin)
        donnees_taches = self._collecter_donnees_taches(date_debut, date_fin)

        # Construire le résumé structuré
        resume = ResumeHebdomadaire(
            semaine=semaine_str,
            date_debut=date_debut,
            date_fin=date_fin,
            repas=ResumeRepas(
                nb_repas_planifies=donnees_repas.get("nb_planifies", 0),
                nb_repas_realises=donnees_repas.get("nb_realises", 0),
                recettes_populaires=donnees_repas.get("recettes", []),
                taux_realisation=(
                    donnees_repas.get("nb_realises", 0)
                    / max(donnees_repas.get("nb_planifies", 1), 1)
                    * 100
                ),
            ),
            budget=ResumeBudget(
                total_depenses=donnees_budget.get("total", 0),
                top_categories=[
                    {"categorie": k, "montant": v}
                    for k, v in sorted(
                        donnees_budget.get("categories", {}).items(),
                        key=lambda x: x[1],
                        reverse=True,
                    )[:5]
                ],
            ),
            activites=ResumeActivites(
                nb_activites=donnees_activites.get("nb_activites", 0),
                activites_realisees=donnees_activites.get("noms", []),
            ),
            taches=ResumeTaches(
                nb_taches_realisees=donnees_taches.get("nb_realisees", 0),
                nb_taches_en_retard=donnees_taches.get("nb_en_retard", 0),
            ),
            genere_le=datetime.now(),
        )

        # Calculer le score de la semaine
        resume.score_semaine = self._calculer_score(resume)

        # Générer le résumé narratif via IA (si client disponible)
        if self.client is not None:
            try:
                resume_narratif = self._generer_narratif(resume)
                if resume_narratif:
                    resume.resume_narratif = resume_narratif
            except Exception as e:
                logger.warning(f"Erreur génération narrative IA: {e}")
                resume.resume_narratif = self._generer_narratif_fallback(resume)
        else:
            resume.resume_narratif = self._generer_narratif_fallback(resume)

        return resume

    def _calculer_score(self, resume: ResumeHebdomadaire) -> int:
        """Calcule un score sur 100 basé sur les métriques de la semaine."""
        score = 50  # Base

        # Repas (+/- 20 points)
        if resume.repas.taux_realisation >= 80:
            score += 20
        elif resume.repas.taux_realisation >= 50:
            score += 10
        elif resume.repas.nb_repas_planifies == 0:
            score -= 5

        # Tâches (+/- 15 points)
        if resume.taches.nb_taches_en_retard == 0:
            score += 15
        elif resume.taches.nb_taches_en_retard <= 2:
            score += 5
        else:
            score -= 10

        # Activités (+/- 15 points)
        if resume.activites.nb_activites >= 3:
            score += 15
        elif resume.activites.nb_activites >= 1:
            score += 8

        return max(0, min(100, score))

    def _generer_narratif(self, resume: ResumeHebdomadaire) -> str:
        """Génère le résumé narratif via IA."""
        prompt = f"""Génère un résumé hebdomadaire familial pour la semaine du {resume.date_debut} au {resume.date_fin}.

Données de la semaine:
- Repas: {resume.repas.nb_repas_planifies} planifiés, {resume.repas.nb_repas_realises} réalisés ({resume.repas.taux_realisation:.0f}%)
  Recettes: {", ".join(resume.repas.recettes_populaires) if resume.repas.recettes_populaires else "Aucune"}
- Budget: {resume.budget.total_depenses:.2f}€ dépensés
  Top catégories: {", ".join(f"{c['categorie']}: {c['montant']:.0f}€" for c in resume.budget.top_categories)}
- Activités: {resume.activites.nb_activites} activités ({", ".join(resume.activites.activites_realisees) if resume.activites.activites_realisees else "Aucune"})
- Tâches: {resume.taches.nb_taches_realisees} réalisées, {resume.taches.nb_taches_en_retard} en retard
- Score global: {resume.score_semaine}/100"""
        result = self.call_with_cache_sync(
            prompt=prompt,
            system_prompt=self.SYSTEM_PROMPT,
            temperature=0.7,
            max_tokens=1500,
        )

        return result or ""

    def _generer_narratif_fallback(self, resume: ResumeHebdomadaire) -> str:
        """Génère un résumé narratif sans IA (fallback)."""
        lines = [
            f"## 📊 Bilan de la Semaine ({resume.date_debut} → {resume.date_fin})",
            "",
            "### 🍽️ Repas",
            f"- {resume.repas.nb_repas_planifies} repas planifiés, "
            f"{resume.repas.nb_repas_realises} réalisés "
            f"({resume.repas.taux_realisation:.0f}%)",
        ]

        if resume.repas.recettes_populaires:
            lines.append(f"- Recettes: {', '.join(resume.repas.recettes_populaires)}")

        lines.extend(
            [
                "",
                "### 💰 Budget",
                f"- Total dépensé: **{resume.budget.total_depenses:.2f} €**",
            ]
        )

        if resume.budget.top_categories:
            for cat in resume.budget.top_categories[:3]:
                lines.append(f"  - {cat['categorie']}: {cat['montant']:.0f} €")

        lines.extend(
            [
                "",
                "### 🎯 Activités",
                f"- {resume.activites.nb_activites} activité(s) cette semaine",
            ]
        )

        lines.extend(
            [
                "",
                "### ✅ Tâches Maison",
                f"- {resume.taches.nb_taches_realisees} tâche(s) réalisée(s)",
                f"- {resume.taches.nb_taches_en_retard} tâche(s) en retard",
            ]
        )

        lines.extend(
            [
                "",
                f"### 🎯 Score de la semaine: **{resume.score_semaine}/100**",
            ]
        )

        return "\n".join(lines)

    def est_jour_resume(self) -> bool:
        """Vérifie si aujourd'hui est le jour de génération du résumé (lundi)."""
        return date.today().weekday() == 0  # Lundi = 0


# ═══════════════════════════════════════════════════════════
# FACTORY
# ═══════════════════════════════════════════════════════════


@service_factory("resume_hebdo", tags={"famille", "ia"})
def obtenir_service_resume_hebdo() -> ServiceResumeHebdo:
    """Factory pour le service de résumé hebdomadaire."""
    return ServiceResumeHebdo()


__all__ = [
    "ServiceResumeHebdo",
    "ResumeHebdomadaire",
    "obtenir_service_resume_hebdo",
]
