"""
Configuration Module - Dataclass de configuration CRUD
"""

from collections.abc import Callable
from dataclasses import dataclass, field

from src.services.core.base import BaseService


@dataclass
class ConfigurationModule:
    """
    Configuration complète d'un module CRUD

    Permet de générer automatiquement l'UI complète pour
    n'importe quel module métier (recettes, inventaire, etc.)

    Attributes:
        name: Identifiant unique du module (ex: "recettes")
        title: Titre affiché (ex: "Recettes")
        icon: Emoji icône (ex: "🍽️")
        service: Instance du service CRUD
        display_fields: Champs à afficher [{key, label, type}]
        search_fields: Champs pour la recherche
        filters_config: Configuration des filtres
        stats_config: Configuration des stats [{label, value_key|filter}]
        actions: Actions disponibles [{label, icon, callback}]
        status_field: Champ de statut (optionnel)
        status_colors: Mapping statut → couleur
        metadata_fields: Champs métadonnées à afficher
        image_field: Champ image (optionnel)
        form_fields: Configuration du formulaire
        export_formats: Formats d'export disponibles
        items_per_page: Nombre d'items par page
        on_view: Callback vue détail
        on_edit: Callback édition
        on_delete: Callback suppression
        on_create: Callback création

    Example:
        config = ConfigurationModule(
            name="recettes",
            title="Recettes",
            icon="🍽️",
            service=recette_service,
            display_fields=[{"key": "nom", "label": "Nom"}],
            search_fields=["nom", "description"],
        )
    """

    # Identité
    name: str
    title: str
    icon: str

    # Service
    service: BaseService

    # Affichage
    display_fields: list[dict] = field(default_factory=list)
    search_fields: list[str] = field(default_factory=list)

    # Filtres
    filters_config: dict = field(default_factory=dict)

    # Stats
    stats_config: list[dict] = field(default_factory=list)

    # Actions
    actions: list[dict] = field(default_factory=list)

    # Statut
    status_field: str | None = None
    status_colors: dict[str, str] = field(default_factory=dict)

    # Métadonnées
    metadata_fields: list[str] = field(default_factory=list)
    image_field: str | None = None

    # Formulaire
    form_fields: list[dict] = field(default_factory=list)

    # Import/Export
    export_formats: list[str] = field(default_factory=lambda: ["csv", "json"])

    # Pagination
    items_per_page: int = 20

    # Callbacks
    on_view: Callable | None = None
    on_edit: Callable | None = None
    on_delete: Callable | None = None
    on_create: Callable | None = None


# Alias pour compatibilité
ModuleConfig = ConfigurationModule
