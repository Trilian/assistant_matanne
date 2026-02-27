"""
Module Jardin Zones - Dashboard des zones du jardin.

Fonctionnalités:
- Vue d'ensemble des zones du jardin avec notes d'état
- Gestion des photos avant/après
- Conseils d'amélioration par zone
- Cartes de zone avec progression visuelle
"""

import logging
from typing import TYPE_CHECKING

import plotly.graph_objects as go
import streamlit as st

from src.core.monitoring.rerun_profiler import profiler_rerun
from src.modules._framework import error_boundary
from src.ui.fragments import cached_fragment
from src.ui.keys import KeyNamespace
from src.ui.state.url import tabs_with_url
from src.ui.tokens import Couleur

if TYPE_CHECKING:
    from src.services.maison.jardin_service import JardinService

__all__ = [
    "app",
    "EMOJI_ZONE",
    "COULEUR_ETAT",
    "LABEL_ETAT",
    "charger_zones",
    "mettre_a_jour_zone",
    "ajouter_photo_zone",
    "afficher_carte_zone",
    "afficher_vue_ensemble",
    "afficher_detail_zone",
    "afficher_conseils_amelioration",
]

_keys = KeyNamespace("jardin_zones")
logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# SERVICE LOADER
# ═══════════════════════════════════════════════════════════


def _get_service() -> "JardinService":
    """Charge paresseusement le service jardin."""
    from src.services.maison.jardin_service import get_jardin_service

    return get_jardin_service()


def creer_zone(nom: str, type_zone: str = "autre", superficie: float | None = None) -> bool:
    """Wrapper UI: crée une zone via le service et invalide le cache."""
    try:
        res = _get_service().ajouter_zone(nom=nom, type_zone=type_zone, superficie_m2=superficie)
        if res:
            charger_zones.clear()
            return True
        return False
    except Exception as e:
        logger.error(f"Erreur creer_zone UI: {e}")
        return False


# ═══════════════════════════════════════════════════════════
# CONSTANTES
# ═══════════════════════════════════════════════════════════

EMOJI_ZONE = {
    "pelouse": "🌿",
    "potager": "🥕",
    "arbres": "🌳",
    "piscine": "🏊",
    "terrasse": "🪑",
    "compost": "♻️",
}

COULEUR_ETAT = {
    1: Couleur.SCALE_CRITICAL,
    2: Couleur.SCALE_BAD,
    3: Couleur.SCALE_OK,
    4: Couleur.SCALE_GOOD,
    5: Couleur.SCALE_EXCELLENT,
}

LABEL_ETAT = {
    1: "Critique",
    2: "Mauvais",
    3: "Correct",
    4: "Bon",
    5: "Excellent",
}


# ═══════════════════════════════════════════════════════════
# DATA
# ═══════════════════════════════════════════════════════════


@st.cache_data(ttl=300)
def charger_zones() -> list:
    """Charge toutes les zones du jardin depuis la DB.

    Returns:
        Liste de dicts avec: id, nom, type_zone, etat_note, superficie,
        commentaire, photos.
    """
    return _get_service().charger_zones()


def mettre_a_jour_zone(zone_id: int, updates: dict, db=None) -> bool:
    """Met à jour une zone du jardin.

    Args:
        zone_id: ID de la zone.
        updates: Dict des champs à mettre à jour.
        db: Session DB optionnelle (ignorée, conservée pour rétrocompatibilité).

    Returns:
        True si la mise à jour a réussi.
    """
    result = _get_service().mettre_a_jour_zone(zone_id, updates)
    if result:
        charger_zones.clear()
    return result


def ajouter_photo_zone(zone_id: int, url: str, est_avant: bool = True, db=None) -> bool:
    """Ajoute une photo à une zone.

    Args:
        zone_id: ID de la zone.
        url: URL de la photo.
        est_avant: True pour photo 'avant', False pour 'après'.
        db: Session DB optionnelle (ignorée, conservée pour rétrocompatibilité).

    Returns:
        True si l'ajout a réussi.
    """
    result = _get_service().ajouter_photo_zone(zone_id, url, est_avant)
    if result:
        charger_zones.clear()
    return result


# ═══════════════════════════════════════════════════════════
# UI COMPONENTS
# ═══════════════════════════════════════════════════════════


def afficher_carte_zone(zone: dict) -> None:
    """Affiche une carte pour une zone du jardin."""
    note = zone.get("etat_note", 3)
    couleur = COULEUR_ETAT.get(note, "#757575")
    label = LABEL_ETAT.get(note, "Inconnu")
    emoji = EMOJI_ZONE.get(zone.get("type_zone", ""), "🌍")

    with st.container(border=True):
        cols = st.columns([2, 1])
        with cols[0]:
            st.markdown(f"**{emoji} {zone.get('nom', '')}**")
            st.caption(f"État: {label} ({note}/5)")
            if zone.get("etat_description"):
                st.caption(zone["etat_description"])
            if zone.get("prochaine_action"):
                st.caption(f"Prochaine action: {zone['prochaine_action']}")
        with cols[1]:
            st.metric("Superficie", f"{zone.get('surface_m2', 0)} m²")

        st.progress(note / 5)

        photos = zone.get("photos_url", [])
        if photos:
            st.caption(f"📸 {len(photos)} photo(s)")


