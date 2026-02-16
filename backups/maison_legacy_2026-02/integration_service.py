"""
Service Intégration Maison - Pipelines automatiques inter-modules.

Features:
- Pipeline Projet → Liste Courses → Budget
- Pipeline Entretien → Stock consommables
- Pipeline Jardin → Météo → Notifications
- Synchronisation calendrier familial
- Pipeline Objets à acheter/changer → Courses/Budget
- Synchronisation tâches récurrentes → Planning semaine
"""

import logging
from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Any

from sqlalchemy.orm import Session

from src.core.ai import ClientIA
from src.core.database import obtenir_contexte_db
from src.services.base import BaseAIService

from .schemas import (
    ArticleCoursesGenere,
    FrequenceTache,
    LienObjetBudget,
    LienObjetCourses,
    NiveauUrgence,
    ObjetAvecStatut,
    PipelineResult,
    PrioriteRemplacement,
    StatutObjet,
    SyncPlanningRequest,
    SyncPlanningResult,
    TacheMaisonRecurrente,
)

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# SERVICE INTÉGRATION
# ═══════════════════════════════════════════════════════════


class MaisonIntegrationService(BaseAIService):
    """Service d'intégration inter-modules pour la maison.

    Pipelines automatiques:
    1. Projet → Matériaux → Liste Courses → Budget
    2. Tâche entretien → Vérifier stock → Alerte réapprovisionnement
    3. Météo → Impact jardin → Notification push
    4. Planning maison → Calendrier familial

    Example:
        >>> service = get_maison_integration_service()
        >>> result = await service.pipeline_projet_vers_courses(projet_id=1)
        >>> print(f"Articles ajoutés: {result.articles_ajoutes}")
    """

    def __init__(self, client: ClientIA | None = None):
        """Initialise le service d'intégration.

        Args:
            client: Client IA optionnel
        """
        if client is None:
            client = ClientIA()
        super().__init__(
            client=client,
            cache_prefix="maison_integration",
            default_ttl=600,
            service_name="maison_integration",
        )

    # ─────────────────────────────────────────────────────────
    # PIPELINE PROJET → COURSES → BUDGET
    # ─────────────────────────────────────────────────────────

    async def pipeline_projet_vers_courses(
        self,
        projet_id: int,
        db: Session | None = None,
    ) -> PipelineResult:
        """Pipeline automatique: Projet → Liste Courses → Budget.

        Étapes:
        1. Récupérer les matériaux du projet
        2. Vérifier le stock existant
        3. Ajouter les manquants à la liste de courses
        4. Mettre à jour le budget prévisionnel

        Args:
            projet_id: ID du projet
            db: Session DB optionnelle

        Returns:
            PipelineResult avec détails des opérations
        """
        logger.info(f"Pipeline projet→courses pour projet {projet_id}")

        etapes_completees = []
        erreurs = []
        articles_ajoutes = 0
        budget_impacte = Decimal("0")

        try:
            # 1. Récupérer les matériaux du projet
            materiaux = await self._obtenir_materiaux_projet(projet_id, db)
            etapes_completees.append(f"Récupéré {len(materiaux)} matériaux du projet")

            # 2. Vérifier stock existant
            materiaux_manquants = await self._verifier_stock(materiaux, db)
            etapes_completees.append(f"{len(materiaux_manquants)} matériaux à acheter")

            # 3. Ajouter à la liste de courses
            if materiaux_manquants:
                articles_ajoutes = await self._ajouter_liste_courses(
                    materiaux_manquants,
                    source=f"Projet #{projet_id}",
                    db=db,
                )
                etapes_completees.append(f"{articles_ajoutes} articles ajoutés à la liste")

            # 4. Mettre à jour le budget
            budget_impacte = await self._mettre_a_jour_budget(
                projet_id,
                materiaux_manquants,
                db=db,
            )
            etapes_completees.append(f"Budget mis à jour: {budget_impacte}€")

        except Exception as e:
            erreurs.append(f"Erreur pipeline: {str(e)}")
            logger.error(f"Pipeline projet→courses échoué: {e}")

        return PipelineResult(
            succes=len(erreurs) == 0,
            pipeline="projet_vers_courses",
            etapes_completees=etapes_completees,
            erreurs=erreurs,
            metadata={
                "projet_id": projet_id,
                "articles_ajoutes": articles_ajoutes,
                "budget_impacte": str(budget_impacte),
            },
        )

    async def _obtenir_materiaux_projet(
        self,
        projet_id: int,
        db: Session | None,
    ) -> list[dict]:
        """Récupère les matériaux nécessaires pour un projet."""
        # TODO: Appeler projets_service.obtenir_materiaux(projet_id)
        # Simulation
        return [
            {"nom": "Vis 4x40mm", "quantite": 50, "prix_unitaire": 0.05},
            {"nom": "Peinture blanche 10L", "quantite": 2, "prix_unitaire": 45.00},
            {"nom": "Rouleau peinture", "quantite": 3, "prix_unitaire": 8.00},
        ]

    async def _verifier_stock(
        self,
        materiaux: list[dict],
        db: Session | None,
    ) -> list[dict]:
        """Vérifie le stock et retourne les matériaux manquants."""
        # TODO: Appeler inventaire_service.verifier_disponibilite()
        # Simulation: supposons 50% en stock
        return materiaux[:2]  # Les 2 premiers manquants

    async def _ajouter_liste_courses(
        self,
        articles: list[dict],
        source: str,
        db: Session | None,
    ) -> int:
        """Ajoute les articles à la liste de courses."""
        # TODO: Appeler ServiceCourses.ajouter_articles()
        logger.info(f"Ajout {len(articles)} articles à la liste (source: {source})")
        return len(articles)

    async def _mettre_a_jour_budget(
        self,
        projet_id: int,
        articles: list[dict],
        db: Session | None,
    ) -> Decimal:
        """Met à jour le budget du projet avec les achats prévus."""
        # TODO: Appeler BudgetService.ajouter_depenses_prevues()
        total = sum(
            Decimal(str(a.get("prix_unitaire", 0))) * a.get("quantite", 1) for a in articles
        )
        return total

    # ─────────────────────────────────────────────────────────
    # PIPELINE ENTRETIEN → STOCK → ALERTE
    # ─────────────────────────────────────────────────────────

    async def pipeline_entretien_stock(
        self,
        tache_id: int,
        db: Session | None = None,
    ) -> PipelineResult:
        """Pipeline: Tâche entretien → Vérifier consommables → Alerte.

        Vérifie automatiquement si les produits nécessaires sont en stock
        avant une tâche d'entretien planifiée.

        Args:
            tache_id: ID de la tâche d'entretien
            db: Session DB optionnelle

        Returns:
            PipelineResult avec alertes éventuelles
        """
        logger.info(f"Pipeline entretien→stock pour tâche {tache_id}")

        etapes_completees = []
        erreurs = []
        alertes = []

        try:
            # 1. Récupérer les produits nécessaires
            produits_requis = await self._obtenir_produits_tache(tache_id, db)
            etapes_completees.append(f"Tâche nécessite {len(produits_requis)} produits")

            # 2. Vérifier stock
            produits_bas = await self._verifier_stock_consommables(produits_requis, db)

            # 3. Créer alertes si manquants
            for produit in produits_bas:
                alertes.append(
                    {
                        "produit": produit["nom"],
                        "stock_actuel": produit.get("stock", 0),
                        "urgence": NiveauUrgence.MOYENNE.value,
                    }
                )
                # TODO: Appeler ServiceNotifications.envoyer()

            etapes_completees.append(f"{len(alertes)} alertes de stock bas générées")

        except Exception as e:
            erreurs.append(f"Erreur pipeline: {str(e)}")

        return PipelineResult(
            succes=len(erreurs) == 0,
            pipeline="entretien_stock",
            etapes_completees=etapes_completees,
            erreurs=erreurs,
            metadata={
                "tache_id": tache_id,
                "alertes": alertes,
            },
        )

    async def _obtenir_produits_tache(
        self,
        tache_id: int,
        db: Session | None,
    ) -> list[dict]:
        """Récupère les produits nécessaires pour une tâche."""
        # TODO: Mapper tâche → produits
        return [
            {"nom": "Liquide vaisselle", "quantite_requise": 1},
            {"nom": "Éponge", "quantite_requise": 1},
        ]

    async def _verifier_stock_consommables(
        self,
        produits: list[dict],
        db: Session | None,
    ) -> list[dict]:
        """Vérifie le stock des consommables."""
        # TODO: Appeler HouseStock.verifier()
        # Simulation: 30% en stock bas
        produits_bas = []
        for p in produits:
            if p["nom"] == "Éponge":  # Simulation
                produits_bas.append({**p, "stock": 0})
        return produits_bas

    # ─────────────────────────────────────────────────────────
    # PIPELINE MÉTÉO → JARDIN → NOTIFICATION
    # ─────────────────────────────────────────────────────────

    async def pipeline_meteo_jardin(
        self,
        db: Session | None = None,
    ) -> PipelineResult:
        """Pipeline: Météo → Impact jardin → Notification push.

        Vérifie la météo et génère des alertes/conseils pour le jardin.

        Args:
            db: Session DB optionnelle

        Returns:
            PipelineResult avec actions suggérées
        """
        logger.info("Pipeline météo→jardin")

        etapes_completees = []
        erreurs = []
        notifications = []

        try:
            # 1. Récupérer prévisions météo
            meteo = await self._obtenir_previsions_meteo()
            etapes_completees.append("Prévisions météo récupérées")

            # 2. Analyser impact jardin
            impacts = await self._analyser_impact_jardin(meteo, db)
            etapes_completees.append(f"{len(impacts)} impacts identifiés")

            # 3. Générer notifications si nécessaire
            for impact in impacts:
                if impact.get("urgence") in ["haute", "critique"]:
                    notif = await self._envoyer_notification_jardin(impact)
                    if notif:
                        notifications.append(notif)

            etapes_completees.append(f"{len(notifications)} notifications envoyées")

        except Exception as e:
            erreurs.append(f"Erreur pipeline: {str(e)}")

        return PipelineResult(
            succes=len(erreurs) == 0,
            pipeline="meteo_jardin",
            etapes_completees=etapes_completees,
            erreurs=erreurs,
            metadata={
                "notifications": notifications,
            },
        )

    async def _obtenir_previsions_meteo(self) -> dict:
        """Récupère les prévisions météo."""
        # TODO: Appeler ServiceMeteo.obtenir_previsions()
        return {
            "temperature_min": -2,
            "temperature_max": 12,
            "precipitation_mm": 0,
            "vent_kmh": 15,
            "gel": True,
        }

    async def _analyser_impact_jardin(
        self,
        meteo: dict,
        db: Session | None,
    ) -> list[dict]:
        """Analyse l'impact météo sur le jardin."""
        impacts = []

        if meteo.get("gel"):
            impacts.append(
                {
                    "type": "gel",
                    "message": "Gel nocturne prévu - protéger les plantes sensibles",
                    "urgence": "haute",
                    "action": "Rentrer les pots, voiler les semis",
                }
            )

        if meteo.get("precipitation_mm", 0) > 30:
            impacts.append(
                {
                    "type": "pluie_forte",
                    "message": "Fortes pluies prévues",
                    "urgence": "moyenne",
                    "action": "Reporter l'arrosage, vérifier drainage",
                }
            )

        return impacts

    async def _envoyer_notification_jardin(self, impact: dict) -> dict | None:
        """Envoie une notification push pour le jardin."""
        # TODO: Appeler ServiceNtfy.envoyer()
        logger.info(f"Notification jardin: {impact.get('message')}")
        return {
            "titre": f"🌱 Jardin - {impact.get('type', '').upper()}",
            "message": impact.get("message"),
            "action": impact.get("action"),
        }

    # ─────────────────────────────────────────────────────────
    # PIPELINE PLANNING → CALENDRIER FAMILIAL
    # ─────────────────────────────────────────────────────────

    async def pipeline_sync_calendrier(
        self,
        db: Session | None = None,
    ) -> PipelineResult:
        """Synchronise les tâches maison avec le calendrier familial.

        Args:
            db: Session DB optionnelle

        Returns:
            PipelineResult avec événements synchronisés
        """
        logger.info("Pipeline sync calendrier familial")

        etapes_completees = []
        erreurs = []
        evenements_sync = 0

        try:
            # 1. Récupérer tâches maison planifiées
            taches = await self._obtenir_taches_planifiees(db)
            etapes_completees.append(f"Récupéré {len(taches)} tâches planifiées")

            # 2. Récupérer projets avec deadlines
            projets = await self._obtenir_projets_deadlines(db)
            etapes_completees.append(f"Récupéré {len(projets)} projets avec deadline")

            # 3. Synchroniser avec calendrier familial
            evenements_sync = await self._sync_calendrier_familial(
                taches=taches,
                projets=projets,
                db=db,
            )
            etapes_completees.append(f"{evenements_sync} événements synchronisés")

        except Exception as e:
            erreurs.append(f"Erreur pipeline: {str(e)}")

        return PipelineResult(
            succes=len(erreurs) == 0,
            pipeline="sync_calendrier",
            etapes_completees=etapes_completees,
            erreurs=erreurs,
            metadata={
                "evenements_sync": evenements_sync,
            },
        )

    async def _obtenir_taches_planifiees(self, db: Session | None) -> list[dict]:
        """Récupère les tâches maison planifiées."""
        # TODO: Appeler entretien_service.obtenir_taches_semaine()
        return [
            {"titre": "Ménage complet", "date": date.today() + timedelta(days=2)},
            {"titre": "Tonte pelouse", "date": date.today() + timedelta(days=5)},
        ]

    async def _obtenir_projets_deadlines(self, db: Session | None) -> list[dict]:
        """Récupère les projets avec deadlines."""
        # TODO: Appeler projets_service.obtenir_deadlines()
        return [
            {"titre": "Finir peinture chambre", "deadline": date.today() + timedelta(days=10)},
        ]

    async def _sync_calendrier_familial(
        self,
        taches: list[dict],
        projets: list[dict],
        db: Session | None,
    ) -> int:
        """Synchronise les événements avec le calendrier familial."""
        # TODO: Appeler ServicePlanning.creer_evenements_batch()
        total = len(taches) + len(projets)
        logger.info(f"Synchronisation de {total} événements avec calendrier familial")
        return total

    # ─────────────────────────────────────────────────────────
    # EXÉCUTION BATCH DE TOUS LES PIPELINES
    # ─────────────────────────────────────────────────────────

    async def executer_pipelines_quotidiens(
        self,
        db: Session | None = None,
    ) -> list[PipelineResult]:
        """Exécute tous les pipelines automatiques quotidiens.

        Appelé typiquement par un scheduler ou cron job.

        Args:
            db: Session DB optionnelle

        Returns:
            Liste des résultats de chaque pipeline
        """
        logger.info("Exécution des pipelines quotidiens maison")
        resultats = []

        # Pipeline météo → jardin (le plus important)
        resultats.append(await self.pipeline_meteo_jardin(db))

        # Pipeline sync calendrier
        resultats.append(await self.pipeline_sync_calendrier(db))

        # Pipeline objets à acheter → courses/budget
        resultats.append(await self.pipeline_objets_a_acheter(db))

        # Pipeline tâches récurrentes → planning
        resultats.append(await self.pipeline_taches_recurrentes_planning(db))

        # Log résumé
        succes = sum(1 for r in resultats if r.succes)
        logger.info(f"Pipelines terminés: {succes}/{len(resultats)} réussis")

        return resultats

    # ─────────────────────────────────────────────────────────
    # PIPELINE OBJETS → COURSES/BUDGET
    # ─────────────────────────────────────────────────────────

    async def pipeline_objets_a_acheter(
        self,
        db: Session | None = None,
    ) -> PipelineResult:
        """Pipeline: Objets à acheter/changer → Courses + Budget.

        Synchronise tous les objets marqués "à acheter" ou "à changer"
        avec la liste de courses et le budget familial.

        Args:
            db: Session DB optionnelle

        Returns:
            PipelineResult avec détails
        """
        logger.info("Pipeline objets à acheter → courses/budget")

        etapes_completees = []
        erreurs = []
        articles_courses = 0
        depenses_budget = 0

        try:
            # 1. Récupérer tous les objets à acheter/changer
            objets = await self._obtenir_objets_a_traiter(db)
            etapes_completees.append(f"Récupéré {len(objets)} objets à traiter")

            # 2. Pour chaque objet, vérifier s'il est déjà dans courses/budget
            for objet in objets:
                # Vérifier si déjà dans la liste de courses
                if objet.lien_course_id is None:
                    article = await self._creer_article_courses_depuis_objet(objet, db)
                    if article:
                        articles_courses += 1

                # Vérifier si déjà dans le budget
                if objet.lien_budget_id is None and objet.cout_remplacement_estime:
                    depense = await self._creer_depense_depuis_objet(objet, db)
                    if depense:
                        depenses_budget += 1

            etapes_completees.append(f"{articles_courses} articles ajoutés aux courses")
            etapes_completees.append(f"{depenses_budget} dépenses ajoutées au budget")

        except Exception as e:
            erreurs.append(f"Erreur pipeline objets: {str(e)}")
            logger.error(f"Pipeline objets échoué: {e}")

        return PipelineResult(
            succes=len(erreurs) == 0,
            pipeline="objets_a_acheter",
            etapes_completees=etapes_completees,
            erreurs=erreurs,
            metadata={
                "articles_courses_crees": articles_courses,
                "depenses_budget_creees": depenses_budget,
            },
        )

    async def _obtenir_objets_a_traiter(
        self,
        db: Session | None,
    ) -> list[ObjetAvecStatut]:
        """Récupère les objets à acheter/changer non encore synchronisés."""
        # TODO: Appeler inventaire_service.lister_objets_a_remplacer()
        # Pour l'instant, simulation
        return []

    async def _creer_article_courses_depuis_objet(
        self,
        objet: ObjetAvecStatut,
        db: Session | None,
    ) -> ArticleCoursesGenere | None:
        """Crée un article de courses depuis un objet à acheter."""
        try:
            # TODO: Appeler ServiceCourses.ajouter_article()
            article = ArticleCoursesGenere(
                nom=objet.nom,
                quantite=1,
                unite="unité",
                categorie=objet.categorie.value
                if hasattr(objet.categorie, "value")
                else str(objet.categorie),
                prix_estime=objet.cout_remplacement_estime,
                source="objet_a_acheter"
                if objet.statut == StatutObjet.A_ACHETER
                else "objet_a_changer",
                source_id=objet.id,
                priorite=self._convertir_priorite_objet(objet.priorite_remplacement),
            )
            logger.info(f"Article courses créé pour objet: {objet.nom}")
            return article
        except Exception as e:
            logger.error(f"Erreur création article courses: {e}")
            return None

    async def _creer_depense_depuis_objet(
        self,
        objet: ObjetAvecStatut,
        db: Session | None,
    ) -> LienObjetBudget | None:
        """Crée une dépense budget depuis un objet à acheter."""
        try:
            # TODO: Appeler BudgetService.ajouter_depense_prevue()
            lien = LienObjetBudget(
                objet_id=objet.id,
                objet_nom=objet.nom,
                montant_prevu=objet.cout_remplacement_estime or Decimal("0"),
                categorie_budget="equipement"
                if objet.statut == StatutObjet.A_ACHETER
                else "remplacement",
            )
            logger.info(f"Dépense budget créée pour objet: {objet.nom}")
            return lien
        except Exception as e:
            logger.error(f"Erreur création dépense budget: {e}")
            return None

    def _convertir_priorite_objet(
        self,
        priorite: PrioriteRemplacement | None,
    ) -> str:
        """Convertit la priorité objet en priorité courses."""
        if not priorite:
            return "normale"
        mapping = {
            PrioriteRemplacement.URGENTE: "urgente",
            PrioriteRemplacement.HAUTE: "haute",
            PrioriteRemplacement.NORMALE: "normale",
            PrioriteRemplacement.BASSE: "basse",
            PrioriteRemplacement.FUTURE: "basse",
        }
        return mapping.get(priorite, "normale")

    # ─────────────────────────────────────────────────────────
    # PIPELINE TÂCHES RÉCURRENTES → PLANNING
    # ─────────────────────────────────────────────────────────

    async def pipeline_taches_recurrentes_planning(
        self,
        db: Session | None = None,
    ) -> PipelineResult:
        """Pipeline: Tâches récurrentes maison → Planning familial.

        Synchronise les tâches d'entretien quotidiennes, hebdomadaires,
        mensuelles avec le calendrier/planning familial.

        Args:
            db: Session DB optionnelle

        Returns:
            PipelineResult avec événements créés
        """
        logger.info("Pipeline tâches récurrentes → planning")

        etapes_completees = []
        erreurs = []
        evenements_crees = 0

        try:
            # 1. Récupérer les tâches récurrentes actives
            taches = await self._obtenir_taches_recurrentes_actives(db)
            etapes_completees.append(f"Récupéré {len(taches)} tâches récurrentes")

            # 2. Pour chaque tâche, calculer les prochaines occurrences
            for tache in taches:
                prochaines_dates = self._calculer_prochaines_occurrences(
                    tache,
                    periode_jours=30,  # Planifier sur 1 mois
                )

                # 3. Créer les événements dans le planning
                for date_tache in prochaines_dates:
                    succes = await self._creer_evenement_planning(tache, date_tache, db)
                    if succes:
                        evenements_crees += 1

            etapes_completees.append(f"{evenements_crees} événements créés dans le planning")

        except Exception as e:
            erreurs.append(f"Erreur pipeline tâches: {str(e)}")
            logger.error(f"Pipeline tâches récurrentes échoué: {e}")

        return PipelineResult(
            succes=len(erreurs) == 0,
            pipeline="taches_recurrentes_planning",
            etapes_completees=etapes_completees,
            erreurs=erreurs,
            metadata={
                "evenements_crees": evenements_crees,
            },
        )

    async def _obtenir_taches_recurrentes_actives(
        self,
        db: Session | None,
    ) -> list[TacheMaisonRecurrente]:
        """Récupère les tâches récurrentes actives."""
        # TODO: Appeler entretien_service.lister_taches_recurrentes()
        # Simulation avec tâches types
        return [
            TacheMaisonRecurrente(
                id=1,
                nom="Ménage complet",
                categorie="entretien",
                frequence=FrequenceTache.HEBDOMADAIRE,
                jour_semaine=5,  # Samedi
                duree_estimee_min=120,
                priorite=NiveauUrgence.MOYENNE,
                actif=True,
            ),
            TacheMaisonRecurrente(
                id=2,
                nom="Arrosage plantes",
                categorie="jardin",
                frequence=FrequenceTache.BIHEBDOMADAIRE,
                duree_estimee_min=30,
                priorite=NiveauUrgence.HAUTE,
                actif=True,
            ),
            TacheMaisonRecurrente(
                id=3,
                nom="Vérifier détecteurs fumée",
                categorie="entretien",
                frequence=FrequenceTache.MENSUEL,
                jour_mois=1,
                duree_estimee_min=15,
                priorite=NiveauUrgence.HAUTE,
                actif=True,
            ),
        ]

    def _calculer_prochaines_occurrences(
        self,
        tache: TacheMaisonRecurrente,
        periode_jours: int = 30,
    ) -> list[date]:
        """Calcule les prochaines dates d'exécution d'une tâche."""
        dates = []
        aujourd_hui = date.today()
        date_fin = aujourd_hui + timedelta(days=periode_jours)

        if tache.frequence == FrequenceTache.QUOTIDIEN:
            # Tous les jours
            current = aujourd_hui
            while current <= date_fin:
                dates.append(current)
                current += timedelta(days=1)

        elif tache.frequence == FrequenceTache.HEBDOMADAIRE:
            # Tous les X jours de la semaine
            if tache.jour_semaine is not None:
                current = aujourd_hui
                while current <= date_fin:
                    if current.weekday() == tache.jour_semaine:
                        dates.append(current)
                    current += timedelta(days=1)

        elif tache.frequence == FrequenceTache.BIHEBDOMADAIRE:
            # Toutes les 2 semaines
            if tache.jour_semaine is not None:
                current = aujourd_hui
                semaines_depuis_derniere = 0
                while current <= date_fin:
                    if current.weekday() == tache.jour_semaine:
                        if semaines_depuis_derniere % 2 == 0:
                            dates.append(current)
                        semaines_depuis_derniere += 1
                    current += timedelta(days=1)

        elif tache.frequence == FrequenceTache.MENSUEL:
            # Un jour spécifique du mois
            if tache.jour_mois is not None:
                current = aujourd_hui.replace(day=1)
                while current <= date_fin:
                    try:
                        date_tache = current.replace(day=tache.jour_mois)
                        if date_tache >= aujourd_hui and date_tache <= date_fin:
                            dates.append(date_tache)
                    except ValueError:
                        # Jour invalide (ex: 31 février)
                        pass
                    # Passer au mois suivant
                    if current.month == 12:
                        current = current.replace(year=current.year + 1, month=1)
                    else:
                        current = current.replace(month=current.month + 1)

        return dates[:10]  # Limiter à 10 occurrences max

    async def _creer_evenement_planning(
        self,
        tache: TacheMaisonRecurrente,
        date_evenement: date,
        db: Session | None,
    ) -> bool:
        """Crée un événement dans le planning familial."""
        try:
            # TODO: Appeler ServicePlanning.creer_evenement()
            # ou ServicePlanningUnifie.ajouter_tache()
            logger.info(f"Événement planning: {tache.nom} le {date_evenement}")
            return True
        except Exception as e:
            logger.error(f"Erreur création événement planning: {e}")
            return False

    async def synchroniser_planning(
        self,
        request: SyncPlanningRequest,
        db: Session | None = None,
    ) -> SyncPlanningResult:
        """Synchronisation complète avec le planning familial.

        Permet de synchroniser manuellement:
        - Tâches spécifiques
        - Projets avec deadlines
        - Tâches récurrentes

        Args:
            request: Paramètres de synchronisation
            db: Session DB optionnelle

        Returns:
            SyncPlanningResult avec détails
        """
        logger.info("Synchronisation manuelle avec planning familial")

        evenements_crees = 0
        evenements_maj = 0
        conflits = []
        prochains_evenements = []

        try:
            # 1. Synchroniser les tâches spécifiques
            if request.taches_a_synchroniser:
                for tache_id in request.taches_a_synchroniser:
                    # TODO: Récupérer et synchroniser
                    evenements_crees += 1

            # 2. Synchroniser les projets
            if request.projets_a_synchroniser:
                for projet_id in request.projets_a_synchroniser:
                    # TODO: Récupérer et synchroniser
                    evenements_crees += 1

            # 3. Synchroniser les tâches récurrentes
            if request.inclure_recurrentes:
                result = await self.pipeline_taches_recurrentes_planning(db)
                evenements_crees += result.metadata.get("evenements_crees", 0)

        except Exception as e:
            logger.error(f"Erreur synchronisation planning: {e}")

        return SyncPlanningResult(
            succes=True,
            evenements_crees=evenements_crees,
            evenements_mis_a_jour=evenements_maj,
            conflits_detectes=conflits,
            prochains_evenements=prochains_evenements,
            message=f"Synchronisation terminée: {evenements_crees} événements créés",
        )


# ═══════════════════════════════════════════════════════════
# FACTORY
# ═══════════════════════════════════════════════════════════


def get_maison_integration_service(
    client: ClientIA | None = None,
) -> MaisonIntegrationService:
    """Factory pour obtenir le service d'intégration maison.

    Args:
        client: Client IA optionnel

    Returns:
        Instance de MaisonIntegrationService
    """
    return MaisonIntegrationService(client=client)
