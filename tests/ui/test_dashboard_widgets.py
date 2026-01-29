"""Tests unitaires pour les widgets dashboard et logique UI pure."""

import pytest
from datetime import date, datetime, timedelta
from unittest.mock import MagicMock, patch


# ═══════════════════════════════════════════════════════════
# TESTS DASHBOARD_WIDGETS - GRAPHIQUES PLOTLY
# ═══════════════════════════════════════════════════════════


class TestGraphiqueRepartitionRepas:
    """Tests pour graphique_repartition_repas."""

    def test_graphique_avec_donnees_valides(self):
        """Création graphique avec données."""
        from src.ui.components.dashboard_widgets import graphique_repartition_repas
        
        planning_data = [
            {"type_repas": "déjeuner"},
            {"type_repas": "déjeuner"},
            {"type_repas": "dîner"},
            {"type_repas": "petit_déjeuner"},
        ]
        
        fig = graphique_repartition_repas(planning_data)
        
        assert fig is not None
        # Vérifier que c'est un Pie chart
        assert len(fig.data) > 0
        assert fig.data[0].type == "pie"

    def test_graphique_liste_vide_retourne_none(self):
        """Liste vide retourne None."""
        from src.ui.components.dashboard_widgets import graphique_repartition_repas
        
        result = graphique_repartition_repas([])
        
        assert result is None

    def test_comptage_types_repas(self):
        """Vérification comptage par type."""
        from src.ui.components.dashboard_widgets import graphique_repartition_repas
        
        planning_data = [
            {"type_repas": "déjeuner"},
            {"type_repas": "déjeuner"},
            {"type_repas": "déjeuner"},
            {"type_repas": "dîner"},
        ]
        
        fig = graphique_repartition_repas(planning_data)
        
        # Les valeurs du pie chart doivent contenir 3 et 1
        assert fig is not None
        values = list(fig.data[0].values)
        assert 3 in values and 1 in values


class TestGraphiqueInventaireCategories:
    """Tests pour graphique_inventaire_categories."""

    def test_graphique_avec_inventaire(self):
        """Création graphique avec inventaire."""
        from src.ui.components.dashboard_widgets import graphique_inventaire_categories
        
        inventaire = [
            {"categorie": "Fruits", "statut": "ok"},
            {"categorie": "Fruits", "statut": "critique"},
            {"categorie": "Légumes", "statut": "ok"},
            {"categorie": "Viandes", "statut": "sous_seuil"},
        ]
        
        fig = graphique_inventaire_categories(inventaire)
        
        assert fig is not None
        # Vérifier barres empilées (2 traces)
        assert len(fig.data) == 2

    def test_graphique_inventaire_vide(self):
        """Inventaire vide retourne None."""
        from src.ui.components.dashboard_widgets import graphique_inventaire_categories
        
        result = graphique_inventaire_categories([])
        
        assert result is None


class TestGraphiqueActiviteSemaine:
    """Tests pour graphique_activite_semaine."""

    def test_graphique_avec_activites(self):
        """Création graphique avec activités."""
        from src.ui.components.dashboard_widgets import graphique_activite_semaine
        
        today = date.today()
        activites = [
            {"date": today - timedelta(days=i), "count": i * 2, "type": "action"}
            for i in range(7)
        ]
        
        fig = graphique_activite_semaine(activites)
        
        assert fig is not None
        # Scatter plot avec fill
        assert fig.data[0].type == "scatter"

    def test_graphique_activites_vides(self):
        """Activités vides génère graphique vide."""
        from src.ui.components.dashboard_widgets import graphique_activite_semaine
        
        # Même avec liste vide, retourne un graphique (7 jours à 0)
        fig = graphique_activite_semaine([])
        
        assert fig is not None
        # Tous les counts doivent être 0
        assert all(y == 0 for y in fig.data[0].y)


class TestGraphiqueProgressionObjectifs:
    """Tests pour graphique_progression_objectifs."""

    def test_graphique_avec_objectifs(self):
        """Création graphique avec objectifs."""
        from src.ui.components.dashboard_widgets import graphique_progression_objectifs
        
        objectifs = [
            {"nom": "Objectif A", "actuel": 80, "cible": 100},
            {"nom": "Objectif B", "actuel": 50, "cible": 100},
            {"nom": "Objectif C", "actuel": 30, "cible": 100},
        ]
        
        fig = graphique_progression_objectifs(objectifs)
        
        assert fig is not None
        # 2 traces: fond et progression
        assert len(fig.data) == 2

    def test_graphique_objectifs_vides(self):
        """Objectifs vides retourne None."""
        from src.ui.components.dashboard_widgets import graphique_progression_objectifs
        
        result = graphique_progression_objectifs([])
        
        assert result is None

    def test_progression_couleurs(self):
        """Test couleurs selon progression."""
        # 80%+ = vert, 50-79% = orange, <50% = rouge
        from src.ui.components.dashboard_widgets import graphique_progression_objectifs
        
        objectifs = [
            {"nom": "Haut", "actuel": 90, "cible": 100},  # 90% → vert
            {"nom": "Moyen", "actuel": 60, "cible": 100},  # 60% → orange
            {"nom": "Bas", "actuel": 20, "cible": 100},  # 20% → rouge
        ]
        
        fig = graphique_progression_objectifs(objectifs)
        
        # Les barres de progression (trace 1)
        colors = fig.data[1].marker.color
        
        # Vert pour 90%
        assert "#4CAF50" in colors
        # Orange pour 60%
        assert "#FFB74D" in colors
        # Rouge pour 20%
        assert "#FF5722" in colors


