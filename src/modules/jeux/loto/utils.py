"""
Logique métier Loto - Analyses statistiques et simulations
Ce module contient toute la logique pure, testable sans Streamlit.

⚠️ DISCLAIMER IMPORTANT:
Le Loto est un jeu de hasard pur. Les tirages sont parfaitement aléatoires
et indépendants. Aucune analyse statistique ne peut prédire les résultats.

Ce module propose:
- Analyse des fréquences historiques (à titre informatif)
- Détection des numéros "chauds/froids" (curiosité statistique)
- Simulation de stratégies pour éviter les numéros populaires
- Suivi des performances de "paris virtuels"
"""

import logging
import random
from collections import Counter
from decimal import Decimal
from typing import Any

import streamlit as st

from src.core.database import obtenir_contexte_db
from src.core.models import GrilleLoto, TirageLoto

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════
# CONSTANTES LOTO FRANÇAIS
# ═══════════════════════════════════════════════════════════════════

# Loto FDJ: 5 numéros parmi 49 + 1 numéro chance parmi 10
NUMERO_MIN = 1
NUMERO_MAX = 49
CHANCE_MIN = 1
CHANCE_MAX = 10
NB_NUMEROS = 5

# Gains par rang (approximatifs, varient selon jackpot et nombre de gagnants)
GAINS_PAR_RANG = {
    1: None,  # Jackpot (variable)
    2: 100_000,  # 5 bons
    3: 1_000,  # 4 bons + chance
    4: 500,  # 4 bons
    5: 50,  # 3 bons + chance
    6: 20,  # 3 bons
    7: 10,  # 2 bons + chance
    8: 5,  # 2 bons
    9: 2.20,  # 1 bon + chance (remboursement)
}

# Coût d'une grille simple
COUT_GRILLE = Decimal("2.20")

# Numéros populaires (dates anniversaires, à éviter pour maximiser gains potentiels)
NUMEROS_POPULAIRES = set(range(1, 32))  # 1-31 = dates

# Probabilité de gagner le jackpot (5 bons + chance)
PROBA_JACKPOT = 1 / 19_068_840  # ~1 sur 19 millions


# ═══════════════════════════════════════════════════════════════════
# ANALYSE DES FRÉQUENCES
# ═══════════════════════════════════════════════════════════════════


def calculer_frequences_numeros(tirages: list[dict[str, Any]]) -> dict[str, Any]:
    """
    Calcule la fréquence d'apparition de chaque numéro.

    Args:
        tirages: Liste des tirages historiques

    Returns:
        Statistiques de fréquence par numéro
    """
    if not tirages:
        return {"frequences": {}, "frequences_chance": {}, "nb_tirages": 0}

    compteur_numeros = Counter()
    compteur_chance = Counter()
    dernier_tirage = {}

    for tirage in tirages:
        date_t = tirage.get("date_tirage")

        # Compter les 5 numéros principaux
        for i in range(1, 6):
            num = tirage.get(f"numero_{i}")
            if num:
                compteur_numeros[num] += 1
                dernier_tirage[num] = date_t

        # Numéro chance
        chance = tirage.get("numero_chance")
        if chance:
            compteur_chance[chance] += 1

    nb_tirages = len(tirages)

    # Calculer stats par numéro
    frequences = {}
    for num in range(NUMERO_MIN, NUMERO_MAX + 1):
        freq = compteur_numeros.get(num, 0)
        frequences[num] = {
            "frequence": freq,
            "pourcentage": round(freq / nb_tirages * 100, 2) if nb_tirages > 0 else 0,
            "dernier_tirage": dernier_tirage.get(num),
            "ecart": calculer_ecart(tirages, num) if tirages else 0,
        }

    frequences_chance = {}
    for num in range(CHANCE_MIN, CHANCE_MAX + 1):
        freq = compteur_chance.get(num, 0)
        frequences_chance[num] = {
            "frequence": freq,
            "pourcentage": round(freq / nb_tirages * 100, 2) if nb_tirages > 0 else 0,
        }

    return {
        "frequences": frequences,
        "frequences_chance": frequences_chance,
        "nb_tirages": nb_tirages,
    }


