"""
Service Fiche Tâche Assistée — lookup catalogue JSON + IA Mistral fallback.

Pour chaque tâche (entretien, travaux, jardin, lessive), retourne une fiche
structurée : étapes, produits, durée, astuce connectée.
"""

import json
import logging
from pathlib import Path

from pydantic import BaseModel, Field

from src.core.ai import ClientIA
from src.core.decorators import avec_cache, avec_gestion_erreurs
from src.services.core.base import BaseAIService
from src.services.core.registry import service_factory

logger = logging.getLogger(__name__)

_DATA_DIR = Path(__file__).parents[3] / "data" / "reference"


class FicheTache(BaseModel):
    """Fiche tâche assistée."""

    nom: str
    type_tache: str
    duree_estimee_min: int = 15
    difficulte: str = "facile"  # facile, moyen, difficile
    etapes: list[str] = Field(default_factory=list)
    produits: list[dict] = Field(default_factory=list)
    outils: list[str] = Field(default_factory=list)
    astuce_connectee: str | None = None
    video_recherche: str | None = None
    source: str = "catalogue"


def _charger_json(nom_fichier: str) -> dict | list | None:
    """Charge un fichier JSON de référence."""
    path = _DATA_DIR / nom_fichier
    if not path.exists():
        return None
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Erreur chargement {nom_fichier}: {e}")
        return None


