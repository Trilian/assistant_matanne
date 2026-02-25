"""
Service Entretien - Gestion intelligente des routines ménage.

Features:
- Création de routines IA avec tâches suggérées
- Optimisation de la semaine (équilibrage charge)
- Détection de patterns (périodicité automatique)
- Sync calendrier Google/Apple
- Adaptation météo (vitres si beau temps, etc.)
"""

import logging
from datetime import date, timedelta

from sqlalchemy.orm import Session, selectinload

from src.core.ai import ClientIA, obtenir_client_ia
from src.core.decorators import avec_cache, avec_session_db
from src.core.models import Routine, TacheRoutine
from src.services.core.base import BaseAIService
from src.services.core.events.bus import obtenir_bus
from src.services.core.registry import service_factory

from .entretien_gamification_mixin import EntretienGamificationMixin
from .schemas import (
    RoutineSuggestionIA,
)

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════
# CONSTANTES
# ═══════════════════════════════════════════════════════════

CATEGORIES_ENTRETIEN = [
    "menage",
    "cuisine",
    "salle_de_bain",
    "chambres",
    "linge",
    "jardin",
    "administratif",
]

FREQUENCES = {
    "quotidien": 1,
    "tous_2_jours": 2,
    "hebdo": 7,
    "bi_mensuel": 14,
    "mensuel": 30,
    "trimestriel": 90,
    "saisonnier": 120,
    "annuel": 365,
}

# Note: JOURS_SEMAINE importé de src.core.constants si nécessaire


# ═══════════════════════════════════════════════════════════
# SERVICE ENTRETIEN
# ═══════════════════════════════════════════════════════════


