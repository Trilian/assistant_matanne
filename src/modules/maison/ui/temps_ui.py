"""
UI Suivi du Temps - Chronomètre et statistiques.

Composants:
- Chronomètre interactif start/stop
- Dashboard statistiques
- Cartes suggestions IA
- Graphiques temps par activité
"""

from datetime import datetime
from typing import Callable

import streamlit as st

# ═══════════════════════════════════════════════════════════
# STYLES CSS
# ═══════════════════════════════════════════════════════════

TEMPS_CSS = """
<style>
/* Chronomètre principal */
.chrono-container {
    background: linear-gradient(135deg, #1e3a5f 0%, #2d5a87 100%);
    border-radius: 20px;
    padding: 30px;
    text-align: center;
    color: white;
    margin: 20px 0;
    box-shadow: 0 10px 40px rgba(0,0,0,0.2);
}

.chrono-temps {
    font-family: 'SF Mono', 'Monaco', monospace;
    font-size: 4rem;
    font-weight: 700;
    letter-spacing: 4px;
    margin: 20px 0;
    text-shadow: 0 2px 10px rgba(0,0,0,0.3);
}

.chrono-temps.actif {
    color: #4ade80;
    animation: pulse 1s ease-in-out infinite;
}

@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.8; }
}

.chrono-activite {
    font-size: 1.5rem;
    margin-bottom: 10px;
    opacity: 0.9;
}

.chrono-boutons {
    display: flex;
    justify-content: center;
    gap: 15px;
    margin-top: 20px;
}

/* Barre de progression hebdo */
.progress-hebdo {
    background: #e5e7eb;
    border-radius: 10px;
    height: 20px;
    overflow: hidden;
    margin: 10px 0;
}

.progress-bar {
    height: 100%;
    border-radius: 10px;
    transition: width 0.5s ease;
}

.progress-bar.jardin { background: linear-gradient(90deg, #22c55e, #4ade80); }
.progress-bar.menage { background: linear-gradient(90deg, #3b82f6, #60a5fa); }
.progress-bar.bricolage { background: linear-gradient(90deg, #f59e0b, #fbbf24); }

/* Carte statistique */
.stat-card {
    background: white;
    border-radius: 16px;
    padding: 20px;
    text-align: center;
    box-shadow: 0 4px 15px rgba(0,0,0,0.08);
    transition: transform 0.2s ease;
}

.stat-card:hover {
    transform: translateY(-3px);
}

.stat-valeur {
    font-size: 2.5rem;
    font-weight: 700;
    color: #1f2937;
    line-height: 1;
}

.stat-unite {
    font-size: 1rem;
    color: #6b7280;
    margin-left: 4px;
}

.stat-label {
    font-size: 0.9rem;
    color: #6b7280;
    margin-top: 8px;
}

.stat-tendance {
    font-size: 0.85rem;
    margin-top: 5px;
    padding: 3px 8px;
    border-radius: 8px;
    display: inline-block;
}

.stat-tendance.hausse { background: #fef2f2; color: #ef4444; }
.stat-tendance.baisse { background: #f0fdf4; color: #22c55e; }
.stat-tendance.stable { background: #f3f4f6; color: #6b7280; }

/* Carte suggestion */
.suggestion-card {
    background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
    border-radius: 14px;
    padding: 16px;
    margin: 10px 0;
    border-left: 4px solid #f59e0b;
}

.suggestion-titre {
    font-weight: 700;
    font-size: 1.1rem;
    color: #78350f;
    margin-bottom: 8px;
}

.suggestion-description {
    font-size: 0.9rem;
    color: #92400e;
}

.suggestion-economie {
    display: inline-block;
    background: #fef9c3;
    padding: 4px 10px;
    border-radius: 8px;
    font-size: 0.8rem;
    font-weight: 600;
    color: #854d0e;
    margin-top: 8px;
}

/* Carte matériel */
.materiel-card {
    background: white;
    border-radius: 14px;
    padding: 16px;
    margin: 10px 0;
    border: 2px solid #e5e7eb;
    transition: all 0.2s ease;
}

.materiel-card:hover {
    border-color: #3b82f6;
    box-shadow: 0 4px 15px rgba(59,130,246,0.15);
}

.materiel-nom {
    font-weight: 700;
    font-size: 1.1rem;
    color: #1f2937;
}

.materiel-prix {
    color: #22c55e;
    font-weight: 600;
    font-size: 1.2rem;
}

.materiel-roi {
    font-size: 0.85rem;
    color: #6b7280;
}

/* Historique sessions */
.session-item {
    display: flex;
    align-items: center;
    padding: 12px;
    background: white;
    border-radius: 10px;
    margin: 6px 0;
    border-left: 4px solid #3b82f6;
}

.session-icone {
    font-size: 1.5rem;
    margin-right: 12px;
}

.session-info {
    flex: 1;
}

.session-activite {
    font-weight: 600;
    color: #1f2937;
}

.session-date {
    font-size: 0.8rem;
    color: #6b7280;
}

.session-duree {
    font-weight: 700;
    color: #3b82f6;
    font-size: 1.1rem;
}

/* Sélecteur activité */
.activite-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
    gap: 10px;
    margin: 15px 0;
}

.activite-btn {
    background: white;
    border: 2px solid #e5e7eb;
    border-radius: 12px;
    padding: 15px 10px;
    text-align: center;
    cursor: pointer;
    transition: all 0.2s ease;
}

.activite-btn:hover {
    border-color: #3b82f6;
    transform: translateY(-2px);
}

.activite-btn.selected {
    border-color: #3b82f6;
    background: #eff6ff;
}

.activite-btn-icone {
    font-size: 1.8rem;
    display: block;
    margin-bottom: 5px;
}

.activite-btn-label {
    font-size: 0.75rem;
    color: #374151;
}
</style>
"""


