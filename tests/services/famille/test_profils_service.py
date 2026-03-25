"""
Tests pour src/services/profils.py — ProfilService.

Couvre:
- CRUD profils (obtenir, mettre à jour)
- Changement de profil actif
- PIN: définir, vérifier, supprimer
- Sections protégées
- Export/import configuration (round-trip)
- Réinitialisation de section
- Validation schemas Pydantic
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy.orm import Session

from src.core.models.notifications import PreferenceNotification
from src.core.models.users import ProfilUtilisateur
from src.services.core.utilisateur.profils import (
    AVATARS_DISPONIBLES,
    NOTIFICATIONS_MODULES_DEFAUT,
    PREFERENCES_MODULES_DEFAUT,
    SECTIONS_PROTEGER,
    ProfilService,
    _hasher_pin,
    get_profil_service,
)

# ═══════════════════════════════════════════════════════════
# FIXTURES
# ═══════════════════════════════════════════════════════════


@pytest.fixture
def profil_anne(db: Session) -> ProfilUtilisateur:
    """Crée le profil Anne en base de test."""
    profil = ProfilUtilisateur(
        username="anne",
        display_name="Anne",
        email="anne@test.com",
        avatar_emoji="👩",
        taille_cm=165,
        poids_kg=60.0,
        objectif_pas_quotidien=10000,
        objectif_calories_brulees=500,
        objectif_minutes_actives=30,
        garmin_connected=False,
        theme_prefere="auto",
        preferences_modules=PREFERENCES_MODULES_DEFAUT.copy(),
    )
    db.add(profil)
    db.commit()
    db.refresh(profil)
    return profil


@pytest.fixture
def profil_mathieu(db: Session) -> ProfilUtilisateur:
    """Crée le profil Mathieu en base de test."""
    profil = ProfilUtilisateur(
        username="mathieu",
        display_name="Mathieu",
        email="mathieu@test.com",
        avatar_emoji="👨",
        objectif_pas_quotidien=12000,
        objectif_calories_brulees=600,
        objectif_minutes_actives=45,
        garmin_connected=True,
        theme_prefere="sombre",
    )
    db.add(profil)
    db.commit()
    db.refresh(profil)
    return profil


@pytest.fixture
def deux_profils(profil_anne, profil_mathieu):
    """Les deux profils Anne et Mathieu."""
    return profil_anne, profil_mathieu


@pytest.fixture
def notif_prefs(db: Session) -> PreferenceNotification:
    """Crée des préférences de notification en base."""
    pref = PreferenceNotification(
        id=1,  # BigInteger PK — SQLite ne l'auto-incrémente pas
        courses_rappel=True,
        repas_suggestion=True,
        stock_alerte=True,
        meteo_alerte=True,
        budget_alerte=True,
        modules_actifs=NOTIFICATIONS_MODULES_DEFAUT.copy(),
        canal_prefere="push",
    )
    db.add(pref)
    db.commit()
    db.refresh(pref)
    return pref


# ═══════════════════════════════════════════════════════════
# CONSTANTES
# ═══════════════════════════════════════════════════════════


class TestConstantes:
    """Tests des constantes du service."""

    def test_avatars_disponibles_non_vide(self):
        assert len(AVATARS_DISPONIBLES) > 0

    def test_preferences_modules_defaut_structure(self):
        assert "cuisine" in PREFERENCES_MODULES_DEFAUT
        assert "famille" in PREFERENCES_MODULES_DEFAUT
        assert "maison" in PREFERENCES_MODULES_DEFAUT
        assert "planning" in PREFERENCES_MODULES_DEFAUT
        assert "budget" in PREFERENCES_MODULES_DEFAUT

    def test_preferences_modules_cuisine_champs(self):
        cuisine = PREFERENCES_MODULES_DEFAUT["cuisine"]
        assert "nb_suggestions_ia" in cuisine
        assert "types_cuisine_preferes" in cuisine
        assert "duree_max_batch_min" in cuisine

    def test_notifications_modules_defaut_structure(self):
        for module in ("cuisine", "famille", "maison", "planning", "budget"):
            assert module in NOTIFICATIONS_MODULES_DEFAUT
            assert isinstance(NOTIFICATIONS_MODULES_DEFAUT[module], dict)

    def test_sections_proteger(self):
        assert isinstance(SECTIONS_PROTEGER, list)
        assert "budget" in SECTIONS_PROTEGER
        assert "admin" in SECTIONS_PROTEGER


# ═══════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════


class TestHasherPin:
    """Tests de la fonction de hachage PIN."""

    def test_hash_deterministe(self):
        """Le même PIN produit le même hash."""
        assert _hasher_pin("1234") == _hasher_pin("1234")

    def test_hash_differents_pins(self):
        """Deux PINs différents donnent des hashs différents."""
        assert _hasher_pin("1234") != _hasher_pin("5678")

    def test_hash_longueur_sha256(self):
        """Le hash SHA-256 fait 64 caractères hex."""
        h = _hasher_pin("0000")
        assert len(h) == 64
        assert all(c in "0123456789abcdef" for c in h)


# ═══════════════════════════════════════════════════════════
# FACTORY
# ═══════════════════════════════════════════════════════════


class TestFactory:
    """Tests de la factory singleton."""

    def test_get_profil_service_retourne_instance(self):
        service = get_profil_service()
        assert isinstance(service, ProfilService)

    def test_get_profil_service_singleton(self):
        """Deux appels retournent le même objet."""
        s1 = get_profil_service()
        s2 = get_profil_service()
        assert s1 is s2


# ═══════════════════════════════════════════════════════════
# CRUD — OBTENIR PROFILS
# ═══════════════════════════════════════════════════════════


class TestObtenir:
    """Tests des méthodes de lecture."""

    def test_obtenir_profils_vide(self, patch_db_context):
        """Base vide → liste vide."""
        result = ProfilService.obtenir_profils()
        assert result == []

    def test_obtenir_profils_deux(self, db, deux_profils, patch_db_context):
        """Deux profils insérés → liste de 2."""
        result = ProfilService.obtenir_profils()
        assert len(result) == 2
        noms = {p.username for p in result}
        assert noms == {"anne", "mathieu"}

    def test_obtenir_profil_existant(self, db, profil_anne, patch_db_context):
        """Récupérer un profil existant par username."""
        result = ProfilService.obtenir_profil("anne")
        assert result is not None
        assert result.username == "anne"
        assert result.display_name == "Anne"

    def test_obtenir_profil_inexistant(self, patch_db_context):
        """Username inconnu → None."""
        result = ProfilService.obtenir_profil("inconnu")
        assert result is None

    def test_obtenir_profil_par_id(self, db, profil_anne, patch_db_context):
        """Récupérer un profil par ID."""
        result = ProfilService.obtenir_profil_par_id(profil_anne.id)
        assert result is not None
        assert result.username == "anne"

    def test_obtenir_profil_par_id_inexistant(self, patch_db_context):
        """ID inconnu → None."""
        result = ProfilService.obtenir_profil_par_id(9999)
        assert result is None


# ═══════════════════════════════════════════════════════════
# CRUD — MISE À JOUR
# ═══════════════════════════════════════════════════════════


class TestMettreAJour:
    """Tests de mise à jour de profil."""

    def test_mettre_a_jour_champs_basiques(self, db, profil_anne, patch_db_context):
        """Mise à jour email et display_name."""
        result = ProfilService.mettre_a_jour_profil(
            "anne", {"email": "nouveau@test.com", "display_name": "Anne M."}
        )
        assert result is not None
        assert result.email == "nouveau@test.com"
        assert result.display_name == "Anne M."

    def test_mettre_a_jour_theme(self, db, profil_anne, patch_db_context):
        """Mise à jour du thème préféré."""
        result = ProfilService.mettre_a_jour_profil("anne", {"theme_prefere": "sombre"})
        assert result is not None
        assert result.theme_prefere == "sombre"

    def test_mettre_a_jour_preferences_modules(self, db, profil_anne, patch_db_context):
        """Mise à jour des préférences modules."""
        prefs = {"cuisine": {"nb_suggestions_ia": 10}}
        result = ProfilService.mettre_a_jour_profil("anne", {"preferences_modules": prefs})
        assert result is not None
        assert result.preferences_modules["cuisine"]["nb_suggestions_ia"] == 10

    def test_mettre_a_jour_objectifs_fitness(self, db, profil_anne, patch_db_context):
        """Mise à jour des objectifs fitness."""
        result = ProfilService.mettre_a_jour_profil(
            "anne",
            {
                "objectif_pas_quotidien": 15000,
                "objectif_calories_brulees": 700,
                "objectif_minutes_actives": 60,
            },
        )
        assert result is not None
        assert result.objectif_pas_quotidien == 15000
        assert result.objectif_calories_brulees == 700
        assert result.objectif_minutes_actives == 60

    def test_mettre_a_jour_champ_interdit_ignore(self, db, profil_anne, patch_db_context):
        """Les champs non autorisés sont ignorés silencieusement."""
        result = ProfilService.mettre_a_jour_profil(
            "anne", {"username": "hacker", "pin_hash": "fake"}
        )
        assert result is not None
        # username et pin_hash ne sont pas dans champs_autorises
        assert result.username == "anne"
        assert result.pin_hash is None

    def test_mettre_a_jour_profil_inexistant(self, patch_db_context):
        """Mise à jour d'un profil inexistant → None."""
        result = ProfilService.mettre_a_jour_profil("inconnu", {"email": "x@x.com"})
        assert result is None


