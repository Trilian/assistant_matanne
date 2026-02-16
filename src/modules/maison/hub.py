"""
🏠 Hub Maison - Dashboard Intelligent

Hub central avec :
- Briefing IA quotidien
- Tâches prioritaires (respect charge mentale)
- Stats visuelles
- Navigation modules

Architecture:
┌──────────────────────────────────────────────────────────────┐
│ 📋 AUJOURD'HUI                                               │
│ "3 tâches • 45 min • Charge: ████░░░░░░ 40%"                │
├──────────────────────────────────────────────────────────────┤
│ 🚨 ALERTES          │ 📊 STATS DU MOIS                      │
└──────────────────────────────────────────────────────────────┘
│ 🌳 Jardin  │ 🏡 Entretien  │ 💡 Charges  │ 💰 Dépenses     │
└──────────────────────────────────────────────────────────────┘
"""

from datetime import date, datetime

import streamlit as st

from src.core.database import obtenir_contexte_db
from src.core.models import ObjetMaison, PieceMaison
from src.core.models.temps_entretien import SessionTravail, ZoneJardin
from src.core.state import GestionnaireEtat

# ═══════════════════════════════════════════════════════════
# STYLES CSS
# ═══════════════════════════════════════════════════════════

CSS = """
<style>
/* Header principal */
.hub-main-header {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    color: white;
    padding: 1.5rem 2rem;
    border-radius: 16px;
    margin-bottom: 1.5rem;
    box-shadow: 0 4px 20px rgba(0,0,0,0.15);
}
.hub-main-header h1 {
    margin: 0 0 0.5rem 0;
    font-size: 1.8rem;
    font-weight: 600;
}
.hub-date {
    opacity: 0.8;
    font-size: 0.95rem;
}

/* Section tâches */
.taches-section {
    background: white;
    border-radius: 12px;
    padding: 1.25rem;
    margin-bottom: 1rem;
    box-shadow: 0 2px 12px rgba(0,0,0,0.06);
}
.taches-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1rem;
    padding-bottom: 0.75rem;
    border-bottom: 1px solid #eee;
}
.taches-title {
    font-size: 1.1rem;
    font-weight: 600;
    color: #1a1a2e;
}
.charge-badge {
    padding: 0.3rem 0.8rem;
    border-radius: 20px;
    font-size: 0.85rem;
    font-weight: 500;
}
.charge-leger { background: #d4edda; color: #155724; }
.charge-normal { background: #fff3cd; color: #856404; }
.charge-eleve { background: #f8d7da; color: #721c24; }

/* Tâche individuelle */
.tache-item {
    display: flex;
    align-items: center;
    padding: 0.75rem;
    margin: 0.5rem 0;
    border-radius: 8px;
    background: #f8f9fa;
    transition: all 0.2s ease;
}
.tache-item:hover {
    background: #e9ecef;
    transform: translateX(4px);
}
.tache-icon {
    width: 36px;
    height: 36px;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-right: 0.75rem;
    font-size: 1.1rem;
}
.tache-jardin { background: #d4edda; }
.tache-entretien { background: #cce5ff; }
.tache-charges { background: #fff3cd; }
.tache-depenses { background: #f5c6cb; }
.tache-content {
    flex: 1;
}
.tache-titre {
    font-weight: 500;
    color: #212529;
}
.tache-meta {
    font-size: 0.8rem;
    color: #6c757d;
}
.tache-duree {
    font-size: 0.85rem;
    color: #495057;
    background: white;
    padding: 0.25rem 0.6rem;
    border-radius: 4px;
}

/* Alertes */
.alerte-card {
    padding: 0.75rem 1rem;
    border-radius: 8px;
    margin-bottom: 0.5rem;
    display: flex;
    align-items: flex-start;
    gap: 0.75rem;
}
.alerte-info { background: #cce5ff; border-left: 3px solid #004085; }
.alerte-warning { background: #fff3cd; border-left: 3px solid #856404; }
.alerte-danger { background: #f8d7da; border-left: 3px solid #721c24; }
.alerte-success { background: #d4edda; border-left: 3px solid #155724; }
.alerte-icon { font-size: 1.2rem; }
.alerte-content { flex: 1; }
.alerte-titre { font-weight: 500; font-size: 0.9rem; }
.alerte-desc { font-size: 0.8rem; opacity: 0.85; }

/* Modules navigation */
.modules-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1rem;
    margin-top: 1.5rem;
}
.module-card {
    background: white;
    border-radius: 12px;
    padding: 1.25rem;
    text-align: center;
    box-shadow: 0 2px 12px rgba(0,0,0,0.06);
    transition: all 0.3s ease;
    cursor: pointer;
    border: 2px solid transparent;
}
.module-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 25px rgba(0,0,0,0.1);
}
.module-card.jardin:hover { border-color: #28a745; }
.module-card.entretien:hover { border-color: #007bff; }
.module-card.charges:hover { border-color: #ffc107; }
.module-card.depenses:hover { border-color: #dc3545; }
.module-icon {
    font-size: 2.5rem;
    margin-bottom: 0.5rem;
}
.module-titre {
    font-weight: 600;
    color: #1a1a2e;
    margin-bottom: 0.25rem;
}
.module-stat {
    font-size: 0.85rem;
    color: #6c757d;
}
.module-highlight {
    font-size: 0.8rem;
    padding: 0.2rem 0.5rem;
    border-radius: 4px;
    margin-top: 0.5rem;
    display: inline-block;
}
.highlight-success { background: #d4edda; color: #155724; }
.highlight-warning { background: #fff3cd; color: #856404; }
.highlight-info { background: #cce5ff; color: #004085; }

/* Stats section */
.stats-mini {
    display: flex;
    gap: 1rem;
    margin-top: 1rem;
}
.stat-item {
    flex: 1;
    text-align: center;
    padding: 0.75rem;
    background: #f8f9fa;
    border-radius: 8px;
}
.stat-value {
    font-size: 1.5rem;
    font-weight: bold;
    color: #1a1a2e;
}
.stat-label {
    font-size: 0.75rem;
    color: #6c757d;
    text-transform: uppercase;
}

/* Jauge charge */
.jauge-container {
    height: 8px;
    background: #e9ecef;
    border-radius: 4px;
    overflow: hidden;
    margin: 0.5rem 0;
}
.jauge-fill {
    height: 100%;
    border-radius: 4px;
    transition: width 0.5s ease;
}
.jauge-leger { background: linear-gradient(90deg, #28a745, #34ce57); }
.jauge-normal { background: linear-gradient(90deg, #ffc107, #ffda6a); }
.jauge-eleve { background: linear-gradient(90deg, #dc3545, #e4606d); }
</style>
"""


