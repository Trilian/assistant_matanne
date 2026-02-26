"""
Service de courses récurrentes — Détection automatique et templates.

Analyse l'historique d'achats pour détecter les produits récurrents
et proposer une liste de base automatique.
"""

from __future__ import annotations

import logging
from collections import Counter
from dataclasses import dataclass, field
from datetime import date, timedelta

from sqlalchemy import func
from sqlalchemy.orm import Session

from src.core.decorators import avec_session_db

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# TYPES
# ═══════════════════════════════════════════════════════════


@dataclass
class ArticleRecurrent:
    """Produit détecté comme récurrent."""

    nom: str
    ingredient_id: int | None = None
    frequence_jours: float = 7.0  # Tous les combien de jours
    quantite_moyenne: float = 1.0
    unite: str = "pièce"
    fiabilite: float = 0.0  # 0-1, confiance de la détection
    dernier_achat: date | None = None
    prochain_achat_prevu: date | None = None
    rayon: str = "Autre"


@dataclass
class ListeRecurrente:
    """Liste de courses récurrente auto-générée."""

    articles: list[ArticleRecurrent]
    date_generation: date = field(default_factory=date.today)
    periode_analyse: int = 90  # jours d'historique analysés
    confiance_globale: float = 0.0


# ═══════════════════════════════════════════════════════════
# FONCTIONS
# ═══════════════════════════════════════════════════════════

SEUIL_RECURRENCE = 3  # Minimum d'achats pour détecter une récurrence
PERIODE_ANALYSE_JOURS = 90  # 3 mois d'historique


@avec_session_db
def detecter_articles_recurrents(
    periode_jours: int = PERIODE_ANALYSE_JOURS,
    seuil_achats: int = SEUIL_RECURRENCE,
    *,
    db: Session,
) -> list[ArticleRecurrent]:
    """
    Analyse l'historique pour détecter les articles achetés régulièrement.

    Algorithme:
    1. Récupère les achats sur N jours
    2. Groupe par ingrédient
    3. Calcule la fréquence moyenne d'achat
    4. Filtre les articles achetés au moins `seuil` fois

    Returns:
        Liste triée par fiabilité décroissante
    """
    from src.core.models.courses import ArticleCourses

    date_debut = date.today() - timedelta(days=periode_jours)

    # Articles achetés dans la période
    achats = (
        db.query(
            ArticleCourses.ingredient_id,
            ArticleCourses.rayon_magasin,
            ArticleCourses.quantite_necessaire,
            ArticleCourses.achete_le,
        )
        .filter(
            ArticleCourses.achete.is_(True),
            ArticleCourses.achete_le.isnot(None),
            ArticleCourses.achete_le >= date_debut,
        )
        .all()
    )

    if not achats:
        return []

    # Grouper par ingrédient
    par_ingredient: dict[int, list] = {}
    for achat in achats:
        if achat.ingredient_id:
            par_ingredient.setdefault(achat.ingredient_id, []).append(achat)

    resultats = []
    for ingredient_id, achats_ing in par_ingredient.items():
        if len(achats_ing) < seuil_achats:
            continue

        # Récupérer le nom
        from src.core.models.recettes import Ingredient

        ingredient = db.query(Ingredient).get(ingredient_id)
        if not ingredient:
            continue

        # Calculer la fréquence
        dates_achat = sorted(
            [
                a.achete_le.date() if hasattr(a.achete_le, "date") else a.achete_le
                for a in achats_ing
                if a.achete_le
            ]
        )

        if len(dates_achat) >= 2:
            intervalles = [
                (dates_achat[i + 1] - dates_achat[i]).days for i in range(len(dates_achat) - 1)
            ]
            freq_moyenne = sum(intervalles) / len(intervalles)

            # Fiabilité basée sur la régularité (écart-type faible = fiable)
            if len(intervalles) >= 2:
                moy = freq_moyenne
                variance = sum((x - moy) ** 2 for x in intervalles) / len(intervalles)
                ecart_type = variance**0.5
                # Plus l'écart-type est faible par rapport à la moyenne, plus c'est fiable
                fiabilite = max(0.0, min(1.0, 1.0 - (ecart_type / max(moy, 1))))
            else:
                fiabilite = 0.5
        else:
            freq_moyenne = float(periode_jours / len(dates_achat))
            fiabilite = 0.3

        # Quantité moyenne
        quantites = [a.quantite_necessaire for a in achats_ing if a.quantite_necessaire]
        qte_moy = sum(quantites) / len(quantites) if quantites else 1.0

        # Rayon le plus fréquent
        rayons = [a.rayon_magasin for a in achats_ing if a.rayon_magasin]
        rayon = Counter(rayons).most_common(1)[0][0] if rayons else "Autre"

        dernier_achat = dates_achat[-1] if dates_achat else None
        prochain = dernier_achat + timedelta(days=int(freq_moyenne)) if dernier_achat else None

        resultats.append(
            ArticleRecurrent(
                nom=ingredient.nom,
                ingredient_id=ingredient_id,
                frequence_jours=round(freq_moyenne, 1),
                quantite_moyenne=round(qte_moy, 1),
                rayon=rayon,
                fiabilite=round(fiabilite, 2),
                dernier_achat=dernier_achat,
                prochain_achat_prevu=prochain,
            )
        )

    resultats.sort(key=lambda a: a.fiabilite, reverse=True)
    return resultats


@avec_session_db
def generer_liste_recurrente(
    periode_jours: int = PERIODE_ANALYSE_JOURS,
    *,
    db: Session,
) -> ListeRecurrente:
    """
    Génère une liste de courses basée sur les articles récurrents
    dont le prochain achat est prévu cette semaine.

    Returns:
        ListeRecurrente avec articles à racheter
    """
    articles = detecter_articles_recurrents(periode_jours=periode_jours, db=db)

    aujourd_hui = date.today()
    fin_semaine = aujourd_hui + timedelta(days=7)

    # Filtrer : articles dont le prochain achat est dans la semaine
    a_racheter = [
        a for a in articles if a.prochain_achat_prevu and a.prochain_achat_prevu <= fin_semaine
    ]

    confiance = sum(a.fiabilite for a in a_racheter) / len(a_racheter) if a_racheter else 0.0

    return ListeRecurrente(
        articles=a_racheter,
        periode_analyse=periode_jours,
        confiance_globale=round(confiance, 2),
    )


@avec_session_db
def articles_a_racheter_urgent(*, db: Session) -> list[ArticleRecurrent]:
    """
    Articles dont la date de rachat prévue est dépassée.

    Returns:
        Articles en retard, triés par urgence
    """
    articles = detecter_articles_recurrents(db=db)
    aujourd_hui = date.today()

    urgents = [
        a for a in articles if a.prochain_achat_prevu and a.prochain_achat_prevu < aujourd_hui
    ]

    # Trier par retard croissant (le plus en retard en premier)
    urgents.sort(key=lambda a: a.prochain_achat_prevu or aujourd_hui)
    return urgents


__all__ = [
    "ArticleRecurrent",
    "ListeRecurrente",
    "detecter_articles_recurrents",
    "generer_liste_recurrente",
    "articles_a_racheter_urgent",
]
