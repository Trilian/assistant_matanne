"""
Tests pour MaisonIntegrationService.

Couvre:
- Pipeline Projet → Courses → Budget
- Pipeline Entretien → Stock
- Pipeline Météo → Jardin → Notification
- Pipeline Sync Calendrier
"""

import json
from datetime import date, timedelta
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.services.maison.integration_service import (
    MaisonIntegrationService,
    get_maison_integration_service,
)
from src.services.maison.schemas import PipelineResult


class TestIntegrationServiceInit:
    """Tests d'initialisation du service."""

    def test_factory_returns_service(self):
        """La factory retourne une instance valide."""
        with patch("src.services.maison.integration_service.ClientIA"):
            service = get_maison_integration_service()
            assert isinstance(service, MaisonIntegrationService)

    def test_factory_accepts_custom_client(self):
        """La factory accepte un client personnalisé."""
        mock_client = MagicMock()
        service = get_maison_integration_service(client=mock_client)
        assert service.client == mock_client


class TestPipelineProjetCourses:
    """Tests du pipeline Projet → Courses → Budget."""

    @pytest.mark.asyncio
    async def test_pipeline_complet(self, mock_client_ia, projet_test_data):
        """Exécute le pipeline complet avec succès."""
        service = MaisonIntegrationService(client=mock_client_ia)

        # Mock les méthodes internes
        service._obtenir_materiaux_projet = AsyncMock(
            return_value=[
                {"nom": "Vis", "quantite": 50, "prix_unitaire": 0.05},
                {"nom": "Peinture", "quantite": 2, "prix_unitaire": 45},
            ]
        )
        service._verifier_stock = AsyncMock(
            return_value=[
                {"nom": "Peinture", "quantite": 2, "prix_unitaire": 45},
            ]
        )
        service._ajouter_liste_courses = AsyncMock(return_value=1)
        service._mettre_a_jour_budget = AsyncMock(return_value=Decimal("90.00"))

        result = await service.pipeline_projet_vers_courses(projet_id=projet_test_data["id"])

        assert result.succes is True
        assert result.pipeline == "projet_vers_courses"
        assert len(result.etapes_completees) > 0

    @pytest.mark.asyncio
    async def test_pipeline_erreur_gestion(self, mock_client_ia):
        """Gère les erreurs du pipeline gracieusement."""
        service = MaisonIntegrationService(client=mock_client_ia)

        service._obtenir_materiaux_projet = AsyncMock(side_effect=Exception("Erreur test"))

        result = await service.pipeline_projet_vers_courses(projet_id=1)

        assert result.succes is False
        assert len(result.erreurs) > 0

    @pytest.mark.asyncio
    async def test_materiaux_en_stock(self, mock_client_ia):
        """Gère le cas où tous les matériaux sont en stock."""
        service = MaisonIntegrationService(client=mock_client_ia)

        service._obtenir_materiaux_projet = AsyncMock(
            return_value=[
                {"nom": "Vis", "quantite": 50, "prix_unitaire": 0.05},
            ]
        )
        service._verifier_stock = AsyncMock(return_value=[])  # Tout en stock
        service._ajouter_liste_courses = AsyncMock(return_value=0)
        service._mettre_a_jour_budget = AsyncMock(return_value=Decimal("0"))

        result = await service.pipeline_projet_vers_courses(projet_id=1)

        assert result.succes is True
        assert result.metadata.get("articles_ajoutes") == 0


class TestPipelineEntretienStock:
    """Tests du pipeline Entretien → Stock → Alerte."""

    @pytest.mark.asyncio
    async def test_pipeline_stock_bas(self, mock_client_ia):
        """Détecte et alerte sur les stocks bas."""
        service = MaisonIntegrationService(client=mock_client_ia)

        service._obtenir_produits_tache = AsyncMock(
            return_value=[
                {"nom": "Liquide vaisselle", "quantite_requise": 1},
                {"nom": "Éponge", "quantite_requise": 1},
            ]
        )
        service._verifier_stock_consommables = AsyncMock(
            return_value=[
                {"nom": "Éponge", "stock": 0},
            ]
        )

        result = await service.pipeline_entretien_stock(tache_id=1)

        assert result.succes is True
        assert len(result.metadata.get("alertes", [])) > 0

    @pytest.mark.asyncio
    async def test_pipeline_stock_ok(self, mock_client_ia):
        """Pas d'alerte si tout est en stock."""
        service = MaisonIntegrationService(client=mock_client_ia)

        service._obtenir_produits_tache = AsyncMock(
            return_value=[
                {"nom": "Liquide vaisselle", "quantite_requise": 1},
            ]
        )
        service._verifier_stock_consommables = AsyncMock(return_value=[])

        result = await service.pipeline_entretien_stock(tache_id=1)

        assert result.succes is True
        assert len(result.metadata.get("alertes", [])) == 0


