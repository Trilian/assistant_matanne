"""
Composants réutilisables pour le module planning
"""

from datetime import date, datetime
import streamlit as st


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# BADGES & INDICATEURS
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


def afficher_badge_charge(charge_score: int, taille: str = "normal") -> None:
    """Affiche badge visuel de charge"""
    if charge_score < 35:
        emoji = "🔔"
        label = "Faible"
        couleur = "#00AA00"
    elif charge_score < 70:
        emoji = "💰"
        label = "Normal"
        couleur = "#FFAA00"
    else:
        emoji = "❌"
        label = "Intense"
        couleur = "#FF0000"

    if taille == "petit":
        st.write(f"{emoji} {label}")
    else:
        st.markdown(f"### {emoji} {label} ({charge_score}/100)")


def afficher_badge_priorite(priorite: str) -> None:
    """Affiche badge de priorité (basse, moyenne, haute)"""
    priorite_emoji = {
        "basse": ("🔔", "Basse"),
        "moyenne": ("💰", "Moyenne"),
        "haute": ("❌", "Haute"),
    }

    emoji, label = priorite_emoji.get(priorite.lower(), ("⚫", "Autre"))
    st.write(f"{emoji} {label}")


def afficher_badge_activite_jules(adapte: bool) -> None:
    """Badge indiquant si activité est adaptée à Jules"""
    if adapte:
        st.write("👶 Adapté Jules (19m)")
    else:
        st.write("📅 Activité famille")


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# SELECTEURS & FORMULAIRES
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


def selecteur_semaine(key_prefix: str = "semaine") -> tuple[date, date]:
    """Selecteur de semaine (retourne date_debut, date_fin)"""
    if f"{key_prefix}_start" not in st.session_state:
        today = date.today()
        st.session_state[f"{key_prefix}_start"] = today - __import__("datetime").timedelta(days=today.weekday())

    col_nav1, col_nav2, col_nav3 = st.columns([1, 2, 1])

    with col_nav1:
        if st.button("â¬…ï¸ Précédente", key=f"{key_prefix}_prev"):
            st.session_state[f"{key_prefix}_start"] -= __import__("datetime").timedelta(days=7)
            st.rerun()

    with col_nav2:
        week_start = st.session_state[f"{key_prefix}_start"]
        week_end = week_start + __import__("datetime").timedelta(days=6)
        st.markdown(
            f"<h3 style='text-align: center;'>{week_start.strftime('%d/%m')} – {week_end.strftime('%d/%m/%Y')}</h3>",
            unsafe_allow_html=True,
        )

    with col_nav3:
        if st.button("Suivante âž¡ï¸", key=f"{key_prefix}_next"):
            st.session_state[f"{key_prefix}_start"] += __import__("datetime").timedelta(days=7)
            st.rerun()

    week_start = st.session_state[f"{key_prefix}_start"]
    week_end = week_start + __import__("datetime").timedelta(days=6)

    return week_start, week_end


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# CARTES & AFFICHAGE ÉVÉNEMENTS
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


def carte_repas(repas: dict) -> None:
    """Carte pour afficher un repas"""
    with st.container():
        col1, col2 = st.columns([3, 1])

        with col1:
            st.write(f"**{repas['type'].upper()}**: {repas['recette']}")

        with col2:
            st.caption(f"{repas['portions']} portions")

        if repas.get("temps_total"):
            st.caption(f"⏱️ {repas['temps_total']} min")

        if repas.get("notes"):
            st.caption(f"🗑️ {repas['notes']}")


def carte_activite(activite: dict) -> None:
    """Carte pour afficher une activité"""
    with st.container():
        label = "👶" if activite.get("pour_jules") else "📅"
        col1, col2 = st.columns([3, 1])

        with col1:
            st.write(f"{label} **{activite['titre']}**")
            st.caption(f"Type: {activite.get('type', 'N/A')}")

        with col2:
            if activite.get("budget"):
                st.metric("Budget", f"{activite['budget']:.0f}€")


def carte_projet(projet: dict) -> None:
    """Carte pour afficher un projet"""
    priorite_emoji = {
        "basse": "🔔",
        "moyenne": "💰",
        "haute": "❌",
    }.get(projet.get("priorite", "moyenne"), "⚫")

    with st.container():
        st.write(f"{priorite_emoji} **{projet['nom']}**")
        st.caption(f"Statut: {projet.get('statut', 'N/A')}")

        if projet.get("echéance"):
            st.caption(f"Échéance: {projet['echéance'].strftime('%d/%m')}")


def carte_event(event: dict) -> None:
    """Carte pour afficher un événement calendrier"""
    with st.container():
        debut = (
            event["debut"].strftime("%H:%M")
            if isinstance(event["debut"], datetime)
            else "–"
        )

        col1, col2 = st.columns([3, 1])

        with col1:
            st.write(f"**{event['titre']}**")
            if event.get("lieu"):
                st.caption(f"🗑️ {event['lieu']}")

        with col2:
            st.caption(debut)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# ALERTS & NOTIFICATIONS
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


def afficher_alerte(alerte: str, type_alerte: str = "warning") -> None:
    """Affiche une alerte (warning, error, success, info)"""
    if type_alerte == "warning":
        st.warning(alerte, icon="âš ï¸")
    elif type_alerte == "error":
        st.error(alerte, icon="❌")
    elif type_alerte == "success":
        st.success(alerte, icon="✅")
    else:
        st.info(alerte, icon="ℹ️")


def afficher_liste_alertes(alertes: list[str]) -> None:
    """Affiche liste d'alertes groupées"""
    if not alertes:
        return

    st.markdown("### âš ï¸ Alertes")
    for alerte in alertes:
        afficher_alerte(alerte)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# STATISTIQUES
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


def afficher_stats_semaine(stats: dict) -> None:
    """Affiche statistiques semaine en colonnes"""
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric("📷 Repas", stats.get("total_repas", 0))

    with col2:
        st.metric("🎨 Activités", stats.get("total_activites", 0))

    with col3:
        st.metric("👶 Pour Jules", stats.get("activites_jules", 0))

    with col4:
        st.metric("📋 Projets", stats.get("total_projets", 0))

    with col5:
        budget = stats.get("budget_total", 0)
        st.metric("📱 Budget", f"{budget:.0f}€")

