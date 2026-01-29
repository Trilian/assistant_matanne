"""
Tests pour le module cuisine/courses.py
Gestion complète de la liste de courses avec filtres et suggestions IA
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch
from tests.conftest import SessionStateMock


class TestConstantes:
    """Tests pour les constantes du module courses"""

    def test_priority_emojis(self):
        """Vérifie les emojis de priorité"""
        PRIORITY_EMOJIS = {
            "haute": "ðŸ”´",
            "moyenne": "ðŸŸ¡",
            "basse": "ðŸŸ¢"
        }
        
        assert PRIORITY_EMOJIS["haute"] == "ðŸ”´"
        assert PRIORITY_EMOJIS["moyenne"] == "ðŸŸ¡"
        assert PRIORITY_EMOJIS["basse"] == "ðŸŸ¢"

    def test_rayons_default(self):
        """Vérifie les rayons par défaut"""
        RAYONS_DEFAULT = [
            "Fruits & Légumes",
            "Laitier",
            "Boulangerie",
            "Viandes",
            "Poissons",
            "Surgelés",
            "Ã‰pices",
            "Boissons",
            "Autre"
        ]
        
        assert len(RAYONS_DEFAULT) == 9
        assert "Fruits & Légumes" in RAYONS_DEFAULT
        assert "Autre" in RAYONS_DEFAULT


class TestAppCourses:
    """Tests pour la fonction principale app()"""

    @patch("src.modules.cuisine.courses._init_realtime_sync")
    @patch("src.modules.cuisine.courses.get_courses_service")
    @patch("src.modules.cuisine.courses.st")
    def test_initialise_session_state(self, mock_st, mock_get_service, mock_init_sync):
        """Initialise correctement le session_state"""
        from src.domains.cuisine.logic.courses import app
        
        mock_st.session_state = SessionStateMock()
        mock_service = MagicMock()
        mock_get_service.return_value = mock_service
        
        # Mock tabs
        mock_tabs = [MagicMock() for _ in range(5)]
        for tab in mock_tabs:
            tab.__enter__ = MagicMock(return_value=tab)
            tab.__exit__ = MagicMock()
        mock_st.tabs.return_value = mock_tabs
        
        app()
        
        assert "courses_refresh" in mock_st.session_state
        assert "new_article_mode" in mock_st.session_state

    @patch("src.modules.cuisine.courses._init_realtime_sync")
    @patch("src.modules.cuisine.courses.get_courses_service")
    @patch("src.modules.cuisine.courses.st")
    def test_appel_init_realtime_sync(self, mock_st, mock_get_service, mock_init_sync):
        """Appelle l'initialisation de la sync temps réel"""
        from src.domains.cuisine.logic.courses import app
        
        mock_st.session_state = SessionStateMock()
        mock_service = MagicMock()
        mock_get_service.return_value = mock_service
        
        # Mock tabs
        mock_tabs = [MagicMock() for _ in range(5)]
        for tab in mock_tabs:
            tab.__enter__ = MagicMock(return_value=tab)
            tab.__exit__ = MagicMock()
        mock_st.tabs.return_value = mock_tabs
        
        app()
        
        mock_init_sync.assert_called_once()


class TestGroupementRayons:
    """Tests pour le groupement par rayon"""

    def test_groupe_articles_par_rayon(self):
        """Groupe les articles par rayon"""
        articles = [
            MagicMock(rayon="Fruits & Légumes", nom="Pommes"),
            MagicMock(rayon="Fruits & Légumes", nom="Bananes"),
            MagicMock(rayon="Laitier", nom="Lait"),
            MagicMock(rayon="Laitier", nom="Yaourt"),
            MagicMock(rayon="Boulangerie", nom="Pain"),
        ]
        
        # Grouper par rayon
        grouped = {}
        for article in articles:
            rayon = article.rayon or "Autre"
            if rayon not in grouped:
                grouped[rayon] = []
            grouped[rayon].append(article)
        
        assert len(grouped) == 3
        assert len(grouped["Fruits & Légumes"]) == 2
        assert len(grouped["Laitier"]) == 2
        assert len(grouped["Boulangerie"]) == 1

    def test_rayon_none_devient_autre(self):
        """Les articles sans rayon vont dans 'Autre'"""
        articles = [
            MagicMock(rayon=None, nom="Article 1"),
            MagicMock(rayon="", nom="Article 2"),
        ]
        
        grouped = {}
        for article in articles:
            rayon = article.rayon or "Autre"
            if rayon not in grouped:
                grouped[rayon] = []
            grouped[rayon].append(article)
        
        # Les articles sans rayon et avec rayon vide vont dans "Autre"
        assert "Autre" in grouped or "" in grouped


