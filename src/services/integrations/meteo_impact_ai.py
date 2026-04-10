"""
Service IA pour l'analyse météo cross-module.

Crée des connexions intelligentes entre météo et:
- Jardin (semis, récoltes, protection)
- Activités familiales (intérieur/extérieur)
- Recettes (produits de saison, conservation)
- Énergie (prédictions chauffage/climat)
- Entretien maison (tâches adaptées)
"""

from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field

from src.core.ai import obtenir_client_ia
from src.services.core.base import BaseAIService
from src.services.core.registry import service_factory

# ── Modèles Pydantic ──


class ImpactMeteo(BaseModel):
    """Impact météo sur un domaine"""

    domaine: str = Field(
        ..., description="Domaine affecté (jardin/activités/cuisine/énergie/entretien)"
    )
    type_impact: str = Field(..., description="Type d'impact")
    severite: Literal["faible", "moyen", "important"] = Field(
        ..., description="Sévérité de l'impact"
    )
    recommandation: str = Field(..., description="Recommandation d'action")
    urgence: bool = Field(..., description="True si action urgente")


class MeteoContexte(BaseModel):
    """Contexte météo enrichi"""

    date: str = Field(..., description="Date de prévision (YYYY-MM-DD)")
    conditions: str = Field(..., description="Conditions générales (ex: pluie, soleil, mixte)")
    temperature_min: float = Field(..., description="Température min en °C")
    temperature_max: float = Field(..., description="Température max en °C")
    humidite: int = Field(..., ge=0, le=100, description="Humidité en %")
    chance_pluie: int = Field(..., ge=0, le=100, description="% de chance de pluie")
    vent_km_h: float = Field(..., ge=0, description="Vitesse vent")
    impacts: list[ImpactMeteo] = Field(..., description="Impacts identifiés")


