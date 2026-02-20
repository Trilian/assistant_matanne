"""Tests pour le Bus d'événements domaine — Pub/Sub synchrone."""

import threading
import time

import pytest

from src.services.core.events.bus import (
    BusEvenements,
    EvenementDomaine,
)

# ═══════════════════════════════════════════════════════════
# ÉVÉNEMENT DOMAINE
# ═══════════════════════════════════════════════════════════


class TestEvenementDomaine:
    """Tests de l'objet événement immutable."""

    def test_creation(self):
        event = EvenementDomaine(type="recette.planifiee", data={"recette_id": 1})
        assert event.type == "recette.planifiee"
        assert event.data == {"recette_id": 1}
        assert event.event_id  # Auto-généré

    def test_event_id_auto_genere(self):
        event = EvenementDomaine(type="test.event")
        assert event.event_id.startswith("test.event_")

    def test_event_id_custom(self):
        event = EvenementDomaine(type="test", event_id="custom-123")
        assert event.event_id == "custom-123"

    def test_source(self):
        event = EvenementDomaine(
            type="stock.modifie",
            data={"article_id": 5},
            source="inventaire_service",
        )
        assert event.source == "inventaire_service"

    def test_immutable(self):
        event = EvenementDomaine(type="test")
        with pytest.raises(AttributeError):
            event.type = "modifié"  # type: ignore[misc]


# ═══════════════════════════════════════════════════════════
# BUS D'ÉVÉNEMENTS — SOUSCRIPTION
# ═══════════════════════════════════════════════════════════


class TestBusSouscription:
    """Tests de souscription et désouscription."""

    def setup_method(self):
        self.bus = BusEvenements()

    def test_souscrire_et_recevoir(self):
        received = []
        self.bus.souscrire("test.event", lambda e: received.append(e))
        self.bus.emettre("test.event", {"key": "value"})
        assert len(received) == 1
        assert received[0].data == {"key": "value"}

    def test_multiple_souscriptions(self):
        received_a = []
        received_b = []
        self.bus.souscrire("test.event", lambda e: received_a.append(e))
        self.bus.souscrire("test.event", lambda e: received_b.append(e))
        self.bus.emettre("test.event")
        assert len(received_a) == 1
        assert len(received_b) == 1

    def test_desouscrire(self):
        received = []

        def handler(e):
            received.append(e)

        self.bus.souscrire("test.event", handler)
        assert self.bus.desouscrire("test.event", handler) is True
        self.bus.emettre("test.event")
        assert len(received) == 0

    def test_desouscrire_non_existant(self):
        def handler(e):
            pass

        assert self.bus.desouscrire("inexistant", handler) is False

    def test_alias_anglais(self):
        received = []

        def handler(e):
            received.append(e)

        self.bus.subscribe("test", handler)
        self.bus.emit("test")
        assert len(received) == 1
        assert self.bus.unsubscribe("test", handler) is True


# ═══════════════════════════════════════════════════════════
# BUS D'ÉVÉNEMENTS — ÉMISSION
# ═══════════════════════════════════════════════════════════


class TestBusEmission:
    """Tests de l'émission d'événements."""

    def setup_method(self):
        self.bus = BusEvenements()

    def test_emettre_retourne_nb_handlers(self):
        self.bus.souscrire("test", lambda e: None)
        self.bus.souscrire("test", lambda e: None)
        count = self.bus.emettre("test")
        assert count == 2

    def test_emettre_sans_handlers_retourne_zero(self):
        count = self.bus.emettre("aucun_souscripteur")
        assert count == 0

    def test_emettre_avec_source(self):
        received = []
        self.bus.souscrire("test", lambda e: received.append(e))
        self.bus.emettre("test", source="mon_service")
        assert received[0].source == "mon_service"

    def test_erreur_handler_ne_bloque_pas_les_autres(self):
        """Un handler qui plante ne doit pas empêcher les autres."""
        received = []

        def good_handler(e):
            received.append("ok")

        def bad_handler(e):
            raise RuntimeError("boom")

        self.bus.souscrire("test", bad_handler)
        self.bus.souscrire("test", good_handler)
        count = self.bus.emettre("test")

        # Le bon handler doit quand même s'exécuter
        assert "ok" in received
        assert count >= 1  # Au moins le bon handler

    def test_bus_suspendu_ne_emet_pas(self):
        received = []
        self.bus.souscrire("test", lambda e: received.append(e))
        self.bus.suspendre()
        self.bus.emettre("test")
        assert len(received) == 0

    def test_bus_repris_emet(self):
        received = []
        self.bus.souscrire("test", lambda e: received.append(e))
        self.bus.suspendre()
        self.bus.emettre("test")
        self.bus.reprendre()
        self.bus.emettre("test")
        assert len(received) == 1


# ═══════════════════════════════════════════════════════════
# WILDCARDS
# ═══════════════════════════════════════════════════════════


