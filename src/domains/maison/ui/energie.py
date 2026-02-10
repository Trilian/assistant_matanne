"""
Dashboard Énergie - Suivi consommation gaz, électricité, eau.

Visualisation des consommations avec:
- Graphiques d'évolution sur 12 mois
- Comparaison année N vs N-1
- Alertes dépassement
- Prix unitaire par énergie
- Estimation du prochain relevé
"""

import streamlit as st
from datetime import date, timedelta
from typing import Optional
import plotly.graph_objects as go
import plotly.express as px

from src.core.database import obtenir_contexte_db
from src.core.models import HouseExpense


# ═══════════════════════════════════════════════════════════
# CONSTANTES
# ═══════════════════════════════════════════════════════════

ENERGIES = {
    "electricite": {
        "emoji": "⚡",
        "couleur": "#FFEB3B",
        "unite": "kWh",
        "label": "Électricité",
        "prix_moyen": 0.22,  # €/kWh estimé
    },
    "gaz": {
        "emoji": "🔥",
        "couleur": "#FF5722",
        "unite": "m³",
        "label": "Gaz",
        "prix_moyen": 0.11,  # €/m³ estimé
    },
    "eau": {
        "emoji": "💧",
        "couleur": "#2196F3",
        "unite": "m³",
        "label": "Eau",
        "prix_moyen": 4.50,  # €/m³ estimé
    },
}

MOIS_FR = ["", "Jan", "Fév", "Mar", "Avr", "Mai", "Juin", 
           "Juil", "Août", "Sep", "Oct", "Nov", "Déc"]


# ═══════════════════════════════════════════════════════════
# DATA LOADING
# ═══════════════════════════════════════════════════════════

@st.cache_data(ttl=300)
def charger_historique_energie(energie: str, nb_mois: int = 24) -> list[dict]:
    """Charge l'historique d'une énergie sur N mois."""
    today = date.today()
    result = []
    
    for i in range(nb_mois):
        mois = today.month - i
        annee = today.year
        while mois <= 0:
            mois += 12
            annee -= 1
        
        try:
            with obtenir_contexte_db() as db:
                depense = db.query(HouseExpense).filter(
                    HouseExpense.categorie == energie,
                    HouseExpense.mois == mois,
                    HouseExpense.annee == annee
                ).first()
            
            result.append({
                "mois": mois,
                "annee": annee,
                "label": f"{MOIS_FR[mois]} {annee}",
                "montant": float(depense.montant) if depense else None,
                "consommation": float(depense.consommation) if depense and depense.consommation else None,
            })
        except:
            result.append({
                "mois": mois,
                "annee": annee,
                "label": f"{MOIS_FR[mois]} {annee}",
                "montant": None,
                "consommation": None,
            })
    
    return list(reversed(result))


def get_stats_energie(energie: str) -> dict:
    """Calcule les stats pour une énergie."""
    historique = charger_historique_energie(energie, nb_mois=24)
    
    # Filtrer les valeurs non nulles
    avec_montant = [h for h in historique if h["montant"] is not None]
    avec_conso = [h for h in historique if h["consommation"] is not None]
    
    # 12 derniers mois
    recent = avec_montant[-12:] if len(avec_montant) >= 12 else avec_montant
    recent_conso = avec_conso[-12:] if len(avec_conso) >= 12 else avec_conso
    
    # Calculs
    total_annuel = sum(h["montant"] for h in recent) if recent else 0
    moyenne_mensuelle = total_annuel / len(recent) if recent else 0
    
    conso_totale = sum(h["consommation"] for h in recent_conso) if recent_conso else 0
    conso_moyenne = conso_totale / len(recent_conso) if recent_conso else 0
    
    # Dernier mois vs précédent
    dernier = recent[-1] if recent else {"montant": 0, "consommation": 0}
    precedent = recent[-2] if len(recent) >= 2 else {"montant": 0, "consommation": 0}
    
    delta_montant = dernier["montant"] - precedent["montant"] if precedent["montant"] else 0
    delta_conso = (dernier["consommation"] or 0) - (precedent["consommation"] or 0)
    
    # Prix unitaire moyen
    prix_unitaire = (total_annuel / conso_totale) if conso_totale > 0 else ENERGIES[energie]["prix_moyen"]
    
    return {
        "total_annuel": total_annuel,
        "moyenne_mensuelle": moyenne_mensuelle,
        "conso_totale": conso_totale,
        "conso_moyenne": conso_moyenne,
        "dernier_montant": dernier["montant"] or 0,
        "derniere_conso": dernier["consommation"] or 0,
        "delta_montant": delta_montant,
        "delta_conso": delta_conso,
        "prix_unitaire": prix_unitaire,
    }


