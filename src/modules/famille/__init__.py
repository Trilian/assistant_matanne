"""Domaine Famille - Gestion famille (Jules, santé, activités, shopping).

Nouveaux modules (refonte 2026-02):
- hub_famille.py: Dashboard avec cards cliquables
- jules_nouveau.py: Activités adaptées âge + shopping + conseils IA
- suivi_perso.py: Anne & Mathieu, Garmin, alimentation
- weekend.py: Planning weekend + suggestions IA
- achats_famille.py: Wishlist famille par catégorie

Modules conservés:
- activites.py: Planning activités générales
- routines.py: Routines quotidiennes
"""

# Import paresseux des modules pour faciliter les tests
# Les modules UI dépendent de pandas/plotly et ne sont pas requis pour les tests de logique


def __getattr__(name):
    """Chargement paresseux des modules pour optimiser les tests et le démarrage."""
    if name in ("hub_famille", "jules", "suivi_perso", "weekend", "achats_famille", 
                "activites", "routines"):
        from . import ui
        return getattr(ui, name)
    elif name in ("activites_logic", "routines_logic", "helpers"):
        from . import logic
        return getattr(logic, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
