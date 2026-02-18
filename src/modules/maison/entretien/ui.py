"""
Entretien - Composants UI réutilisables.

Affichage de tâches, pièces, score gamifié, badges, etc.
"""

import logging

import streamlit as st

logger = logging.getLogger(__name__)


# =============================================================================
# COMPOSANTS UI GAMIFIÉS
# =============================================================================


def afficher_header(score: dict):
    """Affiche le header avec score."""
    st.markdown(
        f"""
    <div class="entretien-header">
        <h1>🏠 Entretien Maison</h1>
        <div class="score-badge">
            <span style="font-size: 1.25rem">✨</span>
            <span>Score: <strong>{score["score"]}/100</strong> • {score["niveau"]}</span>
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )


def afficher_score_gamifie(score: dict, streak: int = 0):
    """Affiche le score propreté avec anneau SVG animé et gamification."""
    score_val = score.get("score", 50)
    niveau = score.get("niveau", "Moyen")

    # Couleur selon score
    if score_val >= 90:
        stroke_color = "#27ae60"
        niveau_class = "excellent"
    elif score_val >= 70:
        stroke_color = "#3498db"
        niveau_class = "bon"
    elif score_val >= 50:
        stroke_color = "#f39c12"
        niveau_class = "moyen"
    else:
        stroke_color = "#e74c3c"
        niveau_class = "mauvais"

    # Calcul de l'arc SVG
    circumference = 2 * 3.14159 * 70
    stroke_dasharray = (score_val / 100) * circumference

    st.markdown(
        f"""
    <div class="score-container animate-in">
        <div class="score-ring">
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
            <div class="score-value" style="color: {stroke_color};">{score_val}</div>
        </div>
        <div class="score-label">SCORE PROPRETÉ</div>
        <div class="score-niveau {niveau_class}">✨ {niveau}</div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Streak si > 3
    if streak >= 3:
        st.markdown(
            f"""
        <div class="streak-proprete">
            <span class="star">⭐</span>
            <div>
                <span style="font-size: 1.5rem; font-weight: 800;">{streak}</span>
                <span style="font-size: 0.85rem; opacity: 0.9;">jours maison nickel</span>
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )


def afficher_badges_entretien(badges_obtenus: list[str], stats: dict):
    """Affiche la collection de badges entretien."""
    from .logic import BADGES_ENTRETIEN

    st.markdown("### 🏅 Collection de badges")

    cols = st.columns(4)

    for i, badge_def in enumerate(BADGES_ENTRETIEN):
        badge_id = badge_def["id"]
        est_obtenu = badge_id in badges_obtenus or badge_def["condition"](stats)

        locked_class = "" if est_obtenu else "locked"

        with cols[i % 4]:
            st.markdown(
                f"""
            <div class="badge-entretien {locked_class}">
                <span class="icon">{badge_def["emoji"]}</span>
                <span class="name">{badge_def["nom"]}</span>
                {'<span class="date">Obtenu ✓</span>' if est_obtenu else '<span class="date">🔒</span>'}
            </div>
            """,
                unsafe_allow_html=True,
            )


def afficher_alertes_predictives(alertes: list[dict]):
    """Affiche les alertes prédictives pour les tâches à venir."""
    if not alertes:
        return

    st.markdown("### 🔮 Prochainement")

    for alerte in alertes[:5]:
        st.markdown(
            f"""
        <div class="alerte-predictive animate-in">
            <span class="icon">📅</span>
            <div class="content">
                <div class="title">{alerte.get("tache_nom", "Tâche")}</div>
                <div class="description">{alerte.get("objet_nom", "")} • {alerte.get("piece", "")}</div>
                <div class="date-prevue">📆 Prévu le {alerte.get("date_prevue", "bientôt")}</div>
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )


def afficher_planning_previsionnel(taches_futures: list[dict]):
    """Affiche le planning prévisionnel des tâches."""
    if not taches_futures:
        st.info("✅ Aucune tâche prévue dans les prochaines semaines !")
        return

    # Grouper par période
    cette_semaine = [t for t in taches_futures if t.get("jours_restants", 999) <= 7]
    ce_mois = [t for t in taches_futures if 7 < t.get("jours_restants", 999) <= 30]
    plus_tard = [t for t in taches_futures if t.get("jours_restants", 999) > 30]

    if cette_semaine:
        st.markdown("#### 🔴 Cette semaine")
        for t in cette_semaine:
            _afficher_planning_item(t, "cette-semaine")

    if ce_mois:
        st.markdown("#### 🟠 Ce mois")
        for t in ce_mois:
            _afficher_planning_item(t, "ce-mois")

    if plus_tard:
        st.markdown("#### 🟢 Plus tard")
        for t in plus_tard[:5]:
            _afficher_planning_item(t, "plus-tard")


def _afficher_planning_item(tache: dict, classe: str):
    """Affiche un item du planning."""
    st.markdown(
        f"""
    <div class="planning-item {classe}">
        <div class="date-badge">J-{tache.get("jours_restants", "?")}</div>
        <div class="details">
            <div class="tache-nom">{tache.get("tache_nom", "Tâche")}</div>
            <div class="objet-nom">{tache.get("objet_nom", "")} • {tache.get("piece", "")}</div>
        </div>
        <span>⏱️ {tache.get("duree_min", 15)} min</span>
    </div>
    """,
        unsafe_allow_html=True,
    )


def afficher_tache_entretien(tache: dict, key: str) -> bool:
    """
    Affiche une tâche d'entretien avec actions.

    Returns:
        True si la tâche a été marquée comme faite.
    """
    cat_class = tache.get("categorie_id", "divers")
    retard = tache.get("retard_jours", 0)

    col1, col2 = st.columns([6, 1])

    with col1:
        retard_html = f'<span class="retard">⚠️ {retard}j de retard</span>' if retard > 0 else ""
        pro_html = '<span class="pro-badge">Pro</span>' if tache.get("est_pro") else ""

        st.markdown(
            f"""
        <div class="tache-entretien">
            <div class="icon-circle {cat_class}">{tache["categorie_icon"]}</div>
            <div class="content">
                <div class="title">{tache["tache_nom"]} {pro_html}</div>
                <div style="font-size: 0.9rem; color: #4a5568; margin-bottom: 0.5rem;">
                    {tache["objet_nom"]} • {tache.get("piece", "Non assigné")}
                </div>
                <div class="meta">
                    <span class="meta-item">⏱️ {tache["duree_min"]} min</span>
                    <span class="meta-item">🔄 Tous les {tache["frequence_jours"]}j</span>
                    {retard_html}
                </div>
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    with col2:
        if st.button("✅", key=f"done_ent_{key}", help="Marquer comme fait"):
            return True

    return False


def afficher_piece_card(piece_id: str, piece_data: dict, nb_taches: int):
    """Affiche une carte de pièce."""
    badge_html = f'<div class="badge-count">{nb_taches}</div>' if nb_taches > 0 else ""

    st.markdown(
        f"""
    <div class="piece-card">
        {badge_html}
        <div class="emoji">{piece_data.get("icon", "🏠")}</div>
        <div class="nom">{piece_data.get("nom", piece_id)}</div>
    </div>
    """,
        unsafe_allow_html=True,
    )


def afficher_score_widget(score: dict):
    """Affiche le widget de score propreté."""
    st.markdown(
        f"""
    <div class="score-proprete">
        <div class="value">{score["score"]}</div>
        <div class="label">{score["niveau"]}</div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Métriques détaillées
    col1, col2, col3 = st.columns(3)
    col1.metric("Tâches à faire", score.get("taches_total", 0))
    col2.metric(
        "Urgentes", score.get("urgentes", 0), delta=None if score.get("urgentes", 0) == 0 else "⚠️"
    )
    col3.metric("Prioritaires", score.get("hautes", 0))


def afficher_objet_inventaire(objet: dict, catalogue: dict, index: int, mes_objets: list[dict]):
    """Affiche un objet dans l'inventaire avec option de suppression."""
    objet_data = None
    for cat_data in catalogue.get("categories", {}).values():
        if objet["objet_id"] in cat_data.get("objets", {}):
            objet_data = cat_data["objets"][objet["objet_id"]]
            break

    nom = objet.get("nom_perso") or (objet_data.get("nom") if objet_data else objet["objet_id"])
    nb_taches = len(objet_data.get("taches", [])) if objet_data else 0

    col1, col2 = st.columns([5, 1])
    with col1:
        st.markdown(
            f"""
        <div class="objet-inventaire">
            <div class="icon">{catalogue.get("categories", {}).get(objet.get("categorie_id"), {}).get("icon", "📦")}</div>
            <div class="info">
                <div class="nom">{nom}</div>
                <div class="piece">{objet.get("marque", "") or "Marque non renseignée"}</div>
            </div>
            <div class="stats">
                <div class="taches-count">{nb_taches} tâches auto</div>
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    with col2:
        return st.button("🗑️", key=f"del_obj_{index}", help="Supprimer")


def afficher_stats_rapides(taches: list[dict]):
    """Affiche les stats rapides des tâches."""
    urgentes = len([t for t in taches if t.get("priorite") == "urgente"])
    hautes = len([t for t in taches if t.get("priorite") == "haute"])
    temps_total = sum(t.get("duree_min", 0) for t in taches)

    st.markdown(
        f"""
    <div class="stats-grid">
        <div class="stat-box urgent">
            <div class="value">{urgentes}</div>
            <div class="label">Urgentes</div>
        </div>
        <div class="stat-box warning">
            <div class="value">{hautes}</div>
            <div class="label">Prioritaires</div>
        </div>
        <div class="stat-box">
            <div class="value">{len(taches)}</div>
            <div class="label">À faire</div>
        </div>
        <div class="stat-box">
            <div class="value">{temps_total} min</div>
            <div class="label">Temps total</div>
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )


def afficher_timeline_item(historique_entry: dict, catalogue: dict, label_date: str = None):
    """Affiche un élément de timeline historique."""
    # Trouver l'icône
    objet_id = historique_entry.get("objet_id", "")
    icon = "✅"
    for cat_data in catalogue.get("categories", {}).values():
        if objet_id in cat_data.get("objets", {}):
            icon = cat_data.get("icon", "✅")
            break

    st.markdown(
        f"""
    <div class="timeline-item done">
        <span>{icon}</span>
        <span><strong>{historique_entry.get("tache_nom", "Tâche")}</strong></span>
        <span style="color: #718096">• {historique_entry.get("objet_id", "").replace("_", " ")}</span>
    </div>
    """,
        unsafe_allow_html=True,
    )
