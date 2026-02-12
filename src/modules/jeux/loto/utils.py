"""
Logique mÃetier Loto - Analyses statistiques et simulations
Ce module contient toute la logique pure, testable sans Streamlit.

âš ï¸ DISCLAIMER IMPORTANT:
Le Loto est un jeu de hasard pur. Les tirages sont parfaitement alÃeatoires
et indÃependants. Aucune analyse statistique ne peut prÃedire les rÃesultats.

Ce module propose:
- Analyse des frÃequences historiques (Ã  titre informatif)
- DÃetection des numÃeros "chauds/froids" (curiositÃe statistique)
- Simulation de stratÃegies pour Ãeviter les numÃeros populaires
- Suivi des performances de "paris virtuels"
"""

from datetime import date, timedelta
from typing import Optional, Dict, Any, List, Tuple, Set
from decimal import Decimal
from collections import Counter, defaultdict
import random
import logging

logger = logging.getLogger(__name__)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# CONSTANTES LOTO FRANÃ‡AIS
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

# Loto FDJ: 5 numÃeros parmi 49 + 1 numÃero chance parmi 10
NUMERO_MIN = 1
NUMERO_MAX = 49
CHANCE_MIN = 1
CHANCE_MAX = 10
NB_NUMEROS = 5

# Gains par rang (approximatifs, varient selon jackpot et nombre de gagnants)
GAINS_PAR_RANG = {
    1: None,  # Jackpot (variable)
    2: 100_000,  # 5 bons
    3: 1_000,    # 4 bons + chance
    4: 500,      # 4 bons
    5: 50,       # 3 bons + chance
    6: 20,       # 3 bons
    7: 10,       # 2 bons + chance
    8: 5,        # 2 bons
    9: 2.20,     # 1 bon + chance (remboursement)
}

# Coût d'une grille simple
COUT_GRILLE = Decimal("2.20")

# NumÃeros populaires (dates anniversaires, Ã  Ãeviter pour maximiser gains potentiels)
NUMEROS_POPULAIRES = set(range(1, 32))  # 1-31 = dates

# ProbabilitÃe de gagner le jackpot (5 bons + chance)
PROBA_JACKPOT = 1 / 19_068_840  # ~1 sur 19 millions


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# ANALYSE DES FRÉQUENCES
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

