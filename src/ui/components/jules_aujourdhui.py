"""
Vue "Ce que Jules a fait aujourd'hui" - Résumé quotidien automatique.

Génère un résumé des activités de Jules exportable
en message WhatsApp/SMS pour les proches.

Usage:
    from src.ui.components import widget_jules_aujourdhui, exporter_resume_jules

    widget_jules_aujourdhui()
"""

import logging
from datetime import date, datetime, timedelta

import streamlit as st

from src.core.state import naviguer
from src.ui.keys import KeyNamespace
from src.ui.registry import composant_ui
from src.ui.tokens_semantic import Sem

logger = logging.getLogger(__name__)

_keys = KeyNamespace("jules_aujourdhui")


# ═══════════════════════════════════════════════════════════
# SERVICE
# ═══════════════════════════════════════════════════════════


def obtenir_activites_jules_aujourdhui() -> list[dict]:
    """
    Récupère les activités de Jules pour aujourd'hui.

    Returns:
        Liste d'activités avec détails
    """
    try:
        from src.core.db import obtenir_contexte_db
        from src.core.models import ActiviteJules

        aujourdhui = date.today()

        with obtenir_contexte_db() as session:
            activites = (
                session.query(ActiviteJules)
                .filter(ActiviteJules.date_activite == aujourdhui)
                .order_by(ActiviteJules.heure_debut)
                .all()
            )

            return [
                {
                    "id": a.id,
                    "titre": a.titre,
                    "type": a.type_activite,
                    "heure": a.heure_debut.strftime("%H:%M") if a.heure_debut else None,
                    "duree": a.duree_minutes,
                    "notes": a.notes,
                    "humeur": a.humeur,
                    "icone": _get_activite_icone(a.type_activite),
                }
                for a in activites
            ]

    except Exception as e:
        logger.debug(f"Activités Jules non disponibles: {e}")

    return []


def obtenir_repas_jules_aujourdhui() -> list[dict]:
    """
    Récupère les repas de Jules pour aujourd'hui.

    Returns:
        Liste des repas avec détails
    """
    try:
        from src.core.db import obtenir_contexte_db
        from src.core.models import RepasJules

        aujourdhui = date.today()

        with obtenir_contexte_db() as session:
            repas = (
                session.query(RepasJules)
                .filter(RepasJules.date_repas == aujourdhui)
                .order_by(RepasJules.heure_repas)
                .all()
            )

            return [
                {
                    "type": r.type_repas,
                    "heure": r.heure_repas.strftime("%H:%M") if r.heure_repas else None,
                    "aliments": r.aliments,
                    "quantite": r.quantite_mangee,
                    "commentaire": r.commentaire,
                }
                for r in repas
            ]

    except Exception as e:
        logger.debug(f"Repas Jules non disponibles: {e}")

    return []


def obtenir_siestes_jules_aujourdhui() -> list[dict]:
    """
    Récupère les siestes de Jules pour aujourd'hui.

    Returns:
        Liste des siestes avec détails
    """
    try:
        from src.core.db import obtenir_contexte_db
        from src.core.models import SiesteJules

        aujourdhui = date.today()

        with obtenir_contexte_db() as session:
            siestes = (
                session.query(SiesteJules)
                .filter(SiesteJules.date_sieste == aujourdhui)
                .order_by(SiesteJules.heure_debut)
                .all()
            )

            return [
                {
                    "heure_debut": s.heure_debut.strftime("%H:%M") if s.heure_debut else None,
                    "heure_fin": s.heure_fin.strftime("%H:%M") if s.heure_fin else None,
                    "duree": s.duree_minutes,
                    "qualite": s.qualite,
                }
                for s in siestes
            ]

    except Exception as e:
        logger.debug(f"Siestes Jules non disponibles: {e}")

    return []


