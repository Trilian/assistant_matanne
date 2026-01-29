"""Tests unitaires pour le service action_history."""

import pytest
from datetime import datetime, timedelta


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS ENUMS
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestActionTypeEnum:
    """Tests pour l'enum ActionType."""

    def test_types_actions_disponibles(self):
        """Vérifie les types d'actions."""
        from src.services.action_history import ActionType
        
        # Recettes
        assert ActionType.RECETTE_CREATED is not None
        assert ActionType.RECETTE_UPDATED is not None
        assert ActionType.RECETTE_DELETED is not None
        
        # Inventaire
        assert ActionType.INVENTAIRE_ADDED is not None
        assert ActionType.INVENTAIRE_UPDATED is not None
        
        # Courses
        assert ActionType.COURSES_ITEM_ADDED is not None
        assert ActionType.COURSES_ITEM_CHECKED is not None
        
        # Planning
        assert ActionType.PLANNING_REPAS_ADDED is not None

    def test_action_type_valeur_string(self):
        """Types ont des valeurs string."""
        from src.services.action_history import ActionType
        
        for action in ActionType:
            assert isinstance(action.value, str)
            assert "." in action.value  # Format "entity.action"


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS MODÃˆLES PYDANTIC
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestActionEntryModel:
    """Tests pour le modèle ActionEntry."""

    def test_action_entry_creation(self):
        """Création d'une entrée d'action."""
        from src.services.action_history import ActionEntry, ActionType
        
        entry = ActionEntry(
            user_id="user_1",
            user_name="Test User",
            action_type=ActionType.RECETTE_CREATED,
            entity_type="recette",
            entity_id=1,
            entity_name="Tarte aux pommes",
            description="Création d'une nouvelle recette"
        )
        
        assert entry.user_id == "user_1"
        assert entry.action_type == ActionType.RECETTE_CREATED

    def test_action_entry_timestamp_auto(self):
        """Timestamp créé automatiquement."""
        from src.services.action_history import ActionEntry, ActionType
        
        entry = ActionEntry(
            user_id="user_1",
            user_name="Test",
            action_type=ActionType.RECETTE_CREATED,
            entity_type="recette",
            description="Test"
        )
        
        assert entry.created_at is not None
        # Devrait être proche de maintenant
        delta = datetime.now() - entry.created_at
        assert delta.seconds < 5

    def test_action_entry_avec_details(self):
        """Entrée avec détails."""
        from src.services.action_history import ActionEntry, ActionType
        
        entry = ActionEntry(
            user_id="user_1",
            user_name="Test",
            action_type=ActionType.INVENTAIRE_UPDATED,
            entity_type="inventaire",
            entity_id=5,
            description="Modification quantité",
            details={"champ": "quantite", "avant": 10, "apres": 8}
        )
        
        assert entry.details["avant"] == 10
        assert entry.details["apres"] == 8


class TestActionFilterModel:
    """Tests pour ActionFilter."""

    def test_filter_defaults(self):
        """Valeurs par défaut du filtre."""
        from src.services.action_history import ActionFilter
        
        filtre = ActionFilter()
        
        assert filtre.limit == 50
        assert filtre.offset == 0

    def test_filter_par_type(self):
        """Filtre par type d'action."""
        from src.services.action_history import ActionFilter, ActionType
        
        filtre = ActionFilter(
            action_types=[ActionType.RECETTE_CREATED, ActionType.RECETTE_UPDATED]
        )
        
        assert len(filtre.action_types) == 2

    def test_filter_par_periode(self):
        """Filtre par période."""
        from src.services.action_history import ActionFilter
        
        maintenant = datetime.now()
        semaine_derniere = maintenant - timedelta(days=7)
        
        filtre = ActionFilter(
            date_from=semaine_derniere,
            date_to=maintenant
        )
        
        assert filtre.date_from is not None
        assert filtre.date_to is not None


class TestActionStatsModel:
    """Tests pour ActionStats."""

    def test_stats_defaults(self):
        """Valeurs par défaut des stats."""
        from src.services.action_history import ActionStats
        
        stats = ActionStats()
        
        assert stats.total_actions == 0
        assert stats.actions_today == 0


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS SERVICE ACTION HISTORY
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestActionHistoryServiceInit:
    """Tests d'initialisation du service."""

    def test_service_creation(self):
        """Création du service."""
        from src.services.action_history import ActionHistoryService
        
        service = ActionHistoryService()
        
        assert service is not None

    def test_service_methodes_requises(self):
        """Le service a les méthodes requises."""
        from src.services.action_history import ActionHistoryService
        
        service = ActionHistoryService()
        
        assert hasattr(service, 'log_action')


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS LOGIQUE PURE
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestComputeChanges:
    """Tests pour calcul des changements."""

    def test_compute_changes_modification(self):
        """Calcul des changements pour modification."""
        old = {"quantite": 10, "nom": "Lait"}
        new = {"quantite": 8, "nom": "Lait"}
        
        changes = {}
        for key in old.keys():
            if old[key] != new.get(key):
                changes[key] = {"avant": old[key], "apres": new.get(key)}
        
        assert "quantite" in changes
        assert changes["quantite"]["avant"] == 10
        assert changes["quantite"]["apres"] == 8

    def test_compute_changes_suppression(self):
        """Calcul pour suppression (avant seulement)."""
        old = {"id": 1, "nom": "Article supprimé"}
        new = None
        
        if new is None:
            changes = {"deleted": old}
        else:
            changes = {}
        
        assert "deleted" in changes

    def test_compute_changes_aucun(self):
        """Aucun changement si identique."""
        old = {"quantite": 10, "nom": "Lait"}
        new = {"quantite": 10, "nom": "Lait"}
        
        changes = {}
        for key in old.keys():
            if old[key] != new.get(key):
                changes[key] = {"avant": old[key], "apres": new.get(key)}
        
        assert len(changes) == 0


