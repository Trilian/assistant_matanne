"""
Service Jardin - Gestion intelligente du jardin avec IA.

Features:
- Conseils saisonniers et météo-adaptatifs
- Plan d'arrosage intelligent
- Diagnostic plantes via vision IA
- Alertes gel/canicule automatiques
- Suggestions plantation par saison
"""

import logging
from datetime import date, timedelta

from sqlalchemy.orm import Session

from src.core.ai import ClientIA
from src.core.database import obtenir_contexte_db
from src.core.models import GardenItem
from src.services.base import BaseAIService

from .schemas import (
    AlerteMaison,
    ConseilJardin,
    DiagnosticPlante,
    EtatPlante,
    NiveauUrgence,
    PlanArrosage,
    TypeAlerteMaison,
)

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════
# CONSTANTES
# ═══════════════════════════════════════════════════════════

SAISONS = {
    (3, 4, 5): "printemps",
    (6, 7, 8): "été",
    (9, 10, 11): "automne",
    (12, 1, 2): "hiver",
}

SEUIL_GEL = 2.0  # °C
SEUIL_CANICULE = 35.0  # °C
SEUIL_SECHERESSE_JOURS = 7  # Jours sans pluie


# ═══════════════════════════════════════════════════════════
# SERVICE JARDIN
# ═══════════════════════════════════════════════════════════


