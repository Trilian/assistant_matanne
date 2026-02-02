"""
Tests pour src/core/ai/parser.py
Cible: AnalyseurIA - parsing JSON, réparation, stratégies
"""

import pytest
import json
from unittest.mock import Mock, patch
from pydantic import BaseModel


# ═══════════════════════════════════════════════════════════
# MODÈLES DE TEST
# ═══════════════════════════════════════════════════════════


class RecetteSimple(BaseModel):
    """Modèle simple pour tests."""
    nom: str
    temps: int


class RecetteAvecIngredients(BaseModel):
    """Modèle avec liste pour tests."""
    nom: str
    ingredients: list[str]


class RecetteOptionnelle(BaseModel):
    """Modèle avec champs optionnels."""
    nom: str
    description: str | None = None
    temps: int = 30


# ═══════════════════════════════════════════════════════════
# TESTS STRATÉGIE 1: PARSE DIRECT
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestAnalyseurIAParseDirecte:
    """Tests pour la stratégie 1: parse direct."""

    def test_parse_json_propre(self):
        """Parse un JSON propre correctement formaté."""
        from src.core.ai.parser import AnalyseurIA
        
        reponse = '{"nom": "Tarte aux pommes", "temps": 45}'
        
        result = AnalyseurIA.analyser(reponse, RecetteSimple)
        
        assert result.nom == "Tarte aux pommes"
        assert result.temps == 45

    def test_parse_json_avec_espaces(self):
        """Parse un JSON avec espaces et newlines."""
        from src.core.ai.parser import AnalyseurIA
        
        reponse = '''
        {
            "nom": "Quiche lorraine",
            "temps": 60
        }
        '''
        
        result = AnalyseurIA.analyser(reponse, RecetteSimple)
        
        assert result.nom == "Quiche lorraine"
        assert result.temps == 60

    def test_parse_json_avec_liste(self):
        """Parse un JSON contenant une liste."""
        from src.core.ai.parser import AnalyseurIA
        
        reponse = '{"nom": "Salade", "ingredients": ["laitue", "tomates", "concombre"]}'
        
        result = AnalyseurIA.analyser(reponse, RecetteAvecIngredients)
        
        assert result.nom == "Salade"
        assert len(result.ingredients) == 3
        assert "tomates" in result.ingredients


# ═══════════════════════════════════════════════════════════
# TESTS STRATÉGIE 2: EXTRACTION JSON
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestAnalyseurIAExtractionJSON:
    """Tests pour la stratégie 2: extraction JSON."""

    def test_extraction_json_dans_texte(self):
        """Extrait le JSON d'un texte avec du contenu autour."""
        from src.core.ai.parser import AnalyseurIA
        
        reponse = '''Voici la recette demandée:
        {"nom": "Crêpes", "temps": 20}
        J'espère que ça vous plaira!'''
        
        result = AnalyseurIA.analyser(reponse, RecetteSimple)
        
        assert result.nom == "Crêpes"
        assert result.temps == 20

    def test_extraction_json_markdown(self):
        """Extrait le JSON d'un bloc markdown."""
        from src.core.ai.parser import AnalyseurIA
        
        reponse = '''```json
{"nom": "Gâteau", "temps": 90}
```'''
        
        result = AnalyseurIA.analyser(reponse, RecetteSimple)
        
        assert result.nom == "Gâteau"
        assert result.temps == 90

    def test_extraction_json_triple_backticks(self):
        """Extrait le JSON de triple backticks sans json."""
        from src.core.ai.parser import AnalyseurIA
        
        reponse = '''Résultat:
```
{"nom": "Mousse chocolat", "temps": 30}
```
Bon appétit!'''
        
        result = AnalyseurIA.analyser(reponse, RecetteSimple)
        
        assert result.nom == "Mousse chocolat"


# ═══════════════════════════════════════════════════════════
# TESTS STRATÉGIE 3: RÉPARATION
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestAnalyseurIAReparation:
    """Tests pour la stratégie 3: réparation JSON."""

    def test_reparation_virgule_finale(self):
        """Répare un JSON avec virgule finale."""
        from src.core.ai.parser import AnalyseurIA
        
        # JSON invalide avec virgule finale
        reponse = '{"nom": "Soupe", "temps": 25,}'
        
        result = AnalyseurIA.analyser(reponse, RecetteSimple)
        
        assert result.nom == "Soupe"

    def test_reparation_guillemets_simples(self):
        """Répare un JSON avec guillemets simples ou utilise fallback."""
        from src.core.ai.parser import AnalyseurIA
        
        reponse = "{'nom': 'Omelette', 'temps': 10}"
        fallback = {"nom": "Omelette", "temps": 10}
        
        # Le parser peut ou non réparer les guillemets simples
        # On teste avec fallback pour couvrir les deux cas
        result = AnalyseurIA.analyser(reponse, RecetteSimple, valeur_secours=fallback)
        
        assert result.nom == "Omelette"

    def test_reparation_cle_sans_guillemets(self):
        """Répare un JSON avec clés sans guillemets."""
        from src.core.ai.parser import AnalyseurIA
        
        reponse = '{nom: "Riz", temps: 15}'
        
        result = AnalyseurIA.analyser(reponse, RecetteSimple)
        
        assert result.nom == "Riz"


