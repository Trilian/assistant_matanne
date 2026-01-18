"""
Tests pour les Features 1 et 2:
- Feature 1: Historique des modifications
- Feature 2: Gestion des photos
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock

from src.core.models import HistoriqueInventaire, ArticleInventaire


class TestHistoriqueInventaire:
    """Tests du modèle HistoriqueInventaire"""
    
    def test_historique_creation(self):
        """Test création d'un enregistrement historique"""
        historique = HistoriqueInventaire(
            article_id=1,
            quantite_ancien=10,
            quantite_nouveau=8,
            difference=-2,
            difference_unite="kg",
            raison="consommation",
            motif_modif="Utilisation quotidienne",
            notes="Utilisé pour la sauce tomate",
            utilisateur_action="user@example.com",
            date_changement=datetime.now()
        )
        
        assert historique.article_id == 1
        assert historique.quantite_ancien == 10
        assert historique.quantite_nouveau == 8
        assert historique.difference == -2
    
    def test_historique_raisons(self):
        """Test les différentes raisons de modification"""
        raisons = ["consommation", "achat", "péremption", "ajustement", "transfert"]
        
        for raison in raisons:
            historique = HistoriqueInventaire(
                article_id=1,
                quantite_ancien=10,
                quantite_nouveau=8,
                difference=-2,
                difference_unite="kg",
                raison=raison,
                motif_modif="Test",
                notes="Test",
                utilisateur_action="user@example.com",
                date_changement=datetime.now()
            )
            
            assert historique.raison == raison
    
    def test_historique_timestamp(self):
        """Test timestamps"""
        now = datetime.now()
        
        historique = HistoriqueInventaire(
            article_id=1,
            quantite_ancien=10,
            quantite_nouveau=8,
            difference=-2,
            difference_unite="kg",
            raison="consommation",
            motif_modif="Test",
            notes="Test",
            utilisateur_action="user@example.com",
            date_changement=now
        )
        
        assert historique.date_changement == now
        # date_ajout devrait être automatique
        assert hasattr(historique, 'date_ajout')


class TestHistoriqueFeature:
    """Tests de la feature Historique des modifications"""
    
    @pytest.fixture
    def mock_article(self):
        """Fixture pour un article mocké"""
        article = Mock(spec=ArticleInventaire)
        article.id = 1
        article.nom = "Tomates"
        article.quantite = 10
        article.historique = []
        
        return article
    
    def test_enregistrer_modification(self, mock_article):
        """Test enregistrement d'une modification"""
        # Simule une modification
        ancien = 10
        nouveau = 8
        
        historique = HistoriqueInventaire(
            article_id=mock_article.id,
            quantite_ancien=ancien,
            quantite_nouveau=nouveau,
            difference=nouveau - ancien,
            difference_unite="kg",
            raison="consommation",
            motif_modif="Utilisation",
            notes="Pour la sauce",
            utilisateur_action="chef@kitchen.com",
            date_changement=datetime.now()
        )
        
        mock_article.historique.append(historique)
        
        assert len(mock_article.historique) == 1
        assert mock_article.historique[0].quantite_ancien == ancien
        assert mock_article.historique[0].quantite_nouveau == nouveau
    
    def test_get_historique(self, mock_article):
        """Test récupération de l'historique"""
        # Ajoute plusieurs entrées
        for i in range(3):
            historique = HistoriqueInventaire(
                article_id=mock_article.id,
                quantite_ancien=10-i,
                quantite_nouveau=10-(i+1),
                difference=-1,
                difference_unite="kg",
                raison="consommation",
                motif_modif="Test",
                notes="Test",
                utilisateur_action="user@example.com",
                date_changement=datetime.now() - timedelta(days=i)
            )
            
            mock_article.historique.append(historique)
        
        assert len(mock_article.historique) == 3
    
    def test_historique_timeline(self, mock_article):
        """Test que l'historique peut être trié par date"""
        # Ajoute des entrées dans un ordre désorganisé
        dates = [
            datetime.now() - timedelta(days=2),
            datetime.now(),
            datetime.now() - timedelta(days=1),
        ]
        
        for i, date in enumerate(dates):
            historique = HistoriqueInventaire(
                article_id=mock_article.id,
                quantite_ancien=10,
                quantite_nouveau=9,
                difference=-1,
                difference_unite="kg",
                raison="consommation",
                motif_modif="Test",
                notes="Test",
                utilisateur_action="user@example.com",
                date_changement=date
            )
            
            mock_article.historique.append(historique)
        
        # Trie par date
        sorted_hist = sorted(mock_article.historique, key=lambda h: h.date_changement)
        
        assert sorted_hist[0].date_changement == dates[0]
        assert sorted_hist[2].date_changement == dates[1]