class EntretienService(EntretienGamificationMixin, BaseAIService):
    """Service IA pour la gestion des routines ménage.

    Hérite de BaseAIService pour les appels IA. Les opérations CRUD DB
    sont gérées via @avec_session_db plutôt que BaseService[Routine] car :
    - Les méthodes CRUD sont spécifiques au domaine (pas de CRUD générique)
    - BaseAIService et BaseService[T] ont des constructeurs incompatibles
    - Le pattern @avec_session_db est cohérent avec le reste du service

    Fonctionnalités:
    - Création routines avec suggestions IA
    - Optimisation répartition hebdomadaire
    - Détection automatique de périodicité
    - Adaptation aux contraintes météo
    - Gamification: badges, streaks, score propreté
    - Génération automatique des tâches d'entretien

    Example:
        >>> service = get_entretien_service()
        >>> taches = service.generer_taches(mes_objets, historique)
        >>> stats = service.calculer_stats_globales(objets, historique)
        >>> badges = service.obtenir_badges(stats)
    """

    def __init__(self, client: ClientIA | None = None):
        """Initialise le service entretien.

        Args:
            client: Client IA optionnel
        """
        if client is None:
            client = obtenir_client_ia()
        super().__init__(
            client=client,
            cache_prefix="entretien",
            default_ttl=3600,
            service_name="entretien",
        )

    # ─────────────────────────────────────────────────────────
    # CRÉATION ROUTINES IA
    # ─────────────────────────────────────────────────────────

    async def creer_routine_ia(
        self, nom: str, description: str = "", categorie: str = "menage"
    ) -> RoutineSuggestionIA:
        """Crée une routine avec tâches suggérées par l'IA.

        Args:
            nom: Nom de la routine
            description: Description/contexte (taille logement, etc.)
            categorie: Catégorie de la routine

        Returns:
            RoutineSuggestionIA avec tâches et durées estimées
        """
        context = f" ({description})" if description else ""

        prompt = f"""Pour la routine "{nom}"{context}, catégorie {categorie}:
1. Suggère 5-8 tâches pratiques dans un ordre logique
2. Estime le temps pour chaque tâche (en minutes)
3. Recommande une fréquence (quotidien/hebdo/mensuel)

Format JSON:
{{"taches": ["Tâche 1 (10min)", ...], "duree_totale": 60, "frequence": "hebdo"}}"""

        try:
            response = await self.call_with_cache(
                prompt=prompt,
                system_prompt="Tu es expert en organisation domestique et productivité",
                max_tokens=700,
            )
            import json

            data = json.loads(response)
            return RoutineSuggestionIA(
                nom=nom,
                description=description or f"Routine {categorie}",
                taches_suggerees=data.get("taches", []),
                frequence_recommandee=data.get("frequence", "hebdo"),
                duree_totale_estimee_min=data.get("duree_totale", 60),
            )
        except Exception as e:
            logger.warning(f"Création routine IA échouée: {e}")
            # Fallback avec tâches par défaut
            return RoutineSuggestionIA(
                nom=nom,
                description=description or f"Routine {categorie}",
                taches_suggerees=self._get_taches_defaut(categorie),
                frequence_recommandee="hebdo",
                duree_totale_estimee_min=60,
            )
        finally:
            # Émettre événement domaine (succès ou fallback)
            obtenir_bus().emettre(
                "entretien.routine_creee",
                {"nom": nom, "categorie": categorie},
                source="entretien",
            )

    async def suggerer_taches(self, nom_routine: str, contexte: str = "") -> str:
        """Suggère des tâches pour une routine existante.

        Args:
            nom_routine: Nom de la routine
            contexte: Contexte additionnel

        Returns:
            Texte avec tâches suggérées
        """
        prompt = f"""Pour la routine "{nom_routine}" {contexte},
suggère 5-8 tâches pratiques et dans un ordre logique.
Format: "- Tâche : description courte (X min)"."""

        return await self.call_with_cache(
            prompt=prompt,
            system_prompt="Tu es expert en organisation domestique",
            max_tokens=600,
        )

    # ─────────────────────────────────────────────────────────
    # OPTIMISATION SEMAINE
    # ─────────────────────────────────────────────────────────

    async def optimiser_semaine(
        self, taches: list[str], contraintes: dict | None = None
    ) -> dict[str, list[str]]:
        """Optimise la répartition des tâches sur la semaine.

        Args:
            taches: Liste des tâches à répartir
            contraintes: Contraintes (jours indisponibles, etc.)

        Returns:
            Dict {jour: [tâches]}
        """
        contraintes_txt = ""
        if contraintes:
            if contraintes.get("jours_off"):
                contraintes_txt = f" Éviter: {', '.join(contraintes['jours_off'])}."

        taches_txt = "\n".join(f"- {t}" for t in taches)

        prompt = f"""Répartis ces tâches ménagères sur la semaine de façon équilibrée:
{taches_txt}
{contraintes_txt}

Critères:
- Équilibrer la charge par jour
- Regrouper les tâches similaires
- Éviter de surcharger un seul jour

Format JSON: {{"Lundi": [...], "Mardi": [...], ...}}"""

        try:
            response = await self.call_with_cache(
                prompt=prompt,
                system_prompt="Tu es expert en planification et organisation du temps",
                max_tokens=800,
            )
            import json

            result = json.loads(response)
        except Exception as e:
            logger.warning(f"Optimisation semaine échouée: {e}")
            # Répartition simple par défaut
            result = self._repartition_simple(taches)

        # Émettre événement domaine
        obtenir_bus().emettre(
            "entretien.semaine_optimisee",
            {"nb_taches": len(taches), "nb_jours": len(result)},
            source="entretien",
        )

        return result

    async def conseil_efficacite(self) -> str:
        """Donne des astuces pour un ménage plus efficace.

        Returns:
            Texte avec conseils d'efficacité
        """
        prompt = """Donne 5 astuces pratiques pour rendre le ménage plus efficace et moins chronophage.
Sois spécifique et actionnable. Inclus des techniques de pros."""

        return await self.call_with_cache(
            prompt=prompt,
            system_prompt="Tu es expert en organisation domestique et efficacité",
            max_tokens=500,
        )

    # ─────────────────────────────────────────────────────────
    # DÉTECTION PATTERNS
    # ─────────────────────────────────────────────────────────

    def detecter_periodicite(self, historique: list[date]) -> tuple[int, float]:
        """Détecte la périodicité dans un historique de dates.

        Args:
            historique: Liste de dates d'exécution

        Returns:
            Tuple (période en jours, confiance 0-1)
        """
        if len(historique) < 3:
            return 7, 0.3  # Défaut hebdo avec faible confiance

        # Calculer les intervalles
        sorted_dates = sorted(historique)
        intervalles = [
            (sorted_dates[i + 1] - sorted_dates[i]).days for i in range(len(sorted_dates) - 1)
        ]

        if not intervalles:
            return 7, 0.3

        # Moyenne et écart-type
        moyenne = sum(intervalles) / len(intervalles)
        variance = sum((x - moyenne) ** 2 for x in intervalles) / len(intervalles)
        ecart_type = variance**0.5

        # Confiance basée sur la régularité
        confiance = max(0.3, 1 - (ecart_type / moyenne)) if moyenne > 0 else 0.3

        # Arrondir à la période standard la plus proche
        periode = self._arrondir_periode(int(moyenne))

        return periode, confiance

    def suggerer_prochaine_date(self, derniere_execution: date, periode_jours: int) -> date:
        """Suggère la prochaine date d'exécution.

        Args:
            derniere_execution: Date de dernière exécution
            periode_jours: Période en jours

        Returns:
            Prochaine date suggérée
        """
        prochaine = derniere_execution + timedelta(days=periode_jours)
        # Si dans le passé, proposer aujourd'hui ou demain
        if prochaine < date.today():
            return date.today()
        return prochaine

    # ─────────────────────────────────────────────────────────
    # ADAPTATION MÉTÉO
    # ─────────────────────────────────────────────────────────

    async def adapter_planning_meteo(self, taches_jour: list[str], meteo: dict) -> list[str]:
        """Adapte le planning du jour selon la météo.

        Args:
            taches_jour: Tâches prévues
            meteo: Données météo (pluie, soleil, etc.)

        Returns:
            Tâches réordonnées/modifiées
        """
        taches_modifiees = []
        pluie = meteo.get("pluie_mm", 0) > 5
        soleil = meteo.get("ensoleillement", "partiel") == "fort"

        for tache in taches_jour:
            tache_lower = tache.lower()

            # Reporter vitres si pluie prévue
            if "vitre" in tache_lower and pluie:
                taches_modifiees.append(f"⏸️ {tache} (reporté - pluie)")
                continue

            # Prioriser si beau temps
            if "vitre" in tache_lower and soleil:
                taches_modifiees.insert(0, f"☀️ {tache} (idéal aujourd'hui!)")
                continue

            taches_modifiees.append(tache)

        return taches_modifiees

    # ─────────────────────────────────────────────────────────
    # CRUD HELPERS
    # ─────────────────────────────────────────────────────────

    @avec_cache(ttl=300)
    @avec_session_db
    def obtenir_routines(self, db: Session | None = None) -> list[Routine]:
        """Récupère toutes les routines actives.

        Args:
            db: Session DB (injectée automatiquement par @avec_session_db)

        Returns:
            Liste des routines
        """
        return db.query(Routine).filter(Routine.actif.is_(True)).all()

    def get_routines(self, db: Session | None = None) -> list[Routine]:
        """Alias anglais pour obtenir_routines (rétrocompatibilité)."""
        return self.obtenir_routines(db)

    @avec_cache(ttl=300)
    @avec_session_db
    def obtenir_taches_du_jour(self, db: Session | None = None) -> list[TacheRoutine]:
        """Récupère les tâches à faire aujourd'hui.

        Args:
            db: Session DB (injectée automatiquement par @avec_session_db)

        Returns:
            Liste des tâches du jour
        """
        jour_semaine = date.today().weekday()
        return self._query_taches_jour(db, jour_semaine)

    def get_taches_du_jour(self, db: Session | None = None) -> list[TacheRoutine]:
        """Alias anglais pour obtenir_taches_du_jour (rétrocompatibilité)."""
        return self.obtenir_taches_du_jour(db)

    def _query_taches_jour(self, db: Session, jour_semaine: int) -> list[TacheRoutine]:
        """Query interne pour tâches du jour."""
        # Récupérer routines actives du jour
        routines = (
            db.query(Routine)
            .options(selectinload(Routine.tasks))
            .filter(Routine.actif.is_(True))
            .all()
        )
        taches = []
        for routine in routines:
            taches.extend(routine.tasks)
        return taches

    # ─────────────────────────────────────────────────────────
    # HELPERS PRIVÉS
    # ─────────────────────────────────────────────────────────

    def _get_taches_defaut(self, categorie: str) -> list[str]:
        """Retourne des tâches par défaut pour une catégorie."""
        taches_defaut = {
            "menage": [
                "Aspirateur salon (15min)",
                "Serpillère (15min)",
                "Poussières meubles (10min)",
                "Nettoyage cuisine (20min)",
            ],
            "salle_de_bain": [
                "Nettoyage lavabo (5min)",
                "Nettoyage WC (5min)",
                "Nettoyage douche (10min)",
                "Miroirs (5min)",
            ],
            "cuisine": [
                "Vaisselle/lave-vaisselle (10min)",
                "Plan de travail (5min)",
                "Poubelles (5min)",
                "Frigo (15min)",
            ],
        }
        return taches_defaut.get(categorie, taches_defaut["menage"])

    def _repartition_simple(self, taches: list[str]) -> dict[str, list[str]]:
        """Répartition simple des tâches sur la semaine."""
        planning = {jour: [] for jour in JOURS_SEMAINE}
        for i, tache in enumerate(taches):
            jour = JOURS_SEMAINE[i % 7]
            planning[jour].append(tache)
        return planning

    def _arrondir_periode(self, jours: int) -> int:
        """Arrondit à la période standard la plus proche."""
        periodes_std = [1, 2, 7, 14, 30, 90, 365]
        return min(periodes_std, key=lambda x: abs(x - jours))


# ═══════════════════════════════════════════════════════════
# FACTORY
# ═══════════════════════════════════════════════════════════


def obtenir_service_entretien(client: ClientIA | None = None) -> EntretienService:
    """Factory pour obtenir le service entretien (convention française).

    Args:
        client: Client IA optionnel

    Returns:
        Instance de EntretienService
    """
    return EntretienService(client=client)


@service_factory("entretien", tags={"maison", "crud", "entretien"})
def get_entretien_service(client: ClientIA | None = None) -> EntretienService:
    """Factory pour obtenir le service entretien (alias anglais)."""
    return obtenir_service_entretien(client)
