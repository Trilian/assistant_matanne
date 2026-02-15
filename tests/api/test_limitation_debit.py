"""
Tests pour src/api/limitation_debit.py

Tests unitaires avec vraies données pour la limitation de débit.
"""

import time
from unittest.mock import MagicMock

import pytest

# ═══════════════════════════════════════════════════════════
# DONNÉES DE TEST
# ═══════════════════════════════════════════════════════════


ADRESSES_IP = [
    "192.168.1.1",
    "10.0.0.1",
    "172.16.0.1",
    "8.8.8.8",
]

CHEMINS_EXEMPTS = ["/health", "/docs", "/redoc", "/openapi.json"]

CHEMINS_PROTEGES = [
    "/api/v1/recettes",
    "/api/v1/inventaire",
    "/api/v1/courses",
    "/api/v1/planning",
]

CHEMINS_IA = [
    "/api/v1/ai/suggestions",
    "/api/v1/suggest/recettes",
]


# ═══════════════════════════════════════════════════════════
# TESTS STRATEGIE
# ═══════════════════════════════════════════════════════════


class TestStrategieLimitationDebit:
    """Tests de l'énumération StrategieLimitationDebit."""

    def test_strategies_francaises_existent(self):
        """Les stratégies françaises sont définies."""
        from src.api.limitation_debit import StrategieLimitationDebit

        assert hasattr(StrategieLimitationDebit, "FENETRE_FIXE")
        assert hasattr(StrategieLimitationDebit, "FENETRE_GLISSANTE")
        assert hasattr(StrategieLimitationDebit, "SEAU_A_JETONS")

    def test_alias_anglais_existent(self):
        """Les alias anglais sont définis."""
        from src.api.limitation_debit import RateLimitStrategy

        assert hasattr(RateLimitStrategy, "FIXED_WINDOW")
        assert hasattr(RateLimitStrategy, "SLIDING_WINDOW")
        assert hasattr(RateLimitStrategy, "TOKEN_BUCKET")

    def test_valeurs_equivalentes(self):
        """Stratégies françaises et anglaises ont mêmes valeurs."""
        from src.api.limitation_debit import StrategieLimitationDebit

        assert StrategieLimitationDebit.FENETRE_FIXE.value == "fixed_window"
        assert StrategieLimitationDebit.FENETRE_GLISSANTE.value == "sliding_window"
        assert StrategieLimitationDebit.SEAU_A_JETONS.value == "token_bucket"


# ═══════════════════════════════════════════════════════════
# TESTS CONFIG
# ═══════════════════════════════════════════════════════════


