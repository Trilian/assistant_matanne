"""
Widget conseil Jules IA du jour.

Affiche une suggestion d'activité ou un conseil de développement
adapté à l'âge de Jules et à la météo du jour.
Utilise JulesAIService avec cache quotidien.
"""

import logging
from datetime import date

import streamlit as st

from src.ui.engine import StyleSheet
from src.ui.fragments import cached_fragment
from src.ui.keys import KeyNamespace
from src.ui.tokens import Couleur, Espacement, Rayon
from src.ui.tokens_semantic import Sem

logger = logging.getLogger(__name__)

_keys = KeyNamespace("conseil_jules")


# ═══════════════════════════════════════════════════════════
# DONNÉES
# ═══════════════════════════════════════════════════════════


def _obtenir_age_mois() -> int:
    """Retourne l'âge de Jules en mois."""
    try:
        from src.core.constants import JULES_NAISSANCE

        return (date.today() - JULES_NAISSANCE).days // 30
    except Exception:
        return 20  # Fallback


def _obtenir_contexte_meteo() -> str:
    """Retourne le contexte météo pour adapter les activités."""
    try:
        from src.services.integrations.weather import obtenir_service_meteo

        previsions = obtenir_service_meteo().get_previsions(nb_jours=1)
        if previsions:
            meteo = previsions[0]
            if meteo.precipitation_mm > 5 or meteo.probabilite_pluie > 60:
                return "intérieur (pluie prévue)"
            if meteo.temperature_max > 30:
                return "intérieur ou ombre (fortes chaleurs)"
            if meteo.temperature_min < 5:
                return "intérieur (froid)"
            return "extérieur ou intérieur (beau temps)"
    except Exception:
        pass
    return "intérieur"


def _generer_conseil_local(age_mois: int) -> dict:
    """Génère un conseil local sans IA (fallback rapide).

    Returns:
        Dict {activite, benefice, astuce}.
    """
    # Conseils par tranche d'âge
    if age_mois <= 18:
        conseils = [
            {
                "activite": "🎨 Peinture avec les doigts",
                "benefice": "Motricité fine et créativité",
                "astuce": "Utilisez des colorants alimentaires pour plus de sécurité",
            },
            {
                "activite": "📚 Lecture interactive",
                "benefice": "Langage et vocabulaire",
                "astuce": "Laissez Jules tourner les pages et pointer les images",
            },
            {
                "activite": "🧱 Tour de cubes",
                "benefice": "Coordination et logique",
                "astuce": "Comptez ensemble en empilant les cubes",
            },
        ]
    elif age_mois <= 22:
        conseils = [
            {
                "activite": "🎶 Musique et danse",
                "benefice": "Rythme et expression corporelle",
                "astuce": "Utilisez des ustensiles de cuisine comme instruments",
            },
            {
                "activite": "🫧 Jeu avec l'eau",
                "benefice": "Motricité et découverte sensorielle",
                "astuce": "Transvasement avec gobelets dans la baignoire",
            },
            {
                "activite": "🧩 Puzzle simple (2-4 pièces)",
                "benefice": "Résolution de problèmes",
                "astuce": "Commencez par montrer puis laissez-le essayer",
            },
            {
                "activite": "🏃 Parcours moteur",
                "benefice": "Motricité globale et équilibre",
                "astuce": "Coussins au sol pour ramper, enjamber, grimper",
            },
        ]
    else:
        conseils = [
            {
                "activite": "🎭 Jeu d'imitation",
                "benefice": "Développement social et imagination",
                "astuce": "Cuisiner ensemble avec des ustensiles jouets",
            },
            {
                "activite": "✏️ Dessin et gribouillage",
                "benefice": "Pré-écriture et créativité",
                "astuce": "Gros crayons de cire, adaptés aux petites mains",
            },
            {
                "activite": "🌿 Exploration nature",
                "benefice": "Éveil sensoriel et vocabulaire",
                "astuce": "Nommez les plantes, textures et couleurs ensemble",
            },
            {
                "activite": "🧸 Jeu de rôle",
                "benefice": "Langage et compréhension sociale",
                "astuce": "Faites parler les peluches, créez des scénarios simples",
            },
        ]

    # Choisir un conseil basé sur le jour (un par jour)
    import random

    rng = random.Random(date.today().toordinal())
    return rng.choice(conseils)


# ═══════════════════════════════════════════════════════════
# WIDGET UI
# ═══════════════════════════════════════════════════════════


@cached_fragment(ttl=3600)  # Cache 1h
def afficher_conseil_jules():
    """Affiche le conseil Jules du jour."""
    age_mois = _obtenir_age_mois()
    contexte_meteo = _obtenir_contexte_meteo()

    container_cls = StyleSheet.create_class(
        {
            "background": f"linear-gradient(135deg, {Couleur.BG_JULES_START}, {Couleur.BG_JULES_END})",
            "border-radius": Rayon.XL,
            "padding": Espacement.LG,
            "border-left": f"4px solid {Couleur.JULES_PRIMARY}",
            "margin-bottom": Espacement.MD,
        }
    )

    StyleSheet.inject()

    st.markdown(f'<div class="{container_cls}">', unsafe_allow_html=True)

    col_titre, col_age = st.columns([3, 1])

    with col_titre:
        st.markdown("### 🧒 Conseil Jules du jour")

    with col_age:
        st.markdown(
            f'<p style="text-align:right;color:{Couleur.JULES_PRIMARY};'
            f'font-weight:600;">{age_mois} mois</p>',
            unsafe_allow_html=True,
        )

    # Conseil local (toujours disponible, rapide)
    conseil = _generer_conseil_local(age_mois)

    st.markdown(f"**{conseil['activite']}**")
    st.markdown(f"🎯 *{conseil['benefice']}*")
    st.caption(f"💡 Astuce : {conseil['astuce']}")

    # Option IA pour plus de détails
    col_ia, col_nav = st.columns(2)

    with col_ia:
        if st.button(
            "✨ Idées IA", key=_keys("suggestion_ia"), help="Suggestions personnalisées par l'IA"
        ):
            with st.spinner("✨ L'IA réfléchit..."):
                try:
                    from src.services.famille.jules_ai import obtenir_jules_ai_service

                    service = obtenir_jules_ai_service()
                    # Utiliser la version streaming
                    stream = service.stream_activites(
                        age_mois=age_mois,
                        meteo=contexte_meteo,
                        nb=2,
                    )
                    st.write_stream(stream)
                except Exception as e:
                    logger.debug(f"IA Jules indisponible: {e}")
                    st.info("✨ Service IA temporairement indisponible")

    with col_nav:
        if st.button("👶 Voir tout", key=_keys("nav_jules")):
            from src.core.state import naviguer

            naviguer("famille.jules")

    st.markdown("</div>", unsafe_allow_html=True)


__all__ = ["afficher_conseil_jules"]
