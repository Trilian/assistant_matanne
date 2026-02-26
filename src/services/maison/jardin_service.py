"""
Service Jardin - Gestion intelligente du jardin avec IA.

Features:
- Conseils saisonniers et météo-adaptatifs
- Plan d'arrosage intelligent
- Diagnostic plantes via vision IA
- Alertes gel/canicule automatiques
- Suggestions plantation par saison
- Gamification : badges, streaks, autonomie alimentaire
- Génération automatique des tâches jardin
"""

import logging
from datetime import date, timedelta

from sqlalchemy.orm import Session

from src.core.ai import ClientIA, obtenir_client_ia
from src.core.decorators import avec_cache, avec_session_db
from src.core.models import ElementJardin
from src.core.monitoring import chronometre
from src.services.core.base import BaseAIService
from src.services.core.events import obtenir_bus
from src.services.core.registry import service_factory

from .jardin_gamification_mixin import BADGES_JARDIN, JardinGamificationMixin
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


class JardinService(JardinGamificationMixin, BaseAIService):
    """Service IA pour la gestion intelligente du jardin.

    Hérite de BaseAIService pour les appels IA. Les opérations CRUD DB
    sont gérées via @avec_session_db plutôt que BaseService[ZoneJardin] car :
    - Les méthodes CRUD sont spécifiques au domaine (pas de CRUD générique)
    - BaseAIService et BaseService[T] ont des constructeurs incompatibles
    - Le pattern @avec_session_db est cohérent avec le reste du service

    Fonctionnalités:
    - Conseils saisonniers automatiques
    - Adaptation à la météo locale
    - Diagnostic plantes par photo
    - Planification arrosage intelligent
    - Gamification: badges, streaks, autonomie alimentaire
    - Génération automatique des tâches

    Example:
        >>> service = get_jardin_service()
        >>> conseils = await service.generer_conseils_saison("printemps")
        >>> taches = service.generer_taches(mes_plantes, meteo)
        >>> stats = service.calculer_stats(plantes, recoltes)
        >>> badges = service.obtenir_badges(stats)
    """

    def __init__(self, client: ClientIA | None = None):
        """Initialise le service jardin.

        Args:
            client: Client IA optionnel (créé automatiquement si None)
        """
        if client is None:
            client = obtenir_client_ia()
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
            saison = self.obtenir_saison_actuelle()

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
            saison = self.obtenir_saison_actuelle()

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
            saison = self.obtenir_saison_actuelle()

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
            saison = self.obtenir_saison_actuelle()
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
    def obtenir_saison_actuelle() -> str:
        """Retourne la saison actuelle."""
        mois = date.today().month
        for mois_tuple, saison in SAISONS.items():
            if mois in mois_tuple:
                return saison
        return "printemps"

    @staticmethod
    def get_saison_actuelle() -> str:
        """Alias anglais pour obtenir_saison_actuelle (rétrocompatibilité)."""
        return JardinService.obtenir_saison_actuelle()

    # ─────────────────────────────────────────────────────────
    # ÉMISSION D'ÉVÉNEMENTS — Appelé par les modules après CRUD
    # ─────────────────────────────────────────────────────────

    @staticmethod
    def emettre_modification(
        element_id: int = 0,
        nom: str = "",
        action: str = "modifie",
    ) -> None:
        """Émet un événement jardin.modifie pour déclencher l'invalidation de cache.

        Doit être appelé par les modules après ajout/modification/suppression
        d'un élément jardin.

        Args:
            element_id: ID de l'élément
            nom: Nom de l'élément
            action: "plante_ajoutee", "arrosage", "recolte", "supprime"
        """
        obtenir_bus().emettre(
            "jardin.modifie",
            {"element_id": element_id, "nom": nom, "action": action},
            source="jardin",
        )

    @chronometre(nom="jardin.obtenir_plantes", seuil_alerte_ms=1500)
    @chronometre("maison.jardin.plantes", seuil_alerte_ms=1500)
    @avec_cache(ttl=300)
    @avec_session_db
    def obtenir_plantes(self, db: Session | None = None) -> list[ElementJardin]:
        """Récupère toutes les plantes du jardin.

        Args:
            db: Session DB (injectée automatiquement par @avec_session_db)

        Returns:
            Liste des plantes
        """
        return db.query(ElementJardin).all()

    def get_plantes(self, db: Session | None = None) -> list[ElementJardin]:
        """Alias anglais pour obtenir_plantes (rétrocompatibilité)."""
        return self.obtenir_plantes(db)

    @chronometre(nom="jardin.plantes_a_arroser", seuil_alerte_ms=1500)
    @avec_cache(ttl=300)
    @avec_session_db
    def obtenir_plantes_a_arroser(self, db: Session | None = None) -> list[ElementJardin]:
        """Récupère les plantes nécessitant arrosage.

        Args:
            db: Session DB (injectée automatiquement par @avec_session_db)

        Returns:
            Liste des plantes à arroser
        """
        return self._query_plantes_arrosage(db)

    def get_plantes_a_arroser(self, db: Session | None = None) -> list[ElementJardin]:
        """Alias anglais pour obtenir_plantes_a_arroser (rétrocompatibilité)."""
        return self.obtenir_plantes_a_arroser(db)

    def _query_plantes_arrosage(self, db: Session) -> list[ElementJardin]:
        """Query interne pour plantes à arroser."""
        seuil = date.today() - timedelta(days=3)
        return (
            db.query(ElementJardin)
            .filter(
                (ElementJardin.dernier_arrosage < seuil)
                | (ElementJardin.dernier_arrosage.is_(None))
            )
            .all()
        )

    @avec_cache(ttl=300)
    @avec_session_db
    def obtenir_recoltes_proches(self, db: Session | None = None) -> list[ElementJardin]:
        """Récupère les plantes à récolter dans les 7 prochains jours.

        Args:
            db: Session DB (injectée automatiquement par @avec_session_db)

        Returns:
            Liste des plantes à récolter bientôt.
        """
        today = date.today()
        dans_7_jours = today + timedelta(days=7)
        return (
            db.query(ElementJardin)
            .filter(
                ElementJardin.date_recolte_prevue.isnot(None),
                ElementJardin.date_recolte_prevue >= today,
                ElementJardin.date_recolte_prevue <= dans_7_jours,
            )
            .all()
        )

    def get_recoltes_proches(self, db: Session | None = None) -> list[ElementJardin]:
        """Alias anglais pour obtenir_recoltes_proches (rétrocompatibilité)."""
        return self.obtenir_recoltes_proches(db)

    @avec_cache(ttl=300)
    @avec_session_db
    def obtenir_stats_jardin(self, db: Session | None = None) -> dict:
        """Calcule les statistiques du jardin.

        Args:
            db: Session DB (injectée automatiquement par @avec_session_db)

        Returns:
            Dict avec total_plantes, a_arroser, recoltes_proches, categories.
        """
        total = db.query(ElementJardin).filter(ElementJardin.statut == "actif").count()
        plantes_arroser = len(self._query_plantes_arrosage(db))

        # Récoltes proches
        today = date.today()
        dans_7_jours = today + timedelta(days=7)
        recoltes_proches = (
            db.query(ElementJardin)
            .filter(
                ElementJardin.date_recolte_prevue.isnot(None),
                ElementJardin.date_recolte_prevue >= today,
                ElementJardin.date_recolte_prevue <= dans_7_jours,
            )
            .count()
        )

        # Catégories distinctes
        from sqlalchemy import func

        categories = (
            db.query(func.count(func.distinct(ElementJardin.type)))
            .filter(ElementJardin.statut == "actif")
            .scalar()
            or 0
        )

        return {
            "total_plantes": total,
            "a_arroser": plantes_arroser,
            "recoltes_proches": recoltes_proches,
            "categories": categories,
        }

    def get_stats_jardin(self, db: Session | None = None) -> dict:
        """Alias anglais pour obtenir_stats_jardin (rétrocompatibilité)."""
        return self.obtenir_stats_jardin(db)

    # ─────────────────────────────────────────────────────────
    # CRUD PLANTES (non-IA)
    # ─────────────────────────────────────────────────────────

    @avec_session_db
    def ajouter_plante(
        self,
        nom: str,
        type_plante: str,
        db: Session | None = None,
        **kwargs,
    ) -> ElementJardin | None:
        """Ajoute une plante au jardin.

        Args:
            nom: Nom de la plante
            type_plante: Type (legume, fruit, fleur, etc.)
            db: Session DB (injectée par @avec_session_db)
            **kwargs: Champs additionnels (zone_id, date_plantation, etc.)

        Returns:
            ElementJardin créé, ou None en cas d'erreur.
        """
        try:
            plante = ElementJardin(nom=nom, type_plante=type_plante, **kwargs)
            db.add(plante)
            db.commit()
            db.refresh(plante)
            logger.info(f"✅ Plante ajoutée: {nom}")
            return plante
        except Exception as e:
            logger.error(f"Erreur ajout plante: {e}")
            db.rollback()
            return None

    @avec_session_db
    def arroser_plante(self, plante_id: int, db: Session | None = None) -> bool:
        """Enregistre un arrosage pour une plante.

        Args:
            plante_id: ID de la plante
            db: Session DB (injectée par @avec_session_db)

        Returns:
            True si l'arrosage a été enregistré.
        """
        try:
            from src.core.models.maison import JournalJardin

            log = JournalJardin(garden_item_id=plante_id, action="arrosage")
            db.add(log)
            db.commit()
            logger.info(f"✅ Arrosage enregistré pour plante {plante_id}")
            return True
        except Exception as e:
            logger.error(f"Erreur arrosage: {e}")
            db.rollback()
            return False

    @avec_session_db
    def ajouter_log_jardin(
        self,
        plante_id: int,
        action: str,
        notes: str = "",
        db: Session | None = None,
    ) -> bool:
        """Ajoute un log d'activité pour une plante.

        Args:
            plante_id: ID de la plante
            action: Type d'action (arrosage, taille, recolte, etc.)
            notes: Notes additionnelles
            db: Session DB (injectée par @avec_session_db)

        Returns:
            True si le log a été enregistré.
        """
        try:
            from src.core.models.maison import JournalJardin

            log = JournalJardin(
                garden_item_id=plante_id,
                action=action,
                notes=notes,
            )
            db.add(log)
            db.commit()
            logger.info(f"✅ Log jardin ajouté: {action} pour plante {plante_id}")
            return True
        except Exception as e:
            logger.error(f"Erreur log jardin: {e}")
            db.rollback()
            return False

    # ─────────────────────────────────────────────────────────
    # CRUD ZONES JARDIN
    # ─────────────────────────────────────────────────────────

    @avec_session_db
    def charger_zones(self, db: Session | None = None) -> list[dict]:
        """Charge toutes les zones du jardin depuis la DB.

        Args:
            db: Session DB (injectée par @avec_session_db)

        Returns:
            Liste de dicts avec: id, nom, type_zone, etat_note, superficie,
            commentaire, photos.
        """
        try:
            from src.core.models.temps_entretien import ZoneJardin

            zones = db.query(ZoneJardin).all()
            result = []
            for z in zones:
                result.append(
                    {
                        "id": z.id,
                        "nom": z.nom,
                        "type_zone": getattr(z, "type_zone", "autre"),
                        "etat_note": getattr(z, "etat_note", None) or 3,
                        "surface_m2": getattr(z, "surface_m2", None)
                        or getattr(z, "superficie", None)
                        or 0,
                        "etat_description": getattr(z, "etat_description", None)
                        or getattr(z, "commentaire", None)
                        or "",
                        "objectif": getattr(z, "objectif", None) or "",
                        "prochaine_action": getattr(z, "prochaine_action", None) or "",
                        "date_prochaine_action": getattr(z, "date_prochaine_action", None),
                        "photos_url": getattr(z, "photos_url", None)
                        or getattr(z, "photos", None)
                        or [],
                        "budget_estime": getattr(z, "budget_estime", None) or 0,
                    }
                )
            return result
        except Exception as e:
            logger.error(f"Erreur chargement zones: {e}")
            return []

    @avec_session_db
    def mettre_a_jour_zone(
        self,
        zone_id: int,
        updates: dict,
        db: Session | None = None,
    ) -> bool:
        """Met à jour une zone du jardin.

        Args:
            zone_id: ID de la zone.
            updates: Dict des champs à mettre à jour.
            db: Session DB (injectée par @avec_session_db)

        Returns:
            True si la mise à jour a réussi.
        """
        try:
            from src.core.models.temps_entretien import ZoneJardin

            zone = db.query(ZoneJardin).filter_by(id=zone_id).first()
            if zone is None:
                logger.warning(f"Zone {zone_id} non trouvée")
                return False
            for key, value in updates.items():
                setattr(zone, key, value)
            db.commit()
            logger.info(f"✅ Zone {zone_id} mise à jour")
            return True
        except Exception as e:
            logger.error(f"Erreur mise à jour zone: {e}")
            db.rollback()
            return False

    @avec_session_db
    def ajouter_photo_zone(
        self,
        zone_id: int,
        url: str,
        est_avant: bool = True,
        db: Session | None = None,
    ) -> bool:
        """Ajoute une photo à une zone.

        Args:
            zone_id: ID de la zone.
            url: URL de la photo.
            est_avant: True pour photo 'avant', False pour 'après'.
            db: Session DB (injectée par @avec_session_db)

        Returns:
            True si l'ajout a réussi.
        """
        try:
            from src.core.models.temps_entretien import ZoneJardin

            prefix = "avant:" if est_avant else "apres:"
            photo_entry = f"{prefix}{url}"

            zone = db.query(ZoneJardin).filter_by(id=zone_id).first()
            if zone is None:
                logger.warning(f"Zone {zone_id} non trouvée")
                return False
            photos = zone.photos_url if zone.photos_url is not None else []
            photos.append(photo_entry)
            zone.photos_url = photos
            db.commit()
            logger.info(f"✅ Photo ajoutée à zone {zone_id}")
            return True
        except Exception as e:
            logger.error(f"Erreur ajout photo: {e}")
            db.rollback()
            return False


# ═══════════════════════════════════════════════════════════
# FACTORY
# ═══════════════════════════════════════════════════════════


def obtenir_service_jardin(client: ClientIA | None = None) -> JardinService:
    """Factory pour obtenir le service jardin (convention française).

    Args:
        client: Client IA optionnel

    Returns:
        Instance de JardinService
    """
    return JardinService(client=client)


@service_factory("jardin", tags={"maison", "crud", "jardin"})
def get_jardin_service(client: ClientIA | None = None) -> JardinService:
    """Factory pour obtenir le service jardin (alias anglais)."""
    return obtenir_service_jardin(client)
