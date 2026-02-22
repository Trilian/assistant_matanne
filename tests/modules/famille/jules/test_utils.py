"""
Tests pour src/modules/famille/jules/utils.py

Tests complets pour les fonctions utilitaires du module jules.
"""

from datetime import date, timedelta
from unittest.mock import MagicMock, patch


class TestConstantes:
    """Tests pour les constantes du module"""

    def test_activites_par_age_contient_tranches(self):
        """Vérifie que ACTIVITES_PAR_AGE contient les tranches attendues"""
        from src.modules.famille.jules.utils import ACTIVITES_PAR_AGE

        assert (18, 24) in ACTIVITES_PAR_AGE
        assert (24, 36) in ACTIVITES_PAR_AGE

    def test_activites_par_age_structure(self):
        """Vérifie la structure des activités"""
        from src.modules.famille.jules.utils import ACTIVITES_PAR_AGE

        for tranche, activites in ACTIVITES_PAR_AGE.items():
            assert isinstance(activites, list)
            for activite in activites:
                assert "nom" in activite
                assert "emoji" in activite
                assert "duree" in activite
                assert "interieur" in activite
                assert "description" in activite

    def test_tailles_par_age_contient_tranches(self):
        """Vérifie que TAILLES_PAR_AGE contient les tranches attendues"""
        from src.modules.famille.jules.utils import TAILLES_PAR_AGE

        assert (12, 18) in TAILLES_PAR_AGE
        assert (18, 24) in TAILLES_PAR_AGE
        assert (24, 36) in TAILLES_PAR_AGE

    def test_tailles_par_age_structure(self):
        """Vérifie la structure des tailles"""
        from src.modules.famille.jules.utils import TAILLES_PAR_AGE

        for tranche, tailles in TAILLES_PAR_AGE.items():
            assert "vetements" in tailles
            assert "chaussures" in tailles

    def test_categories_conseils_contient_cles(self):
        """Vérifie que CATEGORIES_CONSEILS contient les clés attendues"""
        from src.modules.famille.jules.utils import CATEGORIES_CONSEILS

        cles_attendues = ["proprete", "sommeil", "alimentation", "langage", "motricite", "social"]
        for cle in cles_attendues:
            assert cle in CATEGORIES_CONSEILS

    def test_categories_conseils_structure(self):
        """Vérifie la structure des catégories de conseils"""
        from src.modules.famille.jules.utils import CATEGORIES_CONSEILS

        for cle, valeur in CATEGORIES_CONSEILS.items():
            assert "emoji" in valeur
            assert "titre" in valeur
            assert "description" in valeur


class TestGetAgeJules:
    """Tests pour la fonction get_age_jules"""

    def test_retourne_age_depuis_db(self):
        """Récupère l'âge de Jules depuis la base de données"""
        with patch("src.modules.famille.age_utils._obtenir_date_naissance") as mock_naiss:
            mock_naiss.return_value = date(2024, 6, 22)

            from src.modules.famille.jules.utils import get_age_jules

            result = get_age_jules()

            assert "mois" in result
            assert "semaines" in result
            assert "jours" in result
            assert "date_naissance" in result
            assert result["date_naissance"] == date(2024, 6, 22)

    def test_retourne_valeur_par_defaut_si_jules_non_trouve(self):
        """Retourne une valeur par défaut si Jules n'est pas trouvé"""
        from src.core.constants import JULES_NAISSANCE

        with patch("src.modules.famille.age_utils._obtenir_date_naissance") as mock_naiss:
            mock_naiss.return_value = JULES_NAISSANCE

            from src.modules.famille.jules.utils import get_age_jules

            result = get_age_jules()

            assert result["date_naissance"] == date(2024, 6, 22)

    def test_retourne_valeur_par_defaut_sur_exception(self):
        """Retourne une valeur par défaut en cas d'erreur"""
        from src.core.constants import JULES_NAISSANCE

        with patch("src.modules.famille.age_utils._obtenir_date_naissance") as mock_naiss:
            mock_naiss.return_value = JULES_NAISSANCE

            from src.modules.famille.jules.utils import get_age_jules

            result = get_age_jules()

            assert "mois" in result
            assert result["date_naissance"] == date(2024, 6, 22)

    def test_calcul_age_correct(self):
        """Vérifie le calcul de l'âge est correct"""
        naissance = date.today() - timedelta(days=60)

        with patch("src.modules.famille.age_utils._obtenir_date_naissance") as mock_naiss:
            mock_naiss.return_value = naissance

            from src.modules.famille.jules.utils import get_age_jules

            result = get_age_jules()

            assert result["jours"] == 60
            assert result["semaines"] == 8
            assert result["mois"] == 2

    def test_retourne_defaut_si_date_naissance_none(self):
        """Retourne valeur par défaut si date_of_birth est None"""
        from src.core.constants import JULES_NAISSANCE

        with patch("src.modules.famille.age_utils._obtenir_date_naissance") as mock_naiss:
            mock_naiss.return_value = JULES_NAISSANCE

            from src.modules.famille.jules.utils import get_age_jules

            result = get_age_jules()

            assert result["date_naissance"] == date(2024, 6, 22)