class TestIndicateurSanteSysteme:
    """Tests pour indicateur_sante_systeme."""

    @patch('src.core.database.verifier_connexion')
    @patch('src.core.cache_multi.get_cache')
    def test_sante_tout_ok(self, mock_cache, mock_db):
        """Système sain retourne ok."""
        from src.ui.components.dashboard_widgets import indicateur_sante_systeme
        
        mock_db.return_value = True
        mock_cache.return_value.get_stats.return_value = {"hit_rate": "80%"}
        
        status = indicateur_sante_systeme()
        
        assert status["global"] == "ok"
        assert len(status["details"]) >= 1


# ═══════════════════════════════════════════════════════════
# TESTS BASE_IO - IMPORT/EXPORT
# ═══════════════════════════════════════════════════════════


class TestIOConfig:
    """Tests pour IOConfig."""

    def test_config_creation(self):
        """Création d'une config IO."""
        from src.ui.core.base_io import IOConfig
        
        config = IOConfig(
            field_mapping={"nom": "Nom", "quantite": "Quantité"},
            required_fields=["nom"]
        )
        
        assert config.field_mapping["nom"] == "Nom"
        assert "nom" in config.required_fields

    def test_config_avec_transformers(self):
        """Config avec transformateurs."""
        from src.ui.core.base_io import IOConfig
        
        config = IOConfig(
            field_mapping={"nom": "Nom"},
            required_fields=["nom"],
            transformers={"nom": str.upper}
        )
        
        assert config.transformers is not None
        assert config.transformers["nom"]("test") == "TEST"


class TestBaseIOServiceTransformers:
    """Tests pour _apply_transformers."""

    def test_transformer_applique(self):
        """Transformer appliqué aux items."""
        from src.ui.core.base_io import IOConfig, BaseIOService
        
        config = IOConfig(
            field_mapping={"nom": "Nom"},
            required_fields=["nom"],
            transformers={"nom": str.upper}
        )
        
        service = BaseIOService(config)
        items = [{"nom": "test"}, {"nom": "autre"}]
        
        result = service._apply_transformers(items)
        
        assert result[0]["nom"] == "TEST"
        assert result[1]["nom"] == "AUTRE"

    def test_transformer_erreur_silencieuse(self):
        """Erreur transformer silencieuse (warning)."""
        from src.ui.core.base_io import IOConfig, BaseIOService
        
        def bad_transformer(x):
            raise ValueError("Erreur!")
        
        config = IOConfig(
            field_mapping={"nom": "Nom"},
            required_fields=["nom"],
            transformers={"nom": bad_transformer}
        )
        
        service = BaseIOService(config)
        items = [{"nom": "test"}]
        
        # Ne doit pas lever d'exception
        result = service._apply_transformers(items)
        
        # La valeur originale est préservée
        assert result[0]["nom"] == "test"

    def test_transformer_champ_absent(self):
        """Transformer ignoré si champ absent."""
        from src.ui.core.base_io import IOConfig, BaseIOService
        
        config = IOConfig(
            field_mapping={"nom": "Nom", "autre": "Autre"},
            required_fields=["nom"],
            transformers={"autre": str.upper}
        )
        
        service = BaseIOService(config)
        items = [{"nom": "test"}]  # pas de champ "autre"
        
        result = service._apply_transformers(items)
        
        # Pas d'erreur, item retourné tel quel
        assert result[0]["nom"] == "test"
        assert "autre" not in result[0]


# ═══════════════════════════════════════════════════════════
# TESTS BASE_FORM - FORM BUILDER
# ═══════════════════════════════════════════════════════════


