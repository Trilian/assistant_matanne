"""
Tests pour les fonctions utilitaires de liste de courses.
Ces tests sont simples car les fonctions sont pures (pas de dépendance Streamlit).
"""

import pytest

from src.modules.cuisine.courses.liste_utils import (
    calculer_statistiques_liste,
    extraire_rayons_uniques,
    filtrer_liste,
    formater_article_label,
    generer_texte_impression,
    grouper_par_rayon,
    valider_article_data,
)


class TestFiltrerListe:
    """Tests pour filtrer_liste()."""

    @pytest.fixture
    def sample_liste(self):
        """Liste d'articles de test."""
        return [
            {"ingredient_nom": "Tomates", "priorite": "haute", "rayon_magasin": "Fruits"},
            {"ingredient_nom": "Pommes", "priorite": "basse", "rayon_magasin": "Fruits"},
            {"ingredient_nom": "Lait", "priorite": "moyenne", "rayon_magasin": "Crèmerie"},
            {"ingredient_nom": "Pain", "priorite": "haute", "rayon_magasin": "Boulangerie"},
        ]

    def test_filtrer_sans_criteres(self, sample_liste):
        """Sans critères, retourne la liste complète."""
        result = filtrer_liste(sample_liste)
        assert len(result) == 4

    def test_filtrer_par_priorite(self, sample_liste):
        """Filtre par priorité haute."""
        result = filtrer_liste(sample_liste, priorite="haute")
        assert len(result) == 2
        assert all(a["priorite"] == "haute" for a in result)

    def test_filtrer_par_rayon(self, sample_liste):
        """Filtre par rayon Fruits."""
        result = filtrer_liste(sample_liste, rayon="Fruits")
        assert len(result) == 2
        assert all(a["rayon_magasin"] == "Fruits" for a in result)

    def test_filtrer_par_recherche(self, sample_liste):
        """Filtre par terme de recherche."""
        result = filtrer_liste(sample_liste, search_term="tom")
        assert len(result) == 1
        assert result[0]["ingredient_nom"] == "Tomates"

    def test_filtrer_recherche_insensible_casse(self, sample_liste):
        """Recherche insensible à la casse."""
        result = filtrer_liste(sample_liste, search_term="LAIT")
        assert len(result) == 1
        assert result[0]["ingredient_nom"] == "Lait"

    def test_filtrer_combinaison_criteres(self, sample_liste):
        """Filtre avec plusieurs critères."""
        result = filtrer_liste(sample_liste, priorite="haute", rayon="Fruits")
        assert len(result) == 1
        assert result[0]["ingredient_nom"] == "Tomates"

    def test_filtrer_liste_vide(self):
        """Filtre sur liste vide."""
        result = filtrer_liste([])
        assert result == []

    def test_filtrer_aucun_resultat(self, sample_liste):
        """Filtres qui ne donnent aucun résultat."""
        result = filtrer_liste(sample_liste, search_term="inexistant")
        assert result == []


class TestGrouperParRayon:
    """Tests pour grouper_par_rayon()."""

    def test_grouper_basique(self):
        """Groupement basique par rayon."""
        liste = [
            {"ingredient_nom": "A", "rayon_magasin": "Fruits"},
            {"ingredient_nom": "B", "rayon_magasin": "Crèmerie"},
            {"ingredient_nom": "C", "rayon_magasin": "Fruits"},
        ]
        result = grouper_par_rayon(liste)

        assert "Fruits" in result
        assert "Crèmerie" in result
        assert len(result["Fruits"]) == 2
        assert len(result["Crèmerie"]) == 1

    def test_grouper_rayon_manquant(self):
        """Articles sans rayon ont rayon_magasin=None ou absent, vont dans 'Autre'."""
        liste = [
            {"ingredient_nom": "A"},  # rayon_magasin absent
            {"ingredient_nom": "B", "rayon_magasin": "Autre"},  # rayon explicite
        ]
        result = grouper_par_rayon(liste)

        assert "Autre" in result
        assert len(result["Autre"]) == 2

    def test_grouper_rayon_none(self):
        """Articles avec rayon_magasin=None vont dans 'Autre'."""
        liste = [
            {"ingredient_nom": "A", "rayon_magasin": None},
            {"ingredient_nom": "B", "rayon_magasin": "Fruits"},
        ]
        result = grouper_par_rayon(liste)

        assert "Autre" in result
        assert "Fruits" in result
        assert len(result["Autre"]) == 1

    def test_grouper_liste_vide(self):
        """Groupement sur liste vide."""
        result = grouper_par_rayon([])
        assert result == {}


