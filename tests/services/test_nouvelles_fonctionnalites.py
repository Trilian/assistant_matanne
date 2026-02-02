"""
Tests pour les nouvelles fonctionnalités:
- Scan factures OCR
- Courses intelligentes
- Notifications push
"""

import pytest
from datetime import date
from unittest.mock import Mock, patch, AsyncMock

# ═══════════════════════════════════════════════════════════
# TESTS SERVICE OCR FACTURES
# ═══════════════════════════════════════════════════════════

class TestFactureOCRService:
    """Tests pour le service OCR factures."""
    
    def test_parser_reponse_valid_json(self):
        """Test parsing d'une réponse JSON valide."""
        from src.services.facture_ocr import FactureOCRService
        
        service = FactureOCRService()
        
        reponse = '''
        {
            "fournisseur": "EDF",
            "type_energie": "electricite",
            "montant_ttc": 125.50,
            "consommation": 450,
            "unite_consommation": "kWh",
            "mois_facturation": 3,
            "annee_facturation": 2024
        }
        '''
        
        donnees = service._parser_reponse(reponse)
        
        assert donnees.fournisseur == "EDF"
        assert donnees.type_energie == "electricite"
        assert donnees.montant_ttc == 125.50
        assert donnees.consommation == 450
    
    def test_parser_reponse_markdown_wrapper(self):
        """Test parsing avec wrapper markdown."""
        from src.services.facture_ocr import FactureOCRService
        
        service = FactureOCRService()
        
        reponse = '''```json
{
    "fournisseur": "Engie",
    "type_energie": "gaz",
    "montant_ttc": 89.90
}
```'''
        
        donnees = service._parser_reponse(reponse)
        
        assert donnees.fournisseur == "Engie"
        assert donnees.type_energie == "gaz"
    
    def test_parser_reponse_invalid_json(self):
        """Test parsing d'une réponse JSON invalide."""
        from src.services.facture_ocr import FactureOCRService
        
        service = FactureOCRService()
        
        reponse = "Ceci n'est pas du JSON"
        
        donnees = service._parser_reponse(reponse)
        
        # Doit retourner des valeurs par défaut
        assert donnees.fournisseur == "Inconnu"
        assert len(donnees.erreurs) > 0
    
    def test_calcul_confiance(self):
        """Test du calcul du score de confiance."""
        from src.services.facture_ocr import FactureOCRService
        
        service = FactureOCRService()
        
        # Réponse complète = haute confiance
        reponse_complete = '''
        {
            "fournisseur": "EDF",
            "type_energie": "electricite",
            "montant_ttc": 125.50,
            "consommation": 450
        }
        '''
        donnees = service._parser_reponse(reponse_complete)
        assert donnees.confiance >= 0.7
        
        # Réponse partielle = confiance moyenne
        reponse_partielle = '''
        {
            "fournisseur": "Inconnu",
            "type_energie": "autre",
            "montant_ttc": 0
        }
        '''
        donnees_partiel = service._parser_reponse(reponse_partielle)
        assert donnees_partiel.confiance < 0.5


# ═══════════════════════════════════════════════════════════
# TESTS SERVICE COURSES INTELLIGENTES
# ═══════════════════════════════════════════════════════════

class TestCoursesIntelligentesService:
    """Tests pour le service courses intelligentes."""
    
    def test_determiner_rayon(self):
        """Test détermination du rayon par ingrédient."""
        from src.services.courses_intelligentes import CoursesIntelligentesService
        
        # Mock le client IA pour éviter l'erreur
        with patch('src.services.courses_intelligentes.obtenir_client_ia') as mock_client:
            mock_client.return_value = Mock()
            service = CoursesIntelligentesService()
        
        assert service._determiner_rayon("Tomates cerises") == "Fruits & Légumes"
        assert service._determiner_rayon("Poulet rôti") == "Boucherie"
        assert service._determiner_rayon("Saumon fumé") == "Poissonnerie"
        assert service._determiner_rayon("Lait entier") == "Crèmerie"
        assert service._determiner_rayon("Pâtes") == "Épicerie"
        assert service._determiner_rayon("Inconnu") == "Autre"
    
    def test_determiner_priorite(self):
        """Test détermination de priorité par rayon."""
        from src.services.courses_intelligentes import CoursesIntelligentesService
        
        with patch('src.services.courses_intelligentes.obtenir_client_ia') as mock_client:
            mock_client.return_value = Mock()
            service = CoursesIntelligentesService()
        
        # Viandes/poissons = haute priorité (périssables)
        assert service._determiner_priorite("Boucherie") == 1
        assert service._determiner_priorite("Poissonnerie") == 1
        
        # Épicerie = basse priorité (se conserve)
        assert service._determiner_priorite("Épicerie") == 3
    
    def test_comparer_avec_stock(self):
        """Test comparaison besoins vs stock."""
        from src.services.courses_intelligentes import CoursesIntelligentesService, ArticleCourse
        
        with patch('src.services.courses_intelligentes.obtenir_client_ia') as mock_client:
            mock_client.return_value = Mock()
            service = CoursesIntelligentesService()
        
        articles = [
            ArticleCourse(nom="Tomates", quantite=500, unite="g", rayon="Légumes", priorite=2),
            ArticleCourse(nom="Lait", quantite=2, unite="L", rayon="Crèmerie", priorite=1),
            ArticleCourse(nom="Pâtes", quantite=1, unite="paquet", rayon="Épicerie", priorite=3),
        ]
        
        stock = {
            "tomates": 200,  # Moins que nécessaire
            "lait": 3,       # Plus que nécessaire
        }
        
        resultat = service.comparer_avec_stock(articles, stock)
        
        # Tomates: besoin 500, stock 200 -> acheter 300
        # Lait: besoin 2, stock 3 -> rien à acheter (filtré)
        # Pâtes: besoin 1, stock 0 -> acheter 1
        
        assert len(resultat) == 2  # Tomates et Pâtes
        assert any(a.nom == "Tomates" and a.a_acheter == 300 for a in resultat)
        assert any(a.nom == "Pâtes" and a.a_acheter == 1 for a in resultat)


