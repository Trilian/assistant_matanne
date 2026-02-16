"""
Charges - Point d'entrée principal.

Module de suivi des charges et consommations énergétiques.
Fonctionnalités avancées:
- Éco-score gamifié avec badges
- Détection d'anomalies
- Simulation économies IA
- Comparaisons périodiques
"""

import asyncio
import logging
from datetime import date, datetime, timedelta
from decimal import Decimal

import streamlit as st

from .styles import CHARGES_CSS

logger = logging.getLogger(__name__)


# =============================================================================
# CONSTANTES ÉNERGIE
# =============================================================================

ENERGIES = {
    "electricite": {
        "emoji": "⚡",
        "couleur": "#FFEB3B",
        "unite": "kWh",
        "label": "Électricité",
        "prix_moyen": Decimal("0.22"),
        "conso_moyenne_mois": 400,
    },
    "gaz": {
        "emoji": "🔥",
        "couleur": "#FF5722",
        "unite": "m³",
        "label": "Gaz",
        "prix_moyen": Decimal("0.11"),
        "conso_moyenne_mois": 150,
    },
    "eau": {
        "emoji": "💧",
        "couleur": "#2196F3",
        "unite": "m³",
        "label": "Eau",
        "prix_moyen": Decimal("4.50"),
        "conso_moyenne_mois": 10,
    },
}

# Définitions des badges gamifiés
BADGES_DEFINITIONS = [
    {
        "id": "econome_eau",
        "nom": "Économe en eau",
        "emoji": "💧",
        "description": "Consommation eau -20% vs moyenne",
        "condition": lambda stats: stats.get("eau_ratio", 1) < 0.8,
        "categorie": "eau",
    },
    {
        "id": "econome_elec",
        "nom": "Électricité maîtrisée",
        "emoji": "⚡",
        "description": "Consommation élec -15% vs moyenne",
        "condition": lambda stats: stats.get("elec_ratio", 1) < 0.85,
        "categorie": "energie",
    },
    {
        "id": "econome_gaz",
        "nom": "Chauffage optimisé",
        "emoji": "🔥",
        "description": "Consommation gaz -10% vs moyenne",
        "condition": lambda stats: stats.get("gaz_ratio", 1) < 0.9,
        "categorie": "energie",
    },
    {
        "id": "streak_7",
        "nom": "Série de 7 jours",
        "emoji": "🔥",
        "description": "7 jours consécutifs sous la moyenne",
        "condition": lambda stats: stats.get("streak", 0) >= 7,
        "categorie": "general",
    },
    {
        "id": "streak_30",
        "nom": "Champion du mois",
        "emoji": "🏆",
        "description": "30 jours sous la moyenne",
        "condition": lambda stats: stats.get("streak", 0) >= 30,
        "categorie": "general",
    },
    {
        "id": "premiere_facture",
        "nom": "Premier pas",
        "emoji": "🎯",
        "description": "Première facture enregistrée",
        "condition": lambda stats: stats.get("nb_factures", 0) >= 1,
        "categorie": "general",
    },
    {
        "id": "suivi_complet",
        "nom": "Suivi complet",
        "emoji": "📊",
        "description": "Les 3 énergies suivies",
        "condition": lambda stats: stats.get("energies_suivies", 0) >= 3,
        "categorie": "general",
    },
    {
        "id": "eco_warrior",
        "nom": "Éco-warrior",
        "emoji": "🌿",
        "description": "Score éco ≥ 80",
        "condition": lambda stats: stats.get("eco_score", 0) >= 80,
        "categorie": "general",
    },
]