# ═══════════════════════════════════════════════════════════
# DONNÉES
# ═══════════════════════════════════════════════════════════


def _obtenir_stats_globales() -> dict:
    """Récupère les statistiques globales du hub."""
    stats = {
        "zones_jardin": 0,
        "pieces": 0,
        "objets_a_changer": 0,
        "taches_jour": 0,
        "temps_prevu_min": 0,
        "autonomie_pourcent": 47,  # TODO: calculer depuis recoltes
    }

    try:
        with obtenir_contexte_db() as db:
            # Zones jardin
            stats["zones_jardin"] = db.query(ZoneJardin).count()

            # Pièces
            stats["pieces"] = db.query(PieceMaison).count()

            # Objets à changer
            stats["objets_a_changer"] = (
                db.query(ObjetMaison)
                .filter(ObjetMaison.statut.in_(["a_changer", "a_reparer"]))
                .count()
            )

            # Sessions ce mois
            debut_mois = date.today().replace(day=1)
            sessions = (
                db.query(SessionTravail)
                .filter(SessionTravail.debut >= datetime.combine(debut_mois, datetime.min.time()))
                .all()
            )
            stats["temps_mois_heures"] = sum(s.duree_minutes or 0 for s in sessions) / 60

    except Exception:
        pass

    return stats


def _obtenir_taches_jour() -> list[dict]:
    """Récupère les tâches à faire aujourd'hui (mock pour l'instant)."""
    # TODO: Implémenter avec la vraie table taches_home
    return [
        {
            "id": 1,
            "titre": "Arroser les tomates",
            "domaine": "jardin",
            "duree_min": 15,
            "priorite": "normale",
            "zone": "Potager sud",
        },
        {
            "id": 2,
            "titre": "Passer l'aspirateur salon",
            "domaine": "entretien",
            "duree_min": 20,
            "priorite": "haute",
            "piece": "Salon",
        },
        {
            "id": 3,
            "titre": "Vérifier facture EDF",
            "domaine": "charges",
            "duree_min": 10,
            "priorite": "normale",
            "contrat": "EDF",
        },
    ]


