"""
B.7 — Simplification flux utilisateur.

Endpoints et services pour :
- B7.1: Flux cuisine "3 clics" (valider planning → cocher courses → checkout auto)
- B7.2: Digest famille quotidien
- B7.3: Flux maison simplifié (notification → fiche → marquer fait)
- B7.5: Feedback fin de semaine
"""

import logging
from datetime import date, timedelta

from src.core.db import obtenir_contexte_db
from src.core.decorators import avec_gestion_erreurs

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# B7.1: FLUX CUISINE 3 CLICS
# ═══════════════════════════════════════════════════════════


@avec_gestion_erreurs(default_return={})
def flux_cuisine_3_clics(planning_id: int | None = None) -> dict:
    """Flux simplifié : récupère l'état actuel du flux cuisine.

    Retourne les étapes restantes et les actions possibles pour
    simplifier le parcours planning → courses → checkout.

    Returns:
        {"etape_actuelle": str, "planning": {...}, "courses": {...}, "actions_suivantes": [...]}
    """
    from src.core.models.courses import ListeCourses
    from src.core.models.planning import Planning

    with obtenir_contexte_db() as session:
        aujourd_hui = date.today()
        lundi = aujourd_hui - timedelta(days=aujourd_hui.weekday())
        dimanche = lundi + timedelta(days=6)

        # Étape 1: Vérifier le planning
        planning = None
        if planning_id:
            planning = session.query(Planning).filter(Planning.id == planning_id).first()
        else:
            planning = (
                session.query(Planning)
                .filter(
                    Planning.semaine_debut >= lundi,
                    Planning.semaine_debut <= dimanche,
                    Planning.etat.in_(["brouillon", "valide", "actif"]),
                )
                .order_by(Planning.cree_le.desc())
                .first()
            )

        if not planning:
            return {
                "etape_actuelle": "creer_planning",
                "planning": None,
                "courses": None,
                "actions_suivantes": [
                    {"action": "generer_planning_ia", "label": "Générer un planning IA", "url": "/api/v1/suggestions/planning"},
                ],
            }

        if planning.etat == "brouillon":
            return {
                "etape_actuelle": "valider_planning",
                "planning": {
                    "id": planning.id,
                    "semaine": str(planning.semaine_debut),
                    "etat": planning.etat,
                },
                "courses": None,
                "actions_suivantes": [
                    {
                        "action": "valider_planning",
                        "label": "Valider le brouillon planning",
                        "url": f"/api/v1/planning/{planning.id}/valider",
                    },
                    {
                        "action": "regenerer_planning",
                        "label": "Régénérer le brouillon",
                        "url": f"/api/v1/planning/{planning.id}/regenerer",
                    },
                ],
            }

        # Étape 2: Vérifier la liste de courses
        liste = (
            session.query(ListeCourses)
            .filter(
                ListeCourses.etat.in_(["brouillon", "active"]),
            )
            .order_by(ListeCourses.cree_le.desc())
            .first()
        )

        if not liste:
            return {
                "etape_actuelle": "generer_courses",
                "planning": {
                    "id": planning.id,
                    "semaine": str(planning.semaine_debut),
                    "etat": planning.etat,
                },
                "courses": None,
                "actions_suivantes": [
                    {"action": "generer_courses", "label": "Générer la liste de courses", "url": f"/api/v1/courses/generer-depuis-planning/{planning.id}"},
                ],
            }

        if liste.etat == "brouillon":
            return {
                "etape_actuelle": "confirmer_courses",
                "planning": {
                    "id": planning.id,
                    "semaine": str(planning.semaine_debut),
                    "etat": planning.etat,
                },
                "courses": {
                    "id": liste.id,
                    "etat": liste.etat,
                    "articles": len(liste.articles or []),
                },
                "actions_suivantes": [
                    {
                        "action": "confirmer_courses",
                        "label": "Confirmer la liste de courses",
                        "url": f"/api/v1/courses/{liste.id}/confirmer",
                    },
                ],
            }

        # Étape 3: Vérifier l'état du checkout
        nb_articles = len(liste.articles) if hasattr(liste, 'articles') else 0
        nb_coches = sum(1 for a in (liste.articles or []) if a.achete) if hasattr(liste, 'articles') else 0

        if nb_coches < nb_articles:
            return {
                "etape_actuelle": "faire_courses",
                "planning": {"id": planning.id, "semaine": str(planning.semaine_debut)},
                "courses": {"id": liste.id, "articles": nb_articles, "coches": nb_coches, "progression": round(nb_coches / max(nb_articles, 1) * 100)},
                "actions_suivantes": [
                    {"action": "voir_liste", "label": "Ouvrir la liste de courses", "url": f"/cuisine/courses"},
                    {"action": "checkout_auto", "label": "Tout cocher et valider", "url": f"/api/v1/courses/{liste.id}/valider"},
                ],
            }

        return {
            "etape_actuelle": "termine",
            "planning": {"id": planning.id, "semaine": str(planning.semaine_debut)},
            "courses": {"id": liste.id, "articles": nb_articles, "coches": nb_coches, "progression": 100},
            "actions_suivantes": [
                {"action": "feedback", "label": "Donner son avis sur la semaine", "url": "/api/v1/ia/feedback-semaine"},
            ],
        }


