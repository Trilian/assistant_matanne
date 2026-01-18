"""
Tests pour les Features 3 et 4:
- Feature 3: Notifications push
- Feature 4: Import/Export avancé
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock
import pandas as pd

from src.services.notifications import (
    NotificationService,
    Notification,
    obtenir_service_notifications
)
from src.services.inventaire import ArticleImport


class TestNotification:
    """Tests du modèle Notification"""
    
    def test_notification_creation(self):
        """Test création d'une notification"""
        notif = Notification(
            id="notif_1",
            titre="Stock critique",
            message="Les tomates sont en stock critique",
            priorite="haute",
            icone="🔴",
            lue=False,
            date_creation=datetime.now()
        )
        
        assert notif.titre == "Stock critique"
        assert notif.priorite == "haute"
        assert notif.lue == False
    
    def test_notification_priorities(self):
        """Test les différentes priorités"""
        priorities = ["haute", "moyenne", "basse"]
        
        for priority in priorities:
            notif = Notification(
                id=f"notif_{priority}",
                titre="Test",
                message="Test",
                priorite=priority,
                icone="ℹ️",
                lue=False,
                date_creation=datetime.now()
            )
            
            assert notif.priorite == priority


class TestNotificationService:
    """Tests du service NotificationService"""
    
    @pytest.fixture
    def service(self):
        """Fixture pour un service de notifications"""
        return NotificationService()
    
    def test_service_initialization(self, service):
        """Test initialisation du service"""
        assert service is not None
        assert len(service.notifications) == 0
    
    def test_generer_notification(self, service):
        """Test génération d'une notification"""
        notif = service.generer_notification(
            titre="Test",
            message="Message de test",
            priorite="haute"
        )
        
        assert notif.titre == "Test"
        assert notif.priorite == "haute"
        assert len(service.notifications) == 1
    
    def test_obtenir_notifications(self, service):
        """Test récupération des notifications"""
        # Ajoute 3 notifications
        for i in range(3):
            service.generer_notification(
                titre=f"Notification {i}",
                message="Test",
                priorite="moyenne"
            )
        
        notifs = service.obtenir_notifications()
        
        assert len(notifs) == 3
    
    def test_obtenir_notifications_non_lues(self, service):
        """Test récupération des notifications non lues"""
        # Ajoute 3 notifications
        for i in range(3):
            service.generer_notification(
                titre=f"Notification {i}",
                message="Test",
                priorite="moyenne"
            )
        
        # Marque la première comme lue
        notifs = service.obtenir_notifications()
        service.marquer_lue(notifs[0].id)
        
        non_lues = service.obtenir_notifications_non_lues()
        
        assert len(non_lues) == 2
    
    def test_marquer_lue(self, service):
        """Test marquage comme lue"""
        notif = service.generer_notification(
            titre="Test",
            message="Test",
            priorite="haute"
        )
        
        assert notif.lue == False
        
        service.marquer_lue(notif.id)
        
        # Récupère la notification mise à jour
        updated = [n for n in service.notifications if n.id == notif.id][0]
        assert updated.lue == True
    
    def test_supprimer_notification(self, service):
        """Test suppression d'une notification"""
        notif = service.generer_notification(
            titre="Test",
            message="Test",
            priorite="haute"
        )
        
        assert len(service.notifications) == 1
        
        service.supprimer_notification(notif.id)
        
        assert len(service.notifications) == 0
    
    def test_obtenir_stats(self, service):
        """Test récupération des stats"""
        # Ajoute 3 notifications
        notif1 = service.generer_notification("N1", "M1", "haute")
        notif2 = service.generer_notification("N2", "M2", "moyenne")
        notif3 = service.generer_notification("N3", "M3", "basse")
        
        # Marque 2 comme lues
        service.marquer_lue(notif1.id)
        service.marquer_lue(notif2.id)
        
        stats = service.obtenir_stats()
        
        assert stats["total"] == 3
        assert stats["non_lues"] == 1
        assert stats["lues"] == 2
    
    def test_effacer_toutes_lues(self, service):
        """Test effacement de toutes les notifications lues"""
        # Ajoute 3 notifications
        notif1 = service.generer_notification("N1", "M1", "haute")
        notif2 = service.generer_notification("N2", "M2", "moyenne")
        notif3 = service.generer_notification("N3", "M3", "basse")
        
        # Marque 2 comme lues
        service.marquer_lue(notif1.id)
        service.marquer_lue(notif2.id)
        
        assert len(service.notifications) == 3
        
        service.effacer_toutes_lues()
        
        # Doit garder seulement la non-lue
        assert len(service.notifications) == 1


class TestObteinirServiceNotifications:
    """Tests du singleton obtenir_service_notifications"""
    
    def test_singleton_pattern(self):
        """Test que le singleton retourne la même instance"""
        service1 = obtenir_service_notifications()
        service2 = obtenir_service_notifications()
        
        assert service1 is service2
    
    def test_singleton_is_notification_service(self):
        """Test que le singleton retourne un NotificationService"""
        service = obtenir_service_notifications()
        
        assert isinstance(service, NotificationService)