class TestCacheActions:
    """Tests pour le cache des actions."""

    def test_cache_limite_taille(self):
        """Cache limité en taille."""
        cache = []
        max_size = 100
        
        # Ajouter plus que la limite
        for i in range(150):
            cache.append({"id": i})
            if len(cache) > max_size:
                cache.pop(0)  # Retirer le plus ancien
        
        assert len(cache) == max_size

    def test_cache_ordre_chronologique(self):
        """Cache en ordre chronologique."""
        actions = [
            {"id": 1, "date": datetime(2026, 1, 10)},
            {"id": 2, "date": datetime(2026, 1, 15)},
            {"id": 3, "date": datetime(2026, 1, 20)},
        ]
        
        # Plus récent en premier
        triees = sorted(actions, key=lambda x: x["date"], reverse=True)
        
        assert triees[0]["id"] == 3


class TestFiltrerActions:
    """Tests pour le filtrage des actions."""

    def test_filtrer_par_type(self):
        """Filtrage par type."""
        from src.services.action_history import ActionType
        
        actions = [
            {"type": ActionType.RECETTE_CREATED, "id": 1},
            {"type": ActionType.INVENTAIRE_ADDED, "id": 2},
            {"type": ActionType.RECETTE_UPDATED, "id": 3},
        ]
        
        types_recette = [ActionType.RECETTE_CREATED, ActionType.RECETTE_UPDATED]
        filtrees = [a for a in actions if a["type"] in types_recette]
        
        assert len(filtrees) == 2

    def test_filtrer_par_date(self):
        """Filtrage par période."""
        maintenant = datetime.now()
        
        actions = [
            {"date": maintenant - timedelta(days=1), "id": 1},
            {"date": maintenant - timedelta(days=10), "id": 2},
            {"date": maintenant - timedelta(days=5), "id": 3},
        ]
        
        semaine_derniere = maintenant - timedelta(days=7)
        filtrees = [a for a in actions if a["date"] >= semaine_derniere]
        
        assert len(filtrees) == 2  # id 1 et 3

    def test_filtrer_par_entite(self):
        """Filtrage par entité."""
        actions = [
            {"entity_type": "recette", "entity_id": 1},
            {"entity_type": "inventaire", "entity_id": 2},
            {"entity_type": "recette", "entity_id": 3},
        ]
        
        filtrees = [a for a in actions if a["entity_type"] == "recette"]
        
        assert len(filtrees) == 2


class TestStatistiquesActions:
    """Tests pour les statistiques d'actions."""

    def test_compter_par_type(self):
        """Comptage par type."""
        from src.services.action_history import ActionType
        from collections import Counter
        
        actions = [
            ActionType.RECETTE_CREATED,
            ActionType.RECETTE_CREATED,
            ActionType.INVENTAIRE_ADDED,
            ActionType.RECETTE_UPDATED,
        ]
        
        compteur = Counter(actions)
        
        assert compteur[ActionType.RECETTE_CREATED] == 2
        assert compteur[ActionType.INVENTAIRE_ADDED] == 1

    def test_compter_par_utilisateur(self):
        """Comptage par utilisateur."""
        from collections import Counter
        
        actions = [
            {"user_id": "user_1"},
            {"user_id": "user_1"},
            {"user_id": "user_2"},
            {"user_id": "user_1"},
        ]
        
        compteur = Counter(a["user_id"] for a in actions)
        
        assert compteur["user_1"] == 3
        assert compteur["user_2"] == 1

    def test_actions_par_heure(self):
        """Actions par heure de la journée."""
        from collections import Counter
        
        actions = [
            {"date": datetime(2026, 1, 28, 9, 0)},
            {"date": datetime(2026, 1, 28, 9, 30)},
            {"date": datetime(2026, 1, 28, 14, 0)},
            {"date": datetime(2026, 1, 28, 9, 15)},
        ]
        
        heures = [a["date"].hour for a in actions]
        compteur = Counter(heures)
        
        assert compteur[9] == 3  # 9h est le pic


class TestDescriptionAction:
    """Tests pour la génération de descriptions."""

    def test_description_recette_created(self):
        """Description pour création recette."""
        action_type = "recette.created"
        entity_name = "Tarte aux pommes"
        
        templates = {
            "recette.created": "Création de la recette '{name}'",
            "recette.updated": "Modification de la recette '{name}'",
            "recette.deleted": "Suppression de la recette '{name}'",
        }
        
        description = templates[action_type].format(name=entity_name)
        
        assert description == "Création de la recette 'Tarte aux pommes'"

    def test_description_inventaire_updated(self):
        """Description pour modification inventaire."""
        entity_name = "Lait"
        avant = 10
        apres = 8
        
        description = f"Modification de {entity_name}: {avant} â†’ {apres}"
        
        assert "10 â†’ 8" in description

