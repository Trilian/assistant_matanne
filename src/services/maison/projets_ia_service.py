"""
Service IA pour l'assistance aux projets maison.

Estimation complexité/timeline, budget prévisionnel, matching artisans.
"""

from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional, Literal

from src.core.ai import obtenir_client_ia
from src.services.core.base import BaseAIService
from src.services.core.registry import service_factory


# ── Modèles Pydantic ──


class EstimationProjet(BaseModel):
    """Estimation pour un projet maison"""

    projet_nom: str = Field(..., description="Nom du projet")
    complexite: Literal["simple", "moyen", "complex"] = Field(
        ..., description="Complexité estimée"
    )
    temps_jours: int = Field(..., ge=1, description="Durée estimée en jours de travail")
    est_diy: bool = Field(..., description="Peut être fait en DIY")
    competences_requises: list[str] = Field(..., description="Compétences nécessaires")
    materiaux_principaux: list[str] = Field(..., description="Matériaux à acheter")
    budget_materialisation: float = Field(..., ge=0, description="Budget matériaux estimé")
    budget_main_oeuvre: Optional[float] = Field(
        None, ge=0, description="Budget main d'oeuvre si artisan"
    )
    budget_total_min: float = Field(..., ge=0, description="Budget min total")
    budget_total_max: float = Field(..., ge=0, description="Budget max total")
    risques: list[str] = Field(..., description="Risques/pièges identifiés")
    etapes_cles: list[str] = Field(..., description="Étapes principales")
    prerequisites: list[str] = Field(..., description="Préalables (dépendances)")
    recommandations: list[str] = Field(..., description="Recommandations")


class MatchingArtisan(BaseModel):
    """Correspondance avec artisans potentiels"""

    type_metier: str = Field(..., description="Type de métier (ex: électricien, plombier)")
    specialites_requises: list[str] = Field(..., description="Spécialités nécessaires")
    certificat_recommande: Optional[str] = Field(
        None, description="Certification recommandée"
    )
    nb_references: int = Field(..., ge=0, description="Nombre de références typiques")
    criteres_selection: list[str] = Field(..., description="Critères de sélection pertinents")
    questions_entretien: list[str] = Field(..., description="Questions à poser aux artisans")