# Conseils d'économies par énergie
CONSEILS_ECONOMIES = {
    "electricite": [
        {
            "emoji": "💡",
            "titre": "Passez aux LED",
            "desc": "Économie ~80% sur l'éclairage",
            "economie": "40€/an",
        },
        {
            "emoji": "🔌",
            "titre": "Multiprises à interrupteur",
            "desc": "Évitez les appareils en veille",
            "economie": "50€/an",
        },
        {
            "emoji": "🌡️",
            "titre": "Thermostat intelligent",
            "desc": "Chauffage optimisé = -15% facture",
            "economie": "200€/an",
        },
        {
            "emoji": "🧊",
            "titre": "Dégivrez régulièrement",
            "desc": "Un frigo givré consomme +30%",
            "economie": "30€/an",
        },
        {
            "emoji": "🌀",
            "titre": "Lavage froid",
            "desc": "Laver à 30°C au lieu de 60°C",
            "economie": "25€/an",
        },
    ],
    "gaz": [
        {
            "emoji": "🌡️",
            "titre": "Baissez d'1°C",
            "desc": "Économie de 7% sur le chauffage",
            "economie": "150€/an",
        },
        {
            "emoji": "🏠",
            "titre": "Isolation",
            "desc": "30% de pertes par le toit non isolé",
            "economie": "400€/an",
        },
        {
            "emoji": "🚿",
            "titre": "Douche < bain",
            "desc": "50L vs 150L d'eau chaude",
            "economie": "100€/an",
        },
        {
            "emoji": "🔧",
            "titre": "Entretien chaudière",
            "desc": "Une chaudière bien réglée = -10%",
            "economie": "120€/an",
        },
    ],
    "eau": [
        {
            "emoji": "🚿",
            "titre": "Douche courte",
            "desc": "5 min = 60L vs 200L bain",
            "economie": "200€/an",
        },
        {
            "emoji": "💧",
            "titre": "Mousseurs",
            "desc": "Économisez 50% sur les robinets",
            "economie": "50€/an",
        },
        {
            "emoji": "🌧️",
            "titre": "Récupérateur d'eau",
            "desc": "Pour l'arrosage du jardin",
            "economie": "100€/an",
        },
        {
            "emoji": "🔧",
            "titre": "Réparez les fuites",
            "desc": "Un robinet = 120L/jour perdus",
            "economie": "150€/an",
        },
    ],
}

# Niveaux éco-score
NIVEAUX_ECO = [
    {"min": 90, "nom": "Éco-Champion", "emoji": "🏆", "class": "gold"},
    {"min": 75, "nom": "Éco-Expert", "emoji": "🥈", "class": "silver"},
    {"min": 60, "nom": "Éco-Apprenti", "emoji": "🥉", "class": "bronze"},
    {"min": 40, "nom": "Éco-Débutant", "emoji": "🌱", "class": "beginner"},
    {"min": 0, "nom": "À améliorer", "emoji": "📈", "class": "beginner"},
]


# =============================================================================
# COMPOSANTS UI GAMIFIÉS
# =============================================================================


def afficher_header():
    """Affiche le header du module."""
    st.markdown(
        """
    <div class="charges-header">
        <h1>💡 Charges & Énergie</h1>
        <p>Suivez vos consommations, relevez les défis éco et gagnez des badges !</p>
    </div>
    """,
        unsafe_allow_html=True,
    )