class TestBusWildcards:
    """Tests des patterns wildcard."""

    def setup_method(self):
        self.bus = BusEvenements()

    def test_wildcard_basique(self):
        received = []
        self.bus.souscrire("stock.*", lambda e: received.append(e))
        self.bus.emettre("stock.modifie")
        self.bus.emettre("stock.ajoute")
        assert len(received) == 2

    def test_wildcard_ne_matche_pas_autre_domaine(self):
        received = []
        self.bus.souscrire("stock.*", lambda e: received.append(e))
        self.bus.emettre("recette.planifiee")
        assert len(received) == 0

    def test_global_wildcard(self):
        """Le wildcard * reçoit tous les événements."""
        received = []
        self.bus.souscrire("*", lambda e: received.append(e))
        self.bus.emettre("stock.modifie")
        self.bus.emettre("recette.planifiee")
        self.bus.emettre("autre.chose")
        assert len(received) == 3

    def test_wildcard_et_exact_combinés(self):
        """Un handler wildcard et un exact reçoivent tous les deux l'événement."""
        received_exact = []
        received_wild = []
        self.bus.souscrire("stock.modifie", lambda e: received_exact.append(e))
        self.bus.souscrire("stock.*", lambda e: received_wild.append(e))
        self.bus.emettre("stock.modifie")
        assert len(received_exact) == 1
        assert len(received_wild) == 1


# ═══════════════════════════════════════════════════════════
# PRIORITÉ
# ═══════════════════════════════════════════════════════════


class TestBusPriorite:
    """Tests des handlers prioritaires."""

    def setup_method(self):
        self.bus = BusEvenements()

    def test_priorite_ordre_execution(self):
        """Les handlers haute priorité s'exécutent en premier."""
        order = []
        self.bus.souscrire("test", lambda e: order.append("low"), priority=0)
        self.bus.souscrire("test", lambda e: order.append("high"), priority=10)
        self.bus.souscrire("test", lambda e: order.append("mid"), priority=5)
        self.bus.emettre("test")
        assert order == ["high", "mid", "low"]


# ═══════════════════════════════════════════════════════════
# HISTORIQUE & MÉTRIQUES
# ═══════════════════════════════════════════════════════════


class TestBusHistorique:
    """Tests de l'historique et des métriques."""

    def setup_method(self):
        self.bus = BusEvenements(historique_taille=5)

    def test_historique_enregistre(self):
        self.bus.souscrire("test", lambda e: None)
        self.bus.emettre("test", {"a": 1})
        self.bus.emettre("test", {"a": 2})
        historique = self.bus.obtenir_historique()
        assert len(historique) == 2

    def test_historique_limite(self):
        """L'historique ne dépasse pas la taille configurée."""
        for i in range(10):
            self.bus.emettre("test", {"i": i})
        historique = self.bus.obtenir_historique()
        assert len(historique) <= 5

    def test_historique_filtre_par_type(self):
        self.bus.emettre("stock.modifie")
        self.bus.emettre("recette.planifiee")
        self.bus.emettre("stock.ajoute")
        historique = self.bus.obtenir_historique(type_evenement="stock.modifie")
        assert len(historique) == 1

    def test_metriques(self):
        self.bus.souscrire("test", lambda e: None)
        self.bus.emettre("test")
        self.bus.emettre("test")
        metriques = self.bus.obtenir_metriques()
        assert metriques["actif"] is True
        assert metriques["total_souscriptions"] >= 1
        assert "test" in metriques["metriques_par_type"]
        assert metriques["metriques_par_type"]["test"]["emissions"] == 2

    def test_reinitialiser(self):
        self.bus.souscrire("test", lambda e: None)
        self.bus.emettre("test")
        self.bus.reinitialiser()
        assert self.bus.obtenir_historique() == []
        metriques = self.bus.obtenir_metriques()
        assert metriques["total_souscriptions"] == 0


# ═══════════════════════════════════════════════════════════
# THREAD SAFETY
# ═══════════════════════════════════════════════════════════


@pytest.mark.concurrency
class TestBusThreadSafety:
    """Tests de la sécurité thread."""

    def test_emission_concurrente(self):
        """Plusieurs threads émettent en même temps."""
        bus = BusEvenements()
        counter = {"value": 0}
        lock = threading.Lock()

        def handler(e):
            with lock:
                counter["value"] += 1

        bus.souscrire("concurrent", handler)

        threads = []
        for _ in range(10):
            t = threading.Thread(target=lambda: bus.emettre("concurrent"))
            threads.append(t)
            t.start()

        for t in threads:
            t.join(timeout=5)

        assert counter["value"] == 10

    def test_souscription_concurrente(self):
        """Plusieurs threads souscrivent en même temps."""
        bus = BusEvenements()
        handlers = []

        def subscribe_handler(i):
            def noop(e):
                pass

            handlers.append(noop)
            bus.souscrire(f"event_{i}", noop)

        threads = [threading.Thread(target=subscribe_handler, args=(i,)) for i in range(20)]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=5)

        metriques = bus.obtenir_metriques()
        assert metriques["total_souscriptions"] == 20
