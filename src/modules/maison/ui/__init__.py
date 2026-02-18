"""
UI Components pour le module Maison.

Composants visuels interactifs déplacés de src/ui/maison/:
- Plan interactif de la maison (pièces, objets)
- Plan interactif du jardin (zones, plantes)
- Cartes et widgets spécifiques maison
- Suivi du temps (chronomètre, statistiques)
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .composants import (
        badge_priorite,
        badge_statut_widget,
        carte_objet_statut,
        indicateur_urgence,
        modal_changement_statut,
        selecteur_statut,
        timeline_versions,
        widget_cout_travaux,
    )
    from .plan_jardin import (
        MeteoJardinData,
        PlanJardinInteractif,
        PlanteData,
        ZoneJardinData,
        calendrier_jardin,
        carte_zone,
        grille_plantes,
    )
    from .plan_maison import (
        ObjetData,
        PieceData,
        PlanMaisonInteractif,
        carte_piece,
        grille_objets,
        timeline_travaux,
    )
    from .temps_ui import (
        carte_materiel,
        carte_suggestion,
        chronometre_widget,
        dashboard_temps,
        historique_sessions,
        score_efficacite,
    )


def __getattr__(name: str):
    """Lazy loading des composants UI."""
    # Plan maison
    if name in (
        "PlanMaisonInteractif",
        "PieceData",
        "ObjetData",
        "carte_piece",
        "grille_objets",
        "timeline_travaux",
    ):
        from .plan_maison import (
            ObjetData,
            PieceData,
            PlanMaisonInteractif,
            carte_piece,
            grille_objets,
            timeline_travaux,
        )

        return locals()[name]

    # Plan jardin
    if name in (
        "PlanJardinInteractif",
        "ZoneJardinData",
        "PlanteData",
        "MeteoJardinData",
        "carte_zone",
        "calendrier_jardin",
        "grille_plantes",
    ):
        from .plan_jardin import (
            MeteoJardinData,
            PlanJardinInteractif,
            PlanteData,
            ZoneJardinData,
            calendrier_jardin,
            carte_zone,
            grille_plantes,
        )

        return locals()[name]

    # Composants réutilisables
    if name in (
        "carte_objet_statut",
        "badge_priorite",
        "badge_statut_widget",
        "modal_changement_statut",
        "widget_cout_travaux",
        "timeline_versions",
        "selecteur_statut",
        "indicateur_urgence",
    ):
        from .composants import (
            badge_priorite,
            badge_statut_widget,
            carte_objet_statut,
            indicateur_urgence,
            modal_changement_statut,
            selecteur_statut,
            timeline_versions,
            widget_cout_travaux,
        )

        return locals()[name]

    # Suivi du temps
    if name in (
        "chronometre_widget",
        "dashboard_temps",
        "carte_suggestion",
        "carte_materiel",
        "historique_sessions",
        "score_efficacite",
    ):
        from .temps_ui import (
            carte_materiel,
            carte_suggestion,
            chronometre_widget,
            dashboard_temps,
            historique_sessions,
            score_efficacite,
        )

        return locals()[name]

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    # Plan maison
    "PlanMaisonInteractif",
    "PieceData",
    "ObjetData",
    "carte_piece",
    "grille_objets",
    "timeline_travaux",
    # Plan jardin
    "PlanJardinInteractif",
    "ZoneJardinData",
    "PlanteData",
    "MeteoJardinData",
    "carte_zone",
    "calendrier_jardin",
    "grille_plantes",
    # Composants
    "carte_objet_statut",
    "badge_priorite",
    "badge_statut_widget",
    "modal_changement_statut",
    "widget_cout_travaux",
    "timeline_versions",
    "selecteur_statut",
    "indicateur_urgence",
    # Suivi du temps
    "chronometre_widget",
    "dashboard_temps",
    "carte_suggestion",
    "carte_materiel",
    "historique_sessions",
    "score_efficacite",
]
