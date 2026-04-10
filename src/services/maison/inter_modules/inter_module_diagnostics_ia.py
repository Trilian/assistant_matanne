"""
Service pour les interactions inter-modules Maison (Diagnostics IA) × Artisans.

IM9: Photo → diagnostic → artisans en 3 étapes
"""

import logging

from src.core.ai import obtenir_client_ia
from src.core.decorators import avec_session_db
from src.services.core.base import BaseAIService
from src.services.core.registry import service_factory

logger = logging.getLogger(__name__)


class DiagnosticsIAArtisansService(BaseAIService):
    """Service pour les diagnostics IA de pannes avec suggestion d'artisans."""

    def __init__(self):
        super().__init__(
            client=obtenir_client_ia(),
            cache_prefix="diagnostics_ia",
            default_ttl=7200,
            service_name="diagnostics_ia",
        )

    def diagnostiquer_panne_photo(
        self,
        image_url: str,
        description_panne: str = "",
    ) -> dict:
        """Diagnostique une panne via photo Pixtral + description (IM9).

        Utilise Mistral Pixtral pour analyser une photo de panne et générer:
        1. Identification de la panne
        2. Estimation de coût
        3. Liste d'artisans compétents

        Args:
            image_url: URL ou chemin vers l'image
            description_panne: Description textuelle additionnelle

        Returns:
            Dict avec diagnostic, estimation et artisans suggérés
        """
        try:
            # En production: utiliser Pixtral via obtenir_client_ia()
            # Pour l'MVP: simulation d'une panne courante

            prompt_diag = f"""Analyse cette image de panne domestique:
Description fournie: {description_panne}

Fournis un diagnostic JSON avec:
- type_panne (chauffage, plomberie, electricite, etc)
- localisation (cuisine, salle de bain, etc)
- severite (1-5, 1=mineure, 5=critique)
- cause_probable (description courte)
- cout_reparation_estime_min (euros)
- cout_reparation_estime_max (euros)
- temps_reparation_h (heures estimées)
- reparation_diy (booléen: peut-on le faire soi-même?)
- urgence (bool: intervention rapide nécessaire?)
- artisans_competents (liste des métiers: "électricien", "plombier", etc.)
"""

            # Simulation pour MVP
            diagnostic = {
                "type_panne": "plomberie",
                "localisation": "salle de bain",
                "severite": 3,
                "cause_probable": "Fuite tuyauterie sous-sol",
                "cout_reparation_estime_min": 150,
                "cout_reparation_estime_max": 400,
                "temps_reparation_h": 2,
                "reparation_diy": False,
                "urgence": True,
                "artisans_competents": ["plombier", "plombier-chauffagiste"],
            }

            logger.info(
                f"✅ Diagnostic panne: {diagnostic['type_panne']} "
                f"({diagnostic['severite']}/5 sévérité)"
            )

            return diagnostic

        except Exception as e:
            logger.error(f"Erreur diagnostic IA: {e}")
            return {"error": str(e)}

    @avec_session_db
    def creer_projet_maison_depuis_diagnostic(
        self,
        diagnostic: dict,
        db=None,
    ) -> dict:
        """Crée un projet maison automatique depuis un diagnostic (IM9).

        Args:
            diagnostic: Dict de diagnostic retourné par diagnostiquer_panne_photo()
            db: Session DB (injectée par @avec_session_db)

        Returns:
            Dict avec id_projet et détails du projet créé
        """
        from datetime import datetime, timedelta

        from src.core.models import ProjetMaison

        try:
            # Créer le projet
            severite_map = {1: "faible", 2: "moyen", 3: "moyen", 4: "haut", 5: "critique"}
            priorite = severite_map.get(diagnostic.get("severite", 2), "moyen")

            projet = ProjetMaison(
                nom=f"Réparation: {diagnostic.get('type_panne', 'Panne')}",
                description=(
                    f"Type: {diagnostic.get('type_panne')}\n"
                    f"Cause: {diagnostic.get('cause_probable')}\n"
                    f"Coût estimé: {diagnostic.get('cout_reparation_estime_min')}-"
                    f"{diagnostic.get('cout_reparation_estime_max')}€\n"
                    f"Temps estimé: {diagnostic.get('temps_reparation_h')}h"
                ),
                priorite=priorite,
                date_creation=datetime.now(),
                localisation=diagnostic.get("localisation", "maison"),
                budget_estime=diagnostic.get("cout_reparation_estime_max", 250),
                statut="planifie",
            )

            # Ajouter catégories d'artisans
            artisans_str = ", ".join(diagnostic.get("artisans_competents", []))
            projet.artisans_requestus = artisans_str

            db.add(projet)
            db.commit()
            db.refresh(projet)

            logger.info(f"✅ Projet maison créé: {projet.nom} (id={projet.id})")

            return {
                "id_projet": projet.id,
                "nom": projet.nom,
                "priorite": priorite,
                "budget_estime": projet.budget_estime,
                "artisans_requestus": artisans_str,
                "message": "Projet de réparation créé et prêt pour chercher des artisans",
            }

        except Exception as e:
            logger.error(f"Erreur création projet: {e}")
            db.rollback()
            return {"error": str(e)}

    @avec_session_db
    def suggerer_artisans_pour_panne(
        self,
        type_panne: str,
        localisation: str = "maison",
        db=None,
    ) -> dict:
        """Suggère des artisans compétents pour une panne (IM9).

        Args:
            type_panne: Type de panne (plomberie, électricité, etc.)
            localisation: Localisation (cuisine, salle de bain, etc.)
            db: Session DB (injectée par @avec_session_db)

        Returns:
            Dict avec liste des artisans suggérés
        """
        try:
            # Mapping type_panne -> métiers
            metiers_map = {
                "plomberie": ["plombier", "plombier-chauffagiste"],
                "electricite": ["électricien", "électricien-domotique"],
                "chauffage": ["chauffagiste", "plombier-chauffagiste"],
                "toiture": ["charpentier", "couvreur"],
                "maçonnerie": ["maçon", "carreleur"],
                "peinture": ["peintre", "décorateur"],
                "menuiserie": ["menuisier", "charpentier"],
            }

            metiers = metiers_map.get(
                type_panne.lower(),
                ["artisan multi-services"],
            )

            # Simulation: données d'artisans (en production: depuis DB)
            artisans_simules = [
                {
                    "nom": "Jean Plomberie SARL",
                    "metier": "plombier",
                    "nota": 4.8,
                    "avis": 142,
                    "disponibilite": "Demain 09:00-12:00",
                    "tarif_interventin_ht": 80,
                },
                {
                    "nom": "Eaux & Tuyaux",
                    "metier": "plombier",
                    "nota": 4.6,
                    "avis": 98,
                    "disponibilite": "Jeudi 14:00-17:00",
                    "tarif_interventin_ht": 75,
                },
            ]

            return {
                "type_panne": type_panne,
                "localisation": localisation,
                "metiers_demandes": metiers,
                "artisans_suggerees": artisans_simules,
                "nb_artisans": len(artisans_simules),
                "message": (
                    f"Trouvé {len(artisans_simules)} artisan(s) pour {type_panne}. "
                    f"Cliquez pour contacter."
                ),
            }

        except Exception as e:
            logger.error(f"Erreur suggestion artisans: {e}")
            return {"error": str(e)}


@service_factory("diagnostics_ia_artisans", tags={"maison", "reparations", "ia"})
def obtenir_service_diagnostics_ia_artisans() -> DiagnosticsIAArtisansService:
    """Factory pour le service Diagnostics IA Artisans."""
    return DiagnosticsIAArtisansService()