# ═══════════════════════════════════════════════════════════
# CHANGEMENT DE PROFIL ACTIF
# ═══════════════════════════════════════════════════════════


class TestChangerProfil:
    """Tests du changement de profil actif."""

    def test_changer_profil_actif_succes(self, db, profil_anne, patch_db_context):
        """Changement vers un profil existant."""
        with patch("src.services.profils.ProfilService.obtenir_profil") as mock_get:
            mock_get.return_value = profil_anne
            result = ProfilService.changer_profil_actif("anne")

        assert result is True

    def test_changer_profil_actif_inexistant(self, patch_db_context):
        """Changement vers un profil inexistant → False."""
        with patch("src.services.profils.ProfilService.obtenir_profil", return_value=None):
            result = ProfilService.changer_profil_actif("inconnu")
        assert result is False


# ═══════════════════════════════════════════════════════════
# PIN / SÉCURITÉ
# ═══════════════════════════════════════════════════════════


class TestPIN:
    """Tests de gestion du PIN."""

    def test_definir_pin(self, db, profil_anne, patch_db_context):
        """Définir un PIN sur un profil."""
        result = ProfilService.definir_pin("anne", "1234")
        assert result is True
        # Vérifier en base
        db.refresh(profil_anne)
        assert profil_anne.pin_hash is not None
        assert profil_anne.pin_hash == _hasher_pin("1234")

    def test_definir_pin_profil_inexistant(self, patch_db_context):
        """PIN sur profil inexistant → False."""
        result = ProfilService.definir_pin("inconnu", "1234")
        assert result is False

    def test_verifier_pin_correct(self, db, profil_anne, patch_db_context):
        """Vérifier un PIN correct."""
        ProfilService.definir_pin("anne", "4567")
        result = ProfilService.verifier_pin("anne", "4567")
        assert result is True

    def test_verifier_pin_incorrect(self, db, profil_anne, patch_db_context):
        """Vérifier un PIN incorrect."""
        ProfilService.definir_pin("anne", "4567")
        result = ProfilService.verifier_pin("anne", "9999")
        assert result is False

    def test_verifier_pin_absent(self, db, profil_anne, patch_db_context):
        """Vérifier PIN quand aucun n'est défini → False."""
        result = ProfilService.verifier_pin("anne", "1234")
        assert result is False

    def test_verifier_pin_profil_inexistant(self, patch_db_context):
        """Vérifier PIN d'un profil inexistant → False."""
        result = ProfilService.verifier_pin("inconnu", "1234")
        assert result is False

    def test_supprimer_pin(self, db, profil_anne, patch_db_context):
        """Supprimer le PIN réinitialise pin_hash et sections."""
        ProfilService.definir_pin("anne", "1234")
        ProfilService.definir_sections_protegees("anne", ["budget", "admin"])

        result = ProfilService.supprimer_pin("anne")
        assert result is True

        db.refresh(profil_anne)
        assert profil_anne.pin_hash is None
        assert profil_anne.sections_protegees is None

    def test_supprimer_pin_profil_inexistant(self, patch_db_context):
        """Supprimer PIN d'un profil inexistant → False."""
        result = ProfilService.supprimer_pin("inconnu")
        assert result is False


