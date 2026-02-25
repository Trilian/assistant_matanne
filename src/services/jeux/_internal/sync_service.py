"""
SyncService - Service de synchronisation des données vers la base.

Connecte les sources de données (Football-Data, Loto) avec SeriesService
pour persister les statistiques calculées.

Utilisation:
    sync_service = get_sync_service()
    sync_service.synchroniser_paris("FL1")  # Ligue 1
    sync_service.synchroniser_loto()
"""

import logging
from datetime import datetime
from typing import Literal

from sqlalchemy.orm import Session

from src.core.decorators import avec_resilience, avec_session_db
from src.services.core.registry import service_factory

from .football_data import FootballDataService, StatistiquesMarcheData
from .loto_data import LotoDataService, StatistiqueNumeroLoto
from .series_service import SEUIL_VALUE_ALERTE, get_series_service

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# TYPES
# ═══════════════════════════════════════════════════════════

TypeJeu = Literal["paris", "loto"]


# ═══════════════════════════════════════════════════════════
# SERVICE PRINCIPAL
# ═══════════════════════════════════════════════════════════


class SyncService:
    """
    Service de synchronisation des données externes vers la base.

    Orchestre:
    1. Récupération des données (Football-Data / Loto)
    2. Calcul des statistiques
    3. Persistance via SeriesService
    4. Création d'alertes si opportunités détectées
    """

    def __init__(self):
        """Initialise le service."""
        self.series_service = get_series_service()

    # ─────────────────────────────────────────────────────────────────
    # SYNCHRONISATION PARIS SPORTIFS
    # ─────────────────────────────────────────────────────────────────

    @avec_resilience(retry=2, timeout_s=60, fallback=None)
    def synchroniser_paris(
        self,
        competition: str = "FL1",
        api_key: str | None = None,
        jours_historique: int = 365,
    ) -> dict:
        """
        Synchronise les données Paris Sportifs depuis Football-Data.org.

        Args:
            competition: Code compétition (FL1, PL, BL1, SA, PD)
            api_key: Clé API optionnelle
            jours_historique: Nombre de jours d'historique

        Returns:
            Dict avec statistiques de sync:
            - marches_maj: Nombre de marchés mis à jour
            - alertes_creees: Nombre d'alertes créées
            - erreurs: Liste d'erreurs éventuelles
        """
        resultat = {
            "marches_maj": 0,
            "alertes_creees": 0,
            "erreurs": [],
            "competition": competition,
            "timestamp": datetime.utcnow().isoformat(),
        }

        try:
            with FootballDataService(api_key) as football_service:
                # Récupérer toutes les statistiques
                stats_marches = football_service.calculer_toutes_statistiques(
                    competition=competition, jours=jours_historique
                )

                if not stats_marches:
                    resultat["erreurs"].append("Aucune donnée récupérée")
                    return resultat

                # Persister chaque marché
                for marche, stats in stats_marches.items():
                    try:
                        self._persister_stats_paris(stats, competition)
                        resultat["marches_maj"] += 1

                        # Créer alerte si opportunité
                        value = SeriesService.calculer_value(stats.frequence, stats.serie_actuelle)
                        if value >= SEUIL_VALUE_ALERTE:
                            self._creer_alerte_paris(stats, competition, value)
                            resultat["alertes_creees"] += 1

                    except Exception as e:
                        resultat["erreurs"].append(f"{marche}: {str(e)}")

                logger.info(
                    f"Sync Paris {competition}: {resultat['marches_maj']} marchés, "
                    f"{resultat['alertes_creees']} alertes"
                )

                # Émettre événement pour invalidation cache
                try:
                    from src.services.core.events.bus import obtenir_bus

                    obtenir_bus().emettre(
                        "jeux.sync_terminee",
                        {
                            "domaine": "paris",
                            "nb_elements": resultat["marches_maj"],
                            "nb_alertes": resultat["alertes_creees"],
                        },
                        source="sync_service",
                    )
                except Exception:  # noqa: BLE001
                    pass

        except Exception as e:
            logger.error(f"Erreur sync paris {competition}: {e}")
            resultat["erreurs"].append(str(e))

        return resultat

    @avec_session_db
    def _persister_stats_paris(
        self,
        stats: StatistiquesMarcheData,
        competition: str,
        db: Session | None = None,
    ) -> None:
        """Persiste les statistiques d'un marché paris."""
        self.series_service.creer_ou_maj_serie(
            type_jeu="paris",
            marche=stats.marche,
            championnat=competition,
            serie_actuelle=stats.serie_actuelle,
            frequence=stats.frequence,
            nb_occurrences=stats.nb_occurrences,
            nb_total=stats.total_matchs,
            derniere_occurrence=stats.derniere_occurrence,
            db=db,
        )

    @avec_session_db
    def _creer_alerte_paris(
        self,
        stats: StatistiquesMarcheData,
        competition: str,
        value: float,
        db: Session | None = None,
    ) -> None:
        """Crée une alerte pour un marché paris."""
        serie = self.series_service.obtenir_serie("paris", stats.marche, competition, db=db)
        if serie:
            self.series_service.creer_alerte(
                serie_id=serie.id,
                type_jeu="paris",
                marche=stats.marche,
                championnat=competition,
                value=value,
                serie=stats.serie_actuelle,
                frequence=stats.frequence,
                db=db,
            )

    # ─────────────────────────────────────────────────────────────────
    # SYNCHRONISATION LOTO
    # ─────────────────────────────────────────────────────────────────

    @avec_resilience(retry=2, timeout_s=60, fallback=None)
    def synchroniser_loto(
        self,
        source: str = "nouveau_loto",
        type_numeros: str = "principal",  # "principal", "chance", "tous"
    ) -> dict:
        """
        Synchronise les données Loto depuis data.gouv.fr.

        Args:
            source: Source des données ("nouveau_loto" ou "loto_historique")
            type_numeros: "principal", "chance" ou "tous"

        Returns:
            Dict avec statistiques de sync
        """
        resultat = {
            "numeros_maj": 0,
            "alertes_creees": 0,
            "erreurs": [],
            "source": source,
            "timestamp": datetime.utcnow().isoformat(),
        }

        try:
            with LotoDataService() as loto_service:
                # Télécharger l'historique
                tirages = loto_service.telecharger_historique(source)

                if not tirages:
                    resultat["erreurs"].append("Aucun tirage récupéré")
                    return resultat

                # Calculer et persister stats
                stats_globales = loto_service.calculer_toutes_statistiques(tirages)

                # Numéros principaux
                if type_numeros in ("principal", "tous"):
                    for num, stats in stats_globales.numeros_principaux.items():
                        try:
                            self._persister_stats_loto(stats)
                            resultat["numeros_maj"] += 1

                            if stats.value >= SEUIL_VALUE_ALERTE:
                                self._creer_alerte_loto(stats)
                                resultat["alertes_creees"] += 1

                        except Exception as e:
                            resultat["erreurs"].append(f"Numéro {num}: {str(e)}")

                # Numéros chance
                if type_numeros in ("chance", "tous"):
                    for num, stats in stats_globales.numeros_chance.items():
                        try:
                            self._persister_stats_loto(stats)
                            resultat["numeros_maj"] += 1

                            if stats.value >= SEUIL_VALUE_ALERTE:
                                self._creer_alerte_loto(stats)
                                resultat["alertes_creees"] += 1

                        except Exception as e:
                            resultat["erreurs"].append(f"Chance {num}: {str(e)}")

                logger.info(
                    f"Sync Loto: {resultat['numeros_maj']} numéros, "
                    f"{resultat['alertes_creees']} alertes"
                )

                # Émettre événement pour invalidation cache
                try:
                    from src.services.core.events.bus import obtenir_bus

                    obtenir_bus().emettre(
                        "jeux.sync_terminee",
                        {
                            "domaine": "loto",
                            "nb_elements": resultat["numeros_maj"],
                            "nb_alertes": resultat["alertes_creees"],
                        },
                        source="sync_service",
                    )
                except Exception:  # noqa: BLE001
                    pass

        except Exception as e:
            logger.error(f"Erreur sync loto: {e}")
            resultat["erreurs"].append(str(e))

        return resultat

    @avec_session_db
    def _persister_stats_loto(
        self,
        stats: StatistiqueNumeroLoto,
        db: Session | None = None,
    ) -> None:
        """Persiste les statistiques d'un numéro loto."""
        # Marche = numéro + type (ex: "principal_7" ou "chance_5")
        marche = f"{stats.type_numero}_{stats.numero}"

        self.series_service.creer_ou_maj_serie(
            type_jeu="loto",
            marche=marche,
            championnat=None,  # Pas de championnat pour Loto
            serie_actuelle=stats.serie_actuelle,
            frequence=stats.frequence,
            nb_occurrences=stats.nb_sorties,
            nb_total=stats.total_tirages,
            derniere_occurrence=stats.derniere_sortie,
            db=db,
        )

    @avec_session_db
    def _creer_alerte_loto(
        self,
        stats: StatistiqueNumeroLoto,
        db: Session | None = None,
    ) -> None:
        """Crée une alerte pour un numéro loto."""
        marche = f"{stats.type_numero}_{stats.numero}"
        serie = self.series_service.obtenir_serie("loto", marche, db=db)

        if serie:
            self.series_service.creer_alerte(
                serie_id=serie.id,
                type_jeu="loto",
                marche=marche,
                championnat=None,
                value=stats.value,
                serie=stats.serie_actuelle,
                frequence=stats.frequence,
                db=db,
            )

    # ─────────────────────────────────────────────────────────────────
    # SYNCHRONISATION COMPLÈTE
    # ─────────────────────────────────────────────────────────────────

    def synchroniser_tout(
        self,
        competitions: list[str] | None = None,
        api_key: str | None = None,
    ) -> dict:
        """
        Synchronise toutes les données (Paris + Loto).

        Args:
            competitions: Liste des compétitions Paris (défaut: FL1)
            api_key: Clé API Football-Data

        Returns:
            Dict avec résultats de toutes les syncs
        """
        if competitions is None:
            competitions = ["FL1"]

        resultats = {
            "paris": {},
            "loto": None,
            "timestamp": datetime.utcnow().isoformat(),
        }

        # Sync Paris
        for comp in competitions:
            resultats["paris"][comp] = self.synchroniser_paris(comp, api_key)

        # Sync Loto
        resultats["loto"] = self.synchroniser_loto(type_numeros="tous")

        return resultats


# ═══════════════════════════════════════════════════════════
# FACTORY
# ═══════════════════════════════════════════════════════════


def obtenir_service_sync_jeux() -> SyncService:
    """
    Factory pour créer une instance du service (convention française).

    Returns:
        Instance SyncService
    """
    return SyncService()


@service_factory("sync", tags={"jeux", "sync"})
def get_sync_service() -> SyncService:
    """
    Factory pour créer une instance du service (alias anglais).

    Returns:
        Instance SyncService
    """
    return obtenir_service_sync_jeux()