# ═══════════════════════════════════════════════════════════
# CONSTANTES
# ═══════════════════════════════════════════════════════════

ICONES_ACTIVITES = {
    "arrosage": "💧",
    "tonte": "🌿",
    "taille": "✂️",
    "desherbage": "🌱",
    "plantation": "🌷",
    "recolte": "🥕",
    "compost": "♻️",
    "traitement": "🧪",
    "menage_general": "🧹",
    "aspirateur": "🧹",
    "lavage_sol": "🪣",
    "poussiere": "🪶",
    "vitres": "🪟",
    "lessive": "👕",
    "repassage": "👔",
    "bricolage": "🔧",
    "peinture": "🎨",
    "plomberie": "🚿",
    "electricite": "💡",
    "nettoyage_exterieur": "🏠",
    "rangement": "📦",
    "administratif": "📋",
    "autre": "⏱️",
}

LABELS_ACTIVITES = {
    "arrosage": "Arrosage",
    "tonte": "Tonte",
    "taille": "Taille",
    "desherbage": "Désherbage",
    "plantation": "Plantation",
    "recolte": "Récolte",
    "compost": "Compost",
    "traitement": "Traitement",
    "menage_general": "Ménage",
    "aspirateur": "Aspirateur",
    "lavage_sol": "Lavage sol",
    "poussiere": "Poussière",
    "vitres": "Vitres",
    "lessive": "Lessive",
    "repassage": "Repassage",
    "bricolage": "Bricolage",
    "peinture": "Peinture",
    "plomberie": "Plomberie",
    "electricite": "Électricité",
    "nettoyage_exterieur": "Ext. maison",
    "rangement": "Rangement",
    "administratif": "Admin",
    "autre": "Autre",
}


# ═══════════════════════════════════════════════════════════
# COMPOSANTS
# ═══════════════════════════════════════════════════════════


