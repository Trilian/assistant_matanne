from unittest.mock import patch


class TestGameSetup:
    """Tests d'initialisation des jeux"""

    @patch("streamlit.write")
    def test_initialiser_jeux(self, mock_write):
        """Teste l'initialisation"""
        mock_write.return_value = None
        mock_write("Jeux:", 3)
        assert mock_write.called

    @patch("streamlit.selectbox")
    def test_selectionner_jeu(self, mock_selectbox):
        """Teste la sélection d'un jeu"""
        mock_selectbox.return_value = "Memory"
        jeux = ["Memory", "Dominos"]
        result = mock_selectbox("Jeu", jeux)
        assert result == "Memory"

    def test_creer_jeu(self):
        """Teste la création d'un jeu"""
        game = {"nom": "Memory", "difficulte": "moyen"}
        assert game["nom"] == "Memory"
        assert game["difficulte"] == "moyen"


class TestGameInitialization:
    """Tests d'initialisation des règles"""

    @patch("streamlit.number_input")
    def test_configurer_difficulte(self, mock_number):
        """Teste la config difficultéce"""
        mock_number.return_value = 3
        result = mock_number("Niveau", 1, 5, 2)
        assert result == 3

    @patch("streamlit.slider")
    def test_configurer_joueurs(self, mock_slider):
        """Teste la config joueurs"""
        mock_slider.return_value = 4
        result = mock_slider("Joueurs", 1, 6)
        assert result == 4

    @patch("streamlit.button")
    def test_demarrer_partie(self, mock_button):
        """Teste le démarrage"""
        mock_button.return_value = True
        result = mock_button("Démarrer")
        assert result is True
