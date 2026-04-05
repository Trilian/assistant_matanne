"""Tests unitaires pour le bus d'événements et les subscribers (P2-04).

Couvre:
- BusEvenements (émission, souscription, priorité, wildcards, historique)
- Types d'événements domaine (EvenementRecettePlanifiee, etc.)
- Subscribers (invalidation cache, métriques)
"""

import pytest

from src.services.core.events.bus import BusEvenements, EvenementDomaine


# ═══════════════════════════════════════════════════════════
# TESTS BusEvenements
# ═══════════════════════════════════════════════════════════


class TestBusEvenements:
    """Tests pour le bus d'événements."""

    def test_emettre_et_souscrire(self):
        """Un handler reçoit les événements émis."""
        bus = BusEvenements(historique_taille=50)
        received = []

        def handler(event: EvenementDomaine):
            received.append(event)

        bus.souscrire("test.event", handler)
        event = bus.emettre("test.event", data={"key": "value"}, source="test")

        assert len(received) == 1
        assert received[0].type == "test.event"
        assert received[0].data["key"] == "value"
        assert received[0].source == "test"

    def test_desouscrire(self):
        """Après désinscription, le handler ne reçoit plus d'événements."""
        bus = BusEvenements()
        received = []

        def handler(event: EvenementDomaine):
            received.append(event)

        bus.souscrire("test.event", handler)
        bus.emettre("test.event")
        assert len(received) == 1

        bus.desouscrire("test.event", handler)
        bus.emettre("test.event")
        assert len(received) == 1  # Pas de nouveau message

    def test_desouscrire_retourne_false_si_inexistant(self):
        """Désinscription d'un handler non inscrit retourne False."""
        bus = BusEvenements()

        def handler(event):
            pass

        result = bus.desouscrire("inexistant", handler)
        assert result is False

    def test_priorite_handlers(self):
        """Les handlers sont exécutés par ordre de priorité."""
        bus = BusEvenements()
        order = []

        def handler_low(event):
            order.append("low")

        def handler_high(event):
            order.append("high")

        bus.souscrire("test.priority", handler_low, priority=0)
        bus.souscrire("test.priority", handler_high, priority=10)
        bus.emettre("test.priority")

        # La priorité haute devrait être exécutée en premier
        assert order[0] == "high"
        assert order[1] == "low"

    def test_multiple_handlers(self):
        """Plusieurs handlers reçoivent le même événement."""
        bus = BusEvenements()
        results = {"a": False, "b": False}

        def handler_a(event):
            results["a"] = True

        def handler_b(event):
            results["b"] = True

        bus.souscrire("multi.event", handler_a)
        bus.souscrire("multi.event", handler_b)
        bus.emettre("multi.event")

        assert results["a"] is True
        assert results["b"] is True

    def test_historique_evenements(self):
        """L'historique conserve les derniers événements."""
        bus = BusEvenements(historique_taille=5)

        for i in range(10):
            bus.emettre("test.history", data={"i": i})

        historique = bus.obtenir_historique()
        assert len(historique) <= 5

    def test_historique_taille_limitee(self):
        """L'historique ne dépasse pas la taille configurée."""
        bus = BusEvenements(historique_taille=3)
        for i in range(10):
            bus.emettre("event", data={"i": i})

        historique = bus.obtenir_historique()
        assert len(historique) <= 3

    def test_metriques_evenements(self):
        """Les métriques comptent les événements émis."""
        bus = BusEvenements()
        bus.souscrire("metric.test", lambda e: None)

        bus.emettre("metric.test")
        bus.emettre("metric.test")
        bus.emettre("metric.test")

        metriques = bus.obtenir_metriques()
        assert "metric.test" in metriques.get("metriques_par_type", metriques)

    def test_evenement_domaine_immutable(self):
        """EvenementDomaine est immutable (frozen dataclass)."""
        event = EvenementDomaine(
            type="test",
            data={"key": "val"},
            source="test_source",
        )
        assert event.type == "test"
        assert event.data["key"] == "val"
        assert event.source == "test_source"

        with pytest.raises(AttributeError):
            event.type = "modified"

    def test_emettre_retourne_count(self):
        """L'émission retourne le nombre de handlers exécutés."""
        bus = BusEvenements()
        bus.souscrire("return.test", lambda e: None)
        result = bus.emettre("return.test", data={"x": 1})

        # emettre retourne le nombre de handlers exécutés
        assert result == 1

    def test_alias_anglais(self):
        """Les alias anglais (subscribe, emit, unsubscribe) fonctionnent."""
        bus = BusEvenements()
        received = []

        bus.subscribe("alias.test", lambda e: received.append(e))
        bus.emit("alias.test", source="alias")

        assert len(received) == 1

    def test_handler_erreur_ne_bloque_pas(self):
        """Un handler qui lève une exception ne bloque pas les autres."""
        bus = BusEvenements()
        results = []

        def bad_handler(event):
            raise RuntimeError("boom")

        def good_handler(event):
            results.append("ok")

        bus.souscrire("error.test", bad_handler, priority=10)
        bus.souscrire("error.test", good_handler, priority=0)
        bus.emettre("error.test")

        assert "ok" in results


# ═══════════════════════════════════════════════════════════
# TESTS Types d'événements
# ═══════════════════════════════════════════════════════════