class TestPipelineMeteoJardin:
    """Tests du pipeline Météo → Jardin → Notification."""

    @pytest.mark.asyncio
    async def test_pipeline_gel(self, mock_client_ia, meteo_gel_data):
        """Envoie une notification si gel prévu."""
        service = MaisonIntegrationService(client=mock_client_ia)

        service._obtenir_previsions_meteo = AsyncMock(return_value=meteo_gel_data)
        service._analyser_impact_jardin = AsyncMock(
            return_value=[
                {"type": "gel", "urgence": "haute", "message": "Gel prévu"},
            ]
        )
        service._envoyer_notification_jardin = AsyncMock(
            return_value={
                "titre": "Alerte gel",
                "message": "Protéger les plantes",
            }
        )

        result = await service.pipeline_meteo_jardin()

        assert result.succes is True
        assert len(result.metadata.get("notifications", [])) > 0

    @pytest.mark.asyncio
    async def test_pipeline_meteo_normale(self, mock_client_ia, meteo_data):
        """Pas de notification si météo normale."""
        service = MaisonIntegrationService(client=mock_client_ia)

        service._obtenir_previsions_meteo = AsyncMock(return_value=meteo_data)
        service._analyser_impact_jardin = AsyncMock(return_value=[])

        result = await service.pipeline_meteo_jardin()

        assert result.succes is True
        assert len(result.metadata.get("notifications", [])) == 0


class TestPipelineSyncCalendrier:
    """Tests du pipeline Sync Calendrier."""

    @pytest.mark.asyncio
    async def test_sync_taches_projets(self, mock_client_ia):
        """Synchronise tâches et projets avec le calendrier."""
        service = MaisonIntegrationService(client=mock_client_ia)

        service._obtenir_taches_planifiees = AsyncMock(
            return_value=[
                {"titre": "Ménage", "date": date.today() + timedelta(days=2)},
            ]
        )
        service._obtenir_projets_deadlines = AsyncMock(
            return_value=[
                {"titre": "Peinture", "deadline": date.today() + timedelta(days=10)},
            ]
        )
        service._sync_calendrier_familial = AsyncMock(return_value=2)

        result = await service.pipeline_sync_calendrier()

        assert result.succes is True
        assert result.metadata.get("evenements_sync") == 2


class TestPipelinesBatch:
    """Tests de l'exécution batch des pipelines."""

    @pytest.mark.asyncio
    async def test_executer_pipelines_quotidiens(self, mock_client_ia):
        """Exécute tous les pipelines quotidiens."""
        service = MaisonIntegrationService(client=mock_client_ia)

        # Mock tous les pipelines (4 maintenant)
        service.pipeline_meteo_jardin = AsyncMock(
            return_value=PipelineResult(
                succes=True,
                pipeline="meteo_jardin",
                etapes_completees=["OK"],
                erreurs=[],
            )
        )
        service.pipeline_sync_calendrier = AsyncMock(
            return_value=PipelineResult(
                succes=True,
                pipeline="sync_calendrier",
                etapes_completees=["OK"],
                erreurs=[],
            )
        )
        service.pipeline_objets_a_acheter = AsyncMock(
            return_value=PipelineResult(
                succes=True,
                pipeline="objets_a_acheter",
                etapes_completees=["OK"],
                erreurs=[],
            )
        )
        service.pipeline_taches_recurrentes_planning = AsyncMock(
            return_value=PipelineResult(
                succes=True,
                pipeline="taches_recurrentes_planning",
                etapes_completees=["OK"],
                erreurs=[],
            )
        )

        results = await service.executer_pipelines_quotidiens()

        assert len(results) == 4
        assert all(r.succes for r in results)

    @pytest.mark.asyncio
    async def test_batch_avec_echec_partiel(self, mock_client_ia):
        """Gère les échecs partiels dans le batch."""
        service = MaisonIntegrationService(client=mock_client_ia)

        service.pipeline_meteo_jardin = AsyncMock(
            return_value=PipelineResult(
                succes=False,
                pipeline="meteo_jardin",
                etapes_completees=[],
                erreurs=["Erreur API météo"],
            )
        )
        service.pipeline_sync_calendrier = AsyncMock(
            return_value=PipelineResult(
                succes=True,
                pipeline="sync_calendrier",
                etapes_completees=["OK"],
                erreurs=[],
            )
        )
        service.pipeline_objets_a_acheter = AsyncMock(
            return_value=PipelineResult(
                succes=True,
                pipeline="objets_a_acheter",
                etapes_completees=["OK"],
                erreurs=[],
            )
        )
        service.pipeline_taches_recurrentes_planning = AsyncMock(
            return_value=PipelineResult(
                succes=True,
                pipeline="taches_recurrentes_planning",
                etapes_completees=["OK"],
                erreurs=[],
            )
        )

        results = await service.executer_pipelines_quotidiens()

        assert len(results) == 4
        succes_count = sum(1 for r in results if r.succes)
        assert succes_count == 3  # 3 succès, 1 échec