# ═══════════════════════════════════════════════════════════
# SECTIONS PROTÉGÉES
# ═══════════════════════════════════════════════════════════


class TestSectionsProtegees:
    """Tests de la gestion des sections protégées."""

    def test_definir_sections(self, db, profil_anne, patch_db_context):
        """Définir les sections protégées."""
        result = ProfilService.definir_sections_protegees("anne", ["budget", "sante"])
        assert result is True
        db.refresh(profil_anne)
        assert profil_anne.sections_protegees == ["budget", "sante"]

    def test_definir_sections_vide(self, db, profil_anne, patch_db_context):
        """Définir une liste vide de sections."""
        result = ProfilService.definir_sections_protegees("anne", [])
        assert result is True
        db.refresh(profil_anne)
        assert profil_anne.sections_protegees == []

    def test_definir_sections_profil_inexistant(self, patch_db_context):
        """Sections sur profil inexistant → False."""
        result = ProfilService.definir_sections_protegees("inconnu", ["admin"])
        assert result is False


# ═══════════════════════════════════════════════════════════
# EXPORT / IMPORT
# ═══════════════════════════════════════════════════════════


class TestExport:
    """Tests d'export de configuration."""

    def test_exporter_configuration_basique(self, db, profil_anne, patch_db_context):
        """Export contient version, profil et santé."""
        export = ProfilService.exporter_configuration("anne")
        assert export["version"] == "1.0"
        assert "timestamp" in export
        assert export["profil"]["username"] == "anne"
        assert export["profil"]["display_name"] == "Anne"
        assert export["sante"]["taille_cm"] == 165
        assert export["sante"]["poids_kg"] == 60.0

    def test_exporter_configuration_profil_inexistant(self, patch_db_context):
        """Export d'un profil inexistant → dict vide."""
        export = ProfilService.exporter_configuration("inconnu")
        assert export == {}

    def test_exporter_configuration_avec_notifications(
        self, db, profil_anne, notif_prefs, patch_db_context
    ):
        """Export inclut les préférences de notification."""
        export = ProfilService.exporter_configuration("anne")
        assert "notifications" in export
        assert export["notifications"]["canal_prefere"] == "push"
        assert export["notifications"]["courses_rappel"] is True

    def test_exporter_preferences_modules(self, db, profil_anne, patch_db_context):
        """Export inclut les préférences par module."""
        export = ProfilService.exporter_configuration("anne")
        prefs = export["profil"]["preferences_modules"]
        assert "cuisine" in prefs
        assert prefs["cuisine"]["nb_suggestions_ia"] == 5

    def test_exporter_theme(self, db, profil_anne, patch_db_context):
        """Export inclut le thème préféré."""
        export = ProfilService.exporter_configuration("anne")
        assert export["profil"]["theme_prefere"] == "auto"


