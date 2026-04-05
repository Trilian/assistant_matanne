"""
Tests unitaires pour les services IA de la Phase 6.

Couvre: NotesIAService, MemoVocalService, JardinAnomaliesIAService,
InsightsAnalyticsService, GroupeurNotifications, ChatAIService (contexte).
"""

import pytest
from unittest.mock import Mock, patch

# ──────────────────────────────────────────────
# NotesIAService
# ──────────────────────────────────────────────

from src.services.utilitaires.notes_ia import (
    NotesIAService,
    TagsProposes,
    TAGS_DISPONIBLES,
)


class TestNotesIAService:
    """Tests pour le service d'auto-étiquetage des notes."""

    @pytest.fixture
    def service(self):
        with patch("src.services.utilitaires.notes_ia.obtenir_client_ia", return_value=Mock()):
            return NotesIAService()

    def test_auto_etiqueter_contenu_vide(self, service):
        """Contenu et titre vides → tags vides."""
        result = service.auto_etiqueter(contenu="", titre="")
        assert result.tags == []
        assert result.confiance == 0.0

    def test_auto_etiqueter_retour_ia(self, service):
        """IA retourne des tags → filtrage et retour."""
        service.call_with_parsing_sync = Mock(
            return_value=TagsProposes(tags=["courses", "recette"], confiance=0.9)
        )
        result = service.auto_etiqueter(contenu="Acheter du lait et des oeufs pour la tarte")
        assert "courses" in result.tags
        assert "recette" in result.tags
        assert result.confiance == 0.9

    def test_auto_etiqueter_filtre_tags_invalides(self, service):
        """L'IA retourne des tags hors liste → ils sont filtrés."""
        service.call_with_parsing_sync = Mock(
            return_value=TagsProposes(tags=["courses", "tag_inventé", "maison"], confiance=0.8)
        )
        result = service.auto_etiqueter(contenu="Réparer le robinet et acheter du lait")
        assert "courses" in result.tags
        assert "maison" in result.tags
        assert "tag_inventé" not in result.tags

    def test_auto_etiqueter_ia_none(self, service):
        """IA retourne None → fallback tags vides."""
        service.call_with_parsing_sync = Mock(return_value=None)
        result = service.auto_etiqueter(contenu="Un texte quelconque")
        assert result.tags == []
        assert result.confiance == 0.0

    def test_auto_etiqueter_avec_titre(self, service):
        """Le titre est inclus dans le prompt envoyé à l'IA."""
        service.call_with_parsing_sync = Mock(
            return_value=TagsProposes(tags=["jardin"], confiance=0.85)
        )
        result = service.auto_etiqueter(contenu="Arroser les tomates", titre="Jardin")
        service.call_with_parsing_sync.assert_called_once()
        prompt = service.call_with_parsing_sync.call_args.kwargs.get(
            "prompt", service.call_with_parsing_sync.call_args[1].get("prompt", "")
        )
        assert "Jardin" in prompt
        assert result.tags == ["jardin"]

    def test_tags_disponibles_coherents(self):
        """Vérifie que la liste de tags contient les catégories attendues."""
        attendus = ["courses", "recette", "maison", "jardin", "jules", "famille", "budget"]
        for tag in attendus:
            assert tag in TAGS_DISPONIBLES


# ──────────────────────────────────────────────
# MemoVocalService
# ──────────────────────────────────────────────

from src.services.utilitaires.memo_vocal import (
    MemoVocalService,
    MemoClassifie,
    MODULES_VALIDES,
    ACTIONS_VALIDES,
    MODULE_URLS,
)