def generer_resume_jules(
    activites: list[dict],
    repas: list[dict] | None = None,
    siestes: list[dict] | None = None,
    format_export: str = "whatsapp",
) -> str:
    """
    Génère un résumé textuel de la journée de Jules.

    Args:
        activites: Liste des activités
        repas: Liste des repas (optionnel)
        siestes: Liste des siestes (optionnel)
        format_export: "whatsapp", "sms", "email"

    Returns:
        Texte formaté du résumé
    """
    aujourdhui = date.today().strftime("%d/%m/%Y")

    # Emoji selon format
    use_emoji = format_export in ("whatsapp", "email")

    lines = []

    # Header
    if use_emoji:
        lines.append(f"👶 *Journée de Jules - {aujourdhui}*")
    else:
        lines.append(f"Journée de Jules - {aujourdhui}")

    lines.append("")

    # Activités
    if activites:
        if use_emoji:
            lines.append("🎯 *Activités:*")
        else:
            lines.append("Activités:")

        for a in activites:
            heure = f"[{a['heure']}] " if a.get("heure") else ""
            duree = f" ({a['duree']} min)" if a.get("duree") else ""
            icone = a.get("icone", "") + " " if use_emoji else ""
            lines.append(f"• {heure}{icone}{a['titre']}{duree}")

            if a.get("notes"):
                lines.append(f"  → {a['notes']}")

        lines.append("")

    # Repas
    if repas:
        if use_emoji:
            lines.append("🍽️ *Repas:*")
        else:
            lines.append("Repas:")

        for r in repas:
            heure = f"[{r['heure']}] " if r.get("heure") else ""
            quantite = f" - {r['quantite']}" if r.get("quantite") else ""
            lines.append(f"• {heure}{r['type']}: {r['aliments']}{quantite}")

        lines.append("")

    # Siestes
    if siestes:
        total_sieste = sum(s.get("duree", 0) or 0 for s in siestes)

        if use_emoji:
            lines.append(f"😴 *Siestes:* {total_sieste} min au total")
        else:
            lines.append(f"Siestes: {total_sieste} min au total")

        for s in siestes:
            debut = s.get("heure_debut", "?")
            fin = s.get("heure_fin", "?")
            qualite = f" ({s['qualite']})" if s.get("qualite") else ""
            lines.append(f"• {debut} → {fin}{qualite}")

        lines.append("")

    # Humeur générale
    if activites:
        humeurs = [a["humeur"] for a in activites if a.get("humeur")]
        if humeurs:
            humeur_dominante = max(set(humeurs), key=humeurs.count)
            humeur_emoji = {"content": "😊", "neutre": "😐", "grognon": "😤", "fatigue": "😴"}.get(
                humeur_dominante, "😊"
            )
            if use_emoji:
                lines.append(f"💚 *Humeur dominante:* {humeur_emoji} {humeur_dominante}")
            else:
                lines.append(f"Humeur: {humeur_dominante}")

    # Footer
    lines.append("")
    if use_emoji:
        lines.append("❤️ _Généré par Assistant Matanne_")

    return "\n".join(lines)


def _get_activite_icone(type_activite: str | None) -> str:
    """Retourne l'icône pour un type d'activité."""
    icones = {
        "motricite": "🏃",
        "eveil": "🧠",
        "jeu": "🎮",
        "lecture": "📚",
        "musique": "🎵",
        "sortie": "🌳",
        "bain": "🛁",
        "repas": "🍽️",
        "sieste": "😴",
        "change": "👶",
        "autre": "📝",
    }
    return icones.get((type_activite or "").lower(), "📝")


# ═══════════════════════════════════════════════════════════
# COMPOSANTS UI
# ═══════════════════════════════════════════════════════════


