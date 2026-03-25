"""
Service IA pour l'analyse du budget familial.

Prédictions, détection d'anomalies et suggestions d'économies
via Mistral AI.
"""

from pydantic import BaseModel, Field

from src.core.ai import obtenir_client_ia
from src.services.core.base import BaseAIService
from src.services.core.registry import service_factory


# ── Modèles Pydantic pour réponses structurées ──


class PredictionCategorie(BaseModel):
    """Prédiction pour une catégorie de dépenses."""

    categorie: str = Field(..., description="Nom de la catégorie")
    montant_prevu: float = Field(..., ge=0, description="Montant prévu en euros")
    tendance: str = Field(
        ..., description="Tendance: hausse, baisse ou stable"
    )
    explication: str = Field(..., description="Explication courte de la tendance")


class PredictionBudget(BaseModel):
    """Prédiction budgétaire mensuelle complète."""

    total_prevu: float = Field(..., ge=0, description="Total prévu pour le mois")
    par_categorie: list[PredictionCategorie] = Field(
        default_factory=list, description="Prédictions par catégorie"
    )
    confiance: float = Field(
        ..., ge=0, le=1, description="Indice de confiance (0-1)"
    )
    resume: str = Field(..., description="Résumé textuel de la prédiction")


class AnomalieBudget(BaseModel):
    """Anomalie détectée dans les dépenses."""

    type: str = Field(..., description="Type: pic, baisse, nouvelle_categorie, irregularite")
    categorie: str = Field(..., description="Catégorie concernée")
    ecart_pourcent: float = Field(..., description="Écart en pourcentage vs moyenne")
    severite: str = Field(..., description="Sévérité: info, warning, danger")
    description: str = Field(..., description="Description de l'anomalie")


class SuggestionEconomie(BaseModel):
    """Suggestion d'économie basée sur l'analyse."""

    titre: str = Field(..., description="Titre court de la suggestion")
    description: str = Field(..., description="Description détaillée du conseil")
    economie_estimee: float = Field(..., ge=0, description="Économie mensuelle estimée en euros")
    categorie: str = Field(..., description="Catégorie de dépense visée")
    difficulte: str = Field(..., description="Difficulté: facile, moyen, difficile")


