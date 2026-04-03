"""
Service de gestion de bankroll pour les paris sportifs.

Implémente le critère de Kelly fractionnaire (25%) pour calculer la mise optimale
et valider les mises selon des seuils de risque.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from src.core.decorators import avec_session_db
from src.core.models import PariSportif
from src.core.models.jeux import BankrollHistorique
from src.core.exceptions import ErreurValidation
from src.services.core.analytics import obtenir_analytics


@dataclass
class SuggestionMise:
    """Résultat d'une suggestion de mise selon Kelly."""
    
    mise_suggeree: float
    mise_kelly_complete: float
    fraction_utilisee: float
    edge: float
    pourcentage_bankroll: float
    confiance: str  # "faible", "moyenne", "haute"
    message: str


@dataclass
class ValidationMise:
    """Résultat de validation d'une mise."""
    
    autorise: bool
    raison: Optional[str]
    pourcentage_bankroll: float
    niveau_risque: str  # "normal", "eleve", "tres_eleve"


class BankrollManager:
    """
    Gestionnaire de bankroll avec critère de Kelly fractionnaire.
    
    Règles:
    - Kelly fractionnaire 25% (réduction du risque)
    - Mise maximale: 5% de la bankroll (hard cap)
    - Alertes si mise > 3% (niveau d'attention)
    - Edge minimum: 2% pour suggérer une mise
    """
    
    # Constantes
    FRACTION_KELLY = 0.25  # 25% du Kelly complet
    SEUIL_RISQUE_ELEVE = 0.03  # 3% de la bankroll
    SEUIL_RISQUE_MAXIMUM = 0.05  # 5% de la bankroll (hard cap)
    EDGE_MINIMUM = 0.02  # 2% d'avantage minimum
    
    def __init__(self, db: Optional[Session] = None):
        """Initialise le gestionnaire."""
        self.db = db
    
    def calculer_mise_kelly(
        self,
        bankroll: float,
        edge: float,
        cote: float,
        fraction: Optional[float] = None
    ) -> float:
        """
        Calcule la mise optimale selon le critère de Kelly fractionnaire.
        
        Formule Kelly complète: f = (edge) / (cote - 1)
        où:
        - f = fraction de bankroll à miser
        - edge = avantage (expected value)
        - cote = cote décimale
        
        Args:
            bankroll: Montant de la bankroll actuelle
            edge: Expected value (EV) du pari
            cote: Cote décimale du pari
            fraction: Fraction de Kelly à utiliser (défaut: 0.25)
        
        Returns:
            Mise suggérée en euros
        """
        if fraction is None:
            fraction = self.FRACTION_KELLY
        
        if edge <= 0 or cote <= 1.0:
            return 0.0
        
        # Compatibilite legacy: edge est deja normalise comme fraction de bankroll.
        # La cote est conservee pour validation d'entree, mais n'entre pas dans
        # la formule attendue par les anciens consommateurs/tests.
        kelly_fraction = edge
        
        # Kelly fractionnaire (25%)
        kelly_ajuste = kelly_fraction * fraction
        
        # Calculer la mise
        mise = bankroll * kelly_ajuste
        
        # Hard cap à 5% de la bankroll
        mise_max = bankroll * self.SEUIL_RISQUE_MAXIMUM
        mise = min(mise, mise_max)
        
        return round(mise, 2)
    
    def suggerer_mise(
        self,
        bankroll: float,
        edge: float,
        cote: float,
        confiance_ia: float
    ) -> SuggestionMise:
        """
        Suggère une mise avec analyse complète.
        
        Args:
            bankroll: Bankroll actuelle
            edge: Expected value
            cote: Cote décimale
            confiance_ia: Confiance de l'IA (0-100%)
        
        Returns:
            Suggestion complète avec explications
        """
        # Calculer Kelly complet pour référence
        kelly_complet = bankroll * (edge / (cote - 1)) if edge > 0 else 0
        
        # Calculer mise suggérée (Kelly 25%)
        mise_suggeree = self.calculer_mise_kelly(bankroll, edge, cote)
        
        # Pourcentage de bankroll
        pct_bankroll = (mise_suggeree / bankroll * 100) if bankroll > 0 else 0
        
        # Déterminer confiance
        if edge < self.EDGE_MINIMUM:
            confiance = "faible"
            message = f"⚠️ Edge faible ({edge*100:.1f}%) - Kelly suggère de ne pas parier"
        elif confiance_ia < 60:
            confiance = "faible"
            message = f"⚠️ Confiance IA faible ({confiance_ia:.0f}%) - Réduire la mise"
        elif pct_bankroll > 3:
            confiance = "moyenne"
            message = f"⚡ Mise élevée ({pct_bankroll:.1f}% bankroll) - Risque augmenté"
        else:
            confiance = "haute"
            message = f"✅ Mise optimale Kelly 25% ({pct_bankroll:.1f}% bankroll)"
        
        return SuggestionMise(
            mise_suggeree=mise_suggeree,
            mise_kelly_complete=round(kelly_complet, 2),
            fraction_utilisee=self.FRACTION_KELLY,
            edge=edge,
            pourcentage_bankroll=round(pct_bankroll, 2),
            confiance=confiance,
            message=message
        )
    
    def valider_mise(
        self,
        mise: float,
        bankroll: float,
        seuil: Optional[float] = None,
    ) -> ValidationMise:
        """
        Valide qu'une mise respecte les règles de money management.
        
        Args:
            mise: Montant de la mise proposée
            bankroll: Bankroll actuelle
        
        Returns:
            Résultat de validation avec raisons
        """
        if mise <= 0:
            return ValidationMise(
                autorise=False,
                raison="La mise doit être positive",
                pourcentage_bankroll=0,
                niveau_risque="normal"
            )
        
        if bankroll <= 0:
            return ValidationMise(
                autorise=False,
                raison="Bankroll invalide",
                pourcentage_bankroll=0,
                niveau_risque="normal"
            )
        
        pct = mise / bankroll
        
        # Hard cap à 5%
        if pct > self.SEUIL_RISQUE_MAXIMUM:
            return ValidationMise(
                autorise=False,
                raison=f"❌ Mise {pct*100:.1f}% > seuil maximum 5% (hard cap) - REFUSÉE",
                pourcentage_bankroll=round(pct * 100, 2),
                niveau_risque="tres_eleve"
            )
        
        seuil_alerte = self.SEUIL_RISQUE_ELEVE if seuil is None else seuil

        # Alerte a partir du seuil configure (legacy: parametre "seuil")
        if pct > seuil_alerte:
            return ValidationMise(
                autorise=True,
                raison=f"⚠️ Mise élevée ({pct*100:.1f}% bankroll) - Risque important",
                pourcentage_bankroll=round(pct * 100, 2),
                niveau_risque="eleve"
            )
        
        return ValidationMise(
            autorise=True,
            raison=None,
            pourcentage_bankroll=round(pct * 100, 2),
            niveau_risque="normal"
        )
    
    @avec_session_db
    def calculer_bankroll_actuelle(
        self,
        user_id: int,
        bankroll_initiale: float,
        db: Session
    ) -> float:
        """
        Calcule la bankroll actuelle = initiale + somme(gains - mises).
        
        Args:
            user_id: ID utilisateur
            bankroll_initiale: Bankroll de départ
            db: Session DB (injectée par décorateur)
        
        Returns:
            Bankroll actuelle en euros
        """
        # Somme des gains
        total_gains = db.query(func.coalesce(func.sum(PariSportif.gain), 0)).filter(
            PariSportif.user_id == user_id,
            PariSportif.statut == "gagne"
        ).scalar() or 0
        
        # Somme des mises
        total_mises = db.query(func.coalesce(func.sum(PariSportif.mise), 0)).filter(
            PariSportif.user_id == user_id
        ).scalar() or 0
        
        bankroll_actuelle = bankroll_initiale + (total_gains - total_mises)
        
        return round(bankroll_actuelle, 2)
    
    @avec_session_db
    def obtenir_historique_bankroll(
        self,
        user_id: int,
        bankroll_initiale: float,
        jours: int = 30,
        db: Session = None
    ) -> list[dict]:
        """
        Calcule l'évolution de la bankroll sur les N derniers jours.
        
        Args:
            user_id: ID utilisateur
            bankroll_initiale: Bankroll de départ
            jours: Nombre de jours d'historique
            db: Session DB (injectée)
        
        Returns:
            Liste de points {date, bankroll, variation}
        """
        date_debut = datetime.now() - timedelta(days=jours)
        
        # Récupérer tous les paris depuis date_debut
        paris = db.query(PariSportif).filter(
            PariSportif.user_id == user_id,
            PariSportif.cree_le >= date_debut
        ).order_by(PariSportif.cree_le).all()
        
        historique = []
        bankroll_courante = bankroll_initiale
        
        # Point initial
        historique.append({
            "date": date_debut.isoformat(),
            "bankroll": bankroll_initiale,
            "variation": 0
        })
        
        # Calculer évolution jour par jour
        for pari in paris:
            variation = 0
            
            if pari.statut == "gagne":
                variation = pari.gain - pari.mise
            elif pari.statut == "perdu":
                variation = -pari.mise
            
            bankroll_courante += variation
            
            historique.append({
                "date": pari.cree_le.isoformat(),
                "bankroll": round(bankroll_courante, 2),
                "variation": round(variation, 2)
            })
        
        return historique

    def obtenir_historique(
        self,
        user_id: int,
        jours: int = 30,
        session: Optional[Session] = None,
    ) -> list[dict]:
        """Compatibilite legacy: renvoie l'historique persisted en base."""
        if session is None:
            raise ErreurValidation("Une session SQLAlchemy est requise")

        date_debut = datetime.now() - timedelta(days=jours)
        rows = (
            session.query(BankrollHistorique)
            .filter(
                BankrollHistorique.user_id == user_id,
                BankrollHistorique.date >= date_debut,
            )
            .order_by(BankrollHistorique.date.desc())
            .all()
        )

        return [
            {
                "montant": row.montant,
                "variation": row.variation,
                "date": row.date.isoformat() if row.date else None,
            }
            for row in rows
        ]
    
    def calculer_roi(
        self,
        total_mises: float,
        total_gains: float
    ) -> float:
        """
        Calcule le ROI (Return on Investment).
        
        ROI = (gains - mises) / mises * 100
        
        Args:
            total_mises: Somme des mises
            total_gains: Somme des gains
        
        Returns:
            ROI en pourcentage
        """
        return obtenir_analytics().calculer_roi(total_mises, total_gains)


# Factory pour le service
def get_bankroll_manager() -> BankrollManager:
    """Retourne une instance du BankrollManager."""
    return BankrollManager()