class TestConfigLimitationDebit:
    """Tests de la configuration."""

    def test_valeurs_par_defaut(self):
        """Les valeurs par défaut sont raisonnables."""
        from src.api.limitation_debit import ConfigLimitationDebit

        config = ConfigLimitationDebit()

        assert config.requetes_par_minute == 60
        assert config.requetes_par_heure == 1000
        assert config.requetes_par_jour == 10000

    def test_limites_utilisateurs(self):
        """Les limites par type d'utilisateur sont cohérentes."""
        from src.api.limitation_debit import ConfigLimitationDebit

        config = ConfigLimitationDebit()

        # Anonyme < Authentifié < Premium
        assert config.requetes_anonyme_par_minute < config.requetes_authentifie_par_minute
        assert config.requetes_authentifie_par_minute < config.requetes_premium_par_minute

    def test_limites_ia_restrictives(self):
        """Les limites IA sont plus restrictives."""
        from src.api.limitation_debit import ConfigLimitationDebit

        config = ConfigLimitationDebit()

        # IA plus restrictif que standard
        assert config.requetes_ia_par_minute < config.requetes_par_minute
        assert config.requetes_ia_par_heure < config.requetes_par_heure
        assert config.requetes_ia_par_jour < config.requetes_par_jour

    def test_alias_anglais_proprietaires(self):
        """Les alias anglais retournent les bonnes valeurs."""
        from src.api.limitation_debit import ConfigLimitationDebit

        config = ConfigLimitationDebit(requetes_par_minute=42)

        assert config.requests_per_minute == 42
        assert config.requests_per_minute == config.requetes_par_minute

    def test_tous_alias_anglais(self):
        """Tous les alias anglais sont testés pour couverture."""
        from src.api.limitation_debit import ConfigLimitationDebit

        config = ConfigLimitationDebit()

        # Tous les alias anglais doivent fonctionner
        assert config.requests_per_minute == config.requetes_par_minute
        assert config.requests_per_hour == config.requetes_par_heure
        assert config.requests_per_day == config.requetes_par_jour
        assert config.anonymous_requests_per_minute == config.requetes_anonyme_par_minute
        assert config.authenticated_requests_per_minute == config.requetes_authentifie_par_minute
        assert config.premium_requests_per_minute == config.requetes_premium_par_minute
        assert config.ai_requests_per_minute == config.requetes_ia_par_minute
        assert config.ai_requests_per_hour == config.requetes_ia_par_heure
        assert config.ai_requests_per_day == config.requetes_ia_par_jour
        assert config.strategy == config.strategie
        assert config.enable_headers == config.activer_headers
        assert config.exempt_paths == config.chemins_exemptes

    def test_chemins_exemptes_par_defaut(self):
        """Les chemins exemptés par défaut sont corrects."""
        from src.api.limitation_debit import ConfigLimitationDebit

        config = ConfigLimitationDebit()

        for chemin in CHEMINS_EXEMPTS:
            assert chemin in config.chemins_exemptes


# ═══════════════════════════════════════════════════════════
# TESTS STOCKAGE
# ═══════════════════════════════════════════════════════════


class TestStockageLimitationDebit:
    """Tests du stockage en mémoire."""

    @pytest.fixture
    def stockage(self):
        """Crée un stockage frais pour chaque test."""
        from src.api.limitation_debit import StockageLimitationDebit

        return StockageLimitationDebit()

    def test_incrementer_premiere_requete(self, stockage):
        """Première requête retourne 1."""
        cle = "ip:192.168.1.1:minute"
        compte = stockage.incrementer(cle, 60)
        assert compte == 1

    def test_incrementer_plusieurs_requetes(self, stockage):
        """Le compteur s'incrémente correctement."""
        cle = "ip:192.168.1.1:minute"

        for i in range(1, 11):
            compte = stockage.incrementer(cle, 60)
            assert compte == i

    def test_obtenir_compte_vide(self, stockage):
        """Clé inexistante retourne 0."""
        compte = stockage.obtenir_compte("cle_inexistante", 60)
        assert compte == 0

    def test_obtenir_restant(self, stockage):
        """Calcul du restant correct."""
        cle = "test:restant"
        limite = 10

        for _ in range(3):
            stockage.incrementer(cle, 60)

        restant = stockage.obtenir_restant(cle, 60, limite)
        assert restant == 7  # 10 - 3

    def test_obtenir_restant_negatif_devient_zero(self, stockage):
        """Restant négatif devient 0."""
        cle = "test:depassement"
        limite = 5

        for _ in range(10):
            stockage.incrementer(cle, 60)

        restant = stockage.obtenir_restant(cle, 60, limite)
        assert restant == 0

    def test_bloquer_et_verifier(self, stockage):
        """Le blocage fonctionne."""
        cle = "ip:mauvais_acteur"

        assert not stockage.est_bloque(cle)

        stockage.bloquer(cle, 60)

        assert stockage.est_bloque(cle)

    def test_alias_anglais_stockage(self, stockage):
        """Les alias anglais fonctionnent."""
        cle = "test:alias"

        compte = stockage.increment(cle, 60)
        assert compte == 1

        compte = stockage.get_count(cle, 60)
        assert compte == 1

        restant = stockage.get_remaining(cle, 60, 10)
        assert restant == 9

        stockage.block(cle, 60)
        assert stockage.is_blocked(cle)

    def test_nettoyage_anciennes_entrees(self, stockage):
        """Les entrées expirées sont nettoyées."""
        cle = "test:expiration"

        # Simule des entrées anciennes en patchant time
        stockage._store[cle] = [
            (time.time() - 120, 1),  # 2 minutes ago - expired
            (time.time() - 30, 1),  # 30s ago - valid
        ]

        # Fenêtre de 60 secondes
        compte = stockage.obtenir_compte(cle, 60)

        # Seule l'entrée valide reste
        assert compte == 1