class MeteoImpactAIService(BaseAIService):
    """
    Service IA pour analyse cross-module de l'impact météo.

    Connecte intelligemment météo et modules:
    - **Jardin**: semis/plantation/récolte, protection, arrosage
    - **Activités**: suggestions types loisirs (intérieur/extérieur)
    - **Cuisine**: fruits/légumes de saison, conservation
    - **Énergie**: prédictions consommation chauffage/clim
    - **Entretien**: tâches adaptées (pas de peinture par pluie, etc)
    """

    def __init__(self):
        super().__init__(
            client=obtenir_client_ia(),
            cache_prefix="meteo_impact",
            default_ttl=3600,
            service_name="meteo_impact",
        )

    async def analyser_impacts(
        self,
        previsions_7j: list[dict],
        saison: str,
    ) -> list[MeteoContexte]:
        """
        Analyse les impacts météo sur 7 jours.

        Args:
            previsions_7j: Prévisions [{"date": "2026-04-05", "conditions": "pluie", "temp_min": 8, "temp_max": 12, "humidite": 85, "chance_pluie": 80, "vent_km_h": 25}, ...]
            saison: Saison actuelle (printemps/été/automne/hiver)

        Returns:
            Analyse des impacts par jour
        """
        previsions_str = "\n".join(
            f"{p['date']}: {p['conditions']}, {p['temp_min']}-{p['temp_max']}°C, "
            f"pluie {p['chance_pluie']}%, vent {p['vent_km_h']} km/h"
            for p in previsions_7j
        )

        prompt = f"""Analyse météo sur 7 jours - Saison: {saison}

Prévisions:
{previsions_str}

Pour chaque jour, identifie les impacts sur:
1. **Jardin**: semis/plantation/récolte/protection/arrosage
2. **Activités**: suggestions loisirs (intérieur/extérieur possible?)
3. **Cuisine**: fruits/légumes de saison, conservation
4. **Énergie**: impact consommation chauffage/clim
5. **Entretien**: tâches adaptées (ex: pas de peinture par pluie)

Format JSON par jour avec: conditions, temp min/max, humidité, %pluie, vent, impacts[]."""

        result = await self.call_with_list_parsing(
            prompt=prompt,
            item_model=MeteoContexte,
            system_prompt="Tu es expert météo appliquée aux activités familiales et jardin. Sois spécifique et actionnable.",
        )

        return result

    async def suggerer_activites_meteo(
        self,
        date: str,
        conditions: str,
        temperature: tuple[float, float],  # (min, max)
        public: str = "famille",  # "enfants", "adultes", "famille"
        budget: float | None = None,
    ) -> str:
        """
        Suggère des activités adaptées à la météo.

        Args:
            date: Date (YYYY-MM-DD)
            conditions: Conditions (pluie, soleil, nuageux, mixte, tempête)
            temperature: Tuple (min, max) en °C
            public: Type public (enfants/adultes/famille)
            budget: Budget max en euros

        Returns:
            Suggé de 3-5 activités adaptées
        """
        budget_str = f", budget max {budget}€" if budget else ""

        prompt = f"""Suggère des activités pour {public} le {date}:
Météo: {conditions}, {temperature[0]}-{temperature[1]}°C{budget_str}

Critères:
- Adaptées aux conditions (pluie → intérieur, soleil → extérieur possible)
- Adaptées à la température
- Amusantes et stimulantes
- Réalisables facilement

Format: "🎯 Activité 1 (25 min, intérieur)\n📝 Description..."."""

        return await self.call_with_cache(
            prompt=prompt,
            system_prompt="Tu es expert en loisirs familiaux. Sois créatif et pratique.",
            max_tokens=500,
        )

    async def conseil_jardin_meteo(
        self,
        date: str,
        conditions: str,
        humidite: int,
        temperature: tuple[float, float],
        phase_jardin: str = "mixte",  # "semis", "croissance", "récolte", "mixte"
    ) -> str:
        """
        Donne des conseils jardin adaptés à la météo.

        Args:
            date: Date
            conditions: Conditions
            humidite: % humidité (0-100)
            temperature: (min, max) en °C
            phase_jardin: Stade de croissance

        Returns:
            Conseils jardin pratiques
        """
        prompt = f"""Conseil jardin pour le {date}:
Météo: {conditions}, {temperature[0]}-{temperature[1]}°C, humidité {humidite}%
Phase: {phase_jardin}

Propose:
1. Tâches adaptées (arrosage, semis, récolte, protection)
2. Timing optimal (matin/après-midi)
3. Précautions à prendre
4. Éléments à surveiller

Sois détaillé et pratique."""

        return await self.call_with_cache(
            prompt=prompt,
            system_prompt="Tu es maraîcher expert. Adapte conseils à la météo locale.",
            max_tokens=400,
        )

    async def predire_consommation_energie(
        self,
        previsions_7j: list[dict],
        type_chauffage: str = "pompe_chaleur",  # "radiateurs", "clim", "pompe_chaleur", "mixte"
    ) -> dict:
        """
        Prédit consommation énergétique basée sur météo.

        Args:
            previsions_7j: Prévisions météo
            type_chauffage: Type de système (radiateurs/clim/pompe_chaleur/mixte)

        Returns:
            Prédictions consommation et recommandations
        """
        previsions_str = "\n".join(
            f"{p['date']}: {p['temp_min']}-{p['temp_max']}°C" for p in previsions_7j
        )

        prompt = f"""Prédit consommation énergie pour {type_chauffage}:

Prévisions:
{previsions_str}

Estime:
1. % variation consommation chauffage par jour
2. Jours avec pics probables
3. Recommandations optimisation
4. Heures creuses à privilégier

Format JSON."""

        result = await self.call_with_dict_parsing(
            prompt=prompt,
            system_prompt="Tu es expert efficacité énergétique. Sois précis dans estimations.",
        )

        return result

    def stream_impacts_detailles(
        self,
        date: str,
        conditions: str,
        temperature: tuple[float, float],
        saison: str,
    ):
        """Stream détails des impacts pour un jour."""
        prompt = f"""Analyse détaillée des impacts pour {date}:
Conditions: {conditions}, {temperature[0]}-{temperature[1]}°C
Saison: {saison}

Impacts sur: jardin, activités, cuisine, énergie, entretien."""

        return self.call_with_streaming_sync(
            prompt=prompt,
            system_prompt="Tu es expert météo appliquée.",
            max_tokens=600,
        )


@service_factory("meteo_impact", tags={"meteo", "ia", "core", "cross-module"})
def get_meteo_impact_ai_service() -> MeteoImpactAIService:
    """Factory pour le service météo impact."""
    return MeteoImpactAIService()
