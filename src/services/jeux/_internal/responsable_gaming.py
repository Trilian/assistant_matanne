"""
Service de mise responsable — Gestion du budget jeu

Fonctionnalités:
- Limite mensuelle configurable
- Jauge de progression avec alertes (50%, 75%, 90%, 100%)
- Mode cool-down après dépassement
- Auto-exclusion temporaire
- Rappels pédagogiques
"""

import logging
from datetime import date, timedelta
from decimal import Decimal
from typing import Any

from sqlalchemy.orm import Session

from src.core.decorators import avec_session_db
from src.services.core.registry import service_factory

logger = logging.getLogger(__name__)

# Seuils d'alerte en pourcentage
SEUIL_ALERTE_50 = 50
SEUIL_ALERTE_75 = 75
SEUIL_ALERTE_90 = 90
SEUIL_ALERTE_100 = 100

# Limites par défaut
LIMITE_MENSUELLE_DEFAUT = Decimal("50.00")
COOLDOWN_JOURS_DEFAUT = 3

# Messages pédagogiques
MESSAGES_RAPPEL = [
    "🎲 Le jeu doit rester un divertissement, pas une source de revenus.",
    "📊 L'espérance mathématique est toujours négative sur le long terme.",
    "💡 Ne misez jamais plus que ce que vous pouvez vous permettre de perdre.",
    "⏰ Fixez-vous des limites de temps ET de budget.",
    "🧠 Après une série de pertes, faites une pause. Ne 'chassez' pas vos pertes.",
    "📱 Joueurs Info Service: 09 74 75 13 13 (appel non surtaxé)",
]