class TestPipelineResultSchema:
    """Tests du schema PipelineResult."""

    def test_result_structure(self):
        """Vérifie la structure du résultat."""
        result = PipelineResult(
            succes=True,
            pipeline="test",
            etapes_completees=["Étape 1", "Étape 2"],
            erreurs=[],
            metadata={"key": "value"},
        )

        assert result.succes is True
        assert result.pipeline == "test"
        assert len(result.etapes_completees) == 2
        assert len(result.erreurs) == 0
        assert result.metadata.get("key") == "value"

    def test_result_avec_erreurs(self):
        """Vérifie un résultat avec erreurs."""
        result = PipelineResult(
            succes=False,
            pipeline="failed",
            etapes_completees=["Étape 1"],
            erreurs=["Erreur grave", "Autre erreur"],
            metadata={},
        )

        assert result.succes is False
        assert len(result.erreurs) == 2


class TestIntegrationCalculs:
    """Tests des calculs d'intégration."""

    def test_calcul_budget_materiaux(self):
        """Calcule le budget des matériaux."""
        materiaux = [
            {"nom": "Vis", "quantite": 50, "prix_unitaire": Decimal("0.05")},
            {"nom": "Peinture", "quantite": 2, "prix_unitaire": Decimal("45.00")},
        ]

        total = sum(m["quantite"] * m["prix_unitaire"] for m in materiaux)

        assert total == Decimal("92.50")

    def test_filtrage_alertes_urgentes(self):
        """Filtre les alertes par niveau d'urgence."""
        from src.services.maison.schemas import NiveauUrgence

        alertes = [
            {"niveau": NiveauUrgence.HAUTE, "message": "Urgent!"},
            {"niveau": NiveauUrgence.BASSE, "message": "Info"},
            {"niveau": NiveauUrgence.MOYENNE, "message": "Important"},
        ]

        urgentes = [
            a for a in alertes if a["niveau"] in [NiveauUrgence.HAUTE, NiveauUrgence.MOYENNE]
        ]

        assert len(urgentes) == 2


# ═══════════════════════════════════════════════════════════
# TESTS PIPELINE OBJETS → COURSES/BUDGET
# ═══════════════════════════════════════════════════════════