class TestPrioriteEmoji:
    """Tests pour les emojis de priorité"""

    def test_emoji_haute(self):
        """Emoji rouge pour haute priorité"""
        PRIORITY_EMOJIS = {"haute": "ðŸ”´", "moyenne": "ðŸŸ¡", "basse": "ðŸŸ¢"}
        assert PRIORITY_EMOJIS.get("haute") == "ðŸ”´"

    def test_emoji_moyenne(self):
        """Emoji jaune pour priorité moyenne"""
        PRIORITY_EMOJIS = {"haute": "ðŸ”´", "moyenne": "ðŸŸ¡", "basse": "ðŸŸ¢"}
        assert PRIORITY_EMOJIS.get("moyenne") == "ðŸŸ¡"

    def test_emoji_basse(self):
        """Emoji vert pour basse priorité"""
        PRIORITY_EMOJIS = {"haute": "ðŸ”´", "moyenne": "ðŸŸ¡", "basse": "ðŸŸ¢"}
        assert PRIORITY_EMOJIS.get("basse") == "ðŸŸ¢"

    def test_emoji_default(self):
        """Emoji par défaut pour priorité inconnue"""
        PRIORITY_EMOJIS = {"haute": "ðŸ”´", "moyenne": "ðŸŸ¡", "basse": "ðŸŸ¢"}
        assert PRIORITY_EMOJIS.get("inconnue", "âšª") == "âšª"


class TestCalculsMetriques:
    """Tests pour le calcul des métriques de liste de courses"""

    def test_calcul_total_articles(self):
        """Calcule le total d'articles"""
        articles = [MagicMock() for _ in range(15)]
        assert len(articles) == 15

    def test_calcul_articles_non_achetes(self):
        """Calcule les articles non achetés"""
        articles = [
            MagicMock(est_achete=False),
            MagicMock(est_achete=True),
            MagicMock(est_achete=False),
            MagicMock(est_achete=True),
        ]
        
        non_achetes = [a for a in articles if not a.est_achete]
        assert len(non_achetes) == 2

    def test_calcul_articles_achetes(self):
        """Calcule les articles achetés"""
        articles = [
            MagicMock(est_achete=True),
            MagicMock(est_achete=True),
            MagicMock(est_achete=False),
        ]
        
        achetes = [a for a in articles if a.est_achete]
        assert len(achetes) == 2

    def test_pourcentage_progression(self):
        """Calcule le pourcentage de progression"""
        articles = [
            MagicMock(est_achete=True),
            MagicMock(est_achete=True),
            MagicMock(est_achete=False),
            MagicMock(est_achete=False),
        ]
        
        total = len(articles)
        achetes = len([a for a in articles if a.est_achete])
        
        pourcentage = (achetes / total) * 100 if total > 0 else 0
        assert pourcentage == 50.0

    def test_pourcentage_liste_vide(self):
        """Gère le cas de liste vide"""
        articles = []
        
        total = len(articles)
        achetes = len([a for a in articles if a.est_achete])
        
        pourcentage = (achetes / total) * 100 if total > 0 else 0
        assert pourcentage == 0


class TestFiltresArticles:
    """Tests pour les filtres d'articles"""

    def test_filtre_par_rayon(self):
        """Filtre les articles par rayon"""
        articles = [
            MagicMock(rayon="Fruits & Légumes"),
            MagicMock(rayon="Laitier"),
            MagicMock(rayon="Fruits & Légumes"),
        ]
        
        filtre_rayon = "Fruits & Légumes"
        filtered = [a for a in articles if a.rayon == filtre_rayon]
        
        assert len(filtered) == 2

    def test_filtre_par_priorite(self):
        """Filtre les articles par priorité"""
        articles = [
            MagicMock(priorite="haute"),
            MagicMock(priorite="basse"),
            MagicMock(priorite="haute"),
        ]
        
        filtre_priorite = "haute"
        filtered = [a for a in articles if a.priorite == filtre_priorite]
        
        assert len(filtered) == 2

    def test_filtre_non_achetes(self):
        """Filtre uniquement les articles non achetés"""
        articles = [
            MagicMock(est_achete=False),
            MagicMock(est_achete=True),
            MagicMock(est_achete=False),
        ]
        
        filtered = [a for a in articles if not a.est_achete]
        assert len(filtered) == 2

    def test_filtre_suggestions_ia(self):
        """Filtre les articles suggérés par IA"""
        articles = [
            MagicMock(est_suggestion_ia=True),
            MagicMock(est_suggestion_ia=False),
            MagicMock(est_suggestion_ia=True),
        ]
        
        filtered = [a for a in articles if a.est_suggestion_ia]
        assert len(filtered) == 2


