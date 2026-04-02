"""Service de prediction de courses a partir de l'historique d'achats (IA2).

 Prediction courses intelligente — historique + IA Mistral
pour pre-remplir la liste de courses avec des suggestions contextuelles.
"""

from __future__ import annotations

import logging
from datetime import UTC, date, datetime
from typing import Any

from sqlalchemy.orm import Session

from src.core.decorators import avec_gestion_erreurs, avec_session_db
from src.services.core.registry import service_factory

logger = logging.getLogger(__name__)


class ServicePredictionCourses:
    """Predictions d'articles recurrents avec score de confiance."""

    def _calculer_boost_contexte(
        self,
        article_nom: str,
        categorie: str | None,
        now: datetime,
        evenements: list[str] | None,
        nb_invites: int,
    ) -> tuple[float, float, list[str]]:
        """Retourne (boost_confiance, multiplicateur_quantite, raisons)."""
        nom = (article_nom or "").lower()
        cat = (categorie or "").lower()
        raisons: list[str] = []
        boost = 0.0
        multiplicateur_quantite = 1.0

        # Saisonnalite simple (signal faible)
        mois = now.month
        hiver = {11, 12, 1, 2}
        ete = {6, 7, 8}
        if mois in hiver and any(k in nom or k in cat for k in ["soupe", "potage", "raclette", "fondue"]):
            boost += 0.08
            raisons.append("saisonnalite_hiver")
        if mois in ete and any(k in nom or k in cat for k in ["salade", "glace", "barbecue", "grillade"]):
            boost += 0.08
            raisons.append("saisonnalite_ete")

        # Evenements declares (anniversaire, fete, invites...)
        for ev in (evenements or []):
            ev_l = ev.lower()
            if any(k in ev_l for k in ["anniversaire", "fete", "soir", "invite", "apero", "barbecue"]):
                boost += 0.06
                raisons.append("evenement_festif")
                break

        # Nombre d'invites impacte surtout la quantite suggeree
        if nb_invites > 0:
            multiplicateur_quantite += min(1.0, nb_invites * 0.15)
            boost += min(0.1, nb_invites * 0.02)
            raisons.append("invites")

        return boost, multiplicateur_quantite, raisons

    @avec_gestion_erreurs(default_return=[])
    @avec_session_db
    def predire_articles(
        self,
        limite: int = 25,
        inclure_deja_sur_liste: bool = False,
        evenements: list[str] | None = None,
        nb_invites: int = 0,
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

            boost_contexte, multiplicateur_quantite, raisons_contexte = self._calculer_boost_contexte(
                article_nom=nom,
                categorie=h.categorie,
                now=now,
                evenements=evenements,
                nb_invites=nb_invites,
            )

            confiance_contextualisee = round(min(1.0, confiance + boost_contexte), 3)
            quantite_suggeree = round(max(1.0, multiplicateur_quantite), 1)

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
                    "confiance_contextualisee": confiance_contextualisee,
                    "sur_liste_active": sur_liste,
                    "ingredient_id": ingredient.id if ingredient else None,
                    "quantite_suggeree": quantite_suggeree,
                    "unite_suggeree": ingredient.unite if ingredient else "pcs",
                    "contexte_applique": {
                        "nb_invites": nb_invites,
                        "evenements": evenements or [],
                        "raisons": raisons_contexte,
                    },
                }
            )

        predictions.sort(
            key=lambda item: (
                item["confiance_contextualisee"],
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

    @avec_gestion_erreurs(default_return=[])
    @avec_session_db
    def predire_avec_ia(
        self,
        limite: int = 10,
        contexte_planning: str | None = None,
        *,
        db: Session | None = None,
    ) -> list[dict[str, Any]]:
        """Utilise Mistral pour enrichir les predictions avec le contexte du planning.

        Combine l'historique d'achats avec le planning de la semaine
        pour proposer des articles pertinents manquants.
        """
        if db is None:
            return []

        from src.core.models.courses import HistoriqueAchats

        historiques = (
            db.query(HistoriqueAchats)
            .filter(HistoriqueAchats.nb_achats >= 3)
            .order_by(HistoriqueAchats.nb_achats.desc())
            .limit(50)
            .all()
        )

        if not historiques:
            return []

        articles_frequents = [
            f"- {h.article_nom} (catég: {h.categorie or 'N/A'}, "
            f"freq: {h.frequence_jours or '?'}j, "
            f"x{h.nb_achats} achats)"
            for h in historiques
        ]

        # Récupérer le planning de la semaine si contexte non fourni
        if not contexte_planning:
            try:
                from src.core.models.planning import Repas
                from sqlalchemy.orm import joinedload

                aujourd_hui = date.today()
                fin_semaine = date.fromordinal(
                    aujourd_hui.toordinal() + (6 - aujourd_hui.weekday())
                )
                repas = (
                    db.query(Repas)
                    .options(joinedload(Repas.recette))
                    .filter(
                        Repas.date_repas >= aujourd_hui,
                        Repas.date_repas <= fin_semaine,
                    )
                    .all()
                )
                if repas:
                    contexte_planning = "Repas prévus cette semaine:\n" + "\n".join(
                        f"- {r.date_repas} {r.type_repas}: {r.recette.nom if r.recette else 'N/A'}"
                        for r in repas
                    )
            except Exception:
                logger.debug("Impossible de charger le planning pour les prédictions IA")

        prompt = (
            "Voici les articles les plus achetés par cette famille:\n"
            + "\n".join(articles_frequents[:30])
        )
        if contexte_planning:
            prompt += f"\n\n{contexte_planning}"

        prompt += (
            f"\n\nSuggère les {limite} articles les plus susceptibles de manquer "
            "dans leurs placards. Retourne un JSON array avec: "
            '{"nom": str, "raison": str, "priorite": "haute"|"moyenne"|"basse"}'
        )

        try:
            from src.core.ai import obtenir_client_ia

            client = obtenir_client_ia()
            reponse = client.appeler(
                prompt=prompt,
                system_prompt=(
                    "Tu es un assistant courses familial. Tu analyses les habitudes "
                    "d'achat et le planning de repas pour proposer les articles qui "
                    "manquent probablement. Sois pratique et concis."
                ),
                temperature=0.5,
                max_tokens=800,
            )

            import json
            suggestions_brutes = json.loads(
                reponse.strip().removeprefix("```json").removesuffix("```").strip()
            )

            return [
                {
                    "article_nom": s.get("nom", ""),
                    "raison": s.get("raison", ""),
                    "priorite": s.get("priorite", "moyenne"),
                    "source": "ia_mistral",
                }
                for s in suggestions_brutes
                if s.get("nom")
            ][:limite]
        except Exception:
            logger.debug("Prédiction IA indisponible, fallback sur historique seul")
            return []

    @avec_gestion_erreurs(default_return=[])
    def predire_complet(
        self,
        limite: int = 20,
        evenements: list[str] | None = None,
        nb_invites: int = 0,
    ) -> list[dict[str, Any]]:
        """Combine predictions historique + IA pour une liste complète."""
        predictions_historique = self.predire_articles(
            limite=limite,
            evenements=evenements,
            nb_invites=nb_invites,
        )

        predictions_ia = self.predire_avec_ia(limite=max(5, limite // 2))

        # Dédoublonner par nom d'article
        noms_vus = {p["article_nom"].lower() for p in predictions_historique}
        for p_ia in predictions_ia:
            if p_ia["article_nom"].lower() not in noms_vus:
                predictions_historique.append({
                    **p_ia,
                    "confiance": 0.5,
                    "confiance_contextualisee": 0.55,
                    "frequence_jours": 0,
                    "jours_depuis_dernier_achat": 0,
                    "retard_jours": 0,
                    "sur_liste_active": False,
                    "ingredient_id": None,
                    "quantite_suggeree": 1.0,
                    "unite_suggeree": "pcs",
                    "contexte_applique": {
                        "nb_invites": nb_invites,
                        "evenements": evenements or [],
                        "raisons": [p_ia.get("raison", "suggestion_ia")],
                    },
                })
                noms_vus.add(p_ia["article_nom"].lower())

        return predictions_historique[:limite]


@service_factory("prediction_courses", tags={"cuisine", "courses", "ia"})
def obtenir_service_prediction_courses() -> ServicePredictionCourses:
    """Factory singleton du service prediction courses."""
    return ServicePredictionCourses()


