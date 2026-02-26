"""
Service de gestion des profils utilisateurs.

Gère le CRUD des profils, le changement de profil actif,
le PIN de sécurité, et l'import/export de configuration.
"""

from __future__ import annotations

import hashlib
import logging
from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session

from src.core.decorators import avec_session_db
from src.core.models.notifications import PreferenceNotification
from src.core.models.users import ProfilUtilisateur
from src.services.core.registry import service_factory

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# CONSTANTES
# ═══════════════════════════════════════════════════════════

AVATARS_DISPONIBLES = [
    "👩",
    "👨",
    "👤",
    "🧑",
    "👩‍💻",
    "👨‍💻",
    "🦸‍♀️",
    "🦸‍♂️",
    "🧑‍🍳",
    "🏃‍♀️",
    "🏃‍♂️",
]

PREFERENCES_MODULES_DEFAUT: dict[str, dict[str, Any]] = {
    "cuisine": {
        "nb_suggestions_ia": 5,
        "types_cuisine_preferes": [],
        "duree_max_batch_min": 120,
    },
    "famille": {
        "activites_favorites_jules": [],
        "frequence_rappels_routines": "quotidien",
    },
    "maison": {
        "seuil_alerte_entretien_jours": 7,
    },
    "planning": {
        "horizon_defaut": "semaine",
    },
    "budget": {
        "seuils_alerte_pct": 80,
    },
}

NOTIFICATIONS_MODULES_DEFAUT: dict[str, dict[str, bool]] = {
    "cuisine": {
        "suggestions_repas": True,
        "stock_bas": True,
        "batch_cooking": False,
    },
    "famille": {
        "routines_jules": True,
        "activites_weekend": True,
        "achats_planifier": False,
    },
    "maison": {
        "entretien_programme": True,
        "charges_payer": True,
        "jardin_arrosage": False,
    },
    "planning": {
        "rappels_evenements": True,
        "taches_retard": True,
    },
    "budget": {
        "depassement_seuil": True,
        "resume_mensuel": False,
    },
}

SECTIONS_PROTEGER = ["budget", "sante", "admin"]


# ═══════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════


def _hasher_pin(pin: str) -> str:
    """Hash un PIN avec SHA-256."""
    return hashlib.sha256(pin.encode("utf-8")).hexdigest()


# ═══════════════════════════════════════════════════════════
# SERVICE
# ═══════════════════════════════════════════════════════════