def calculer_frequences_numeros(tirages: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calcule la frÃequence d'apparition de chaque numÃero.
    
    Args:
        tirages: Liste des tirages historiques
        
    Returns:
        Statistiques de frÃequence par numÃero
    """
    if not tirages:
        return {
            "frequences": {},
            "frequences_chance": {},
            "nb_tirages": 0
        }
    
    compteur_numeros = Counter()
    compteur_chance = Counter()
    dernier_tirage = {}
    
    for tirage in tirages:
        date_t = tirage.get("date_tirage")
        
        # Compter les 5 numÃeros principaux
        for i in range(1, 6):
            num = tirage.get(f"numero_{i}")
            if num:
                compteur_numeros[num] += 1
                dernier_tirage[num] = date_t
        
        # NumÃero chance
        chance = tirage.get("numero_chance")
        if chance:
            compteur_chance[chance] += 1
    
    nb_tirages = len(tirages)
    
    # Calculer stats par numÃero
    frequences = {}
    for num in range(NUMERO_MIN, NUMERO_MAX + 1):
        freq = compteur_numeros.get(num, 0)
        frequences[num] = {
            "frequence": freq,
            "pourcentage": round(freq / nb_tirages * 100, 2) if nb_tirages > 0 else 0,
            "dernier_tirage": dernier_tirage.get(num),
            "ecart": calculer_ecart(tirages, num) if tirages else 0
        }
    
    frequences_chance = {}
    for num in range(CHANCE_MIN, CHANCE_MAX + 1):
        freq = compteur_chance.get(num, 0)
        frequences_chance[num] = {
            "frequence": freq,
            "pourcentage": round(freq / nb_tirages * 100, 2) if nb_tirages > 0 else 0
        }
    
    return {
        "frequences": frequences,
        "frequences_chance": frequences_chance,
        "nb_tirages": nb_tirages
    }


def calculer_ecart(tirages: List[Dict[str, Any]], numero: int) -> int:
    """
    Calcule l'Ãecart (nombre de tirages depuis la dernière apparition).
    
    Args:
        tirages: Liste des tirages (du plus ancien au plus rÃecent)
        numero: NumÃero Ã  analyser
        
    Returns:
        Nombre de tirages depuis dernière apparition
    """
    for i, tirage in enumerate(reversed(tirages)):
        numeros = [tirage.get(f"numero_{j}") for j in range(1, 6)]
        if numero in numeros:
            return i
    return len(tirages)  # Jamais sorti


def identifier_numeros_chauds_froids(frequences: Dict[int, Dict], 
                                      nb_top: int = 10) -> Dict[str, List[int]]:
    """
    Identifie les numÃeros les plus et moins frÃequents.
    
    âš ï¸ Rappel: Ceci est purement informatif. Les tirages sont indÃependants.
    
    Args:
        frequences: Dict des frÃequences par numÃero
        nb_top: Nombre de numÃeros Ã  retourner par catÃegorie
        
    Returns:
        NumÃeros chauds et froids
    """
    if not frequences:
        return {"chauds": [], "froids": [], "retard": []}
    
    # Trier par frÃequence
    tries_freq = sorted(
        frequences.items(), 
        key=lambda x: x[1].get("frequence", 0), 
        reverse=True
    )
    
    # Trier par Ãecart (retard)
    tries_ecart = sorted(
        frequences.items(),
        key=lambda x: x[1].get("ecart", 0),
        reverse=True
    )
    
    return {
        "chauds": [num for num, _ in tries_freq[:nb_top]],
        "froids": [num for num, _ in tries_freq[-nb_top:]],
        "retard": [num for num, _ in tries_ecart[:nb_top]]
    }


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# ANALYSE DE PATTERNS (CuriositÃe statistique)
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

def analyser_patterns_tirages(tirages: List[Dict[str, Any]]) -> Dict[str, Any]:
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
        
        # ParitÃe
        pairs = sum(1 for n in numeros if n % 2 == 0)
        nb_pairs.append(pairs)
        nb_impairs.append(5 - pairs)
        
        # Écart min-max
        ecarts_min_max.append(numeros[-1] - numeros[0])
        
        # Paires frÃequentes
        for i in range(len(numeros)):
            for j in range(i + 1, len(numeros)):
                paires_frequentes[(numeros[i], numeros[j])] += 1
    
    if not sommes:
        return {}
    
    # Top 10 paires les plus frÃequentes
    top_paires = paires_frequentes.most_common(10)
    
    return {
        "somme_moyenne": round(sum(sommes) / len(sommes), 1),
        "somme_min": min(sommes),
        "somme_max": max(sommes),
        "pairs_moyen": round(sum(nb_pairs) / len(nb_pairs), 1),
        "ecart_moyen": round(sum(ecarts_min_max) / len(ecarts_min_max), 1),
        "paires_frequentes": [
            {"paire": list(paire), "frequence": freq} 
            for paire, freq in top_paires
        ],
        "distribution_parite": {
            "0_pair_5_impair": nb_pairs.count(0),
            "1_pair_4_impair": nb_pairs.count(1),
            "2_pair_3_impair": nb_pairs.count(2),
            "3_pair_2_impair": nb_pairs.count(3),
            "4_pair_1_impair": nb_pairs.count(4),
            "5_pair_0_impair": nb_pairs.count(5),
        }
    }


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# GÉNÉRATION DE GRILLES
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

def generer_grille_aleatoire() -> Dict[str, Any]:
    """
    GÃenère une grille complètement alÃeatoire.
    
    Returns:
        Grille avec 5 numÃeros + numÃero chance
    """
    numeros = sorted(random.sample(range(NUMERO_MIN, NUMERO_MAX + 1), NB_NUMEROS))
    chance = random.randint(CHANCE_MIN, CHANCE_MAX)
    
    return {
        "numeros": numeros,
        "numero_chance": chance,
        "source": "aleatoire"
    }


def generer_grille_eviter_populaires() -> Dict[str, Any]:
    """
    GÃenère une grille en Ãevitant les numÃeros populaires (1-31).
    
    StratÃegie: En cas de gain, partager avec moins de gagnants.
    
    Returns:
        Grille avec numÃeros moins populaires
    """
    # PrivilÃegier les numÃeros 32-49 (moins jouÃes)
    pool_prioritaire = list(range(32, NUMERO_MAX + 1))  # 18 numÃeros
    pool_secondaire = list(range(NUMERO_MIN, 32))  # 31 numÃeros
    
    # Prendre 3-4 numÃeros du pool prioritaire, 1-2 du secondaire
    nb_prioritaire = random.randint(3, 4)
    nb_secondaire = NB_NUMEROS - nb_prioritaire
    
    numeros = (
        random.sample(pool_prioritaire, nb_prioritaire) +
        random.sample(pool_secondaire, nb_secondaire)
    )
    numeros = sorted(numeros)
    chance = random.randint(CHANCE_MIN, CHANCE_MAX)
    
    return {
        "numeros": numeros,
        "numero_chance": chance,
        "source": "eviter_populaires",
        "note": "Évite les dates (1-31) pour maximiser gains potentiels"
    }


def generer_grille_equilibree(patterns: Dict[str, Any]) -> Dict[str, Any]:
    """
    GÃenère une grille "ÃequilibrÃee" basÃee sur les patterns historiques.
    
    âš ï¸ Ceci n'augmente PAS les chances de gagner, mais produit
    une grille statistiquement "typique".
    
    Args:
        patterns: RÃesultat de analyser_patterns_tirages()
        
    Returns:
        Grille ÃequilibrÃee
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
        
        # Score = proximitÃe avec les moyennes
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
        "note": f"Somme proche de la moyenne ({somme_cible})"
    }


