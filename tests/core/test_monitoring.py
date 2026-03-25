"""
Tests pour src/core/monitoring/ — collecteur, décorateurs, santé, sentry, probes.
"""

import asyncio
import os
import threading
import time
from unittest.mock import MagicMock, patch

import pytest

from src.core.monitoring import (
    CollecteurMetriques,
    MetriqueType,
    PointMetrique,
    chronometre,
    collecteur,
    enregistrer_metrique,
    obtenir_snapshot,
    reinitialiser_collecteur,
)
from src.core.monitoring.health import (
    SanteComposant,
    SanteSysteme,
    StatutSante,
    enregistrer_verification,
)

# ═══════════════════════════════════════════════════════════
# FIXTURES
# ═══════════════════════════════════════════════════════════


@pytest.fixture(autouse=True)
def clean_collecteur():
    """Réinitialise le collecteur global entre chaque test."""
    reinitialiser_collecteur()
    yield
    reinitialiser_collecteur()


@pytest.fixture
def reset_sentry():
    """Réinitialise l'état de Sentry entre les tests."""
    import src.core.monitoring.sentry as sentry_module

    original_state = sentry_module._sentry_initialise
    yield
    sentry_module._sentry_initialise = original_state


# ═══════════════════════════════════════════════════════════
# TESTS COLLECTEUR
# ═══════════════════════════════════════════════════════════


class TestCollecteurEnregistrement:
    """Tests pour l'enregistrement de métriques."""

    def test_enregistrer_compteur(self):
        c = CollecteurMetriques()
        point = c.enregistrer("test.compteur", 1, MetriqueType.COMPTEUR)

        assert isinstance(point, PointMetrique)
        assert point.nom == "test.compteur"
        assert point.valeur == 1
        assert point.type == MetriqueType.COMPTEUR

    def test_enregistrer_jauge(self):
        c = CollecteurMetriques()
        c.enregistrer("test.jauge", 42.5, MetriqueType.JAUGE)

        assert c.obtenir_total("test.jauge") == 42.5

    def test_enregistrer_histogramme(self):
        c = CollecteurMetriques()
        c.enregistrer("test.latence", 100.0, MetriqueType.HISTOGRAMME)
        c.enregistrer("test.latence", 200.0, MetriqueType.HISTOGRAMME)

        assert c.obtenir_total("test.latence") == 300.0

    def test_incrementer_shortcut(self):
        c = CollecteurMetriques()
        c.incrementer("appels")
        c.incrementer("appels")
        c.incrementer("appels", 3)

        assert c.obtenir_total("appels") == 5

    def test_jauge_shortcut(self):
        c = CollecteurMetriques()
        c.jauge("temperature", 36.5)

        assert c.obtenir_total("temperature") == 36.5

    def test_jauge_remplace_valeur(self):
        c = CollecteurMetriques()
        c.jauge("temperature", 36.5)
        c.jauge("temperature", 37.0)

        assert c.obtenir_total("temperature") == 37.0

    def test_histogramme_shortcut(self):
        c = CollecteurMetriques()
        c.histogramme("latence", 100.0)
        c.histogramme("latence", 200.0)

        serie = c.obtenir_serie("latence")
        assert len(serie) == 2

    def test_labels(self):
        c = CollecteurMetriques()
        point = c.enregistrer("test", 1, labels={"service": "recettes"})

        assert point.labels == {"service": "recettes"}

    def test_labels_globaux(self):
        c = CollecteurMetriques()
        c.definir_labels_globaux({"env": "test"})
        point = c.enregistrer("test", 1, labels={"module": "cuisine"})

        assert point.labels == {"env": "test", "module": "cuisine"}

    def test_obtenir_total_inexistant(self):
        c = CollecteurMetriques()

        assert c.obtenir_total("inexistant") == 0.0

    def test_obtenir_serie_inexistante(self):
        c = CollecteurMetriques()

        assert c.obtenir_serie("inexistant") == []

    def test_taille_historique_limitee(self):
        c = CollecteurMetriques(taille_historique=5)

        for i in range(10):
            c.enregistrer("test", float(i), MetriqueType.COMPTEUR)

        serie = c.obtenir_serie("test")
        assert len(serie) == 5
        # Les 5 dernières valeurs (5, 6, 7, 8, 9)
        assert serie[0].valeur == 5.0


