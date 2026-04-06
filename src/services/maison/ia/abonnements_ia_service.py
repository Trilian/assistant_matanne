"""
Service IA pour la comparaison et l'analyse des abonnements maison.
"""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field

from src.core.ai import obtenir_client_ia
from src.services.core.base import BaseAIService
from src.services.core.registry import service_factory


class ConseilAbonnement(BaseModel):
    """Conseil IA sur un abonnement ou une piste d'économie."""

    titre: str = Field(..., description="Titre court du conseil")
    detail: str = Field(..., description="Explication détaillée")
    economies_estimees_eur: Optional[float] = Field(None, ge=0, description="Économies estimées par mois")
    priorite: str = Field(..., description="haute | moyenne | basse")
    categorie: str = Field(..., description="Type de contrat concerné")


class AbonnementsIAService(BaseAIService):
    """Analyse IA des abonnements maison et pistes d'optimisation."""

    def __init__(self) -> None:
        super().__init__(
            client=obtenir_client_ia(),
            cache_prefix="abonnements_ia",
            default_ttl=3600,  # 1h
            service_name="abonnements_ia",
        )

    def comparer_abonnements(
        self,
        abonnements: list[dict],
        total_mensuel: float,
    ) -> dict:
        """
        Analyse les abonnements actuels et propose des pistes de réduction.

        Args:
            abonnements: Liste des abonnements actuels (type, fournisseur, prix_mensuel)
            total_mensuel: Coût mensuel total actuel

        Returns:
            Rapport avec conseils, économies estimées et contrats à renégocier
        """
        if not abonnements:
            return {"conseils": [], "economies_potentielles_eur": 0, "resume": "Aucun abonnement à analyser."}

        liste_txt = "\n".join(
            f"- {a.get('type_abonnement', 'inconnu')} ({a.get('fournisseur', 'N/A')}): "
            f"{a.get('prix_mensuel', 0):.2f} €/mois"
            for a in abonnements[:20]
        )

        cache_key = f"compare_{int(total_mensuel)}_{len(abonnements)}"
        prompt = (
            f"Tu es un expert en comparaison de contrats et abonnements domestiques en France.\n"
            f"Abonnements actuels (total: {total_mensuel:.2f} €/mois):\n{liste_txt}\n\n"
            f"Identifie 3 à 5 pistes concrètes d'économies ou de renégociation. "
            f"Réponds UNIQUEMENT en JSON strict (sans markdown) avec:\n"
            f'{{"conseils": [{{"titre": "...", "detail": "...", "economies_estimees_eur": 10.0, "priorite": "haute|moyenne|basse", "categorie": "..."}}], '
            f'"economies_potentielles_eur": 25.0, "resume": "phrase synthèse"}}'
        )

        conseils = self.call_with_list_parsing_sync(
            prompt=prompt,
            item_model=ConseilAbonnement,
            system_prompt="Tu es un expert en contrats domestiques français. Réponds uniquement en JSON valide.",
            temperature=0.3,
            max_tokens=1500,
            cache_key=cache_key,
        )

        economies = sum(c.economies_estimees_eur or 0 for c in conseils)
        return {
            "conseils": [c.model_dump() for c in conseils],
            "economies_potentielles_eur": round(economies, 2),
            "resume": f"{len(conseils)} conseil(s) — jusqu'à {economies:.0f} €/mois d'économies potentielles.",
        }


@service_factory("abonnements_ia", tags={"maison", "abonnements", "ia"})
def obtenir_service_abonnements_ia() -> AbonnementsIAService:
    """Retourne le service IA de comparaison d'abonnements."""
    return AbonnementsIAService()
