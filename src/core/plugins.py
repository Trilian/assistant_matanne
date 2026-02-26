"""
Système de plugins modulaire — Innovation 2.2.

Architecture "plugin" où les modules sont auto-découverts via manifestes.
Chaque module expose un MODULE_MANIFEST avec ses métadonnées.

Usage:
    from src.core.plugins import (
        PluginManifest,
        PluginRegistry,
        obtenir_registre_plugins,
        decouvrir_modules,
    )

    # Auto-découverte des modules
    registre = obtenir_registre_plugins()
    registre.decouvrir("src.modules")

    # Lister les modules actifs
    for plugin in registre.lister():
        print(f"{plugin.nom} v{plugin.version}")

    # Vérifier les dépendances
    erreurs = registre.verifier_dependances()

    # Obtenir les pages pour st.navigation
    pages = registre.construire_pages()

Manifest dans un module:
    # src/modules/maison/jardin.py
    MODULE_MANIFEST = {
        "nom": "Jardin",
        "version": "2.1",
        "icone": "🌱",
        "section": "🏠 Maison",
        "dependances": ["maison.hub"],
        "configuration": {"afficher_plan_2d": True},
        "tags": ["maison", "jardin", "outdoor"],
        "pages": [("jardin", "🌱 Jardin", "app")],
    }
"""

from __future__ import annotations

import importlib
import logging
import pkgutil
from dataclasses import dataclass, field
from typing import Any, Callable

import streamlit as st

logger = logging.getLogger(__name__)

__all__ = [
    "PluginManifest",
    "PluginRegistry",
    "obtenir_registre_plugins",
    "decouvrir_modules",
]


# ═══════════════════════════════════════════════════════════
# MANIFEST — Métadonnées d'un module plugin
# ═══════════════════════════════════════════════════════════


@dataclass
class PluginManifest:
    """Manifeste d'un module plugin.

    Décrit un module avec ses métadonnées, dépendances et pages.
    """

    nom: str
    version: str = "1.0"
    icone: str = "📦"
    section: str = ""
    description: str = ""
    auteur: str = ""
    dependances: list[str] = field(default_factory=list)
    configuration: dict[str, Any] = field(default_factory=dict)
    tags: list[str] = field(default_factory=list)
    pages: list[tuple[str, str, str]] = field(default_factory=list)
    # (key, titre_affiche, nom_fonction_app)
    module_path: str = ""
    actif: bool = True
    priorite: int = 50  # 0 = premier, 100 = dernier

    @classmethod
    def from_dict(cls, data: dict[str, Any], module_path: str = "") -> PluginManifest:
        """Crée un manifest depuis un dict (MODULE_MANIFEST).

        Args:
            data: Dict du module
            module_path: Chemin d'import du module

        Returns:
            PluginManifest
        """
        return cls(
            nom=data.get("nom", "Inconnu"),
            version=data.get("version", "1.0"),
            icone=data.get("icone", "📦"),
            section=data.get("section", ""),
            description=data.get("description", ""),
            auteur=data.get("auteur", ""),
            dependances=data.get("dependances", []),
            configuration=data.get("configuration", {}),
            tags=data.get("tags", []),
            pages=data.get("pages", []),
            module_path=module_path,
            actif=data.get("actif", True),
            priorite=data.get("priorite", 50),
        )


# ═══════════════════════════════════════════════════════════
# PLUGIN REGISTRY — Registre centralisé de plugins
# ═══════════════════════════════════════════════════════════


