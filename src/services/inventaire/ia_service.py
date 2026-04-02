"""
Service IA pour la gestion intelligente de l'inventaire.

Déplacé depuis les services partagés vers la couche services dédiée.
"""

from datetime import datetime, timedelta
from typing import Optional
from pydantic import BaseModel, Field

from src.core.ai import obtenir_client_ia
from src.services.core.base import BaseAIService
from src.services.core.registry import service_factory


# ── Modèles Pydantic pour structures IA ──


class PredictionConsommation(BaseModel):
    """Prédiction de consommation pour un ingrédient"""

    ingredient_nom: str = Field(..., description="Nom de l'ingrédient")
    consommation_hebdo_kg: float = Field(..., ge=0, description="Kg consommés par semaine")
    stock_actuel_kg: float = Field(..., ge=0, description="Stock actuel en kg")
    jours_autonomie: int = Field(..., ge=0, description="Jours avant rupture de stock")
    seuil_reapprovisionnement_kg: float = Field(
        ..., ge=0, description="Seuil recommandé pour réapprovisionner"
    )
    raison: str = Field(..., description="Explication courte du calcul")


class ScoreRotationFIFO(BaseModel):
    """Score d'optimalité de rotation FIFO"""

    ingredient_nom: str = Field(..., description="Nom de l'ingrédient")
    date_expiration: datetime = Field(..., description="Date d'expiration")
    jours_avant_expiration: int = Field(..., ge=0, description="Jours avant expiration")
    priorite_consommation: int = Field(
        ..., ge=1, le=5, description="1=urgent (proche expiration), 5=pas urgent"
    )
    recommandation: str = Field(..., description="Recommandation de consommation")


