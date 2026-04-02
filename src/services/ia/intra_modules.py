"""
B.6 — Améliorations intra-modules.

Services complémentaires pour :
- B6.1: Checkout courses → mise à jour prix moyens inventaire
- B6.5: Routines → tracking streak de complétion
- B6.6: Énergie → comparaison N vs N-1
- B6.7: Entretien → suggestions IA proactives par âge équipement
"""

import logging
from collections import defaultdict
from datetime import date, timedelta

from src.core.db import obtenir_contexte_db
from src.core.decorators import avec_gestion_erreurs, avec_session_db

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# B6.1: CHECKOUT → PRIX MOYENS INVENTAIRE
# ═══════════════════════════════════════════════════════════


@avec_gestion_erreurs(default_return=0)
def mettre_a_jour_prix_moyens_checkout(liste_id: int) -> int:
    """Met à jour les prix moyens dans l'inventaire après un checkout de courses.

    Calcule la moyenne pondérée (70% ancien, 30% nouveau) pour chaque article
    acheté dont le prix est renseigné.

    Returns:
        Nombre d'articles mis à jour.
    """
    from src.core.models.courses import ArticleCourses
    from src.core.models.inventaire import ArticleInventaire

    mis_a_jour = 0

    with obtenir_contexte_db() as session:
        articles = (
            session.query(ArticleCourses)
            .filter(
                ArticleCourses.liste_id == liste_id,
                ArticleCourses.coche.is_(True),
                ArticleCourses.prix_unitaire.isnot(None),
                ArticleCourses.prix_unitaire > 0,
            )
            .all()
        )

        for article in articles:
            inventaire = (
                session.query(ArticleInventaire)
                .filter(ArticleInventaire.nom == article.nom)
                .first()
            )

            if inventaire:
                ancien_prix = inventaire.prix_moyen or 0.0
                nouveau_prix = float(article.prix_unitaire)

                if ancien_prix > 0:
                    inventaire.prix_moyen = round(ancien_prix * 0.7 + nouveau_prix * 0.3, 2)
                else:
                    inventaire.prix_moyen = round(nouveau_prix, 2)

                mis_a_jour += 1

        session.commit()

    logger.info(f"B6.1: {mis_a_jour} prix moyens mis à jour après checkout liste {liste_id}")
    return mis_a_jour


# ═══════════════════════════════════════════════════════════
# B6.5: ROUTINES → STREAK TRACKING
# ═══════════════════════════════════════════════════════════


@avec_gestion_erreurs(default_return={})
def calculer_streak_routines() -> dict:
    """Calcule le streak de complétion pour chaque routine active.

    Un streak = nombre de périodes consécutives où toutes les tâches
    de la routine ont été complétées.

    Returns:
        Dict {routine_id: {"nom": ..., "streak": N, "meilleur_streak": M, "taux_completion": pct}}
    """
    from src.core.models.maison import Routine, TacheRoutine

    with obtenir_contexte_db() as session:
        routines = (
            session.query(Routine)
            .filter(Routine.actif.is_(True))
            .all()
        )

        resultats = {}

        for routine in routines:
            taches = (
                session.query(TacheRoutine)
                .filter(TacheRoutine.routine_id == routine.id)
                .order_by(TacheRoutine.fait_le.desc())
                .all()
            )

            # Calculer le streak par jours consécutifs
            streak_actuel = 0
            meilleur_streak = 0
            streak_temp = 0
            jours_completes = set()

            for tache in taches:
                if tache.fait_le:
                    jours_completes.add(tache.fait_le.date() if hasattr(tache.fait_le, 'date') else tache.fait_le)

            if not jours_completes:
                resultats[routine.id] = {
                    "nom": routine.nom,
                    "streak": 0,
                    "meilleur_streak": 0,
                    "taux_completion": 0.0,
                }
                continue

            # Trier les jours et compter les streaks
            jours_tries = sorted(jours_completes, reverse=True)
            aujourd_hui = date.today()

            # Streak actuel (depuis aujourd'hui en arrière)
            for i, jour in enumerate(jours_tries):
                attendu = aujourd_hui - timedelta(days=i)
                if jour == attendu:
                    streak_actuel += 1
                else:
                    break

            # Meilleur streak historique
            if jours_tries:
                jours_asc = sorted(jours_completes)
                streak_temp = 1
                meilleur_streak = 1
                for i in range(1, len(jours_asc)):
                    if (jours_asc[i] - jours_asc[i - 1]).days == 1:
                        streak_temp += 1
                        meilleur_streak = max(meilleur_streak, streak_temp)
                    else:
                        streak_temp = 1

            # Taux de complétion (30 derniers jours)
            trente_jours = aujourd_hui - timedelta(days=30)
            jours_30 = [j for j in jours_completes if j >= trente_jours]
            taux = len(jours_30) / 30.0 * 100

            resultats[routine.id] = {
                "nom": routine.nom,
                "streak": streak_actuel,
                "meilleur_streak": meilleur_streak,
                "taux_completion": round(taux, 1),
            }

        return resultats