class BudgetAIService(BaseAIService):
    """Service IA pour l'analyse prédictive du budget familial."""

    def __init__(self):
        super().__init__(
            client=obtenir_client_ia(),
            cache_prefix="budget_ai",
            default_ttl=3600,
            service_name="budget_ai",
        )

    def predire_budget_mensuel(
        self,
        historique_par_mois: list[dict],
    ) -> PredictionBudget | None:
        """
        Prédit le budget du mois prochain à partir de l'historique.

        Args:
            historique_par_mois: Liste de dicts {mois, annee, total, par_categorie: {cat: montant}}
                                 pour les 6 derniers mois.

        Returns:
            PredictionBudget ou None si échec IA
        """
        if not historique_par_mois:
            return None

        historique_text = "\n".join(
            f"- {h['mois']:02d}/{h['annee']}: Total {h['total']:.2f}€ "
            f"({', '.join(f'{cat}: {m:.2f}€' for cat, m in h.get('par_categorie', {}).items())})"
            for h in historique_par_mois
        )

        prompt = f"""Analyse cet historique de dépenses familiales et prédit le budget du mois prochain.

Historique (6 derniers mois):
{historique_text}

Fournis:
- total_prevu: estimation du total pour le mois prochain
- par_categorie: liste avec pour chaque catégorie active: categorie, montant_prevu, tendance ("hausse"/"baisse"/"stable"), explication courte
- confiance: indice de confiance de 0 à 1 (basé sur la régularité des données)
- resume: 1-2 phrases résumant la prédiction et points d'attention"""

        system_prompt = """Tu es expert en analyse financière familiale.
Réponds UNIQUEMENT avec du JSON valide, sans markdown ni texte supplémentaire.
Sois réaliste et prudent dans tes prédictions. Base-toi sur les tendances observées."""

        return self.call_with_json_parsing_sync(
            prompt=prompt,
            response_model=PredictionBudget,
            system_prompt=system_prompt,
            max_tokens=1500,
        )

    def detecter_anomalies(
        self,
        depenses_mois_courant: dict,
        moyennes_historiques: dict,
    ) -> list[AnomalieBudget]:
        """
        Détecte les anomalies dans les dépenses du mois courant.

        Args:
            depenses_mois_courant: {categorie: montant} pour le mois en cours
            moyennes_historiques: {categorie: montant_moyen} sur les mois précédents

        Returns:
            Liste d'anomalies détectées
        """
        if not depenses_mois_courant:
            return []

        courant_text = "\n".join(
            f"- {cat}: {m:.2f}€" for cat, m in depenses_mois_courant.items()
        )
        moyennes_text = "\n".join(
            f"- {cat}: {m:.2f}€ (moyenne)" for cat, m in moyennes_historiques.items()
        )

        prompt = f"""Compare les dépenses du mois en cours avec les moyennes historiques et détecte les anomalies.

Dépenses mois en cours:
{courant_text}

Moyennes historiques:
{moyennes_text}

Pour chaque anomalie détectée, fournis:
- type: "pic" (dépense anormalement haute), "baisse" (dépense anormalement basse), "nouvelle_categorie" (catégorie absente de l'historique), "irregularite" (pattern inhabituel)
- categorie: catégorie concernée
- ecart_pourcent: écart en pourcentage par rapport à la moyenne (positif=hausse, négatif=baisse)
- severite: "info" (écart < 20%), "warning" (écart 20-50%), "danger" (écart > 50%)
- description: explication courte et actionnable

Ne remonte que les anomalies significatives (écart > 15%)."""

        system_prompt = """Tu es expert en détection d'anomalies financières familiales.
Réponds UNIQUEMENT avec du JSON valide, sans markdown ni texte supplémentaire.
Sois précis sur les écarts et pragmatique dans les descriptions."""

        return self.call_with_list_parsing_sync(
            prompt=prompt,
            item_model=AnomalieBudget,
            system_prompt=system_prompt,
            max_tokens=1500,
        )

    def suggerer_economies(
        self,
        depenses_par_categorie: dict,
        total_mensuel: float,
    ) -> list[SuggestionEconomie]:
        """
        Suggère des pistes d'économies basées sur le profil de dépenses.

        Args:
            depenses_par_categorie: {categorie: montant_mensuel_moyen}
            total_mensuel: total moyen mensuel

        Returns:
            Liste de suggestions d'économies
        """
        if not depenses_par_categorie:
            return []

        depenses_text = "\n".join(
            f"- {cat}: {m:.2f}€/mois ({m / total_mensuel * 100:.0f}% du total)"
            for cat, m in sorted(depenses_par_categorie.items(), key=lambda x: -x[1])
        )

        prompt = f"""Analyse ce profil de dépenses familiales et suggère 3-5 pistes d'économies concrètes.

Dépenses moyennes mensuelles (total: {total_mensuel:.2f}€):
{depenses_text}

Pour chaque suggestion:
- titre: titre court et accrocheur
- description: conseil concret et actionnable (2-3 phrases)
- economie_estimee: économie mensuelle réaliste en euros
- categorie: catégorie de dépense visée
- difficulte: "facile" (changement simple), "moyen" (nécessite un effort), "difficile" (changement de mode de vie)

Sois réaliste et concret. Adapte les conseils à une famille avec enfant."""

        system_prompt = """Tu es conseiller en finances familiales.
Réponds UNIQUEMENT avec du JSON valide, sans markdown ni texte supplémentaire.
Tes suggestions doivent être pratiques, réalistes et adaptées à une famille française."""

        return self.call_with_list_parsing_sync(
            prompt=prompt,
            item_model=SuggestionEconomie,
            system_prompt=system_prompt,
            max_tokens=1500,
        )


@service_factory("budget_ai", tags={"famille", "ia", "budget"})
def obtenir_budget_ai_service() -> BudgetAIService:
    """Factory singleton pour BudgetAIService."""
    return BudgetAIService()


def get_budget_ai_service() -> BudgetAIService:
    """English alias for obtenir_budget_ai_service."""
    return obtenir_budget_ai_service()