def calculer_ecart(tirages: list[dict[str, Any]], numero: int) -> int:
    """
    Calcule l'écart (nombre de tirages depuis la dernière apparition).

    Args:
        tirages: Liste des tirages (du plus ancien au plus récent)
        numero: Numéro à analyser

    Returns:
        Nombre de tirages depuis dernière apparition
    """
    for i, tirage in enumerate(reversed(tirages)):
        numeros = [tirage.get(f"numero_{j}") for j in range(1, 6)]
        if numero in numeros:
            return i
    return len(tirages)  # Jamais sorti


def identifier_numeros_chauds_froids(
    frequences: dict[int, dict], nb_top: int = 10
) -> dict[str, list[int]]:
    """
    Identifie les numéros les plus et moins fréquents.

    ⚠️ Rappel: Ceci est purement informatif. Les tirages sont indépendants.

    Args:
        frequences: Dict des fréquences par numéro
        nb_top: Nombre de numéros à retourner par catégorie

    Returns:
        Numéros chauds et froids
    """
    if not frequences:
        return {"chauds": [], "froids": [], "retard": []}

    # Trier par fréquence
    tries_freq = sorted(frequences.items(), key=lambda x: x[1].get("frequence", 0), reverse=True)

    # Trier par écart (retard)
    tries_ecart = sorted(frequences.items(), key=lambda x: x[1].get("ecart", 0), reverse=True)

    return {
        "chauds": [num for num, _ in tries_freq[:nb_top]],
        "froids": [num for num, _ in tries_freq[-nb_top:]],
        "retard": [num for num, _ in tries_ecart[:nb_top]],
    }


# ═══════════════════════════════════════════════════════════════════
# ANALYSE DE PATTERNS (Curiosité statistique)
# ═══════════════════════════════════════════════════════════════════


def analyser_patterns_tirages(tirages: list[dict[str, Any]]) -> dict[str, Any]:
    """
    Analyse divers patterns dans les tirages historiques.

    Args:
        tirages: Liste des tirages

    Returns:
        Statistiques sur les patterns
    """
    if not tirages:
        return {}

    sommes = []
    nb_pairs = []
    nb_impairs = []
    ecarts_min_max = []
    paires_frequentes = Counter()

    for tirage in tirages:
        numeros = sorted([tirage.get(f"numero_{i}") for i in range(1, 6)])
        numeros = [n for n in numeros if n]  # Filtrer None

        if len(numeros) != 5:
            continue

        # Somme
        sommes.append(sum(numeros))

        # Parité
        pairs = sum(1 for n in numeros if n % 2 == 0)
        nb_pairs.append(pairs)
        nb_impairs.append(5 - pairs)

        # Écart min-max
        ecarts_min_max.append(numeros[-1] - numeros[0])

        # Paires fréquentes
        for i in range(len(numeros)):
            for j in range(i + 1, len(numeros)):
                paires_frequentes[(numeros[i], numeros[j])] += 1

    if not sommes:
        return {}

    # Top 10 paires les plus fréquentes
    top_paires = paires_frequentes.most_common(10)

    return {
        "somme_moyenne": round(sum(sommes) / len(sommes), 1),
        "somme_min": min(sommes),
        "somme_max": max(sommes),
        "pairs_moyen": round(sum(nb_pairs) / len(nb_pairs), 1),
        "ecart_moyen": round(sum(ecarts_min_max) / len(ecarts_min_max), 1),
        "paires_frequentes": [
            {"paire": list(paire), "frequence": freq} for paire, freq in top_paires
        ],
        "distribution_parite": {
            "0_pair_5_impair": nb_pairs.count(0),
            "1_pair_4_impair": nb_pairs.count(1),
            "2_pair_3_impair": nb_pairs.count(2),
            "3_pair_2_impair": nb_pairs.count(3),
            "4_pair_1_impair": nb_pairs.count(4),
            "5_pair_0_impair": nb_pairs.count(5),
        },
    }


