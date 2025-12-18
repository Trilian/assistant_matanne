"""
Service Planning Semaine - Logique métier
Gère génération IA, CRUD, déplacements
"""
import logging
from datetime import date, timedelta
from typing import List, Dict, Optional, Tuple
from sqlalchemy.orm import Session
from src.core.database import get_db_context
from src.core.models import (
    PlanningHebdomadaire,
    RepasPlanning,
    ConfigPlanningUtilisateur,
    Recette,
    TypeRepasEnum,
    VersionRecette,
    TypeVersionRecetteEnum,
)
from src.core.ai_agent import AgentIA
import json

logger = logging.getLogger(__name__)


class PlanningService:
    """Service métier pour le planning hebdomadaire"""

    JOURS_SEMAINE = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]

    # ===================================
    # CONFIGURATION
    # ===================================

    @staticmethod
    def get_or_create_config(utilisateur_id: int = None) -> ConfigPlanningUtilisateur:
        """Récupère ou crée la config utilisateur"""
        with get_db_context() as db:
            config = (
                db.query(ConfigPlanningUtilisateur)
                .filter(ConfigPlanningUtilisateur.utilisateur_id == utilisateur_id)
                .first()
            )

            if not config:
                config = ConfigPlanningUtilisateur(utilisateur_id=utilisateur_id)
                db.add(config)
                db.commit()
                db.refresh(config)

            return config

    @staticmethod
    def update_config(config_data: Dict, utilisateur_id: int = None):
        """Met à jour la config utilisateur"""
        with get_db_context() as db:
            config = PlanningService.get_or_create_config(utilisateur_id)

            for key, value in config_data.items():
                if hasattr(config, key):
                    setattr(config, key, value)

            db.commit()

    # ===================================
    # CRUD PLANNING
    # ===================================

    @staticmethod
    def get_semaine_debut(date_ref: date = None) -> date:
        """Retourne le lundi de la semaine"""
        if date_ref is None:
            date_ref = date.today()
        return date_ref - timedelta(days=date_ref.weekday())

    @staticmethod
    def create_planning(semaine_debut: date, nom: str = None) -> int:
        """Crée un nouveau planning vide"""
        with get_db_context() as db:
            planning = PlanningHebdomadaire(
                semaine_debut=semaine_debut,
                nom=nom or f"Semaine du {semaine_debut.strftime('%d/%m/%Y')}",
                statut="brouillon",
            )
            db.add(planning)
            db.commit()
            return planning.id

    @staticmethod
    def get_planning(planning_id: int) -> Optional[PlanningHebdomadaire]:
        """Récupère un planning complet"""
        with get_db_context() as db:
            return (
                db.query(PlanningHebdomadaire)
                .filter(PlanningHebdomadaire.id == planning_id)
                .first()
            )

    @staticmethod
    def get_planning_semaine(semaine_debut: date) -> Optional[PlanningHebdomadaire]:
        """Récupère le planning d'une semaine spécifique"""
        with get_db_context() as db:
            return (
                db.query(PlanningHebdomadaire)
                .filter(PlanningHebdomadaire.semaine_debut == semaine_debut)
                .first()
            )

    @staticmethod
    def delete_planning(planning_id: int):
        """Supprime un planning"""
        with get_db_context() as db:
            db.query(PlanningHebdomadaire).filter(PlanningHebdomadaire.id == planning_id).delete()
            db.commit()

    # ===================================
    # GESTION REPAS
    # ===================================

    @staticmethod
    def add_repas(
        planning_id: int,
        jour_semaine: int,
        date_repas: date,
        type_repas: str,
        recette_id: int = None,
        **kwargs,
    ) -> int:
        """Ajoute un repas au planning"""
        with get_db_context() as db:
            ordre_map = {
                "petit_déjeuner": 1,
                "déjeuner": 2,
                "goûter": 3,
                "dîner": 4,
                "bébé": 5,
                "batch_cooking": 6,
            }

            repas = RepasPlanning(
                planning_id=planning_id,
                jour_semaine=jour_semaine,
                date=date_repas,
                type_repas=type_repas,
                recette_id=recette_id,
                ordre=kwargs.get("ordre", ordre_map.get(type_repas, 0)),
                portions=kwargs.get("portions", 4),
                est_adapte_bebe=kwargs.get("est_adapte_bebe", False),
                est_batch_cooking=kwargs.get("est_batch_cooking", False),
                notes=kwargs.get("notes"),
            )
            db.add(repas)
            db.commit()
            return repas.id

    @staticmethod
    def update_repas(repas_id: int, **kwargs):
        """Met à jour un repas"""
        with get_db_context() as db:
            repas = db.query(RepasPlanning).filter(RepasPlanning.id == repas_id).first()
            if repas:
                for key, value in kwargs.items():
                    if hasattr(repas, key):
                        setattr(repas, key, value)
                db.commit()

    @staticmethod
    def delete_repas(repas_id: int):
        """Supprime un repas"""
        with get_db_context() as db:
            db.query(RepasPlanning).filter(RepasPlanning.id == repas_id).delete()
            db.commit()

    @staticmethod
    def deplacer_repas(repas_id: int, nouveau_jour: int, nouvelle_date: date):
        """Déplace un repas vers un autre jour"""
        PlanningService.update_repas(repas_id, jour_semaine=nouveau_jour, date=nouvelle_date)

    @staticmethod
    def echanger_repas(repas_id_1: int, repas_id_2: int):
        """Échange deux repas (déjeuner ↔ dîner par exemple)"""
        with get_db_context() as db:
            repas1 = db.query(RepasPlanning).filter(RepasPlanning.id == repas_id_1).first()
            repas2 = db.query(RepasPlanning).filter(RepasPlanning.id == repas_id_2).first()

            if repas1 and repas2:
                # Échanger les recettes
                repas1.recette_id, repas2.recette_id = repas2.recette_id, repas1.recette_id
                repas1.portions, repas2.portions = repas2.portions, repas1.portions
                repas1.notes, repas2.notes = repas2.notes, repas1.notes
                db.commit()

    # ===================================
    # GÉNÉRATION IA
    # ===================================

    @staticmethod
    async def generer_planning_ia(
        semaine_debut: date, config: ConfigPlanningUtilisateur, agent: AgentIA
    ) -> int:
        """Génère un planning complet avec l'IA"""
        logger.info(f"Génération IA planning semaine du {semaine_debut}")

        # 1. Créer le planning
        planning_id = PlanningService.create_planning(
            semaine_debut, f"Planning IA {semaine_debut.strftime('%d/%m')}"
        )

        # 2. Récupérer recettes disponibles
        with get_db_context() as db:
            recettes = db.query(Recette).all()
            recettes_data = [
                {
                    "id": r.id,
                    "nom": r.nom,
                    "type_repas": r.type_repas,
                    "temps_total": r.temps_preparation + r.temps_cuisson,
                    "est_rapide": r.est_rapide,
                    "compatible_bebe": r.compatible_bebe,
                    "compatible_batch": r.compatible_batch,
                    "a_version_bebe": any(
                        v.type_version == TypeVersionRecetteEnum.BEBE for v in r.versions
                    ),
                    "a_version_batch": any(
                        v.type_version == TypeVersionRecetteEnum.BATCH_COOKING for v in r.versions
                    ),
                }
                for r in recettes
            ]

        # 3. Construire le prompt pour l'IA
        repas_actifs = [k for k, v in config.repas_actifs.items() if v]

        prompt = f"""Génère un planning de repas pour 7 jours.

Configuration :
- Adultes : {config.nb_adultes}, Enfants : {config.nb_enfants}
- Bébé : {'Oui' if config.a_bebe else 'Non'}
- Repas à planifier : {', '.join(repas_actifs)}
- Batch cooking : {'Oui' if config.batch_cooking_actif else 'Non'}

Recettes disponibles : {len(recettes_data)} recettes

Contraintes :
- Varier les types de recettes
- Equilibrer rapide/complexe
- Si bébé : privilégier recettes compatibles
- Si batch cooking : planifier sessions {config.jours_batch}

Format JSON strict :
{{
  "planning": [
    {{
      "jour": 0,
      "repas": [
        {{
          "type": "déjeuner",
          "recette_nom": "Nom de la recette",
          "portions": 4,
          "adapte_bebe": false,
          "raison": "Pourquoi cette recette"
        }}
      ]
    }}
  ]
}}

Recettes disponibles (extraits) :
{json.dumps(recettes_data[:20], indent=2, ensure_ascii=False)}

UNIQUEMENT le JSON, aucun texte avant ou après !"""

        # 4. Appeler l'IA
        try:
            response = await agent._call_mistral(
                prompt=prompt,
                system_prompt="Tu es un nutritionniste expert en planification de repas. Réponds UNIQUEMENT en JSON valide.",
                temperature=0.7,
                max_tokens=2000,
            )

            # 5. Parser réponse
            cleaned = response.strip().replace("```json", "").replace("```", "")
            data = json.loads(cleaned)

            # 6. Créer les repas
            with get_db_context() as db:
                for jour_data in data.get("planning", []):
                    jour = jour_data["jour"]
                    date_jour = semaine_debut + timedelta(days=jour)

                    for repas_data in jour_data.get("repas", []):
                        recette_nom = repas_data["recette_nom"]

                        # Trouver la recette
                        recette = (
                            db.query(Recette).filter(Recette.nom.ilike(f"%{recette_nom}%")).first()
                        )

                        if recette:
                            PlanningService.add_repas(
                                planning_id=planning_id,
                                jour_semaine=jour,
                                date_repas=date_jour,
                                type_repas=repas_data["type"],
                                recette_id=recette.id,
                                portions=repas_data.get("portions", 4),
                                est_adapte_bebe=repas_data.get("adapte_bebe", False),
                                notes=f"IA : {repas_data.get('raison', '')}",
                            )

            # Marquer comme généré par IA
            with get_db_context() as db:
                planning = (
                    db.query(PlanningHebdomadaire)
                    .filter(PlanningHebdomadaire.id == planning_id)
                    .first()
                )
                if planning:
                    planning.genere_par_ia = True
                    db.commit()

            logger.info(f"✅ Planning IA généré : {planning_id}")
            return planning_id

        except Exception as e:
            logger.error(f"❌ Erreur génération IA : {e}")
            # Supprimer le planning vide
            PlanningService.delete_planning(planning_id)
            raise ValueError(f"Échec génération IA : {str(e)}")

    # ===================================
    # EXPORT / UTILS
    # ===================================

    @staticmethod
    def get_planning_structure(planning_id: int) -> Dict:
        """Retourne le planning sous forme structurée pour affichage"""
        with get_db_context() as db:
            planning = (
                db.query(PlanningHebdomadaire)
                .filter(PlanningHebdomadaire.id == planning_id)
                .first()
            )

            if not planning:
                return None

            # Structure par jour
            structure = {
                "planning_id": planning.id,
                "nom": planning.nom,
                "semaine_debut": planning.semaine_debut,
                "jours": [],
            }

            for jour_idx in range(7):
                date_jour = planning.semaine_debut + timedelta(days=jour_idx)

                repas_jour = [r for r in planning.repas if r.jour_semaine == jour_idx]

                structure["jours"].append(
                    {
                        "jour_idx": jour_idx,
                        "nom_jour": PlanningService.JOURS_SEMAINE[jour_idx],
                        "date": date_jour,
                        "repas": [
                            {
                                "id": r.id,
                                "type": r.type_repas,
                                "recette": {
                                    "id": r.recette.id,
                                    "nom": r.recette.nom,
                                    "temps_total": r.recette.temps_preparation
                                    + r.recette.temps_cuisson,
                                    "url_image": r.recette.url_image,
                                }
                                if r.recette
                                else None,
                                "portions": r.portions,
                                "est_adapte_bebe": r.est_adapte_bebe,
                                "est_batch": r.est_batch_cooking,
                                "notes": r.notes,
                                "statut": r.statut,
                            }
                            for r in sorted(repas_jour, key=lambda x: x.ordre)
                        ],
                    }
                )

            return structure


# Instance globale
planning_service = PlanningService()