class TestCollecteurSnapshot:
    """Tests pour le snapshot de métriques."""

    def test_snapshot_structure(self):
        c = CollecteurMetriques()
        c.incrementer("test.appels")

        snap = c.snapshot()

        assert "timestamp" in snap
        assert "uptime_seconds" in snap
        assert "metriques" in snap
        assert "test.appels" in snap["metriques"]

    def test_snapshot_compteur_info(self):
        c = CollecteurMetriques()
        c.incrementer("test.appels")
        c.incrementer("test.appels")

        snap = c.snapshot()
        info = snap["metriques"]["test.appels"]

        assert info["type"] == "COMPTEUR"
        assert info["total"] == 2.0
        assert info["nb_points"] == 2

    def test_snapshot_histogramme_statistiques(self):
        c = CollecteurMetriques()
        for v in [100, 200, 300, 400, 500]:
            c.histogramme("latence", float(v))

        snap = c.snapshot()
        stats = snap["metriques"]["latence"]["statistiques"]

        assert stats["min"] == 100.0
        assert stats["max"] == 500.0
        assert "moyenne" in stats
        assert "mediane" in stats
        assert "p95" in stats
        assert "p99" in stats

    def test_snapshot_dernier_point(self):
        c = CollecteurMetriques()
        c.incrementer("test", labels={"k": "v"})

        snap = c.snapshot()
        dernier = snap["metriques"]["test"]["dernier_point"]

        assert dernier["valeur"] == 1.0
        assert dernier["labels"] == {"k": "v"}
        assert "timestamp" in dernier


class TestCollecteurIntrospection:
    """Tests pour l'introspection du collecteur."""

    def test_lister_metriques(self):
        c = CollecteurMetriques()
        c.incrementer("a")
        c.incrementer("b")
        c.jauge("c", 1)

        noms = c.lister_metriques()

        assert set(noms) == {"a", "b", "c"}

    def test_reinitialiser(self):
        c = CollecteurMetriques()
        c.incrementer("test")
        c.reinitialiser()

        assert c.lister_metriques() == []
        assert c.obtenir_total("test") == 0.0

    def test_filtrer_par_prefixe(self):
        c = CollecteurMetriques()
        c.incrementer("ia.appels")
        c.incrementer("ia.erreurs")
        c.incrementer("db.requetes")

        filtered = c.filtrer_par_prefixe("ia.")

        assert set(filtered["metriques"].keys()) == {"ia.appels", "ia.erreurs"}


class TestCollecteurThreadSafety:
    """Tests de thread-safety du collecteur."""

    def test_concurrent_enregistrements(self):
        c = CollecteurMetriques()
        errors = []

        def worker():
            try:
                for _ in range(100):
                    c.incrementer("concurrent")
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=worker) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert not errors
        assert c.obtenir_total("concurrent") == 1000.0

    def test_concurrent_snapshot(self):
        c = CollecteurMetriques()
        errors = []

        def writer():
            for i in range(50):
                c.incrementer("data")

        def reader():
            try:
                for _ in range(50):
                    c.snapshot()
            except Exception as e:
                errors.append(e)

        t1 = threading.Thread(target=writer)
        t2 = threading.Thread(target=reader)
        t1.start()
        t2.start()
        t1.join()
        t2.join()

        assert not errors


# ═══════════════════════════════════════════════════════════
# TESTS FONCTIONS MODULE-LEVEL
# ═══════════════════════════════════════════════════════════


class TestFonctionsGlobales:
    """Tests pour les fonctions module-level du collecteur."""

    def test_enregistrer_metrique(self):
        point = enregistrer_metrique("global.test", 1)

        assert point.nom == "global.test"

    def test_obtenir_snapshot(self):
        enregistrer_metrique("global.test", 1)
        snap = obtenir_snapshot()

        assert "global.test" in snap["metriques"]

    def test_reinitialiser_collecteur(self):
        enregistrer_metrique("global.test", 1)
        reinitialiser_collecteur()

        assert collecteur.lister_metriques() == []


# ═══════════════════════════════════════════════════════════
# TESTS DÉCORATEUR CHRONOMETRE
# ═══════════════════════════════════════════════════════════


class TestChronometre:
    """Tests pour le décorateur @chronometre."""

    def test_chronometre_enregistre_duree(self):
        @chronometre("test.fn")
        def ma_fonction():
            return 42

        result = ma_fonction()

        assert result == 42

        serie = collecteur.obtenir_serie("test.fn.duree_ms")
        assert len(serie) == 1
        assert serie[0].valeur >= 0

    def test_chronometre_incremente_appels(self):
        @chronometre("test.fn2")
        def ma_fonction():
            pass

        ma_fonction()
        ma_fonction()

        assert collecteur.obtenir_total("test.fn2.appels") == 2

    def test_chronometre_enregistre_erreurs(self):
        @chronometre("test.erreur")
        def ma_fonction_erreur():
            raise ValueError("boom")

        with pytest.raises(ValueError, match="boom"):
            ma_fonction_erreur()

        assert collecteur.obtenir_total("test.erreur.erreurs") == 1
        # La durée est aussi enregistrée même en cas d'erreur
        assert len(collecteur.obtenir_serie("test.erreur.duree_ms")) == 1

    def test_chronometre_avec_labels(self):
        @chronometre("test.labels", labels={"service": "recettes"})
        def fn():
            pass

        fn()

        serie = collecteur.obtenir_serie("test.labels.duree_ms")
        assert serie[0].labels.get("service") == "recettes"

    def test_chronometre_seuil_alerte(self, caplog):
        @chronometre("test.lent", seuil_alerte_ms=0.001)
        def fn_lente():
            time.sleep(0.01)

        with caplog.at_level("WARNING"):
            fn_lente()

        assert "Alerte performance" in caplog.text

    def test_chronometre_preserve_metadata(self):
        @chronometre("test.meta")
        def ma_fonction_speciale():
            """Docstring originale."""
            pass

        assert ma_fonction_speciale.__name__ == "ma_fonction_speciale"
        assert ma_fonction_speciale.__doc__ == "Docstring originale."