class TestFormBuilderInit:
    """Tests d'initialisation FormBuilder."""

    def test_creation_form(self):
        """Création d'un FormBuilder."""
        from src.ui.core.base_form import FormBuilder
        
        form = FormBuilder("test_form", title="Mon Formulaire")
        
        assert form.form_id == "test_form"
        assert form.title == "Mon Formulaire"
        assert form.fields == []

    def test_creation_form_sans_titre(self):
        """FormBuilder sans titre."""
        from src.ui.core.base_form import FormBuilder
        
        form = FormBuilder("test_form")
        
        assert form.title is None


class TestFormBuilderAddFields:
    """Tests pour ajout de champs."""

    def test_add_text_field(self):
        """Ajout champ texte."""
        from src.ui.core.base_form import FormBuilder
        
        form = FormBuilder("test")
        form.add_text("nom", "Nom", required=True, default="test")
        
        assert len(form.fields) == 1
        field = form.fields[0]
        assert field["type"] == "text"
        assert field["name"] == "nom"
        assert field["required"] is True
        assert "Nom *" in field["label"]

    def test_add_textarea_field(self):
        """Ajout textarea."""
        from src.ui.core.base_form import FormBuilder
        
        form = FormBuilder("test")
        form.add_textarea("desc", "Description", height=150)
        
        field = form.fields[0]
        assert field["type"] == "textarea"
        assert field["height"] == 150

    def test_add_number_field(self):
        """Ajout champ nombre."""
        from src.ui.core.base_form import FormBuilder
        
        form = FormBuilder("test")
        form.add_number("quantite", "Quantité", min_value=0, max_value=100, step=0.5)
        
        field = form.fields[0]
        assert field["type"] == "number"
        assert field["min_value"] == 0
        assert field["max_value"] == 100
        assert field["step"] == 0.5

    def test_add_select_field(self):
        """Ajout select."""
        from src.ui.core.base_form import FormBuilder
        
        options = ["Option 1", "Option 2", "Option 3"]
        form = FormBuilder("test")
        form.add_select("choix", "Choix", options=options, default="Option 2")
        
        field = form.fields[0]
        assert field["type"] == "select"
        assert field["options"] == options
        assert field["default"] == "Option 2"

    def test_add_multiselect_field(self):
        """Ajout multiselect."""
        from src.ui.core.base_form import FormBuilder
        
        options = ["A", "B", "C"]
        form = FormBuilder("test")
        form.add_multiselect("tags", "Tags", options=options, default=["A", "C"])
        
        field = form.fields[0]
        assert field["type"] == "multiselect"
        assert field["default"] == ["A", "C"]

    def test_add_checkbox_field(self):
        """Ajout checkbox."""
        from src.ui.core.base_form import FormBuilder
        
        form = FormBuilder("test")
        form.add_checkbox("actif", "Actif", default=True)
        
        field = form.fields[0]
        assert field["type"] == "checkbox"
        assert field["default"] is True

    def test_add_date_field(self):
        """Ajout champ date."""
        from src.ui.core.base_form import FormBuilder
        
        today = date.today()
        form = FormBuilder("test")
        form.add_date("date_debut", "Date début", default=today)
        
        field = form.fields[0]
        assert field["type"] == "date"
        assert field["default"] == today

    def test_chainable_methods(self):
        """Méthodes chaînables."""
        from src.ui.core.base_form import FormBuilder
        
        form = (
            FormBuilder("test")
            .add_text("nom", "Nom", required=True)
            .add_number("age", "Âge")
            .add_checkbox("actif", "Actif")
        )
        
        assert len(form.fields) == 3


# ═══════════════════════════════════════════════════════════
# TESTS CALCULS PURS (EXTRAITS DES WIDGETS)
# ═══════════════════════════════════════════════════════════


class TestCalculProgressionCouleur:
    """Tests calcul couleur selon progression."""

    def test_couleur_progression_haute(self):
        """≥80% = vert."""
        def calc_color(progression):
            return "#4CAF50" if progression >= 80 else "#FFB74D" if progression >= 50 else "#FF5722"
        
        assert calc_color(100) == "#4CAF50"
        assert calc_color(80) == "#4CAF50"
        assert calc_color(85) == "#4CAF50"

    def test_couleur_progression_moyenne(self):
        """50-79% = orange."""
        def calc_color(progression):
            return "#4CAF50" if progression >= 80 else "#FFB74D" if progression >= 50 else "#FF5722"
        
        assert calc_color(79) == "#FFB74D"
        assert calc_color(50) == "#FFB74D"
        assert calc_color(65) == "#FFB74D"

    def test_couleur_progression_basse(self):
        """<50% = rouge."""
        def calc_color(progression):
            return "#4CAF50" if progression >= 80 else "#FFB74D" if progression >= 50 else "#FF5722"
        
        assert calc_color(49) == "#FF5722"
        assert calc_color(0) == "#FF5722"
        assert calc_color(25) == "#FF5722"


