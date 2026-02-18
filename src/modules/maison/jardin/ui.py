"""
Jardin - Composants UI réutilisables.

Fonctions d'affichage pour header, tâches, calendrier, badges gamifiés, etc.
"""

import logging

import streamlit as st

logger = logging.getLogger(__name__)


# =============================================================================
# COMPOSANTS UI GAMIFIÉS
# =============================================================================


def afficher_score_jardin_gamifie(autonomie: dict, streak: int = 0):
    """Affiche le score d'autonomie avec anneau SVG animé."""
    score = autonomie.get("pourcentage_prevu", 0)

    # Couleur selon niveau
    if score >= 50:
        stroke_color = "#27ae60"
    elif score >= 25:
        stroke_color = "#3498db"
    elif score >= 10:
        stroke_color = "#f39c12"
    else:
        stroke_color = "#e74c3c"

    circumference = 2 * 3.14159 * 70
    stroke_dasharray = (score / 100) * circumference

    st.markdown(
        f"""
    <div class="score-jardin-container animate-grow">
        <div class="score-jardin-ring">
            <svg width="180" height="180" viewBox="0 0 180 180">
                <circle cx="90" cy="90" r="70" fill="none" stroke="rgba(255,255,255,0.2)" stroke-width="12"/>
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
            <div class="score-jardin-value">{score}%</div>
        </div>
        <div class="score-jardin-label">Autonomie Alimentaire</div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Streak
    if streak >= 3:
        st.markdown(
            f"""
        <div style="text-align: center; margin-top: 1rem;
                    background: linear-gradient(135deg, #f39c12, #e67e22);
                    border-radius: 20px; padding: 0.5rem 1rem; display: inline-block;">
            🔥 <strong>{streak}</strong> jours consécutifs au jardin
        </div>
        """,
            unsafe_allow_html=True,
        )


def afficher_badges_jardin(badges_obtenus: list[str], stats: dict):
    """Affiche la collection de badges jardin."""
    from .logic import BADGES_JARDIN

    st.markdown("### 🏅 Collection de badges")

    cols = st.columns(4)

    for i, badge_def in enumerate(BADGES_JARDIN):
        badge_id = badge_def["id"]
        est_obtenu = badge_id in badges_obtenus

        classe = "unlocked" if est_obtenu else "locked"

        with cols[i % 4]:
            st.markdown(
                f"""
            <div class="badge-jardin {classe}">
                <span class="icon">{badge_def["emoji"]}</span>
                <span class="name">{badge_def["nom"]}</span>
                <span class="status">{"✓ Obtenu" if est_obtenu else "🔒 Verrouillé"}</span>
            </div>
            """,
                unsafe_allow_html=True,
            )


def afficher_previsions_recoltes_ui(previsions: list[dict]):
    """Affiche les prévisions de récoltes."""
    if not previsions:
        st.info("🌱 Plantez des légumes pour voir vos prévisions de récoltes !")
        return

    st.markdown("### 🥕 Prévisions de récoltes")

    for prev in previsions:
        st.markdown(
            f"""
        <div class="prevision-recolte">
            <span class="emoji">{prev.get("emoji", "🌱")}</span>
            <div class="details">
                <div class="nom">{prev.get("nom", "Légume")}</div>
                <div class="quantite">~{prev.get("quantite_prevue_kg", 0)} kg</div>
            </div>
            <span class="periode">{prev.get("periode", "Bientôt")}</span>
        </div>
        """,
            unsafe_allow_html=True,
        )


def afficher_planning_jardin_ui(planning: list[dict]):
    """Affiche le planning prévisionnel des activités."""
    if not planning:
        st.success("✅ Aucune activité prévue prochainement")
        return

    st.markdown("### 📅 Planning prévisionnel")

    for item in planning[:10]:
        type_class = item.get("type", "autre")
        st.markdown(
            f"""
        <div class="planning-jardin-item {type_class}">
            <span style="font-size: 1.5rem;">{item.get("emoji", "🌱")}</span>
            <div style="flex: 1;">
                <strong>{item.get("titre", "Activité")}</strong>
            </div>
            <span class="mois-badge">{item.get("mois_label", "")}</span>
        </div>
        """,
            unsafe_allow_html=True,
        )


def afficher_autonomie_gamifiee(autonomie: dict):
    """Affiche la jauge d'autonomie gamifiée."""
    pourcent = autonomie.get("pourcentage_prevu", 0)

    st.markdown(
        f"""
    <div class="autonomie-gamifie">
        <div class="percent">{pourcent}%</div>
        <div class="label">vers l'autosuffisance</div>
        <div class="autonomie-progress">
            <div class="autonomie-progress-fill" style="width: {pourcent}%;"></div>
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Détails
    col1, col2 = st.columns(2)
    col1.metric("Production prévue", f"{autonomie.get('production_prevue_kg', 0)} kg")
    col2.metric("Besoins famille", f"{autonomie.get('besoins_kg', 265)} kg/an")


# =============================================================================
# COMPOSANTS UI STANDARDS
# =============================================================================


def afficher_header(meteo: dict):
    """Affiche le header du module jardin avec météo."""
    st.markdown(
        f"""
    <div class="jardin-header">
        <h2>🌱 Mon Potager Intelligent</h2>
        <p>
            <span style="font-size: 1.8rem">☀️</span>
            <strong>{meteo.get("temperature", 20)}°C</strong>
            {"💧 Pluie prévue" if meteo.get("pluie_prevue") else ""}
            {"🥶 Risque gel" if meteo.get("gel_risque") else ""}
        </p>
        <small>{meteo.get("conseil", "")}</small>
    </div>
    """,
        unsafe_allow_html=True,
    )


def afficher_tache(tache: dict, key: str) -> bool:
    """
    Affiche une tâche du jardin avec bouton d'accomplissement.

    Returns:
        True si la tâche a été marquée comme accomplie.
    """
    priorite_class = tache.get("priorite", "normale")

    st.markdown(
        f"""
    <div class="tache-card {priorite_class}">
        <div class="tache-emoji">{tache.get("emoji", "📋")}</div>
        <div class="tache-content">
            <div class="tache-titre">{tache.get("titre", "Tâche")}</div>
            <div class="tache-description">{tache.get("description", "")}</div>
            <div class="tache-meta">
                <span>⏱️ {tache.get("duree_min", 15)} min</span>
                <span class="priorite-badge {priorite_class}">{priorite_class.capitalize()}</span>
            </div>
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    return st.checkbox("✅ Fait", key=key, label_visibility="collapsed")


def afficher_calendrier_plante(plante_data: dict):
    """Affiche le calendrier visuel d'une plante (semis, plantation, récolte)."""
    mois_noms = ["J", "F", "M", "A", "M", "J", "J", "A", "S", "O", "N", "D"]

    semis_int = plante_data.get("semis_interieur", [])
    semis_dir = plante_data.get("semis_direct", [])
    plantation = plante_data.get("plantation_exterieur", [])
    recolte = plante_data.get("recolte", [])

    html = '<div class="calendrier-plante">'
    for i, nom in enumerate(mois_noms, 1):
        classes = []
        if i in semis_int:
            classes.append("semis-int")
        elif i in semis_dir:
            classes.append("semis-dir")
        if i in plantation:
            classes.append("plantation")
        if i in recolte:
            classes.append("recolte")

        class_str = " ".join(classes) if classes else ""
        html += f'<span class="mois {class_str}">{nom}</span>'
    html += "</div>"

    st.markdown(html, unsafe_allow_html=True)

    # Légende
    st.caption("🟡 Semis int. | 🟢 Semis direct | 🔵 Plantation | 🔴 Récolte")


def afficher_plante_card(plante_data: dict, mes_infos: dict | None = None):
    """Affiche une carte plante compacte."""
    nom = plante_data.get("nom", "Plante")
    emoji = plante_data.get("emoji", "🌱")
    categorie = plante_data.get("categorie", "")

    surface = mes_infos.get("surface_m2", 0) if mes_infos else 0

    st.markdown(
        f"""
    <div class="plante-card">
        <div class="plante-emoji">{emoji}</div>
        <div class="plante-info">
            <strong>{nom}</strong>
            <small>{categorie}</small>
            {f'<span class="surface">{surface}m²</span>' if surface else ""}
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )


def afficher_autonomie_card(autonomie: dict):
    """Affiche la carte principale d'autonomie alimentaire."""
    st.markdown(
        f"""
    <div class="autonomie-gauge">
        <div class="value">{autonomie["pourcentage_prevu"]}%</div>
        <div class="label">Autonomie alimentaire prévue</div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    st.metric(
        "Production prévue",
        f"{autonomie['production_prevue_kg']} kg",
        f"sur {autonomie['besoins_kg']} kg besoin annuel",
    )


def afficher_compagnons(plante_data: dict):
    """Affiche les badges de compagnonnage d'une plante."""
    compagnons_pos = plante_data.get("compagnons_positifs", [])
    compagnons_neg = plante_data.get("compagnons_negatifs", [])

    if not compagnons_pos and not compagnons_neg:
        return

    st.markdown("**Compagnonnage:**")
    html_comp = '<div class="compagnons-list">'
    for c in compagnons_pos[:5]:
        html_comp += f'<span class="compagnon-badge positif">✓ {c}</span>'
    for c in compagnons_neg[:3]:
        html_comp += f'<span class="compagnon-badge negatif">✗ {c}</span>'
    html_comp += "</div>"
    st.markdown(html_comp, unsafe_allow_html=True)


def afficher_zone_culture(nom: str, description: str, active: bool = False, emoji: str = "📦"):
    """Affiche une zone de culture du plan jardin."""
    classe = "active" if active else ""
    couleur_texte = "white" if active else "#8d6e63"
    couleur_small = "#aaa" if active else "#6d4c41"

    st.markdown(
        f"""
    <div class="zone-culture {classe}">
        <span style="color: {couleur_texte};">{emoji} {nom}</span>
        <br><small style="color: {couleur_small};">{description}</small>
    </div>
    """,
        unsafe_allow_html=True,
    )