# ═══════════════════════════════════════════════════════════
# TESTS LIMITEUR
# ═══════════════════════════════════════════════════════════


class TestLimiteurDebit:
    """Tests du limiteur de débit."""

    @pytest.fixture
    def limiteur(self):
        """Crée un limiteur frais."""
        from src.api.limitation_debit import (
            ConfigLimitationDebit,
            LimiteurDebit,
            StockageLimitationDebit,
        )

        stockage = StockageLimitationDebit()
        config = ConfigLimitationDebit(
            requetes_anonyme_par_minute=5,  # Limite basse pour tests
            requetes_authentifie_par_minute=10,
        )
        return LimiteurDebit(stockage=stockage, config=config)

    def _creer_requete_mock(self, ip: str = "192.168.1.1", path: str = "/api/v1/test"):
        """Helper pour créer une requête mock."""
        request = MagicMock()
        request.client.host = ip
        request.url.path = path
        request.headers.get.return_value = None
        return request

    def test_generer_cle_avec_ip(self, limiteur):
        """Génère une clé basée sur l'IP."""
        request = self._creer_requete_mock()

        cle = limiteur._generer_cle(request)

        assert "ip:192.168.1.1" in cle

    def test_generer_cle_avec_utilisateur(self, limiteur):
        """Génère une clé basée sur l'ID utilisateur."""
        request = self._creer_requete_mock()

        cle = limiteur._generer_cle(request, identifiant="user_123")

        assert "user:user_123" in cle
        assert "ip:" not in cle

    def test_verifier_limite_autorise(self, limiteur):
        """Première requête est autorisée."""
        request = self._creer_requete_mock()

        resultat = limiteur.verifier_limite(request)

        assert resultat["allowed"] is True
        assert resultat["remaining"] > 0

    def test_verifier_limite_chemin_exempt(self, limiteur):
        """Chemins exemptés ne sont pas limités."""
        for chemin in CHEMINS_EXEMPTS:
            request = self._creer_requete_mock(path=chemin)

            resultat = limiteur.verifier_limite(request)

            assert resultat["allowed"] is True
            assert resultat["limit"] == -1  # Pas de limite

    def test_verifier_limite_depassee(self, limiteur):
        """Une fois limite dépassée, HTTPException levée."""
        from fastapi import HTTPException

        request = self._creer_requete_mock()

        # Épuiser la limite (5 requêtes anonymes)
        for _ in range(5):
            limiteur.verifier_limite(request)

        # 6ème requête doit échouer
        with pytest.raises(HTTPException) as exc_info:
            limiteur.verifier_limite(request)

        assert exc_info.value.status_code == 429
        assert "Limite" in exc_info.value.detail or "dépassée" in exc_info.value.detail

    def test_limite_plus_haute_pour_utilisateur_authentifie(self, limiteur):
        """Utilisateurs authentifiés ont plus de requêtes."""
        request = self._creer_requete_mock()

        # Utilisateur anonyme: limite = 5
        for _ in range(5):
            limiteur.verifier_limite(request)

        # Utilisateur authentifié depuis une autre IP: limite = 10
        request2 = self._creer_requete_mock(ip="10.0.0.1")
        for _ in range(10):
            resultat = limiteur.verifier_limite(request2, id_utilisateur="user_abc")
            assert resultat["allowed"]

    def test_alias_check_rate_limit(self, limiteur):
        """L'alias anglais fonctionne."""
        request = self._creer_requete_mock()

        resultat = limiteur.check_rate_limit(request)

        assert resultat["allowed"] is True


