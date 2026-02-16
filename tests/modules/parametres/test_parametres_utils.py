"""
Tests pour src/modules/outils/parametres_utils.py

Tests complets pour atteindre 80%+ de couverture.
"""

import json

from src.modules.parametres.utils import (
    comparer_versions,
    exporter_config,
    formater_parametre_affichage,
    formater_version,
    fusionner_config,
    generer_config_defaut,
    get_preferences_par_categorie,
    valider_email,
    valider_parametres,
    verifier_sante_config,
    version_est_superieure,
)


class TestValiderParametres:
    """Tests pour la validation des paramètres"""

    def test_parametres_valides(self):
        """Teste la validation avec des paramètres corrects"""
        data = {
            "nom_famille": "Dupont",
            "email": "test@example.com",
            "devise": "EUR",
            "langue": "fr",
            "theme": "light",
        }
        valide, erreurs = valider_parametres(data)
        assert valide is True
        assert erreurs == []

    def test_nom_famille_trop_court(self):
        """Teste le rejet d'un nom de famille trop court"""
        data = {"nom_famille": "A"}
        valide, erreurs = valider_parametres(data)
        assert valide is False
        assert any("2 caractères" in e for e in erreurs)

    def test_nom_famille_vide(self):
        """Teste le rejet d'un nom de famille vide"""
        data = {"nom_famille": ""}
        valide, erreurs = valider_parametres(data)
        assert valide is False
        assert len(erreurs) == 1

    def test_nom_famille_trop_long(self):
        """Teste le rejet d'un nom de famille trop long"""
        data = {"nom_famille": "A" * 51}
        valide, erreurs = valider_parametres(data)
        assert valide is False
        assert any("50 caractères" in e for e in erreurs)

    def test_email_invalide_sans_arobase(self):
        """Teste le rejet d'un email sans @"""
        data = {"email": "test.example.com"}
        valide, erreurs = valider_parametres(data)
        assert valide is False
        assert any("@" in e for e in erreurs)

    def test_email_invalide_domaine_incorrect(self):
        """Teste le rejet d'un email avec domaine sans point"""
        data = {"email": "test@localhost"}
        valide, erreurs = valider_parametres(data)
        assert valide is False
        assert any("domaine" in e for e in erreurs)

    def test_devise_non_supportee(self):
        """Teste le rejet d'une devise non supportée"""
        data = {"devise": "JPY"}
        valide, erreurs = valider_parametres(data)
        assert valide is False
        assert any("Devise" in e for e in erreurs)

    def test_devises_valides(self):
        """Teste les devises supportées"""
        for devise in ["EUR", "USD", "GBP", "CHF", "CAD"]:
            data = {"devise": devise}
            valide, erreurs = valider_parametres(data)
            assert valide is True

    def test_langue_non_supportee(self):
        """Teste le rejet d'une langue non supportée"""
        data = {"langue": "it"}
        valide, erreurs = valider_parametres(data)
        assert valide is False
        assert any("Langue" in e for e in erreurs)

    def test_langues_valides(self):
        """Teste les langues supportées"""
        for langue in ["fr", "en", "es", "de"]:
            data = {"langue": langue}
            valide, erreurs = valider_parametres(data)
            assert valide is True

    def test_theme_non_supporte(self):
        """Teste le rejet d'un thème non supporté"""
        data = {"theme": "blue"}
        valide, erreurs = valider_parametres(data)
        assert valide is False
        assert any("Thème" in e for e in erreurs)

    def test_themes_valides(self):
        """Teste les thèmes supportés"""
        for theme in ["light", "dark", "auto"]:
            data = {"theme": theme}
            valide, erreurs = valider_parametres(data)
            assert valide is True

    def test_parametres_vides(self):
        """Teste avec un dictionnaire vide"""
        valide, erreurs = valider_parametres({})
        assert valide is True
        assert erreurs == []

    def test_plusieurs_erreurs(self):
        """Teste la détection de plusieurs erreurs"""
        data = {
            "nom_famille": "A",
            "email": "invalide",
            "devise": "XXX",
        }
        valide, erreurs = valider_parametres(data)
        assert valide is False
        assert len(erreurs) >= 2