def afficher_eco_score_gamifie(score: int, variation: int | None, streak: int):
    """Affiche l'éco-score avec animation et gamification."""
    # Déterminer couleur selon score
    if score >= 80:
        couleur = "#27ae60"
        stroke_color = "#2ecc71"
    elif score >= 60:
        couleur = "#f39c12"
        stroke_color = "#f1c40f"
    elif score >= 40:
        couleur = "#e67e22"
        stroke_color = "#d35400"
    else:
        couleur = "#e74c3c"
        stroke_color = "#c0392b"

    # Calculer l'angle pour le cercle SVG
    circumference = 2 * 3.14159 * 70
    stroke_dasharray = (score / 100) * circumference

    # Déterminer niveau et classe
    niveau = next((n for n in NIVEAUX_ECO if score >= n["min"]), NIVEAUX_ECO[-1])

    # Variation text
    if variation is not None:
        if variation > 0:
            var_html = f'<div class="eco-score-variation up">📈 +{variation} pts</div>'
        elif variation < 0:
            var_html = f'<div class="eco-score-variation down">📉 {variation} pts</div>'
        else:
            var_html = '<div class="eco-score-variation stable">➡️ Stable</div>'
    else:
        var_html = '<div class="eco-score-variation stable">Première mesure</div>'

    st.markdown(
        f"""
    <div class="eco-score-container animate-in">
        <div class="eco-score-ring">
            <svg width="180" height="180" viewBox="0 0 180 180">
                <circle cx="90" cy="90" r="70" fill="none" stroke="#2d3748" stroke-width="12" opacity="0.3"/>
                <circle
                    cx="90" cy="90" r="70"
                    fill="none"
                    stroke="{stroke_color}"
                    stroke-width="12"
                    stroke-linecap="round"
                    stroke-dasharray="{stroke_dasharray} {circumference}"
                    transform="rotate(-90 90 90)"
                    style="filter: drop-shadow(0 0 10px {stroke_color});"
                />
            </svg>
            <div class="eco-score-value" style="color: {couleur};">{score}</div>
        </div>
        <div class="eco-score-label">ÉCO-SCORE</div>
        {var_html}
        <div class="eco-level {niveau['class']}">{niveau['emoji']} {niveau['nom']}</div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Streak counter (si >= 3)
    if streak >= 3:
        st.markdown(
            f"""
        <div class="streak-counter" style="margin-top: 1rem;">
            <span class="fire">🔥</span>
            <div>
                <span class="count">{streak}</span>
                <span class="label">jours d'affilée sous la moyenne</span>
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )


def afficher_badges_collection(badges_obtenus: list[str], stats: dict):
    """Affiche la collection de badges avec état locked/unlocked."""
    st.markdown("### 🏅 Collection de badges")

    cols = st.columns(4)

    for i, badge_def in enumerate(BADGES_DEFINITIONS):
        badge_id = badge_def["id"]
        est_obtenu = badge_id in badges_obtenus or badge_def["condition"](stats)

        # Vérifier si nouvellement obtenu
        is_new = badge_id not in st.session_state.get("badges_vus", []) and est_obtenu

        locked_class = "" if est_obtenu else "locked"
        new_class = "new" if is_new else ""

        with cols[i % 4]:
            st.markdown(
                f"""
            <div class="badge-eco {locked_class} {new_class}">
                <span class="icon">{badge_def['emoji']}</span>
                <span class="name">{badge_def['nom']}</span>
                {'<span class="date">Obtenu ✓</span>' if est_obtenu else '<span class="date">🔒 Verrouillé</span>'}
            </div>
            """,
                unsafe_allow_html=True,
            )

    # Mettre à jour badges vus
    if badges_obtenus:
        st.session_state.badges_vus = badges_obtenus


