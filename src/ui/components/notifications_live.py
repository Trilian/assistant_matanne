"""
Widget Notifications Temps Réel — Auto-refresh via @st.fragment(run_every).

Fragment isolé qui se rafraîchit automatiquement toutes les 30 secondes
sans rerun de la page entière. Affiche les alertes inventaire,
tâches en retard, et produits proches de la péremption.

Usage (dans app.py ou n'importe quel module):
    from src.ui.components.notifications_live import widget_notifications_live
    widget_notifications_live()
"""

import logging
from datetime import datetime, timedelta
from typing import Any

import streamlit as st

from src.ui.fragments import auto_refresh
from src.ui.keys import KeyNamespace

logger = logging.getLogger(__name__)

_keys = KeyNamespace("notif_live")


# ═══════════════════════════════════════════════════════════
# COLLECTEUR D'ALERTES
# ═══════════════════════════════════════════════════════════


def _collecter_alertes() -> list[dict[str, Any]]:
    """Collecte toutes les alertes actives depuis les services.

    Returns:
        Liste de notifications triées par priorité.
    """
    alertes: list[dict[str, Any]] = []

    # 1. Alertes inventaire (stock bas, péremption)
    try:
        from src.services.core.notifications import (
            obtenir_service_notifications_inventaire,
        )

        service = obtenir_service_notifications_inventaire()
        if service:
            notifs = getattr(service, "notifications", {})
            for _user_id, user_notifs in notifs.items():
                for notif in user_notifs:
                    alertes.append(
                        {
                            "type": "inventaire",
                            "priorite": getattr(notif, "priorite", "normale"),
                            "titre": getattr(notif, "titre", "Alerte inventaire"),
                            "message": getattr(notif, "message", ""),
                            "icone": getattr(notif, "icone", "📦"),
                            "lue": getattr(notif, "lue", False),
                        }
                    )
    except Exception as e:
        logger.debug(f"Alertes inventaire indisponibles: {e}")

    # 2. Tâches entretien en retard
    try:
        from src.core.db import obtenir_contexte_db
        from src.core.models.habitat import TacheEntretien

        with obtenir_contexte_db() as session:
            taches_retard = (
                session.query(TacheEntretien)
                .filter(
                    TacheEntretien.prochaine_fois < datetime.now().date(),
                    TacheEntretien.fait.is_(False),
                )
                .limit(5)
                .all()
            )

            for tache in taches_retard:
                alertes.append(
                    {
                        "type": "entretien",
                        "priorite": "haute",
                        "titre": f"🏠 Retard: {tache.nom}",
                        "message": (
                            f"Prévu le {tache.prochaine_fois.strftime('%d/%m')}"
                            if tache.prochaine_fois
                            else "Aucune date"
                        ),
                        "icone": "🏠",
                        "lue": False,
                    }
                )
    except Exception as e:
        logger.debug(f"Tâches entretien indisponibles: {e}")

    # 3. Produits proches de la péremption
    try:
        from src.core.db import obtenir_contexte_db
        from src.core.models.inventaire import ArticleInventaire

        seuil = datetime.now().date() + timedelta(days=3)

        with obtenir_contexte_db() as session:
            proches_peremption = (
                session.query(ArticleInventaire)
                .filter(
                    ArticleInventaire.date_peremption <= seuil,
                    ArticleInventaire.date_peremption >= datetime.now().date(),
                    ArticleInventaire.quantite > 0,
                )
                .limit(5)
                .all()
            )

            for article in proches_peremption:
                if article.date_peremption is None:
                    continue
                jours = (article.date_peremption - datetime.now().date()).days
                nom = article.ingredient.nom if article.ingredient else f"Article #{article.id}"
                alertes.append(
                    {
                        "type": "peremption",
                        "priorite": "haute" if jours <= 1 else "moyenne",
                        "titre": f"⏰ {nom} expire dans {jours}j",
                        "message": f"Péremption: {article.date_peremption.strftime('%d/%m')}",
                        "icone": "⏰",
                        "lue": False,
                    }
                )
    except Exception as e:
        logger.debug(f"Alertes péremption indisponibles: {e}")

    # Trier par priorité : critique > haute > moyenne > normale > basse
    ordre_priorite = {"critique": 0, "haute": 1, "moyenne": 2, "normale": 3, "basse": 4}
    alertes.sort(key=lambda a: ordre_priorite.get(a["priorite"], 3))

    return alertes


# ═══════════════════════════════════════════════════════════
# COULEURS PAR PRIORITÉ
# ═══════════════════════════════════════════════════════════

_COULEURS_PRIORITE = {
    "critique": "#d32f2f",
    "haute": "#f57c00",
    "moyenne": "#fbc02d",
    "normale": "#1976d2",
    "basse": "#757575",
}


# ═══════════════════════════════════════════════════════════
# WIDGET NOTIFICATIONS TEMPS RÉEL
# ═══════════════════════════════════════════════════════════


@auto_refresh(seconds=30)
def widget_notifications_live(max_alertes: int = 5) -> None:
    """Widget de notifications temps réel avec auto-refresh.

    Se rafraîchit toutes les 30 secondes sans rerun de la page.
    Affiche les alertes critiques dans un popover compact.

    Args:
        max_alertes: Nombre maximum d'alertes à afficher.
    """
    alertes = _collecter_alertes()

    if not alertes:
        return  # Rien à afficher

    non_lues = [a for a in alertes if not a.get("lue", False)]
    nb_non_lues = len(non_lues)

    # Badge avec nombre
    label = f"🔔 {nb_non_lues} alerte{'s' if nb_non_lues != 1 else ''}"

    with st.popover(label, use_container_width=False):
        st.markdown("**🔔 Alertes en temps réel**")
        st.caption(f"Dernière vérification: {datetime.now().strftime('%H:%M:%S')}")

        # Limiter le nombre affiché
        alertes_affichees = alertes[:max_alertes]

        if not alertes_affichees:
            st.success("✅ Aucune alerte active")
            return

        for alerte in alertes_affichees:
            couleur = _COULEURS_PRIORITE.get(alerte["priorite"], "#757575")

            st.markdown(
                f'<div style="padding:6px 10px;margin:4px 0;'
                f"border-left:3px solid {couleur};"
                f'border-radius:4px;background:var(--st-surface-alt,#fafafa);">'
                f"<strong>{alerte['icone']} {alerte['titre']}</strong><br>"
                f'<span style="font-size:0.85rem;color:var(--st-on-surface-secondary,#666);">'
                f"{alerte['message']}</span></div>",
                unsafe_allow_html=True,
            )

        if len(alertes) > max_alertes:
            st.caption(f"... et {len(alertes) - max_alertes} autres alertes")

        # Bouton pour voir toutes les notifications
        if st.button("📋 Voir tout", key=_keys("voir_tout"), use_container_width=True):
            from src.core.state import GestionnaireEtat

            GestionnaireEtat.naviguer_vers("notifications_push")
            st.rerun()


__all__ = ["widget_notifications_live"]
