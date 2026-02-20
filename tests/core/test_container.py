"""Tests pour le conteneur d'injection de dépendances."""

import pytest

from src.core.container import Conteneur, Scope

# ═══════════════════════════════════════════════════════════
# FIXTURES & HELPERS
# ═══════════════════════════════════════════════════════════


class ServiceA:
    """Service A de test."""

    def __init__(self, valeur: str = "default_a") -> None:
        self.valeur = valeur


class ServiceB:
    """Service B qui dépend de A."""

    def __init__(self, service_a: ServiceA) -> None:
        self.service_a = service_a


class ServiceDisposable:
    """Service avec cleanup."""

    def __init__(self) -> None:
        self.disposed = False

    def dispose(self) -> None:
        self.disposed = True


@pytest.fixture
def conteneur():
    """Conteneur frais pour chaque test."""
    c = Conteneur()
    yield c
    c.reinitialiser()


# ═══════════════════════════════════════════════════════════
# TESTS: ENREGISTREMENT
# ═══════════════════════════════════════════════════════════


class TestEnregistrement:
    """Tests d'enregistrement de composants."""

    def test_singleton_enregistrement(self, conteneur: Conteneur):
        """Enregistrer un singleton."""
        conteneur.singleton(ServiceA, factory=lambda: ServiceA("test"))
        assert conteneur.est_enregistre(ServiceA)

    def test_factory_enregistrement(self, conteneur: Conteneur):
        """Enregistrer un transient."""
        conteneur.factory(ServiceA, factory=lambda: ServiceA("test"))
        assert conteneur.est_enregistre(ServiceA)

    def test_instance_enregistrement(self, conteneur: Conteneur):
        """Enregistrer une instance existante."""
        instance = ServiceA("existant")
        conteneur.instance(ServiceA, instance)
        assert conteneur.est_enregistre(ServiceA)

    def test_alias_enregistrement(self, conteneur: Conteneur):
        """Enregistrer avec alias."""
        conteneur.singleton(ServiceA, factory=lambda: ServiceA("alias"), alias="config")
        assert conteneur.est_enregistre(ServiceA)
        assert conteneur.est_enregistre("config")

    def test_non_enregistre(self, conteneur: Conteneur):
        """Vérifier composant non enregistré."""
        assert not conteneur.est_enregistre(ServiceA)


# ═══════════════════════════════════════════════════════════
# TESTS: RÉSOLUTION
# ═══════════════════════════════════════════════════════════


class TestResolution:
    """Tests de résolution de composants."""

    def test_resolve_singleton(self, conteneur: Conteneur):
        """Résoudre un singleton retourne la même instance."""
        conteneur.singleton(ServiceA, factory=lambda: ServiceA("singleton"))

        a1 = conteneur.resolve(ServiceA)
        a2 = conteneur.resolve(ServiceA)

        assert a1 is a2
        assert a1.valeur == "singleton"

    def test_resolve_transient(self, conteneur: Conteneur):
        """Résoudre un transient retourne une nouvelle instance."""
        conteneur.factory(ServiceA, factory=lambda: ServiceA("transient"))

        a1 = conteneur.resolve(ServiceA)
        a2 = conteneur.resolve(ServiceA)

        assert a1 is not a2
        assert a1.valeur == "transient"

    def test_resolve_instance(self, conteneur: Conteneur):
        """Résoudre une instance pré-enregistrée."""
        original = ServiceA("pre-created")
        conteneur.instance(ServiceA, original)

        resolved = conteneur.resolve(ServiceA)
        assert resolved is original

    def test_resolve_par_alias(self, conteneur: Conteneur):
        """Résoudre via alias."""
        conteneur.singleton(ServiceA, factory=lambda: ServiceA("alias"), alias="cfg")

        par_type = conteneur.resolve(ServiceA)
        par_alias = conteneur.resolve("cfg")

        assert par_type is par_alias

    def test_resolve_avec_dependance(self, conteneur: Conteneur):
        """Résoudre un service avec injection de conteneur."""
        conteneur.singleton(ServiceA, factory=lambda: ServiceA("dep"))
        conteneur.singleton(
            ServiceB,
            factory=lambda c: ServiceB(c.resolve(ServiceA)),
        )

        b = conteneur.resolve(ServiceB)
        assert b.service_a.valeur == "dep"

    def test_resolve_non_enregistre_raise(self, conteneur: Conteneur):
        """Résoudre un composant non enregistré lève KeyError."""
        with pytest.raises(KeyError, match="Composant non enregistré"):
            conteneur.resolve(ServiceA)

    def test_try_resolve_retourne_none(self, conteneur: Conteneur):
        """try_resolve retourne None si non enregistré."""
        assert conteneur.try_resolve(ServiceA) is None

    def test_try_resolve_retourne_instance(self, conteneur: Conteneur):
        """try_resolve retourne l'instance si enregistré."""
        conteneur.singleton(ServiceA, factory=lambda: ServiceA("ok"))
        result = conteneur.try_resolve(ServiceA)
        assert result is not None
        assert result.valeur == "ok"


