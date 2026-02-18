"""
Tests pour src/utils/formatters/numbers.py
Données réelles de cuisine et courses
"""

import pytest

from src.core.formatters import (
    arrondir_intelligent,
    formater_monnaie,
    formater_nombre,
    formater_plage,
    formater_pourcentage,
    formater_prix,
    formater_quantite,
    formater_quantite_unite,
    formater_taille_fichier,
)


@pytest.mark.unit
class TestFormaterQuantite:
    """Tests pour formater_quantite avec ingrédients réels."""

    # Entiers
    def test_quantite_4_oeufs(self):
        """4 oeufs."""
        assert formater_quantite(4) == "4"

    def test_quantite_2_pommes(self):
        """2 pommes."""
        assert formater_quantite(2.0) == "2"

    # Décimales utiles
    def test_quantite_demi_litre_lait(self):
        """0.5L lait."""
        assert formater_quantite(0.5) == "0.5"

    def test_quantite_1_5_kg_farine(self):
        """1.5kg farine."""
        assert formater_quantite(1.5) == "1.5"

    def test_quantite_250g_beurre(self):
        """250g beurre."""
        assert formater_quantite(250) == "250"

    # Avec décimales spécifiques
    def test_quantite_2_decimales(self):
        """Précision 2 décimales."""
        assert formater_quantite(2.125, decimals=2) == "2.12"

    def test_quantite_3_decimales(self):
        """Précision 3 décimales."""
        assert formater_quantite(3.1416, decimals=3) == "3.142"

    # Cas limites
    def test_quantite_0(self):
        """Quantité 0."""
        assert formater_quantite(0) == "0"

    def test_quantite_none(self):
        """Quantité None."""
        assert formater_quantite(None) == "0"

    def test_quantite_invalid(self):
        """Quantité invalide."""
        assert formater_quantite("abc") == "0"


@pytest.mark.unit
class TestFormaterQuantiteUnite:
    """Tests pour formater_quantite_unite."""

    def test_500g_sucre(self):
        """500g de sucre."""
        assert formater_quantite_unite(500, "g") == "500 g"

    def test_1_5kg_poulet(self):
        """1.5kg de poulet."""
        assert formater_quantite_unite(1.5, "kg") == "1.5 kg"

    def test_3_oeufs(self):
        """3 oeufs (pcs)."""
        assert formater_quantite_unite(3, "pcs") == "3 pcs"

    def test_250ml_lait(self):
        """250ml de lait."""
        assert formater_quantite_unite(250, "mL") == "250 mL"

    def test_sans_unite(self):
        """Pas d'unité."""
        assert formater_quantite_unite(5, "") == "5"

    def test_unite_avec_espaces(self):
        """Unité avec espaces."""
        assert formater_quantite_unite(2, "  kg  ") == "2 kg"


@pytest.mark.unit
class TestFormaterPrix:
    """Tests pour formater_prix avec prix courses réels."""

    def test_prix_1_baguette(self):
        """Baguette 1€."""
        assert formater_prix(1) == "1€"

    def test_prix_2_50_camembert(self):
        """Camembert 2.50€."""
        assert formater_prix(2.50) == "2.50€"

    def test_prix_4_99_poulet(self):
        """Poulet 4.99€."""
        assert formater_prix(4.99) == "4.99€"

    def test_prix_12_viande(self):
        """Viande hachée 12€."""
        assert formater_prix(12.0) == "12€"

    def test_prix_en_dollars(self):
        """Prix en dollars."""
        assert formater_prix(10, currency="$") == "10$"

    def test_prix_0(self):
        """Prix 0."""
        assert formater_prix(0) == "0€"

    def test_prix_none(self):
        """Prix None."""
        assert formater_prix(None) == "0€"

    def test_prix_invalid(self):
        """Prix invalide."""
        assert formater_prix("abc") == "0€"


@pytest.mark.unit
class TestFormaterMonnaie:
    """Tests pour formater_monnaie avec budget famille."""

    def test_monnaie_budget_courses(self):
        """Budget courses 150€."""
        result = formater_monnaie(150)
        assert "150" in result
        assert "€" in result

    def test_monnaie_budget_mensuel(self):
        """Budget mensuel 1234.56€."""
        result = formater_monnaie(1234.56, "EUR", "fr_FR")
        assert "1 234" in result
        assert "€" in result

    def test_monnaie_gros_budget(self):
        """Gros budget 12500€."""
        result = formater_monnaie(12500, "EUR", "fr_FR")
        assert "12 500" in result

    def test_monnaie_en_dollars(self):
        """Budget en dollars."""
        result = formater_monnaie(100, "USD", "en_US")
        assert "$" in result

    def test_monnaie_en_livres(self):
        """Budget en livres."""
        result = formater_monnaie(100, "GBP", "en_GB")
        assert "£" in result

    def test_monnaie_0(self):
        """0€."""
        result = formater_monnaie(0)
        assert "0" in result

    def test_monnaie_none(self):
        """None."""
        result = formater_monnaie(None)
        assert "0" in result