class TestImport:
    """Tests d'import de configuration."""

    def test_importer_configuration_valide(self, db, profil_anne, patch_db_context):
        """Import d'une configuration valide."""
        data = {
            "version": "1.0",
            "profil": {
                "display_name": "Anne Modifiée",
                "email": "new@test.com",
                "avatar_emoji": "🦸‍♀️",
                "theme_prefere": "clair",
                "preferences_modules": {"cuisine": {"nb_suggestions_ia": 8}},
            },
            "sante": {
                "taille_cm": 170,
                "poids_kg": 62.0,
                "objectif_pas_quotidien": 12000,
            },
        }
        ok, msg = ProfilService.importer_configuration("anne", data)
        assert ok is True
        assert "succès" in msg.lower()

        db.refresh(profil_anne)
        assert profil_anne.display_name == "Anne Modifiée"
        assert profil_anne.email == "new@test.com"
        assert profil_anne.taille_cm == 170
        assert profil_anne.objectif_pas_quotidien == 12000

    def test_importer_format_invalide_sans_version(self, db, profil_anne, patch_db_context):
        """Import sans version → erreur."""
        ok, msg = ProfilService.importer_configuration("anne", {"profil": {}})
        assert ok is False
        assert "version" in msg.lower() or "invalide" in msg.lower()

    def test_importer_format_invalide_sans_profil(self, db, profil_anne, patch_db_context):
        """Import sans clé profil → erreur."""
        ok, msg = ProfilService.importer_configuration("anne", {"version": "1.0"})
        assert ok is False

    def test_importer_profil_inexistant(self, patch_db_context):
        """Import sur profil inexistant → erreur."""
        data = {"version": "1.0", "profil": {"display_name": "X"}}
        ok, msg = ProfilService.importer_configuration("inconnu", data)
        assert ok is False
        assert "introuvable" in msg.lower()


class TestExportImportRoundTrip:
    """Tests aller-retour export → import."""

    def test_round_trip_preserves_data(self, db, profil_anne, notif_prefs, patch_db_context):
        """Un export suivi d'un import préserve les données."""
        # Modifier le profil
        ProfilService.mettre_a_jour_profil(
            "anne",
            {
                "display_name": "Anne T.",
                "email": "anne.t@test.com",
                "theme_prefere": "sombre",
                "preferences_modules": {"cuisine": {"nb_suggestions_ia": 12}},
            },
        )

        # Exporter
        export = ProfilService.exporter_configuration("anne")
        assert export["profil"]["display_name"] == "Anne T."

        # Réinitialiser le profil
        ProfilService.mettre_a_jour_profil(
            "anne",
            {
                "display_name": "Anne Reset",
                "email": None,
                "theme_prefere": "auto",
                "preferences_modules": {},
            },
        )

        # Ré-importer
        ok, _ = ProfilService.importer_configuration("anne", export)
        assert ok is True

        db.refresh(profil_anne)
        assert profil_anne.display_name == "Anne T."
        assert profil_anne.email == "anne.t@test.com"
        assert profil_anne.theme_prefere == "sombre"
        assert profil_anne.preferences_modules["cuisine"]["nb_suggestions_ia"] == 12