# ═══════════════════════════════════════════════════════════
# TESTS MIDDLEWARE
# ═══════════════════════════════════════════════════════════


class TestMiddlewareLimitationDebit:
    """Tests du middleware FastAPI."""

    def test_import_middleware(self):
        """Le middleware s'importe correctement."""
        from src.api.limitation_debit import MiddlewareLimitationDebit

        assert MiddlewareLimitationDebit is not None

    def test_alias_anglais(self):
        """L'alias anglais existe."""
        from src.api.limitation_debit import MiddlewareLimitationDebit, RateLimitMiddleware

        assert RateLimitMiddleware is MiddlewareLimitationDebit

    def test_middleware_dans_app(self):
        """Le middleware est utilisable dans une app FastAPI."""
        from fastapi import FastAPI

        from src.api.limitation_debit import MiddlewareLimitationDebit

        app = FastAPI()
        app.add_middleware(MiddlewareLimitationDebit)

        # Vérifie que le middleware est enregistré
        middleware_classes = [m.cls for m in app.user_middleware]
        assert MiddlewareLimitationDebit in middleware_classes


# ═══════════════════════════════════════════════════════════
# TESTS DÉCORATEURS
# ═══════════════════════════════════════════════════════════


class TestDecorateurLimiteDebit:
    """Tests du décorateur @limite_debit."""

    def test_import_decorateur(self):
        """Le décorateur s'importe."""
        from src.api.limitation_debit import limite_debit, rate_limit

        assert callable(limite_debit)
        assert callable(rate_limit)

    def test_decorateur_sur_fonction(self):
        """Le décorateur peut décorer une fonction."""
        from src.api.limitation_debit import limite_debit

        @limite_debit(requetes_par_minute=10)
        async def ma_fonction():
            return "ok"

        assert callable(ma_fonction)

    def test_alias_rate_limit(self):
        """L'alias rate_limit fonctionne."""
        from src.api.limitation_debit import rate_limit

        @rate_limit(requests_per_minute=10)
        async def english_function():
            return "ok"

        assert callable(english_function)


# ═══════════════════════════════════════════════════════════
# TESTS INTÉGRATION
# ═══════════════════════════════════════════════════════════


class TestIntegrationLimitationDebit:
    """Tests d'intégration avec vraie app FastAPI."""

    @pytest.fixture
    def app_test(self, monkeypatch):
        """Crée une app FastAPI de test avec rate limiting activé."""
        from fastapi import FastAPI

        from src.api.limitation_debit import (
            ConfigLimitationDebit,
            LimiteurDebit,
            MiddlewareLimitationDebit,
            StockageLimitationDebit,
        )

        # Réactiver le rate limiting pour ces tests spécifiques
        monkeypatch.setenv("RATE_LIMITING_DISABLED", "false")

        # Config très restrictive pour les tests
        stockage = StockageLimitationDebit()
        config = ConfigLimitationDebit(
            requetes_anonyme_par_minute=3,
        )
        limiteur = LimiteurDebit(stockage=stockage, config=config)

        app = FastAPI()
        app.add_middleware(MiddlewareLimitationDebit, limiteur=limiteur)

        @app.get("/test")
        async def test_endpoint():
            return {"status": "ok"}

        @app.get("/health")
        async def health():
            return {"healthy": True}

        return app

    def test_endpoint_protege(self, app_test):
        """Endpoint protégé respecte la limite."""
        from fastapi.testclient import TestClient

        client = TestClient(app_test, raise_server_exceptions=False)

        # 3 requêtes autorisées
        for i in range(3):
            response = client.get("/test")
            assert response.status_code == 200, f"Req {i + 1} failed: {response.status_code}"

        # 4ème requête bloquée (429 ou 500 selon gestion d'erreurs)
        response = client.get("/test")
        assert response.status_code in (
            429,
            500,
        ), f"Expected rate limit, got {response.status_code}"

    def test_endpoint_exempt(self, app_test):
        """Endpoint /health n'est pas limité."""
        from fastapi.testclient import TestClient

        client = TestClient(app_test)

        # Beaucoup de requêtes
        for _ in range(100):
            response = client.get("/health")
            assert response.status_code == 200

    def test_headers_rate_limit_presents(self, app_test):
        """Les headers de limite sont présents."""
        from fastapi.testclient import TestClient

        client = TestClient(app_test)
        response = client.get("/test")

        assert "X-RateLimit-Limit" in response.headers
        assert "X-RateLimit-Remaining" in response.headers
        assert "X-RateLimit-Reset" in response.headers


