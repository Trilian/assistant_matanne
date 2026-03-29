"""
CatalogueEnrichissementService — Enrichissement IA des catalogues de référence.

Enrichit automatiquement les fichiers JSON de référence (guide lessive,
astuces domotique, routines par défaut, plantes) via l'IA Mistral.
"""

import json
import logging
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any

from src.services.core.registry import service_factory

logger = logging.getLogger(__name__)

CHEMIN_REFERENCE = Path("data/reference")


class CatalogueEnrichissementService:
    """Enrichit les catalogues de données de référence via l'IA Mistral."""

    def __init__(self) -> None:
        self._client: Any = None

    def _obtenir_client(self) -> Any:
        """Lazy-loading du client IA."""
        if self._client is None:
            try:
                from src.core.ai import obtenir_client_ia
                self._client = obtenir_client_ia()
            except Exception as exc:
                logger.warning("Client IA indisponible: %s", exc)
        return self._client

    def _backup(self, fichier: Path) -> None:
        """Copie le fichier vers le dossier backups avec horodatage."""
        dossier_backup = CHEMIN_REFERENCE / "backups"
        dossier_backup.mkdir(parents=True, exist_ok=True)
        horodatage = datetime.now().strftime("%Y%m%d_%H%M%S")
        destination = dossier_backup / f"{fichier.stem}_{horodatage}.json"
        shutil.copy2(fichier, destination)
        logger.info("Backup créé: %s", destination)

    def _charger_json(self, fichier: Path) -> dict | list:
        """Charge un fichier JSON de façon sécurisée."""
        if not fichier.exists():
            return []
        try:
            with fichier.open(encoding="utf-8") as f:
                return json.load(f)
        except Exception as exc:
            logger.error("Erreur chargement JSON %s: %s", fichier, exc)
            return []

    def _sauvegarder_json(self, fichier: Path, data: Any) -> None:
        """Sauvegarde les données en JSON indenté."""
        fichier.parent.mkdir(parents=True, exist_ok=True)
        with fichier.open("w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _appeler_ia_sync(self, prompt: str) -> str | None:
        """Appel IA synchrone simplifié."""
        client = self._obtenir_client()
        if client is None:
            return None
        try:
            import asyncio
            loop = asyncio.new_event_loop()
            try:
                reponse = loop.run_until_complete(
                    client.appeler(prompt, temperature=0.7, max_tokens=1500)
                )
                return reponse
            finally:
                loop.close()
        except Exception as exc:
            logger.warning("Erreur appel IA: %s", exc)
            return None

    def enrichir_guide_lessive(self, min_nouvelles: int = 3) -> int:
        """Enrichit guide_lessive.json avec de nouvelles entrées IA.

        Returns:
            Nombre de nouvelles entrées ajoutées.
        """
        try:
            fichier = CHEMIN_REFERENCE / "guide_lessive.json"
            existant = self._charger_json(fichier)
            if isinstance(existant, dict):
                entrees = existant.get("entrees", existant.get("guides", []))
            else:
                entrees = existant if isinstance(existant, list) else []

            noms_existants = [str(e.get("tache", e.get("nom", ""))) for e in entrees if isinstance(e, dict)]
            prompt = (
                f"Voici les entrées existantes du guide de traitement des taches de lessive: {noms_existants}. "
                f"Génère {min_nouvelles + 2} nouvelles entrées de guide lessive pour des types de taches différents "
                f"(non présents dans la liste). Chaque entrée doit avoir: tache (string), "
                f"etapes (liste de strings), produits (liste de strings), tissu (string optionnel). "
                f"Réponds UNIQUEMENT en JSON: [{{\"tache\": \"...\", \"etapes\": [...], \"produits\": [...]}}]"
            )

            reponse = self._appeler_ia_sync(prompt)
            if not reponse:
                return 0

            debut = reponse.find("[")
            fin = reponse.rfind("]") + 1
            if debut < 0 or fin <= debut:
                return 0

            nouvelles = json.loads(reponse[debut:fin])
            valides = [e for e in nouvelles if isinstance(e, dict) and e.get("tache")]
            if len(valides) < min_nouvelles:
                logger.warning("Enrichissement lessive: seulement %d entrées valides", len(valides))
                return 0

            self._backup(fichier) if fichier.exists() else None
            entrees.extend(valides)
            if isinstance(existant, dict):
                existant["entrees"] = entrees
                self._sauvegarder_json(fichier, existant)
            else:
                self._sauvegarder_json(fichier, entrees)
            logger.info("Guide lessive enrichi: +%d entrées", len(valides))
            return len(valides)
        except Exception as exc:
            logger.error("Erreur enrichissement guide lessive: %s", exc)
            return 0

    def enrichir_astuces_domotique(self, min_nouvelles: int = 3) -> int:
        """Enrichit astuces_domotique.json avec de nouvelles astuces IA.

        Returns:
            Nombre de nouvelles astuces ajoutées.
        """
        try:
            fichier = CHEMIN_REFERENCE / "astuces_domotique.json"
            existant = self._charger_json(fichier)
            if isinstance(existant, dict):
                astuces = existant.get("astuces", [])
            else:
                astuces = existant if isinstance(existant, list) else []

            titres_existants = [str(a.get("titre", a.get("nom", ""))) for a in astuces if isinstance(a, dict)]
            prompt = (
                f"Voici les astuces domotique existantes: {titres_existants[:20]}. "
                f"Génère {min_nouvelles + 2} nouvelles astuces domotique pour la maison connectée "
                f"(non présentes dans la liste, variées et pratiques). "
                f"Chaque astuce doit avoir: titre (string), description (string), categorie (string), "
                f"economie_energie (bool optionnel). "
                f"Réponds UNIQUEMENT en JSON: [{{\"titre\": \"...\", \"description\": \"...\", \"categorie\": \"...\"}}]"
            )

            reponse = self._appeler_ia_sync(prompt)
            if not reponse:
                return 0

            debut = reponse.find("[")
            fin = reponse.rfind("]") + 1
            if debut < 0 or fin <= debut:
                return 0

            nouvelles = json.loads(reponse[debut:fin])
            valides = [a for a in nouvelles if isinstance(a, dict) and a.get("titre")]
            if len(valides) < min_nouvelles:
                return 0

            self._backup(fichier) if fichier.exists() else None
            astuces.extend(valides)
            if isinstance(existant, dict):
                existant["astuces"] = astuces
                self._sauvegarder_json(fichier, existant)
            else:
                self._sauvegarder_json(fichier, astuces)
            logger.info("Astuces domotique enrichies: +%d", len(valides))
            return len(valides)
        except Exception as exc:
            logger.error("Erreur enrichissement astuces domotique: %s", exc)
            return 0

    def enrichir_routines_defaut(self, min_nouvelles: int = 3) -> int:
        """Enrichit routines_defaut.json avec de nouvelles routines IA.

        Returns:
            Nombre de nouvelles routines ajoutées.
        """
        try:
            fichier = CHEMIN_REFERENCE / "routines_defaut.json"
            existant = self._charger_json(fichier)
            if isinstance(existant, dict):
                routines = existant.get("routines", [])
            else:
                routines = existant if isinstance(existant, list) else []

            noms_existants = [str(r.get("nom", "")) for r in routines if isinstance(r, dict)]
            prompt = (
                f"Voici les routines ménagères existantes: {noms_existants}. "
                f"Génère {min_nouvelles + 2} nouvelles routines ménagères quotidiennes ou hebdomadaires "
                f"(non présentes dans la liste). Chaque routine doit avoir: nom (string), "
                f"description (string), frequence ('quotidien'|'hebdomadaire'|'mensuel'), "
                f"moment_journee ('matin'|'soir'|'flexible'), "
                f"taches (liste de {{nom: string, duree_estimee_min: int}}). "
                f"Réponds UNIQUEMENT en JSON: [{{\"nom\": \"...\", \"frequence\": \"...\", \"taches\": [...]}}]"
            )

            reponse = self._appeler_ia_sync(prompt)
            if not reponse:
                return 0

            debut = reponse.find("[")
            fin = reponse.rfind("]") + 1
            if debut < 0 or fin <= debut:
                return 0

            nouvelles = json.loads(reponse[debut:fin])
            valides = [r for r in nouvelles if isinstance(r, dict) and r.get("nom")]
            if len(valides) < min_nouvelles:
                return 0

            self._backup(fichier) if fichier.exists() else None
            routines.extend(valides)
            if isinstance(existant, dict):
                existant["routines"] = routines
                self._sauvegarder_json(fichier, existant)
            else:
                self._sauvegarder_json(fichier, routines)
            logger.info("Routines défaut enrichies: +%d", len(valides))
            return len(valides)
        except Exception as exc:
            logger.error("Erreur enrichissement routines défaut: %s", exc)
            return 0

    def enrichir_plantes(self, min_nouvelles: int = 3) -> int:
        """Enrichit plantes_catalogue.json avec de nouvelles plantes IA.

        Returns:
            Nombre de nouvelles plantes ajoutées.
        """
        try:
            fichier = CHEMIN_REFERENCE / "plantes_catalogue.json"
            existant = self._charger_json(fichier)
            if isinstance(existant, dict):
                plantes = existant.get("plantes", [])
            else:
                plantes = existant if isinstance(existant, list) else []

            noms_existants = [str(p.get("nom", p.get("nom_commun", ""))) for p in plantes if isinstance(p, dict)]
            prompt = (
                f"Voici les plantes existantes dans le catalogue: {noms_existants[:20]}. "
                f"Génère {min_nouvelles + 2} nouvelles plantes de jardin ou d'intérieur "
                f"(non présentes dans la liste). Chaque plante doit avoir: nom (string), "
                f"nom_latin (string), type ('legume'|'fruit'|'fleur'|'arbre'|'interieur'|'aromatique'), "
                f"arrosage_frequence (string), exposition ('soleil'|'mi-ombre'|'ombre'), "
                f"mois_plantation (liste de mois), conseils (string). "
                f"Réponds UNIQUEMENT en JSON: [{{\"nom\": \"...\", \"type\": \"...\", \"arrosage_frequence\": \"...\"}}]"
            )

            reponse = self._appeler_ia_sync(prompt)
            if not reponse:
                return 0

            debut = reponse.find("[")
            fin = reponse.rfind("]") + 1
            if debut < 0 or fin <= debut:
                return 0

            nouvelles = json.loads(reponse[debut:fin])
            valides = [p for p in nouvelles if isinstance(p, dict) and p.get("nom")]
            if len(valides) < min_nouvelles:
                return 0

            self._backup(fichier) if fichier.exists() else None
            plantes.extend(valides)
            if isinstance(existant, dict):
                existant["plantes"] = plantes
                self._sauvegarder_json(fichier, existant)
            else:
                self._sauvegarder_json(fichier, plantes)
            logger.info("Plantes enrichies: +%d", len(valides))
            return len(valides)
        except Exception as exc:
            logger.error("Erreur enrichissement plantes: %s", exc)
            return 0

    def enrichir_tout(self) -> dict[str, int]:
        """Enrichit tous les catalogues.

        Returns:
            dict avec le nombre de nouvelles entrées par catalogue.
        """
        return {
            "lessive": self.enrichir_guide_lessive(),
            "domotique": self.enrichir_astuces_domotique(),
            "routines": self.enrichir_routines_defaut(),
            "plantes": self.enrichir_plantes(),
        }


@service_factory("catalogue_enrichissement")
def obtenir_catalogue_enrichissement_service() -> CatalogueEnrichissementService:
    """Factory singleton pour CatalogueEnrichissementService."""
    return CatalogueEnrichissementService()


# ─── Aliases rétrocompatibilité (Sprint 12 A3) ───────────────────────────────
get_catalogue_enrichissement_service = obtenir_catalogue_enrichissement_service  # alias rétrocompatibilité Sprint 12 A3