class ProjetsMaisonAIService(BaseAIService):
    """
    Service IA pour assistance aux projets maison.

    Fonctionnalités:
    - Estimation complexité/timeline
    - Budget prévisionnel (matériaux + main d'oeuvre)
    - Recommandations DIY vs artisan
    - Matching artisans adaptés
    - Risques et préalables
    - Étapes et planification
    """

    def __init__(self):
        super().__init__(
            client=obtenir_client_ia(),
            cache_prefix="projets_maison",
            default_ttl=7200,
            service_name="projets_maison_ia",
        )

    async def estimer_projet(
        self,
        projet_description: str,
        surface_m2: Optional[float] = None,
        type_maison: str = "maison_2020",  # "maison_ancien", "maison_2020", "appart"
        contraintes: list[str] = None,
    ) -> EstimationProjet:
        """
        Estime complexité, budget, timeline pour un projet.

        Args:
            projet_description: Description détaillée du projet
            surface_m2: Surface concernée si applicable
            type_maison: Type d'habitation
            contraintes: Contraintes spéciales

        Returns:
            EstimationProjet avec détails complets
        """
        surface_str = f", Surface: {surface_m2}m²" if surface_m2 else ""
        contraintes_str = f", Contraintes: {', '.join(contraintes)}" if contraintes else ""

        prompt = f"""Estime ce projet maison:
{projet_description}{surface_str}
Type maison: {type_maison}{contraintes_str}

Fournis:
1. Complexité (simple/moyen/complex)
2. Temps estimé (jours de travail)
3. Est-ce DIY possible?
4. Compétences requises
5. Matériaux principaux à acheter
6. Budget matériaux (min-max)
7. Budget main d'oeuvre si artisan (min-max)
8. Budget TOTAL (min-max)
9. Risques/pièges à éviter
10. Étapes clés de réalisation
11. Préalables/dépendances
12. Recommandations

Format JSON détaillé."""

        result = await self.call_with_dict_parsing(
            prompt=prompt,
            system_prompt="Tu es expert en rénovation maison (15+ ans expérience). Sois réaliste dans estimations.",
        )

        return EstimationProjet(
            projet_nom=projet_description.split("\n")[0][:50],
            complexite=result.get("complexite", "moyen"),
            temps_jours=int(result.get("temps_jours", 5)),
            est_diy=result.get("est_diy", True),
            competences_requises=result.get("competences_requises", []),
            materiaux_principaux=result.get("materiaux_principaux", []),
            budget_materialisation=float(result.get("budget_materialisation", 500)),
            budget_main_oeuvre=float(result.get("budget_main_oeuvre") or 0) if result.get("budget_main_oeuvre") else None,
            budget_total_min=float(result.get("budget_total_min", 500)),
            budget_total_max=float(result.get("budget_total_max", 2000)),
            risques=result.get("risques", []),
            etapes_cles=result.get("etapes_cles", []),
            prerequisites=result.get("prerequisites", []),
            recommandations=result.get("recommandations", []),
        )

    async def plannifier_projet(
        self,
        projet_description: str,
        date_debut: str,
        delai_jours: int,
        disponibilite_hebdo: int = 10,  # heures/semaine
    ) -> str:
        """
        Crée un plan d'exécution détaillé.

        Args:
            projet_description: Description du projet
            date_debut: Date de démarrage (YYYY-MM-DD)
            delai_jours: Délai pour terminer
            disponibilite_hebdo: Heures/semaine disponibles

        Returns:
            Plan d'exécution détaillé avec timeline
        """
        prompt = f"""Planifie ce projet:
{projet_description}

Paramètres:
- Date de démarrage: {date_debut}
- Délai max: {delai_jours} jours
- Disponibilité: {disponibilite_hebdo}h/semaine

Propose:
1. Chronologie semaine par semaine
2. Tâches pour chaque semaine
3. Points de contrôle/validation
4. Facteurs critique à surveiller
5. Plans B si retard

Sois réaliste sur la faisabilité."""

        return await self.call_with_cache(
            prompt=prompt,
            system_prompt="Tu es project manager en rénovation. Crée des plans réalistes.",
            max_tokens=1000,
        )

    async def consiller_diy_vs_artisan(
        self,
        projet_description: str,
        competences_diy: list[str] = None,
        temps_disponible: int = 20,  # heures/semaine
        budget_main_oeuvre_max: float = 5000,
    ) -> dict:
        """
        Conseille DIY vs artisan.

        Args:
            projet_description: Description du projet
            competences_diy: Compétences possédées
            temps_disponible: Heures/semaine disponibles
            budget_main_oeuvre_max: Budget max pour artisan

        Returns:
            Recommandation détaillée DIY vs artisan
        """
        competences_str = f"Compétences: {', '.join(competences_diy)}" if competences_diy else ""

        prompt = f"""Conseille DIY vs Artisan pour:
{projet_description}
{competences_str}
Temps dispo: {temps_disponible}h/semaine
Budget artisan max: {budget_main_oeuvre_max}€

Analyse:
1. Faisabilité DIY (%)
2. Temps total DIY vs artisan
3. Budget total DIY vs artisan
4. Risques DIY
5. Qualité DIY vs pro
6. Recommandation finale
7. Si artisan: type à chercher
8. Si DIY: tuto/ressources recommandées

Format JSON."""

        result = await self.call_with_dict_parsing(
            prompt=prompt,
            system_prompt="Tu es neutre entre DIY et artisan. Conseille au mieux des intérêts.",
        )

        return result

    async def matcher_artisans(
        self,
        type_travaux: str,
        projet_specificicites: Optional[str] = None,
    ) -> MatchingArtisan:
        """
        Tire le profil idéal de l'artisan.

        Args:
            type_travaux: Type (électricité, plomberie, maçon, etc)
            projet_specificicites: Détails spécifiques

        Returns:
            MatchingArtisan avec critères de sélection
        """
        prompt = f"""Profile l'artisan idéal pour:
Type: {type_travaux}
Spécificités: {projet_specificicites or 'générique'}

Fournis:
1. Type de métier/statut
2. Spécialités essentielles
3. Certification recommandée (RGE, Qualibat, etc)
4. Nombre de références à demander
5. Critères de sélection importants
6. Questions à poser lors entretien

Format JSON."""

        result = await self.call_with_dict_parsing(
            prompt=prompt,
            system_prompt="Tu es expert en sélection artisans. Fournis critères pertinents.",
        )

        return MatchingArtisan(
            type_metier=result.get("type_metier", type_travaux),
            specialites_requises=result.get("specialites_requises", []),
            certificat_recommande=result.get("certificat_recommande"),
            nb_references=int(result.get("nb_references", 3)),
            criteres_selection=result.get("criteres_selection", []),
            questions_entretien=result.get("questions_entretien", []),
        )

    async def evaluer_devis(
        self,
        type_travaux: str,
        devis_montant: float,
        description_travaux: str,
        prix_materialisation_estime: float,
    ) -> dict:
        """
        Évalue la pertinence d'un devis.

        Args:
            type_travaux: Type de travaux
            devis_montant: Montant du devis
            description_travaux: Détails des travaux
            prix_materialisation_estime: Prix estimé des matériaux

        Returns:
            Évaluation du devis (fair/expensive/cheap)
        """
        prompt = f"""Évalue ce devis:
Type: {type_travaux}
Montant: {devis_montant}€
Détails: {description_travaux}
Matériaux estimés: {prix_materialisation_estime}€

Analyse:
1. Main d'oeuvre: {devis_montant - prix_materialisation_estime}€
2. Est-ce juste/cher/bon marché?
3. Comparaison secteur
4. Éléments à vérifier
5. Recommandation (accepter/négocier/refuser)

Format JSON."""

        result = await self.call_with_dict_parsing(
            prompt=prompt,
            system_prompt="Tu es expert prix secteur BTP. Sois factuel dans comparaisons.",
        )

        return result

    def stream_estimation_projet(
        self,
        projet_description: str,
        surface_m2: Optional[float] = None,
    ):
        """Stream d'estimation détaillée."""
        prompt = f"""Estime ce projet:
{projet_description}
{f'Surface: {surface_m2}m²' if surface_m2 else ''}

Complexité, timeline, budget, DIY possible, risques, étapes, recommandations."""

        return self.call_with_streaming_sync(
            prompt=prompt,
            system_prompt="Tu es expert rénovation.",
            max_tokens=800,
        )


@service_factory("projets_maison_ia", tags={"maison", "projets", "ia"})
def get_projets_maison_ai_service() -> ProjetsMaisonAIService:
    """Factory pour le service projets maison."""
    return ProjetsMaisonAIService()