class TestCalculerStatistiquesListe:
    """Tests pour calculer_statistiques_liste()."""

    def test_statistiques_completes(self):
        """Calcul avec toutes les données."""
        liste = [
            {"priorite": "haute"},
            {"priorite": "haute"},
            {"priorite": "basse"},
        ]
        liste_achetee = [{"id": 1}, {"id": 2}]
        alertes = [{"id": 1}]

        result = calculer_statistiques_liste(liste, liste_achetee, alertes)

        assert result["a_acheter"] == 3
        assert result["haute_priorite"] == 2
        assert result["stock_bas"] == 1
        assert result["total_achetes"] == 2

    def test_statistiques_sans_optionnels(self):
        """Calcul sans données optionnelles."""
        liste = [{"priorite": "moyenne"}]

        result = calculer_statistiques_liste(liste)

        assert result["a_acheter"] == 1
        assert result["haute_priorite"] == 0
        assert result["stock_bas"] == 0
        assert result["total_achetes"] == 0

    def test_statistiques_liste_vide(self):
        """Calcul sur liste vide."""
        result = calculer_statistiques_liste([])

        assert result["a_acheter"] == 0
        assert result["haute_priorite"] == 0


class TestFormaterArticleLabel:
    """Tests pour formater_article_label()."""

    @pytest.fixture
    def priority_emojis(self):
        return {"haute": "🔴", "moyenne": "🟡", "basse": "🟢"}

    def test_formater_basique(self, priority_emojis):
        """Formatage basique."""
        article = {
            "ingredient_nom": "Tomates",
            "quantite_necessaire": 2.5,
            "unite": "kg",
            "priorite": "haute",
        }
        result = formater_article_label(article, priority_emojis)

        assert "🔴" in result
        assert "Tomates" in result
        assert "2.5" in result
        assert "kg" in result

    def test_formater_avec_notes(self, priority_emojis):
        """Formatage avec notes."""
        article = {
            "ingredient_nom": "Lait",
            "quantite_necessaire": 1,
            "unite": "l",
            "priorite": "moyenne",
            "notes": "Bio de préférence",
        }
        result = formater_article_label(article, priority_emojis)

        assert "📝" in result
        assert "Bio de préférence" in result

    def test_formater_avec_ia_marker(self, priority_emojis):
        """Formatage avec marqueur IA."""
        article = {
            "ingredient_nom": "Pain",
            "quantite_necessaire": 1,
            "unite": "pièce",
            "priorite": "basse",
            "suggere_par_ia": True,
        }
        result = formater_article_label(article, priority_emojis)

        assert "⏰" in result

    def test_formater_sans_notes_ni_ia(self, priority_emojis):
        """Formatage sans notes ni IA."""
        article = {
            "ingredient_nom": "Œufs",
            "quantite_necessaire": 12,
            "unite": "pièce",
            "priorite": "moyenne",
        }
        result = formater_article_label(
            article, priority_emojis, include_notes=False, include_ia_marker=False
        )

        assert "📝" not in result
        assert "⏰" not in result

    def test_formater_priorite_inconnue(self, priority_emojis):
        """Formatage avec priorité non mappée."""
        article = {
            "ingredient_nom": "Test",
            "quantite_necessaire": 1,
            "unite": "kg",
            "priorite": "inconnue",
        }
        result = formater_article_label(article, priority_emojis)

        assert "⚫" in result  # Emoji par défaut