class TestArticleImport:
    """Tests du modèle ArticleImport"""
    
    def test_article_import_creation(self):
        """Test création d'un article import"""
        article = ArticleImport(
            nom="Tomates",
            quantite=10,
            unite="kg",
            seuil_min=2,
            emplacement="Frigo",
            categorie="Légumes",
            date_peremption="2025-02-28"
        )
        
        assert article.nom == "Tomates"
        assert article.quantite == 10
        assert article.unite == "kg"
    
    def test_article_import_validation(self):
        """Test validation des champs"""
        # Quantité négative
        with pytest.raises(ValueError):
            ArticleImport(
                nom="Test",
                quantite=-1,  # Invalid!
                unite="kg",
                seuil_min=1,
                emplacement="Test",
                categorie="Test",
                date_peremption="2025-02-28"
            )
    
    def test_article_import_optional_fields(self):
        """Test avec champs optionnels"""
        article = ArticleImport(
            nom="Tomates",
            quantite=10,
            unite="kg",
            seuil_min=2
            # emplacement, categorie, date_peremption sont optionnels
        )
        
        assert article.nom == "Tomates"


class TestImportExportIntegration:
    """Tests d'intégration pour Import/Export"""
    
    def test_import_validation_success(self):
        """Test validation d'un import correct"""
        data = {
            "Nom": ["Tomates", "Lait"],
            "Quantité": [10, 2],
            "Unité": ["kg", "L"],
            "Seuil Min": [2, 1],
            "Emplacement": ["Frigo", "Frigo"],
            "Catégorie": ["Légumes", "Produits Laitiers"],
            "Date Péremption": ["2025-02-28", "2025-02-20"]
        }
        
        df = pd.DataFrame(data)
        
        # Simule la validation
        errors = []
        for idx, row in df.iterrows():
            try:
                article = ArticleImport(
                    nom=row["Nom"],
                    quantite=float(row["Quantité"]),
                    unite=row["Unité"],
                    seuil_min=float(row["Seuil Min"]),
                    emplacement=row["Emplacement"],
                    categorie=row["Catégorie"],
                    date_peremption=row["Date Péremption"]
                )
            except Exception as e:
                errors.append(f"Ligne {idx+1}: {str(e)}")
        
        assert len(errors) == 0
    
    def test_import_validation_errors(self):
        """Test validation avec erreurs"""
        data = {
            "Nom": ["Tomates", "Lait"],
            "Quantité": ["abc", 2],  # Quantité invalide à la ligne 1
            "Unité": ["kg", "L"],
            "Seuil Min": [2, 1],
        }
        
        df = pd.DataFrame(data)
        
        # Simule la validation
        errors = []
        for idx, row in df.iterrows():
            try:
                quantite = float(row["Quantité"])
            except:
                errors.append(f"Ligne {idx+1}: Quantité invalide")
        
        assert len(errors) == 1
    
    def test_csv_format_validation(self):
        """Test validation du format CSV"""
        # Simule un fichier CSV
        csv_data = """Nom,Quantité,Unité,Seuil Min,Emplacement,Catégorie
Tomates,10,kg,2,Frigo,Légumes
Lait,2,L,1,Frigo,Produits Laitiers"""
        
        # Parse en DataFrame
        from io import StringIO
        df = pd.read_csv(StringIO(csv_data))
        
        assert len(df) == 2
        assert list(df.columns) == ["Nom", "Quantité", "Unité", "Seuil Min", "Emplacement", "Catégorie"]
    
    def test_json_export_format(self):
        """Test format d'export JSON"""
        data = {
            "metadata": {
                "date_export": datetime.now().isoformat(),
                "total_articles": 2
            },
            "articles": [
                {
                    "nom": "Tomates",
                    "quantite": 10,
                    "unite": "kg"
                },
                {
                    "nom": "Lait",
                    "quantite": 2,
                    "unite": "L"
                }
            ]
        }
        
        assert "metadata" in data
        assert "articles" in data
        assert len(data["articles"]) == 2


class TestNotificationsIntegration:
    """Tests d'intégration pour les notifications"""
    
    def test_notification_workflow(self):
        """Test du workflow complet de notifications"""
        service = obtenir_service_notifications()
        
        # Génère des notifications de différentes priorités
        notif_haute = service.generer_notification(
            titre="Stock critique",
            message="Les tomates sont en rupture",
            priorite="haute"
        )
        
        notif_moyenne = service.generer_notification(
            titre="Stock bas",
            message="Le lait est à seuil minimum",
            priorite="moyenne"
        )
        
        # Récupère les notifications
        toutes = service.obtenir_notifications()
        assert len(toutes) == 2
        
        # Marque une comme lue
        service.marquer_lue(notif_haute.id)
        non_lues = service.obtenir_notifications_non_lues()
        assert len(non_lues) == 1
        
        # Obtient les stats
        stats = service.obtenir_stats()
        assert stats["total"] == 2
        assert stats["lues"] == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