# ═══════════════════════════════════════════════════════════
# TESTS: LIFECYCLE
# ═══════════════════════════════════════════════════════════


class TestLifecycle:
    """Tests du cycle de vie du conteneur."""

    def test_initialiser_eager(self, conteneur: Conteneur):
        """Initialiser crée tous les singletons."""
        conteneur.singleton(ServiceA, factory=lambda: ServiceA("eager"))
        conteneur.initialiser()

        # L'instance est déjà créée avant resolve
        stats = conteneur.obtenir_statistiques()
        assert stats["instancies"] == 1

    def test_initialiser_idempotent(self, conteneur: Conteneur):
        """Initialiser peut être appelé plusieurs fois."""
        conteneur.singleton(ServiceA, factory=lambda: ServiceA("idem"))
        conteneur.initialiser()
        conteneur.initialiser()  # Pas d'erreur

        assert conteneur.obtenir_statistiques()["instancies"] == 1

    def test_fermer_avec_cleanup(self, conteneur: Conteneur):
        """Fermer appelle les fonctions cleanup."""
        service = ServiceDisposable()
        conteneur.instance(ServiceDisposable, service)
        conteneur.singleton(
            ServiceDisposable,
            factory=lambda: service,
            cleanup=lambda s: s.dispose(),
        )
        # Résoudre pour instancier
        conteneur.resolve(ServiceDisposable)
        conteneur.fermer()

        assert service.disposed

    def test_reinitialiser(self, conteneur: Conteneur):
        """Réinitialiser vide tout."""
        conteneur.singleton(ServiceA, factory=lambda: ServiceA("reset"))
        conteneur.resolve(ServiceA)
        conteneur.reinitialiser()

        assert not conteneur.est_enregistre(ServiceA)
        assert conteneur.obtenir_statistiques()["total_enregistres"] == 0

    def test_initialiser_avec_erreur_partielle(self, conteneur: Conteneur):
        """Initialiser gère les erreurs de factory."""

        def factory_qui_echoue():
            raise ValueError("Config manquante")

        conteneur.singleton(ServiceA, factory=factory_qui_echoue)
        conteneur.singleton(ServiceB, factory=lambda c: ServiceB(ServiceA("fallback")))

        # Ne doit pas planter
        conteneur.initialiser()

        # ServiceB devrait être instancié malgré l'échec de ServiceA
        stats = conteneur.obtenir_statistiques()
        assert stats["initialise"]


# ═══════════════════════════════════════════════════════════
# TESTS: INTROSPECTION
# ═══════════════════════════════════════════════════════════


class TestIntrospection:
    """Tests d'introspection du conteneur."""

    def test_lister_composants(self, conteneur: Conteneur):
        """Lister les composants enregistrés."""
        conteneur.singleton(ServiceA, factory=lambda: ServiceA())
        conteneur.factory(ServiceB, factory=lambda c: ServiceB(c.resolve(ServiceA)))

        composants = conteneur.lister_composants()
        assert "ServiceA" in composants
        assert "ServiceB" in composants
        assert composants["ServiceA"]["scope"] == "singleton"
        assert composants["ServiceB"]["scope"] == "transient"

    def test_statistiques(self, conteneur: Conteneur):
        """Obtenir les statistiques."""
        conteneur.singleton(ServiceA, factory=lambda: ServiceA())
        conteneur.factory(ServiceB, factory=lambda c: ServiceB(c.resolve(ServiceA)))

        stats = conteneur.obtenir_statistiques()
        assert stats["total_enregistres"] == 2
        assert stats["singletons"] == 1
        assert stats["transients"] == 1
        assert stats["instancies"] == 0

    def test_repr(self, conteneur: Conteneur):
        """Repr du conteneur."""
        assert "0 composants" in repr(conteneur)
        conteneur.singleton(ServiceA, factory=lambda: ServiceA())
        assert "1 composants" in repr(conteneur)


# ═══════════════════════════════════════════════════════════
# TESTS: THREAD-SAFETY
# ═══════════════════════════════════════════════════════════


class TestThreadSafety:
    """Tests de thread-safety."""

    def test_resolve_concurrent(self, conteneur: Conteneur):
        """Résolution concurrente d'un singleton."""
        import threading

        call_count = 0

        def slow_factory():
            nonlocal call_count
            call_count += 1
            import time

            time.sleep(0.01)
            return ServiceA(f"instance_{call_count}")

        conteneur.singleton(ServiceA, factory=slow_factory)

        results: list[ServiceA] = []
        errors: list[Exception] = []

        def resolver():
            try:
                results.append(conteneur.resolve(ServiceA))
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=resolver) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert not errors
        assert len(results) == 10
        # Tous doivent être la même instance (singleton)
        assert all(r is results[0] for r in results)