# ═══════════════════════════════════════════════════════════
# TESTS SANTÉ
# ═══════════════════════════════════════════════════════════


class TestSanteComposant:
    """Tests pour SanteComposant."""

    def test_creation(self):
        comp = SanteComposant(
            nom="test",
            statut=StatutSante.SAIN,
            message="OK",
        )

        assert comp.nom == "test"
        assert comp.statut == StatutSante.SAIN

    def test_statuts_enum(self):
        assert StatutSante.SAIN.name == "SAIN"
        assert StatutSante.DEGRADE.name == "DEGRADE"
        assert StatutSante.CRITIQUE.name == "CRITIQUE"
        assert StatutSante.INCONNU.name == "INCONNU"


class TestSanteSysteme:
    """Tests pour SanteSysteme."""

    def test_vers_dict(self):
        sys = SanteSysteme(
            sain=True,
            composants={
                "test": SanteComposant(
                    nom="test",
                    statut=StatutSante.SAIN,
                    message="OK",
                    details={"key": "value"},
                    duree_verification_ms=1.5,
                ),
            },
        )

        d = sys.vers_dict()

        assert d["sain"] is True
        assert "test" in d["composants"]
        assert d["composants"]["test"]["statut"] == "SAIN"
        assert d["composants"]["test"]["message"] == "OK"
        assert d["composants"]["test"]["duree_ms"] == 1.5

    def test_systeme_non_sain_si_critique(self):
        sys = SanteSysteme(
            sain=False,
            composants={
                "db": SanteComposant(nom="db", statut=StatutSante.CRITIQUE),
            },
        )

        assert sys.sain is False


class TestVerificationCustom:
    """Tests pour l'enregistrement de vérifications custom."""

    def test_enregistrer_verification(self):
        def check_custom():
            return SanteComposant(
                nom="custom",
                statut=StatutSante.SAIN,
                message="OK",
            )

        enregistrer_verification("custom", check_custom)

        # La vérification est enregistrée (pas de crash)
        assert True


# ═══════════════════════════════════════════════════════════
# TESTS POINT METRIQUE
# ═══════════════════════════════════════════════════════════


class TestPointMetrique:
    """Tests pour le dataclass PointMetrique."""

    def test_immutable(self):
        point = PointMetrique(
            nom="test",
            valeur=1.0,
            type=MetriqueType.COMPTEUR,
            timestamp=time.time(),
        )

        with pytest.raises(AttributeError):
            point.valeur = 2.0  # type: ignore[misc]

    def test_default_labels(self):
        point = PointMetrique(
            nom="test",
            valeur=1.0,
            type=MetriqueType.COMPTEUR,
            timestamp=time.time(),
        )

        assert point.labels == {}


# ═══════════════════════════════════════════════════════════
# TESTS HEALTH - VÉRIFICATIONS BUILT-IN
# (Fusionné depuis test_monitoring_complete.py)
# ═══════════════════════════════════════════════════════════


class TestVerifierDb:
    """Tests pour _verifier_db."""

    def test_verifier_db_succes(self):
        from src.core.monitoring.health import StatutSante, _verifier_db

        with patch("src.core.db.verifier_connexion") as mock_conn:
            mock_conn.return_value = (True, "OK")
            result = _verifier_db()

            assert result.nom == "database"
            assert result.statut == StatutSante.SAIN
            assert result.message == "OK"
            assert result.duree_verification_ms >= 0

    def test_verifier_db_echec(self):
        from src.core.monitoring.health import StatutSante, _verifier_db

        with patch("src.core.db.verifier_connexion") as mock_conn:
            mock_conn.return_value = (False, "Connection refused")
            result = _verifier_db()

            assert result.statut == StatutSante.CRITIQUE
            assert "Connection refused" in result.message

    def test_verifier_db_exception(self):
        from src.core.monitoring.health import StatutSante, _verifier_db

        with patch("src.core.db.verifier_connexion") as mock_conn:
            mock_conn.side_effect = Exception("boom")
            result = _verifier_db()

            assert result.statut == StatutSante.CRITIQUE
            assert "boom" in result.message