def afficher_energie_card(
    energie_id: str, data: dict, conso: float, cout: Decimal, tendance: str, ratio: float
):
    """Affiche une carte énergie avec barre de progression."""
    trend_class = "down" if tendance == "baisse" else ("up" if tendance == "hausse" else "stable")
    trend_icon = "📉" if tendance == "baisse" else ("📈" if tendance == "hausse" else "➡️")

    # Barre de progression vs moyenne
    progress_pct = min(100, ratio * 100)
    progress_class = "good" if ratio < 0.9 else ("warning" if ratio < 1.1 else "bad")

    st.markdown(
        f"""
    <div class="energie-card {energie_id} animate-in">
        <div class="header">
            <div>
                <span class="icon">{data['emoji']}</span>
                <span class="title">{data['label']}</span>
            </div>
            <span class="trend {trend_class}">{trend_icon} {tendance.capitalize()}</span>
        </div>
        <div class="value">{conso:.0f} <span class="unit">{data['unite']}</span></div>
        <div style="font-size: 1rem; color: #718096;">{cout:.2f} € ce mois</div>
        <div class="progress-bar-compare">
            <div class="fill {progress_class}" style="width: {progress_pct}%"></div>
        </div>
        <div style="font-size: 0.8rem; color: #a0aec0; margin-top: 0.5rem;">
            {ratio*100:.0f}% de la moyenne nationale
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )


def afficher_anomalies(anomalies: list[dict]):
    """Affiche les alertes d'anomalies détectées."""
    if not anomalies:
        return

    st.markdown("### ⚠️ Alertes détectées")

    for anomalie in anomalies:
        st.markdown(
            f"""
        <div class="anomalie-alert animate-in">
            <span class="icon">⚠️</span>
            <div class="content">
                <div class="title">{anomalie.get('titre', 'Anomalie détectée')}</div>
                <div class="description">{anomalie.get('description', '')}</div>
                <div class="action">💡 {anomalie.get('conseil', 'Vérifiez vos équipements')}</div>
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )


def afficher_simulation_economies(energie: str, economie_estimee: Decimal, periode: str = "par an"):
    """Affiche le résultat de simulation d'économies."""
    st.markdown(
        f"""
    <div class="simulation-card animate-in">
        <div class="header">
            <span>{ENERGIES[energie]['emoji']} Simulation {ENERGIES[energie]['label']}</span>
        </div>
        <div class="result">
            <div class="savings">💰 {economie_estimee:.0f} €</div>
            <div class="period">{periode}</div>
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )


def afficher_conseil_eco(conseil: dict):
    """Affiche un conseil d'économie."""
    st.markdown(
        f"""
    <div class="conseil-eco">
        <span class="icon">{conseil['emoji']}</span>
        <div class="text">
            <div class="title">{conseil['titre']}</div>
            <div class="desc">{conseil['desc']}</div>
        </div>
        <span class="economie">{conseil['economie']}</span>
    </div>
    """,
        unsafe_allow_html=True,
    )


def afficher_facture_item(facture: dict, energie_data: dict, index: int):
    """Affiche une facture avec actions."""
    conso_text = ""
    if facture.get("consommation"):
        conso_text = f" • {facture['consommation']:.0f} {energie_data.get('unite', '')}"

    st.markdown(
        f"""
    <div class="facture-item animate-in">
        <div class="icon">{energie_data.get('emoji', '📄')}</div>
        <div class="details">
            <div class="type">{energie_data.get('label', facture.get('type'))}</div>
            <div class="date">{facture.get('date')} • {facture.get('fournisseur', 'Non précisé')}</div>
            <div class="conso">{conso_text}</div>
        </div>
        <div class="montant">{facture.get('montant', 0):.2f} €</div>
    </div>
    """,
        unsafe_allow_html=True,
    )


# =============================================================================
# LOGIQUE MÉTIER (CALCULS & ANALYSE)
# =============================================================================


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

    # Calculer streak (simulation simple)
    stats["streak"] = calculer_streak(factures)

    return stats


def calculer_eco_score_avance(factures: list[dict], stats: dict) -> int:
    """Calcule l'éco-score avancé basé sur multiples facteurs."""
    if not factures:
        return 50  # Score neutre par défaut

    score = 50  # Base

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

    # Bonus pour suivi complet
    if stats.get("energies_suivies", 0) >= 3:
        score += 5

    # Bonus pour streak
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

    # Simplification: compte le nombre de factures récentes sous la moyenne
    streak = 0

    for facture in sorted(factures, key=lambda f: f.get("date", ""), reverse=True):
        energie_id = facture.get("type")
        if energie_id not in ENERGIES:
            continue

        config = ENERGIES[energie_id]
        conso = facture.get("consommation", 0)
        moyenne = config["conso_moyenne_mois"]

        if conso < moyenne:
            streak += 7  # Chaque facture représente ~1 semaine
        else:
            break

    return min(streak, 90)  # Max 3 mois


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

    # Calculer tendance
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

        # Vérifier pics
        for f in factures_energie:
            conso = f.get("consommation", 0)
            if conso > moyenne * 1.5:
                anomalies.append(
                    {
                        "titre": f"Pic de consommation {config['label']}",
                        "description": f"{f.get('date', 'Récemment')}: {conso:.0f} {config['unite']} (+{((conso/moyenne)-1)*100:.0f}% vs votre moyenne)",
                        "conseil": "Vérifiez s'il y a eu un événement particulier",
                        "energie": energie_id,
                        "severite": "warning",
                    }
                )

        # Vérifier vs moyenne nationale
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

    return anomalies[:5]  # Max 5 anomalies


def obtenir_badges_obtenus(stats: dict) -> list[str]:
    """Retourne la liste des IDs de badges obtenus."""
    obtenus = []
    for badge_def in BADGES_DEFINITIONS:
        if badge_def["condition"](stats):
            obtenus.append(badge_def["id"])
    return obtenus


def simuler_economies_energie(energie: str, action: str) -> dict:
    """Simule les économies pour une action donnée."""
    # Économies typiques par action
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

    config = ENERGIES.get(energie, {})
    action_key = action.lower().replace(" ", "_")

    actions = economies_actions.get(energie, {})
    if action_key in actions:
        return actions[action_key]

    # Estimation par défaut
    return {"pct": 0.10, "euros": 100}


# =============================================================================
# ONGLETS PRINCIPAUX
# =============================================================================


def onglet_dashboard(factures: list[dict]):
    """Onglet tableau de bord gamifié."""
    st.subheader("📊 Vue d'ensemble")

    # Calculer stats globales
    stats = calculer_stats_globales(factures)
    eco_score = stats["eco_score"]
    streak = stats["streak"]
    badges_obtenus = obtenir_badges_obtenus(stats)

    # Calculer variation (si score précédent en session)
    prev_score = st.session_state.get("prev_eco_score")
    variation = eco_score - prev_score if prev_score is not None else None
    st.session_state.prev_eco_score = eco_score

    col1, col2 = st.columns([1, 2])

    with col1:
        # Éco-score gamifié
        afficher_eco_score_gamifie(eco_score, variation, streak)

    with col2:
        # Cartes énergie
        if not factures:
            st.info(
                "📊 Ajoutez vos premières factures pour voir votre tableau de bord énergétique !"
            )
        else:
            for energie_id, energie_data in ENERGIES.items():
                analyse = analyser_consommation(factures, energie_id)
                if analyse["nb_factures"] > 0:
                    afficher_energie_card(
                        energie_id,
                        energie_data,
                        analyse["moyenne_conso"],
                        analyse["total_cout"] / max(1, analyse["nb_factures"]),
                        analyse["tendance"],
                        analyse["ratio"],
                    )

    # Détection d'anomalies
    anomalies = detecter_anomalies(factures)
    if anomalies:
        st.divider()
        afficher_anomalies(anomalies)

    # Badges collection
    st.divider()
    afficher_badges_collection(badges_obtenus, stats)


def onglet_factures(factures: list[dict]):
    """Onglet gestion des factures."""
    st.subheader("📄 Mes Factures")

    # Stats rapides
    if factures:
        col1, col2, col3 = st.columns(3)
        with col1:
            total = sum(Decimal(str(f.get("montant", 0))) for f in factures)
            st.metric("Total factures", f"{total:.2f} €", f"{len(factures)} factures")
        with col2:
            mois_courant = date.today().strftime("%Y-%m")
            factures_mois = [f for f in factures if f.get("date", "").startswith(mois_courant)]
            total_mois = sum(Decimal(str(f.get("montant", 0))) for f in factures_mois)
            st.metric("Ce mois", f"{total_mois:.2f} €")
        with col3:
            # Dernière facture
            if factures:
                derniere = max(factures, key=lambda f: f.get("date", ""))
                st.metric("Dernière", derniere.get("date", "N/A"))

    st.divider()

    # Bouton ajouter
    if st.button("➕ Ajouter une facture", type="primary", use_container_width=True):
        st.session_state.charges_mode_ajout = True

    # Mode ajout
    if st.session_state.get("charges_mode_ajout"):
        st.markdown("### Nouvelle facture")

        with st.form("form_facture"):
            type_energie = st.selectbox(
                "Type d'énergie",
                options=list(ENERGIES.keys()),
                format_func=lambda x: f"{ENERGIES[x]['emoji']} {ENERGIES[x]['label']}",
            )

            col1, col2 = st.columns(2)
            with col1:
                montant = st.number_input("Montant (€)", min_value=0.0, value=50.0, step=5.0)
            with col2:
                consommation = st.number_input(
                    f"Consommation ({ENERGIES[type_energie]['unite']})",
                    min_value=0.0,
                    value=float(ENERGIES[type_energie]["conso_moyenne_mois"]),
                    step=10.0,
                )

            col3, col4 = st.columns(2)
            with col3:
                date_facture = st.date_input("Date de facturation", value=date.today())
            with col4:
                fournisseur = st.text_input("Fournisseur", placeholder="EDF, Engie, Veolia...")

            col_submit = st.columns([1, 1])
            with col_submit[0]:
                submitted = st.form_submit_button(
                    "✅ Enregistrer", type="primary", use_container_width=True
                )
            with col_submit[1]:
                cancelled = st.form_submit_button("❌ Annuler", use_container_width=True)

            if submitted:
                nouvelle_facture = {
                    "type": type_energie,
                    "montant": montant,
                    "consommation": consommation,
                    "date": date_facture.isoformat(),
                    "fournisseur": fournisseur or None,
                    "date_ajout": date.today().isoformat(),
                }
                factures.append(nouvelle_facture)
                st.session_state.factures_charges = factures
                st.session_state.charges_mode_ajout = False
                st.success("✅ Facture enregistrée ! Vérifiez votre éco-score.")
                st.balloons()
                st.rerun()

            if cancelled:
                st.session_state.charges_mode_ajout = False
                st.rerun()

    else:
        # Liste des factures
        if not factures:
            st.info("📄 Aucune facture enregistrée. Ajoutez vos factures pour commencer le suivi !")

            # Aide pour démarrer
            st.markdown("""
            **Comment commencer ?**
            1. Récupérez vos dernières factures d'énergie
            2. Ajoutez-les une par une en cliquant sur "Ajouter une facture"
            3. Suivez l'évolution de votre éco-score et débloquez des badges !
            """)
            return

        # Filtres
        col_filter = st.columns([2, 2, 1])
        with col_filter[0]:
            filtre_energie = st.selectbox(
                "Filtrer par énergie",
                options=["Toutes"] + list(ENERGIES.keys()),
                format_func=lambda x: "Toutes les énergies"
                if x == "Toutes"
                else f"{ENERGIES[x]['emoji']} {ENERGIES[x]['label']}",
            )
        with col_filter[1]:
            ordre = st.selectbox("Trier par", ["Date (récent)", "Date (ancien)", "Montant"])

        # Appliquer filtres
        factures_affichees = factures.copy()
        if filtre_energie != "Toutes":
            factures_affichees = [f for f in factures_affichees if f.get("type") == filtre_energie]

        # Trier
        if ordre == "Date (récent)":
            factures_affichees = sorted(
                factures_affichees, key=lambda f: f.get("date", ""), reverse=True
            )
        elif ordre == "Date (ancien)":
            factures_affichees = sorted(factures_affichees, key=lambda f: f.get("date", ""))
        else:
            factures_affichees = sorted(
                factures_affichees, key=lambda f: f.get("montant", 0), reverse=True
            )

        # Afficher factures
        for i, facture in enumerate(factures_affichees):
            energie_data = ENERGIES.get(facture.get("type"), {})

            col1, col2 = st.columns([6, 1])

            with col1:
                afficher_facture_item(facture, energie_data, i)

            with col2:
                if st.button("🗑️", key=f"del_fact_{i}", help="Supprimer cette facture"):
                    # Trouver l'index dans la liste originale
                    idx = factures.index(facture)
                    factures.pop(idx)
                    st.session_state.factures_charges = factures
                    st.success("Facture supprimée")
                    st.rerun()


def onglet_analyse(factures: list[dict]):
    """Onglet analyse détaillée avec graphiques."""
    st.subheader("📈 Analyse détaillée")

    if not factures:
        st.info("📊 Ajoutez des factures pour voir l'analyse de vos consommations.")
        return

    # Sélection énergie
    energie_sel = st.selectbox(
        "Énergie à analyser",
        options=list(ENERGIES.keys()),
        format_func=lambda x: f"{ENERGIES[x]['emoji']} {ENERGIES[x]['label']}",
    )

    analyse = analyser_consommation(factures, energie_sel)
    config = ENERGIES[energie_sel]

    # KPIs
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(
            "Conso. totale",
            f"{analyse['total_conso']:.0f} {config['unite']}",
            f"{analyse['nb_factures']} factures",
        )
    with col2:
        st.metric("Coût total", f"{analyse['total_cout']:.2f} €")
    with col3:
        icon = (
            "📉"
            if analyse["tendance"] == "baisse"
            else ("📈" if analyse["tendance"] == "hausse" else "➡️")
        )
        st.metric("Tendance", analyse["tendance"].capitalize(), icon)
    with col4:
        ratio_pct = (analyse["ratio"] - 1) * 100
        st.metric("Vs Moyenne", f"{ratio_pct:+.0f}%", "Bien !" if ratio_pct < 0 else "À surveiller")

    st.divider()

    # Graphique évolution (simple avec Streamlit)
    st.markdown("#### 📊 Évolution mensuelle")

    factures_energie = sorted(
        [f for f in factures if f.get("type") == energie_sel], key=lambda f: f.get("date", "")
    )

    if len(factures_energie) >= 2:
        import pandas as pd

        df = pd.DataFrame(
            [
                {
                    "Date": f.get("date", ""),
                    "Consommation": f.get("consommation", 0),
                    "Montant": f.get("montant", 0),
                }
                for f in factures_energie
            ]
        )

        tab1, tab2 = st.tabs(["Consommation", "Coût"])
        with tab1:
            st.line_chart(df.set_index("Date")["Consommation"])
        with tab2:
            st.line_chart(df.set_index("Date")["Montant"])
    else:
        st.info("Ajoutez plus de factures pour voir l'évolution graphique.")

    st.divider()

    # Comparaison moyenne nationale
    st.markdown("#### 🎯 Comparaison moyenne nationale")

    moyenne_ref = config.get("conso_moyenne_mois", 100)
    moyenne_utilisateur = analyse["moyenne_conso"]

    ecart = ((moyenne_utilisateur / moyenne_ref) - 1) * 100 if moyenne_ref > 0 else 0

    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown(f"""
        - **Votre moyenne** : {moyenne_utilisateur:.0f} {config['unite']}/mois
        - **Moyenne nationale** : {moyenne_ref:.0f} {config['unite']}/mois
        - **Écart** : {ecart:+.0f}%
        """)

    with col2:
        if ecart > 20:
            st.error(
                f"⚠️ Consommation {ecart:.0f}% au-dessus de la moyenne. Consultez nos conseils !"
            )
        elif ecart < -10:
            st.success(f"🎉 Bravo ! Vous êtes {-ecart:.0f}% en-dessous de la moyenne.")
        else:
            st.info("📊 Votre consommation est dans la moyenne nationale.")


def onglet_simulation(factures: list[dict]):
    """Onglet simulation d'économies avec IA."""
    st.subheader("💰 Simulation d'économies")

    st.markdown("""
    Découvrez combien vous pourriez économiser en adoptant de bonnes pratiques !
    Sélectionnez les actions que vous envisagez et voyez l'impact.
    """)

    # Sélection énergie
    energie_sel = st.selectbox(
        "Pour quelle énergie ?",
        options=list(ENERGIES.keys()),
        format_func=lambda x: f"{ENERGIES[x]['emoji']} {ENERGIES[x]['label']}",
        key="sim_energie",
    )

    config = ENERGIES[energie_sel]
    conseils = CONSEILS_ECONOMIES.get(energie_sel, [])

    st.markdown(f"### {config['emoji']} Actions {config['label']}")

    # Actions à sélectionner
    actions_selectionnees = []
    total_economie = 0

    for i, conseil in enumerate(conseils):
        col1, col2, col3 = st.columns([4, 2, 1])

        with col1:
            checked = st.checkbox(
                f"{conseil['emoji']} {conseil['titre']}",
                key=f"action_{energie_sel}_{i}",
                help=conseil["desc"],
            )

        with col2:
            st.caption(conseil["desc"])

        with col3:
            st.markdown(f"**{conseil['economie']}**")

        if checked:
            actions_selectionnees.append(conseil)
            # Parser l'économie
            economie_str = conseil["economie"].replace("€/an", "").replace("€", "").strip()
            try:
                total_economie += int(economie_str)
            except ValueError:
                pass

    st.divider()

    # Résultat simulation
    if actions_selectionnees:
        st.markdown("### 📊 Résultat de la simulation")

        col1, col2 = st.columns([1, 1])

        with col1:
            st.markdown(
                f"""
            <div class="simulation-card">
                <div class="header">
                    <span>💰 Économies potentielles</span>
                </div>
                <div class="result">
                    <div class="savings">{total_economie} €</div>
                    <div class="period">par an</div>
                </div>
            </div>
            """,
                unsafe_allow_html=True,
            )

        with col2:
            st.markdown(f"""
            **{len(actions_selectionnees)} action(s) sélectionnée(s):**
            """)
            for action in actions_selectionnees:
                st.markdown(f"- {action['emoji']} {action['titre']}")

        # Bouton simulation IA avancée
        if st.button("🤖 Analyse IA personnalisée", type="secondary"):
            with st.spinner("Analyse en cours..."):
                # Simulation délai IA
                import time

                time.sleep(1.5)

                st.success(f"""
                **💡 Recommandations personnalisées IA:**

                Basé sur votre profil de consommation, voici l'ordre de priorité recommandé:

                1. **{actions_selectionnees[0]['titre'] if actions_selectionnees else 'Aucune action'}** - ROI le plus rapide
                2. Combinez plusieurs actions pour un effet multiplicateur
                3. Économie potentielle réaliste : **{int(total_economie * 0.7)}-{total_economie} €/an**

                *Note: Les économies réelles dépendent de votre usage actuel.*
                """)
    else:
        st.info("👆 Sélectionnez des actions pour voir les économies potentielles")


def onglet_conseils():
    """Onglet conseils d'économies détaillés."""
    st.subheader("💡 Conseils d'économies")

    st.markdown("""
    Retrouvez ici tous les conseils pour réduire votre consommation et améliorer votre éco-score !
    """)

    for energie_id, conseils in CONSEILS_ECONOMIES.items():
        config = ENERGIES[energie_id]

        with st.expander(f"{config['emoji']} {config['label']}", expanded=True):
            for conseil in conseils:
                afficher_conseil_eco(conseil)


# =============================================================================
# POINT D'ENTRÉE
# =============================================================================


def app():
    """Point d'entrée du module Charges gamifié."""
    st.markdown(CHARGES_CSS, unsafe_allow_html=True)

    # Initialiser les données en session
    if "factures_charges" not in st.session_state:
        # TODO: Charger depuis la base de données
        st.session_state.factures_charges = []

    if "badges_vus" not in st.session_state:
        st.session_state.badges_vus = []

    factures = st.session_state.factures_charges

    # Header
    afficher_header()

    # Onglets enrichis
    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        ["📊 Dashboard", "📄 Factures", "📈 Analyse", "💰 Simulation", "💡 Conseils"]
    )

    with tab1:
        onglet_dashboard(factures)

    with tab2:
        onglet_factures(factures)

    with tab3:
        onglet_analyse(factures)

    with tab4:
        onglet_simulation(factures)

    with tab5:
        onglet_conseils()


if __name__ == "__main__":
    app()