# ═══════════════════════════════════════════════════════════
# B7.2: DIGEST FAMILLE QUOTIDIEN
# ═══════════════════════════════════════════════════════════


@avec_gestion_erreurs(default_return={})
def generer_digest_quotidien() -> dict:
    """Génère un digest quotidien famille condensé.

    Rassemble : repas du jour, routines à faire, tâches entretien,
    anniversaires proches, rappels documents.

    Returns:
        Dict avec les sections du digest.
    """
    from src.core.models.maison import Routine, TacheRoutine, TacheEntretien
    from src.core.models.planning import Repas

    aujourd_hui = date.today()

    with obtenir_contexte_db() as session:
        # Repas du jour
        repas = (
            session.query(Repas)
            .filter(Repas.date_repas == aujourd_hui)
            .all()
        )
        repas_data = [{"type": r.type_repas, "recette": r.recette_nom or "Non défini"} for r in repas]

        # Routines du jour
        jour_semaine = aujourd_hui.strftime("%A").lower()
        routines = (
            session.query(Routine)
            .filter(Routine.actif.is_(True))
            .all()
        )
        routines_jour = []
        for r in routines:
            jours = r.jour_semaine or ""
            if jour_semaine in jours.lower() or jours == "" or jours == "*":
                taches = (
                    session.query(TacheRoutine)
                    .filter(
                        TacheRoutine.routine_id == r.id,
                        TacheRoutine.fait_le.is_(None),
                    )
                    .all()
                )
                if taches:
                    routines_jour.append({
                        "routine": r.nom,
                        "taches_restantes": len(taches),
                    })

        # Tâches entretien du jour
        taches_entretien = (
            session.query(TacheEntretien)
            .filter(
                TacheEntretien.prochaine_fois <= aujourd_hui,
                TacheEntretien.fait.is_(False),
            )
            .limit(5)
            .all()
        )
        entretien_data = [{"nom": t.nom, "priorite": t.priorite or "normale"} for t in taches_entretien]

        return {
            "date": str(aujourd_hui),
            "jour": aujourd_hui.strftime("%A %d %B"),
            "repas": repas_data,
            "routines": routines_jour,
            "entretien": entretien_data,
            "nb_sections": sum(1 for s in [repas_data, routines_jour, entretien_data] if s),
        }


# ═══════════════════════════════════════════════════════════
# B7.3: FLUX MAISON — MARQUER FAIT SIMPLIFIÉ
# ═══════════════════════════════════════════════════════════