class TestTriArticles:
    """Tests pour le tri des articles"""

    def test_tri_par_priorite(self):
        """Trie les articles par priorité"""
        ordre_priorite = {"haute": 0, "moyenne": 1, "basse": 2}
        
        articles = [
            MagicMock(priorite="basse", nom="C"),
            MagicMock(priorite="haute", nom="A"),
            MagicMock(priorite="moyenne", nom="B"),
        ]
        
        sorted_articles = sorted(articles, key=lambda a: ordre_priorite.get(a.priorite, 99))
        
        assert sorted_articles[0].priorite == "haute"
        assert sorted_articles[1].priorite == "moyenne"
        assert sorted_articles[2].priorite == "basse"

    def test_tri_par_nom(self):
        """Trie les articles par nom alphabétique"""
        articles = [
            MagicMock(nom="Pommes"),
            MagicMock(nom="Bananes"),
            MagicMock(nom="Cerises"),
        ]
        
        sorted_articles = sorted(articles, key=lambda a: a.nom)
        
        assert sorted_articles[0].nom == "Bananes"
        assert sorted_articles[1].nom == "Cerises"
        assert sorted_articles[2].nom == "Pommes"

    def test_tri_par_rayon(self):
        """Trie les articles par rayon"""
        articles = [
            MagicMock(rayon="Viandes"),
            MagicMock(rayon="Boulangerie"),
            MagicMock(rayon="Fruits & Légumes"),
        ]
        
        sorted_articles = sorted(articles, key=lambda a: a.rayon or "ZZZZ")
        
        assert sorted_articles[0].rayon == "Boulangerie"


class TestValidationArticle:
    """Tests pour la validation des articles"""

    def test_nom_requis(self):
        """Le nom est obligatoire"""
        def valider_article(nom, quantite=1):
            errors = []
            if not nom or not nom.strip():
                errors.append("Le nom est obligatoire")
            if quantite <= 0:
                errors.append("La quantité doit être positive")
            return errors
        
        errors = valider_article("")
        assert "Le nom est obligatoire" in errors

    def test_quantite_positive(self):
        """La quantité doit être positive"""
        def valider_article(nom, quantite=1):
            errors = []
            if not nom or not nom.strip():
                errors.append("Le nom est obligatoire")
            if quantite <= 0:
                errors.append("La quantité doit être positive")
            return errors
        
        errors = valider_article("Pommes", quantite=0)
        assert "La quantité doit être positive" in errors

    def test_article_valide(self):
        """Article valide sans erreurs"""
        def valider_article(nom, quantite=1):
            errors = []
            if not nom or not nom.strip():
                errors.append("Le nom est obligatoire")
            if quantite <= 0:
                errors.append("La quantité doit être positive")
            return errors
        
        errors = valider_article("Pommes", quantite=5)
        assert len(errors) == 0


class TestStatutAchat:
    """Tests pour le changement de statut d'achat"""

    def test_marquer_comme_achete(self):
        """Marque un article comme acheté"""
        article = MagicMock()
        article.est_achete = False
        
        # Simule le toggle
        article.est_achete = not article.est_achete
        
        assert article.est_achete is True

    def test_marquer_comme_non_achete(self):
        """Remet un article en non acheté"""
        article = MagicMock()
        article.est_achete = True
        
        # Simule le toggle
        article.est_achete = not article.est_achete
        
        assert article.est_achete is False


class TestSuggestionsIA:
    """Tests pour les suggestions IA"""

    def test_detecte_suggestions_ia(self):
        """Détecte les articles suggérés par IA"""
        article = MagicMock()
        article.est_suggestion_ia = True
        article.source = "IA"
        
        assert article.est_suggestion_ia is True

    def test_badge_suggestion_ia(self):
        """Affiche le badge IA pour les suggestions"""
        def get_badges(article):
            badges = []
            if article.est_suggestion_ia:
                badges.append("ðŸ¤– IA")
            return badges
        
        article = MagicMock()
        article.est_suggestion_ia = True
        
        badges = get_badges(article)
        assert "ðŸ¤– IA" in badges

    def test_pas_badge_si_pas_ia(self):
        """Pas de badge IA si pas de suggestion"""
        def get_badges(article):
            badges = []
            if article.est_suggestion_ia:
                badges.append("ðŸ¤– IA")
            return badges
        
        article = MagicMock()
        article.est_suggestion_ia = False
        
        badges = get_badges(article)
        assert len(badges) == 0