# ═══════════════════════════════════════════════════════════
# B6.6: ÉNERGIE → COMPARAISON N vs N-1
# ═══════════════════════════════════════════════════════════


@avec_gestion_erreurs(default_return={})
def comparaison_energie_n_vs_n1(type_energie: str = "electricite") -> dict:
    """Compare la consommation énergie mois par mois entre N et N-1.

    Returns:
        Dict avec mois, valeurs N, valeurs N-1, et écarts en %.
    """
    from sqlalchemy import func, extract
    from src.core.models.maison import DepenseMaison

    annee_n = date.today().year
    annee_n1 = annee_n - 1

    with obtenir_contexte_db() as session:
        # Requête pour les deux années
        resultats_n = _requete_mensuelle(session, type_energie, annee_n)
        resultats_n1 = _requete_mensuelle(session, type_energie, annee_n1)

        comparaison = []
        mois_noms = [
            "Janvier", "Février", "Mars", "Avril", "Mai", "Juin",
            "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre",
        ]

        for mois in range(1, 13):
            val_n = resultats_n.get(mois, 0.0)
            val_n1 = resultats_n1.get(mois, 0.0)

            ecart_pct = 0.0
            if val_n1 > 0:
                ecart_pct = round((val_n - val_n1) / val_n1 * 100, 1)

            comparaison.append({
                "mois": mois,
                "mois_nom": mois_noms[mois - 1],
                "annee_n": round(val_n, 2),
                "annee_n1": round(val_n1, 2),
                "ecart_pct": ecart_pct,
                "tendance": "hausse" if ecart_pct > 5 else "baisse" if ecart_pct < -5 else "stable",
            })

        total_n = sum(c["annee_n"] for c in comparaison)
        total_n1 = sum(c["annee_n1"] for c in comparaison)
        ecart_total = round((total_n - total_n1) / total_n1 * 100, 1) if total_n1 > 0 else 0.0

        return {
            "type_energie": type_energie,
            "annee_n": annee_n,
            "annee_n1": annee_n1,
            "mois": comparaison,
            "total_n": round(total_n, 2),
            "total_n1": round(total_n1, 2),
            "ecart_total_pct": ecart_total,
        }


def _requete_mensuelle(session, type_energie: str, annee: int) -> dict[int, float]:
    """Requête de consommation mensuelle pour une année."""
    from sqlalchemy import func
    from src.core.models.maison import DepenseMaison

    rows = (
        session.query(
            DepenseMaison.mois,
            func.sum(DepenseMaison.montant),
        )
        .filter(
            DepenseMaison.annee == annee,
            DepenseMaison.categorie == type_energie,
        )
        .group_by(DepenseMaison.mois)
        .all()
    )

    return {int(r[0]): float(r[1] or 0) for r in rows}


# ═══════════════════════════════════════════════════════════
# B6.7: ENTRETIEN → SUGGESTIONS IA PROACTIVES PAR ÂGE
# ═══════════════════════════════════════════════════════════


@avec_gestion_erreurs(default_return=[])
def suggestions_entretien_par_age_equipement() -> list[dict]:
    """Génère des suggestions d'entretien basées sur l'âge des équipements.

    Identifie les équipements vieillissants et suggère des actions préventives.

    Returns:
        Liste de suggestions {equipement, age_annees, suggestion, priorite}
    """
    from src.core.models.maison import ObjetMaison

    seuils_alerte = {
        "chaudiere": 8,
        "chauffe-eau": 10,
        "climatisation": 10,
        "lave-linge": 8,
        "lave-vaisselle": 8,
        "refrigerateur": 12,
        "four": 10,
        "toiture": 20,
        "peinture": 7,
    }

    suggestions = []

    with obtenir_contexte_db() as session:
        objets = session.query(ObjetMaison).all()

        for objet in objets:
            if not objet.date_achat:
                continue

            age = (date.today() - objet.date_achat).days / 365.25
            categorie = (objet.categorie or "").lower()

            seuil = None
            for cle, val in seuils_alerte.items():
                if cle in categorie or cle in (objet.nom or "").lower():
                    seuil = val
                    break

            if seuil and age >= seuil * 0.8:
                priorite = "haute" if age >= seuil else "moyenne"
                suggestions.append({
                    "equipement": objet.nom,
                    "categorie": objet.categorie,
                    "age_annees": round(age, 1),
                    "seuil_revision": seuil,
                    "suggestion": (
                        f"Équipement '{objet.nom}' a {age:.0f} ans "
                        f"(seuil révision: {seuil} ans). "
                        f"Prévoir une révision ou anticiper le remplacement."
                    ),
                    "priorite": priorite,
                })

    suggestions.sort(key=lambda s: s["age_annees"], reverse=True)
    return suggestions