# ═══════════════════════════════════════════════════════════════════
# GÉNÉRATION DE GRILLES
# ═══════════════════════════════════════════════════════════════════


def generer_grille_aleatoire() -> dict[str, Any]:
    """
    Génère une grille complètement aléatoire.

    Returns:
        Grille avec 5 numéros + numéro chance
    """
    numeros = sorted(random.sample(range(NUMERO_MIN, NUMERO_MAX + 1), NB_NUMEROS))
    chance = random.randint(CHANCE_MIN, CHANCE_MAX)

    return {"numeros": numeros, "numero_chance": chance, "source": "aleatoire"}


def generer_grille_eviter_populaires() -> dict[str, Any]:
    """
    Génère une grille en évitant les numéros populaires (1-31).

    Stratégie: En cas de gain, partager avec moins de gagnants.

    Returns:
        Grille avec numéros moins populaires
    """
    # Privilégier les numéros 32-49 (moins joués)
    pool_prioritaire = list(range(32, NUMERO_MAX + 1))  # 18 numéros
    pool_secondaire = list(range(NUMERO_MIN, 32))  # 31 numéros

    # Prendre 3-4 numéros du pool prioritaire, 1-2 du secondaire
    nb_prioritaire = random.randint(3, 4)
    nb_secondaire = NB_NUMEROS - nb_prioritaire

    numeros = random.sample(pool_prioritaire, nb_prioritaire) + random.sample(
        pool_secondaire, nb_secondaire
    )
    numeros = sorted(numeros)
    chance = random.randint(CHANCE_MIN, CHANCE_MAX)

    return {
        "numeros": numeros,
        "numero_chance": chance,
        "source": "eviter_populaires",
        "note": "Évite les dates (1-31) pour maximiser gains potentiels",
    }


def generer_grille_equilibree(patterns: dict[str, Any]) -> dict[str, Any]:
    """
    Génère une grille "équilibrée" basée sur les patterns historiques.

    ⚠️ Ceci n'augmente PAS les chances de gagner, mais produit
    une grille statistiquement "typique".

    Args:
        patterns: Résultat de analyser_patterns_tirages()

    Returns:
        Grille équilibrée
    """
    # Viser une somme proche de la moyenne
    somme_cible = patterns.get("somme_moyenne", 125)
    ecart_cible = patterns.get("ecart_moyen", 35)

    # Essayer plusieurs fois pour approcher la cible
    meilleure_grille = None
    meilleur_ecart = float("inf")

    for _ in range(100):
        numeros = sorted(random.sample(range(NUMERO_MIN, NUMERO_MAX + 1), NB_NUMEROS))
        somme = sum(numeros)
        ecart = numeros[-1] - numeros[0]

        # Score = proximité avec les moyennes
        score = abs(somme - somme_cible) + abs(ecart - ecart_cible) * 0.5

        if score < meilleur_ecart:
            meilleur_ecart = score
            meilleure_grille = numeros

    chance = random.randint(CHANCE_MIN, CHANCE_MAX)

    return {
        "numeros": meilleure_grille,
        "numero_chance": chance,
        "source": "equilibree",
        "somme": sum(meilleure_grille),
        "ecart": meilleure_grille[-1] - meilleure_grille[0],
        "note": f"Somme proche de la moyenne ({somme_cible})",
    }