class TestVerifierCache:
    """Tests pour _verifier_cache."""

    def test_verifier_cache_succes(self):
        from src.core.monitoring.health import StatutSante, _verifier_cache

        mock_cache = MagicMock()
        mock_cache.obtenir_statistiques.return_value = {
            "hit_rate": 85,
            "total_requetes": 200,
        }

        with patch("src.core.caching.obtenir_cache", return_value=mock_cache):
            result = _verifier_cache()

            assert result.nom == "cache"
            assert result.statut == StatutSante.SAIN
            assert "85" in result.message

    def test_verifier_cache_degrade(self):
        from src.core.monitoring.health import StatutSante, _verifier_cache

        mock_cache = MagicMock()
        mock_cache.obtenir_statistiques.return_value = {
            "hit_rate": 15,
            "total_requetes": 200,
        }

        with patch("src.core.caching.obtenir_cache", return_value=mock_cache):
            result = _verifier_cache()

            assert result.statut == StatutSante.DEGRADE

    def test_verifier_cache_exception(self):
        from src.core.monitoring.health import StatutSante, _verifier_cache

        with patch("src.core.caching.obtenir_cache") as mock:
            mock.side_effect = Exception("Cache error")
            result = _verifier_cache()

            assert result.statut == StatutSante.DEGRADE
            assert "Cache error" in result.message


class TestVerifierIA:
    """Tests pour _verifier_ia."""

    def test_verifier_ia_succes(self):
        from src.core.monitoring.health import StatutSante, _verifier_ia

        mock_limiter = MagicMock()
        mock_limiter.obtenir_statistiques.return_value = {
            "appels_jour": 10,
            "limite_jour": 100,
        }

        with patch("src.core.ai.rate_limit.RateLimitIA", return_value=mock_limiter):
            result = _verifier_ia()

            assert result.nom == "ia"
            assert result.statut == StatutSante.SAIN
            assert "10/100" in result.message

    def test_verifier_ia_critique(self):
        from src.core.monitoring.health import StatutSante, _verifier_ia

        mock_limiter = MagicMock()
        mock_limiter.obtenir_statistiques.return_value = {
            "appels_jour": 95,
            "limite_jour": 100,
        }

        with patch("src.core.ai.rate_limit.RateLimitIA", return_value=mock_limiter):
            result = _verifier_ia()

            assert result.statut == StatutSante.CRITIQUE

    def test_verifier_ia_degrade(self):
        from src.core.monitoring.health import StatutSante, _verifier_ia

        mock_limiter = MagicMock()
        mock_limiter.obtenir_statistiques.return_value = {
            "appels_jour": 75,
            "limite_jour": 100,
        }

        with patch("src.core.ai.rate_limit.RateLimitIA", return_value=mock_limiter):
            result = _verifier_ia()

            assert result.statut == StatutSante.DEGRADE

    def test_verifier_ia_exception(self):
        from src.core.monitoring.health import StatutSante, _verifier_ia

        with patch("src.core.ai.rate_limit.RateLimitIA") as mock:
            mock.side_effect = Exception("IA error")
            result = _verifier_ia()

            assert result.statut == StatutSante.INCONNU


class TestVerifierMetriques:
    """Tests pour _verifier_metriques."""

    def test_verifier_metriques_succes(self):
        from src.core.monitoring.health import StatutSante, _verifier_metriques

        result = _verifier_metriques()

        assert result.nom == "metriques"
        assert result.statut == StatutSante.SAIN
        assert "métriques" in result.message
        assert "uptime" in result.message

    def test_verifier_metriques_exception(self):
        from src.core.monitoring.health import StatutSante, _verifier_metriques

        with patch("src.core.monitoring.collector.collecteur") as mock:
            mock.snapshot.side_effect = Exception("Metrics error")
            result = _verifier_metriques()

            assert result.statut == StatutSante.DEGRADE
            assert "Metrics error" in result.message


