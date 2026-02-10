"""
Tests de couverture pour parametres_logic.py
Objectif: Atteindre ≥80% de couverture
"""

import pytest
import json
from typing import Dict, Any, List

from src.domains.utils.logic.parametres_logic import (
    valider_parametres,
    valider_email,
    generer_config_defaut,
    fusionner_config,
    comparer_versions,
    version_est_superieure,
    formater_version,
    get_preferences_par_categorie,
    exporter_config,
    verifier_sante_config,
    formater_parametre_affichage,
)


# ═══════════════════════════════════════════════════════════
# TESTS VALIDER PARAMETRES
# ═══════════════════════════════════════════════════════════


class TestValiderParametres:
    """Tests pour valider_parametres."""
    
    def test_parametres_valides(self):
        """Paramètres valides passent."""
        data = {
            "nom_famille": "Dupont",
            "email": "test@example.com",
            "devise": "EUR",
            "langue": "fr",
            "theme": "light"
        }
        valide, erreurs = valider_parametres(data)
        assert valide is True
        assert len(erreurs) == 0
        
    def test_nom_trop_court(self):
        """Nom trop court génère erreur."""
        data = {"nom_famille": "A"}
        valide, erreurs = valider_parametres(data)
        assert valide is False
        assert any("2 caractères" in e for e in erreurs)
        
    def test_nom_trop_long(self):
        """Nom trop long génère erreur."""
        data = {"nom_famille": "A" * 51}
        valide, erreurs = valider_parametres(data)
        assert valide is False
        assert any("50 caractères" in e for e in erreurs)
        
    def test_nom_vide(self):
        """Nom vide génère erreur."""
        data = {"nom_famille": ""}
        valide, erreurs = valider_parametres(data)
        assert valide is False
        
    def test_email_sans_arobase(self):
        """Email sans @ génère erreur."""
        data = {"email": "testexample.com"}
        valide, erreurs = valider_parametres(data)
        assert valide is False
        assert any("@" in e for e in erreurs)
        
    def test_email_domaine_invalide(self):
        """Email avec domaine invalide génère erreur."""
        data = {"email": "test@invalid"}
        valide, erreurs = valider_parametres(data)
        assert valide is False
        assert any("domaine" in e for e in erreurs)
        
    def test_email_vide_ok(self):
        """Email vide est accepté (optionnel)."""
        data = {"email": ""}
        valide, erreurs = valider_parametres(data)
        assert valide is True
        
    def test_devise_invalide(self):
        """Devise non supportée génère erreur."""
        data = {"devise": "XYZ"}
        valide, erreurs = valider_parametres(data)
        assert valide is False
        assert any("Devise" in e for e in erreurs)
        
    def test_devises_valides(self):
        """Toutes les devises supportées passent."""
        for devise in ["EUR", "USD", "GBP", "CHF", "CAD"]:
            data = {"devise": devise}
            valide, erreurs = valider_parametres(data)
            assert valide is True, f"Devise {devise} devrait être valide"
            
    def test_langue_invalide(self):
        """Langue non supportée génère erreur."""
        data = {"langue": "xx"}
        valide, erreurs = valider_parametres(data)
        assert valide is False
        assert any("Langue" in e for e in erreurs)
        
    def test_langues_valides(self):
        """Toutes les langues supportées passent."""
        for langue in ["fr", "en", "es", "de"]:
            data = {"langue": langue}
            valide, erreurs = valider_parametres(data)
            assert valide is True
            
    def test_theme_invalide(self):
        """Thème non supporté génère erreur."""
        data = {"theme": "neon"}
        valide, erreurs = valider_parametres(data)
        assert valide is False
        assert any("Thème" in e for e in erreurs)
        
    def test_themes_valides(self):
        """Tous les thèmes supportés passent."""
        for theme in ["light", "dark", "auto"]:
            data = {"theme": theme}
            valide, erreurs = valider_parametres(data)
            assert valide is True
            
    def test_multiples_erreurs(self):
        """Plusieurs erreurs accumulées."""
        data = {
            "nom_famille": "A",
            "email": "invalid",
            "devise": "XYZ",
            "langue": "xx"
        }
        valide, erreurs = valider_parametres(data)
        assert valide is False
        assert len(erreurs) >= 3