class TestValiderEmail:
    """Tests pour la validation des emails"""

    def test_email_valide(self):
        """Teste un email valide"""
        valide, erreur = valider_email("test@example.com")
        assert valide is True
        assert erreur is None

    def test_email_vide(self):
        """Teste un email vide"""
        valide, erreur = valider_email("")
        assert valide is False
        assert erreur == "Email vide"

    def test_email_sans_arobase(self):
        """Teste un email sans @"""
        valide, erreur = valider_email("test.example.com")
        assert valide is False
        assert "@" in erreur

    def test_email_plusieurs_arobases(self):
        """Teste un email avec plusieurs @"""
        valide, erreur = valider_email("test@@example.com")
        assert valide is False
        assert "trop de @" in erreur

    def test_email_partie_locale_vide(self):
        """Teste un email avec partie locale vide"""
        valide, erreur = valider_email("@example.com")
        assert valide is False
        assert "locale" in erreur

    def test_email_domaine_sans_point(self):
        """Teste un email avec domaine sans point"""
        valide, erreur = valider_email("test@localhost")
        assert valide is False
        assert "Domaine" in erreur

    def test_email_trop_long(self):
        """Teste un email trop long (max 254 caractères)"""
        long_email = "a" * 240 + "@example.com"  # 252 caractères = ok
        assert len(long_email) < 254
        valide, _ = valider_email(long_email)
        assert valide is True  # Pas encore trop long

        very_long_email = "a" * 250 + "@example.com"  # 262 caractères = trop long
        valide, erreur = valider_email(very_long_email)
        assert valide is False
        assert "254" in erreur


class TestGenererConfigDefaut:
    """Tests pour la génération de configuration par défaut"""

    def test_config_defaut_complete(self):
        """Teste que la config par défaut contient tous les champs"""
        config = generer_config_defaut()
        assert "nom_famille" in config
        assert "email" in config
        assert "devise" in config
        assert "langue" in config
        assert "theme" in config
        assert "notifications_actives" in config

    def test_valeurs_defaut(self):
        """Teste les valeurs par défaut"""
        config = generer_config_defaut()
        assert config["devise"] == "EUR"
        assert config["langue"] == "fr"
        assert config["theme"] == "light"
        assert config["notifications_actives"] is True


class TestFusionnerConfig:
    """Tests pour la fusion de configurations"""

    def test_fusion_basique(self):
        """Teste la fusion basique"""
        actuelle = {"a": 1, "b": 2}
        nouveaux = {"b": 3, "c": 4}
        resultat = fusionner_config(actuelle, nouveaux)
        assert resultat == {"a": 1, "b": 3, "c": 4}

    def test_fusion_ne_modifie_pas_original(self):
        """Teste que l'original n'est pas modifié"""
        actuelle = {"a": 1}
        nouveaux = {"b": 2}
        fusionner_config(actuelle, nouveaux)
        assert actuelle == {"a": 1}

    def test_fusion_vide(self):
        """Teste la fusion avec dictionnaire vide"""
        actuelle = {"a": 1}
        resultat = fusionner_config(actuelle, {})
        assert resultat == {"a": 1}


class TestComparerVersions:
    """Tests pour la comparaison de versions"""

    def test_version_inferieure(self):
        """Teste version actuelle < version cible"""
        assert comparer_versions("1.0.0", "1.0.1") == -1
        assert comparer_versions("1.0.0", "1.1.0") == -1
        assert comparer_versions("1.0.0", "2.0.0") == -1

    def test_version_egale(self):
        """Teste versions égales"""
        assert comparer_versions("1.0.0", "1.0.0") == 0
        assert comparer_versions("2.3.4", "2.3.4") == 0

    def test_version_superieure(self):
        """Teste version actuelle > version cible"""
        assert comparer_versions("1.0.1", "1.0.0") == 1
        assert comparer_versions("2.0.0", "1.9.9") == 1

    def test_longueurs_differentes(self):
        """Teste les versions avec longueurs différentes"""
        assert comparer_versions("1.0", "1.0.0") == -1
        assert comparer_versions("1.0.0.0", "1.0.0") == 1

    def test_version_invalide(self):
        """Teste avec version invalide"""
        assert comparer_versions("invalid", "1.0.0") == 0
        assert comparer_versions("1.0.0", "invalid") == 0


class TestVersionEstSuperieure:
    """Tests pour version_est_superieure"""

    def test_version_superieure(self):
        """Teste que la version actuelle est >= minimale"""
        assert version_est_superieure("2.0.0", "1.0.0") is True
        assert version_est_superieure("1.0.0", "1.0.0") is True

    def test_version_inferieure(self):
        """Teste que la version actuelle est < minimale"""
        assert version_est_superieure("1.0.0", "2.0.0") is False


class TestFormaterVersion:
    """Tests pour le formatage de version"""

    def test_ajoute_prefixe_v(self):
        """Teste l'ajout du préfixe v"""
        assert formater_version("1.0.0") == "v1.0.0"

    def test_conserve_prefixe_v(self):
        """Teste que le préfixe v existant est conservé"""
        assert formater_version("v1.0.0") == "v1.0.0"