def generer_grille_chauds_froids(frequences: Dict[int, Dict], 
                                  strategie: str = "mixte") -> Dict[str, Any]:
    """
    GÃenère une grille basÃee sur les numÃeros chauds ou froids.
    
    âš ï¸ Rappel: Statistiquement inutile, mais psychologiquement satisfaisant.
    
    Args:
        frequences: FrÃequences des numÃeros
        strategie: "chauds", "froids", ou "mixte"
        
    Returns:
        Grille basÃee sur la stratÃegie
    """
    chauds_froids = identifier_numeros_chauds_froids(frequences)
    
    if strategie == "chauds":
        pool = chauds_froids["chauds"][:20]
    elif strategie == "froids":
        pool = chauds_froids["froids"][:20]
    else:  # mixte
        pool = chauds_froids["chauds"][:10] + chauds_froids["froids"][:10]
    
    # ComplÃeter si pas assez
    while len(pool) < NB_NUMEROS:
        pool.append(random.randint(NUMERO_MIN, NUMERO_MAX))
    pool = list(set(pool))
    
    numeros = sorted(random.sample(pool, min(NB_NUMEROS, len(pool))))
    
    # ComplÃeter si besoin
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
        "note": f"BasÃe sur numÃeros {strategie}"
    }


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# VÉRIFICATION DES GAINS
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

def verifier_grille(grille: Dict[str, Any], tirage: Dict[str, Any]) -> Dict[str, Any]:
    """
    VÃerifie une grille contre un tirage et calcule les gains.
    
    Args:
        grille: Grille jouÃee
        tirage: RÃesultat du tirage
        
    Returns:
        RÃesultat avec rang et gain
    """
    # NumÃeros du tirage
    numeros_tirage = set([tirage.get(f"numero_{i}") for i in range(1, 6)])
    chance_tirage = tirage.get("numero_chance")
    
    # NumÃeros de la grille
    numeros_grille = set(grille.get("numeros", []))
    chance_grille = grille.get("numero_chance")
    
    # Compter les bons numÃeros
    bons_numeros = len(numeros_tirage & numeros_grille)
    chance_ok = chance_grille == chance_tirage
    
    # DÃeterminer le rang
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
        "description": f"{bons_numeros} numÃeros" + (" + chance" if chance_ok else "")
    }


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# SIMULATION & PERFORMANCE
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