class PluginRegistry:
    """Registre centralisé pour les plugins de modules.

    Gère la découverte, validation et organisation des modules.
    """

    def __init__(self):
        self._plugins: dict[str, PluginManifest] = {}
        self._loaded_modules: dict[str, Any] = {}

    def enregistrer(self, manifest: PluginManifest) -> None:
        """Enregistre un plugin dans le registre.

        Args:
            manifest: Manifeste du plugin
        """
        key = manifest.nom.lower().replace(" ", "_")
        self._plugins[key] = manifest
        logger.debug(f"Plugin enregistré: {manifest.nom} v{manifest.version}")

    def decouvrir(self, package_path: str) -> int:
        """Auto-découvre les modules avec MODULE_MANIFEST.

        Parcourt récursivement le package et charge les manifestes.

        Args:
            package_path: Chemin d'import du package (ex: "src.modules")

        Returns:
            Nombre de plugins découverts
        """
        count = 0

        try:
            package = importlib.import_module(package_path)
        except ImportError as e:
            logger.error(f"Impossible de charger le package {package_path}: {e}")
            return 0

        if not hasattr(package, "__path__"):
            # Module simple (pas un package)
            count += self._scan_module(package, package_path)
            return count

        # Parcourir les sous-modules récursivement
        for importer, module_name, is_pkg in pkgutil.walk_packages(
            package.__path__,
            prefix=f"{package_path}.",
        ):
            try:
                mod = importlib.import_module(module_name)
                count += self._scan_module(mod, module_name)
            except Exception as e:
                logger.debug(f"Skip {module_name}: {e}")
                continue

        logger.info(f"[OK] {count} plugin(s) découvert(s) dans {package_path}")
        return count

    def _scan_module(self, module: Any, module_path: str) -> int:
        """Scanne un module pour un MODULE_MANIFEST.

        Args:
            module: Module Python chargé
            module_path: Chemin d'import

        Returns:
            1 si manifest trouvé, 0 sinon
        """
        manifest_data = getattr(module, "MODULE_MANIFEST", None)
        if manifest_data and isinstance(manifest_data, dict):
            manifest = PluginManifest.from_dict(manifest_data, module_path)
            self.enregistrer(manifest)
            self._loaded_modules[manifest.nom.lower().replace(" ", "_")] = module
            return 1
        return 0

    def lister(self, actifs_seulement: bool = True) -> list[PluginManifest]:
        """Liste les plugins enregistrés, triés par priorité.

        Args:
            actifs_seulement: Filtrer les plugins inactifs

        Returns:
            Liste triée de manifestes
        """
        plugins = list(self._plugins.values())
        if actifs_seulement:
            plugins = [p for p in plugins if p.actif]
        return sorted(plugins, key=lambda p: (p.section, p.priorite, p.nom))

    def obtenir(self, key: str) -> PluginManifest | None:
        """Obtient un plugin par sa clé.

        Args:
            key: Clé du plugin (nom normalisé)

        Returns:
            PluginManifest ou None
        """
        return self._plugins.get(key.lower().replace(" ", "_"))

    def par_section(self) -> dict[str, list[PluginManifest]]:
        """Regroupe les plugins par section.

        Returns:
            Dict {section: [plugins]}
        """
        sections: dict[str, list[PluginManifest]] = {}
        for plugin in self.lister():
            section = plugin.section or "Autre"
            sections.setdefault(section, []).append(plugin)
        return sections

    def par_tag(self, tag: str) -> list[PluginManifest]:
        """Filtre les plugins par tag.

        Args:
            tag: Tag à rechercher

        Returns:
            Liste de plugins avec ce tag
        """
        return [p for p in self.lister() if tag in p.tags]

    def verifier_dependances(self) -> list[str]:
        """Vérifie que toutes les dépendances sont satisfaites.

        Returns:
            Liste des erreurs de dépendances
        """
        erreurs = []
        noms_disponibles = {k for k in self._plugins}

        for key, plugin in self._plugins.items():
            for dep in plugin.dependances:
                dep_key = dep.lower().replace(".", "_").replace(" ", "_")
                # Chercher aussi avec le nom exact
                if dep_key not in noms_disponibles and dep not in noms_disponibles:
                    erreurs.append(f"Plugin '{plugin.nom}' requiert '{dep}' (non trouvé)")

        if erreurs:
            logger.warning(f"Dépendances manquantes: {erreurs}")

        return erreurs

    def obtenir_config(self, plugin_key: str, cle: str, defaut: Any = None) -> Any:
        """Obtient une valeur de configuration d'un plugin.

        Args:
            plugin_key: Clé du plugin
            cle: Clé de configuration
            defaut: Valeur par défaut

        Returns:
            Valeur de configuration
        """
        plugin = self.obtenir(plugin_key)
        if plugin:
            return plugin.configuration.get(cle, defaut)
        return defaut

    def construire_pages(self) -> dict[str, list[st.Page]]:
        """Construit les pages st.navigation() depuis les manifestes.

        Returns:
            Dict section → list[st.Page] compatible avec st.navigation()
        """
        from src.core.lazy_loader import ChargeurModuleDiffere

        pages: dict[str, list[st.Page]] = {}

        for plugin in self.lister():
            if not plugin.pages:
                continue

            section = plugin.section or "Autre"
            if section not in pages:
                pages[section] = []

            for page_key, page_title, func_name in plugin.pages:
                module_path = plugin.module_path

                def _make_runner(mp: str, fn: str) -> Callable:
                    def runner():
                        try:
                            mod = ChargeurModuleDiffere.charger(mp)
                            func = getattr(mod, fn, None)
                            if func:
                                func()
                            else:
                                st.error(f"Fonction '{fn}' non trouvée dans {mp}")
                        except Exception as e:
                            st.error(f"Erreur chargement: {e}")

                    return runner

                page = st.Page(
                    _make_runner(module_path, func_name),
                    title=page_title,
                    url_path=page_key.replace(".", "_"),
                )
                pages[section].append(page)

        return pages

    @property
    def stats(self) -> dict[str, Any]:
        """Statistiques du registre."""
        plugins = list(self._plugins.values())
        return {
            "total": len(plugins),
            "actifs": len([p for p in plugins if p.actif]),
            "sections": len(set(p.section for p in plugins)),
            "avec_dependances": len([p for p in plugins if p.dependances]),
        }


# ═══════════════════════════════════════════════════════════
# SINGLETON & HELPERS
# ═══════════════════════════════════════════════════════════

_registre: PluginRegistry | None = None


def obtenir_registre_plugins() -> PluginRegistry:
    """Obtient le registre de plugins singleton.

    Returns:
        PluginRegistry instance
    """
    global _registre
    if _registre is None:
        _registre = PluginRegistry()
    return _registre


def decouvrir_modules(package_path: str = "src.modules") -> int:
    """Découvre et enregistre tous les modules avec manifeste.

    Raccourci pour obtenir_registre_plugins().decouvrir().

    Args:
        package_path: Chemin d'import du package de modules

    Returns:
        Nombre de plugins découverts
    """
    registre = obtenir_registre_plugins()
    return registre.decouvrir(package_path)
