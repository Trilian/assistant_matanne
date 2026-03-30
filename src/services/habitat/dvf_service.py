"""Service Habitat pour l'analyse de marche via les donnees DVF publiques."""

from __future__ import annotations

import logging
from datetime import datetime
from statistics import median
from typing import Any

import httpx

from src.services.core.registry import service_factory

logger = logging.getLogger(__name__)


class DVFHabitatService:
    """Interroge les ressources DVF publiees sur data.gouv pour alimenter Habitat."""

    DATASET_ID = "642205e1f2a0d0428a738699"
    DATASET_URL = f"https://www.data.gouv.fr/api/1/datasets/{DATASET_ID}"
    TABULAR_API_URL = "https://tabular-api.data.gouv.fr/api/resources/{resource_id}/data/"
    USER_AGENT = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
    )

    def __init__(self) -> None:
        self._resources_cache: list[dict[str, Any]] | None = None

    def _client(self) -> httpx.Client:
        return httpx.Client(timeout=20.0, headers={"User-Agent": self.USER_AGENT}, follow_redirects=True)

    def _coerce_float(self, value: Any) -> float | None:
        if value in (None, ""):
            return None
        if isinstance(value, (int, float)):
            return float(value)
        try:
            return float(str(value).replace(" ", "").replace(",", "."))
        except ValueError:
            return None

    def _coerce_int(self, value: Any) -> int | None:
        number = self._coerce_float(value)
        return int(number) if number is not None else None

    def _normaliser_departement(self, departement: str | None) -> str | None:
        if not departement:
            return None
        propre = departement.strip().upper()
        if len(propre) >= 3 and propre.startswith(("97", "98")):
            return propre[:3]
        return propre[:2]

    def _obtenir_resources(self) -> list[dict[str, Any]]:
        if self._resources_cache is not None:
            return self._resources_cache

        try:
            with self._client() as client:
                response = client.get(self.DATASET_URL)
            response.raise_for_status()
            data = response.json()
        except Exception as exc:
            logger.warning("Impossible de charger les ressources DVF: %s", exc)
            self._resources_cache = []
            return self._resources_cache

        resources = data.get("resources") if isinstance(data, dict) else []
        self._resources_cache = [item for item in resources if isinstance(item, dict)]
        return self._resources_cache

    def _trouver_resource(self, departement: str | None) -> dict[str, Any] | None:
        departement = self._normaliser_departement(departement) or "74"
        for resource in self._obtenir_resources():
            title = str(resource.get("title") or "")
            if title.startswith(f"{departement} -"):
                return resource
        return None

    def _requete_transactions(
        self,
        resource_id: str,
        *,
        commune: str | None,
        code_postal: str | None,
        type_local: str | None,
        nb_pieces_min: int | None,
        surface_min_m2: float | None,
        limite: int,
    ) -> list[dict[str, Any]]:
        params: dict[str, Any] = {
            "page_size": max(25, min(limite, 250)),
            "sort": "-date_mutation",
            "logement__exact": 1,
        }
        if commune:
            params["nom_commune__contains"] = commune
        if code_postal:
            params["code_postal__exact"] = code_postal
        if type_local:
            params["type_local__contains"] = type_local
        if nb_pieces_min:
            params["nombre_pieces_principales__greater"] = max(nb_pieces_min - 1, 0)
        if surface_min_m2:
            params["surface_reelle_bati__greater"] = max(surface_min_m2 - 1, 0)

        url = self.TABULAR_API_URL.format(resource_id=resource_id)
        try:
            with self._client() as client:
                response = client.get(url, params=params)
            response.raise_for_status()
            payload = response.json()
        except Exception as exc:
            logger.warning("Impossible de charger les transactions DVF (%s): %s", resource_id, exc)
            return []

        items = payload.get("data") if isinstance(payload, dict) else []
        return [item for item in items if isinstance(item, dict)]

    def _normaliser_transaction(self, item: dict[str, Any]) -> dict[str, Any] | None:
        date_mutation = str(item.get("date_mutation") or "")[:10]
        try:
            datetime.fromisoformat(date_mutation)
        except ValueError:
            return None

        valeur_fonciere = self._coerce_float(item.get("valeur_fonciere"))
        surface_m2 = self._coerce_float(item.get("surface_reelle_bati"))
        prix_m2 = None
        if valeur_fonciere and surface_m2 and surface_m2 > 0:
            prix_m2 = round(valeur_fonciere / surface_m2, 2)

        adresse_parts = [
            str(item.get("adresse_numero") or "").strip(),
            str(item.get("adresse_nom_voie") or "").strip(),
        ]
        adresse = " ".join(part for part in adresse_parts if part)

        return {
            "date_mutation": date_mutation,
            "valeur_fonciere": valeur_fonciere,
            "surface_m2": surface_m2,
            "prix_m2": prix_m2,
            "type_local": item.get("type_local"),
            "nb_pieces": self._coerce_int(item.get("nombre_pieces_principales")),
            "code_postal": str(item.get("code_postal") or ""),
            "commune": item.get("nom_commune") or item.get("commune"),
            "adresse": adresse or None,
        }

    def obtenir_historique_marche(
        self,
        *,
        departement: str | None = None,
        code_postal: str | None = None,
        commune: str | None = None,
        type_local: str | None = None,
        nb_pieces_min: int | None = None,
        surface_min_m2: float | None = None,
        limite: int = 180,
    ) -> dict[str, Any]:
        departement_effectif = self._normaliser_departement(departement or (code_postal[:3] if code_postal and code_postal.startswith(("97", "98")) else code_postal[:2] if code_postal else None)) or "74"
        resource = self._trouver_resource(departement_effectif)
        if not resource:
            return {
                "source": {"dataset_id": self.DATASET_ID, "resource_id": None, "resource_title": None},
                "query": {
                    "departement": departement_effectif,
                    "commune": commune,
                    "code_postal": code_postal,
                    "type_local": type_local,
                },
                "resume": {"nb_transactions": 0},
                "historique": [],
                "repartition_types": [],
                "transactions": [],
            }

        transactions_brutes = self._requete_transactions(
            str(resource.get("id")),
            commune=commune,
            code_postal=code_postal,
            type_local=type_local,
            nb_pieces_min=nb_pieces_min,
            surface_min_m2=surface_min_m2,
            limite=limite,
        )
        transactions = [
            transaction
            for transaction in (self._normaliser_transaction(item) for item in transactions_brutes)
            if transaction is not None
        ]

        prix_m2_values = [item["prix_m2"] for item in transactions if item.get("prix_m2") is not None]
        valeurs = [item["valeur_fonciere"] for item in transactions if item.get("valeur_fonciere") is not None]
        surfaces = [item["surface_m2"] for item in transactions if item.get("surface_m2") is not None]

        buckets: dict[str, list[dict[str, Any]]] = {}
        repartition_types: dict[str, list[dict[str, Any]]] = {}
        for transaction in transactions:
            mois = transaction["date_mutation"][:7]
            buckets.setdefault(mois, []).append(transaction)
            type_name = str(transaction.get("type_local") or "Inconnu")
            repartition_types.setdefault(type_name, []).append(transaction)

        historique = []
        for mois, items in sorted(buckets.items()):
            prix_m2_mois = [item["prix_m2"] for item in items if item.get("prix_m2") is not None]
            valeurs_mois = [item["valeur_fonciere"] for item in items if item.get("valeur_fonciere") is not None]
            historique.append(
                {
                    "mois": mois,
                    "transactions": len(items),
                    "prix_m2_median": round(median(prix_m2_mois), 2) if prix_m2_mois else None,
                    "prix_m2_moyen": round(sum(prix_m2_mois) / len(prix_m2_mois), 2) if prix_m2_mois else None,
                    "valeur_moyenne": round(sum(valeurs_mois) / len(valeurs_mois), 2) if valeurs_mois else None,
                }
            )

        repartition = []
        for type_name, items in sorted(repartition_types.items(), key=lambda entry: len(entry[1]), reverse=True):
            prix_m2_type = [item["prix_m2"] for item in items if item.get("prix_m2") is not None]
            repartition.append(
                {
                    "type_local": type_name,
                    "transactions": len(items),
                    "prix_m2_median": round(median(prix_m2_type), 2) if prix_m2_type else None,
                }
            )

        dernier_point = historique[-1] if historique else None
        commune_label = commune or next((str(item.get("commune")) for item in transactions if item.get("commune")), None)
        code_postal_label = code_postal or next((str(item.get("code_postal")) for item in transactions if item.get("code_postal")), None)

        return {
            "source": {
                "dataset_id": self.DATASET_ID,
                "resource_id": resource.get("id"),
                "resource_title": resource.get("title"),
            },
            "query": {
                "departement": departement_effectif,
                "commune": commune_label,
                "code_postal": code_postal_label,
                "type_local": type_local,
                "nb_pieces_min": nb_pieces_min,
                "surface_min_m2": surface_min_m2,
            },
            "resume": {
                "nb_transactions": len(transactions),
                "prix_m2_median": round(median(prix_m2_values), 2) if prix_m2_values else None,
                "prix_m2_moyen": round(sum(prix_m2_values) / len(prix_m2_values), 2) if prix_m2_values else None,
                "valeur_mediane": round(median(valeurs), 2) if valeurs else None,
                "surface_mediane": round(median(surfaces), 2) if surfaces else None,
                "dernier_mois": dernier_point,
            },
            "historique": historique,
            "repartition_types": repartition,
            "transactions": transactions[:25],
        }


@service_factory("habitat_dvf", tags={"habitat", "dvf", "marche"})
def obtenir_service_dvf_habitat() -> DVFHabitatService:
    """Factory singleton du service DVF Habitat."""

    return DVFHabitatService()