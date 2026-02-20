"""
Charges - Composants UI gamifiés.
"""

import streamlit as st

from src.core.session_keys import SK

from .constantes import BADGES_DEFINITIONS, ENERGIES, NIVEAUX_ECO


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

    circumference = 2 * 3.14159 * 70
    stroke_dasharray = (score / 100) * circumference
    niveau = next((n for n in NIVEAUX_ECO if score >= n["min"]), NIVEAUX_ECO[-1])

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
                <circle cx="90" cy="90" r="70" fill="none" stroke="{stroke_color}" stroke-width="12"
                    stroke-linecap="round" stroke-dasharray="{stroke_dasharray} {circumference}"
                    transform="rotate(-90 90 90)" style="filter: drop-shadow(0 0 10px {stroke_color});"/>
            </svg>
            <div class="eco-score-value" style="color: {couleur};">{score}</div>
        </div>
        <div class="eco-score-label">ÉCO-SCORE</div>
        {var_html}
        <div class="eco-level {niveau["class"]}">{niveau["emoji"]} {niveau["nom"]}</div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    if streak >= 3:
        st.markdown(
            f"""
        <div class="streak-counter" style="margin-top: 1rem;">
            <span class="fire">🔥</span>
            <div><span class="count">{streak}</span>
            <span class="label">jours d'affilée sous la moyenne</span></div>
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
        is_new = badge_id not in st.session_state.get(SK.BADGES_VUS, []) and est_obtenu
        locked_class = "" if est_obtenu else "locked"
        new_class = "new" if is_new else ""

        with cols[i % 4]:
            st.markdown(
                f"""
            <div class="badge-eco {locked_class} {new_class}">
                <span class="icon">{badge_def["emoji"]}</span>
                <span class="name">{badge_def["nom"]}</span>
                {'<span class="date">Obtenu ✓</span>' if est_obtenu else '<span class="date">🔒 Verrouillé</span>'}
            </div>
            """,
                unsafe_allow_html=True,
            )

    if badges_obtenus:
        st.session_state.badges_vus = badges_obtenus


def afficher_energie_card(
    energie_id: str, data: dict, conso: float, cout, tendance: str, ratio: float
):
    """Affiche une carte énergie avec barre de progression."""
    trend_class = "down" if tendance == "baisse" else ("up" if tendance == "hausse" else "stable")
    trend_icon = "📉" if tendance == "baisse" else ("📈" if tendance == "hausse" else "➡️")
    progress_pct = min(100, ratio * 100)
    progress_class = "good" if ratio < 0.9 else ("warning" if ratio < 1.1 else "bad")

    st.markdown(
        f"""
    <div class="energie-card {energie_id} animate-in">
        <div class="header">
            <div><span class="icon">{data["emoji"]}</span><span class="title">{data["label"]}</span></div>
            <span class="trend {trend_class}">{trend_icon} {tendance.capitalize()}</span>
        </div>
        <div class="value">{conso:.0f} <span class="unit">{data["unite"]}</span></div>
        <div style="font-size: 1rem; color: #718096;">{cout:.2f} € ce mois</div>
        <div class="progress-bar-compare"><div class="fill {progress_class}" style="width: {progress_pct}%"></div></div>
        <div style="font-size: 0.8rem; color: #a0aec0; margin-top: 0.5rem;">{ratio * 100:.0f}% de la moyenne nationale</div>
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
                <div class="title">{anomalie.get("titre", "Anomalie détectée")}</div>
                <div class="description">{anomalie.get("description", "")}</div>
                <div class="action">💡 {anomalie.get("conseil", "Vérifiez vos équipements")}</div>
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )


def afficher_simulation_economies(energie: str, economie_estimee, periode: str = "par an"):
    """Affiche le résultat de simulation d'économies."""
    st.markdown(
        f"""
    <div class="simulation-card animate-in">
        <div class="header"><span>{ENERGIES[energie]["emoji"]} Simulation {ENERGIES[energie]["label"]}</span></div>
        <div class="result"><div class="savings">💰 {economie_estimee:.0f} €</div><div class="period">{periode}</div></div>
    </div>
    """,
        unsafe_allow_html=True,
    )


def afficher_conseil_eco(conseil: dict):
    """Affiche un conseil d'économie."""
    st.markdown(
        f"""
    <div class="conseil-eco">
        <span class="icon">{conseil["emoji"]}</span>
        <div class="text"><div class="title">{conseil["titre"]}</div><div class="desc">{conseil["desc"]}</div></div>
        <span class="economie">{conseil["economie"]}</span>
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
        <div class="icon">{energie_data.get("emoji", "📄")}</div>
        <div class="details">
            <div class="type">{energie_data.get("label", facture.get("type"))}</div>
            <div class="date">{facture.get("date")} • {facture.get("fournisseur", "Non précisé")}</div>
            <div class="conso">{conso_text}</div>
        </div>
        <div class="montant">{facture.get("montant", 0):.2f} €</div>
    </div>
    """,
        unsafe_allow_html=True,
    )