class TestMemoVocalService:
    """Tests pour le service de classification des mémos vocaux."""

    @pytest.fixture
    def service(self):
        with patch("src.services.utilitaires.memo_vocal.obtenir_client_ia", return_value=Mock()):
            return MemoVocalService()

    def test_texte_vide(self, service):
        """Texte vide → module note, confiance 0."""
        result = service.transcrire_et_classer("")
        assert result.module == "note"
        assert result.confiance == 0.0

    def test_texte_none_like(self, service):
        """Texte whitespace → même fallback."""
        result = service.transcrire_et_classer("   ")
        assert result.module == "note"
        assert result.confiance == 0.0

    def test_classification_courses(self, service):
        """Mémo courses → module courses."""
        service.call_with_parsing_sync = Mock(
            return_value=MemoClassifie(
                module="courses",
                action="ajouter",
                contenu="lait, pain",
                tags=["alimentation"],
                confiance=0.92,
            )
        )
        result = service.transcrire_et_classer("Acheter du lait et du pain")
        assert result.module == "courses"
        assert result.action == "ajouter"
        assert result.destination_url == "/cuisine/courses"

    def test_classification_jardin(self, service):
        """Mémo jardin → module jardin."""
        service.call_with_parsing_sync = Mock(
            return_value=MemoClassifie(
                module="jardin",
                action="rappel",
                contenu="arroser les tomates",
                tags=["potager"],
                confiance=0.85,
            )
        )
        result = service.transcrire_et_classer("Arroser les tomates demain")
        assert result.module == "jardin"
        assert result.destination_url == "/maison/jardin"

    def test_module_invalide_normalise(self, service):
        """Module inconnu → normalisé en 'note'."""
        service.call_with_parsing_sync = Mock(
            return_value=MemoClassifie(
                module="inconnu",
                action="ajouter",
                contenu="test",
                confiance=0.7,
            )
        )
        result = service.transcrire_et_classer("Un mémo quelconque")
        assert result.module == "note"
        assert result.destination_url == "/outils/notes"

    def test_action_invalide_normalise(self, service):
        """Action inconnue → normalisée en 'ajouter'."""
        service.call_with_parsing_sync = Mock(
            return_value=MemoClassifie(
                module="maison",
                action="detruire",
                contenu="test",
                confiance=0.8,
            )
        )
        result = service.transcrire_et_classer("Quelque chose pour la maison")
        assert result.action == "ajouter"

    def test_ia_none_fallback(self, service):
        """IA retourne None → fallback avec le texte original."""
        service.call_with_parsing_sync = Mock(return_value=None)
        result = service.transcrire_et_classer("Texte quelconque")
        assert result.module == "note"
        assert result.contenu == "Texte quelconque"
        assert result.confiance == 0.3

    def test_truncate_long_text(self, service):
        """Texte très long → tronqué à 2000 caractères dans le prompt."""
        service.call_with_parsing_sync = Mock(
            return_value=MemoClassifie(module="note", action="ajouter", contenu="...", confiance=0.5)
        )
        result = service.transcrire_et_classer("a" * 5000)
        prompt = service.call_with_parsing_sync.call_args.kwargs.get(
            "prompt", service.call_with_parsing_sync.call_args[1].get("prompt", "")
        )
        # Le texte dans le prompt ne doit pas dépasser 2000 chars de l'input
        assert "a" * 2001 not in prompt

    def test_tous_modules_ont_url(self):
        """Chaque module valide a une URL destination."""
        for module in MODULES_VALIDES:
            assert module in MODULE_URLS, f"Module {module} manque dans MODULE_URLS"


# ──────────────────────────────────────────────
# JardinAnomaliesIAService
# ──────────────────────────────────────────────

from src.services.maison.ia.jardin_anomalies_ia import (
    JardinAnomaliesIAService,
    AnomalieJardin,
    AnomaliesJardinResponse,
)