def simuler_strategie(
    tirages: List[Dict[str, Any]],
    strategie: str = "aleatoire",
    nb_grilles_par_tirage: int = 1,
    frequences: Optional[Dict] = None,
    patterns: Optional[Dict] = None
) -> Dict[str, Any]:
    """
    Simule une stratÃegie sur l'historique des tirages.
    
    Args:
        tirages: Historique des tirages
        strategie: "aleatoire", "eviter_populaires", "equilibree", "chauds", "froids"
        nb_grilles_par_tirage: Nombre de grilles jouÃees par tirage
        frequences: FrÃequences prÃe-calculÃees
        patterns: Patterns prÃe-calculÃes
        
    Returns:
        RÃesultats de la simulation
    """
    if not tirages:
        return {"erreur": "Aucun tirage disponible"}
    
    resultats = []
    mises_totales = Decimal("0.00")
    gains_totaux = Decimal("0.00")
    
    for tirage in tirages:
        for _ in range(nb_grilles_par_tirage):
            # GÃenÃerer grille selon stratÃegie
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
            
            # VÃerifier contre le tirage
            resultat = verifier_grille(grille, tirage)
            
            mises_totales += COUT_GRILLE
            gains_totaux += resultat.get("gain", Decimal("0.00"))
            
            resultats.append({
                "date": tirage.get("date_tirage"),
                "grille": grille,
                "resultat": resultat
            })
    
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
        "roi": float((gains_totaux - mises_totales) / mises_totales * 100) if mises_totales > 0 else 0,
        "nb_gagnants": nb_gagnants,
        "taux_gain": round(nb_gagnants / len(resultats) * 100, 2) if resultats else 0,
        "distribution_rangs": dict(rangs),
        "details": resultats[-10:]  # 10 derniers pour affichage
    }


def calculer_esperance_mathematique() -> Dict[str, Any]:
    """
    Calcule l'espÃerance mathÃematique du Loto.
    
    Spoiler: Elle est nÃegative (c'est un jeu d'argent).
    
    Returns:
        EspÃerance et probabilitÃes
    """
    # ProbabilitÃes exactes du Loto français
    probas = {
        1: 1 / 19_068_840,      # 5 + chance
        2: 1 / 2_118_760,       # 5
        3: 1 / 86_677,          # 4 + chance
        4: 1 / 9_631,           # 4
        5: 1 / 2_016,           # 3 + chance
        6: 1 / 224,             # 3
        7: 1 / 144,             # 2 + chance
        8: 1 / 16,              # 2
        9: 1 / 16,              # 1 + chance
    }
    
    # Calcul espÃerance (jackpot moyen estimÃe Ã  5Mâ‚¬)
    jackpot_moyen = 5_000_000
    gains_esperes = (
        probas[1] * jackpot_moyen +
        probas[2] * GAINS_PAR_RANG[2] +
        probas[3] * GAINS_PAR_RANG[3] +
        probas[4] * GAINS_PAR_RANG[4] +
        probas[5] * GAINS_PAR_RANG[5] +
        probas[6] * GAINS_PAR_RANG[6] +
        probas[7] * GAINS_PAR_RANG[7] +
        probas[8] * GAINS_PAR_RANG[8] +
        probas[9] * GAINS_PAR_RANG[9]
    )
    
    esperance = gains_esperes - float(COUT_GRILLE)
    
    return {
        "cout_grille": float(COUT_GRILLE),
        "gains_esperes": round(gains_esperes, 4),
        "esperance": round(esperance, 4),
        "perte_moyenne_pct": round((1 - gains_esperes / float(COUT_GRILLE)) * 100, 1),
        "probabilites": {rang: f"1/{int(1/p):,}" for rang, p in probas.items()},
        "conclusion": (
            f"En moyenne, vous perdez {abs(esperance):.2f}â‚¬ par grille jouÃee. "
            f"Le Loto reverse environ {gains_esperes/float(COUT_GRILLE)*100:.0f}% des mises."
        )
    }


def comparer_strategies(tirages: List[Dict[str, Any]], 
                        nb_simulations: int = 100) -> Dict[str, Any]:
    """
    Compare plusieurs stratÃegies sur les mêmes tirages.
    
    Args:
        tirages: Historique des tirages
        nb_simulations: Nombre de simulations par stratÃegie
        
    Returns:
        Comparaison des performances
    """
    if not tirages:
        return {"erreur": "Aucun tirage"}
    
    # PrÃe-calculer stats
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
            patterns=patterns
        )
        resultats[strat] = {
            "roi": res.get("roi", 0),
            "taux_gain": res.get("taux_gain", 0),
            "nb_gagnants": res.get("nb_gagnants", 0)
        }
    
    # Classement par ROI
    classement = sorted(resultats.items(), key=lambda x: x[1]["roi"], reverse=True)
    
    return {
        "nb_tirages": len(tirages),
        "resultats": resultats,
        "classement": [s[0] for s in classement],
        "meilleure_strategie": classement[0][0] if classement else None,
        "note": "âš ï¸ Ces rÃesultats varient alÃeatoirement. Aucune stratÃegie n'est meilleure Ã  long terme."
    }