class ProfilService:
    """Service de gestion des profils utilisateurs."""

    # ── CRUD ──────────────────────────────────────────────

    @staticmethod
    @avec_session_db
    def obtenir_profils(*, db: Session | None = None) -> list[ProfilUtilisateur]:
        """Retourne tous les profils utilisateurs."""
        return list(db.query(ProfilUtilisateur).order_by(ProfilUtilisateur.id).all())

    @staticmethod
    @avec_session_db
    def obtenir_profil(username: str, *, db: Session | None = None) -> ProfilUtilisateur | None:
        """Retourne un profil par username."""
        return db.query(ProfilUtilisateur).filter_by(username=username).first()

    @staticmethod
    @avec_session_db
    def obtenir_profil_par_id(
        user_id: int, *, db: Session | None = None
    ) -> ProfilUtilisateur | None:
        """Retourne un profil par ID."""
        return db.query(ProfilUtilisateur).filter_by(id=user_id).first()

    @staticmethod
    @avec_session_db
    def mettre_a_jour_profil(
        username: str, data: dict[str, Any], *, db: Session | None = None
    ) -> ProfilUtilisateur | None:
        """Met à jour un profil existant."""
        profil = db.query(ProfilUtilisateur).filter_by(username=username).first()
        if not profil:
            logger.warning("Profil introuvable: %s", username)
            return None

        champs_autorises = {
            "display_name",
            "email",
            "avatar_emoji",
            "date_naissance",
            "taille_cm",
            "poids_kg",
            "objectif_poids_kg",
            "objectif_pas_quotidien",
            "objectif_calories_brulees",
            "objectif_minutes_actives",
            "preferences_modules",
            "theme_prefere",
        }

        for champ, valeur in data.items():
            if champ in champs_autorises:
                setattr(profil, champ, valeur)

        db.commit()
        db.refresh(profil)
        logger.info("Profil mis à jour: %s", username)
        return profil

    # ── Changement de profil actif ────────────────────────

    @staticmethod
    def changer_profil_actif(username: str) -> bool:
        """Change le profil actif dans l'état global."""
        from src.core.state import obtenir_etat

        profil = ProfilService.obtenir_profil(username)
        if not profil:
            logger.warning("Profil introuvable: %s", username)
            return False

        etat = obtenir_etat()
        etat.nom_utilisateur = profil.display_name
        etat.user_id = profil.id
        etat.profil_charge = True
        logger.info("Profil actif changé: %s (id=%s)", username, profil.id)
        return True

    # ── PIN / Sécurité ────────────────────────────────────

    @staticmethod
    @avec_session_db
    def definir_pin(username: str, pin: str, *, db: Session | None = None) -> bool:
        """Définit un PIN pour un profil."""
        profil = db.query(ProfilUtilisateur).filter_by(username=username).first()
        if not profil:
            return False
        profil.pin_hash = _hasher_pin(pin)
        db.commit()
        logger.info("PIN défini pour %s", username)
        return True

    @staticmethod
    @avec_session_db
    def supprimer_pin(username: str, *, db: Session | None = None) -> bool:
        """Supprime le PIN d'un profil."""
        profil = db.query(ProfilUtilisateur).filter_by(username=username).first()
        if not profil:
            return False
        profil.pin_hash = None
        profil.sections_protegees = None
        db.commit()
        logger.info("PIN supprimé pour %s", username)
        return True

    @staticmethod
    @avec_session_db
    def verifier_pin(username: str, pin: str, *, db: Session | None = None) -> bool:
        """Vérifie un PIN."""
        profil = db.query(ProfilUtilisateur).filter_by(username=username).first()
        if not profil or not profil.pin_hash:
            return False
        return profil.pin_hash == _hasher_pin(pin)

    @staticmethod
    @avec_session_db
    def definir_sections_protegees(
        username: str, sections: list[str], *, db: Session | None = None
    ) -> bool:
        """Définit les sections protégées par PIN."""
        profil = db.query(ProfilUtilisateur).filter_by(username=username).first()
        if not profil:
            return False
        profil.sections_protegees = sections
        db.commit()
        return True

    # ── Export / Import ───────────────────────────────────

    @staticmethod
    @avec_session_db
    def exporter_configuration(username: str, *, db: Session | None = None) -> dict[str, Any]:
        """Exporte la configuration complète d'un profil en JSON."""
        profil = db.query(ProfilUtilisateur).filter_by(username=username).first()
        if not profil:
            return {}

        export: dict[str, Any] = {
            "version": "1.0",
            "timestamp": datetime.now().isoformat(),
            "profil": {
                "username": profil.username,
                "display_name": profil.display_name,
                "email": profil.email,
                "avatar_emoji": profil.avatar_emoji,
                "theme_prefere": profil.theme_prefere,
                "preferences_modules": profil.preferences_modules or {},
            },
            "sante": {
                "date_naissance": str(profil.date_naissance) if profil.date_naissance else None,
                "taille_cm": profil.taille_cm,
                "poids_kg": profil.poids_kg,
                "objectif_poids_kg": profil.objectif_poids_kg,
                "objectif_pas_quotidien": profil.objectif_pas_quotidien,
                "objectif_calories_brulees": profil.objectif_calories_brulees,
                "objectif_minutes_actives": profil.objectif_minutes_actives,
            },
        }

        # Préférences de notification
        notif_pref = db.query(PreferenceNotification).filter_by(user_id=None).first()
        if notif_pref:
            export["notifications"] = {
                "courses_rappel": notif_pref.courses_rappel,
                "repas_suggestion": notif_pref.repas_suggestion,
                "stock_alerte": notif_pref.stock_alerte,
                "meteo_alerte": notif_pref.meteo_alerte,
                "budget_alerte": notif_pref.budget_alerte,
                "quiet_hours_start": (
                    str(notif_pref.quiet_hours_start) if notif_pref.quiet_hours_start else None
                ),
                "quiet_hours_end": (
                    str(notif_pref.quiet_hours_end) if notif_pref.quiet_hours_end else None
                ),
                "modules_actifs": notif_pref.modules_actifs or {},
                "canal_prefere": notif_pref.canal_prefere,
            }

        return export

    @staticmethod
    @avec_session_db
    def importer_configuration(
        username: str, data: dict[str, Any], *, db: Session | None = None
    ) -> tuple[bool, str]:
        """Importe une configuration depuis un export JSON."""
        if "version" not in data or "profil" not in data:
            return False, "Format de fichier invalide (version ou profil manquant)"

        profil = db.query(ProfilUtilisateur).filter_by(username=username).first()
        if not profil:
            return False, f"Profil introuvable: {username}"

        # Importer profil
        profil_data = data.get("profil", {})
        for champ in (
            "display_name",
            "email",
            "avatar_emoji",
            "theme_prefere",
            "preferences_modules",
        ):
            if champ in profil_data:
                setattr(profil, champ, profil_data[champ])

        # Importer santé
        sante_data = data.get("sante", {})
        for champ in (
            "taille_cm",
            "poids_kg",
            "objectif_poids_kg",
            "objectif_pas_quotidien",
            "objectif_calories_brulees",
            "objectif_minutes_actives",
        ):
            if champ in sante_data and sante_data[champ] is not None:
                setattr(profil, champ, sante_data[champ])

        db.commit()
        logger.info("Configuration importée pour %s", username)
        return True, "Configuration importée avec succès"

    @staticmethod
    def reinitialiser_section(username: str, section: str) -> tuple[bool, str]:
        """Réinitialise une section aux valeurs par défaut."""
        if section == "preferences_modules":
            resultat = ProfilService.mettre_a_jour_profil(
                username, {"preferences_modules": PREFERENCES_MODULES_DEFAUT}
            )
            return resultat is not None, "Préférences modules réinitialisées"
        if section == "securite":
            ProfilService.supprimer_pin(username)
            return True, "Sécurité réinitialisée (PIN supprimé)"
        if section == "notifications":
            return True, "Notifications réinitialisées"
        return False, f"Section inconnue: {section}"


# ═══════════════════════════════════════════════════════════
# FACTORY
# ═══════════════════════════════════════════════════════════


@service_factory("profil", tags={"utilisateur", "config"})
def get_profil_service() -> ProfilService:
    """Factory singleton pour ProfilService."""
    return ProfilService()