class TestJardinAnomaliesIAService:
    """Tests pour le service de détection d'anomalies jardin."""

    @pytest.fixture
    def service(self):
        with patch("src.services.maison.ia.jardin_anomalies_ia.obtenir_client_ia", return_value=Mock()):
            return JardinAnomaliesIAService()

    def test_aucune_plante(self, service):
        """Liste de plantes vide → score 100, message informatif."""
        result = service.detecter_anomalies(plantes=[])
        assert result.score_sante_jardin == 100.0
        assert len(result.recommandations_generales) > 0
        assert result.anomalies == []

    def test_detection_avec_plantes(self, service):
        """Plantes fournies → IA retourne des anomalies."""
        service.call_with_parsing_sync = Mock(
            return_value=AnomaliesJardinResponse(
                anomalies=[
                    AnomalieJardin(
                        plante="Tomate",
                        type_anomalie="stress_hydrique",
                        severite="moyenne",
                        description="Manque d'eau détecté",
                        action_recommandee="Augmenter l'arrosage",
                    )
                ],
                recommandations_generales=["Penser à pailler"],
                score_sante_jardin=72.0,
            )
        )
        plantes = [
            {"nom": "Tomate", "date_plantation": "2026-03-15", "etat": "jaunissement", "frequence_arrosage": "2x/semaine"},
            {"nom": "Basilic", "date_plantation": "2026-03-20", "etat": "normal", "frequence_arrosage": "quotidien"},
        ]
        result = service.detecter_anomalies(plantes=plantes, saison="printemps")
        assert len(result.anomalies) == 1
        assert result.anomalies[0].plante == "Tomate"
        assert result.anomalies[0].type_anomalie == "stress_hydrique"
        assert result.score_sante_jardin == 72.0

    def test_ia_none_fallback(self, service):
        """IA retourne None → score 50 par défaut."""
        service.call_with_parsing_sync = Mock(return_value=None)
        result = service.detecter_anomalies(
            plantes=[{"nom": "Rose", "etat": "normal"}]
        )
        assert result.score_sante_jardin == 50.0
        assert "indisponible" in result.recommandations_generales[0].lower()

    def test_avec_meteo(self, service):
        """Données météo incluses dans le prompt."""
        service.call_with_parsing_sync = Mock(
            return_value=AnomaliesJardinResponse(
                score_sante_jardin=80.0,
                recommandations_generales=["Protéger du gel"],
            )
        )
        plantes = [{"nom": "Lavande", "etat": "normal"}]
        meteo = [
            {"date": "2026-04-01", "temperature_min": -2, "temperature_max": 8, "pluie_mm": 0},
        ]
        result = service.detecter_anomalies(plantes=plantes, meteo_recente=meteo, saison="printemps")
        prompt = service.call_with_parsing_sync.call_args.kwargs.get(
            "prompt", service.call_with_parsing_sync.call_args[1].get("prompt", "")
        )
        assert "-2" in prompt  # La météo est dans le prompt

    def test_limite_20_plantes(self, service):
        """Maximum 20 plantes dans le prompt."""
        service.call_with_parsing_sync = Mock(
            return_value=AnomaliesJardinResponse(score_sante_jardin=70.0)
        )
        plantes = [{"nom": f"Plante{i}", "etat": "normal"} for i in range(30)]
        service.detecter_anomalies(plantes=plantes)
        prompt = service.call_with_parsing_sync.call_args.kwargs.get(
            "prompt", service.call_with_parsing_sync.call_args[1].get("prompt", "")
        )
        # Plante29 ne devrait pas y être (index 20+)
        assert "Plante20" not in prompt


# ──────────────────────────────────────────────
# GroupeurNotifications
# ──────────────────────────────────────────────

from src.services.core.notifications.groupeur import (
    GroupeurNotifications,
    NotificationPendante,
    TYPE_ICONES,
)


class TestGroupeurNotifications:
    """Tests pour le groupeur de notifications."""

    @pytest.fixture
    def groupeur(self):
        return GroupeurNotifications()

    def test_ajouter_notification(self, groupeur):
        """Ajouter une notification → compteur incrémenté."""
        groupeur.ajouter("cuisine", "Repas planifié", "Planning semaine validé")
        assert groupeur.nombre_pendantes == 1

    def test_ajouter_plusieurs(self, groupeur):
        """Ajouter plusieurs notifications de modules différents."""
        groupeur.ajouter("cuisine", "Repas planifié", "Planning validé")
        groupeur.ajouter("jardin", "Arrosage nécessaire", "Les tomates ont soif")
        groupeur.ajouter("maison", "Entretien prévu", "Vider les filtres")
        assert groupeur.nombre_pendantes == 3

    def test_digest_vide(self, groupeur):
        """Aucune notification → digest vide."""
        assert groupeur.construire_digest() == ""

    def test_digest_contient_titre(self, groupeur):
        """Le digest contient le titre custom."""
        groupeur.ajouter("cuisine", "Test", "msg")
        digest = groupeur.construire_digest(titre_digest="🌅 Bonjour !")
        assert "🌅 Bonjour !" in digest

    def test_digest_format_html(self, groupeur):
        """Le digest utilise le format HTML Telegram."""
        groupeur.ajouter("cuisine", "Repas planifié", "Planning")
        digest = groupeur.construire_digest()
        assert "<b>" in digest

    def test_notifications_critiques(self, groupeur):
        """Notifications priorité ≤ 2 → section critique."""
        groupeur.ajouter("sante", "Urgence", "Alerte santé", priorite=1)
        groupeur.ajouter("cuisine", "Info", "Recette du jour", priorite=4)
        digest = groupeur.construire_digest()
        assert "priorité" in digest.lower()
        assert groupeur.a_des_critiques is True

    def test_pas_de_critiques(self, groupeur):
        """Aucune notification critique."""
        groupeur.ajouter("cuisine", "Info", "test", priorite=3)
        assert groupeur.a_des_critiques is False

    def test_vider(self, groupeur):
        """Vider le groupeur → 0 pendantes."""
        groupeur.ajouter("cuisine", "Test", "msg")
        groupeur.ajouter("maison", "Test2", "msg2")
        groupeur.vider()
        assert groupeur.nombre_pendantes == 0

    def test_icone_module_connu(self, groupeur):
        """Module connu → icône correcte."""
        groupeur.ajouter("jardin", "Test", "msg")
        assert groupeur._pendantes[0].icone == "🌱"

    def test_icone_module_inconnu(self, groupeur):
        """Module inconnu → icône par défaut 📌."""
        groupeur.ajouter("inconnu", "Test", "msg")
        assert groupeur._pendantes[0].icone == "📌"

    def test_digest_max_5_par_module(self, groupeur):
        """Maximum 5 notifications affichées par module dans le digest."""
        for i in range(8):
            groupeur.ajouter("cuisine", f"Notif {i}", f"Message {i}", priorite=4)
        digest = groupeur.construire_digest()
        assert "et 3 autres" in digest

    def test_digest_tri_priorite(self, groupeur):
        """Les notifications sont triées par priorité."""
        groupeur.ajouter("maison", "Bas", "basse prio", priorite=5)
        groupeur.ajouter("sante", "Urgent", "critique", priorite=1)
        groupeur.ajouter("cuisine", "Normal", "normal", priorite=3)
        digest = groupeur.construire_digest()
        # La critique doit apparaître avant les normales
        idx_urgent = digest.index("Urgent")
        idx_normal = digest.index("Normal")
        assert idx_urgent < idx_normal

    def test_footer_singulier(self, groupeur):
        """1 notification → singulier dans le footer."""
        groupeur.ajouter("cuisine", "Test", "msg")
        digest = groupeur.construire_digest()
        assert "1 notification regroupée" in digest

    def test_footer_pluriel(self, groupeur):
        """Plusieurs notifications → pluriel dans le footer."""
        groupeur.ajouter("cuisine", "Test1", "msg")
        groupeur.ajouter("maison", "Test2", "msg")
        digest = groupeur.construire_digest()
        assert "2 notifications regroupées" in digest