# ═══════════════════════════════════════════════════════════
# RÉINITIALISATION
# ═══════════════════════════════════════════════════════════


class TestReinitialiser:
    """Tests de réinitialisation de section."""

    def test_reinitialiser_preferences_modules(self, db, profil_anne, patch_db_context):
        """Réinitialiser preferences_modules remet les valeurs par défaut."""
        # Modifier les prefs
        ProfilService.mettre_a_jour_profil(
            "anne", {"preferences_modules": {"cuisine": {"nb_suggestions_ia": 99}}}
        )

        ok, msg = ProfilService.reinitialiser_section("anne", "preferences_modules")
        assert ok is True
        assert "réinitialisées" in msg.lower()

        db.refresh(profil_anne)
        assert profil_anne.preferences_modules == PREFERENCES_MODULES_DEFAUT

    def test_reinitialiser_securite(self, db, profil_anne, patch_db_context):
        """Réinitialiser securite supprime le PIN."""
        ProfilService.definir_pin("anne", "1234")
        ok, msg = ProfilService.reinitialiser_section("anne", "securite")
        assert ok is True
        db.refresh(profil_anne)
        assert profil_anne.pin_hash is None

    def test_reinitialiser_notifications(self, db, profil_anne, patch_db_context):
        """Réinitialiser notifications retourne True."""
        ok, msg = ProfilService.reinitialiser_section("anne", "notifications")
        assert ok is True

    def test_reinitialiser_section_inconnue(self, patch_db_context):
        """Section inconnue → False."""
        ok, msg = ProfilService.reinitialiser_section("anne", "inconnu")
        assert ok is False
        assert "inconnue" in msg.lower()


# ═══════════════════════════════════════════════════════════
# SCHÉMAS PYDANTIC
# ═══════════════════════════════════════════════════════════


class TestSchemasPydantic:
    """Tests des schémas de validation Pydantic."""

    def test_schema_pin_valide(self):
        from src.core.validation.schemas.profils import SchemaPIN

        schema = SchemaPIN(pin="1234")
        assert schema.pin == "1234"

    def test_schema_pin_6_chiffres(self):
        from src.core.validation.schemas.profils import SchemaPIN

        schema = SchemaPIN(pin="123456")
        assert schema.pin == "123456"

    def test_schema_pin_trop_court(self):
        from src.core.validation.schemas.profils import SchemaPIN

        with pytest.raises(Exception):
            SchemaPIN(pin="123")

    def test_schema_pin_trop_long(self):
        from src.core.validation.schemas.profils import SchemaPIN

        with pytest.raises(Exception):
            SchemaPIN(pin="1234567")

    def test_schema_pin_non_numerique(self):
        from src.core.validation.schemas.profils import SchemaPIN

        with pytest.raises(Exception):
            SchemaPIN(pin="abcd")

    def test_schema_profil_edition_valide(self):
        from src.core.validation.schemas.profils import SchemaProfilEdition

        schema = SchemaProfilEdition(
            display_name="Anne",
            email="anne@test.com",
            taille_cm=165,
            poids_kg=62.5,
        )
        assert schema.display_name == "Anne"
        assert schema.email == "anne@test.com"

    def test_schema_profil_edition_minimal(self):
        from src.core.validation.schemas.profils import SchemaProfilEdition

        schema = SchemaProfilEdition(display_name="Anne")
        assert schema.email is None
        assert schema.taille_cm is None
        assert schema.poids_kg is None

    def test_schema_import_configuration_valide(self):
        from src.core.validation.schemas.profils import SchemaImportConfiguration

        schema = SchemaImportConfiguration(
            version="1.0",
            profil={"username": "anne"},
        )
        assert schema.version == "1.0"

    def test_schema_import_configuration_sans_username(self):
        from src.core.validation.schemas.profils import SchemaImportConfiguration

        with pytest.raises(Exception):
            SchemaImportConfiguration(
                version="1.0",
                profil={"display_name": "Test"},  # données mais pas de username
            )

    def test_schema_import_configuration_version_invalide(self):
        from src.core.validation.schemas.profils import SchemaImportConfiguration

        with pytest.raises(Exception):
            SchemaImportConfiguration(
                version="2.0",
                profil={"username": "anne"},
            )
