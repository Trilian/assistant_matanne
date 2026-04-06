"""
Service Inter-Modules — Bridges entre modules.

Compose les mixins cuisine, famille et maison en une seule classe
BridgesInterModulesService et fournit la factory singleton,
les event handlers et le catalogue de consolidation.

Mixins :
- inter_modules_cuisine.CuisineBridgesMixin
- inter_modules_famille.FamilleBridgesMixin
- inter_modules_maison.MaisonBridgesMixin
"""

import importlib
import logging
from pathlib import Path

from src.services.core.events.bus import EvenementDomaine
from src.services.core.registry import service_factory
from src.services.ia.inter_modules_cuisine import CuisineBridgesMixin
from src.services.ia.inter_modules_famille import FamilleBridgesMixin
from src.services.ia.inter_modules_maison import MaisonBridgesMixin

logger = logging.getLogger(__name__)

_CATALOGUE_BRIDGES_LABELS: dict[str, dict[str, str]] = {
    "src.services.utilitaires.inter_modules.inter_module_dashboard_actions": {
        "groupe": "utilitaires",
        "flux": "Dashboard → Actions rapides",
    },
    "src.services.utilitaires.inter_modules.inter_module_chat_event_bus": {
        "groupe": "utilitaires",
        "flux": "Chat IA → Event Bus",
    },
    "src.services.utilitaires.inter_modules.inter_module_chat_contexte": {
        "groupe": "utilitaires",
        "flux": "Chat → Contexte multi-modules",
    },
    "src.services.famille.inter_module_weekend_courses": {
        "groupe": "famille",
        "flux": "Weekend → Courses",
    },
    "src.services.famille.inter_module_voyages_budget": {
        "groupe": "famille",
        "flux": "Voyages → Budget",
    },
    "src.services.famille.inter_module_meteo_activites": {
        "groupe": "famille",
        "flux": "Météo → Activités",
    },
    "src.services.famille.inter_module_documents_calendrier": {
        "groupe": "famille",
        "flux": "Documents → Calendrier",
    },
    "src.services.cuisine.inter_module_saison_menu": {
        "groupe": "cuisine",
        "flux": "Saison → Menu",
    },
    "src.services.maison.inter_modules.inter_module_jardin_entretien": {
        "groupe": "maison",
        "flux": "Jardin → Entretien",
    },
    "src.services.maison.inter_modules.inter_module_entretien_courses": {
        "groupe": "maison",
        "flux": "Entretien → Courses",
    },
    "src.services.maison.inter_modules.inter_module_charges_energie": {
        "groupe": "maison",
        "flux": "Charges → Énergie",
    },
}


def _humaniser_segment(segment: str) -> str:
    """Formate un segment de nom de bridge pour l'UI admin."""
    return segment.replace("_", " ").strip().capitalize()


def _lister_modules_legacy_inter_modules() -> list[str]:
    """Découvre automatiquement les wrappers legacy `inter_module_*.py`."""
    racine_services = Path(__file__).resolve().parents[1]
    racine_repo = racine_services.parents[1]
    modules: list[str] = []

    for fichier in sorted(racine_services.rglob("inter_module_*.py")):
        if fichier.name == "__init__.py":
            continue
        relatif = fichier.relative_to(racine_repo).with_suffix("")
        modules.append(".".join(relatif.parts))

    return modules


def _construire_definition_catalogue(module: str) -> dict[str, str]:
    """Construit la définition d'un bridge pour le catalogue consolidé."""
    if module in _CATALOGUE_BRIDGES_LABELS:
        return {**_CATALOGUE_BRIDGES_LABELS[module], "module": module}

    parties = module.split(".")
    groupe = parties[2] if len(parties) > 2 else "autres"
    nom_bridge = parties[-1].removeprefix("inter_module_")
    morceaux = [morceau for morceau in nom_bridge.split("_") if morceau]

    source = _humaniser_segment(morceaux[0]) if morceaux else "Bridge"
    cible = _humaniser_segment("_".join(morceaux[1:])) if len(morceaux) > 1 else "Actions"

    return {
        "groupe": groupe,
        "flux": f"{source} → {cible}",
        "module": module,
    }


