"""
Fonctions de statistiques pour les actions écologiques.
"""

from datetime import date

from .crud import get_all_actions


def calculate_stats() -> dict:
    """Calcule les statistiques des actions écologiques.

    Returns:
        Dict avec nb_actions, economie_mensuelle, economie_annuelle,
        cout_nouveau_initial, roi_mois, economies_totales.
    """
    actions = get_all_actions()

    if not actions:
        return {
            "nb_actions": 0,
            "economie_mensuelle": 0,
            "economie_annuelle": 0,
            "cout_nouveau_initial": 0,
            "roi_mois": 0,
            "economies_totales": 0,
        }

    eco_mensuelle = sum(float(a.economie_mensuelle) for a in actions if a.economie_mensuelle)
    cout_initial = sum(float(a.cout_nouveau_initial) for a in actions if a.cout_nouveau_initial)
    eco_annuelle = eco_mensuelle * 12
    roi_mois = (cout_initial / eco_mensuelle) if eco_mensuelle > 0 else 0

    # Calcul des économies totales (depuis la date de début de chaque action)
    economies_totales = 0.0
    for a in actions:
        if a.economie_mensuelle and a.date_debut:
            mois_actifs = max(
                0,
                (date.today().year - a.date_debut.year) * 12
                + (date.today().month - a.date_debut.month),
            )
            economies_totales += float(a.economie_mensuelle) * mois_actifs

    return {
        "nb_actions": len(actions),
        "economie_mensuelle": eco_mensuelle,
        "economie_annuelle": eco_annuelle,
        "cout_nouveau_initial": cout_initial,
        "roi_mois": roi_mois,
        "economies_totales": economies_totales,
    }