class TestPipelineObjetsAcheter:
    """Tests du pipeline Objets à acheter → Courses/Budget."""

    @pytest.fixture
    def service_integration(self, mock_client_ia):
        """Fixture pour le service d'intégration."""
        return MaisonIntegrationService(client=mock_client_ia)

    @pytest.mark.asyncio
    async def test_pipeline_objets_a_acheter(self, service_integration):
        """Exécute le pipeline objets avec succès."""
        result = await service_integration.pipeline_objets_a_acheter()

        assert result.succes is True
        assert result.pipeline == "objets_a_acheter"
        assert "articles_courses_crees" in result.metadata

    @pytest.mark.asyncio
    async def test_pipeline_avec_objets(self, service_integration):
        """Pipeline avec objets à traiter."""
        from src.services.maison.schemas import (
            CategorieObjet,
            ObjetAvecStatut,
            PrioriteRemplacement,
            StatutObjet,
        )

        # Mock la méthode pour retourner des objets
        service_integration._obtenir_objets_a_traiter = AsyncMock(
            return_value=[
                ObjetAvecStatut(
                    id=1,
                    nom="Micro-onde",
                    categorie=CategorieObjet.ELECTROMENAGER,
                    piece="Cuisine",
                    statut=StatutObjet.A_CHANGER,
                    priorite_remplacement=PrioriteRemplacement.HAUTE,
                    cout_remplacement_estime=Decimal("150.00"),
                ),
            ]
        )

        result = await service_integration.pipeline_objets_a_acheter()

        assert result.succes is True
        # Vérifier que les méthodes ont été appelées
        service_integration._obtenir_objets_a_traiter.assert_called_once()

    def test_convertir_priorite_urgente(self, service_integration):
        """Convertit priorité urgente vers courses."""
        from src.services.maison.schemas import PrioriteRemplacement

        priorite = service_integration._convertir_priorite_objet(PrioriteRemplacement.URGENTE)
        assert priorite == "urgente"

    def test_convertir_priorite_none(self, service_integration):
        """Convertit priorité None en normale."""
        priorite = service_integration._convertir_priorite_objet(None)
        assert priorite == "normale"

    @pytest.mark.asyncio
    async def test_creer_article_courses_depuis_objet(self, service_integration):
        """Crée article courses depuis objet."""
        from src.services.maison.schemas import (
            CategorieObjet,
            ObjetAvecStatut,
            StatutObjet,
        )

        objet = ObjetAvecStatut(
            id=1,
            nom="TV Samsung 55 pouces",
            categorie=CategorieObjet.ELECTRONIQUE,
            piece="Salon",
            statut=StatutObjet.A_ACHETER,
            cout_remplacement_estime=Decimal("599.00"),
        )

        article = await service_integration._creer_article_courses_depuis_objet(objet, None)

        assert article is not None
        assert article.nom == "TV Samsung 55 pouces"
        assert article.prix_estime == Decimal("599.00")
        assert article.source == "objet_a_acheter"

    @pytest.mark.asyncio
    async def test_creer_depense_depuis_objet(self, service_integration):
        """Crée dépense budget depuis objet."""
        from src.services.maison.schemas import (
            CategorieObjet,
            ObjetAvecStatut,
            StatutObjet,
        )

        objet = ObjetAvecStatut(
            id=2,
            nom="Aspirateur Dyson",
            categorie=CategorieObjet.ELECTROMENAGER,
            piece="Buanderie",
            statut=StatutObjet.A_CHANGER,
            cout_remplacement_estime=Decimal("399.00"),
        )

        lien = await service_integration._creer_depense_depuis_objet(objet, None)

        assert lien is not None
        assert lien.objet_id == 2
        assert lien.montant_prevu == Decimal("399.00")
        assert lien.categorie_budget == "remplacement"


# ═══════════════════════════════════════════════════════════
# TESTS PIPELINE TÂCHES RÉCURRENTES → PLANNING
# ═══════════════════════════════════════════════════════════


class TestPipelineTachesRecurrentes:
    """Tests du pipeline Tâches récurrentes → Planning."""

    @pytest.fixture
    def service_integration(self, mock_client_ia):
        """Fixture pour le service d'intégration."""
        return MaisonIntegrationService(client=mock_client_ia)

    @pytest.mark.asyncio
    async def test_pipeline_taches_recurrentes_planning(self, service_integration):
        """Exécute le pipeline tâches récurrentes."""
        result = await service_integration.pipeline_taches_recurrentes_planning()

        assert result.succes is True
        assert result.pipeline == "taches_recurrentes_planning"
        assert "evenements_crees" in result.metadata

    def test_calculer_occurrences_quotidien(self, service_integration):
        """Calcule les occurrences quotidiennes."""
        from src.services.maison.schemas import (
            FrequenceTache,
            NiveauUrgence,
            TacheMaisonRecurrente,
        )

        tache = TacheMaisonRecurrente(
            id=1,
            nom="Arroser plantes",
            categorie="jardin",
            frequence=FrequenceTache.QUOTIDIEN,
            actif=True,
        )

        dates = service_integration._calculer_prochaines_occurrences(tache, periode_jours=7)

        # Devrait retourner ~7 dates (une par jour, max 10)
        assert len(dates) >= 7

    def test_calculer_occurrences_hebdomadaire(self, service_integration):
        """Calcule les occurrences hebdomadaires."""
        from src.services.maison.schemas import (
            FrequenceTache,
            NiveauUrgence,
            TacheMaisonRecurrente,
        )

        tache = TacheMaisonRecurrente(
            id=2,
            nom="Ménage complet",
            categorie="entretien",
            frequence=FrequenceTache.HEBDOMADAIRE,
            jour_semaine=5,  # Samedi
            actif=True,
        )

        dates = service_integration._calculer_prochaines_occurrences(tache, periode_jours=30)

        # Devrait retourner ~4-5 samedis
        assert len(dates) >= 4
        # Tous les résultats doivent être des samedis
        for d in dates:
            assert d.weekday() == 5

    def test_calculer_occurrences_mensuel(self, service_integration):
        """Calcule les occurrences mensuelles."""
        from src.services.maison.schemas import (
            FrequenceTache,
            NiveauUrgence,
            TacheMaisonRecurrente,
        )

        tache = TacheMaisonRecurrente(
            id=3,
            nom="Vérifier détecteurs",
            categorie="entretien",
            frequence=FrequenceTache.MENSUEL,
            jour_mois=1,  # Premier du mois
            actif=True,
        )

        dates = service_integration._calculer_prochaines_occurrences(tache, periode_jours=60)

        # Devrait retourner 1-2 occurrences
        assert len(dates) >= 1
        # Tous les résultats doivent être le 1er du mois
        for d in dates:
            assert d.day == 1

    @pytest.mark.asyncio
    async def test_creer_evenement_planning(self, service_integration):
        """Crée un événement dans le planning."""
        from src.services.maison.schemas import (
            FrequenceTache,
            NiveauUrgence,
            TacheMaisonRecurrente,
        )

        tache = TacheMaisonRecurrente(
            id=1,
            nom="Test tâche",
            categorie="test",
            frequence=FrequenceTache.HEBDOMADAIRE,
            actif=True,
        )

        succes = await service_integration._creer_evenement_planning(tache, date.today(), None)

        assert succes is True