class TestGetActivitesPourAge:
    """Tests pour la fonction get_activites_pour_age"""

    def test_retourne_activites_18_24_mois(self):
        """Retourne les activités pour 18-24 mois"""
        from src.modules.famille.jules.utils import get_activites_pour_age

        result = get_activites_pour_age(19)

        assert isinstance(result, list)
        assert len(result) > 0
        assert any(a["nom"] == "Pâte à modeler" for a in result)

    def test_retourne_activites_24_36_mois(self):
        """Retourne les activités pour 24-36 mois"""
        from src.modules.famille.jules.utils import get_activites_pour_age

        result = get_activites_pour_age(30)

        assert isinstance(result, list)
        assert len(result) > 0
        assert any(a["nom"] == "Puzzle simple" for a in result)

    def test_retourne_defaut_pour_age_hors_tranche(self):
        """Retourne les activités 18-24 par défaut pour un âge hors tranche"""
        from src.modules.famille.jules.utils import get_activites_pour_age

        result = get_activites_pour_age(50)

        # Devrait retourner les activités 18-24 par défaut
        assert isinstance(result, list)

    def test_retourne_activites_limite_basse_18_mois(self):
        """Retourne les activités pour exactement 18 mois"""
        from src.modules.famille.jules.utils import get_activites_pour_age

        result = get_activites_pour_age(18)

        assert isinstance(result, list)
        assert len(result) > 0

    def test_retourne_activites_limite_haute_24_mois(self):
        """Retourne les activités pour exactement 24 mois"""
        from src.modules.famille.jules.utils import get_activites_pour_age

        result = get_activites_pour_age(24)

        # 24 est dans la tranche 24-36
        assert isinstance(result, list)


class TestGetTailleVetements:
    """Tests pour la fonction get_taille_vetements"""

    def test_retourne_taille_12_18_mois(self):
        """Retourne la taille pour 12-18 mois"""
        from src.modules.famille.jules.utils import get_taille_vetements

        result = get_taille_vetements(15)

        assert result["vetements"] == "80-86"
        assert result["chaussures"] == "20-21"

    def test_retourne_taille_18_24_mois(self):
        """Retourne la taille pour 18-24 mois"""
        from src.modules.famille.jules.utils import get_taille_vetements

        result = get_taille_vetements(20)

        assert result["vetements"] == "86-92"
        assert result["chaussures"] == "22-23"

    def test_retourne_taille_24_36_mois(self):
        """Retourne la taille pour 24-36 mois"""
        from src.modules.famille.jules.utils import get_taille_vetements

        result = get_taille_vetements(30)

        assert result["vetements"] == "92-98"
        assert result["chaussures"] == "24-25"

    def test_retourne_defaut_pour_age_hors_tranche(self):
        """Retourne la taille par défaut pour un âge hors tranche"""
        from src.modules.famille.jules.utils import get_taille_vetements

        result = get_taille_vetements(50)

        # Valeur par défaut
        assert result["vetements"] == "86-92"
        assert result["chaussures"] == "22-23"

    def test_retourne_taille_age_limite_bas(self):
        """Retourne la taille pour la limite basse d'une tranche"""
        from src.modules.famille.jules.utils import get_taille_vetements

        result = get_taille_vetements(12)

        assert result["vetements"] == "80-86"

    def test_retourne_defaut_pour_age_inferieur_12(self):
        """Retourne valeur par défaut pour âge < 12"""
        from src.modules.famille.jules.utils import get_taille_vetements

        result = get_taille_vetements(10)

        # Devrait retourner la valeur par défaut
        assert "vetements" in result
        assert "chaussures" in result


class TestGetAchatsJulesEnAttente:
    """Tests pour la fonction get_achats_jules_en_attente"""

    def test_retourne_achats_jules_en_attente(self):
        """Récupère les achats Jules en attente"""
        mock_purchase = MagicMock()
        mock_purchase.achete = False
        mock_purchase.categorie = "jules_vetements"

        with patch(
            "src.modules.famille.jules.utils.obtenir_service_achats_famille"
        ) as mock_factory:
            mock_service = MagicMock()
            mock_factory.return_value = mock_service
            mock_service.lister_par_groupe.return_value = [mock_purchase]

            from src.modules.famille.jules.utils import get_achats_jules_en_attente

            result = get_achats_jules_en_attente()

            assert len(result) == 1

    def test_retourne_liste_vide_sur_exception(self):
        """Retourne une liste vide en cas d'erreur"""
        with patch(
            "src.modules.famille.jules.utils.obtenir_service_achats_famille"
        ) as mock_factory:
            mock_factory.return_value.lister_par_groupe.side_effect = Exception("DB error")

            from src.modules.famille.jules.utils import get_achats_jules_en_attente

            result = get_achats_jules_en_attente()

            assert result == []

    def test_retourne_liste_vide_si_aucun_achat(self):
        """Retourne une liste vide si aucun achat"""
        with patch(
            "src.modules.famille.jules.utils.obtenir_service_achats_famille"
        ) as mock_factory:
            mock_service = MagicMock()
            mock_factory.return_value = mock_service
            mock_service.lister_par_groupe.return_value = []

            from src.modules.famille.jules.utils import get_achats_jules_en_attente

            result = get_achats_jules_en_attente()

            assert result == []