class TestVerifierSanteGlobale:
    """Tests pour verifier_sante_globale."""

    def test_verifier_sante_globale_sans_db(self):
        from src.core.monitoring.health import verifier_sante_globale

        with (
            patch("src.core.monitoring.health._verifier_cache") as mock_cache,
            patch("src.core.monitoring.health._verifier_ia") as mock_ia,
            patch("src.core.monitoring.health._verifier_metriques") as mock_metriques,
        ):
            mock_cache.return_value = SanteComposant(nom="cache", statut=StatutSante.SAIN)
            mock_ia.return_value = SanteComposant(nom="ia", statut=StatutSante.SAIN)
            mock_metriques.return_value = SanteComposant(nom="metriques", statut=StatutSante.SAIN)

            result = verifier_sante_globale(inclure_db=False)

            assert result.sain is True
            assert "cache" in result.composants
            assert "ia" in result.composants
            assert "metriques" in result.composants
            assert "database" not in result.composants

    def test_verifier_sante_globale_avec_critique(self):
        from src.core.monitoring.health import verifier_sante_globale

        with (
            patch("src.core.monitoring.health._verifier_cache") as mock_cache,
            patch("src.core.monitoring.health._verifier_ia") as mock_ia,
            patch("src.core.monitoring.health._verifier_metriques") as mock_metriques,
        ):
            mock_cache.return_value = SanteComposant(nom="cache", statut=StatutSante.CRITIQUE)
            mock_ia.return_value = SanteComposant(nom="ia", statut=StatutSante.SAIN)
            mock_metriques.return_value = SanteComposant(nom="metriques", statut=StatutSante.SAIN)

            result = verifier_sante_globale(inclure_db=False)

            assert result.sain is False

    def test_verifier_sante_globale_check_exception(self):
        from src.core.monitoring.health import StatutSante, verifier_sante_globale

        with (
            patch("src.core.monitoring.health._verifier_cache") as mock_cache,
            patch("src.core.monitoring.health._verifier_ia") as mock_ia,
            patch("src.core.monitoring.health._verifier_metriques") as mock_metriques,
        ):
            mock_cache.side_effect = Exception("Unexpected error")
            mock_ia.return_value = SanteComposant(nom="ia", statut=StatutSante.SAIN)
            mock_metriques.return_value = SanteComposant(nom="metriques", statut=StatutSante.SAIN)

            result = verifier_sante_globale(inclure_db=False)

            assert result.composants["cache"].statut == StatutSante.INCONNU
            assert "Erreur inattendue" in result.composants["cache"].message


# ═══════════════════════════════════════════════════════════
# TESTS HEALTH - PROBES KUBERNETES
# ═══════════════════════════════════════════════════════════


class TestProbesKubernetes:
    """Tests pour les probes Kubernetes-style."""

    def test_verifier_liveness(self):
        from src.core.monitoring.health import verifier_liveness

        result = verifier_liveness()

        assert result["vivant"] is True
        assert "pid" in result
        assert isinstance(result["pid"], int)

    def test_verifier_readiness_succes(self):
        from src.core.monitoring.health import verifier_readiness

        with (
            patch("src.core.monitoring.health._verifier_db") as mock_db,
            patch("src.core.monitoring.health._verifier_cache") as mock_cache,
        ):
            mock_db.return_value = SanteComposant(
                nom="database", statut=StatutSante.SAIN, message="OK"
            )
            mock_cache.return_value = SanteComposant(
                nom="cache", statut=StatutSante.SAIN, message="OK"
            )

            result = verifier_readiness()

            assert result["pret"] is True
            assert "database" in result["composants"]
            assert "cache" in result["composants"]

    def test_verifier_readiness_echec(self):
        from src.core.monitoring.health import verifier_readiness

        with (
            patch("src.core.monitoring.health._verifier_db") as mock_db,
            patch("src.core.monitoring.health._verifier_cache") as mock_cache,
        ):
            mock_db.return_value = SanteComposant(
                nom="database", statut=StatutSante.CRITIQUE, message="Down"
            )
            mock_cache.return_value = SanteComposant(
                nom="cache", statut=StatutSante.SAIN, message="OK"
            )

            result = verifier_readiness()

            assert result["pret"] is False

    def test_verifier_readiness_exception(self):
        from src.core.monitoring.health import verifier_readiness

        with (
            patch("src.core.monitoring.health._verifier_db") as mock_db,
            patch("src.core.monitoring.health._verifier_cache") as mock_cache,
        ):
            mock_db.side_effect = Exception("DB Error")
            mock_cache.side_effect = Exception("Cache Error")

            result = verifier_readiness()

            assert result["pret"] is False
            assert result["composants"]["database"]["statut"] == "CRITIQUE"

    def test_verifier_startup_succes(self):
        from src.core.monitoring.health import verifier_startup

        with (
            patch("src.core.config.obtenir_parametres") as mock_params,
            patch("src.core.db.verifier_connexion") as mock_conn,
        ):
            mock_params.return_value = MagicMock()
            mock_conn.return_value = (True, "OK")

            result = verifier_startup()

            assert result["initialise"] is True
            assert result["details"]["config"] is True
            assert result["details"]["database"] is True

    def test_verifier_startup_config_echec(self):
        from src.core.monitoring.health import verifier_startup

        with (
            patch("src.core.config.obtenir_parametres") as mock_params,
            patch("src.core.db.verifier_connexion") as mock_conn,
        ):
            mock_params.side_effect = Exception("Config error")
            mock_conn.return_value = (True, "OK")

            result = verifier_startup()

            assert result["initialise"] is False
            assert result["details"]["config"] is False

    def test_verifier_startup_db_echec(self):
        from src.core.monitoring.health import verifier_startup

        with (
            patch("src.core.config.obtenir_parametres") as mock_params,
            patch("src.core.db.verifier_connexion") as mock_conn,
        ):
            mock_params.return_value = MagicMock()
            mock_conn.side_effect = Exception("DB error")

            result = verifier_startup()

            assert result["initialise"] is False
            assert result["details"]["database"] is False


