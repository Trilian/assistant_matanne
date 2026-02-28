"""
Widget résumé maison / entretien pour le dashboard.

Affiche un aperçu compact de l'état de la maison:
- Tâches en retard
- Prochaine tâche planifiée
- Score "état de la maison"
"""

import logging

import streamlit as st

from src.ui.engine import StyleSheet
from src.ui.fragments import cached_fragment
from src.ui.keys import KeyNamespace
from src.ui.tokens import Couleur, Espacement, Rayon
from src.ui.tokens_semantic import Sem

logger = logging.getLogger(__name__)

_keys = KeyNamespace("resume_maison")


def _obtenir_donnees_maison() -> dict:
    """Collecte les données maison/entretien.

    Returns:
        Dict avec taches_retard, prochaine_tache, score.
    """
    donnees = {
        "taches_retard": [],
        "nb_retard": 0,
        "prochaine_tache": None,
        "score_maison": 100,
    }

    # Tâches en retard
    try:
        from src.services.accueil_data_service import get_accueil_data_service

        taches = get_accueil_data_service().get_taches_en_retard(limit=10)
        if taches:
            donnees["taches_retard"] = taches[:5]
            donnees["nb_retard"] = len(taches)

            # Score: pénalité par tâche en retard
            penalite = min(len(taches) * 10, 80)
            donnees["score_maison"] = max(20, 100 - penalite)
    except Exception:
        pass

    # Stats maison
    try:
        from src.services.maison.hub_data_service import get_hub_data_service

        hub = get_hub_data_service()
        stats = hub.get_all_stats()
        if stats:
            donnees["stats_maison"] = stats
    except Exception:
        pass

    return donnees


# ═══════════════════════════════════════════════════════════
# WIDGET UI
# ═══════════════════════════════════════════════════════════


@cached_fragment(ttl=300)  # Cache 5 min
def afficher_widget_maison():
    """Affiche le widget résumé maison/entretien."""
    donnees = _obtenir_donnees_maison()

    container_cls = StyleSheet.create_class(
        {
            "background": "linear-gradient(135deg, #EFEBE9, #D7CCC8)",
            "border-radius": Rayon.XL,
            "padding": Espacement.LG,
            "border-left": f"4px solid {Couleur.WARNING}",
            "margin-bottom": Espacement.MD,
        }
    )

    StyleSheet.inject()

    st.markdown(f'<div class="{container_cls}">', unsafe_allow_html=True)

    col_titre, col_score = st.columns([4, 1])

    with col_titre:
        st.markdown("### 🏠 Maison")

    with col_score:
        score = donnees["score_maison"]
        couleur_score = (
            Couleur.SUCCESS
            if score >= 80
            else (Couleur.WARNING if score >= 50 else Couleur.RED_500)
        )
        emoji_score = "✨" if score >= 80 else ("👍" if score >= 50 else "⚠️")
        st.markdown(
            f'<p style="text-align:right;font-size:1.5rem;font-weight:700; '
            f'color:{couleur_score}; white-space:nowrap; margin:0;">{emoji_score} {score}%</p>',
            unsafe_allow_html=True,
        )

    # Tâches en retard
    if donnees["nb_retard"] > 0:
        st.warning(f"🧹 **{donnees['nb_retard']}** tâche(s) en retard")

        for t in donnees["taches_retard"][:3]:
            jours = t.get("jours_retard", 0)
            couleur = Couleur.RED_500 if jours > 7 else Couleur.ORANGE
            st.markdown(
                f'<div style="padding:3px 8px;margin:2px 0;'
                f"border-left:3px solid {couleur};border-radius:3px;"
                f'background:{Sem.SURFACE_ALT};">'
                f"<small>🧹 {t['nom']} — <strong>{jours}j</strong> de retard</small>"
                f"</div>",
                unsafe_allow_html=True,
            )
    else:
        st.success("✅ Tout est à jour !")

    # Navigation
    if st.button("🏠 Voir maison", key=_keys("nav_maison")):
        from src.core.state import naviguer

        naviguer("maison.entretien")

    st.markdown("</div>", unsafe_allow_html=True)


__all__ = ["afficher_widget_maison"]