class TestTypesEvenements:
    """Tests pour les types d'événements domaine."""

    def test_evenement_recette_planifiee(self):
        """EvenementRecettePlanifiee a les bons champs."""
        from src.services.core.events.events import EvenementRecettePlanifiee

        event = EvenementRecettePlanifiee(
            recette_id=1,
            recette_nom="Tarte",
            date_planification=None,
            repas="dîner",
        )
        assert event.TYPE == "recette.planifiee"
        assert event.recette_id == 1
        assert event.recette_nom == "Tarte"

    def test_evenement_stock_modifie(self):
        """EvenementStockModifie a les bons champs."""
        from src.services.core.events.events import EvenementStockModifie

        event = EvenementStockModifie(
            article_id=5,
            ingredient_nom="Tomates",
            ancienne_quantite=10.0,
            nouvelle_quantite=5.0,
            raison="consommation",
        )
        assert event.TYPE == "stock.modifie"
        assert event.ancienne_quantite == 10.0

    def test_evenement_courses_generees(self):
        """EvenementCoursesGenerees a les bons champs."""
        from src.services.core.events.events import EvenementCoursesGenerees

        event = EvenementCoursesGenerees(
            nb_articles=15,
            source="planning",
            montant_estime=85.50,
        )
        assert event.TYPE == "courses.generees"
        assert event.nb_articles == 15

    def test_evenement_batch_cooking_termine(self):
        """EvenementBatchCookingTermine a les bons champs."""
        from src.services.core.events.events import EvenementBatchCookingTermine

        event = EvenementBatchCookingTermine(
            session_id=1,
            nb_recettes=5,
            nb_portions=20,
            duree_minutes=180,
        )
        assert event.TYPE == "batch_cooking.termine"
        assert event.nb_portions == 20

    def test_evenement_depense_modifiee(self):
        """EvenementDepenseModifiee a les bons champs."""
        from src.services.core.events.events import EvenementDepenseModifiee

        event = EvenementDepenseModifiee(
            depense_id=3,
            categorie="alimentation",
            montant=45.90,
            action="création",
        )
        assert event.TYPE == "depenses.modifiee"
        assert event.montant == 45.90


# ═══════════════════════════════════════════════════════════
# TESTS WILDCARDS & EDGE CASES
# ═══════════════════════════════════════════════════════════


class TestBusWildcards:
    """Tests pour les souscriptions wildcard."""

    def test_wildcard_etoile_simple(self):
        """Le pattern 'recette.*' matche 'recette.creee' et 'recette.modifiee'."""
        bus = BusEvenements()
        received = []

        bus.souscrire("recette.*", lambda e: received.append(e))
        bus.emettre("recette.creee", data={"id": 1})
        bus.emettre("recette.modifiee", data={"id": 2})
        bus.emettre("stock.modifie", data={"id": 3})

        assert len(received) == 2
        assert all(e.type.startswith("recette.") for e in received)

    def test_wildcard_global(self):
        """Le pattern '*' matche tous les événements."""
        bus = BusEvenements()
        received = []

        bus.souscrire("*", lambda e: received.append(e))
        bus.emettre("recette.creee", data={"id": 1})
        bus.emettre("stock.modifie", data={"id": 2})

        assert len(received) == 2

    def test_wildcard_ne_matche_pas_partiellement(self):
        """Le pattern 'stock.*' ne matche pas 'stocks.modifie'."""
        bus = BusEvenements()
        received = []

        bus.souscrire("stock.*", lambda e: received.append(e))
        bus.emettre("stocks.modifie", data={"id": 1})
        bus.emettre("stock.modifie", data={"id": 2})

        assert len(received) == 1


class TestBusEdgeCases:
    """Tests edge cases pour le bus d'événements."""

    def test_handler_erreur_ne_bloque_pas_les_autres(self):
        """Un handler en erreur ne bloque pas les handlers suivants."""
        bus = BusEvenements()
        results = []

        def handler_ok(e):
            results.append("ok")

        def handler_erreur(e):
            raise ValueError("Erreur test")

        bus.souscrire("test.event", handler_ok, priority=10)
        bus.souscrire("test.event", handler_erreur, priority=5)
        bus.souscrire("test.event", handler_ok, priority=1)

        bus.emettre("test.event", data={})
        assert results.count("ok") == 2

    def test_handler_duplique_execute_deux_fois(self):
        """Un même handler souscrit deux fois est exécuté deux fois."""
        bus = BusEvenements()
        count = {"n": 0}

        def handler(e):
            count["n"] += 1

        bus.souscrire("test.event", handler)
        bus.souscrire("test.event", handler)
        bus.emettre("test.event", data={})

        assert count["n"] == 2

    def test_emission_evenement_sans_souscripteur(self):
        """Émettre un événement sans souscripteur ne lève pas d'exception."""
        bus = BusEvenements()
        result = bus.emettre("aucun.souscripteur", data={"test": True})
        assert result == 0

    def test_historique_contient_details(self):
        """L'historique contient les données de l'événement."""
        bus = BusEvenements(historique_taille=10)
        bus.emettre("test.event", data={"clef": "valeur"}, source="test")

        historique = bus.obtenir_historique()
        assert len(historique) == 1
        assert historique[0].data.get("clef") == "valeur"

    def test_desouscrire_empêche_reception(self):
        """Après désabonnement, le handler ne reçoit plus d'événements."""
        bus = BusEvenements()
        received = []

        def handler(e):
            received.append(e)

        bus.souscrire("test.event", handler)
        bus.emettre("test.event", data={})
        assert len(received) == 1

        bus.desouscrire("test.event", handler)
        bus.emettre("test.event", data={})
        assert len(received) == 1