@avec_gestion_erreurs(default_return={})
def marquer_tache_fait_avec_prochaine(tache_id: int) -> dict:
    """Marque une tâche d'entretien comme faite et calcule automatiquement la prochaine date.

    Returns:
        {"tache_id": id, "fait": True, "prochaine_fois": date_str}
    """
    from src.core.models.maison import TacheEntretien

    with obtenir_contexte_db() as session:
        tache = session.query(TacheEntretien).filter(TacheEntretien.id == tache_id).first()

        if not tache:
            return {"erreur": f"Tâche {tache_id} introuvable"}

        tache.fait = True
        tache.derniere_execution = date.today()

        # Calculer automatiquement la prochaine date selon la fréquence
        frequences_jours = {
            "quotidien": 1,
            "hebdomadaire": 7,
            "bimensuel": 14,
            "mensuel": 30,
            "trimestriel": 90,
            "semestriel": 180,
            "annuel": 365,
        }

        freq = (tache.frequence or "mensuel").lower()
        jours = frequences_jours.get(freq, 30)
        prochaine = date.today() + timedelta(days=jours)
        tache.prochaine_fois = prochaine

        session.commit()

        try:
            from src.services.core.events.bus import obtenir_bus

            obtenir_bus().emettre(
                "entretien.tache_terminee",
                {
                    "tache_id": tache.id,
                    "nom": tache.nom,
                    "categorie": tache.categorie,
                    "date_realisation": date.today().isoformat(),
                    "prochaine_fois": str(prochaine),
                },
                source="flux_utilisateur",
            )
        except Exception:
            logger.debug("Émission entretien.tache_terminee ignorée", exc_info=True)

        return {
            "tache_id": tache.id,
            "nom": tache.nom,
            "fait": True,
            "prochaine_fois": str(prochaine),
            "frequence": freq,
        }


# ═══════════════════════════════════════════════════════════
# B7.5: FEEDBACK FIN DE SEMAINE
# ═══════════════════════════════════════════════════════════


@avec_gestion_erreurs(default_return={})
def enregistrer_feedback_semaine(feedbacks: list[dict]) -> dict:
    """Enregistre les feedbacks de fin de semaine pour améliorer l'IA.

    Args:
        feedbacks: Liste de dict {"recette_id": int, "note": 1-5, "commentaire": str, "mange": bool}

    Returns:
        {"nb_feedbacks": N, "score_moyen": float}
    """
    from src.core.models.user_preferences import RetourRecette

    if not feedbacks:
        return {"nb_feedbacks": 0, "score_moyen": 0}

    notes = []

    with obtenir_contexte_db() as session:
        for fb in feedbacks:
            recette_id = fb.get("recette_id")
            note = int(fb.get("note", 3) or 3)
            mange = bool(fb.get("mange", True))
            commentaire = fb.get("commentaire", "")
            user_id = str(fb.get("user_id") or "system")

            if not recette_id:
                continue

            if note <= 2 or not mange:
                feedback = "dislike"
            elif note >= 4:
                feedback = "like"
            else:
                feedback = "neutral"

            retour = (
                session.query(RetourRecette)
                .filter(RetourRecette.user_id == user_id, RetourRecette.recette_id == recette_id)
                .first()
            )
            if retour is None:
                retour = RetourRecette(
                    user_id=user_id,
                    recette_id=recette_id,
                    feedback=feedback,
                )
                session.add(retour)
            else:
                retour.feedback = feedback

            retour.contexte = f"note={note}/5"
            retour.notes = commentaire[:1000] if commentaire else retour.notes

            # Émettre événement de feedback pour l'IA
            from src.services.core.events.bus import obtenir_bus

            obtenir_bus().emettre(
                "recette.feedback",
                {
                    "recette_id": recette_id,
                    "note": note,
                    "mange": mange,
                    "commentaire": commentaire,
                    "feedback": feedback,
                    "user_id": user_id,
                },
                source="feedback_semaine",
            )

            notes.append(note)

        session.commit()

    score_moyen = sum(notes) / len(notes) if notes else 0

    return {
        "nb_feedbacks": len(notes),
        "score_moyen": round(score_moyen, 1),
    }