def generer_grille_chauds_froids(
    frequences: dict[int, dict], strategie: str = "mixte"
) -> dict[str, Any]:
    """
    Génère une grille basée sur les numéros chauds ou froids.

    ⚠️ Rappel: Statistiquement inutile, mais psychologiquement satisfaisant.

    Args:
        frequences: Fréquences des numéros
        strategie: "chauds", "froids", ou "mixte"

    Returns:
        Grille basée sur la stratégie
    """
    chauds_froids = identifier_numeros_chauds_froids(frequences)

    if strategie == "chauds":
        pool = chauds_froids["chauds"][:20]
    elif strategie == "froids":
        pool = chauds_froids["froids"][:20]
    else:  # mixte
        pool = chauds_froids["chauds"][:10] + chauds_froids["froids"][:10]

    # Compléter si pas assez
    while len(pool) < NB_NUMEROS:
        pool.append(random.randint(NUMERO_MIN, NUMERO_MAX))
    pool = list(set(pool))

    numeros = sorted(random.sample(pool, min(NB_NUMEROS, len(pool))))

    # Compléter si besoin
    while len(numeros) < NB_NUMEROS:
        n = random.randint(NUMERO_MIN, NUMERO_MAX)
        if n not in numeros:
            numeros.append(n)
    numeros = sorted(numeros[:NB_NUMEROS])

    chance = random.randint(CHANCE_MIN, CHANCE_MAX)

    return {
        "numeros": numeros,
        "numero_chance": chance,
        "source": f"strategie_{strategie}",
        "note": f"Basé sur numéros {strategie}",
    }


# ═══════════════════════════════════════════════════════════════════
# VÉRIFICATION DES GAINS
# ═══════════════════════════════════════════════════════════════════


def verifier_grille(grille: dict[str, Any], tirage: dict[str, Any]) -> dict[str, Any]:
    """
    Vérifie une grille contre un tirage et calcule les gains.

    Args:
        grille: Grille jouée
        tirage: Résultat du tirage

    Returns:
        Résultat avec rang et gain
    """
    # Numéros du tirage
    numeros_tirage = set([tirage.get(f"numero_{i}") for i in range(1, 6)])
    chance_tirage = tirage.get("numero_chance")

    # Numéros de la grille
    numeros_grille = set(grille.get("numeros", []))
    chance_grille = grille.get("numero_chance")

    # Compter les bons numéros
    bons_numeros = len(numeros_tirage & numeros_grille)
    chance_ok = chance_grille == chance_tirage

    # Déterminer le rang
    rang = None
    gain = Decimal("0.00")

    if bons_numeros == 5 and chance_ok:
        rang = 1  # Jackpot!
        gain = Decimal(str(tirage.get("jackpot_euros", 2_000_000)))
    elif bons_numeros == 5:
        rang = 2
        gain = Decimal(str(GAINS_PAR_RANG[2]))
    elif bons_numeros == 4 and chance_ok:
        rang = 3
        gain = Decimal(str(GAINS_PAR_RANG[3]))
    elif bons_numeros == 4:
        rang = 4
        gain = Decimal(str(GAINS_PAR_RANG[4]))
    elif bons_numeros == 3 and chance_ok:
        rang = 5
        gain = Decimal(str(GAINS_PAR_RANG[5]))
    elif bons_numeros == 3:
        rang = 6
        gain = Decimal(str(GAINS_PAR_RANG[6]))
    elif bons_numeros == 2 and chance_ok:
        rang = 7
        gain = Decimal(str(GAINS_PAR_RANG[7]))
    elif bons_numeros == 2:
        rang = 8
        gain = Decimal(str(GAINS_PAR_RANG[8]))
    elif bons_numeros == 1 and chance_ok:
        rang = 9
        gain = Decimal(str(GAINS_PAR_RANG[9]))

    return {
        "bons_numeros": bons_numeros,
        "chance_ok": chance_ok,
        "rang": rang,
        "gain": gain,
        "gagnant": rang is not None,
        "description": f"{bons_numeros} numéros" + (" + chance" if chance_ok else ""),
    }


# ═══════════════════════════════════════════════════════════════════
# SIMULATION & PERFORMANCE
# ═══════════════════════════════════════════════════════════════════