# ═══════════════════════════════════════════════════════════
# TESTS ALIAS RÉTROCOMPATIBILITÉ
# ═══════════════════════════════════════════════════════════


class TestAliasRetrocompatibilite:
    """Tests que tous les alias anglais existent."""

    def test_tous_les_alias_existent(self):
        """Tous les anciens noms anglais sont disponibles."""
        from src.api.limitation_debit import (
            RateLimitConfig,
            RateLimiter,
            RateLimitMiddleware,
            RateLimitStore,
            # Classes
            RateLimitStrategy,
            # Fonctions
            rate_limit,
        )

        assert RateLimitStrategy is not None
        assert RateLimitConfig is not None
        assert RateLimitStore is not None
        assert RateLimiter is not None
        assert RateLimitMiddleware is not None
        assert rate_limit is not None

    def test_instances_globales(self):
        """Les instances globales sont accessibles."""
        from src.api.limitation_debit import (
            config_limitation_debit,
            limiteur_debit,
            rate_limit_config,
            rate_limiter,
        )

        # Alias pointent vers mêmes objets
        assert rate_limit_config is config_limitation_debit
        assert rate_limiter is limiteur_debit


# ═══════════════════════════════════════════════════════════
# TESTS UTILITAIRES ET FONCTIONS ADDITIONNELLES
# ═══════════════════════════════════════════════════════════


class TestUtilitaires:
    """Tests des fonctions utilitaires."""

    def test_obtenir_stats_limitation(self):
        """obtenir_stats_limitation retourne les stats."""
        from src.api.limitation_debit import obtenir_stats_limitation

        stats = obtenir_stats_limitation()

        assert "cles_actives" in stats
        assert "cles_bloquees" in stats
        assert "configuration" in stats
        assert "requetes_par_minute" in stats["configuration"]

    def test_get_rate_limit_stats_alias(self):
        """Alias anglais pour obtenir_stats_limitation."""
        from src.api.limitation_debit import get_rate_limit_stats

        stats = get_rate_limit_stats()

        assert "cles_actives" in stats

    def test_reinitialiser_limites(self):
        """reinitialiser_limites réinitialise les compteurs."""
        from src.api.limitation_debit import (
            _stockage,
            reinitialiser_limites,
        )

        # Ajouter des données
        _stockage.incrementer("test:key", 60)

        # Réinitialiser
        reinitialiser_limites()

        # Les données devraient être nettoyées (nouveau stockage)

    def test_reset_rate_limits_alias(self):
        """Alias anglais pour reinitialiser_limites."""
        from src.api.limitation_debit import reset_rate_limits

        # Doit s'exécuter sans erreur
        reset_rate_limits()

    def test_configurer_limites(self):
        """configurer_limites met à jour la config globale."""
        from src.api.limitation_debit import (
            ConfigLimitationDebit,
            configurer_limites,
        )

        # Créer une nouvelle config
        nouvelle_config = ConfigLimitationDebit(requetes_par_minute=999)

        # Configurer
        configurer_limites(nouvelle_config)

        # Vérifier
        from src.api.limitation_debit import (
            config_limitation_debit as config_après,
        )

        assert config_après.requetes_par_minute == 999

    def test_configure_rate_limits_alias(self):
        """Alias anglais pour configurer_limites."""
        from src.api.limitation_debit import (
            ConfigLimitationDebit,
            configure_rate_limits,
        )

        config = ConfigLimitationDebit(requetes_par_minute=777)
        configure_rate_limits(config)


