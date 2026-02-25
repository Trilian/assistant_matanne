"""Module Maison - Gestion intégrée de l'habitat avec lazy loading.

Sous-modules disponibles:
- hub: Hub central intelligent avec briefing IA
- jardin: Potager intelligent avec tâches auto-générées
- entretien: Entretien maison avec inventaire équipements
- charges: Suivi énergie et charges fixes
- depenses: Suivi dépenses maison
"""

__all__ = [
    "charges",
    "depenses",
    "eco_tips",
    "energie",
    "entretien",
    "hub",
    "jardin",
    "jardin_zones",
    "meubles",
    "projets",
]


def __getattr__(name: str):
    """Import differé pour éviter les imports circulaires."""
    if name in __all__:
        from importlib import import_module

        module = import_module(f".{name}", __package__)
        globals()[name] = module
        return module
    raise AttributeError(f"module 'src.modules.maison' has no attribute '{name}'")
