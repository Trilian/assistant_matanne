"""
Tests pour src/core/ai/parser.py - Analyseur JSON IA.
"""

import json

import pytest
from pydantic import BaseModel, Field

from src.core.ai.parser import AnalyseurIA, analyser_liste_reponse


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# MODÃˆLES DE TEST
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class RecetteTest(BaseModel):
    """Modèle de test pour recettes."""

    nom: str
    temps_preparation: int = 30
    difficulte: str = "facile"


class IngredientTest(BaseModel):
    """Modèle de test pour ingrédients."""

    nom: str
    quantite: float = 1.0
    unite: str = "pièce"


class ReponseListe(BaseModel):
    """Modèle avec liste."""

    items: list[RecetteTest]


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS NETTOYAGE BASIQUE
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestNettoyageBasique:
    """Tests pour _nettoyer_basique()."""

    def test_supprime_bom(self):
        """Test suppression BOM."""
        texte = "\ufeff{\"nom\": \"test\"}"
        result = AnalyseurIA._nettoyer_basique(texte)
        assert "\ufeff" not in result

    def test_supprime_markdown_json(self):
        """Test suppression balises markdown."""
        texte = "```json\n{\"nom\": \"test\"}\n```"
        result = AnalyseurIA._nettoyer_basique(texte)
        assert "```" not in result
        assert "json" not in result.lower() or "nom" in result

    def test_supprime_caracteres_controle(self):
        """Test suppression caractères de contrôle."""
        texte = '{"nom": "test\x00\x1F"}'
        result = AnalyseurIA._nettoyer_basique(texte)
        assert "\x00" not in result
        assert "\x1F" not in result

    def test_strip_whitespace(self):
        """Test strip whitespace."""
        texte = "  {\"nom\": \"test\"}  "
        result = AnalyseurIA._nettoyer_basique(texte)
        assert result == '{"nom": "test"}'


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS EXTRACTION JSON
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestExtractionJSON:
    """Tests pour _extraire_objet_json()."""

    def test_extrait_objet_simple(self):
        """Test extraction objet simple."""
        texte = 'Voici la recette: {"nom": "Tarte"} et voilà!'
        result = AnalyseurIA._extraire_objet_json(texte)
        assert result == '{"nom": "Tarte"}'

    def test_extrait_objet_imbriqué(self):
        """Test extraction objet imbriqué."""
        texte = '{"recette": {"nom": "Tarte", "infos": {"temps": 30}}}'
        result = AnalyseurIA._extraire_objet_json(texte)
        assert '"nom": "Tarte"' in result
        assert '"temps": 30' in result

    def test_extrait_liste(self):
        """Test extraction liste."""
        texte = 'Recettes: [{"nom": "A"}, {"nom": "B"}] terminé'
        result = AnalyseurIA._extraire_objet_json(texte)
        assert result.startswith("[")
        assert result.endswith("]")

    def test_raise_si_pas_json(self):
        """Test raise si pas de JSON."""
        texte = "Pas de JSON ici!"
        with pytest.raises(ValueError, match="Aucun objet"):
            AnalyseurIA._extraire_objet_json(texte)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS RÃ‰PARATION INTELLIGENTE
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestReparationIntelligente:
    """Tests pour _reparer_intelligemment()."""

    def test_repare_virgule_trailing(self):
        """Test réparation virgule trailing."""
        texte = '{"nom": "test",}'
        result = AnalyseurIA._reparer_intelligemment(texte)
        data = json.loads(result)
        assert data["nom"] == "test"

    def test_repare_booleans_python(self):
        """Test réparation booleans Python."""
        texte = '{"actif": True, "archive": False}'
        result = AnalyseurIA._reparer_intelligemment(texte)
        data = json.loads(result)
        assert data["actif"] is True
        assert data["archive"] is False

    def test_repare_none_python(self):
        """Test réparation None Python."""
        texte = '{"valeur": None}'
        result = AnalyseurIA._reparer_intelligemment(texte)
        data = json.loads(result)
        assert data["valeur"] is None

    def test_repare_cles_sans_guillemets(self):
        """Test réparation clés sans guillemets."""
        texte = '{nom: "test"}'
        result = AnalyseurIA._reparer_intelligemment(texte)
        # Devrait maintenant avoir des guillemets
        assert '"nom"' in result


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS PARSE PARTIEL
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestParsePartiel:
    """Tests pour _analyser_partiel()."""

    def test_parse_partiel_extrait_champs(self):
        """Test extraction champs partiels."""
        texte = '{"nom": "Tarte", "temps_preparation": 45, incomplet...'
        result = AnalyseurIA._analyser_partiel(texte, RecetteTest)
        
        assert result is not None
        assert "nom" in result
        assert result["nom"] == "Tarte"

    def test_parse_partiel_json_cassé(self):
        """Test parse JSON cassé."""
        texte = '{"nom": "Test", "temps_preparation": 30'  # Pas de fermeture
        result = AnalyseurIA._analyser_partiel(texte, RecetteTest)
        
        # Peut retourner quelque chose ou None selon le parsing
        if result:
            assert "nom" in result

    def test_parse_partiel_retourne_none_si_vide(self):
        """Test retourne None si aucun champ."""
        texte = "Pas de JSON valide ici"
        result = AnalyseurIA._analyser_partiel(texte, RecetteTest)
        assert result is None


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS ANALYSEUR PRINCIPAL
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestAnalyseurPrincipal:
    """Tests pour AnalyseurIA.analyser()."""

    def test_strategie_1_json_propre(self):
        """Test stratégie 1 - JSON propre."""
        reponse = '{"nom": "Tarte", "temps_preparation": 45, "difficulte": "facile"}'
        result = AnalyseurIA.analyser(reponse, RecetteTest)
        
        assert result.nom == "Tarte"
        assert result.temps_preparation == 45

    def test_strategie_2_extraction(self):
        """Test stratégie 2 - extraction JSON."""
        reponse = 'Voici ma suggestion: {"nom": "Quiche", "temps_preparation": 60, "difficulte": "moyen"} Bon appétit!'
        result = AnalyseurIA.analyser(reponse, RecetteTest)
        
        assert result.nom == "Quiche"
        assert result.temps_preparation == 60

    def test_strategie_3_reparation(self):
        """Test stratégie 3 - réparation."""
        reponse = '{"nom": "Salade", "temps_preparation": 10, "difficulte": "facile",}'
        result = AnalyseurIA.analyser(reponse, RecetteTest)
        
        assert result.nom == "Salade"

    def test_fallback_si_echec(self):
        """Test fallback si toutes stratégies échouent."""
        reponse = "Texte complètement invalide"
        fallback = {"nom": "Fallback", "temps_preparation": 0, "difficulte": "inconnu"}
        
        result = AnalyseurIA.analyser(reponse, RecetteTest, valeur_secours=fallback)
        
        assert result.nom == "Fallback"

    def test_strict_mode_raises(self):
        """Test mode strict raise si échec."""
        reponse = "Invalide"
        
        with pytest.raises(ValueError, match="Impossible d'analyser"):
            AnalyseurIA.analyser(reponse, RecetteTest, strict=True)

    def test_avec_markdown(self):
        """Test avec balises markdown."""
        reponse = '```json\n{"nom": "Pizza", "temps_preparation": 90, "difficulte": "moyen"}\n```'
        result = AnalyseurIA.analyser(reponse, RecetteTest)
        
        assert result.nom == "Pizza"

    def test_valeurs_par_defaut(self):
        """Test valeurs par défaut du modèle."""
        reponse = '{"nom": "Test"}'
        result = AnalyseurIA.analyser(reponse, RecetteTest)
        
        assert result.nom == "Test"
        assert result.temps_preparation == 30  # Default
        assert result.difficulte == "facile"  # Default


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS ANALYSER LISTE REPONSE
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestAnalyserListeReponse:
    """Tests pour analyser_liste_reponse()."""

    def test_parse_liste_simple(self):
        """Test parse liste simple."""
        reponse = '{"items": [{"nom": "A", "temps_preparation": 10, "difficulte": "facile"}, {"nom": "B", "temps_preparation": 20, "difficulte": "moyen"}]}'
        result = analyser_liste_reponse(reponse, RecetteTest)
        
        assert len(result) == 2
        assert result[0].nom == "A"
        assert result[1].nom == "B"

    def test_parse_liste_vide(self):
        """Test parse liste vide."""
        reponse = '{"items": []}'
        result = analyser_liste_reponse(reponse, RecetteTest)
        
        assert result == []

    def test_fallback_liste(self):
        """Test fallback pour liste."""
        reponse = "Invalide"
        fallback = [{"nom": "Default", "temps_preparation": 0, "difficulte": "?"}]
        
        result = analyser_liste_reponse(reponse, RecetteTest, items_secours=fallback)
        
        assert len(result) == 1
        assert result[0].nom == "Default"


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS CAS EDGE
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestCasEdge:
    """Tests pour cas edge et limites."""

    def test_json_tres_long(self):
        """Test JSON très long."""
        reponse = '{"nom": "' + "A" * 10000 + '", "temps_preparation": 30, "difficulte": "facile"}'
        result = AnalyseurIA.analyser(reponse, RecetteTest)
        
        assert len(result.nom) == 10000

    def test_caracteres_speciaux(self):
        """Test caractères spéciaux dans valeurs."""
        reponse = '{"nom": "PÃ¢té été", "temps_preparation": 30, "difficulte": "facile"}'
        result = AnalyseurIA.analyser(reponse, RecetteTest)
        
        assert result.nom == "PÃ¢té été"

    def test_unicode_emojis(self):
        """Test unicode et emojis."""
        reponse = '{"nom": "Pizza ðŸ•", "temps_preparation": 30, "difficulte": "facile"}'
        result = AnalyseurIA.analyser(reponse, RecetteTest)
        
        assert "ðŸ•" in result.nom

    def test_nombres_float(self):
        """Test nombres à virgule."""
        reponse = '{"nom": "Test", "quantite": 1.5, "unite": "kg"}'
        result = AnalyseurIA.analyser(reponse, IngredientTest)
        
        assert result.quantite == 1.5

    def test_reponse_vide(self):
        """Test réponse vide."""
        reponse = ""
        fallback = {"nom": "Empty", "temps_preparation": 0, "difficulte": "?"}
        
        result = AnalyseurIA.analyser(reponse, RecetteTest, valeur_secours=fallback)
        
        assert result.nom == "Empty"

    def test_reponse_whitespace_only(self):
        """Test réponse whitespace seulement."""
        reponse = "   \n\t   "
        fallback = {"nom": "Whitespace", "temps_preparation": 0, "difficulte": "?"}
        
        result = AnalyseurIA.analyser(reponse, RecetteTest, valeur_secours=fallback)
        
        assert result.nom == "Whitespace"


