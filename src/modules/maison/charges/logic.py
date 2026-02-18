"""
Charges - Logique métier.

Fonctions de calcul et d'analyse:
- calculer_stats_globales: Stats pour badges et éco-score
- calculer_eco_score_avance: Éco-score multi-facteurs
- calculer_streak: Jours consécutifs sous la moyenne
- analyser_consommation: Analyse détaillée par énergie
- detecter_anomalies: Détection de pics/anomalies
- obtenir_badges_obtenus: Liste des badges débloqués
- simuler_economies_energie: Simulation d'économies
"""

from decimal import Decimal

from .constantes import BADGES_DEFINITIONS, ENERGIES


def calculer_stats_globales(factures: list[dict]) -> dict:
    """Calcule les statistiques globales pour badges et éco-score."""
    stats = {
        "nb_factures": len(factures),
        "streak": 0,
        "eco_score": 50,
        "energies_suivies": 0,
        "eau_ratio": 1.0,
        "elec_ratio": 1.0,
        "gaz_ratio": 1.0,
    }

    if not factures:
        return stats

    # Compter les énergies suivies
    energies_presentes = set(f.get("type") for f in factures)
    stats["energies_suivies"] = len(energies_presentes)

    # Calculer ratios par énergie
    for energie_id, config in ENERGIES.items():
        factures_energie = [f for f in factures if f.get("type") == energie_id]
        if factures_energie:
            conso_moyenne = sum(f.get("consommation", 0) for f in factures_energie) / len(
                factures_energie
            )
            ratio = (
                conso_moyenne / config["conso_moyenne_mois"]
                if config["conso_moyenne_mois"] > 0
                else 1.0
            )

            if energie_id == "eau":
                stats["eau_ratio"] = ratio
            elif energie_id == "electricite":
                stats["elec_ratio"] = ratio
            elif energie_id == "gaz":
                stats["gaz_ratio"] = ratio

    # Calculer éco-score
    stats["eco_score"] = calculer_eco_score_avance(factures, stats)
    stats["streak"] = calculer_streak(factures)

    return stats


def calculer_eco_score_avance(factures: list[dict], stats: dict) -> int:
    """Calcule l'éco-score avancé basé sur multiples facteurs."""
    if not factures:
        return 50

    score = 50

    # Points pour chaque énergie sous la moyenne
    if stats.get("eau_ratio", 1) < 0.8:
        score += 15
    elif stats.get("eau_ratio", 1) < 1.0:
        score += 5
    elif stats.get("eau_ratio", 1) > 1.2:
        score -= 10

    if stats.get("elec_ratio", 1) < 0.85:
        score += 15
    elif stats.get("elec_ratio", 1) < 1.0:
        score += 5
    elif stats.get("elec_ratio", 1) > 1.2:
        score -= 10

    if stats.get("gaz_ratio", 1) < 0.9:
        score += 10
    elif stats.get("gaz_ratio", 1) < 1.0:
        score += 5
    elif stats.get("gaz_ratio", 1) > 1.2:
        score -= 10

    if stats.get("energies_suivies", 0) >= 3:
        score += 5

    streak = stats.get("streak", 0)
    if streak >= 30:
        score += 10
    elif streak >= 7:
        score += 5

    return max(0, min(100, score))


def calculer_streak(factures: list[dict]) -> int:
    """Calcule le streak de jours sous la moyenne."""
    if not factures:
        return 0

    streak = 0
    for facture in sorted(factures, key=lambda f: f.get("date", ""), reverse=True):
        energie_id = facture.get("type")
        if energie_id not in ENERGIES:
            continue

        config = ENERGIES[energie_id]
        conso = facture.get("consommation", 0)
        moyenne = config["conso_moyenne_mois"]

        if conso < moyenne:
            streak += 7
        else:
            break

    return min(streak, 90)