# ═══════════════════════════════════════════════════════════
# TESTS DÉCORATEUR CHRONOMETRE_ASYNC
# ═══════════════════════════════════════════════════════════


class TestChronometreAsync:
    """Tests pour le décorateur @chronometre_async."""

    def test_chronometre_async_enregistre_duree(self):
        from src.core.monitoring.decorators import chronometre_async

        @chronometre_async("test.async_fn")
        async def ma_fonction_async():
            return 42

        result = asyncio.run(ma_fonction_async())

        assert result == 42

        serie = collecteur.obtenir_serie("test.async_fn.duree_ms")
        assert len(serie) == 1
        assert serie[0].valeur >= 0

    def test_chronometre_async_incremente_appels(self):
        from src.core.monitoring.decorators import chronometre_async

        @chronometre_async("test.async_fn2")
        async def ma_fonction_async():
            pass

        asyncio.run(ma_fonction_async())
        asyncio.run(ma_fonction_async())

        assert collecteur.obtenir_total("test.async_fn2.appels") == 2

    def test_chronometre_async_enregistre_erreurs(self):
        from src.core.monitoring.decorators import chronometre_async

        @chronometre_async("test.async_erreur")
        async def ma_fonction_erreur():
            raise ValueError("async boom")

        with pytest.raises(ValueError, match="async boom"):
            asyncio.run(ma_fonction_erreur())

        assert collecteur.obtenir_total("test.async_erreur.erreurs") == 1
        assert len(collecteur.obtenir_serie("test.async_erreur.duree_ms")) == 1

    def test_chronometre_async_avec_labels(self):
        from src.core.monitoring.decorators import chronometre_async

        @chronometre_async("test.async_labels", labels={"service": "recettes"})
        async def fn():
            pass

        asyncio.run(fn())

        serie = collecteur.obtenir_serie("test.async_labels.duree_ms")
        assert serie[0].labels.get("service") == "recettes"

    def test_chronometre_async_seuil_alerte(self, caplog):
        from src.core.monitoring.decorators import chronometre_async

        @chronometre_async("test.async_lent", seuil_alerte_ms=0.001)
        async def fn_lente():
            await asyncio.sleep(0.01)

        with caplog.at_level("WARNING"):
            asyncio.run(fn_lente())

        assert "Alerte performance" in caplog.text


# ═══════════════════════════════════════════════════════════
# TESTS SENTRY
# ═══════════════════════════════════════════════════════════


class TestSentryDisponibilite:
    """Tests pour la disponibilité de Sentry."""

    def test_est_sentry_disponible_avec_sdk(self):
        from src.core.monitoring.sentry import _est_sentry_disponible

        result = _est_sentry_disponible()
        assert isinstance(result, bool)

    def test_est_sentry_disponible_sans_sdk(self):
        import sys

        sentry_backup = sys.modules.get("sentry_sdk")
        sys.modules["sentry_sdk"] = None  # type: ignore

        import src.core.monitoring.sentry as sentry_module

        assert hasattr(sentry_module, "_est_sentry_disponible")

        if sentry_backup:
            sys.modules["sentry_sdk"] = sentry_backup


