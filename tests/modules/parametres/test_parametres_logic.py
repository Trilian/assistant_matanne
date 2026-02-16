"""
Tests pour parametres_logic.py - Fonctions pures de gestion des paramètres
"""

from src.modules.parametres.utils import (
    comparer_versions,
    formater_version,
    fusionner_config,
    generer_config_defaut,
    get_preferences_par_categorie,
    valider_email,
    valider_parametres,
    version_est_superieure,
)

# ═══════════════════════════════════════════════════════════
# Tests Validation Paramètres
# ═══════════════════════════════════════════════════════════


class TestValiderParametres:
    """Tests pour valider_parametres."""

    def test_parametres_vides(self):
        """Valide des paramètres vides."""
        valide, erreurs = valider_parametres({})
        assert valide is True
        assert len(erreurs) == 0

    def test_nom_famille_valide(self):
        """Valide un nom de famille correct."""
        valide, erreurs = valider_parametres({"nom_famille": "Dupont"})
        assert valide is True
        assert len(erreurs) == 0

    def test_nom_famille_trop_court(self):
        """Rejette un nom trop court."""
        valide, erreurs = valider_parametres({"nom_famille": "A"})
        assert valide is False
        assert any("2 caractères" in e for e in erreurs)

    def test_nom_famille_vide(self):
        """Rejette un nom vide."""
        valide, erreurs = valider_parametres({"nom_famille": ""})
        assert valide is False

    def test_nom_famille_trop_long(self):
        """Rejette un nom trop long."""
        valide, erreurs = valider_parametres({"nom_famille": "A" * 60})
        assert valide is False
        assert any("50 caractères" in e for e in erreurs)

    def test_email_valide(self):
        """Valide un email correct."""
        valide, erreurs = valider_parametres({"email": "test@example.com"})
        assert valide is True

    def test_email_sans_arobase(self):
        """Rejette un email sans @."""
        valide, erreurs = valider_parametres({"email": "testexample.com"})
        assert valide is False
        assert any("@" in e for e in erreurs)

    def test_email_domaine_invalide(self):
        """Rejette un email avec domaine invalide."""
        valide, erreurs = valider_parametres({"email": "test@invalid"})
        assert valide is False
        assert any("domaine" in e.lower() for e in erreurs)

    def test_devise_valide(self):
        """Valide les devises supportées."""
        for devise in ["EUR", "USD", "GBP", "CHF", "CAD"]:
            valide, erreurs = valider_parametres({"devise": devise})
            assert valide is True, f"Devise {devise} devrait être valide"

    def test_devise_invalide(self):
        """Rejette une devise non supportée."""
        valide, erreurs = valider_parametres({"devise": "JPY"})
        assert valide is False
        assert any("devise" in e.lower() for e in erreurs)

    def test_langue_valide(self):
        """Valide les langues supportées."""
        for langue in ["fr", "en", "es", "de"]:
            valide, erreurs = valider_parametres({"langue": langue})
            assert valide is True

    def test_langue_invalide(self):
        """Rejette une langue non supportée."""
        valide, erreurs = valider_parametres({"langue": "jp"})
        assert valide is False

    def test_theme_valide(self):
        """Valide les thèmes supportés."""
        for theme in ["light", "dark", "auto"]:
            valide, erreurs = valider_parametres({"theme": theme})
            assert valide is True

    def test_theme_invalide(self):
        """Rejette un thème non supporté."""
        valide, erreurs = valider_parametres({"theme": "sepia"})
        assert valide is False

    def test_multiples_erreurs(self):
        """Détecte plusieurs erreurs."""
        valide, erreurs = valider_parametres(
            {"nom_famille": "A", "email": "invalid", "devise": "XYZ"}
        )
        assert valide is False
        assert len(erreurs) >= 3


# ═══════════════════════════════════════════════════════════
# Tests Validation Email
# ═══════════════════════════════════════════════════════════


class TestValiderEmail:
    """Tests pour valider_email."""

    def test_email_valide(self):
        """Valide un email correct."""
        valide, msg = valider_email("user@example.com")
        assert valide is True
        assert msg is None

    def test_email_vide(self):
        """Rejette un email vide."""
        valide, msg = valider_email("")
        assert valide is False
        assert "vide" in msg.lower()

    def test_email_sans_arobase(self):
        """Rejette un email sans @."""
        valide, msg = valider_email("userexample.com")
        assert valide is False
        assert "@" in msg

    def test_email_multiple_arobase(self):
        """Rejette un email avec plusieurs @."""
        valide, msg = valider_email("user@test@example.com")
        assert valide is False
        assert "trop" in msg.lower()

    def test_email_sans_domaine(self):
        """Rejette un email sans domaine valide."""
        valide, msg = valider_email("user@")
        assert valide is False

    def test_email_domaine_sans_point(self):
        """Rejette un domaine sans point."""
        valide, msg = valider_email("user@example")
        assert valide is False
        assert "domaine" in msg.lower()

    def test_email_partie_locale_vide(self):
        """Rejette une partie locale vide."""
        valide, msg = valider_email("@example.com")
        assert valide is False

    def test_email_trop_long(self):
        """Rejette un email trop long."""
        long_email = "a" * 250 + "@example.com"
        valide, msg = valider_email(long_email)
        assert valide is False
        assert "254" in msg or "long" in msg.lower()


# ═══════════════════════════════════════════════════════════
# Tests Configuration Par Défaut
# ═══════════════════════════════════════════════════════════