def analyser_consommation(factures: list[dict], energie: str) -> dict:
    """Analyse la consommation d'une énergie avec détails."""
    factures_energie = [f for f in factures if f.get("type") == energie]

    if not factures_energie:
        return {
            "total_conso": 0,
            "total_cout": Decimal("0"),
            "tendance": "stable",
            "nb_factures": 0,
            "moyenne_conso": 0,
            "ratio": 1.0,
        }

    config = ENERGIES.get(energie, {})
    total_conso = sum(f.get("consommation", 0) for f in factures_energie)
    total_cout = sum(Decimal(str(f.get("montant", 0))) for f in factures_energie)
    moyenne_conso = total_conso / len(factures_energie)
    ratio = (
        moyenne_conso / config.get("conso_moyenne_mois", 100)
        if config.get("conso_moyenne_mois")
        else 1.0
    )

    tendance = "stable"
    if len(factures_energie) >= 2:
        factures_triees = sorted(factures_energie, key=lambda f: f.get("date", ""))
        moitie = len(factures_triees) // 2
        premiere = sum(f.get("consommation", 0) for f in factures_triees[:moitie])
        seconde = sum(f.get("consommation", 0) for f in factures_triees[moitie:])

        if seconde > premiere * 1.1:
            tendance = "hausse"
        elif seconde < premiere * 0.9:
            tendance = "baisse"

    return {
        "total_conso": total_conso,
        "total_cout": total_cout,
        "tendance": tendance,
        "nb_factures": len(factures_energie),
        "moyenne_conso": moyenne_conso,
        "ratio": ratio,
    }


def detecter_anomalies(factures: list[dict]) -> list[dict]:
    """Détecte les anomalies dans les consommations."""
    anomalies = []
    if not factures:
        return anomalies

    for energie_id, config in ENERGIES.items():
        factures_energie = [f for f in factures if f.get("type") == energie_id]
        if not factures_energie:
            continue

        consos = [f.get("consommation", 0) for f in factures_energie if f.get("consommation")]
        if not consos:
            continue

        moyenne = sum(consos) / len(consos)
        moyenne_ref = config.get("conso_moyenne_mois", 100)

        for f in factures_energie:
            conso = f.get("consommation", 0)
            if conso > moyenne * 1.5:
                anomalies.append(
                    {
                        "titre": f"Pic de consommation {config['label']}",
                        "description": f"{f.get('date', 'Récemment')}: {conso:.0f} {config['unite']} (+{((conso / moyenne) - 1) * 100:.0f}% vs votre moyenne)",
                        "conseil": "Vérifiez s'il y a eu un événement particulier",
                        "energie": energie_id,
                        "severite": "warning",
                    }
                )

        if moyenne > moyenne_ref * 1.3:
            ecart = ((moyenne / moyenne_ref) - 1) * 100
            anomalies.append(
                {
                    "titre": f"Consommation {config['label']} élevée",
                    "description": f"Votre consommation est {ecart:.0f}% au-dessus de la moyenne nationale",
                    "conseil": f"Consultez nos conseils pour réduire votre {config['label'].lower()}",
                    "energie": energie_id,
                    "severite": "danger" if ecart > 50 else "warning",
                }
            )

    return anomalies[:5]


def obtenir_badges_obtenus(stats: dict) -> list[str]:
    """Retourne la liste des IDs de badges obtenus."""
    obtenus = []
    for badge_def in BADGES_DEFINITIONS:
        if badge_def["condition"](stats):
            obtenus.append(badge_def["id"])
    return obtenus


def simuler_economies_energie(energie: str, action: str) -> dict:
    """Simule les économies pour une action donnée."""
    economies_actions = {
        "electricite": {
            "led": {"pct": 0.80, "euros": 40},
            "veille": {"pct": 0.10, "euros": 50},
            "thermostat": {"pct": 0.15, "euros": 200},
        },
        "gaz": {
            "1degre": {"pct": 0.07, "euros": 150},
            "isolation": {"pct": 0.30, "euros": 400},
            "chaudiere": {"pct": 0.10, "euros": 120},
        },
        "eau": {
            "douche": {"pct": 0.30, "euros": 200},
            "mousseur": {"pct": 0.50, "euros": 50},
            "fuite": {"pct": 0.15, "euros": 150},
        },
    }

    action_key = action.lower().replace(" ", "_")
    actions = economies_actions.get(energie, {})
    if action_key in actions:
        return actions[action_key]
    return {"pct": 0.10, "euros": 100}