class ResponsableGamingService:
    """Service de gestion de la mise responsable."""

    def _obtenir_mois_courant(self) -> date:
        """Retourne le premier jour du mois courant."""
        today = date.today()
        return today.replace(day=1)

    @avec_session_db
    def obtenir_suivi_mensuel(self, db: Session | None = None) -> dict[str, Any]:
        """
        Obtient ou crée le suivi du mois en cours.

        Returns:
            Dict avec infos du suivi mensuel
        """
        from src.core.models.jeux import MiseResponsable

        mois = self._obtenir_mois_courant()
        suivi = db.query(MiseResponsable).filter_by(mois=mois).first()

        if not suivi:
            # Récupérer la limite du mois précédent ou utiliser le défaut
            mois_prec = (mois - timedelta(days=1)).replace(day=1)
            prec = db.query(MiseResponsable).filter_by(mois=mois_prec).first()
            limite = prec.limite_mensuelle if prec else LIMITE_MENSUELLE_DEFAUT

            suivi = MiseResponsable(
                mois=mois,
                limite_mensuelle=limite,
                mises_cumulees=Decimal("0.00"),
            )
            db.add(suivi)
            db.commit()
            db.refresh(suivi)

        return {
            "mois": suivi.mois,
            "limite_mensuelle": float(suivi.limite_mensuelle),
            "mises_cumulees": float(suivi.mises_cumulees),
            "pourcentage": suivi.pourcentage_utilise,
            "reste_disponible": float(suivi.reste_disponible),
            "est_bloque": suivi.est_bloque,
            "auto_exclusion": suivi.auto_exclusion_jusqu_a,
            "cooldown_actif": suivi.cooldown_actif,
            "cooldown_fin": suivi.cooldown_fin,
            "alertes": {
                "50_pct": suivi.alerte_50_pct,
                "75_pct": suivi.alerte_75_pct,
                "90_pct": suivi.alerte_90_pct,
                "100_pct": suivi.alerte_100_pct,
            },
        }

    @avec_session_db
    def verifier_mise_autorisee(
        self, montant: Decimal, db: Session | None = None
    ) -> dict[str, Any]:
        """
        Vérifie si une mise est autorisée.

        Args:
            montant: Montant de la mise envisagée

        Returns:
            Dict avec autorisee, raison, reste_apres
        """
        from src.core.models.jeux import MiseResponsable

        mois = self._obtenir_mois_courant()
        suivi = db.query(MiseResponsable).filter_by(mois=mois).first()

        if not suivi:
            return {
                "autorisee": True,
                "raison": None,
                "reste_apres": float(LIMITE_MENSUELLE_DEFAUT - montant),
            }

        if suivi.est_bloque:
            if suivi.auto_exclusion_jusqu_a and suivi.auto_exclusion_jusqu_a > date.today():
                return {
                    "autorisee": False,
                    "raison": f"Auto-exclusion active jusqu'au {suivi.auto_exclusion_jusqu_a}",
                    "reste_apres": 0,
                }
            if suivi.cooldown_actif:
                return {
                    "autorisee": False,
                    "raison": f"Période de cool-down active jusqu'au {suivi.cooldown_fin}",
                    "reste_apres": 0,
                }
            return {
                "autorisee": False,
                "raison": "Limite mensuelle atteinte",
                "reste_apres": 0,
            }

        reste = suivi.reste_disponible
        if montant > reste:
            return {
                "autorisee": False,
                "raison": f"Montant ({montant}€) dépasse le reste disponible ({reste}€)",
                "reste_apres": 0,
            }

        return {
            "autorisee": True,
            "raison": None,
            "reste_apres": float(reste - montant),
        }

    @avec_session_db
    def enregistrer_mise(
        self, montant: Decimal, type_jeu: str, db: Session | None = None
    ) -> dict[str, Any]:
        """
        Enregistre une mise et met à jour les alertes.

        Args:
            montant: Montant misé
            type_jeu: "paris", "loto", "euromillions"

        Returns:
            Dict avec nouveau_total, pourcentage, alertes_declenchees
        """
        from src.core.models.jeux import MiseResponsable

        mois = self._obtenir_mois_courant()
        suivi = db.query(MiseResponsable).filter_by(mois=mois).first()

        if not suivi:
            suivi = MiseResponsable(
                mois=mois,
                limite_mensuelle=LIMITE_MENSUELLE_DEFAUT,
                mises_cumulees=Decimal("0.00"),
            )
            db.add(suivi)

        suivi.mises_cumulees += montant
        pct = suivi.pourcentage_utilise

        alertes = []
        if pct >= SEUIL_ALERTE_50 and not suivi.alerte_50_pct:
            suivi.alerte_50_pct = True
            alertes.append("50%")
        if pct >= SEUIL_ALERTE_75 and not suivi.alerte_75_pct:
            suivi.alerte_75_pct = True
            alertes.append("75%")
        if pct >= SEUIL_ALERTE_90 and not suivi.alerte_90_pct:
            suivi.alerte_90_pct = True
            alertes.append("90%")
        if pct >= SEUIL_ALERTE_100 and not suivi.alerte_100_pct:
            suivi.alerte_100_pct = True
            alertes.append("100%")
            # Activer cool-down automatique
            suivi.cooldown_actif = True
            suivi.cooldown_fin = date.today() + timedelta(days=COOLDOWN_JOURS_DEFAUT)

        db.commit()

        logger.info(
            f"Mise {montant}€ ({type_jeu}) enregistrée. "
            f"Total: {suivi.mises_cumulees}/{suivi.limite_mensuelle} ({pct:.0f}%)"
        )

        return {
            "nouveau_total": float(suivi.mises_cumulees),
            "pourcentage": pct,
            "reste_disponible": float(suivi.reste_disponible),
            "alertes_declenchees": alertes,
            "est_bloque": suivi.est_bloque,
        }

    @avec_session_db
    def modifier_limite(self, nouvelle_limite: Decimal, db: Session | None = None) -> bool:
        """Modifie la limite mensuelle."""
        from src.core.models.jeux import MiseResponsable

        mois = self._obtenir_mois_courant()
        suivi = db.query(MiseResponsable).filter_by(mois=mois).first()

        if not suivi:
            suivi = MiseResponsable(
                mois=mois,
                limite_mensuelle=nouvelle_limite,
            )
            db.add(suivi)
        else:
            suivi.limite_mensuelle = nouvelle_limite

        db.commit()
        logger.info(f"Limite mensuelle modifiée: {nouvelle_limite}€")
        return True

    @avec_session_db
    def activer_auto_exclusion(self, nb_jours: int, db: Session | None = None) -> date:
        """
        Active l'auto-exclusion pour X jours.

        Returns:
            Date de fin d'exclusion
        """
        from src.core.models.jeux import MiseResponsable

        mois = self._obtenir_mois_courant()
        suivi = db.query(MiseResponsable).filter_by(mois=mois).first()

        if not suivi:
            suivi = MiseResponsable(
                mois=mois,
                limite_mensuelle=LIMITE_MENSUELLE_DEFAUT,
            )
            db.add(suivi)

        fin = date.today() + timedelta(days=nb_jours)
        suivi.auto_exclusion_jusqu_a = fin
        db.commit()

        logger.info(f"Auto-exclusion activée jusqu'au {fin}")
        return fin

    @avec_session_db
    def desactiver_cooldown(self, db: Session | None = None) -> bool:
        """Désactive le cool-down (si la date est passée)."""
        from src.core.models.jeux import MiseResponsable

        mois = self._obtenir_mois_courant()
        suivi = db.query(MiseResponsable).filter_by(mois=mois).first()

        if suivi and suivi.cooldown_actif:
            if suivi.cooldown_fin and suivi.cooldown_fin <= date.today():
                suivi.cooldown_actif = False
                suivi.cooldown_fin = None
                db.commit()
                return True
        return False

    @avec_session_db
    def obtenir_historique_limites(
        self, nb_mois: int = 12, db: Session | None = None
    ) -> list[dict[str, Any]]:
        """Historique des limites et mises sur N mois."""
        from src.core.models.jeux import MiseResponsable

        suivis = (
            db.query(MiseResponsable).order_by(MiseResponsable.mois.desc()).limit(nb_mois).all()
        )

        return [
            {
                "mois": s.mois,
                "limite": float(s.limite_mensuelle),
                "mises": float(s.mises_cumulees),
                "pourcentage": s.pourcentage_utilise,
                "est_bloque": s.est_bloque,
            }
            for s in suivis
        ]

    def obtenir_message_rappel(self) -> str:
        """Retourne un message de rappel aléatoire."""
        import random

        return random.choice(MESSAGES_RAPPEL)


@service_factory("responsable_gaming", tags={"jeux", "responsable"})
def get_responsable_gaming_service() -> ResponsableGamingService:
    """Factory pour le service de mise responsable."""
    return ResponsableGamingService()