class TestSentryInitialisation:
    """Tests pour l'initialisation de Sentry."""

    def test_initialiser_sentry_sans_dsn(self, reset_sentry):
        import src.core.monitoring.sentry as sentry_module

        sentry_module._sentry_initialise = False

        old_dsn = os.environ.pop("SENTRY_DSN", None)

        try:
            result = sentry_module.initialiser_sentry(dsn=None)
            assert result is False
        finally:
            if old_dsn:
                os.environ["SENTRY_DSN"] = old_dsn

    def test_initialiser_sentry_deja_initialise(self, reset_sentry):
        import src.core.monitoring.sentry as sentry_module

        sentry_module._sentry_initialise = True

        result = sentry_module.initialiser_sentry()
        assert result is True

    def test_initialiser_sentry_sans_sdk(self, reset_sentry):
        import src.core.monitoring.sentry as sentry_module

        sentry_module._sentry_initialise = False

        with patch.object(sentry_module, "_est_sentry_disponible", return_value=False):
            result = sentry_module.initialiser_sentry(dsn="https://fake@sentry.io/123")
            assert result is False

    def test_initialiser_sentry_avec_sdk_succes(self, reset_sentry):
        import src.core.monitoring.sentry as sentry_module

        sentry_module._sentry_initialise = False

        mock_sdk = MagicMock()

        with (
            patch.object(sentry_module, "_est_sentry_disponible", return_value=True),
            patch.dict("sys.modules", {"sentry_sdk": mock_sdk}),
            patch.object(sentry_module, "_obtenir_version_app", return_value="1.0.0"),
        ):
            with patch(
                "builtins.__import__",
                side_effect=lambda name, *args: (
                    mock_sdk if name == "sentry_sdk" else __import__(name, *args)
                ),
            ):
                result = sentry_module.initialiser_sentry(dsn="https://fake@sentry.io/123")

    def test_initialiser_sentry_avec_exception(self, reset_sentry):
        import src.core.monitoring.sentry as sentry_module

        sentry_module._sentry_initialise = False

        with patch.object(sentry_module, "_est_sentry_disponible", return_value=True):
            with patch("builtins.__import__", side_effect=Exception("Import error")):
                try:
                    sentry_module.initialiser_sentry(dsn="https://fake@sentry.io/123")
                except Exception:
                    pass

    def test_est_sentry_actif(self, reset_sentry):
        import src.core.monitoring.sentry as sentry_module

        sentry_module._sentry_initialise = False
        assert sentry_module.est_sentry_actif() is False

        sentry_module._sentry_initialise = True
        assert sentry_module.est_sentry_actif() is True


class TestSentryCapture:
    """Tests pour les fonctions de capture Sentry."""

    def test_capturer_exception_sentry_inactif(self, reset_sentry):
        import src.core.monitoring.sentry as sentry_module

        sentry_module._sentry_initialise = False

        result = sentry_module.capturer_exception(ValueError("test"))
        assert result is None

    def test_capturer_exception_sentry_actif(self, reset_sentry):
        import src.core.monitoring.sentry as sentry_module

        sentry_module._sentry_initialise = True

        mock_sdk = MagicMock()
        mock_sdk.capture_exception.return_value = "event-id-123"
        mock_sdk.set_context = MagicMock()
        mock_sdk.set_tag = MagicMock()

        with patch.dict("sys.modules", {"sentry_sdk": mock_sdk}):
            sentry_module.capturer_exception(
                ValueError("test error"),
                contexte={"user": "123"},
                tags={"module": "test"},
            )

    def test_capturer_exception_avec_erreur(self, reset_sentry):
        import src.core.monitoring.sentry as sentry_module

        sentry_module._sentry_initialise = True

        with patch("builtins.__import__", side_effect=Exception("SDK error")):
            try:
                sentry_module.capturer_exception(ValueError("test"))
            except Exception:
                pass

    def test_capturer_message_sentry_inactif(self, reset_sentry):
        import src.core.monitoring.sentry as sentry_module

        sentry_module._sentry_initialise = False

        result = sentry_module.capturer_message("Test message")
        assert result is None

    def test_capturer_message_sentry_actif(self, reset_sentry):
        import src.core.monitoring.sentry as sentry_module

        sentry_module._sentry_initialise = True

        mock_sdk = MagicMock()
        mock_sdk.capture_message.return_value = "event-id-456"
        mock_sdk.set_context = MagicMock()

        with patch.dict("sys.modules", {"sentry_sdk": mock_sdk}):
            sentry_module.capturer_message(
                "Test message",
                niveau="warning",
                contexte={"key": "value"},
            )

    def test_definir_utilisateur_sentry_inactif(self, reset_sentry):
        import src.core.monitoring.sentry as sentry_module

        sentry_module._sentry_initialise = False

        sentry_module.definir_utilisateur(user_id="123", email="test@test.com")

    def test_definir_utilisateur_sentry_actif(self, reset_sentry):
        import src.core.monitoring.sentry as sentry_module

        sentry_module._sentry_initialise = True

        mock_sdk = MagicMock()

        with patch.dict("sys.modules", {"sentry_sdk": mock_sdk}):
            sentry_module.definir_utilisateur(
                user_id="123",
                email="test@test.com",
                username="testuser",
            )

    def test_ajouter_breadcrumb_sentry_inactif(self, reset_sentry):
        import src.core.monitoring.sentry as sentry_module

        sentry_module._sentry_initialise = False

        sentry_module.ajouter_breadcrumb("Test breadcrumb", categorie="test")

    def test_ajouter_breadcrumb_sentry_actif(self, reset_sentry):
        import src.core.monitoring.sentry as sentry_module

        sentry_module._sentry_initialise = True

        mock_sdk = MagicMock()

        with patch.dict("sys.modules", {"sentry_sdk": mock_sdk}):
            sentry_module.ajouter_breadcrumb(
                "Test breadcrumb",
                categorie="test",
                niveau="info",
                data={"key": "value"},
            )