@cached_fragment(ttl=300)
def afficher_vue_ensemble() -> None:
    """Affiche la vue d'ensemble des zones."""
    zones = charger_zones()

    if not zones:
        st.warning("Aucune zone enregistrée.")
        return

    # Métriques globales
    note_moy = sum(z.get("etat_note", 3) for z in zones) / len(zones)
    surface_totale = sum(z.get("surface_m2", 0) for z in zones)

    cols = st.columns(3)
    with cols[0]:
        st.metric("Zones", len(zones))
    with cols[1]:
        st.metric("Note moyenne", f"{note_moy:.1f}/5")
    with cols[2]:
        st.metric("Surface totale", f"{surface_totale} m²")

    # Zones critiques
    critiques = [z for z in zones if z.get("etat_note", 3) <= 1]
    for z in critiques:
        st.error(f"⚠️ {z['nom']} est en état critique !")

    # Graphique
    noms = [z.get("nom", "") for z in zones]
    notes = [z.get("etat_note", 3) for z in zones]
    couleurs = [COULEUR_ETAT.get(n, "#757575") for n in notes]

    fig = go.Figure(
        data=[go.Bar(x=noms, y=notes, marker_color=couleurs)],
    )
    fig.update_layout(title="État des zones", yaxis_range=[0, 5])
    st.plotly_chart(fig, use_container_width=True)


def afficher_detail_zone(zone: dict) -> None:
    """Affiche le détail d'une zone."""
    emoji = EMOJI_ZONE.get(zone.get("type_zone", ""), "🌍")
    st.markdown(f"### {emoji} {zone.get('nom', '')}")

    note = zone.get("etat_note", 3)
    label = LABEL_ETAT.get(note, "Inconnu")
    couleur = COULEUR_ETAT.get(note, "#757575")

    st.progress(note / 5)
    st.caption(f"État: {label} • Superficie: {zone.get('surface_m2', 0)} m²")

    if zone.get("etat_description"):
        st.markdown(zone["etat_description"])

    if zone.get("prochaine_action"):
        st.info(f"Prochaine action: {zone['prochaine_action']}")

    photos = zone.get("photos_url", [])
    if photos:
        avant = [p.replace("avant:", "") for p in photos if p.startswith("avant:")]
        apres = [p.replace("apres:", "") for p in photos if p.startswith("apres:")]
        tab_avant, tab_apres = st.tabs(["📸 Avant", "📸 Après"])
        with tab_avant:
            for p in avant:
                st.image(p)
        with tab_apres:
            for p in apres:
                st.image(p)


def afficher_conseils_amelioration() -> None:
    """Affiche les conseils d'amélioration pour le jardin."""
    st.markdown("### 💡 Conseils d'amélioration")

    conseils = {
        "pelouse": "Tondre régulièrement, arroser le matin, scarifier au printemps.",
        "potager": "Rotation des cultures, paillage, compost maison.",
        "arbres": "Élaguer en hiver, surveiller les parasites, mulcher.",
        "piscine": "Contrôler le pH, nettoyer les filtres, hiverner correctement.",
        "terrasse": "Nettoyer au Kärcher, traiter le bois, vérifier les joints.",
        "compost": "Équilibrer vert/brun, aérer, maintenir l'humidité.",
    }

    st.info("Astuce: Un entretien régulier permet de maintenir toutes les zones en bon état.")

    for zone_type, conseil in conseils.items():
        emoji = EMOJI_ZONE.get(zone_type, "🌍")
        with st.expander(f"{emoji} {zone_type.capitalize()}"):
            st.markdown(conseil)


# ═══════════════════════════════════════════════════════════
# APP
# ═══════════════════════════════════════════════════════════


@profiler_rerun("jardin_zones")
def app():
    """Point d'entrée du module Jardin Zones."""
    with error_boundary(titre="Erreur module Jardin Zones"):
        st.title("🌳 Jardin - Dashboard Zones")
        st.caption("Vue d'ensemble et gestion des zones de votre jardin.")

        zones = charger_zones()

        # Onglets
        TAB_LABELS = ["🗺️ Vue d'ensemble", "📋 Détail", "💡 Conseils"]
        tab_index = tabs_with_url(TAB_LABELS, param="tab")
        tab1, tab2, tab3 = st.tabs(TAB_LABELS)

        with tab1:
            afficher_vue_ensemble()
            st.divider()

            # Formulaire rapide pour ajouter une zone
            with st.expander("➕ Ajouter une zone", expanded=False):
                col1, col2 = st.columns([3, 1])
                with col1:
                    nom_zone = st.text_input("Nom de la zone", key=_keys("new_zone_nom"))
                    type_zone = st.selectbox(
                        "Type de zone",
                        list(EMOJI_ZONE.keys()),
                        format_func=lambda k: f"{EMOJI_ZONE.get(k, '')} {k.capitalize()}",
                        key=_keys("new_zone_type"),
                    )
                with col2:
                    superficie = st.number_input(
                        "Surface (m²)", min_value=0.0, value=0.0, key=_keys("new_zone_surface")
                    )
                if st.button("Créer la zone", key=_keys("create_zone")):
                    if nom_zone:
                        ok = creer_zone(nom_zone, type_zone, superficie or None)
                        if ok:
                            st.success("Zone créée")
                            st.experimental_rerun()
                        else:
                            st.error("Échec création zone")

            if zones:
                st.divider()
                for z in zones:
                    afficher_carte_zone(z)

        with tab2:
            if zones:
                noms = [z.get("nom", f"Zone {i}") for i, z in enumerate(zones)]
                selection = st.selectbox(
                    "Choisir une zone",
                    noms,
                )
                zone_selectionnee = next((z for z in zones if z.get("nom") == selection), zones[0])
                afficher_detail_zone(zone_selectionnee)
            else:
                st.info("Aucune zone à afficher.")

        with tab3:
            afficher_conseils_amelioration()