# ═══════════════════════════════════════════════════════════
# TESTS SERVICE NOTIFICATIONS PUSH
# ═══════════════════════════════════════════════════════════

class TestNotificationPushService:
    """Tests pour le service notifications push."""
    
    def test_config_par_defaut(self):
        """Test configuration par défaut."""
        from src.services.notifications_push import NotificationPushConfig
        
        config = NotificationPushConfig()
        
        assert config.topic == "matanne-famille"
        assert config.actif == True
        assert config.rappels_taches == True
        assert config.heure_digest == 8
    
    def test_config_personnalisee(self):
        """Test configuration personnalisée."""
        from src.services.notifications_push import NotificationPushConfig
        
        config = NotificationPushConfig(
            topic="ma-famille-2024",
            actif=False,
            heure_digest=20
        )
        
        assert config.topic == "ma-famille-2024"
        assert config.actif == False
        assert config.heure_digest == 20
    
    def test_get_urls(self):
        """Test génération des URLs."""
        from src.services.notifications_push import get_notification_push_service, NotificationPushConfig
        
        config = NotificationPushConfig(topic="test-topic")
        service = get_notification_push_service(config)
        
        assert service.get_subscribe_url() == "ntfy://test-topic"
        assert service.get_web_url() == "https://ntfy.sh/test-topic"
        assert "test-topic" in service.get_subscribe_qr_url()
    
    def test_envoi_desactive(self):
        """Test qu'aucun envoi n'est fait si désactivé."""
        import asyncio
        from src.services.notifications_push import (
            get_notification_push_service, 
            NotificationPushConfig,
            NotificationPush
        )
        
        config = NotificationPushConfig(actif=False)
        service = get_notification_push_service(config)
        
        notification = NotificationPush(
            titre="Test",
            message="Message test"
        )
        
        resultat = asyncio.run(service.envoyer(notification))
        
        assert resultat.succes == False
        assert "désactivées" in resultat.message
    
    def test_creation_notification(self):
        """Test création d'une notification."""
        from src.services.notifications_push import NotificationPush
        
        notif = NotificationPush(
            titre="Alerte tâche",
            message="Nettoyer garage",
            priorite=4,
            tags=["warning", "calendar"]
        )
        
        assert notif.titre == "Alerte tâche"
        assert notif.priorite == 4
        assert "warning" in notif.tags


# ═══════════════════════════════════════════════════════════
# TESTS UI SCAN FACTURES
# ═══════════════════════════════════════════════════════════

class TestScanFacturesUI:
    """Tests pour l'UI scan factures."""
    
    def test_mois_fr_mapping(self):
        """Test mapping des mois français."""
        from src.domains.maison.ui.scan_factures import MOIS_FR
        
        assert MOIS_FR[1] == "Janvier"
        assert MOIS_FR[6] == "Juin"
        assert MOIS_FR[12] == "Décembre"
    
    def test_fournisseurs_connus(self):
        """Test dictionnaire des fournisseurs."""
        from src.domains.maison.ui.scan_factures import FOURNISSEURS_CONNUS
        
        assert "EDF" in FOURNISSEURS_CONNUS
        assert FOURNISSEURS_CONNUS["EDF"]["type"] == "electricite"
        assert FOURNISSEURS_CONNUS["VEOLIA"]["type"] == "eau"


# ═══════════════════════════════════════════════════════════
# TESTS UI NOTIFICATIONS PUSH
# ═══════════════════════════════════════════════════════════

class TestNotificationsPushUI:
    """Tests pour l'UI notifications push."""
    
    def test_help_text(self):
        """Test présence du texte d'aide."""
        from src.domains.utils.ui.notifications_push import HELP_NTFY
        
        assert "ntfy.sh" in HELP_NTFY
        assert "gratuit" in HELP_NTFY.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