class TestGetPreferencesParCategorie:
    """Tests pour le groupement des préférences"""

    def test_groupement_complet(self):
        """Teste le groupement avec toutes les préférences"""
        prefs = {
            "nom_famille": "Dupont",
            "langue": "fr",
            "fuseau_horaire": "Europe/Paris",
            "theme": "dark",
            "format_date": "DD/MM/YYYY",
            "mode_compact": True,
            "notifications_actives": True,
            "notifications_email": False,
            "sync_calendrier": True,
            "api_externe": "http://api.example.com",
            "email": "test@example.com",
            "partage_donnees": False,
        }
        groupees = get_preferences_par_categorie(prefs)

        assert "general" in groupees
        assert "affichage" in groupees
        assert "notifications" in groupees
        assert "integration" in groupees
        assert "confidentialite" in groupees

        assert groupees["general"]["nom_famille"] == "Dupont"
        assert groupees["affichage"]["theme"] == "dark"
        assert groupees["notifications"]["notifications_actives"] is True

    def test_preferences_partielles(self):
        """Teste avec préférences partielles"""
        prefs = {"nom_famille": "Test"}
        groupees = get_preferences_par_categorie(prefs)
        assert groupees["general"]["nom_famille"] == "Test"
        assert "langue" not in groupees["general"]


class TestExporterConfig:
    """Tests pour l'export de configuration"""

    def test_export_json(self):
        """Teste l'export JSON"""
        config = {"nom": "Test", "valeur": 42}
        resultat = exporter_config(config, "json")
        parsed = json.loads(resultat)
        assert parsed["nom"] == "Test"
        assert parsed["valeur"] == 42

    def test_export_yaml(self):
        """Teste l'export YAML"""
        config = {"nom": "Test", "actif": True}
        resultat = exporter_config(config, "yaml")
        assert 'nom: "Test"' in resultat
        assert "actif: true" in resultat

    def test_export_ini(self):
        """Teste l'export INI"""
        config = {"nom": "Test", "valeur": 42}
        resultat = exporter_config(config, "ini")
        assert "[config]" in resultat
        assert "nom = Test" in resultat

    def test_export_format_inconnu(self):
        """Teste l'export avec format inconnu"""
        config = {"test": 123}
        resultat = exporter_config(config, "unknown")
        assert "test" in resultat


class TestVerifierSanteConfig:
    """Tests pour la vérification de santé de la config"""

    def test_config_saine(self):
        """Teste une configuration saine"""
        config = {
            "nom_famille": "Test",
            "devise": "EUR",
            "langue": "fr",
        }
        resultat = verifier_sante_config(config)
        assert resultat["statut"] == "OK"
        assert resultat["score"] == 100
        assert len(resultat["problemes"]) == 0

    def test_config_avec_parametre_manquant(self):
        """Teste avec paramètre obligatoire manquant"""
        config = {"devise": "EUR", "langue": "fr"}
        resultat = verifier_sante_config(config)
        assert resultat["statut"] == "Erreur"
        assert len(resultat["problemes"]) > 0
        assert resultat["score"] < 100

    def test_avertissement_notifications_sans_email(self):
        """Teste l'avertissement notifications sans email"""
        config = {
            "nom_famille": "Test",
            "devise": "EUR",
            "langue": "fr",
            "notifications_email": True,
            "email": "",
        }
        resultat = verifier_sante_config(config)
        assert resultat["statut"] == "Avertissement"
        assert len(resultat["avertissements"]) > 0

    def test_avertissement_sync_sans_api(self):
        """Teste l'avertissement sync calendrier sans API"""
        config = {
            "nom_famille": "Test",
            "devise": "EUR",
            "langue": "fr",
            "sync_calendrier": True,
        }
        resultat = verifier_sante_config(config)
        assert "avertissements" in resultat


class TestFormaterParametreAffichage:
    """Tests pour le formatage d'affichage des paramètres"""

    def test_format_booleen_actif(self):
        """Teste le formatage d'un booléen True"""
        resultat = formater_parametre_affichage("test", True)
        assert "Active" in resultat

    def test_format_booleen_inactif(self):
        """Teste le formatage d'un booléen False"""
        resultat = formater_parametre_affichage("test", False)
        assert "Desactive" in resultat

    def test_format_devise(self):
        """Teste le formatage des devises"""
        assert "€" in formater_parametre_affichage("devise", "EUR")
        assert "$" in formater_parametre_affichage("devise", "USD")
        assert "£" in formater_parametre_affichage("devise", "GBP")

    def test_format_langue(self):
        """Teste le formatage des langues"""
        resultat = formater_parametre_affichage("langue", "fr")
        assert "Français" in resultat

    def test_format_valeur_normale(self):
        """Teste le formatage d'une valeur normale"""
        resultat = formater_parametre_affichage("autre", "valeur")
        assert resultat == "valeur"
