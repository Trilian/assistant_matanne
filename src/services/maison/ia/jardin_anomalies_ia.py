"""
Service IA pour la détection d'anomalies au jardin.

Analyse l'historique des plantes et les conditions météo pour
détecter précocement des problèmes (maladies, stress hydrique, etc.).
"""

from __future__ import annotations

import logging
from typing import Any

from pydantic import BaseModel, Field

from src.services.core.base import BaseAIService
from src.services.core.registry import service_factory

logger = logging.getLogger(__name__)


class AnomalieJardin(BaseModel):
    """Anomalie détectée dans le jardin."""

    plante: str = Field("", description="Nom de la plante concernée")
    type_anomalie: str = Field(
        "", description="Type : maladie, stress_hydrique, carence, nuisible, gel"
    )
    severite: str = Field("faible", description="Sévérité : faible, moyenne, elevee")
    description: str = Field("", description="Description du problème détecté")
    action_recommandee: str = Field("", description="Action corrective recommandée")


class AnomaliesJardinResponse(BaseModel):
    """Réponse complète d'analyse des anomalies jardin."""

    anomalies: list[AnomalieJardin] = Field(default_factory=list)
    recommandations_generales: list[str] = Field(default_factory=list)
    score_sante_jardin: float = Field(0.0, ge=0.0, le=100.0, description="Score santé global 0-100")


class JardinAnomaliesIAService(BaseAIService):
    """Service de détection d'anomalies au jardin via IA."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(
            cache_prefix="jardin_anomalies",
            default_ttl=7200,
            default_temperature=0.4,
            service_name="jardin_anomalies_ia",
            **kwargs,
        )

    def detecter_anomalies(
        self,
        plantes: list[dict[str, Any]],
        meteo_recente: list[dict[str, Any]] | None = None,
        saison: str = "",
    ) -> AnomaliesJardinResponse:
        """Détecte les anomalies potentielles dans le jardin.

        Args:
            plantes: Liste des plantes avec leur état (nom, date_plantation, arrosage, état).
            meteo_recente: Données météo récentes (température, pluie, vent).
            saison: Saison actuelle (printemps, ete, automne, hiver).

        Returns:
            AnomaliesJardinResponse avec anomalies détectées et recommandations.
        """
        if not plantes:
            return AnomaliesJardinResponse(
                score_sante_jardin=100.0,
                recommandations_generales=["Aucune plante enregistrée dans le jardin."],
            )

        # Construire le contexte
        plantes_desc = "\n".join(
            f"- {p.get('nom', 'Inconnue')} : planté le {p.get('date_plantation', '?')}, "
            f"état: {p.get('etat', 'normal')}, arrosage: {p.get('frequence_arrosage', '?')}"
            for p in plantes[:20]
        )

        meteo_desc = ""
        if meteo_recente:
            meteo_desc = "\nMétéo récente :\n" + "\n".join(
                f"- {m.get('date', '?')} : {m.get('temperature_min', '?')}°C-{m.get('temperature_max', '?')}°C, "
                f"pluie: {m.get('pluie_mm', 0)}mm"
                for m in meteo_recente[:7]
            )

        prompt = f"""Analyse l'état de ce jardin familial et détecte les anomalies potentielles.

Saison : {saison or "non précisée"}

Plantes :
{plantes_desc}
{meteo_desc}

Pour chaque anomalie détectée, précise :
- La plante concernée
- Le type (maladie, stress_hydrique, carence, nuisible, gel)
- La sévérité (faible, moyenne, elevee)
- Une description courte
- L'action corrective recommandée

Évalue aussi un score de santé global du jardin (0-100).

Réponds en JSON :
{{
  "anomalies": [{{"plante": "...", "type_anomalie": "...", "severite": "...", "description": "...", "action_recommandee": "..."}}],
  "recommandations_generales": ["..."],
  "score_sante_jardin": 85.0
}}"""

        system_prompt = (
            "Tu es un expert en jardinage et botanique. "
            "Tu analyses l'état des plantes et les conditions météo "
            "pour détecter précocement les problèmes. "
            "Privilégie les traitements naturels et biologiques. "
            "Réponds uniquement en JSON valide."
        )

        result = self.call_with_parsing_sync(
            prompt=prompt,
            response_model=AnomaliesJardinResponse,
            system_prompt=system_prompt,
            temperature=0.4,
            use_cache=True,
        )

        if result is None:
            return AnomaliesJardinResponse(
                score_sante_jardin=50.0,
                recommandations_generales=["Analyse indisponible temporairement."],
            )

        return result


@service_factory("jardin_anomalies_ia", tags={"ia", "maison", "jardin"})
def get_jardin_anomalies_ia_service() -> JardinAnomaliesIAService:
    """Factory pour le service de détection d'anomalies jardin."""
    return JardinAnomaliesIAService()