class JardinService(BaseAIService):
    """Service IA pour la gestion intelligente du jardin.

    Fonctionnalités:
    - Conseils saisonniers automatiques
    - Adaptation à la météo locale
    - Diagnostic plantes par photo
    - Planification arrosage intelligent

    Example:
        >>> service = get_jardin_service()
        >>> conseils = await service.generer_conseils_saison("printemps")
        >>> print(conseils)
    """

    def __init__(self, client: ClientIA | None = None):
        """Initialise le service jardin.

        Args:
            client: Client IA optionnel (créé automatiquement si None)
        """
        if client is None:
            client = ClientIA()
        super().__init__(
            client=client,
            cache_prefix="jardin",
            default_ttl=3600,
            service_name="jardin",
        )

    # ─────────────────────────────────────────────────────────
    # CONSEILS SAISONNIERS
    # ─────────────────────────────────────────────────────────

    async def generer_conseils_saison(self, saison: str | None = None) -> str:
        """Génère des conseils spécifiques à la saison.

        Args:
            saison: Saison (printemps, été, automne, hiver). Si None, détecte auto.

        Returns:
            Conseils formatés en texte
        """
        if saison is None:
            saison = self.get_saison_actuelle()

        prompt = f"""Tu es un expert jardinier. Donne 4-5 conseils pratiques
pour les travaux de jardinage en {saison} (maintenant).
Inclus: plantations, entretien, récoltes, préparation.
Sois concis et actionnable."""

        return await self.call_with_cache(
            prompt=prompt,
            system_prompt="Tu es un expert en jardinage bio et permaculture",
            max_tokens=600,
        )

    async def suggerer_plantes_saison(
        self, saison: str | None = None, climat: str = "tempéré"
    ) -> str:
        """Suggère des plantes à planter cette saison.

        Args:
            saison: Saison actuelle
            climat: Type de climat (tempéré, méditerranéen, etc.)

        Returns:
            Liste de plantes suggérées avec descriptions
        """
        if saison is None:
            saison = self.get_saison_actuelle()

        prompt = f"""Suggère 6 plantes/légumes parfaits à planter en {saison}
sous climat {climat}. Pour chaque plante indique:
- Nom et variété recommandée
- Facilité (débutant/intermédiaire/expert)
- Temps jusqu'à récolte
Format liste avec tirets."""

        return await self.call_with_cache(
            prompt=prompt,
            system_prompt="Tu es expert en jardinage et sélection de plantes",
            max_tokens=700,
        )

    # ─────────────────────────────────────────────────────────
    # ARROSAGE INTELLIGENT
    # ─────────────────────────────────────────────────────────

    async def conseil_arrosage(self, nom_plante: str, saison: str | None = None) -> str:
        """Conseil d'arrosage pour une plante spécifique.

        Args:
            nom_plante: Nom de la plante
            saison: Saison actuelle

        Returns:
            Conseils d'arrosage détaillés
        """
        if saison is None:
            saison = self.get_saison_actuelle()

        prompt = f"""Donne un conseil d'arrosage complet pour {nom_plante} en {saison}.
Inclus: fréquence, quantité (litres), meilleur moment de la journée,
signes de sur/sous-arrosage, adaptation si canicule/pluie."""

        return await self.call_with_cache(
            prompt=prompt,
            system_prompt="Tu es expert en arrosage et soins des plantes",
            max_tokens=400,
        )

    async def generer_plan_arrosage(
        self,
        plantes: list[str],
        meteo_prevue: dict | None = None,
    ) -> list[PlanArrosage]:
        """Génère un plan d'arrosage pour plusieurs plantes.

        Args:
            plantes: Liste des noms de plantes
            meteo_prevue: Prévisions météo optionnelles

        Returns:
            Liste de plans d'arrosage par plante
        """
        plans = []
        pluie_prevue = False

        if meteo_prevue:
            pluie_prevue = meteo_prevue.get("pluie_mm", 0) > 5

        for plante in plantes:
            # Déterminer fréquence selon saison et météo
            saison = self.get_saison_actuelle()
            if saison == "été":
                frequence = "quotidien" if not pluie_prevue else "tous_2_jours"
            elif saison in ("printemps", "automne"):
                frequence = "tous_2_jours" if not pluie_prevue else "hebdo"
            else:
                frequence = "hebdo"

            plans.append(
                PlanArrosage(
                    zone_ou_plante=plante,
                    frequence=frequence,
                    meilleur_moment="matin" if saison == "été" else "soir",
                    ajuste_meteo=True,
                    prochaine_date=date.today()
                    if not pluie_prevue
                    else date.today() + timedelta(days=2),
                )
            )

        return plans

    # ─────────────────────────────────────────────────────────
    # DIAGNOSTIC PLANTES (VISION IA)
    # ─────────────────────────────────────────────────────────

    async def diagnostiquer_plante(
        self, image_base64: str, description: str = ""
    ) -> DiagnosticPlante:
        """Diagnostic d'une plante à partir d'une photo.

        Args:
            image_base64: Image encodée en base64
            description: Description optionnelle du problème

        Returns:
            DiagnosticPlante avec état et recommandations
        """
        context = f" L'utilisateur décrit: {description}" if description else ""

        prompt = f"""Analyse cette photo de plante.{context}
Identifie:
1. L'espèce si possible
2. L'état de santé (excellent/bon/attention/problème)
3. Problèmes visibles (maladies, parasites, carences)
4. Traitements recommandés

Réponds en JSON:
{{"plante": "nom", "etat": "bon", "problemes": [...], "traitements": [...]}}"""

        try:
            response = await self.client.appeler_avec_image(
                prompt=prompt,
                image_base64=image_base64,
                system_prompt="Tu es phytopathologiste expert en diagnostic végétal",
            )
            # Parser la réponse JSON
            import json

            data = json.loads(response)
            return DiagnosticPlante(
                plante_identifiee=data.get("plante"),
                etat=EtatPlante(data.get("etat", "attention")),
                problemes_detectes=data.get("problemes", []),
                traitements_suggeres=data.get("traitements", []),
                confiance=0.8,
            )
        except Exception as e:
            logger.warning(f"Diagnostic IA échoué: {e}")
            return DiagnosticPlante(
                etat=EtatPlante.ATTENTION,
                problemes_detectes=["Diagnostic automatique non disponible"],
                traitements_suggeres=["Consulter un expert"],
                confiance=0.0,
            )

    # ─────────────────────────────────────────────────────────
    # ALERTES MÉTÉO JARDIN
    # ─────────────────────────────────────────────────────────

    async def analyser_meteo_impact(
        self, temperature_min: float, temperature_max: float, pluie_mm: float = 0
    ) -> list[AlerteMaison]:
        """Analyse l'impact météo sur le jardin.

        Args:
            temperature_min: Température minimale prévue
            temperature_max: Température maximale prévue
            pluie_mm: Précipitations prévues

        Returns:
            Liste d'alertes jardin
        """
        alertes = []

        # Alerte gel
        if temperature_min <= SEUIL_GEL:
            alertes.append(
                AlerteMaison(
                    type=TypeAlerteMaison.JARDIN,
                    niveau=NiveauUrgence.HAUTE,
                    titre="⚠️ Risque de gel",
                    message=f"Température min prévue: {temperature_min}°C",
                    action_suggeree="Protéger les plantes sensibles (voile, rentrer pots)",
                    metadata={"temperature": temperature_min},
                )
            )

        # Alerte canicule
        if temperature_max >= SEUIL_CANICULE:
            alertes.append(
                AlerteMaison(
                    type=TypeAlerteMaison.JARDIN,
                    niveau=NiveauUrgence.HAUTE,
                    titre="🔥 Canicule prévue",
                    message=f"Température max prévue: {temperature_max}°C",
                    action_suggeree="Arrosage copieux ce soir, paillage, ombrage",
                    metadata={"temperature": temperature_max},
                )
            )

        # Forte pluie
        if pluie_mm > 30:
            alertes.append(
                AlerteMaison(
                    type=TypeAlerteMaison.JARDIN,
                    niveau=NiveauUrgence.MOYENNE,
                    titre="🌧️ Fortes pluies prévues",
                    message=f"Précipitations: {pluie_mm}mm",
                    action_suggeree="Reporter arrosage, vérifier drainage",
                    metadata={"pluie_mm": pluie_mm},
                )
            )

        return alertes

    async def generer_conseils_meteo(
        self, meteo: dict, plantes: list[str] | None = None
    ) -> list[ConseilJardin]:
        """Génère des conseils jardin adaptés à la météo.

        Args:
            meteo: Données météo (temp_min, temp_max, pluie, etc.)
            plantes: Liste de plantes à considérer

        Returns:
            Liste de conseils contextuels
        """
        conseils = []
        temp_min = meteo.get("temp_min", 10)
        temp_max = meteo.get("temp_max", 20)

        # Conseil gel
        if temp_min <= SEUIL_GEL:
            conseils.append(
                ConseilJardin(
                    titre="Protection gel",
                    contenu="Rentrez les plantes en pot sensibles et protégez les autres avec un voile d'hivernage",
                    priorite=NiveauUrgence.HAUTE,
                    type_conseil="meteo",
                    plantes_concernees=plantes or [],
                )
            )

        # Conseil canicule
        if temp_max >= SEUIL_CANICULE:
            conseils.append(
                ConseilJardin(
                    titre="Canicule - Arrosage",
                    contenu="Arrosez copieusement le soir (jamais en plein soleil). Paillez pour conserver l'humidité.",
                    priorite=NiveauUrgence.HAUTE,
                    type_conseil="meteo",
                    plantes_concernees=plantes or [],
                )
            )

        return conseils

    # ─────────────────────────────────────────────────────────
    # HELPERS
    # ─────────────────────────────────────────────────────────

    @staticmethod
    def get_saison_actuelle() -> str:
        """Retourne la saison actuelle."""
        mois = date.today().month
        for mois_tuple, saison in SAISONS.items():
            if mois in mois_tuple:
                return saison
        return "printemps"

    def get_plantes(self, db: Session | None = None) -> list[GardenItem]:
        """Récupère toutes les plantes du jardin.

        Args:
            db: Session DB optionnelle

        Returns:
            Liste des plantes
        """
        if db is None:
            with obtenir_contexte_db() as session:
                return session.query(GardenItem).all()
        return db.query(GardenItem).all()

    def get_plantes_a_arroser(self, db: Session | None = None) -> list[GardenItem]:
        """Récupère les plantes nécessitant arrosage.

        Args:
            db: Session DB optionnelle

        Returns:
            Liste des plantes à arroser
        """
        if db is None:
            with obtenir_contexte_db() as session:
                return self._query_plantes_arrosage(session)
        return self._query_plantes_arrosage(db)

    def _query_plantes_arrosage(self, db: Session) -> list[GardenItem]:
        """Query interne pour plantes à arroser."""
        seuil = date.today() - timedelta(days=3)
        return (
            db.query(GardenItem)
            .filter((GardenItem.dernier_arrosage < seuil) | (GardenItem.dernier_arrosage.is_(None)))
            .all()
        )


# ═══════════════════════════════════════════════════════════
# FACTORY
# ═══════════════════════════════════════════════════════════


def get_jardin_service(client: ClientIA | None = None) -> JardinService:
    """Factory pour obtenir le service jardin.

    Args:
        client: Client IA optionnel

    Returns:
        Instance de JardinService
    """
    return JardinService(client=client)
