"""Domaine Maison - Gestion entretien, projets et jardin."""

# Import paresseux des modules pour faciliter les tests
# Les modules UI dépendent de pandas et ne sont pas requis pour les tests de logique


def __getattr__(name):
    """Chargement paresseux des modules pour optimiser les tests et le démarrage."""
    if name in ("entretien", "projets", "jardin"):
        from . import ui
        return getattr(ui, name)
    elif name in ("entretien_logic", "projets_logic", "jardin_logic", "helpers"):
        from . import logic
        return getattr(logic, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    # UI
    "entretien", "projets", "jardin",
    # Logic
    "entretien_logic", "projets_logic", "jardin_logic", "helpers",
]