class InventaireAIService(BaseAIService):
    """
    Service IA pour la gestion intelligente de l'inventaire.

    Fonctionnalités:
    - Prédiction de consommation basée sur l'historique
    - Calcul de seuils de réapprovisionnement intelligents
    - Suggestions de rotation FIFO optimale
    - Alertes stock critique
    - Analyse des patterns de consommation
    """

    def __init__(self):
        super().__init__(
            client=obtenir_client_ia(),
            cache_prefix="inventaire",
            default_ttl=3600,  # 1h cache
            service_name="inventaire_ia",
        )

    async def predire_consommation(
        self,
        ingredient_nom: str,
        stock_actuel_kg: float,
        historique_achat_mensuel: list[dict],
    ) -> PredictionConsommation:
        """
        Prédit la consommation basée sur l'historique.

        Args:
            ingredient_nom: Nom de l'ingrédient
            stock_actuel_kg: Stock actuel en kg
            historique_achat_mensuel: Liste des achats [{"date": "2026-01-15", "quantite_kg": 2.5}, ...]

        Returns:
            PredictionConsommation avec jours d'autonomie et seuil recommandé
        """
        # Calculer la moyenne de consommation sur les 3 derniers mois
        if historique_achat_mensuel:
            total_kg = sum(h.get("quantite_kg", 0) for h in historique_achat_mensuel[-12:])
            nb_mois = min(len(historique_achat_mensuel[-12:]), 12)
            consommation_mensuelle_kg = total_kg / max(nb_mois, 1)
        else:
            consommation_mensuelle_kg = 1.0  # Default fallback

        consommation_hebdo_kg = consommation_mensuelle_kg / 4.3

        # IA confirme et ajuste si besoin
        prompt = f"""Analyse la consommation de {ingredient_nom}:
- Stock actuel: {stock_actuel_kg} kg
- Consommation estimée: {consommation_hebdo_kg:.2f} kg/semaine
- Historique: {len(historique_achat_mensuel)} achats des 12 derniers mois

Propose:
1. Consommation réelle (ajustée si pattern anomal)
2. Jours avant rupture
3. Seuil de réapprovisionnement (= 3x consommation hebdo minimum)
4. Raison courte"""

        result = await self.call_with_dict_parsing_sync(
            prompt=prompt,
            system_prompt="Tu es expert en gestion des stocks alimentaires.",
        )

        return PredictionConsommation(
            ingredient_nom=ingredient_nom,
            consommation_hebdo_kg=float(result.get("consommation_hebdo_kg", consommation_hebdo_kg)),
            stock_actuel_kg=stock_actuel_kg,
            jours_autonomie=int(
                (stock_actuel_kg / max(consommation_hebdo_kg, 0.01)) * 7 if consommation_hebdo_kg > 0 else 999
            ),
            seuil_reapprovisionnement_kg=float(result.get("seuil_kg", consommation_hebdo_kg * 3)),
            raison=result.get("raison", "Calcul basé sur historique"),
        )

    async def analyse_rotation_fifo(
        self, ingredients_peremption: list[dict]
    ) -> list[ScoreRotationFIFO]:
        """
        Analyse la rotation FIFO optimale.

        Args:
            ingredients_peremption: Liste [{"nom": "tomate", "date_exp": "2026-02-28"}, ...]

        Returns:
            Liste de ScoreRotationFIFO trié par priorité de consommation
        """
        if not ingredients_peremption:
            return []

        maintenant = datetime.now()
        prompt = f"""Analyse la priorité de consommation pour cette rotation FIFO:
Ingrédients à consommer:
{chr(10).join(f"- {ing['nom']} (expire: {ing['date_exp']})" for ing in ingredients_peremption)}

Pour chaque ingrédient, propose:
1. Jours avant expiration
2. Priorité (1=urgent/rouge, 5=prévu/vert)
3. Recommandation d'utilisation

Format: JSON liste"""

        recommendations = await self.call_with_list_parsing_sync(
            prompt=prompt,
            item_model=ScoreRotationFIFO,
            system_prompt="Tu es expert en gestion des périssables. Réponds en JSON structuré.",
        )

        # Trier par priorité décroissante (urgent d'abord)
        return sorted(recommendations, key=lambda x: -x.priorite_consommation)

    async def suggerer_alerte_stock(
        self,
        articles_bas_stock: list[dict],
        budget_courses_proche: bool = False,
    ) -> str:
        """
        Suggère des alertes intelligentes de réapprovisionnement.

        Args:
            articles_bas_stock: [{"nom": "lait", "stock": 0.5, "seuil": 2}, ...]
            budget_courses_proche: True si les courses prévues prochainement

        Returns:
            Message d'alerte personnalisé
        """
        prompt = f"""Génère une alerte stock intelligente pour:
Articles bas:
{chr(10).join(f"- {a['nom']}: {a['stock']}L/{a['seuil']}L min" for a in articles_bas_stock)}

Courses planifiées: {'Oui, dans 2-3 jours' if budget_courses_proche else 'Non, urgence peut-être'}

Message court (1-2 lignes) qui décrit l'urgence et propose une action."""

        return await self.call_with_cache(
            prompt=prompt,
            system_prompt="Tu es assistant de gestion de maison. Sois informatif mais bref.",
            max_tokens=200,
        )

    def stream_prediction_consommation(
        self,
        ingredient_nom: str,
        stock_actuel_kg: float,
        historique_achat_mensuel: list[dict],
    ):
        """
        Stream de prédiction de consommation.
        """
        if historique_achat_mensuel:
            total_kg = sum(h.get("quantite_kg", 0) for h in historique_achat_mensuel[-12:])
            nb_mois = min(len(historique_achat_mensuel[-12:]), 12)
            consommation_mensuelle_kg = total_kg / max(nb_mois, 1)
        else:
            consommation_mensuelle_kg = 1.0

        consommation_hebdo_kg = consommation_mensuelle_kg / 4.3

        prompt = f"""Analyse la consommation de {ingredient_nom}:
- Stock actuel: {stock_actuel_kg} kg
- Consommation estimée: {consommation_hebdo_kg:.2f} kg/semaine
- Historique: {len(historique_achat_mensuel)} achats

Propose consommation réelle, jours avant rupture et seuil réappro."""

        return self.call_with_streaming_sync(
            prompt=prompt,
            system_prompt="Tu es expert en gestion des stocks alimentaires.",
            max_tokens=400,
        )


@service_factory("inventaire_ia", tags={"inventaire", "ia", "cuisine"})
def get_inventaire_ai_service() -> InventaireAIService:
    """Factory pour le service IA inventaire."""
    return InventaireAIService()
