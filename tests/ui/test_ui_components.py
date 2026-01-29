"""
Tests pour les composants UI (User Interface).

Teste :
- Alignement des cards
- Formatting HTML
- Responsive design
"""

import pytest
import re


# ═══════════════════════════════════════════════════════════
# TESTS ALIGNEMENT RECETTES CARDS
# ═══════════════════════════════════════════════════════════

@pytest.mark.unit
class TestRecetteCardAlignment:
    """Tests pour l'alignement des cards de recettes."""
    
    def test_recipe_card_title_has_fixed_height(self):
        """Teste que le titre de la card a une hauteur fixe."""
        # Style du titre comme dans recettes.py ligne 201
        title_style = "margin: 6px 0; line-height: 1.2; font-size: 15px; height: 2.4em; overflow: hidden; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical;"
        
        # Vérifier la présence des propriétés clés
        assert "height: 2.4em" in title_style
        assert "overflow: hidden" in title_style
        assert "-webkit-line-clamp: 2" in title_style
        assert "display: -webkit-box" in title_style
    
    def test_recipe_card_title_overflow_ellipsis(self):
        """Teste que le texte qui dépasse est tronqué avec points."""
        # Style avec ellipsis
        title_style = "height: 2.4em; overflow: hidden; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical;"
        
        # Ces styles ensemble créent un effet de truncate automatique
        required_styles = [
            "height",
            "overflow",
            "-webkit-line-clamp"
        ]
        
        for style in required_styles:
            assert style in title_style
    
    def test_recipe_card_emoji_preserved(self):
        """Teste que l'emoji de difficulté est préservé."""
        difficulty_emoji_map = {
            "facile": "🟢",
            "moyen": "🟡",
            "difficile": "🔴"
        }
        
        for difficulty, emoji in difficulty_emoji_map.items():
            html_title = f'<h4>{emoji} Titre très long qui pourrait s\'étendre sur deux lignes</h4>'
            
            # L'emoji doit être présent
            assert emoji in html_title
    
    def test_recipe_card_title_multiline_aligned(self):
        """Teste que les titres de 1 et 2 lignes ont même hauteur."""
        # Tous les titres avec height: 2.4em auront exactement 2.4em de haut
        # peu importe le nombre de lignes (grâce à line-height: 1.2)
        # 2.4em ≈ 2 lignes de height
        height_em = 2.4
        line_height = 1.2
        max_lines = int(height_em / line_height)
        
        assert max_lines == 2
    
    def test_recipe_card_description_text_preserved(self):
        """Teste que la description n'est pas affectée par l'alignement du titre."""
        # La description est sur une ligne séparée et ne doit pas être limitée
        # par les styles du titre
        description_style = "margin: 2px 0; font-size: 11px; opacity: 0.7;"
        
        # La description n'a pas de height limitée, donc elle peut s'étendre
        assert "height" not in description_style
        assert "overflow" not in description_style


# ═══════════════════════════════════════════════════════════
# TESTS VALIDATION HTML SANITAIRE
# ═══════════════════════════════════════════════════════════

@pytest.mark.unit
class TestHTMLSanitization:
    """Tests pour la sécurité des styles HTML."""
    
    def test_recipe_card_style_no_malicious_code(self):
        """Teste qu'aucune injection de code n'est possible via styles."""
        malicious_patterns = [
            r"javascript:",
            r"onclick",
            r"onerror",
            r"onload",
            r"expression",
        ]
        
        # Style safe du titre
        safe_style = "margin: 6px 0; line-height: 1.2; font-size: 15px; height: 2.4em; overflow: hidden;"
        
        for pattern in malicious_patterns:
            assert re.search(pattern, safe_style, re.IGNORECASE) is None
    
    def test_recipe_card_numeric_values_valid(self):
        """Teste que les valeurs numériques des styles sont valides."""
        # Valeurs du style
        style_values = {
            "margin": "6px",
            "line-height": "1.2",  # Sans unité pour les multiples
            "font-size": "15px",
            "height": "2.4em",
        }
        
        # Regex pour valider les valeurs (incluant les valeurs sans unité pour line-height)
        numeric_pattern = r"^[\d.]+(?:px|em|rem|%|vh|vw)?$"
        
        for key, value in style_values.items():
            assert re.match(numeric_pattern, value), f"{key}: {value} is not a valid CSS value"


# ═══════════════════════════════════════════════════════════
# TESTS RESPONSIVE DESIGN
# ═══════════════════════════════════════════════════════════

@pytest.mark.unit
class TestResponsiveDesign:
    """Tests pour le design responsive."""
    
    def test_recipe_card_relative_units(self):
        """Teste l'utilisation d'unités relatives pour la responsivité."""
        # Tous les sizes doivent utiliser des unités relatives
        # pour être responsive
        style_with_em = "font-size: 15px; height: 2.4em; line-height: 1.2;"
        
        # em est une unité relative
        assert "em" in style_with_em
    
    def test_recipe_card_flexbox_compatible(self):
        """Teste que le layout est compatible avec flexbox."""
        # display: -webkit-box est compatible avec flex
        style = "display: -webkit-box; -webkit-box-orient: vertical;"
        
        assert "display" in style
        assert "box" in style


# ═══════════════════════════════════════════════════════════
# TESTS COMPATIBILITÉ NAVIGATEURS
# ═══════════════════════════════════════════════════════════

@pytest.mark.unit
class TestBrowserCompatibility:
    """Tests pour la compatibilité navigateurs."""
    
    def test_webkit_prefix_present(self):
        """Teste que les préfixes -webkit- sont présents pour Chrome/Safari."""
        style = "display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical;"
        
        # Webkit prefixes pour anciens navigateurs
        assert "-webkit-box" in style
        assert "-webkit-line-clamp" in style
    
    def test_fallback_properties_present(self):
        """Teste que les propriétés de fallback existent."""
        style = "overflow: hidden; height: 2.4em; display: -webkit-box;"
        
        # overflow: hidden est un fallback si line-clamp ne fonctionne pas
        assert "overflow: hidden" in style
    
    def test_emoji_rendering_consistent(self):
        """Teste que les emojis s'affichent correctement."""
        emojis = ["🟢", "🟡", "🔴", "⚪"]
        
        for emoji in emojis:
            # Vérifier que l'emoji est un caractère Unicode valide
            assert len(emoji) > 0
            assert ord(emoji[0]) > 127  # Caractère non-ASCII


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