def _obtenir_alertes() -> list[dict]:
    """Récupère les alertes actives (mock pour l'instant)."""
    alertes = []

    # TODO: Implémenter avec vraies données (météo, factures, etc.)
    # Exemple d'alertes
    alertes.append(
        {
            "type": "info",
            "icon": "🌡️",
            "titre": "Gel prévu vendredi",
            "description": "Pensez à protéger les plants sensibles",
        }
    )

    # Vérifier objets à changer
    try:
        with obtenir_contexte_db() as db:
            objets_urgents = (
                db.query(ObjetMaison)
                .filter(
                    ObjetMaison.statut == "a_changer",
                    ObjetMaison.priorite_remplacement == "urgente",
                )
                .count()
            )
            if objets_urgents > 0:
                alertes.append(
                    {
                        "type": "warning",
                        "icon": "🔧",
                        "titre": f"{objets_urgents} objet(s) à remplacer",
                        "description": "Priorité urgente - voir détails",
                    }
                )
    except Exception:
        pass

    return alertes


def _calculer_charge(taches: list[dict]) -> dict:
    """Calcule la charge quotidienne."""
    temps_total = sum(t.get("duree_min", 0) for t in taches)
    max_heures = 2  # Config par défaut: 2h max/jour

    pourcent = min(100, int((temps_total / (max_heures * 60)) * 100))

    if pourcent < 50:
        niveau = "leger"
    elif pourcent < 80:
        niveau = "normal"
    else:
        niveau = "eleve"

    return {
        "temps_min": temps_total,
        "temps_str": f"{temps_total // 60}h{temps_total % 60:02d}"
        if temps_total >= 60
        else f"{temps_total} min",
        "pourcent": pourcent,
        "niveau": niveau,
        "nb_taches": len(taches),
    }


# ═══════════════════════════════════════════════════════════
# COMPOSANTS UI
# ═══════════════════════════════════════════════════════════


def _render_header():
    """Affiche l'en-tête principal."""
    aujourdhui = date.today()
    jours = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
    mois = [
        "janvier",
        "février",
        "mars",
        "avril",
        "mai",
        "juin",
        "juillet",
        "août",
        "septembre",
        "octobre",
        "novembre",
        "décembre",
    ]

    date_str = f"{jours[aujourdhui.weekday()]} {aujourdhui.day} {mois[aujourdhui.month - 1]} {aujourdhui.year}"

    st.markdown(
        f"""
        <div class="hub-main-header">
            <h1>🏠 Maison</h1>
            <div class="hub-date">📅 {date_str}</div>
        </div>
    """,
        unsafe_allow_html=True,
    )


def _render_taches(taches: list[dict], charge: dict):
    """Affiche la section des tâches du jour."""
    niveau_class = f"charge-{charge['niveau']}"
    jauge_class = f"jauge-{charge['niveau']}"

    st.markdown(
        f"""
        <div class="taches-section">
            <div class="taches-header">
                <span class="taches-title">📋 Aujourd'hui</span>
                <span class="charge-badge {niveau_class}">
                    {charge['nb_taches']} tâches • {charge['temps_str']}
                </span>
            </div>
            <div class="jauge-container">
                <div class="jauge-fill {jauge_class}" style="width: {charge['pourcent']}%"></div>
            </div>
    """,
        unsafe_allow_html=True,
    )

    # Liste des tâches
    domaine_icons = {
        "jardin": ("🌳", "tache-jardin"),
        "entretien": ("🏡", "tache-entretien"),
        "charges": ("💡", "tache-charges"),
        "depenses": ("💰", "tache-depenses"),
    }

    for tache in taches:
        icon, icon_class = domaine_icons.get(tache["domaine"], ("📝", ""))
        meta_parts = []
        if "zone" in tache:
            meta_parts.append(tache["zone"])
        if "piece" in tache:
            meta_parts.append(tache["piece"])
        if "contrat" in tache:
            meta_parts.append(tache["contrat"])
        meta = " • ".join(meta_parts) if meta_parts else tache["domaine"].capitalize()

        st.markdown(
            f"""
            <div class="tache-item">
                <div class="tache-icon {icon_class}">{icon}</div>
                <div class="tache-content">
                    <div class="tache-titre">{tache['titre']}</div>
                    <div class="tache-meta">{meta}</div>
                </div>
                <div class="tache-duree">{tache['duree_min']} min</div>
            </div>
        """,
            unsafe_allow_html=True,
        )

    st.markdown("</div>", unsafe_allow_html=True)


