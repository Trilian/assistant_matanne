"""
Exceptions Personnalisées
Système d'exceptions unifié pour toute l'application
"""
from typing import Optional, Dict, Any


class AppException(Exception):
    """
    Exception de base de l'application

    Toutes les exceptions custom héritent de celle-ci
    """

    def __init__(
            self,
            message: str,
            details: Optional[Dict[str, Any]] = None,
            user_message: Optional[str] = None
    ):
        """
        Args:
            message: Message technique (logs)
            details: Dict avec contexte additionnel
            user_message: Message friendly pour l'utilisateur
        """
        self.message = message
        self.details = details or {}
        self.user_message = user_message or message
        super().__init__(message)

    def to_dict(self) -> Dict[str, Any]:
        """Convertit en dict pour logs/API"""
        return {
            "type": self.__class__.__name__,
            "message": self.message,
            "user_message": self.user_message,
            "details": self.details
        }


class ValidationError(AppException):
    """
    Erreur de validation de données

    Usage:
        if not nom:
            raise ValidationError(
                "Nom manquant",
                details={"field": "nom"},
                user_message="Le nom est obligatoire"
            )
    """
    pass


class NotFoundError(AppException):
    """
    Ressource introuvable

    Usage:
        recette = db.query(Recette).get(id)
        if not recette:
            raise NotFoundError(
                f"Recette {id} non trouvée",
                details={"recette_id": id},
                user_message="Cette recette n'existe pas"
            )
    """
    pass


class DatabaseError(AppException):
    """
    Erreur base de données

    Usage:
        try:
            db.commit()
        except SQLAlchemyError as e:
            raise DatabaseError(
                f"Erreur DB: {e}",
                details={"operation": "commit"},
                user_message="Erreur de sauvegarde, réessaie"
            )
    """
    pass


class AIServiceError(AppException):
    """
    Erreur service IA (Mistral API)

    Usage:
        if response.status_code != 200:
            raise AIServiceError(
                f"API error: {response.status_code}",
                details={"status": response.status_code},
                user_message="L'IA est temporairement indisponible"
            )
    """
    pass


class RateLimitError(AppException):
    """
    Rate limit dépassé

    Usage:
        if not RateLimiter.can_call():
            raise RateLimitError(
                "Rate limit atteint",
                details={"calls_today": 100},
                user_message="Limite d'appels IA atteinte, réessaie dans 1h"
            )
    """
    pass


class AuthorizationError(AppException):
    """
    Erreur d'autorisation

    Usage:
        if not user.can_delete(recette):
            raise AuthorizationError(
                "User cannot delete this recipe",
                user_message="Tu n'as pas les droits pour supprimer"
            )
    """
    pass


class BusinessLogicError(AppException):
    """
    Erreur de logique métier

    Usage:
        if stock.quantite < 0:
            raise BusinessLogicError(
                "Stock négatif détecté",
                details={"stock_id": stock.id, "quantite": stock.quantite},
                user_message="Impossible d'avoir un stock négatif"
            )
    """
    pass


class ExternalServiceError(AppException):
    """
    Erreur service externe (météo, scraping, etc.)

    Usage:
        if not weather_data:
            raise ExternalServiceError(
                "API météo timeout",
                details={"service": "OpenWeatherMap"},
                user_message="Impossible de récupérer la météo"
            )
    """
    pass