class BridgesInterModulesService(CuisineBridgesMixin, FamilleBridgesMixin, MaisonBridgesMixin):
    """Service de bridges inter-modules — compose les mixins cuisine, famille et maison."""

    def obtenir_catalogue_consolidation(self) -> dict[str, object]:
        """Expose l'état consolidé des inter_modules legacy et canoniques."""
        definitions = [
            _construire_definition_catalogue(module)
            for module in _lister_modules_legacy_inter_modules()
        ]

        items: list[dict[str, object]] = []
        for definition in definitions:
            importable = True
            erreur_import: str | None = None
            try:
                importlib.import_module(str(definition["module"]))
            except Exception as exc:  # pragma: no cover - info d'audit uniquement
                importable = False
                erreur_import = exc.__class__.__name__

            items.append({
                **definition,
                "statut": "consolide",
                "mode": "compat_legacy",
                "disponible": True,
                "importable": importable,
                "verification_import": "ok" if importable else f"warning:{erreur_import}",
            })

        total = len(items)
        groupes = sorted({str(item["groupe"]) for item in items})
        warnings_import = sum(1 for item in items if not item["importable"])

        return {
            "resume": {
                "total_legacy": total,
                "consolides": total,
                "reste_a_traiter": 0,
                "groupes": groupes,
                "warnings_import": warnings_import,
                "statut": "termine",
            },
            "items": items,
        }


# ═══════════════════════════════════════════════════════════
# EVENT HANDLERS (subscribers)
# ═══════════════════════════════════════════════════════════


def _on_jardin_recolte(event: EvenementDomaine) -> None:
    """Handler: Quand une récolte jardin est validée → suggérer des recettes."""
    try:
        nom = event.data.get("nom", "")
        if not nom:
            return

        service = obtenir_service_bridges()
        recettes = service.recolte_vers_recettes(nom)

        if recettes:
            logger.info(
                f"🌱→🍽️ Récolte '{nom}' → {len(recettes)} recette(s) trouvée(s): "
                f"{', '.join(r['nom'] for r in recettes[:3])}"
            )
            from src.services.core.events import obtenir_bus
            obtenir_bus().emettre("bridge.recolte_recettes", {
                "ingredient": nom,
                "recettes": recettes[:5],
                "nb_recettes": len(recettes),
            })
    except Exception as e:
        logger.warning(f"Erreur bridge récolte→recettes: {e}")


def _on_budget_modifie(event: EvenementDomaine) -> None:
    """Handler: Quand le budget est modifié → vérifier les anomalies."""
    try:
        service = obtenir_service_bridges()
        anomalies = service.verifier_anomalies_budget_et_notifier()
        if anomalies:
            logger.info(f"💰 {len(anomalies)} anomalie(s) budget détectée(s)")
    except Exception as e:
        logger.warning(f"Erreur bridge budget→notification: {e}")


def _on_batch_cooking_termine(event: EvenementDomaine) -> None:
    """Handler: Fin de session batch cooking → notification Telegram (E6)."""
    import asyncio

    try:
        session_id = event.data.get("session_id")
        nom_session = event.data.get("nom_session", "Session batch")
        nb_recettes = event.data.get("nb_recettes", 0)
        photo_url = event.data.get("photo_url")

        from src.services.integrations.telegram import envoyer_confirmation_batch_cooking

        asyncio.run(envoyer_confirmation_batch_cooking(
            nom_session=nom_session,
            nb_recettes=nb_recettes,
            photo_url=photo_url,
            session_id=session_id,
        ))
        logger.info(f"✅ Notification Telegram batch cooking #{session_id} envoyée")
    except Exception as e:
        logger.warning(f"Erreur bridge batch_cooking→Telegram: {e}")


# ═══════════════════════════════════════════════════════════
# FACTORY
# ═══════════════════════════════════════════════════════════


@service_factory("bridges_inter_modules", tags={"inter_modules"})
def obtenir_service_bridges() -> BridgesInterModulesService:
    """Factory singleton."""
    return BridgesInterModulesService()


def enregistrer_bridges_subscribers() -> None:
    """Enregistre tous les subscribers de bridges inter-modules dans le bus."""
    from src.services.core.events import obtenir_bus

    bus = obtenir_bus()
    bus.souscrire("jardin.recolte", _on_jardin_recolte)
    bus.souscrire("budget.modifie", _on_budget_modifie)
    bus.souscrire("batch_cooking.termine", _on_batch_cooking_termine)

    logger.info("✅ Bridges inter-modules enregistrés (jardin→recettes, budget→notification, batch_cooking→telegram)")