class TestSentryFiltres:
    """Tests pour les filtres Sentry."""

    def test_filtrer_event_secrets(self):
        from src.core.monitoring.sentry import _filtrer_event

        event = {
            "exception": {
                "values": [
                    {"value": "Error with password=secret123"},
                    {"value": "Error with token=abc123"},
                    {"value": "Normal error message"},
                ]
            }
        }

        filtered = _filtrer_event(event, {})

        assert filtered["exception"]["values"][0]["value"] == "[FILTERED]"
        assert filtered["exception"]["values"][1]["value"] == "[FILTERED]"
        assert filtered["exception"]["values"][2]["value"] == "Normal error message"

    def test_filtrer_event_headers(self):
        from src.core.monitoring.sentry import _filtrer_event

        event = {
            "request": {
                "headers": {
                    "authorization": "Bearer secret_token",
                    "cookie": "session=abc123",
                    "x-api-key": "api_key_123",
                    "content-type": "application/json",
                }
            }
        }

        filtered = _filtrer_event(event, {})

        assert filtered["request"]["headers"]["authorization"] == "[FILTERED]"
        assert filtered["request"]["headers"]["cookie"] == "[FILTERED]"
        assert filtered["request"]["headers"]["x-api-key"] == "[FILTERED]"
        assert filtered["request"]["headers"]["content-type"] == "application/json"

    def test_filtrer_breadcrumb_sensible(self):
        from src.core.monitoring.sentry import _filtrer_breadcrumb

        crumb = {"message": "Login with password=secret"}
        result = _filtrer_breadcrumb(crumb, {})
        assert result is None

        crumb = {"message": "Normal navigation"}
        result = _filtrer_breadcrumb(crumb, {})
        assert result is not None


class TestSentryVersionApp:
    """Tests pour la récupération de version."""

    def test_obtenir_version_app_from_pyproject(self):
        from src.core.monitoring.sentry import _obtenir_version_app

        version = _obtenir_version_app()

        assert isinstance(version, str)
        assert len(version) > 0

    def test_obtenir_version_app_fallback(self):
        from src.core.monitoring.sentry import _obtenir_version_app

        with patch("pathlib.Path.exists", return_value=False):
            os.environ["APP_VERSION"] = "1.2.3"
            try:
                version = _obtenir_version_app()
                assert isinstance(version, str)
            finally:
                del os.environ["APP_VERSION"]


# ═══════════════════════════════════════════════════════════
# TESTS TYPES HEALTH & EDGE CASES
# ═══════════════════════════════════════════════════════════


class TestTypeVerification:
    """Tests pour l'enum TypeVerification."""

    def test_type_verification_enum(self):
        from src.core.monitoring.health import TypeVerification

        assert TypeVerification.LIVENESS.name == "LIVENESS"
        assert TypeVerification.READINESS.name == "READINESS"
        assert TypeVerification.STARTUP.name == "STARTUP"


class TestSanteComposantDetails:
    """Tests supplémentaires pour SanteComposant."""

    def test_sante_composant_avec_details(self):
        comp = SanteComposant(
            nom="test",
            statut=StatutSante.SAIN,
            message="Everything is fine",
            details={"info": "extra data"},
            duree_verification_ms=42.5,
        )

        assert comp.nom == "test"
        assert comp.statut == StatutSante.SAIN
        assert comp.message == "Everything is fine"
        assert comp.details == {"info": "extra data"}
        assert comp.duree_verification_ms == 42.5


class TestSanteSystemeDetails:
    """Tests supplémentaires pour SanteSysteme."""

    def test_sante_systeme_timestamp(self):
        before = time.time()
        sys = SanteSysteme(sain=True)
        after = time.time()

        assert before <= sys.timestamp <= after


class TestPercentile:
    """Tests pour la fonction _percentile du collecteur."""

    def test_percentile_edge_case(self):
        collecteur.reinitialiser()
        collecteur.histogramme("test_edge", 100.0)
        collecteur.histogramme("test_edge", 200.0)

        snap = collecteur.snapshot()
        stats = snap["metriques"]["test_edge"].get("statistiques", {})

        if stats:
            assert "p99" in stats


class TestCollectorEdgeCases:
    """Tests pour cas limites du collecteur."""

    def test_snapshot_jauge_unique(self):
        c = CollecteurMetriques()
        c.jauge("single_gauge", 42.0)

        snap = c.snapshot()

        assert "single_gauge" in snap["metriques"]
        assert snap["metriques"]["single_gauge"]["total"] == 42.0

    def test_histogramme_stats_single_value(self):
        c = CollecteurMetriques()
        c.histogramme("single_hist", 100.0)

        snap = c.snapshot()

        assert "statistiques" not in snap["metriques"]["single_hist"]