def _render_alertes(alertes: list[dict]):
    """Affiche les alertes actives."""
    if not alertes:
        return

    st.markdown("#### 🚨 À noter")

    for alerte in alertes:
        type_class = f"alerte-{alerte['type']}"
        st.markdown(
            f"""
            <div class="alerte-card {type_class}">
                <span class="alerte-icon">{alerte['icon']}</span>
                <div class="alerte-content">
                    <div class="alerte-titre">{alerte['titre']}</div>
                    <div class="alerte-desc">{alerte['description']}</div>
                </div>
            </div>
        """,
            unsafe_allow_html=True,
        )


def _render_modules(stats: dict):
    """Affiche la navigation vers les modules."""
    st.markdown("#### 📂 Modules")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("�\n\n**Jardin**\n\n" + "Potager", use_container_width=True, key="btn_jardin"):
            GestionnaireEtat.naviguer_vers("maison.jardin")
            st.rerun()

        st.markdown(
            """
            <div style="text-align: center; margin-top: -0.5rem;">
                <span class="module-highlight highlight-success">Tâches auto</span>
            </div>
        """,
            unsafe_allow_html=True,
        )

    with col2:
        if st.button(
            "🏡\n\n**Entretien**\n\n" + "Équipements", use_container_width=True, key="btn_entretien"
        ):
            GestionnaireEtat.naviguer_vers("maison.entretien")
            st.rerun()

        st.markdown(
            """
            <div style="text-align: center; margin-top: -0.5rem;">
                <span class="module-highlight highlight-info">Score maison</span>
            </div>
        """,
            unsafe_allow_html=True,
        )

    with col3:
        if st.button(
            "💡\n\n**Charges**\n\nÉnergie & contrats", use_container_width=True, key="btn_charges"
        ):
            GestionnaireEtat.naviguer_vers("maison.charges")
            st.rerun()

        st.markdown(
            """
            <div style="text-align: center; margin-top: -0.5rem;">
                <span class="module-highlight highlight-info">Suivi factures</span>
            </div>
        """,
            unsafe_allow_html=True,
        )

    with col4:
        if st.button(
            "💰\n\n**Dépenses**\n\nBudget maison", use_container_width=True, key="btn_depenses"
        ):
            GestionnaireEtat.naviguer_vers("maison.depenses")
            st.rerun()

        st.markdown(
            """
            <div style="text-align: center; margin-top: -0.5rem;">
                <span class="module-highlight highlight-success">Voir budget</span>
            </div>
        """,
            unsafe_allow_html=True,
        )


def _render_stats_mois(stats: dict):
    """Affiche les mini stats du mois."""
    heures = stats.get("temps_mois_heures", 0)

    st.markdown(
        f"""
        <div class="stats-mini">
            <div class="stat-item">
                <div class="stat-value">{heures:.1f}h</div>
                <div class="stat-label">Ce mois</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">{stats.get('zones_jardin', 0)}</div>
                <div class="stat-label">Zones jardin</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">{stats.get('pieces', 0)}</div>
                <div class="stat-label">Pièces</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">{stats.get('autonomie_pourcent', 0)}%</div>
                <div class="stat-label">Autonomie</div>
            </div>
        </div>
    """,
        unsafe_allow_html=True,
    )


# ═══════════════════════════════════════════════════════════
# POINT D'ENTRÉE
# ═══════════════════════════════════════════════════════════


def app():
    """Point d'entrée du hub maison."""
    st.markdown(CSS, unsafe_allow_html=True)

    # Données
    stats = _obtenir_stats_globales()
    taches = _obtenir_taches_jour()
    alertes = _obtenir_alertes()
    charge = _calculer_charge(taches)

    # Rendu
    _render_header()

    # Layout principal
    col_main, col_side = st.columns([2, 1])

    with col_main:
        _render_taches(taches, charge)
        _render_modules(stats)

    with col_side:
        _render_alertes(alertes)
        _render_stats_mois(stats)

    # Actions rapides
    st.markdown("---")

    with st.expander("⚡ Actions rapides", expanded=False):
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("➕ Nouvelle tâche", use_container_width=True):
                st.info("Formulaire nouvelle tâche")
        with col2:
            if st.button("⏱️ Démarrer chrono", use_container_width=True):
                st.info("Lancer chronomètre")
        with col3:
            if st.button("📊 Stats détaillées", use_container_width=True):
                st.info("Voir statistiques")


# Export pour chargement différé
__all__ = ["app"]