# ═══════════════════════════════════════════════════════════
# GRAPHIQUES
# ═══════════════════════════════════════════════════════════

def graphique_evolution(energie: str, afficher_conso: bool = True):
    """Graphique d'évolution sur 12 mois."""
    info = ENERGIES[energie]
    historique = charger_historique_energie(energie, nb_mois=12)
    
    # Filtrer les valeurs nulles pour l'affichage
    labels = [h["label"] for h in historique]
    montants = [h["montant"] for h in historique]
    consos = [h["consommation"] for h in historique]
    
    fig = go.Figure()
    
    # Barres pour les montants
    fig.add_trace(go.Bar(
        x=labels,
        y=montants,
        name="Montant (€)",
        marker_color=info["couleur"],
        text=[f"{m:.0f}€" if m else "" for m in montants],
        textposition="outside",
    ))
    
    # Ligne pour la consommation
    if afficher_conso and any(c for c in consos):
        fig.add_trace(go.Scatter(
            x=labels,
            y=consos,
            name=f"Conso ({info['unite']})",
            mode="lines+markers",
            yaxis="y2",
            line=dict(color="#333", width=2),
            marker=dict(size=8),
        ))
    
    fig.update_layout(
        title=f"{info['emoji']} Évolution {info['label']} (12 mois)",
        yaxis_title="Montant (€)",
        yaxis2=dict(
            title=f"Consommation ({info['unite']})",
            overlaying="y",
            side="right"
        ) if afficher_conso else None,
        height=400,
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
    )
    
    return fig


def graphique_comparaison_annees(energie: str):
    """Compare année N vs N-1."""
    info = ENERGIES[energie]
    historique = charger_historique_energie(energie, nb_mois=24)
    
    today = date.today()
    annee_courante = today.year
    
    # Séparer par année
    donnees_n = [h for h in historique if h["annee"] == annee_courante]
    donnees_n1 = [h for h in historique if h["annee"] == annee_courante - 1]
    
    fig = go.Figure()
    
    # Année N-1
    fig.add_trace(go.Bar(
        x=[MOIS_FR[h["mois"]] for h in donnees_n1],
        y=[h["montant"] or 0 for h in donnees_n1],
        name=str(annee_courante - 1),
        marker_color="#BDBDBD",
    ))
    
    # Année N
    fig.add_trace(go.Bar(
        x=[MOIS_FR[h["mois"]] for h in donnees_n],
        y=[h["montant"] or 0 for h in donnees_n],
        name=str(annee_courante),
        marker_color=info["couleur"],
    ))
    
    fig.update_layout(
        title=f"{info['emoji']} Comparaison {annee_courante-1} vs {annee_courante}",
        yaxis_title="Montant (€)",
        barmode="group",
        height=350,
    )
    
    return fig


def graphique_repartition():
    """Répartition des dépenses énergie."""
    totaux = {}
    for energie in ENERGIES:
        stats = get_stats_energie(energie)
        totaux[energie] = stats["total_annuel"]
    
    labels = [ENERGIES[e]["label"] for e in totaux]
    values = list(totaux.values())
    colors = [ENERGIES[e]["couleur"] for e in totaux]
    
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        marker_colors=colors,
        textinfo="label+percent",
        textposition="inside",
    )])
    
    fig.update_layout(
        title="🔋 Répartition annuelle",
        height=300,
    )
    
    return fig


# ═══════════════════════════════════════════════════════════
# UI COMPONENTS
# ═══════════════════════════════════════════════════════════

def render_metric_energie(energie: str):
    """Affiche les métriques d'une énergie."""
    info = ENERGIES[energie]
    stats = get_stats_energie(energie)
    
    with st.container(border=True):
        st.markdown(f"### {info['emoji']} {info['label']}")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            delta = f"{stats['delta_montant']:+.0f}€" if stats["delta_montant"] != 0 else None
            st.metric(
                "Dernier mois",
                f"{stats['dernier_montant']:.0f}€",
                delta=delta,
                delta_color="inverse"
            )
        
        with col2:
            st.metric(
                "Moyenne mensuelle",
                f"{stats['moyenne_mensuelle']:.0f}€"
            )
        
        with col3:
            st.metric(
                "Total 12 mois",
                f"{stats['total_annuel']:.0f}€"
            )
        
        # Consommation si disponible
        if stats["conso_moyenne"] > 0:
            st.caption(
                f"📏 Conso moyenne: **{stats['conso_moyenne']:.1f} {info['unite']}/mois** • "
                f"Prix: **{stats['prix_unitaire']:.3f}€/{info['unite']}**"
            )