class TestGenererConfigDefaut:
    """Tests pour generer_config_defaut."""

    def test_retourne_dict(self):
        """Retourne un dictionnaire."""
        config = generer_config_defaut()
        assert isinstance(config, dict)

    def test_cles_essentielles_presentes(self):
        """Les clés essentielles sont présentes."""
        config = generer_config_defaut()
        cles_requises = ["nom_famille", "devise", "langue", "theme"]
        for cle in cles_requises:
            assert cle in config

    def test_valeurs_defaut_valides(self):
        """Les valeurs par défaut sont valides."""
        config = generer_config_defaut()
        assert config["devise"] == "EUR"
        assert config["langue"] == "fr"
        assert config["theme"] == "light"


class TestFusionnerConfig:
    """Tests pour fusionner_config."""

    def test_fusion_simple(self):
        """Fusionne deux configurations."""
        config_base = {"a": 1, "b": 2}
        nouveaux = {"b": 3, "c": 4}

        resultat = fusionner_config(config_base, nouveaux)

        assert resultat["a"] == 1  # Conservé
        assert resultat["b"] == 3  # Écrasé
        assert resultat["c"] == 4  # Ajouté

    def test_ne_modifie_pas_original(self):
        """Ne modifie pas la config originale."""
        config_base = {"a": 1}
        nouveaux = {"b": 2}

        fusionner_config(config_base, nouveaux)

        assert "b" not in config_base

    def test_fusion_vide(self):
        """Fusionne avec dict vide."""
        config_base = {"a": 1}
        resultat = fusionner_config(config_base, {})
        assert resultat == {"a": 1}


# ═══════════════════════════════════════════════════════════
# Tests Comparaison Versions
# ═══════════════════════════════════════════════════════════


class TestComparerVersions:
    """Tests pour comparer_versions."""

    def test_versions_egales(self):
        """Versions égales retournent 0."""
        assert comparer_versions("1.0.0", "1.0.0") == 0
        assert comparer_versions("2.5.3", "2.5.3") == 0

    def test_version_inferieure(self):
        """Version inférieure retourne -1."""
        assert comparer_versions("1.0.0", "2.0.0") == -1
        assert comparer_versions("1.0.0", "1.1.0") == -1
        assert comparer_versions("1.0.0", "1.0.1") == -1

    def test_version_superieure(self):
        """Version supérieure retourne 1."""
        assert comparer_versions("2.0.0", "1.0.0") == 1
        assert comparer_versions("1.1.0", "1.0.0") == 1
        assert comparer_versions("1.0.1", "1.0.0") == 1

    def test_longueurs_differentes(self):
        """Gère les versions de longueurs différentes."""
        assert comparer_versions("1.0", "1.0.1") == -1
        assert comparer_versions("1.0.1", "1.0") == 1

    def test_version_invalide(self):
        """Gère les versions invalides."""
        result = comparer_versions("invalid", "1.0.0")
        assert result == 0  # Retourne 0 en cas d'erreur


class TestVersionEstSuperieure:
    """Tests pour version_est_superieure."""

    def test_superieure(self):
        """Détecte version supérieure."""
        assert version_est_superieure("2.0.0", "1.0.0") is True
        assert version_est_superieure("1.1.0", "1.0.0") is True

    def test_egale(self):
        """Version égale est >= minimale."""
        assert version_est_superieure("1.0.0", "1.0.0") is True

    def test_inferieure(self):
        """Détecte version inférieure."""
        assert version_est_superieure("1.0.0", "2.0.0") is False


class TestFormaterVersion:
    """Tests pour formater_version."""

    def test_ajoute_v(self):
        """Ajoute le préfixe v."""
        assert formater_version("1.0.0") == "v1.0.0"

    def test_preserve_v_existant(self):
        """Préserve le v déjà présent."""
        assert formater_version("v1.0.0") == "v1.0.0"


# ═══════════════════════════════════════════════════════════
# Tests Préférences Par Catégorie
# ═══════════════════════════════════════════════════════════


class TestGetPreferencesParCategorie:
    """Tests pour get_preferences_par_categorie."""

    def test_groupement_general(self):
        """Groupe les préférences générales."""
        prefs = {"nom_famille": "Dupont", "langue": "fr", "fuseau_horaire": "Europe/Paris"}
        groupees = get_preferences_par_categorie(prefs)

        assert "general" in groupees
        assert groupees["general"]["nom_famille"] == "Dupont"
        assert groupees["general"]["langue"] == "fr"

    def test_groupement_affichage(self):
        """Groupe les préférences d'affichage."""
        prefs = {"theme": "dark", "format_date": "DD/MM/YYYY", "mode_compact": True}
        groupees = get_preferences_par_categorie(prefs)

        assert "affichage" in groupees
        assert groupees["affichage"]["theme"] == "dark"

    def test_categories_vides(self):
        """Gère les catégories vides."""
        groupees = get_preferences_par_categorie({})

        assert "general" in groupees
        assert len(groupees["general"]) == 0

    def test_cle_inconnue_ignoree(self):
        """Ignore les clés inconnues."""
        prefs = {"cle_inconnue": "valeur", "theme": "light"}
        groupees = get_preferences_par_categorie(prefs)

        # La clé inconnue n'apparaît dans aucune catégorie
        all_values = []
        for cat_values in groupees.values():
            all_values.extend(cat_values.keys())
        assert "cle_inconnue" not in all_values