# ═══════════════════════════════════════════════════════════
# TESTS VALIDER EMAIL
# ═══════════════════════════════════════════════════════════


class TestValiderEmail:
    """Tests pour valider_email."""
    
    def test_email_vide(self):
        """Email vide retourne erreur."""
        valide, erreur = valider_email("")
        assert valide is False
        assert "vide" in erreur.lower()
        
    def test_email_sans_arobase(self):
        """Email sans @ retourne erreur."""
        valide, erreur = valider_email("testexample.com")
        assert valide is False
        assert "@" in erreur
        
    def test_email_trop_de_arobase(self):
        """Email avec plusieurs @ retourne erreur."""
        valide, erreur = valider_email("test@exam@ple.com")
        assert valide is False
        assert "trop de @" in erreur.lower()
        
    def test_email_partie_locale_vide(self):
        """Email avec partie locale vide."""
        valide, erreur = valider_email("@example.com")
        assert valide is False
        assert "locale" in erreur.lower()
        
    def test_email_domaine_sans_point(self):
        """Email avec domaine sans point."""
        valide, erreur = valider_email("test@localhost")
        assert valide is False
        assert "domaine" in erreur.lower()
        
    def test_email_trop_long(self):
        """Email trop long."""
        long_email = "a" * 250 + "@example.com"
        valide, erreur = valider_email(long_email)
        assert valide is False
        assert "254" in erreur
        
    def test_email_valide(self):
        """Email valide passe."""
        valide, erreur = valider_email("test@example.com")
        assert valide is True
        assert erreur is None
        
    def test_email_complexe_valide(self):
        """Email complexe mais valide."""
        valide, erreur = valider_email("user.name+tag@sub.domain.com")
        assert valide is True


# ═══════════════════════════════════════════════════════════
# TESTS GENERER CONFIG DEFAUT
# ═══════════════════════════════════════════════════════════


class TestGenererConfigDefaut:
    """Tests pour generer_config_defaut."""
    
    def test_contient_cles_essentielles(self):
        """Config contient les clés essentielles."""
        config = generer_config_defaut()
        
        assert "nom_famille" in config
        assert "devise" in config
        assert "langue" in config
        assert "theme" in config
        
    def test_valeurs_defaut_fr(self):
        """Valeurs françaises par défaut."""
        config = generer_config_defaut()
        
        assert config["devise"] == "EUR"
        assert config["langue"] == "fr"
        assert config["fuseau_horaire"] == "Europe/Paris"
        
    def test_notifications_par_defaut(self):
        """Notifications activées par défaut."""
        config = generer_config_defaut()
        
        assert config["notifications_actives"] is True
        assert config["notifications_email"] is False


# ═══════════════════════════════════════════════════════════
# TESTS FUSIONNER CONFIG
# ═══════════════════════════════════════════════════════════


class TestFusionnerConfig:
    """Tests pour fusionner_config."""
    
    def test_fusion_simple(self):
        """Fusionne deux configs simples."""
        actuelle = {"a": 1, "b": 2}
        nouvelle = {"b": 3, "c": 4}
        
        result = fusionner_config(actuelle, nouvelle)
        
        assert result["a"] == 1  # Gardé
        assert result["b"] == 3  # Écrasé
        assert result["c"] == 4  # Ajouté
        
    def test_ne_modifie_pas_origine(self):
        """Ne modifie pas la config originale."""
        actuelle = {"a": 1}
        nouvelle = {"b": 2}
        
        result = fusionner_config(actuelle, nouvelle)
        
        assert "b" not in actuelle
        assert "b" in result


# ═══════════════════════════════════════════════════════════
# TESTS COMPARER VERSIONS
# ═══════════════════════════════════════════════════════════


