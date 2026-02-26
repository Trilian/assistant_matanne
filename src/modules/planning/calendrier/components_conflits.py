"""
Composants Calendrier - Affichage des conflits

Composants UI pour l'affichage des alertes de conflits
détectés dans le planning hebdomadaire.
"""

import logging
from datetime import date

import streamlit as st

from src.ui.keys import KeyNamespace

logger = logging.getLogger(__name__)

_keys = KeyNamespace("conflits_cal")


def afficher_alertes_conflits(date_debut: date):
    """Affiche les alertes de conflits pour la semaine courante.

    Interroge le ServiceConflits et affiche un résumé + détails.

    Args:
        date_debut: Date de début de semaine (lundi).
    """
    try:
        from src.services.planning.conflits import obtenir_service_conflits

        service = obtenir_service_conflits()
        rapport = service.detecter_conflits_semaine(date_debut)

        if not rapport.conflits:
            return  # Pas d'affichage si aucun conflit

        # Résumé compact
        with st.expander(
            f"⚠️ {len(rapport.conflits)} alerte(s) — {rapport.resume}",
            expanded=rapport.a_conflits_critiques,
        ):
            # Métriques
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("🔴 Critiques", rapport.nb_erreurs)
            with col2:
                st.metric("🟡 Avertissements", rapport.nb_avertissements)
            with col3:
                st.metric("🔵 Infos", rapport.nb_infos)

            st.divider()

            # Détails des conflits
            for conflit in rapport.conflits:
                _afficher_conflit(conflit)

    except Exception as e:
        logger.warning(f"Impossible de charger les conflits: {e}")


def _afficher_conflit(conflit):
    """Affiche un conflit individuel."""
    from src.services.planning.conflits import NiveauConflit

    # Sélectionner le composant Streamlit selon le niveau
    if conflit.niveau == NiveauConflit.ERREUR:
        container = st.error
    elif conflit.niveau == NiveauConflit.AVERTISSEMENT:
        container = st.warning
    else:
        container = st.info

    # Message principal
    message = f"{conflit.emoji} **{conflit.date_jour.strftime('%a %d/%m')}** — {conflit.message}"

    if conflit.suggestion:
        message += f"\n\n💡 *{conflit.suggestion}*"

    container(message)


def afficher_verification_conflit_formulaire(
    date_jour: date,
    heure_debut: str | None = None,
    heure_fin: str | None = None,
    titre: str = "Nouvel événement",
):
    """Vérifie les conflits pour un nouvel événement (dans un formulaire).

    Affiche un avertissement inline si le nouvel événement
    entre en conflit avec des événements existants.

    Args:
        date_jour: Date de l'événement.
        heure_debut: Heure de début (format HH:MM).
        heure_fin: Heure de fin (format HH:MM).
        titre: Titre de l'événement.
    """
    if not heure_debut:
        return

    try:
        from src.services.planning.conflits import obtenir_service_conflits

        service = obtenir_service_conflits()
        conflits = service.verifier_nouvel_evenement(
            date_jour=date_jour,
            heure_debut=heure_debut,
            heure_fin=heure_fin,
            titre=titre,
        )

        if conflits:
            for c in conflits:
                if c.niveau.value == "erreur":
                    st.error(f"{c.emoji} {c.message}")
                elif c.niveau.value == "avertissement":
                    st.warning(f"{c.emoji} {c.message}")
                else:
                    st.info(f"{c.emoji} {c.message}")

    except Exception as e:
        logger.debug(f"Vérification conflit impossible: {e}")


__all__ = [
    "afficher_alertes_conflits",
    "afficher_verification_conflit_formulaire",
]