def simuler_strategie(
    tirages: list[dict[str, Any]],
    strategie: str = "aleatoire",
    nb_grilles_par_tirage: int = 1,
    frequences: dict | None = None,
    patterns: dict | None = None,
) -> dict[str, Any]:
    """
    Simule une stratégie sur l'historique des tirages.

    Args:
        tirages: Historique des tirages
        strategie: "aleatoire", "eviter_populaires", "equilibree", "chauds", "froids"
        nb_grilles_par_tirage: Nombre de grilles jouées par tirage
        frequences: Fréquences pré-calculées
        patterns: Patterns pré-calculés

    Returns:
        Résultats de la simulation
    """
    if not tirages:
        return {"erreur": "Aucun tirage disponible"}

    resultats = []
    mises_totales = Decimal("0.00")
    gains_totaux = Decimal("0.00")

    for tirage in tirages:
        for _ in range(nb_grilles_par_tirage):
            # Générer grille selon stratégie
            if strategie == "aleatoire":
                grille = generer_grille_aleatoire()
            elif strategie == "eviter_populaires":
                grille = generer_grille_eviter_populaires()
            elif strategie == "equilibree" and patterns:
                grille = generer_grille_equilibree(patterns)
            elif strategie in ["chauds", "froids", "mixte"] and frequences:
                grille = generer_grille_chauds_froids(frequences, strategie)
            else:
                grille = generer_grille_aleatoire()

            # Vérifier contre le tirage
            resultat = verifier_grille(grille, tirage)

            mises_totales += COUT_GRILLE
            gains_totaux += resultat.get("gain", Decimal("0.00"))

            resultats.append(
                {"date": tirage.get("date_tirage"), "grille": grille, "resultat": resultat}
            )

    # Statistiques
    nb_gagnants = sum(1 for r in resultats if r["resultat"]["gagnant"])
    rangs = Counter(r["resultat"]["rang"] for r in resultats if r["resultat"]["rang"])

    return {
        "strategie": strategie,
        "nb_tirages": len(tirages),
        "nb_grilles": len(resultats),
        "mises_totales": mises_totales,
        "gains_totaux": gains_totaux,
        "profit": gains_totaux - mises_totales,
        "roi": float((gains_totaux - mises_totales) / mises_totales * 100)
        if mises_totales > 0
        else 0,
        "nb_gagnants": nb_gagnants,
        "taux_gain": round(nb_gagnants / len(resultats) * 100, 2) if resultats else 0,
        "distribution_rangs": dict(rangs),
        "details": resultats[-10:],  # 10 derniers pour affichage
    }


def calculer_esperance_mathematique() -> dict[str, Any]:
    """
    Calcule l'espérance mathématique du Loto.

    Spoiler: Elle est négative (c'est un jeu d'argent).

    Returns:
        Espérance et probabilités
    """
    # Probabilités exactes du Loto français
    probas = {
        1: 1 / 19_068_840,  # 5 + chance
        2: 1 / 2_118_760,  # 5
        3: 1 / 86_677,  # 4 + chance
        4: 1 / 9_631,  # 4
        5: 1 / 2_016,  # 3 + chance
        6: 1 / 224,  # 3
        7: 1 / 144,  # 2 + chance
        8: 1 / 16,  # 2
        9: 1 / 16,  # 1 + chance
    }

    # Calcul espérance (jackpot moyen estimé à 5M€)
    jackpot_moyen = 5_000_000
    gains_esperes = (
        probas[1] * jackpot_moyen
        + probas[2] * GAINS_PAR_RANG[2]
        + probas[3] * GAINS_PAR_RANG[3]
        + probas[4] * GAINS_PAR_RANG[4]
        + probas[5] * GAINS_PAR_RANG[5]
        + probas[6] * GAINS_PAR_RANG[6]
        + probas[7] * GAINS_PAR_RANG[7]
        + probas[8] * GAINS_PAR_RANG[8]
        + probas[9] * GAINS_PAR_RANG[9]
    )

    esperance = gains_esperes - float(COUT_GRILLE)

    return {
        "cout_grille": float(COUT_GRILLE),
        "gains_esperes": round(gains_esperes, 4),
        "esperance": round(esperance, 4),
        "perte_moyenne_pct": round((1 - gains_esperes / float(COUT_GRILLE)) * 100, 1),
        "probabilites": {rang: f"1/{int(1 / p):,}" for rang, p in probas.items()},
        "conclusion": (
            f"En moyenne, vous perdez {abs(esperance):.2f}€ par grille jouée. "
            f"Le Loto reverse environ {gains_esperes / float(COUT_GRILLE) * 100:.0f}% des mises."
        ),
    }