class TestComparerVersions:
    """Tests pour comparer_versions."""
    
    def test_versions_egales(self):
        """Versions égales retourne 0."""
        assert comparer_versions("1.0.0", "1.0.0") == 0
        assert comparer_versions("2.1.5", "2.1.5") == 0
        
    def test_version_inferieure(self):
        """Version inférieure retourne -1."""
        assert comparer_versions("1.0.0", "1.0.1") == -1
        assert comparer_versions("1.0.0", "1.1.0") == -1
        assert comparer_versions("1.0.0", "2.0.0") == -1
        
    def test_version_superieure(self):
        """Version supérieure retourne 1."""
        assert comparer_versions("1.0.1", "1.0.0") == 1
        assert comparer_versions("1.1.0", "1.0.0") == 1
        assert comparer_versions("2.0.0", "1.0.0") == 1
        
    def test_longueurs_differentes(self):
        """Versions de longueurs différentes."""
        assert comparer_versions("1.0", "1.0.0") == -1
        assert comparer_versions("1.0.0.1", "1.0.0") == 1
        
    def test_versions_invalides(self):
        """Versions invalides retournent 0."""
        assert comparer_versions("invalid", "1.0.0") == 0
        assert comparer_versions("1.0.0", None) == 0


# ═══════════════════════════════════════════════════════════
# TESTS VERSION EST SUPERIEURE
# ═══════════════════════════════════════════════════════════


class TestVersionEstSuperieure:
    """Tests pour version_est_superieure."""
    
    def test_version_egale(self):
        """Version égale est considérée supérieure."""
        assert version_est_superieure("1.0.0", "1.0.0") is True
        
    def test_version_superieure(self):
        """Version supérieure retourne True."""
        assert version_est_superieure("2.0.0", "1.0.0") is True
        
    def test_version_inferieure(self):
        """Version inférieure retourne False."""
        assert version_est_superieure("1.0.0", "2.0.0") is False


# ═══════════════════════════════════════════════════════════
# TESTS FORMATER VERSION
# ═══════════════════════════════════════════════════════════


class TestFormaterVersion:
    """Tests pour formater_version."""
    
    def test_ajoute_v(self):
        """Ajoute 'v' si absent."""
        assert formater_version("1.0.0") == "v1.0.0"
        
    def test_garde_v_existant(self):
        """Garde 'v' si déjà présent."""
        assert formater_version("v1.0.0") == "v1.0.0"


# ═══════════════════════════════════════════════════════════
# TESTS GET PREFERENCES PAR CATEGORIE
# ═══════════════════════════════════════════════════════════


class TestGetPreferencesParCategorie:
    """Tests pour get_preferences_par_categorie."""
    
    def test_groupement_general(self):
        """Groupe les préférences générales."""
        prefs = {
            "nom_famille": "Dupont",
            "langue": "fr",
            "fuseau_horaire": "Europe/Paris"
        }
        
        result = get_preferences_par_categorie(prefs)
        
        assert "general" in result
        assert result["general"]["nom_famille"] == "Dupont"
        assert result["general"]["langue"] == "fr"
        
    def test_groupement_affichage(self):
        """Groupe les préférences d'affichage."""
        prefs = {
            "theme": "dark",
            "format_date": "DD/MM/YYYY",
            "mode_compact": True
        }
        
        result = get_preferences_par_categorie(prefs)
        
        assert "affichage" in result
        assert result["affichage"]["theme"] == "dark"
        
    def test_groupement_notifications(self):
        """Groupe les préférences notifications."""
        prefs = {
            "notifications_actives": True,
            "notifications_email": False
        }
        
        result = get_preferences_par_categorie(prefs)
        
        assert "notifications" in result
        assert result["notifications"]["notifications_actives"] is True
        
    def test_groupement_integration(self):
        """Groupe les préférences intégration."""
        prefs = {
            "sync_calendrier": True,
            "api_externe": "https://api.example.com"
        }
        
        result = get_preferences_par_categorie(prefs)
        
        assert "integration" in result
        assert result["integration"]["sync_calendrier"] is True
        
    def test_preference_absente(self):
        """Préférence absente n'est pas incluse."""
        prefs = {"nom_famille": "Test"}
        
        result = get_preferences_par_categorie(prefs)
        
        assert "langue" not in result["general"]


# ═══════════════════════════════════════════════════════════
# TESTS EXPORTER CONFIG
# ═══════════════════════════════════════════════════════════