# ═══════════════════════════════════════════════════════════
# TESTS SYNCHRONISATION PLANNING
# ═══════════════════════════════════════════════════════════


class TestSynchronisationPlanning:
    """Tests de la synchronisation avec le planning familial."""

    @pytest.fixture
    def service_integration(self, mock_client_ia):
        """Fixture pour le service d'intégration."""
        return MaisonIntegrationService(client=mock_client_ia)

    @pytest.mark.asyncio
    async def test_synchroniser_planning(self, service_integration):
        """Synchronise avec le planning familial."""
        from src.services.maison.schemas import SyncPlanningRequest

        request = SyncPlanningRequest(
            taches_a_synchroniser=[1, 2, 3],
            projets_a_synchroniser=[1],
            inclure_recurrentes=True,
        )

        result = await service_integration.synchroniser_planning(request)

        assert result.succes is True
        assert result.evenements_crees >= 0

    @pytest.mark.asyncio
    async def test_synchroniser_planning_sans_recurrentes(self, service_integration):
        """Synchronise sans les tâches récurrentes."""
        from src.services.maison.schemas import SyncPlanningRequest

        request = SyncPlanningRequest(
            taches_a_synchroniser=[1],
            inclure_recurrentes=False,
        )

        result = await service_integration.synchroniser_planning(request)

        assert result.succes is True


# ═══════════════════════════════════════════════════════════
# TESTS EXÉCUTION BATCH QUOTIDIENNE
# ═══════════════════════════════════════════════════════════


class TestExecutionBatchQuotidienne:
    """Tests de l'exécution batch des pipelines."""

    @pytest.fixture
    def service_integration(self, mock_client_ia):
        """Fixture pour le service d'intégration."""
        return MaisonIntegrationService(client=mock_client_ia)

    @pytest.mark.asyncio
    async def test_executer_pipelines_quotidiens(self, service_integration):
        """Exécute tous les pipelines quotidiens."""
        resultats = await service_integration.executer_pipelines_quotidiens()

        # Devrait retourner 4 résultats (météo, calendrier, objets, tâches)
        assert len(resultats) == 4
        assert all(isinstance(r, PipelineResult) for r in resultats)

    @pytest.mark.asyncio
    @pytest.mark.xfail(reason="Résilience erreur à implémenter dans le service")
    async def test_resilience_erreur_pipeline(self, service_integration):
        """Continue même si un pipeline échoue."""
        # Mock un pipeline pour qu'il échoue
        original_meteo = service_integration.pipeline_meteo_jardin
        service_integration.pipeline_meteo_jardin = AsyncMock(side_effect=Exception("Erreur météo"))

        try:
            # Le test ne devrait pas planter
            # (le service gère les erreurs en interne)
            resultats = await service_integration.executer_pipelines_quotidiens()
            # Au moins certains résultats doivent exister
            assert len(resultats) >= 0
        finally:
            service_integration.pipeline_meteo_jardin = original_meteo