class TestCalculProgression:
    """Tests calcul de progression."""

    def test_progression_normale(self):
        """Calcul progression standard."""
        def calc_progression(actuel, cible):
            return min(100, (actuel / cible) * 100) if cible > 0 else 0
        
        assert calc_progression(50, 100) == 50.0
        assert calc_progression(75, 100) == 75.0

    def test_progression_plafonnee(self):
        """Progression plafonnée à 100%."""
        def calc_progression(actuel, cible):
            return min(100, (actuel / cible) * 100) if cible > 0 else 0
        
        assert calc_progression(150, 100) == 100
        assert calc_progression(200, 50) == 100

    def test_progression_cible_zero(self):
        """Cible à zéro retourne 0."""
        def calc_progression(actuel, cible):
            return min(100, (actuel / cible) * 100) if cible > 0 else 0
        
        assert calc_progression(50, 0) == 0


class TestComptageTypesRepas:
    """Tests comptage types de repas."""

    def test_comptage_simple(self):
        """Comptage basique par type."""
        planning_data = [
            {"type_repas": "déjeuner"},
            {"type_repas": "déjeuner"},
            {"type_repas": "dîner"},
        ]
        
        types_count = {}
        for repas in planning_data:
            type_repas = repas.get("type_repas", "autre")
            types_count[type_repas] = types_count.get(type_repas, 0) + 1
        
        assert types_count["déjeuner"] == 2
        assert types_count["dîner"] == 1

    def test_comptage_type_manquant(self):
        """Type manquant → "autre"."""
        planning_data = [
            {"nom": "Repas sans type"},
        ]
        
        types_count = {}
        for repas in planning_data:
            type_repas = repas.get("type_repas", "autre")
            types_count[type_repas] = types_count.get(type_repas, 0) + 1
        
        assert types_count["autre"] == 1


class TestGroupementCategories:
    """Tests groupement par catégories."""

    def test_groupement_inventaire(self):
        """Groupement inventaire par catégorie."""
        inventaire = [
            {"categorie": "Fruits", "statut": "ok"},
            {"categorie": "Fruits", "statut": "critique"},
            {"categorie": "Légumes", "statut": "ok"},
        ]
        
        categories = {}
        for article in inventaire:
            cat = article.get("categorie", "Autre")
            if cat not in categories:
                categories[cat] = {"total": 0, "bas": 0}
            categories[cat]["total"] += 1
            if article.get("statut") in ["critique", "sous_seuil"]:
                categories[cat]["bas"] += 1
        
        assert categories["Fruits"]["total"] == 2
        assert categories["Fruits"]["bas"] == 1
        assert categories["Légumes"]["total"] == 1
        assert categories["Légumes"]["bas"] == 0


# ═══════════════════════════════════════════════════════════
# TESTS LABELS FRANÇAIS
# ═══════════════════════════════════════════════════════════


class TestLabelsFrancais:
    """Tests pour labels français."""

    def test_labels_types_repas(self):
        """Labels français pour types de repas."""
        labels_fr = {
            "petit_déjeuner": "Petit-déjeuner",
            "déjeuner": "Déjeuner",
            "dîner": "Dîner",
            "goûter": "Goûter",
        }
        
        assert labels_fr["déjeuner"] == "Déjeuner"
        assert labels_fr["petit_déjeuner"] == "Petit-déjeuner"

    def test_labels_jours_semaine(self):
        """Labels jours de la semaine."""
        jours_fr = ["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"]
        
        # Lundi = index 0
        lundi = date(2024, 1, 1)  # C'était un lundi
        label = jours_fr[lundi.weekday()]
        
        assert label == "Lun"

    def test_icones_activites(self):
        """Icônes par type d'activité."""
        icones = {
            "recette": "🍽️",
            "inventaire": "📦",
            "courses": "🛒",
            "planning": "📅",
            "famille": "👨‍👩‍👦",
            "maison": "🏠",
        }
        
        assert icones["recette"] == "🍽️"
        assert icones["maison"] == "🏠"

    def test_icone_type_inconnu(self):
        """Type inconnu → icône par défaut."""
        icones = {
            "recette": "🍽️",
        }
        
        type_activite = "inconnu"
        icone = icones.get(type_activite, "📌")
        
        assert icone == "📌"


# ═══════════════════════════════════════════════════════════
# TESTS IO SERVICE FACTORY
# ═══════════════════════════════════════════════════════════


class TestBaseIOServiceFactory:
    """Tests pour factory create_io_service."""

    def test_create_io_service(self):
        """Factory crée service."""
        from src.ui.core.base_io import IOConfig, create_io_service
        
        config = IOConfig(
            field_mapping={"nom": "Nom"},
            required_fields=["nom"]
        )
        
        service = create_io_service(config)
        
        assert service is not None
        assert service.config == config