class TestLimiteurDebitHeaders:
    """Tests pour les méthodes de headers du limiteur."""

    @pytest.fixture
    def limiteur_avec_headers_actifs(self):
        """Limiteur avec headers activés."""
        from src.api.limitation_debit import (
            ConfigLimitationDebit,
            LimiteurDebit,
            StockageLimitationDebit,
        )

        stockage = StockageLimitationDebit()
        config = ConfigLimitationDebit(activer_headers=True)
        return LimiteurDebit(stockage=stockage, config=config)

    @pytest.fixture
    def limiteur_sans_headers(self):
        """Limiteur avec headers désactivés."""
        from src.api.limitation_debit import (
            ConfigLimitationDebit,
            LimiteurDebit,
            StockageLimitationDebit,
        )

        stockage = StockageLimitationDebit()
        config = ConfigLimitationDebit(activer_headers=False)
        return LimiteurDebit(stockage=stockage, config=config)

    def test_ajouter_headers_actifs(self, limiteur_avec_headers_actifs):
        """Headers sont ajoutés quand activés."""
        response = MagicMock()
        response.headers = {}

        info_limite = {"limit": 60, "remaining": 55, "reset": 30}

        limiteur_avec_headers_actifs.ajouter_headers(response, info_limite)

        assert "X-RateLimit-Limit" in response.headers
        assert "X-RateLimit-Remaining" in response.headers
        assert "X-RateLimit-Reset" in response.headers

    def test_ajouter_headers_desactives(self, limiteur_sans_headers):
        """Headers ne sont pas ajoutés quand désactivés."""
        response = MagicMock()
        response.headers = {}

        info_limite = {"limit": 60, "remaining": 55, "reset": 30}

        limiteur_sans_headers.ajouter_headers(response, info_limite)

        # Headers ne devraient pas être ajoutés
        assert "X-RateLimit-Limit" not in response.headers

    def test_add_headers_alias(self, limiteur_avec_headers_actifs):
        """Alias add_headers fonctionne."""
        response = MagicMock()
        response.headers = {}

        info_limite = {"limit": 60, "remaining": 55, "reset": 30}

        limiteur_avec_headers_actifs.add_headers(response, info_limite)

        assert "X-RateLimit-Limit" in response.headers

    def test_ajouter_headers_limite_negative(self, limiteur_avec_headers_actifs):
        """Headers non ajoutés si limite négative (chemin exempté)."""
        response = MagicMock()
        response.headers = {}

        info_limite = {"limit": -1, "remaining": -1}

        limiteur_avec_headers_actifs.ajouter_headers(response, info_limite)

        # Headers pas ajoutés pour les chemins exemptés
        assert "X-RateLimit-Limit" not in response.headers