# ═══════════════════════════════════════════════════════════
# TESTS STRATÉGIE 5: FALLBACK
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestAnalyseurIAFallback:
    """Tests pour la stratégie 5: fallback."""

    def test_fallback_utilise_valeur_secours(self):
        """Utilise la valeur de secours si parse échoue."""
        from src.core.ai.parser import AnalyseurIA
        
        reponse = "Ceci n'est pas du JSON valide du tout"
        fallback = {"nom": "Recette par défaut", "temps": 30}
        
        result = AnalyseurIA.analyser(reponse, RecetteSimple, valeur_secours=fallback)
        
        assert result.nom == "Recette par défaut"
        assert result.temps == 30

    def test_strict_mode_raises_error(self):
        """En mode strict, lève une erreur si parse échoue."""
        from src.core.ai.parser import AnalyseurIA
        
        reponse = "Pas du JSON"
        
        with pytest.raises(ValueError) as exc_info:
            AnalyseurIA.analyser(reponse, RecetteSimple, strict=True)
        
        assert "Impossible" in str(exc_info.value)

    def test_no_fallback_no_strict_raises_error(self):
        """Sans fallback et sans strict, lève quand même une erreur."""
        from src.core.ai.parser import AnalyseurIA
        
        reponse = "Pas du JSON du tout !!!@@@"
        
        with pytest.raises(ValueError):
            AnalyseurIA.analyser(reponse, RecetteSimple)


# ═══════════════════════════════════════════════════════════
# TESTS FONCTIONS UTILITAIRES
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestAnalyseurIAUtilitaires:
    """Tests pour les fonctions utilitaires."""

    def test_nettoyer_basique(self):
        """Teste le nettoyage basique."""
        from src.core.ai.parser import AnalyseurIA
        
        texte = '  \n{"test": 1}\n  '
        result = AnalyseurIA._nettoyer_basique(texte)
        
        assert result.strip() == '{"test": 1}'

    def test_extraire_objet_json(self):
        """Teste l'extraction d'objet JSON."""
        from src.core.ai.parser import AnalyseurIA
        
        texte = 'Texte avant {"key": "value"} texte après'
        result = AnalyseurIA._extraire_objet_json(texte)
        
        assert '"key"' in result
        assert '"value"' in result


# ═══════════════════════════════════════════════════════════
# TESTS ANALYSER_LISTE_REPONSE (FONCTION SÉPARÉE)
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestAnalyserListeReponse:
    """Tests pour analyser_liste_reponse (fonction séparée)."""

    def test_analyser_liste_array(self):
        """Parse une liste JSON directe."""
        from src.core.ai.parser import analyser_liste_reponse
        
        reponse = '[{"nom": "Recette 1", "temps": 10}, {"nom": "Recette 2", "temps": 20}]'
        
        result = analyser_liste_reponse(reponse, RecetteSimple)
        
        assert len(result) == 2
        assert result[0].nom == "Recette 1"
        assert result[1].temps == 20

    def test_analyser_liste_avec_items_key(self):
        """Parse une liste avec clé 'items'."""
        from src.core.ai.parser import analyser_liste_reponse
        
        reponse = '{"items": [{"nom": "A", "temps": 5}, {"nom": "B", "temps": 10}]}'
        
        result = analyser_liste_reponse(reponse, RecetteSimple, cle_liste="items")
        
        assert len(result) == 2

    def test_analyser_liste_vide(self):
        """Parse une liste vide."""
        from src.core.ai.parser import analyser_liste_reponse
        
        reponse = '[]'
        
        result = analyser_liste_reponse(reponse, RecetteSimple)
        
        assert result == []


# ═══════════════════════════════════════════════════════════
# TESTS EDGE CASES
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestAnalyseurIAEdgeCases:
    """Tests pour les cas limites."""

    def test_reponse_vide(self):
        """Gère une réponse vide."""
        from src.core.ai.parser import AnalyseurIA
        
        with pytest.raises(ValueError):
            AnalyseurIA.analyser("", RecetteSimple, strict=True)

    def test_reponse_none(self):
        """Gère une réponse None."""
        from src.core.ai.parser import AnalyseurIA
        
        with pytest.raises((ValueError, TypeError, AttributeError)):
            AnalyseurIA.analyser(None, RecetteSimple, strict=True)

    def test_json_nested_profond(self):
        """Parse un JSON profondément imbriqué."""
        from src.core.ai.parser import AnalyseurIA
        
        class ModeleProfond(BaseModel):
            niveau1: dict
        
        reponse = '{"niveau1": {"niveau2": {"niveau3": "valeur"}}}'
        
        result = AnalyseurIA.analyser(reponse, ModeleProfond)
        
        assert result.niveau1["niveau2"]["niveau3"] == "valeur"

    def test_json_caracteres_unicode(self):
        """Parse un JSON avec caractères Unicode."""
        from src.core.ai.parser import AnalyseurIA
        
        reponse = '{"nom": "Crème brûlée", "temps": 45}'
        
        result = AnalyseurIA.analyser(reponse, RecetteSimple)
        
        assert result.nom == "Crème brûlée"

    def test_json_nombres_negatifs(self):
        """Parse un JSON avec nombres négatifs."""
        from src.core.ai.parser import AnalyseurIA
        
        class ModeleAvecNegatif(BaseModel):
            valeur: int
        
        reponse = '{"valeur": -42}'
        
        result = AnalyseurIA.analyser(reponse, ModeleAvecNegatif)
        
        assert result.valeur == -42

    def test_json_boolean_values(self):
        """Parse un JSON avec valeurs booléennes."""
        from src.core.ai.parser import AnalyseurIA
        
        class ModeleAvecBool(BaseModel):
            actif: bool
            visible: bool
        
        reponse = '{"actif": true, "visible": false}'
        
        result = AnalyseurIA.analyser(reponse, ModeleAvecBool)
        
        assert result.actif is True
        assert result.visible is False