def chronometre_widget(
    session_active: dict | None = None,
    on_start: Callable[[str], None] | None = None,
    on_stop: Callable[[int], None] | None = None,
    on_cancel: Callable[[int], None] | None = None,
    key: str = "chrono",
):
    """
    Affiche un chronomètre interactif pour les sessions de travail.

    Args:
        session_active: Session en cours (dict avec id, type_activite, debut)
        on_start: Callback quand on démarre (reçoit type_activite)
        on_stop: Callback quand on arrête (reçoit session_id)
        on_cancel: Callback quand on annule (reçoit session_id)
        key: Clé unique
    """
    st.markdown(TEMPS_CSS, unsafe_allow_html=True)

    # État local
    if f"{key}_activite_selectionnee" not in st.session_state:
        st.session_state[f"{key}_activite_selectionnee"] = None

    # Chronomètre en cours ?
    en_cours = session_active is not None

    if en_cours:
        # Afficher le chronomètre actif
        _afficher_chrono_actif(session_active, on_stop, on_cancel, key)
    else:
        # Afficher le sélecteur d'activité
        _afficher_selecteur_activite(on_start, key)


def _afficher_chrono_actif(
    session: dict,
    on_stop: Callable[[int], None] | None,
    on_cancel: Callable[[int], None] | None,
    key: str,
):
    """Affiche le chronomètre en cours."""
    type_activite = session.get("type_activite", "autre")
    debut = session.get("debut", datetime.now())
    session_id = session.get("id", 0)

    icone = ICONES_ACTIVITES.get(type_activite, "⏱️")
    label = LABELS_ACTIVITES.get(type_activite, type_activite)

    # Calculer temps écoulé
    if isinstance(debut, str):
        debut = datetime.fromisoformat(debut)
    duree = datetime.now() - debut
    heures, reste = divmod(int(duree.total_seconds()), 3600)
    minutes, secondes = divmod(reste, 60)

    temps_str = f"{heures:02d}:{minutes:02d}:{secondes:02d}"

    st.markdown(
        f"""
        <div class="chrono-container">
            <div class="chrono-activite">{icone} {label}</div>
            <div class="chrono-temps actif">{temps_str}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Boutons d'action
    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        if st.button("⏹️ Terminer", key=f"{key}_stop", type="primary", use_container_width=True):
            if on_stop:
                on_stop(session_id)

    with col2:
        # Placeholder pour notes
        pass

    with col3:
        if st.button("❌ Annuler", key=f"{key}_cancel", use_container_width=True):
            if on_cancel:
                on_cancel(session_id)

    # Rafraîchissement automatique toutes les secondes
    st.rerun()


def _afficher_selecteur_activite(
    on_start: Callable[[str], None] | None,
    key: str,
):
    """Affiche le sélecteur d'activité pour démarrer."""
    st.markdown("### ⏱️ Démarrer une session")

    # Catégories d'activités
    categories = {
        "🌳 Jardin": ["arrosage", "tonte", "taille", "desherbage", "plantation", "recolte"],
        "🧹 Ménage": [
            "menage_general",
            "aspirateur",
            "lavage_sol",
            "poussiere",
            "vitres",
            "lessive",
        ],
        "🔧 Bricolage": [
            "bricolage",
            "peinture",
            "plomberie",
            "electricite",
            "nettoyage_exterieur",
        ],
        "📦 Autre": ["rangement", "administratif", "autre"],
    }

    tabs = st.tabs(list(categories.keys()))

    for tab, (cat_nom, activites) in zip(tabs, categories.items(), strict=False):
        with tab:
            cols = st.columns(3)
            for idx, activite in enumerate(activites):
                with cols[idx % 3]:
                    icone = ICONES_ACTIVITES.get(activite, "⏱️")
                    label = LABELS_ACTIVITES.get(activite, activite)

                    if st.button(
                        f"{icone}\n{label}",
                        key=f"{key}_{activite}",
                        use_container_width=True,
                    ):
                        if on_start:
                            on_start(activite)


def dashboard_temps(
    resume_semaine: dict,
    stats_activites: list[dict],
    key: str = "dashboard",
):
    """
    Affiche le tableau de bord des statistiques de temps.

    Args:
        resume_semaine: Dict avec temps_total, jardin, menage, bricolage
        stats_activites: Liste des stats par activité
        key: Clé unique
    """
    st.markdown(TEMPS_CSS, unsafe_allow_html=True)

    # KPIs principaux
    st.markdown("### 📊 Cette semaine")

    col1, col2, col3, col4 = st.columns(4)

    temps_total = resume_semaine.get("temps_total_minutes", 0)
    heures = temps_total // 60
    minutes = temps_total % 60

    with col1:
        st.markdown(
            f"""
            <div class="stat-card">
                <div class="stat-valeur">{heures}<span class="stat-unite">h</span> {minutes}<span class="stat-unite">m</span></div>
                <div class="stat-label">⏱️ Temps total</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        jardin = resume_semaine.get("temps_jardin_minutes", 0)
        st.markdown(
            f"""
            <div class="stat-card">
                <div class="stat-valeur">{jardin}</div>
                <div class="stat-label">🌳 Jardin (min)</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col3:
        menage = resume_semaine.get("temps_menage_minutes", 0)
        st.markdown(
            f"""
            <div class="stat-card">
                <div class="stat-valeur">{menage}</div>
                <div class="stat-label">🧹 Ménage (min)</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col4:
        bricolage = resume_semaine.get("temps_bricolage_minutes", 0)
        st.markdown(
            f"""
            <div class="stat-card">
                <div class="stat-valeur">{bricolage}</div>
                <div class="stat-label">🔧 Bricolage (min)</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Barre de progression par catégorie
    if temps_total > 0:
        st.markdown("#### Répartition")
        jardin_pct = (jardin / temps_total) * 100 if temps_total > 0 else 0
        menage_pct = (menage / temps_total) * 100 if temps_total > 0 else 0
        bricolage_pct = (bricolage / temps_total) * 100 if temps_total > 0 else 0

        st.markdown(
            f"""
            <div style="display: flex; height: 30px; border-radius: 8px; overflow: hidden;">
                <div class="progress-bar jardin" style="width: {jardin_pct}%;" title="Jardin {jardin_pct:.0f}%"></div>
                <div class="progress-bar menage" style="width: {menage_pct}%;" title="Ménage {menage_pct:.0f}%"></div>
                <div class="progress-bar bricolage" style="width: {bricolage_pct}%;" title="Bricolage {bricolage_pct:.0f}%"></div>
            </div>
            <div style="display: flex; justify-content: space-between; margin-top: 5px; font-size: 0.8rem; color: #6b7280;">
                <span>🌳 {jardin_pct:.0f}%</span>
                <span>🧹 {menage_pct:.0f}%</span>
                <span>🔧 {bricolage_pct:.0f}%</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Comparaison semaine précédente
    comparaison = resume_semaine.get("comparaison_semaine_precedente", 0)
    if comparaison != 0:
        tendance_class = "hausse" if comparaison > 0 else "baisse"
        tendance_icone = "📈" if comparaison > 0 else "📉"
        st.markdown(
            f"""
            <div class="stat-tendance {tendance_class}">
                {tendance_icone} {abs(comparaison):.0f}% vs semaine dernière
            </div>
            """,
            unsafe_allow_html=True,
        )


def carte_suggestion(
    suggestion: dict,
    on_action: Callable[[], None] | None = None,
    key: str = "sugg",
):
    """
    Affiche une carte de suggestion d'optimisation.

    Args:
        suggestion: Dict avec titre, description, temps_economise, etc.
        on_action: Callback si action disponible
        key: Clé unique
    """
    titre = suggestion.get("titre", "Suggestion")
    description = suggestion.get("description", "")
    temps_eco = suggestion.get("temps_economise_estime_min", 0)
    type_sugg = suggestion.get("type_suggestion", "")

    icones_type = {
        "regroupement": "🔗",
        "planification": "📅",
        "delegation": "👥",
        "materiel": "🛠️",
    }
    icone = icones_type.get(type_sugg, "💡")

    st.markdown(
        f"""
        <div class="suggestion-card">
            <div class="suggestion-titre">{icone} {titre}</div>
            <div class="suggestion-description">{description}</div>
            {f'<div class="suggestion-economie">⏱️ ~{temps_eco} min/semaine économisées</div>' if temps_eco else ""}
        </div>
        """,
        unsafe_allow_html=True,
    )


def carte_materiel(
    materiel: dict,
    on_voir_produit: Callable[[], None] | None = None,
    key: str = "mat",
):
    """
    Affiche une carte de recommandation matériel.

    Args:
        materiel: Dict avec nom, description, prix, roi, etc.
        on_voir_produit: Callback pour voir le produit
        key: Clé unique
    """
    nom = materiel.get("nom_materiel", "Équipement")
    description = materiel.get("description", "")
    prix_min = materiel.get("prix_estime_min", 0)
    prix_max = materiel.get("prix_estime_max", 0)
    temps_eco = materiel.get("temps_economise_par_session_min", 0)
    roi = materiel.get("retour_investissement_semaines", 0)
    categorie = materiel.get("categorie", "autre")

    icones_cat = {"jardin": "🌳", "menage": "🧹", "bricolage": "🔧"}
    icone = icones_cat.get(categorie, "🛠️")

    with st.container(border=True):
        col1, col2 = st.columns([3, 1])

        with col1:
            st.markdown(f"**{icone} {nom}**")
            st.caption(description)

        with col2:
            if prix_min and prix_max:
                st.markdown(f"**{prix_min}-{prix_max}€**")
            elif prix_min:
                st.markdown(f"**~{prix_min}€**")

        # Badges info
        badges = []
        if temps_eco:
            badges.append(f"⏱️ -{temps_eco}min/session")
        if roi:
            badges.append(f"💰 Rentable en {roi} sem.")

        if badges:
            st.caption(" • ".join(badges))

        if on_voir_produit:
            if st.button("🔗 Voir produit", key=f"{key}_voir", use_container_width=True):
                on_voir_produit()


def historique_sessions(
    sessions: list[dict],
    max_items: int = 10,
    key: str = "hist",
):
    """
    Affiche l'historique des sessions récentes.

    Args:
        sessions: Liste des sessions (dict avec type_activite, debut, duree)
        max_items: Nombre max d'items
        key: Clé unique
    """
    st.markdown("### 📜 Sessions récentes")

    if not sessions:
        st.info("Aucune session enregistrée")
        return

    for idx, session in enumerate(sessions[:max_items]):
        type_act = session.get("type_activite", "autre")
        debut = session.get("debut", "")
        duree = session.get("duree_minutes", 0)

        icone = ICONES_ACTIVITES.get(type_act, "⏱️")
        label = LABELS_ACTIVITES.get(type_act, type_act)

        # Formater la date
        if isinstance(debut, datetime):
            date_str = debut.strftime("%d/%m %H:%M")
        elif isinstance(debut, str):
            try:
                dt = datetime.fromisoformat(debut)
                date_str = dt.strftime("%d/%m %H:%M")
            except ValueError:
                date_str = debut
        else:
            date_str = str(debut)

        st.markdown(
            f"""
            <div class="session-item">
                <div class="session-icone">{icone}</div>
                <div class="session-info">
                    <div class="session-activite">{label}</div>
                    <div class="session-date">{date_str}</div>
                </div>
                <div class="session-duree">{duree} min</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def score_efficacite(
    score: int,
    key: str = "score",
):
    """
    Affiche le score d'efficacité avec jauge.

    Args:
        score: Score de 0 à 100
        key: Clé unique
    """
    # Couleur selon le score
    if score >= 70:
        couleur = "#22c55e"
        label = "Excellent"
    elif score >= 50:
        couleur = "#eab308"
        label = "Bon"
    else:
        couleur = "#ef4444"
        label = "À améliorer"

    st.markdown(
        f"""
        <div style="text-align: center; padding: 20px;">
            <div style="font-size: 3rem; font-weight: 700; color: {couleur};">{score}</div>
            <div style="font-size: 1rem; color: #6b7280;">Score d'efficacité</div>
            <div style="margin-top: 10px;">
                <div style="background: #e5e7eb; height: 8px; border-radius: 4px; overflow: hidden;">
                    <div style="width: {score}%; height: 100%; background: {couleur}; border-radius: 4px;"></div>
                </div>
            </div>
            <div style="margin-top: 8px; font-size: 0.9rem; color: {couleur}; font-weight: 600;">{label}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
