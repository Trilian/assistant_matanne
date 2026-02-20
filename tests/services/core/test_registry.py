"""Tests pour le ServiceRegistry — Registre centralisé thread-safe."""

import threading

import pytest

from src.services.core.registry import ServiceRegistry

# ═══════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════


class DummyService:
    """Service factice pour les tests."""

    def __init__(self):
        self.initialized = True
        self.call_count = 0

    def do_work(self):
        self.call_count += 1
        return "done"


class DummyServiceWithHealth:
    """Service factice avec health check."""

    def __init__(self):
        self.healthy = True

    def health_check(self):
        from src.services.core.base.protocols import ServiceHealth, ServiceStatus

        return ServiceHealth(
            status=ServiceStatus.HEALTHY if self.healthy else ServiceStatus.UNHEALTHY,
            service_name="dummy",
        )


class FailingService:
    """Service qui échoue à l'initialisation."""

    def __init__(self):
        raise RuntimeError("Impossible d'initialiser")


# ═══════════════════════════════════════════════════════════
# ENREGISTREMENT
# ═══════════════════════════════════════════════════════════


class TestRegistryEnregistrement:
    """Tests d'enregistrement de services."""

    def setup_method(self):
        self.registry = ServiceRegistry()

    def test_enregistrer_factory(self):
        self.registry.enregistrer("dummy", DummyService)
        assert self.registry.est_enregistre("dummy") is True
        assert self.registry.est_instancie("dummy") is False

    def test_enregistrer_instance(self):
        instance = DummyService()
        self.registry.enregistrer_instance("dummy", instance)
        assert self.registry.est_enregistre("dummy") is True
        assert self.registry.est_instancie("dummy") is True

    def test_enregistrer_avec_tags(self):
        self.registry.enregistrer("dummy", DummyService, tags={"cuisine", "ia"})
        assert self.registry.est_enregistre("dummy") is True

    def test_alias_anglais(self):
        self.registry.register("english_service", DummyService)
        assert self.registry.is_registered("english_service") is True


# ═══════════════════════════════════════════════════════════
# OBTENTION
# ═══════════════════════════════════════════════════════════


class TestRegistryObtention:
    """Tests d'obtention de services (lazy instantiation)."""

    def setup_method(self):
        self.registry = ServiceRegistry()

    def test_obtenir_cree_instance(self):
        self.registry.enregistrer("dummy", DummyService)
        service = self.registry.obtenir("dummy")
        assert isinstance(service, DummyService)
        assert service.initialized is True

    def test_obtenir_retourne_meme_instance(self):
        """Singleton: le même objet est retourné à chaque appel."""
        self.registry.enregistrer("dummy", DummyService)
        s1 = self.registry.obtenir("dummy")
        s2 = self.registry.obtenir("dummy")
        assert s1 is s2

    def test_obtenir_non_enregistre_leve_key_error(self):
        with pytest.raises(KeyError, match="non enregistré"):
            self.registry.obtenir("inexistant")

    def test_obtenir_type(self):
        self.registry.enregistrer("dummy", DummyService)
        service = self.registry.obtenir_type("dummy", DummyService)
        assert isinstance(service, DummyService)

    def test_obtenir_type_mauvais_type(self):
        self.registry.enregistrer("dummy", DummyService)
        with pytest.raises(TypeError, match="attendu"):
            self.registry.obtenir_type("dummy", DummyServiceWithHealth)

    def test_obtenir_instance_pre_creee(self):
        instance = DummyService()
        instance.call_count = 42
        self.registry.enregistrer_instance("pre", instance)
        retrieved = self.registry.obtenir("pre")
        assert retrieved.call_count == 42

    def test_obtenir_service_qui_echoue(self):
        self.registry.enregistrer("failing", FailingService)
        with pytest.raises(RuntimeError, match="Impossible d'initialiser"):
            self.registry.obtenir("failing")

    def test_alias_anglais(self):
        self.registry.register("svc", DummyService)
        service = self.registry.get("svc")
        assert isinstance(service, DummyService)

    def test_get_typed(self):
        self.registry.register("svc", DummyService)
        service = self.registry.get_typed("svc", DummyService)
        assert isinstance(service, DummyService)


# ═══════════════════════════════════════════════════════════
# REQUÊTES
# ═══════════════════════════════════════════════════════════