# ──────────────────────────────────────────────
# InsightsAnalyticsService
# ──────────────────────────────────────────────

from src.services.dashboard.insights_analytics import (
    InsightsAnalyticsService,
    InsightsFamille,
    TendanceModule,
)


class TestInsightsAnalyticsService:
    """Tests pour le service Insights & Analytics."""

    @pytest.fixture
    def service(self):
        with patch("src.services.dashboard.insights_analytics.obtenir_client_ia", return_value=Mock()):
            return InsightsAnalyticsService()

    @patch("src.services.dashboard.insights_analytics.obtenir_contexte_db")
    def test_generer_insights_basique(self, mock_db, service):
        """Génération d'insights basique sans données en base."""
        from contextlib import contextmanager

        mock_session = Mock()
        mock_session.query.return_value.filter.return_value.all.return_value = []
        mock_session.query.return_value.filter.return_value.scalar.return_value = 0

        @contextmanager
        def _ctx():
            yield mock_session

        mock_db.return_value = _ctx()

        service.call_with_dict_parsing_sync = Mock(
            return_value={
                "resume": "Bonne semaine familiale !",
                "points_forts": ["Régularité des repas"],
                "axes_amelioration": ["Plus de variété"],
            }
        )

        # Contourner le cache pour le test
        result = InsightsAnalyticsService.generer_insights_famille.__wrapped__(service, periode_mois=1)
        assert isinstance(result, InsightsFamille)
        assert result.periode_jours == 30

    def test_generer_narrative_ia(self, service):
        """Génération de narrative IA à partir d'insights."""
        insights = InsightsFamille(
            repas_planifies=14,
            repas_cuisines=12,
            taux_realisation_repas=85.7,
            routines_actives=3,
            meilleur_streak=7,
        )
        service.call_with_dict_parsing_sync = Mock(
            return_value={
                "resume": "Super semaine ! 85% de réalisation.",
                "points_forts": ["Régularité"],
                "axes_amelioration": ["Varier les légumes"],
            }
        )
        result = service._generer_narrative(insights)
        assert "Super semaine" in result
        assert len(insights.points_forts) > 0

    def test_generer_narrative_ia_none(self, service):
        """IA retourne None → résumé vide."""
        insights = InsightsFamille()
        service.call_with_dict_parsing_sync = Mock(return_value=None)
        result = service._generer_narrative(insights)
        assert result == ""


