"""
Dashboard - Alertes critiques
Affichage des alertes pour le tableau de bord principal
"""

from datetime import date

import streamlit as st

from src.ui.keys import KeyNamespace

_keys = KeyNamespace("accueil")


def afficher_critical_alerts():
    """Affiche les alertes importantes"""
    from src.core.state import GestionnaireEtat
    from src.services.cuisine.planning import obtenir_service_planning
    from src.services.inventaire import obtenir_service_inventaire

    alerts = []

    # Inventaire critique
    inventaire = obtenir_service_inventaire().get_inventaire_complet()
    critiques = [art for art in inventaire if art.get("statut") in ["critique", "sous_seuil"]]

    if critiques:
        alerts.append(
            {
                "type": "warning",
                "icon": "⚠️",
                "title": f"{len(critiques)} article(s) en stock bas",
                "action": "Voir l'inventaire",
                "module": "cuisine.inventaire",
            }
        )

    # Peremption proche
    peremption = [art for art in inventaire if art.get("statut") == "peremption_proche"]

    if peremption:
        alerts.append(
            {
                "type": "warning",
                "icon": "⏳",
                "title": f"{len(peremption)} article(s) periment bientôt",
                "action": "Voir l'inventaire",
                "module": "cuisine.inventaire",
            }
        )

    # Planning vide
    planning = obtenir_service_planning().get_planning()

    if not planning or not planning.repas:
        alerts.append(
            {
                "type": "info",
                "icon": "📅",
                "title": "Aucun planning pour cette semaine",
                "action": "Creer un planning",
                "module": "cuisine.planning_semaine",
            }
        )

    # Tâches menage en retard
    try:
        from src.core.db import obtenir_contexte_db
        from src.core.models import MaintenanceTask

        with obtenir_contexte_db() as db:
            taches_retard = (
                db.query(MaintenanceTask)
                .filter(
                    MaintenanceTask.prochaine_fois < date.today(),
                    MaintenanceTask.fait.is_(False),
                )
                .limit(10)
                .all()
            )

            if taches_retard:
                alerts.append(
                    {
                        "type": "warning",
                        "icon": "🧹",
                        "title": f"{len(taches_retard)} tâche(s) menage en retard!",
                        "action": "Voir Maison",
                        "module": "maison.entretien",
                    }
                )

                # Detail des tâches critiques
                for t in taches_retard[:3]:
                    jours_retard = (date.today() - t.prochaine_fois).days
                    alerts.append(
                        {
                            "type": "error" if jours_retard > 7 else "warning",
                            "icon": "⚠️",
                            "title": f"{t.nom} ({jours_retard}j de retard)",
                            "action": "Marquer fait",
                            "module": "maison.entretien",
                        }
                    )
    except Exception:
        pass  # Table pas encore creee

    # Afficher alertes
    if not alerts:
        st.success("✅ Tout est en ordre !")
        return

    st.markdown("### ⏰ Alertes")

    for alert in alerts:
        with st.container():
            col1, col2 = st.columns([4, 1])

            with col1:
                if alert["type"] == "warning":
                    st.warning(f"{alert['icon']} **{alert['title']}**")
                elif alert["type"] == "info":
                    st.info(f"{alert['icon']} **{alert['title']}**")
                else:
                    st.error(f"{alert['icon']} **{alert['title']}**")

            with col2:
                if st.button(alert["action"], key=_keys("alert", alert["module"]), width="stretch"):
                    GestionnaireEtat.naviguer_vers(alert["module"])
                    st.rerun()