def render_dashboard_global():
    """Dashboard global toutes énergies."""
    st.subheader("📊 Vue d'ensemble")
    
    # Métriques globales
    total_annuel = sum(get_stats_energie(e)["total_annuel"] for e in ENERGIES)
    moyenne_mensuelle = total_annuel / 12
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("💰 Total annuel énergies", f"{total_annuel:.0f}€")
    with col2:
        st.metric("📅 Moyenne mensuelle", f"{moyenne_mensuelle:.0f}€")
    
    st.divider()
    
    # Métriques par énergie
    for energie in ENERGIES:
        render_metric_energie(energie)


def render_detail_energie(energie: str):
    """Affiche le détail d'une énergie."""
    info = ENERGIES[energie]
    stats = get_stats_energie(energie)
    
    st.subheader(f"{info['emoji']} Détail {info['label']}")
    
    # KPIs
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total 12 mois", f"{stats['total_annuel']:.0f}€")
    with col2:
        st.metric("Moyenne/mois", f"{stats['moyenne_mensuelle']:.0f}€")
    with col3:
        st.metric("Conso totale", f"{stats['conso_totale']:.0f} {info['unite']}")
    with col4:
        st.metric("Prix unitaire", f"{stats['prix_unitaire']:.3f}€/{info['unite']}")
    
    # Graphiques
    tab1, tab2 = st.tabs(["📈 Évolution", "📊 Comparaison N/N-1"])
    
    with tab1:
        afficher_conso = st.checkbox("Afficher consommation", value=True, key=f"conso_{energie}")
        fig = graphique_evolution(energie, afficher_conso)
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        fig = graphique_comparaison_annees(energie)
        st.plotly_chart(fig, use_container_width=True)


def render_alertes():
    """Affiche les alertes de consommation."""
    st.subheader("⚠️ Alertes")
    
    alertes = []
    
    for energie, info in ENERGIES.items():
        stats = get_stats_energie(energie)
        
        # Alerte si dernier mois > 120% de la moyenne
        if stats["dernier_montant"] > stats["moyenne_mensuelle"] * 1.2:
            pct = (stats["dernier_montant"] / stats["moyenne_mensuelle"] - 1) * 100
            alertes.append({
                "energie": energie,
                "emoji": info["emoji"],
                "label": info["label"],
                "message": f"Facture {info['label']} en hausse de {pct:.0f}% vs moyenne",
                "type": "warning"
            })
        
        # Alerte si consommation en forte hausse
        if stats["delta_conso"] > stats["conso_moyenne"] * 0.3:
            alertes.append({
                "energie": energie,
                "emoji": info["emoji"],
                "label": info["label"],
                "message": f"Consommation {info['label']} en forte hausse (+{stats['delta_conso']:.0f} {info['unite']})",
                "type": "error"
            })
    
    if alertes:
        for alerte in alertes:
            if alerte["type"] == "error":
                st.error(f"{alerte['emoji']} {alerte['message']}")
            else:
                st.warning(f"{alerte['emoji']} {alerte['message']}")
    else:
        st.success("✅ Aucune alerte de consommation")


# ═══════════════════════════════════════════════════════════
# PAGE PRINCIPALE
# ═══════════════════════════════════════════════════════════

def app():
    """Point d'entrée du dashboard énergie."""
    st.title("🔋 Dashboard Énergie")
    st.caption("Suivi consommation gaz, électricité, eau")
    
    # Tabs
    tabs = st.tabs([
        "📊 Vue globale",
        "⚡ Électricité",
        "🔥 Gaz",
        "💧 Eau",
        "⚠️ Alertes"
    ])
    
    with tabs[0]:
        render_dashboard_global()
        
        st.divider()
        
        # Graphique répartition
        col1, col2 = st.columns(2)
        with col1:
            fig = graphique_repartition()
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            render_alertes()
    
    with tabs[1]:
        render_detail_energie("electricite")
    
    with tabs[2]:
        render_detail_energie("gaz")
    
    with tabs[3]:
        render_detail_energie("eau")
    
    with tabs[4]:
        render_alertes()
        
        st.divider()
        st.markdown("### 💡 Conseils économies")
        st.info("""
        **Électricité:**
        - Débrancher les appareils en veille
        - Utiliser des ampoules LED
        - Privilégier heures creuses
        
        **Gaz:**
        - Baisser chauffage de 1°C = -7% conso
        - Entretenir la chaudière
        - Isoler les fenêtres
        
        **Eau:**
        - Douche vs bain
        - Mousseurs sur robinets
        - Réparer les fuites
        """)


if __name__ == "__main__":
    app()