# ──────────────────────────────────────────────
# ChatAIService — Contexte enrichi P6
# ──────────────────────────────────────────────

from src.services.utilitaires.chat.chat_ai import (
    ChatAIService,
    MAPPING_PAGE_CONTEXTE,
    SYSTEM_PROMPTS,
)


class TestChatAIContexteP6:
    """Tests pour l'enrichissement contextuel du ChatAIService (P6)."""

    @pytest.fixture
    def service(self):
        with patch("src.services.utilitaires.chat.chat_ai.obtenir_client_ia", return_value=Mock()):
            return ChatAIService()

    # — _resoudre_contexte —

    def test_contexte_explicite_non_general(self, service):
        """Contexte explicite != general → retourné tel quel, peu importe la page."""
        assert service._resoudre_contexte("cuisine", "/maison/projets") == "cuisine"

    def test_contexte_general_sans_page(self, service):
        """Contexte general sans page → reste general."""
        assert service._resoudre_contexte("general", None) == "general"

    def test_contexte_general_page_cuisine(self, service):
        """Contexte general + page /cuisine → résolu en cuisine."""
        assert service._resoudre_contexte("general", "/cuisine/recettes") == "cuisine"

    def test_contexte_general_page_jardin(self, service):
        """Contexte general + page /maison/jardin → résolu en jardin."""
        assert service._resoudre_contexte("general", "/maison/jardin") == "jardin"

    def test_contexte_general_page_jeux(self, service):
        """Contexte general + page /jeux/paris → résolu en jeux."""
        assert service._resoudre_contexte("general", "/jeux/paris") == "jeux"

    def test_contexte_general_page_planning(self, service):
        """Contexte general + page /planning → résolu en planning."""
        assert service._resoudre_contexte("general", "/planning") == "planning"

    def test_contexte_general_page_inventaire(self, service):
        """Contexte general + page /inventaire → résolu en inventaire."""
        assert service._resoudre_contexte("general", "/inventaire") == "inventaire"

    def test_contexte_general_page_inconnue(self, service):
        """Contexte general + page inconnue → reste general."""
        assert service._resoudre_contexte("general", "/page-inconnue") == "general"

    def test_contexte_general_page_batch_cooking(self, service):
        """Contexte general + page /batch-cooking → résolu en cuisine."""
        assert service._resoudre_contexte("general", "/batch-cooking") == "cuisine"

    # — MAPPING_PAGE_CONTEXTE —

    def test_mapping_couvre_modules_p6(self):
        """Le mapping inclut les nouveaux contextes P6."""
        assert "jardin" in MAPPING_PAGE_CONTEXTE
        assert "jeux" in MAPPING_PAGE_CONTEXTE
        assert "paris" in MAPPING_PAGE_CONTEXTE
        assert "planning" in MAPPING_PAGE_CONTEXTE
        assert "inventaire" in MAPPING_PAGE_CONTEXTE

    # — SYSTEM_PROMPTS —

    def test_prompts_nouveaux_contextes(self):
        """Des system prompts existent pour les contextes P6."""
        for ctx in ("jardin", "jeux", "planning", "inventaire"):
            assert ctx in SYSTEM_PROMPTS, f"System prompt manquant pour '{ctx}'"

    def test_prompts_contenu_pertinent(self):
        """Les prompts P6 mentionnent le bon sujet."""
        assert "jardin" in SYSTEM_PROMPTS["jardin"].lower()
        assert "paris" in SYSTEM_PROMPTS["jeux"].lower() or "jeux" in SYSTEM_PROMPTS["jeux"].lower()
        assert "repas" in SYSTEM_PROMPTS["planning"].lower() or "menu" in SYSTEM_PROMPTS["planning"].lower()
        assert "stock" in SYSTEM_PROMPTS["inventaire"].lower() or "péremption" in SYSTEM_PROMPTS["inventaire"].lower()

    # — envoyer_message avec contexte_page —

    def test_envoyer_message_avec_contexte_page(self, service):
        """envoyer_message accepte contexte_page et l'utilise."""
        service.call_with_cache_sync = Mock(return_value="Réponse test")

        result = service.envoyer_message(
            message="Bonjour",
            contexte="general",
            contexte_page="/cuisine/recettes",
        )
        assert result == "Réponse test"
        # Le system prompt utilisé doit être celui de "cuisine"
        call_args = service.call_with_cache_sync.call_args
        system_prompt = call_args.kwargs.get("system_prompt", "")
        assert "culinaire" in system_prompt or "cuisine" in system_prompt.lower()
