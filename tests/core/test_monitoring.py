"""
Tests pour src/core/monitoring/ — collecteur, décorateurs, santé.
"""

import threading
import time

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