class TestGenererTexteImpression:
    """Tests pour generer_texte_impression()."""

    def test_generer_basique(self):
        """Génération basique du texte d'impression."""
        liste = [
            {
                "ingredient_nom": "Tomates",
                "quantite_necessaire": 2,
                "unite": "kg",
                "rayon_magasin": "Fruits",
            },
            {
                "ingredient_nom": "Lait",
                "quantite_necessaire": 1,
                "unite": "l",
                "rayon_magasin": "Crèmerie",
            },
        ]

        result = generer_texte_impression(liste)

        assert "LISTE DE COURSES" in result
        assert "Fruits" in result
        assert "Crèmerie" in result
        assert "Tomates" in result
        assert "Lait" in result
        assert "☐" in result  # Checkbox

    def test_generer_liste_vide(self):
        """Génération sur liste vide."""
        result = generer_texte_impression([])

        assert "LISTE DE COURSES" in result
        # Ne devrait pas avoir de rayons

    def test_generer_titre_personnalise(self):
        """Génération avec titre personnalisé."""
        liste = [
            {
                "ingredient_nom": "Test",
                "quantite_necessaire": 1,
                "unite": "kg",
                "rayon_magasin": "Autre",
            }
        ]

        result = generer_texte_impression(liste, titre="MA LISTE")

        assert "MA LISTE" in result


class TestValiderArticleData:
    """Tests pour valider_article_data()."""

    def test_valider_donnees_valides(self):
        """Données valides."""
        data = {
            "ingredient_id": 1,
            "quantite_necessaire": 2.5,
            "priorite": "haute",
        }
        valid, msg = valider_article_data(data)

        assert valid is True
        assert msg == ""

    def test_valider_sans_ingredient_id(self):
        """Rejet sans ingredient_id."""
        data = {"quantite_necessaire": 1}
        valid, msg = valider_article_data(data)

        assert valid is False
        assert "ingrédient" in msg.lower()

    def test_valider_quantite_negative(self):
        """Rejet avec quantité négative."""
        data = {"ingredient_id": 1, "quantite_necessaire": -1}
        valid, msg = valider_article_data(data)

        assert valid is False
        assert "quantité" in msg.lower()

    def test_valider_quantite_zero(self):
        """Rejet avec quantité zéro."""
        data = {"ingredient_id": 1, "quantite_necessaire": 0}
        valid, msg = valider_article_data(data)

        assert valid is False

    def test_valider_priorite_invalide(self):
        """Rejet avec priorité invalide."""
        data = {"ingredient_id": 1, "quantite_necessaire": 1, "priorite": "urgente"}
        valid, msg = valider_article_data(data)

        assert valid is False
        assert "priorité" in msg.lower()

    def test_valider_sans_priorite(self):
        """Accepte sans priorité (optionnel)."""
        data = {"ingredient_id": 1, "quantite_necessaire": 1}
        valid, msg = valider_article_data(data)

        assert valid is True


class TestExtraireRayonsUniques:
    """Tests pour extraire_rayons_uniques()."""

    def test_extraire_rayons(self):
        """Extraction des rayons uniques."""
        liste = [
            {"rayon_magasin": "Fruits"},
            {"rayon_magasin": "Crèmerie"},
            {"rayon_magasin": "Fruits"},  # Doublon
            {"rayon_magasin": "Autre"},
        ]

        result = extraire_rayons_uniques(liste)

        assert len(result) == 3
        assert result == ["Autre", "Crèmerie", "Fruits"]  # Trié

    def test_extraire_avec_rayon_manquant(self):
        """Extraction avec rayons manquants."""
        liste = [
            {"ingredient_nom": "A"},
            {"rayon_magasin": "Fruits"},
        ]

        result = extraire_rayons_uniques(liste)

        assert "Autre" in result
        assert "Fruits" in result

    def test_extraire_liste_vide(self):
        """Extraction sur liste vide."""
        result = extraire_rayons_uniques([])
        assert result == []