@pytest.mark.unit
class TestFormaterPourcentage:
    """Tests pour formater_pourcentage."""

    def test_pourcentage_stock_100(self):
        """Stock plein 100%."""
        assert formater_pourcentage(100) == "100%"

    def test_pourcentage_stock_50(self):
        """Stock moitié 50%."""
        assert formater_pourcentage(50.0) == "50%"

    def test_pourcentage_stock_75_5(self):
        """Stock 75.5%."""
        assert formater_pourcentage(75.5) == "75.5%"

    def test_pourcentage_2_decimales(self):
        """Pourcentage 2 décimales."""
        result = formater_pourcentage(33.333, decimals=2)
        assert "33" in result

    def test_pourcentage_0(self):
        """0%."""
        assert formater_pourcentage(0) == "0%"

    def test_pourcentage_none(self):
        """None."""
        assert formater_pourcentage(None) == "0%"


@pytest.mark.unit
class TestFormaterNombre:
    """Tests pour formater_nombre."""

    def test_nombre_1000(self):
        """1000."""
        result = formater_nombre(1000)
        assert "1 000" in result or "1,000" in result

    def test_nombre_1234567(self):
        """1234567."""
        result = formater_nombre(1234567)
        assert "234" in result
        assert "567" in result

    def test_nombre_avec_decimales(self):
        """Avec décimales."""
        result = formater_nombre(1234.56, decimals=2)
        assert "1" in result
        assert "234" in result

    def test_nombre_0(self):
        """0."""
        assert formater_nombre(0) == "0"

    def test_nombre_none(self):
        """None."""
        assert formater_nombre(None) == "0"


@pytest.mark.unit
class TestFormaterTailleFichier:
    """Tests pour formater_taille_fichier (images recettes)."""

    def test_taille_500_octets(self):
        """500 octets."""
        result = formater_taille_fichier(500)
        assert "500" in result
        assert "o" in result.lower()

    def test_taille_1_ko(self):
        """1 Ko."""
        result = formater_taille_fichier(1024)
        assert "1" in result
        assert "Ko" in result or "KB" in result.upper()

    def test_taille_2_5_ko(self):
        """2.5 Ko."""
        result = formater_taille_fichier(2560)
        assert "2.5" in result or "2,5" in result

    def test_taille_1_mo(self):
        """1 Mo (image recette)."""
        result = formater_taille_fichier(1024 * 1024)
        assert "1" in result
        assert "Mo" in result or "MB" in result.upper()

    def test_taille_5_mo(self):
        """5 Mo (grosse image)."""
        result = formater_taille_fichier(1024 * 1024 * 5)
        assert "5" in result
        assert "Mo" in result or "MB" in result.upper()

    def test_taille_1_go(self):
        """1 Go."""
        result = formater_taille_fichier(1024 * 1024 * 1024)
        assert "1" in result
        assert "Go" in result or "GB" in result.upper()

    def test_taille_0(self):
        """0 octets."""
        assert formater_taille_fichier(0) == "0 o"

    def test_taille_none(self):
        """None."""
        assert formater_taille_fichier(None) == "0 o"


@pytest.mark.unit
class TestFormaterPlage:
    """Tests pour formater_plage (temps, prix)."""

    def test_plage_temps_cuisson(self):
        """Temps cuisson 30-45 min."""
        result = formater_plage(30, 45, "min")
        assert "30" in result
        assert "45" in result
        assert "min" in result

    def test_plage_prix(self):
        """Prix 10-20€."""
        result = formater_plage(10, 20, "€")
        assert "10" in result
        assert "20" in result
        assert "€" in result

    def test_plage_portions(self):
        """Portions 4-6."""
        result = formater_plage(4, 6)
        assert "4" in result
        assert "6" in result


@pytest.mark.unit
class TestArrondirIntelligent:
    """Tests pour arrondir_intelligent."""

    def test_arrondi_simple(self):
        """Arrondi simple."""
        assert arrondir_intelligent(3.14159, 2) == 3.14

    def test_arrondi_float_error(self):
        """Corrige erreur float."""
        assert arrondir_intelligent(2.5000000001) == 2.5

    def test_arrondi_0_decimales(self):
        """0 décimales."""
        assert arrondir_intelligent(3.7, 0) == 4.0

    def test_arrondi_none(self):
        """None."""
        assert arrondir_intelligent(None) == 0.0
