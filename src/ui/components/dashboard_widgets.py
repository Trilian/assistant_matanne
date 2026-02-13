"""
Dashboard Widgets - Composants enrichis pour le tableau de bord.

Fournit des widgets visuels avancés :
- Graphiques Plotly interactifs
- Cartes métriques améliorées
- Timeline d'activité
- Indicateurs de santé système
"""

import logging
from datetime import date, datetime, timedelta
from typing import Any

import plotly.graph_objects as go
import streamlit as st

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# GRAPHIQUES PLOTLY
# ═══════════════════════════════════════════════════════════


def graphique_repartition_repas(planning_data: list[dict]) -> go.Figure | None:
    """
    Graphique en camembert de la répartition des repas par type.

    Args:
        planning_data: Liste des repas planifiés

    Returns:
        Figure Plotly ou None si pas de données
    """
    if not planning_data:
        return None

    # Compter par type
    types_count = {}
    for repas in planning_data:
        type_repas = repas.get("type_repas", "autre")
        types_count[type_repas] = types_count.get(type_repas, 0) + 1

    # Couleurs personnalisées
    couleurs = {
        "petit_déjeuner": "#FFB74D",
        "déjeuner": "#4CAF50",
        "dîner": "#2196F3",
        "goûter": "#E91E63",
    }

    labels = list(types_count.keys())
    values = list(types_count.values())
    colors = [couleurs.get(t, "#9E9E9E") for t in labels]

    # Labels français
    labels_fr = {
        "petit_déjeuner": "Petit-déjeuner",
        "déjeuner": "Déjeuner",
        "dîner": "Dîner",
        "goûter": "Goûter",
    }
    labels = [labels_fr.get(l, l.capitalize()) for l in labels]

    fig = go.Figure(
        data=[
            go.Pie(
                labels=labels,
                values=values,
                hole=0.4,
                marker_colors=colors,
                textinfo="label+percent",
                textposition="outside",
            )
        ]
    )

    fig.update_layout(
        showlegend=False,
        margin=dict(l=20, r=20, t=30, b=20),
        height=250,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )

    return fig


def graphique_inventaire_categories(inventaire: list[dict]) -> go.Figure | None:
    """
    Graphique en barres horizontales du stock par catégorie.

    Args:
        inventaire: Liste des articles

    Returns:
        Figure Plotly
    """
    if not inventaire:
        return None

    # Grouper par catégorie
    categories = {}
    for article in inventaire:
        cat = article.get("categorie", "Autre")
        if cat not in categories:
            categories[cat] = {"total": 0, "bas": 0}
        categories[cat]["total"] += 1
        if article.get("statut") in ["critique", "sous_seuil"]:
            categories[cat]["bas"] += 1

    # Trier par total décroissant
    sorted_cats = sorted(categories.items(), key=lambda x: x[1]["total"], reverse=True)[:8]

    cat_names = [c[0] for c in sorted_cats]
    totaux = [c[1]["total"] for c in sorted_cats]
    bas = [c[1]["bas"] for c in sorted_cats]

    fig = go.Figure()

    # Barres stock normal
    fig.add_trace(
        go.Bar(
            y=cat_names,
            x=[t - b for t, b in zip(totaux, bas, strict=False)],
            name="Stock OK",
            orientation="h",
            marker_color="#4CAF50",
        )
    )

    # Barres stock bas
    fig.add_trace(
        go.Bar(
            y=cat_names,
            x=bas,
            name="Stock bas",
            orientation="h",
            marker_color="#FF5722",
        )
    )

    fig.update_layout(
        barmode="stack",
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        margin=dict(l=100, r=20, t=40, b=20),
        height=280,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis_title="Articles",
    )

    return fig


def graphique_activite_semaine(activites: list[dict]) -> go.Figure | None:
    """
    Graphique de l'activité sur les 7 derniers jours.

    Args:
        activites: Liste avec {'date': date, 'count': int, 'type': str}

    Returns:
        Figure Plotly
    """
    if not activites:
        # Générer des données vides pour les 7 jours
        today = date.today()
        activites = [
            {"date": today - timedelta(days=i), "count": 0, "type": "aucune"}
            for i in range(6, -1, -1)
        ]

    dates = [
        a["date"] if isinstance(a["date"], date) else date.fromisoformat(str(a["date"]))
        for a in activites
    ]
    counts = [a.get("count", 0) for a in activites]

    # Noms des jours
    jours_fr = ["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"]
    labels = [jours_fr[d.weekday()] for d in dates]

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=labels,
            y=counts,
            mode="lines+markers",
            line=dict(color="#2196F3", width=3),
            marker=dict(size=10, color="#2196F3"),
            fill="tozeroy",
            fillcolor="rgba(33, 150, 243, 0.1)",
        )
    )

    fig.update_layout(
        margin=dict(l=40, r=20, t=20, b=40),
        height=200,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        yaxis=dict(showgrid=True, gridcolor="rgba(0,0,0,0.1)"),
        xaxis=dict(showgrid=False),
    )

    return fig