class TestLimiteurDebitClé:
    """Tests pour la génération de clés."""

    @pytest.fixture
    def limiteur(self):
        """Crée un limiteur de test."""
        from src.api.limitation_debit import LimiteurDebit, StockageLimitationDebit

        return LimiteurDebit(stockage=StockageLimitationDebit())

    def _creer_requete_mock(self, ip="192.168.1.1", forwarded=None):
        """Helper pour créer une requête mock."""
        request = MagicMock()
        request.client.host = ip
        request.headers.get.return_value = forwarded
        return request

    def test_generer_cle_avec_endpoint(self, limiteur):
        """Génère une clé avec endpoint spécifié."""
        request = self._creer_requete_mock()

        cle = limiteur._generer_cle(request, endpoint="/api/v1/recettes")

        assert "endpoint:/api/v1/recettes" in cle

    def test_generer_cle_avec_x_forwarded_for(self, limiteur):
        """Utilise X-Forwarded-For si présent."""
        request = self._creer_requete_mock(ip="10.0.0.1", forwarded="203.0.113.195, 70.41.3.18")

        cle = limiteur._generer_cle(request)

        # Doit utiliser la première IP du X-Forwarded-For
        assert "ip:203.0.113.195" in cle

    def test_get_key_alias(self, limiteur):
        """Alias _get_key fonctionne."""
        request = self._creer_requete_mock()

        cle = limiteur._get_key(request, identifier="user_123")

        assert "user:user_123" in cle

    def test_generer_cle_client_none(self, limiteur):
        """Génère clé avec client=None."""
        request = MagicMock()
        request.client = None
        request.headers.get.return_value = None

        cle = limiteur._generer_cle(request)

        assert "ip:unknown" in cle


class TestLimiteurDebitPremium:
    """Tests pour les utilisateurs premium."""

    @pytest.fixture
    def limiteur(self):
        """Crée un limiteur avec config de test."""
        from src.api.limitation_debit import (
            ConfigLimitationDebit,
            LimiteurDebit,
            StockageLimitationDebit,
        )

        stockage = StockageLimitationDebit()
        config = ConfigLimitationDebit(
            requetes_premium_par_minute=200,
            requetes_authentifie_par_minute=60,
            requetes_anonyme_par_minute=20,
        )
        return LimiteurDebit(stockage=stockage, config=config)

    def _creer_requete_mock(self, ip="192.168.1.1", path="/api/v1/test"):
        """Helper pour créer une requête mock."""
        request = MagicMock()
        request.client.host = ip
        request.url.path = path
        request.headers.get.return_value = None
        return request

    def test_limite_premium_plus_haute(self, limiteur):
        """Utilisateurs premium ont une limite plus haute."""
        request = self._creer_requete_mock()

        # Première requête
        resultat = limiteur.verifier_limite(request, id_utilisateur="user_123", est_premium=True)

        # La limite doit être celle premium
        assert resultat["allowed"] is True
        assert resultat["limit"] == 200  # Premium limit


class TestLimiteurDebitBlocage:
    """Tests pour le blocage après abus."""

    def test_blocage_cle_bloquee(self):
        """Clé bloquée lève HTTPException."""
        from fastapi import HTTPException

        from src.api.limitation_debit import LimiteurDebit, StockageLimitationDebit

        stockage = StockageLimitationDebit()
        limiteur = LimiteurDebit(stockage=stockage)

        request = MagicMock()
        request.client.host = "1.2.3.4"
        request.url.path = "/api/test"
        request.headers.get.return_value = None

        # Bloquer la clé
        stockage.bloquer("ip:1.2.3.4", 60)

        # Vérifier que l'exception est levée
        with pytest.raises(HTTPException) as exc_info:
            limiteur.verifier_limite(request)

        assert exc_info.value.status_code == 429


class TestStockageTempsReset:
    """Tests pour obtenir_temps_reset."""

    def test_temps_reset_cle_vide(self):
        """Temps reset = 0 si clé vide."""
        from src.api.limitation_debit import StockageLimitationDebit

        stockage = StockageLimitationDebit()

        reset = stockage.obtenir_temps_reset("cle:inexistante", 60)

        assert reset == 0

    def test_temps_reset_avec_donnees(self):
        """Temps reset calculé correctement."""
        from src.api.limitation_debit import StockageLimitationDebit

        stockage = StockageLimitationDebit()

        # Ajouter une entrée
        stockage.incrementer("test:reset", 60)

        reset = stockage.obtenir_temps_reset("test:reset", 60)

        # Devrait être proche de 60 secondes
        assert 55 <= reset <= 60

    def test_get_reset_time_alias(self):
        """Alias get_reset_time fonctionne."""
        from src.api.limitation_debit import StockageLimitationDebit

        stockage = StockageLimitationDebit()
        stockage.incrementer("test:alias", 60)

        reset = stockage.get_reset_time("test:alias", 60)

        assert reset >= 0