class TestExporterConfig:
    """Tests pour exporter_config."""
    
    def test_export_json(self):
        """Export en JSON."""
        config = {"nom": "Test", "actif": True}
        
        result = exporter_config(config, "json")
        
        assert '"nom"' in result
        assert "Test" in result
        parsed = json.loads(result)
        assert parsed["nom"] == "Test"
        
    def test_export_yaml(self):
        """Export en YAML simulé."""
        config = {"nom": "Test", "actif": True}
        
        result = exporter_config(config, "yaml")
        
        assert "nom:" in result
        assert "actif:" in result
        assert "true" in result  # bool en lowercase
        
    def test_export_ini(self):
        """Export en INI simulé."""
        config = {"nom": "Test", "valeur": 42}
        
        result = exporter_config(config, "ini")
        
        assert "[config]" in result
        assert "nom = Test" in result
        
    def test_export_format_inconnu(self):
        """Format inconnu retourne str."""
        config = {"nom": "Test"}
        
        result = exporter_config(config, "unknown")
        
        assert "nom" in result


# ═══════════════════════════════════════════════════════════
# TESTS VERIFIER SANTE CONFIG
# ═══════════════════════════════════════════════════════════


class TestVerifierSanteConfig:
    """Tests pour verifier_sante_config."""
    
    def test_config_saine(self):
        """Config saine retourne OK."""
        config = {
            "nom_famille": "Dupont",
            "devise": "EUR",
            "langue": "fr"
        }
        
        result = verifier_sante_config(config)
        
        assert result["statut"] == "OK"
        assert len(result["problemes"]) == 0
        assert result["score"] == 100
        
    def test_parametre_manquant(self):
        """Paramètre obligatoire manquant."""
        config = {"devise": "EUR", "langue": "fr"}
        # Manque nom_famille
        
        result = verifier_sante_config(config)
        
        assert result["statut"] == "Erreur"
        assert len(result["problemes"]) >= 1
        assert result["score"] < 100
        
    def test_notifications_sans_email(self):
        """Notifications email sans email configuré."""
        config = {
            "nom_famille": "Test",
            "devise": "EUR",
            "langue": "fr",
            "notifications_email": True,
            "email": ""
        }
        
        result = verifier_sante_config(config)
        
        assert result["statut"] == "Avertissement"
        assert len(result["avertissements"]) >= 1
        
    def test_sync_sans_api(self):
        """Sync calendrier sans API configurée."""
        config = {
            "nom_famille": "Test",
            "devise": "EUR",
            "langue": "fr",
            "sync_calendrier": True,
            "api_externe": None
        }
        
        result = verifier_sante_config(config)
        
        assert len(result["avertissements"]) >= 1


# ═══════════════════════════════════════════════════════════
# TESTS FORMATER PARAMETRE AFFICHAGE
# ═══════════════════════════════════════════════════════════


class TestFormaterParametreAffichage:
    """Tests pour formater_parametre_affichage."""
    
    def test_boolean_true(self):
        """Boolean True affiché avec ✅."""
        result = formater_parametre_affichage("actif", True)
        assert "✅" in result
        assert "Activé" in result
        
    def test_boolean_false(self):
        """Boolean False affiché avec ❌."""
        result = formater_parametre_affichage("actif", False)
        assert "❌" in result
        assert "Désactivé" in result
        
    def test_devise_eur(self):
        """Devise EUR affichée avec symbole."""
        result = formater_parametre_affichage("devise", "EUR")
        assert "EUR" in result
        assert "€" in result
        
    def test_devise_usd(self):
        """Devise USD affichée avec symbole."""
        result = formater_parametre_affichage("devise", "USD")
        assert "$" in result
        
    def test_langue_fr(self):
        """Langue française affichée avec drapeau."""
        result = formater_parametre_affichage("langue", "fr")
        assert "Français" in result
        
    def test_valeur_standard(self):
        """Valeur standard retournée en string."""
        result = formater_parametre_affichage("autre", "valeur")
        assert result == "valeur"
        
    def test_valeur_numerique(self):
        """Valeur numérique convertie en string."""
        result = formater_parametre_affichage("nombre", 42)
        assert result == "42"