def graphique_progression_objectifs(objectifs: list[dict]) -> go.Figure | None:
    """
    Graphique de progression des objectifs.

    Args:
        objectifs: Liste {'nom': str, 'actuel': float, 'cible': float}

    Returns:
        Figure Plotly
    """
    if not objectifs:
        return None

    noms = [o["nom"] for o in objectifs]
    progressions = [min(100, (o.get("actuel", 0) / o.get("cible", 1)) * 100) for o in objectifs]

    # Couleurs selon progression
    colors = ["#4CAF50" if p >= 80 else "#FFB74D" if p >= 50 else "#FF5722" for p in progressions]

    fig = go.Figure()

    # Barres de fond (100%)
    fig.add_trace(
        go.Bar(
            y=noms,
            x=[100] * len(noms),
            orientation="h",
            marker_color="rgba(0,0,0,0.1)",
            showlegend=False,
        )
    )

    # Barres de progression
    fig.add_trace(
        go.Bar(
            y=noms,
            x=progressions,
            orientation="h",
            marker_color=colors,
            text=[f"{p:.0f}%" for p in progressions],
            textposition="inside",
            showlegend=False,
        )
    )

    fig.update_layout(
        barmode="overlay",
        margin=dict(l=120, r=20, t=20, b=20),
        height=200,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showticklabels=False, showgrid=False),
    )

    return fig


# ═══════════════════════════════════════════════════════════
# CARTES MÉTRIQUES
# ═══════════════════════════════════════════════════════════


def carte_metrique_avancee(
    titre: str,
    valeur: Any,
    icone: str,
    delta: str | None = None,
    delta_positif: bool = True,
    sous_titre: str | None = None,
    couleur: str = "#4CAF50",
    lien_module: str | None = None,
):
    """
    Carte métrique stylisée.

    Args:
        titre: Titre de la métrique
        valeur: Valeur principale
        icone: Emoji icône
        delta: Variation (optionnel)
        delta_positif: Si la variation est positive
        sous_titre: Texte secondaire
        couleur: Couleur d'accent
        lien_module: Module vers lequel naviguer
    """
    delta_html = ""
    if delta:
        delta_color = "#4CAF50" if delta_positif else "#FF5722"
        delta_arrow = "â†‘" if delta_positif else "â†“"
        delta_html = (
            f'<span style="color: {delta_color}; font-size: 0.9rem;">{delta_arrow} {delta}</span>'
        )

    sous_titre_html = (
        f'<p style="color: #6c757d; margin: 0; font-size: 0.85rem;">{sous_titre}</p>'
        if sous_titre
        else ""
    )

    html = f"""
    <div style="
        background: linear-gradient(135deg, {couleur}15, {couleur}05);
        border-left: 4px solid {couleur};
        border-radius: 12px;
        padding: 1.2rem;
        margin-bottom: 0.5rem;
    ">
        <div style="display: flex; justify-content: space-between; align-items: flex-start;">
            <div>
                <p style="color: #6c757d; margin: 0 0 0.3rem 0; font-size: 0.9rem;">{titre}</p>
                <h2 style="margin: 0; color: #212529;">{valeur}</h2>
                {delta_html}
                {sous_titre_html}
            </div>
            <span style="font-size: 2.5rem;">{icone}</span>
        </div>
    </div>
    """

    st.markdown(html, unsafe_allow_html=True)

    if lien_module:
        if st.button(f"Voir {titre}", key=f"link_{lien_module}", use_container_width=True):
            from src.core.state import GestionnaireEtat

            GestionnaireEtat.naviguer_vers(lien_module)
            st.rerun()


def indicateur_sante_systeme() -> dict:
    """
    Calcule les indicateurs de santé du système.

    Returns:
        Dict avec status et détails
    """
    status = {"global": "ok", "details": []}

    try:
        # Vérifier la connexion DB
        from src.core.database import verifier_connexion

        if verifier_connexion():
            status["details"].append(
                {"nom": "Base de données", "status": "ok", "message": "Connectée"}
            )
        else:
            status["details"].append(
                {"nom": "Base de données", "status": "error", "message": "Déconnectée"}
            )
            status["global"] = "error"
    except Exception as e:
        status["details"].append({"nom": "Base de données", "status": "error", "message": str(e)})
        status["global"] = "error"

    try:
        # Vérifier le cache
        from src.core.cache_multi import obtenir_cache

        cache = obtenir_cache()
        cache_stats = cache.get_stats()
        hit_rate = float(cache_stats.get("hit_rate", "0%").replace("%", ""))

        if hit_rate >= 70:
            status["details"].append(
                {"nom": "Cache", "status": "ok", "message": f"Hit rate: {hit_rate:.0f}%"}
            )
        elif hit_rate >= 40:
            status["details"].append(
                {"nom": "Cache", "status": "warning", "message": f"Hit rate: {hit_rate:.0f}%"}
            )
            if status["global"] == "ok":
                status["global"] = "warning"
        else:
            status["details"].append(
                {"nom": "Cache", "status": "warning", "message": f"Hit rate bas: {hit_rate:.0f}%"}
            )
    except Exception:
        status["details"].append({"nom": "Cache", "status": "ok", "message": "Initialisé"})

    return status