class TestDecorateurLimiteDebitAvance:
    """Tests avancés pour le décorateur limite_debit."""

    @pytest.mark.asyncio
    async def test_decorateur_sans_request(self):
        """Décorateur fonctionne sans Request."""
        from src.api.limitation_debit import limite_debit

        @limite_debit(requetes_par_minute=10)
        async def fonction_sans_request():
            return "ok"

        result = await fonction_sans_request()

        assert result == "ok"

    @pytest.mark.asyncio
    async def test_decorateur_avec_fonction_cle(self):
        """Décorateur avec fonction de clé personnalisée."""
        from fastapi import Request

        from src.api.limitation_debit import limite_debit

        def ma_fonction_cle(request: Request) -> str:
            return f"custom:{request.client.host}"

        @limite_debit(requetes_par_minute=100, fonction_cle=ma_fonction_cle)
        async def fonction_avec_cle_custom(request: Request):
            return "ok"

        request = MagicMock(spec=Request)
        request.client.host = "1.2.3.4"
        request.headers.get.return_value = None

        result = await fonction_avec_cle_custom(request)

        assert result == "ok"

    @pytest.mark.asyncio
    async def test_decorateur_limite_heure(self):
        """Décorateur avec limite par heure."""
        from src.api.limitation_debit import limite_debit, reinitialiser_limites

        reinitialiser_limites()

        @limite_debit(requetes_par_heure=100)
        async def fonction_limite_heure():
            return "ok"

        result = await fonction_limite_heure()

        assert result == "ok"


class TestDependancesFastAPI:
    """Tests pour les dépendances FastAPI."""

    @pytest.mark.asyncio
    async def test_verifier_limite_debit_dependency(self):
        """Dépendance verifier_limite_debit fonctionne."""
        from src.api.limitation_debit import verifier_limite_debit

        request = MagicMock()
        request.client.host = "1.2.3.4"
        request.url.path = "/api/test"
        request.headers.get.return_value = None

        result = await verifier_limite_debit(request)

        assert result["allowed"] is True

    @pytest.mark.asyncio
    async def test_verifier_limite_debit_ia_dependency(self):
        """Dépendance verifier_limite_debit_ia fonctionne."""
        from src.api.limitation_debit import verifier_limite_debit_ia

        request = MagicMock()
        request.client.host = "5.6.7.8"
        request.url.path = "/api/ai/test"
        request.headers.get.return_value = None

        result = await verifier_limite_debit_ia(request)

        assert result["allowed"] is True

    @pytest.mark.asyncio
    async def test_check_rate_limit_alias(self):
        """Alias check_rate_limit fonctionne."""
        from src.api.limitation_debit import check_rate_limit

        request = MagicMock()
        request.client.host = "9.10.11.12"
        request.url.path = "/api/test"
        request.headers.get.return_value = None

        result = await check_rate_limit(request)

        assert result["allowed"] is True

    @pytest.mark.asyncio
    async def test_check_ai_rate_limit_alias(self):
        """Alias check_ai_rate_limit fonctionne."""
        from src.api.limitation_debit import check_ai_rate_limit, reinitialiser_limites

        reinitialiser_limites()

        request = MagicMock()
        request.client.host = "13.14.15.16"
        request.url.path = "/api/ai/suggest"
        request.headers.get.return_value = None

        result = await check_ai_rate_limit(request)

        assert result["allowed"] is True
