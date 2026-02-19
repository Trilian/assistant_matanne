"""
Services - Package des services métier.

Ce package contient tous les services de l'application.
Importez directement depuis les sous-packages:

    # Base
    from src.services.core.base import BaseService, BaseAIService

    # Recettes
    from src.services.cuisine.recettes import ServiceRecettes, obtenir_service_recettes

    # Inventaire
    from src.services.inventaire import ServiceInventaire, obtenir_service_inventaire

    # Courses
    from src.services.cuisine.courses import ServiceCourses, obtenir_service_courses

    # Planning
    from src.services.cuisine.planning import ServicePlanning, obtenir_service_planning

    # Utilisateur (auth, historique)
    from src.services.core.utilisateur import AuthService, get_auth_service

    # Intégrations (barcode, OCR, OpenFoodFacts)
    from src.services.integrations import BarcodeService, get_barcode_service

    # Backup
    from src.services.core.backup import ServiceBackup, obtenir_service_backup

    # Weather
    from src.services.integrations.weather import ServiceMeteo, obtenir_service_meteo

    # Web (PWA, synchronisation)
    from src.services.integrations.web import RealtimeSyncService
"""