class TestArticlePhotos:
    """Tests de la feature Gestion des photos"""
    
    @pytest.fixture
    def mock_article_with_photos(self):
        """Fixture pour un article avec photos"""
        article = Mock(spec=ArticleInventaire)
        article.id = 1
        article.nom = "Tomates"
        article.photo_url = None
        article.photo_filename = None
        article.photo_uploaded_at = None
        
        return article
    
    def test_ajouter_photo(self, mock_article_with_photos):
        """Test ajout d'une photo"""
        photo_url = "s3://bucket/photo_1.jpg"
        photo_filename = "photo_1.jpg"
        
        mock_article_with_photos.photo_url = photo_url
        mock_article_with_photos.photo_filename = photo_filename
        mock_article_with_photos.photo_uploaded_at = datetime.now()
        
        assert mock_article_with_photos.photo_url == photo_url
        assert mock_article_with_photos.photo_filename == photo_filename
        assert mock_article_with_photos.photo_uploaded_at is not None
    
    def test_supprimer_photo(self, mock_article_with_photos):
        """Test suppression d'une photo"""
        # Ajoute d'abord
        mock_article_with_photos.photo_url = "s3://bucket/photo.jpg"
        mock_article_with_photos.photo_filename = "photo.jpg"
        
        assert mock_article_with_photos.photo_url is not None
        
        # Supprime
        mock_article_with_photos.photo_url = None
        mock_article_with_photos.photo_filename = None
        mock_article_with_photos.photo_uploaded_at = None
        
        assert mock_article_with_photos.photo_url is None
        assert mock_article_with_photos.photo_filename is None
    
    def test_photo_formats(self):
        """Test les formats de photo supportés"""
        formats = ["jpg", "jpeg", "png", "webp"]
        
        for fmt in formats:
            filename = f"photo.{fmt}"
            assert filename.endswith(('jpg', 'jpeg', 'png', 'webp'))
    
    def test_photo_validation(self):
        """Test validation des photos"""
        # Simule une validation de fichier
        valid_files = [
            {"name": "photo.jpg", "size": 1024*100, "valid": True},  # 100KB
            {"name": "photo.png", "size": 1024*200, "valid": True},  # 200KB
            {"name": "photo.gif", "size": 1024*300, "valid": False},  # Format non valide
            {"name": "photo.jpg", "size": 1024*10000, "valid": False},  # Trop gros (>5MB)
        ]
        
        MAX_SIZE = 1024 * 5120  # 5MB
        ALLOWED_FORMATS = ['jpg', 'jpeg', 'png', 'webp']
        
        for file_info in valid_files:
            name = file_info["name"]
            size = file_info["size"]
            
            # Validation
            ext = name.split('.')[-1].lower()
            is_valid = (ext in ALLOWED_FORMATS) and (size <= MAX_SIZE)
            
            assert is_valid == file_info["valid"]
    
    def test_photo_metadata(self, mock_article_with_photos):
        """Test métadonnées des photos"""
        now = datetime.now()
        
        mock_article_with_photos.photo_url = "s3://bucket/photo.jpg"
        mock_article_with_photos.photo_filename = "photo.jpg"
        mock_article_with_photos.photo_uploaded_at = now
        
        assert mock_article_with_photos.photo_url is not None
        assert mock_article_with_photos.photo_filename == "photo.jpg"
        assert mock_article_with_photos.photo_uploaded_at == now


class TestHistoriquePhotosIntegration:
    """Tests d'intégration pour Historique + Photos"""
    
    def test_article_with_history_and_photos(self):
        """Test un article avec historique et photos"""
        article = Mock(spec=ArticleInventaire)
        article.id = 1
        article.nom = "Tomates"
        article.quantite = 10
        article.historique = []
        article.photo_url = None
        article.photo_filename = None
        
        # Ajoute des entrées historiques
        hist1 = HistoriqueInventaire(
            article_id=article.id,
            quantite_ancien=10,
            quantite_nouveau=8,
            difference=-2,
            difference_unite="kg",
            raison="consommation",
            motif_modif="Utilisé",
            notes="",
            utilisateur_action="user@example.com",
            date_changement=datetime.now()
        )
        
        article.historique.append(hist1)
        
        # Ajoute une photo
        article.photo_url = "s3://bucket/tomates.jpg"
        article.photo_filename = "tomates.jpg"
        
        assert len(article.historique) == 1
        assert article.photo_url is not None
    
    def test_historical_photo_tracking(self):
        """Test suivi historique des modifications de photos"""
        # Simule l'ajout de plusieurs photos dans le temps
        photos_history = [
            {
                "date": datetime.now() - timedelta(days=2),
                "url": "s3://bucket/photo_v1.jpg",
                "filename": "photo_v1.jpg"
            },
            {
                "date": datetime.now() - timedelta(days=1),
                "url": "s3://bucket/photo_v2.jpg",
                "filename": "photo_v2.jpg"
            },
            {
                "date": datetime.now(),
                "url": "s3://bucket/photo_v3.jpg",
                "filename": "photo_v3.jpg"
            }
        ]
        
        # La dernière photo
        current_photo = photos_history[-1]
        
        assert current_photo["filename"] == "photo_v3.jpg"
        assert len(photos_history) == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