@composant_ui("jules", tags=("ui", "widget", "enfant"))
def widget_jules_aujourdhui(afficher_export: bool = True) -> None:
    """
    Widget complet "Ce que Jules a fait aujourd'hui".

    Args:
        afficher_export: Si True, affiche les boutons d'export
    """
    st.markdown("### 👶 Ce que Jules a fait aujourd'hui")

    # Charger données
    activites = obtenir_activites_jules_aujourdhui()
    repas = obtenir_repas_jules_aujourdhui()
    siestes = obtenir_siestes_jules_aujourdhui()

    # Stats rapides
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("🎯 Activités", len(activites))
    with col2:
        st.metric("🍽️ Repas", len(repas))
    with col3:
        total_sieste = sum(s.get("duree", 0) or 0 for s in siestes)
        st.metric("😴 Sieste", f"{total_sieste} min")

    if not activites and not repas and not siestes:
        st.info(
            "Aucune donnée enregistrée pour aujourd'hui. Commencez à tracer la journée de Jules!"
        )
        if st.button("➕ Ajouter une activité", key=_keys("ajouter")):
            naviguer("famille.jules")
        return

    # Timeline des activités
    if activites:
        st.markdown("#### 🎯 Activités")
        for a in activites:
            heure = a.get("heure", "")
            icone = a.get("icone", "📝")
            humeur_badge = ""
            if a.get("humeur"):
                humeur_emoji = {
                    "content": "😊",
                    "neutre": "😐",
                    "grognon": "😤",
                    "fatigue": "😴",
                }.get(a["humeur"], "")
                humeur_badge = f" {humeur_emoji}"

            st.markdown(
                f"""<div style="padding: 8px; margin: 4px 0; background: {Sem.SURFACE_ALT};
                border-radius: 8px; border-left: 4px solid {Sem.INTERACTIVE};">
                    <strong>{heure}</strong> {icone} {a["titre"]}{humeur_badge}
                    {f"<br><small style='color: {Sem.ON_SURFACE_SECONDARY};'>{a['notes']}</small>" if a.get("notes") else ""}
                </div>""",
                unsafe_allow_html=True,
            )

    # Section export
    if afficher_export:
        st.divider()
        st.markdown("#### 📤 Partager")

        # Générer le résumé
        resume = generer_resume_jules(activites, repas, siestes, format_export="whatsapp")

        # Afficher preview dans expander
        with st.expander("👁️ Aperçu du message"):
            st.text(resume)

        # Boutons export
        col1, col2, col3 = st.columns(3)

        with col1:
            # Copier dans le presse-papier (via JS)
            if st.button("📋 Copier", key=_keys("copier")):
                st.session_state[_keys("resume_copie")] = resume
                st.success("Copié! Collez dans votre app de messagerie.")

        with col2:
            # Lien WhatsApp
            import urllib.parse

            resume_encoded = urllib.parse.quote(resume)
            whatsapp_url = f"https://wa.me/?text={resume_encoded}"
            st.link_button("💬 WhatsApp", whatsapp_url)

        with col3:
            # Télécharger en fichier
            st.download_button(
                "💾 Télécharger",
                data=resume,
                file_name=f"jules_{date.today().strftime('%Y%m%d')}.txt",
                mime="text/plain",
                key=_keys("download"),
            )


@composant_ui("jules", tags=("ui", "widget", "compact"))
def widget_jules_resume_compact() -> None:
    """Version compacte du résumé Jules pour sidebar ou accueil."""
    activites = obtenir_activites_jules_aujourdhui()

    if activites:
        derniere = activites[-1]
        st.markdown(
            f"**👶 Jules:** {derniere['icone']} {derniere['titre']} "
            f"<small style='color: {Sem.ON_SURFACE_SECONDARY};'>({derniere.get('heure', '?')})</small>",
            unsafe_allow_html=True,
        )
    else:
        st.caption("👶 Pas d'activité Jules enregistrée")


@composant_ui("jules", tags=("ui", "carte", "dashboard"))
def carte_resume_jules() -> None:
    """Carte résumé pour le dashboard accueil."""
    activites = obtenir_activites_jules_aujourdhui()
    siestes = obtenir_siestes_jules_aujourdhui()

    total_activites = len(activites)
    total_sieste = sum(s.get("duree", 0) or 0 for s in siestes)

    # Déterminer l'humeur dominante
    humeur = "😊"
    if activites:
        humeurs = [a["humeur"] for a in activites if a.get("humeur")]
        if humeurs:
            humeur_dominante = max(set(humeurs), key=humeurs.count)
            humeur = {"content": "😊", "neutre": "😐", "grognon": "😤", "fatigue": "😴"}.get(
                humeur_dominante, "😊"
            )

    st.markdown(
        f"""
        <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            border-radius: 12px; padding: 16px; color: white; text-align: center;">
            <div style="font-size: 2rem;">{humeur}</div>
            <div style="font-weight: 600; margin: 8px 0;">Jules aujourd'hui</div>
            <div style="font-size: 0.9rem;">
                {total_activites} activités • {total_sieste} min de sieste
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button("📝 Voir le détail", key=_keys("voir_detail")):
        naviguer("famille.jules")


__all__ = [
    "widget_jules_aujourdhui",
    "widget_jules_resume_compact",
    "carte_resume_jules",
    "obtenir_activites_jules_aujourdhui",
    "generer_resume_jules",
]