def afficher_sante_systeme():
    """Affiche les indicateurs de santé."""

    status = indicateur_sante_systeme()

    # Icône global
    icon_map = {"ok": "ðŸŸ¢", "warning": "ðŸŸ¡", "error": "ðŸ”´"}
    global_icon = icon_map.get(status["global"], "âšª")

    with st.expander(f"{global_icon} Santé Système", expanded=False):
        for detail in status["details"]:
            icon = icon_map.get(detail["status"], "âšª")
            st.write(f"{icon} **{detail['nom']}**: {detail['message']}")


# ═══════════════════════════════════════════════════════════
# TIMELINE D'ACTIVITÉ
# ═══════════════════════════════════════════════════════════


def afficher_timeline_activites(activites: list[dict], max_items: int = 5):
    """
    Affiche une timeline des activités récentes.

    Args:
        activites: Liste {'date': datetime, 'action': str, 'type': str}
        max_items: Nombre max d'items à afficher
    """
    if not activites:
        st.info("Aucune activité récente")
        return

    # Icônes par type
    icones = {
        "recette": "ðŸ½ï¸",
        "inventaire": "ðŸ“¦",
        "courses": "ðŸ›’",
        "planning": "ðŸ“…",
        "famille": "ðŸ‘¨â€ðŸ‘©â€ðŸ‘¦",
        "maison": "ðŸ ",
    }

    st.markdown("### ðŸ“‹ Activité Récente")

    for activite in activites[:max_items]:
        icone = icones.get(activite.get("type", ""), "ðŸ“Œ")
        date_str = activite.get("date", "")
        if isinstance(date_str, datetime):
            date_str = date_str.strftime("%d/%m %H:%M")

        action = activite.get("action", "Action")

        st.markdown(
            f'<div style="padding: 0.5rem; margin: 0.3rem 0; '
            f'background: #f8f9fa; border-radius: 8px; display: flex; align-items: center;">'
            f'<span style="margin-right: 0.8rem; font-size: 1.3rem;">{icone}</span>'
            f"<div>"
            f'<span style="font-weight: 500;">{action}</span><br>'
            f'<small style="color: #6c757d;">{date_str}</small>'
            f"</div>"
            f"</div>",
            unsafe_allow_html=True,
        )


# ═══════════════════════════════════════════════════════════
# WIDGETS FAMILLE JULES
# ═══════════════════════════════════════════════════════════


def widget_jules_apercu():
    """Widget d'aperçu de Jules pour le dashboard."""

    # Calculer l'âge de Jules (né le 15/06/2024)
    from datetime import date

    naissance = date(2024, 6, 15)
    aujourd_hui = date.today()
    age_jours = (aujourd_hui - naissance).days
    age_mois = age_jours // 30

    st.markdown(
        f"""
        <div style="
            background: linear-gradient(135deg, #E3F2FD, #BBDEFB);
            border-radius: 16px;
            padding: 1.5rem;
            text-align: center;
        ">
            <span style="font-size: 3rem;">ðŸ‘¶</span>
            <h3 style="margin: 0.5rem 0;">Jules</h3>
            <p style="margin: 0; color: #1565C0; font-weight: 500;">{age_mois} mois</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def widget_meteo_jour():
    """Widget météo simplifié (données statiques pour demo)."""

    # Données simulées - à remplacer par API météo
    meteo = {
        "temp": 12,
        "condition": "â˜ï¸ Nuageux",
        "conseil": "Prévoir une veste légère",
    }

    st.markdown(
        f"""
        <div style="
            background: linear-gradient(135deg, #FFF8E1, #FFECB3);
            border-radius: 12px;
            padding: 1rem;
            text-align: center;
        ">
            <span style="font-size: 2rem;">{meteo["condition"].split()[0]}</span>
            <p style="margin: 0.3rem 0; font-size: 1.5rem; font-weight: 600;">{meteo["temp"]}°C</p>
            <small style="color: #6c757d;">{meteo["conseil"]}</small>
        </div>
        """,
        unsafe_allow_html=True,
    )