class FicheTacheService(BaseAIService):
    """Service fiches tâches : catalogue JSON + IA fallback."""

    def __init__(self, client: ClientIA | None = None):
        super().__init__(
            client=client,
            cache_prefix="fiche_tache",
            default_ttl=3600,
            service_name="fiche_tache",
        )
        self._entretien_catalogue: dict | None = None
        self._lessive_catalogue: dict | None = None
        self._travaux_catalogue: dict | None = None
        self._domotique_catalogue: dict | None = None

    def _get_entretien(self) -> dict:
        if self._entretien_catalogue is None:
            self._entretien_catalogue = _charger_json("entretien_catalogue.json") or {}
        return self._entretien_catalogue

    def _get_lessive(self) -> dict:
        if self._lessive_catalogue is None:
            self._lessive_catalogue = _charger_json("guide_lessive.json") or {}
        return self._lessive_catalogue

    def _get_travaux(self) -> dict:
        if self._travaux_catalogue is None:
            self._travaux_catalogue = _charger_json("guide_travaux_courants.json") or {}
        return self._travaux_catalogue

    def _get_domotique(self) -> dict:
        if self._domotique_catalogue is None:
            self._domotique_catalogue = _charger_json("astuces_domotique.json") or {}
        return self._domotique_catalogue

    @avec_cache(ttl=3600)
    @avec_gestion_erreurs(default_return=None)
    def obtenir_fiche(
        self,
        type_tache: str,
        id_tache: int | None = None,
        nom_tache: str | None = None,
    ) -> FicheTache | None:
        """Cherche une fiche dans les catalogues JSON.

        Returns:
            FicheTache ou None si non trouvée
        """
        if type_tache == "entretien":
            return self._fiche_entretien(id_tache, nom_tache)
        if type_tache == "lessive":
            return self._fiche_lessive(nom_tache)
        if type_tache == "travaux":
            return self._fiche_travaux(nom_tache)
        return None

    def _fiche_entretien(self, id_tache: int | None, nom: str | None) -> FicheTache | None:
        """Cherche dans entretien_catalogue.json."""
        catalogue = self._get_entretien()
        if not isinstance(catalogue, dict):
            return None

        # Chercher dans toutes les catégories
        for categorie, data in catalogue.items():
            if not isinstance(data, dict):
                continue
            for objet in data.get("objets", []):
                for tache in objet.get("taches", []):
                    match = (
                        (nom and nom.lower() in tache.get("nom", "").lower())
                        or (nom and nom.lower() in objet.get("nom", "").lower())
                    )
                    if not match and not nom:
                        match = True  # Retourne premiere si id donné sans nom

                    if match:
                        return FicheTache(
                            nom=tache.get("nom", objet.get("nom", "?")),
                            type_tache="entretien",
                            duree_estimee_min=tache.get("duree_min", 15),
                            difficulte=tache.get("difficulte", "facile"),
                            etapes=tache.get("etapes", [tache.get("description", "")]),
                            produits=tache.get("produits", []),
                            outils=tache.get("outils", []),
                            astuce_connectee=tache.get("astuce_connectee"),
                            source="catalogue",
                        )
        return None

    def _fiche_lessive(self, nom: str | None) -> FicheTache | None:
        """Cherche dans guide_lessive.json."""
        catalogue = self._get_lessive()
        if not catalogue:
            return None

        # Format: {taches: {nom_tache: {tissus: {tissu: {etapes, produits}}}}}
        taches = catalogue.get("taches", catalogue)
        nom_lower = (nom or "").lower()

        for nom_tache, data in taches.items() if isinstance(taches, dict) else []:
            if nom_lower and nom_lower not in nom_tache.lower():
                continue
            if isinstance(data, dict):
                etapes = data.get("etapes", [])
                produits = data.get("produits", [])
                if isinstance(produits, list) and produits and isinstance(produits[0], str):
                    produits = [{"nom": p} for p in produits]
                return FicheTache(
                    nom=nom_tache,
                    type_tache="lessive",
                    duree_estimee_min=data.get("duree_min", 10),
                    etapes=etapes if isinstance(etapes, list) else [etapes],
                    produits=produits,
                    difficulte="facile",
                    source="catalogue",
                )
        return None

    def _fiche_travaux(self, nom: str | None) -> FicheTache | None:
        """Cherche dans guide_travaux_courants.json."""
        catalogue = self._get_travaux()
        if not catalogue:
            return None

        travaux = catalogue.get("travaux", catalogue)
        nom_lower = (nom or "").lower()

        for item in travaux if isinstance(travaux, list) else []:
            if not isinstance(item, dict):
                continue
            if nom_lower and nom_lower not in item.get("nom", "").lower():
                continue
            produits_raw = item.get("materiaux", item.get("produits", []))
            if produits_raw and isinstance(produits_raw[0], str):
                produits_raw = [{"nom": p} for p in produits_raw]
            return FicheTache(
                nom=item.get("nom", "?"),
                type_tache="travaux",
                duree_estimee_min=item.get("duree_min", 60),
                difficulte=item.get("difficulte", "moyen"),
                etapes=item.get("etapes", []),
                produits=produits_raw,
                outils=item.get("outils", []),
                astuce_connectee=item.get("astuce_connectee"),
                source="catalogue",
            )
        return None

    @avec_cache(ttl=86400)
    def generer_fiche_ia(self, nom_tache: str, contexte: str = "") -> FicheTache:
        """Génère une fiche tâche via Mistral IA.

        Args:
            nom_tache: Nom de la tâche
            contexte: Contexte complémentaire

        Returns:
            FicheTache générée
        """
        prompt = f"""Génère une fiche pratique détaillée pour la tâche: "{nom_tache}"
{f"Contexte: {contexte}" if contexte else ""}

Format JSON:
{{
  "nom": "{nom_tache}",
  "duree_estimee_min": 30,
  "difficulte": "facile|moyen|difficile",
  "etapes": ["étape 1", "étape 2", ...],
  "produits": [{{"nom": "nom", "quantite": "1 bouteille", "prix_estime": 3.5}}],
  "outils": ["outil 1"],
  "astuce_connectee": "astuce domotique optionnelle"
}}"""

        try:
            result = self.call_with_cache_sync(
                prompt=prompt,
                system_prompt="Tu es expert en bricolage, ménage et entretien maison. Sois précis et pratique.",
                max_tokens=600,
            )
            import re

            json_match = re.search(r"\{.*\}", result, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                return FicheTache(
                    nom=data.get("nom", nom_tache),
                    type_tache="custom",
                    duree_estimee_min=data.get("duree_estimee_min", 30),
                    difficulte=data.get("difficulte", "moyen"),
                    etapes=data.get("etapes", []),
                    produits=data.get("produits", []),
                    outils=data.get("outils", []),
                    astuce_connectee=data.get("astuce_connectee"),
                    source="ia",
                )
        except Exception as e:
            logger.warning(f"Génération IA fiche tâche échouée: {e}")

        return FicheTache(
            nom=nom_tache,
            type_tache="custom",
            etapes=["Consulter un professionnel ou chercher un tutoriel en ligne"],
            source="ia_fallback",
        )

    @avec_cache(ttl=3600)
    def consulter_guide(
        self,
        type_guide: str,
        tache: str | None = None,
        tissu: str | None = None,
        appareil: str | None = None,
        probleme: str | None = None,
    ) -> dict:
        """Consulte le guide pratique thématique.

        Args:
            type_guide: lessive, electromenager, travaux
            tache: tache lessive (ex: vin, grass)
            tissu: type tissu
            appareil: appareil électroménager
            probleme: problème constaté

        Returns:
            Dict avec infos guide
        """
        if type_guide == "lessive" and tache:
            fiche = self._fiche_lessive(tache)
            if fiche:
                return {
                    "type": "lessive",
                    "tache": tache,
                    "tissu": tissu,
                    "etapes": fiche.etapes,
                    "produits": fiche.produits,
                }

        if type_guide == "electromenager" and appareil:
            catalogue = self._get_travaux()
            if catalogue:
                travaux = catalogue.get("travaux", catalogue)
                probleme_lower = (probleme or "").lower()
                appareil_lower = appareil.lower()
                for item in (travaux if isinstance(travaux, list) else []):
                    if not isinstance(item, dict):
                        continue
                    nom = item.get("nom", "").lower()
                    if appareil_lower in nom and (not probleme_lower or probleme_lower in nom):
                        return {"type": "electromenager", "appareil": appareil, **item}

        # Guide générique
        return {
            "type": type_guide,
            "message": f"Aucun guide spécifique trouvé pour {type_guide}",
            "suggestion": "Utilisez le générateur IA via POST /maison/fiche-tache-ia",
        }


# ═══════════════════════════════════════════════════════════
# FACTORY
# ═══════════════════════════════════════════════════════════


@service_factory("fiche_tache", tags={"maison"})
def obtenir_fiche_tache_service(client: ClientIA | None = None) -> FicheTacheService:
    """Factory singleton pour le service fiches tâches."""
    return FicheTacheService(client=client)


def obtenir_service_fiche_tache(client: ClientIA | None = None) -> FicheTacheService:
    """Alias français."""
    return get_fiche_tache_service(client)


# ─── Aliases rétrocompatibilité  ───────────────────────────────
get_fiche_tache_service = obtenir_fiche_tache_service  # alias rétrocompatibilité 