class TestRegistryRequetes:
    """Tests des requêtes (tag, lister, etc.)."""

    def setup_method(self):
        self.registry = ServiceRegistry()

    def test_par_tag(self):
        self.registry.enregistrer("svc_a", DummyService, tags={"cuisine"})
        self.registry.enregistrer("svc_b", DummyServiceWithHealth, tags={"cuisine", "ia"})
        self.registry.enregistrer("svc_c", DummyService, tags={"jeux"})

        cuisine = self.registry.par_tag("cuisine")
        assert "svc_a" in cuisine
        assert "svc_b" in cuisine
        assert "svc_c" not in cuisine

    def test_lister(self):
        self.registry.enregistrer("a", DummyService)
        self.registry.enregistrer("b", DummyService)
        services = self.registry.lister()
        assert "a" in services
        assert "b" in services

    def test_est_instancie(self):
        self.registry.enregistrer("dummy", DummyService)
        assert self.registry.est_instancie("dummy") is False
        self.registry.obtenir("dummy")
        assert self.registry.est_instancie("dummy") is True


# ═══════════════════════════════════════════════════════════
# HEALTH CHECK
# ═══════════════════════════════════════════════════════════


class TestRegistryHealthCheck:
    """Tests du health check centralisé."""

    def setup_method(self):
        self.registry = ServiceRegistry()

    def test_health_check_global_tous_healthy(self):
        self.registry.enregistrer("svc_a", DummyServiceWithHealth)
        self.registry.enregistrer("svc_b", DummyServiceWithHealth)
        # Force l'instanciation
        self.registry.obtenir("svc_a")
        self.registry.obtenir("svc_b")

        health = self.registry.health_check_global()
        assert health["global_status"] == "healthy"
        assert health["erreurs"] == 0
        assert health["instantiated"] == 2

    def test_health_check_service_sans_methode(self):
        """Un service sans health_check est marqué healthy par défaut."""
        self.registry.enregistrer("simple", DummyService)
        self.registry.obtenir("simple")

        health = self.registry.health_check_global()
        assert health["services"]["simple"]["status"] == "healthy"
        assert health["services"]["simple"]["note"] == "no health_check method"

    def test_health_check_service_non_instancie(self):
        self.registry.enregistrer("non_cree", DummyService)
        health = self.registry.health_check_global()
        assert health["services"]["non_cree"]["status"] == "not_instantiated"


# ═══════════════════════════════════════════════════════════
# MÉTRIQUES
# ═══════════════════════════════════════════════════════════


class TestRegistryMetriques:
    """Tests des métriques d'utilisation."""

    def setup_method(self):
        self.registry = ServiceRegistry()

    def test_metriques_apres_acces(self):
        self.registry.enregistrer("dummy", DummyService)
        self.registry.obtenir("dummy")
        self.registry.obtenir("dummy")
        self.registry.obtenir("dummy")

        metriques = self.registry.obtenir_metriques()
        assert metriques["total_enregistres"] == 1
        assert metriques["total_instancies"] == 1
        assert metriques["services"]["dummy"]["accès"] == 3
        assert metriques["services"]["dummy"]["instancié"] is True


# ═══════════════════════════════════════════════════════════
# RÉINITIALISATION
# ═══════════════════════════════════════════════════════════


class TestRegistryReinitialisation:
    """Tests de réinitialisation des services."""

    def setup_method(self):
        self.registry = ServiceRegistry()

    def test_reinitialiser_un_service(self):
        self.registry.enregistrer("dummy", DummyService)
        s1 = self.registry.obtenir("dummy")
        self.registry.reinitialiser("dummy")
        assert self.registry.est_instancie("dummy") is False
        s2 = self.registry.obtenir("dummy")
        assert s1 is not s2  # Nouvelle instance

    def test_reinitialiser_tous(self):
        self.registry.enregistrer("a", DummyService)
        self.registry.enregistrer("b", DummyService)
        self.registry.obtenir("a")
        self.registry.obtenir("b")
        self.registry.reinitialiser()
        assert self.registry.est_instancie("a") is False
        assert self.registry.est_instancie("b") is False


# ═══════════════════════════════════════════════════════════
# THREAD SAFETY
# ═══════════════════════════════════════════════════════════


@pytest.mark.concurrency
class TestRegistryThreadSafety:
    """Tests de la sécurité thread (double-checked locking)."""

    def test_obtenir_concurrent_meme_instance(self):
        """Plusieurs threads obtiennent le même service — créé une seule fois."""
        registry = ServiceRegistry()
        registry.enregistrer("dummy", DummyService)

        instances = []
        lock = threading.Lock()

        def worker():
            service = registry.obtenir("dummy")
            with lock:
                instances.append(service)

        threads = [threading.Thread(target=worker) for _ in range(20)]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=5)

        # Toutes les instances doivent être le même objet
        assert len(instances) == 20
        assert all(inst is instances[0] for inst in instances)

    def test_enregistrement_concurrent(self):
        """Plusieurs threads enregistrent en même temps."""
        registry = ServiceRegistry()

        def register_worker(i):
            registry.enregistrer(f"svc_{i}", DummyService, tags={f"tag_{i}"})

        threads = [threading.Thread(target=register_worker, args=(i,)) for i in range(20)]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=5)

        assert len(registry.lister()) == 20