def comparer_strategies(tirages: list[dict[str, Any]], nb_simulations: int = 100) -> dict[str, Any]:
    """
    Compare plusieurs stratégies sur les mêmes tirages.

    Args:
        tirages: Historique des tirages
        nb_simulations: Nombre de simulations par stratégie

    Returns:
        Comparaison des performances
    """
    if not tirages:
        return {"erreur": "Aucun tirage"}

    # Pré-calculer stats
    freq_data = calculer_frequences_numeros(tirages)
    patterns = analyser_patterns_tirages(tirages)

    strategies = ["aleatoire", "eviter_populaires", "equilibree", "chauds", "froids"]
    resultats = {}

    for strat in strategies:
        res = simuler_strategie(
            tirages,
            strategie=strat,
            nb_grilles_par_tirage=1,
            frequences=freq_data.get("frequences"),
            patterns=patterns,
        )
        resultats[strat] = {
            "roi": res.get("roi", 0),
            "taux_gain": res.get("taux_gain", 0),
            "nb_gagnants": res.get("nb_gagnants", 0),
        }

    # Classement par ROI
    classement = sorted(resultats.items(), key=lambda x: x[1]["roi"], reverse=True)

    return {
        "nb_tirages": len(tirages),
        "resultats": resultats,
        "classement": [s[0] for s in classement],
        "meilleure_strategie": classement[0][0] if classement else None,
        "note": "⚠️ Ces résultats varient aléatoirement. Aucune stratégie n'est meilleure à long terme.",
    }


# ============================================================
# Fonctions importées depuis utilitaires.py
# ============================================================


def charger_tirages(limite: int = 100):
    """Charge l'historique des tirages"""
    try:
        with obtenir_contexte_db() as session:
            tirages = (
                session.query(TirageLoto)
                .order_by(TirageLoto.date_tirage.desc())
                .limit(limite)
                .all()
            )

            return [
                {
                    "id": t.id,
                    "date_tirage": t.date_tirage,
                    "numero_1": t.numero_1,
                    "numero_2": t.numero_2,
                    "numero_3": t.numero_3,
                    "numero_4": t.numero_4,
                    "numero_5": t.numero_5,
                    "numero_chance": t.numero_chance,
                    "jackpot_euros": t.jackpot_euros,
                    "numeros": t.numeros,
                    "numeros_str": t.numeros_str,
                }
                for t in tirages
            ]
    except Exception as e:
        st.error(f"❌ Erreur chargement tirages: {e}")
        return []


def charger_grilles_utilisateur():
    """Charge les grilles de l'utilisateur"""
    try:
        with obtenir_contexte_db() as session:
            grilles = (
                session.query(GrilleLoto).order_by(GrilleLoto.date_creation.desc()).limit(50).all()
            )

            return [
                {
                    "id": g.id,
                    "numeros": g.numeros,
                    "numeros_str": g.numeros_str,
                    "numero_chance": g.numero_chance,
                    "source": g.source_prediction,
                    "est_virtuelle": g.est_virtuelle,
                    "mise": g.mise,
                    "tirage_id": g.tirage_id,
                    "numeros_trouves": g.numeros_trouves,
                    "chance_trouvee": g.chance_trouvee,
                    "rang": g.rang,
                    "gain": g.gain,
                    "date": g.date_creation,
                }
                for g in grilles
            ]
    except Exception as e:
        st.error(f"❌ Erreur chargement grilles: {e}")
        return []
