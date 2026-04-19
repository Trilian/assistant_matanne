"""
Service Simulation Rénovation — CRUD simulations, scénarios, comparaisons.

Fournit :
- CRUD simulations de rénovation (multi-projet, multi-scénarios)
- CRUD scénarios par simulation
- Duplication de simulations et scénarios
- Comparaison multi-scénarios
- Stats agrégées

Usage:
    service = get_simulation_service()
    simulations = service.lister_simulations()
"""

from __future__ import annotations

import logging
from typing import Any

from sqlalchemy import func
from sqlalchemy.orm import Session

from src.core.decorators import avec_cache, avec_session_db
from src.services.core.registry import service_factory

logger = logging.getLogger(__name__)


class SimulationService:
    """Service de gestion des simulations de rénovation."""

    # ─────────────────────────────────────────────────────────
    # SIMULATIONS — CRUD
    # ─────────────────────────────────────────────────────────

    @avec_session_db
    def lister_simulations(
        self,
        db: Session | None = None,
        statut: str | None = None,
        type_projet: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> dict[str, Any]:
        """Liste les simulations avec filtres et pagination."""
        from src.core.models.maison_extensions import SimulationRenovation

        assert db is not None
        query = db.query(SimulationRenovation)

        if statut:
            query = query.filter(SimulationRenovation.statut == statut)
        if type_projet:
            query = query.filter(SimulationRenovation.type_projet == type_projet)

        total = query.count()
        items = (
            query.order_by(SimulationRenovation.modifie_le.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )

        return {
            "items": [self._simulation_to_dict(s, db) for s in items],
            "total": total,
            "page": page,
            "page_size": page_size,
        }

    @avec_session_db
    def obtenir_simulation(self, simulation_id: int, db: Session | None = None) -> dict[str, Any]:
        """Récupère une simulation par ID avec ses scénarios."""
        from src.core.models.maison_extensions import SimulationRenovation

        assert db is not None
        sim = db.query(SimulationRenovation).filter_by(id=simulation_id).first()
        if not sim:
            raise ValueError(f"Simulation {simulation_id} introuvable")
        return self._simulation_to_dict(sim, db)

    @avec_session_db
    def creer_simulation(self, data: dict[str, Any], db: Session | None = None) -> dict[str, Any]:
        """Crée une nouvelle simulation."""
        from src.core.models.maison_extensions import SimulationRenovation

        assert db is not None
        sim = SimulationRenovation(**data)
        db.add(sim)
        db.flush()
        result = self._simulation_to_dict(sim, db)
        db.commit()
        logger.info(f"Simulation créée: {sim.id} - {sim.nom}")
        return result

    @avec_session_db
    def modifier_simulation(
        self, simulation_id: int, data: dict[str, Any], db: Session | None = None
    ) -> dict[str, Any]:
        """Modifie une simulation existante."""
        from src.core.models.maison_extensions import SimulationRenovation

        assert db is not None
        sim = db.query(SimulationRenovation).filter_by(id=simulation_id).first()
        if not sim:
            raise ValueError(f"Simulation {simulation_id} introuvable")

        for key, value in data.items():
            if hasattr(sim, key) and value is not None:
                setattr(sim, key, value)

        db.flush()
        result = self._simulation_to_dict(sim, db)
        db.commit()
        return result

    @avec_session_db
    def supprimer_simulation(self, simulation_id: int, db: Session | None = None) -> bool:
        """Supprime une simulation et ses scénarios (cascade)."""
        from src.core.models.maison_extensions import SimulationRenovation

        assert db is not None
        sim = db.query(SimulationRenovation).filter_by(id=simulation_id).first()
        if not sim:
            raise ValueError(f"Simulation {simulation_id} introuvable")

        db.delete(sim)
        db.commit()
        logger.info(f"Simulation supprimée: {simulation_id}")
        return True

    @avec_session_db
    def dupliquer_simulation(self, simulation_id: int, db: Session | None = None) -> dict[str, Any]:
        """Duplique une simulation avec tous ses scénarios."""
        from src.core.models.maison_extensions import ScenarioSimulation, SimulationRenovation

        assert db is not None
        original = db.query(SimulationRenovation).filter_by(id=simulation_id).first()
        if not original:
            raise ValueError(f"Simulation {simulation_id} introuvable")

        copie = SimulationRenovation(
            nom=f"{original.nom} (copie)",
            description=original.description,
            type_projet=original.type_projet,
            statut="brouillon",
            pieces_concernees=original.pieces_concernees,
            zones_terrain=original.zones_terrain,
            projet_id=original.projet_id,
            plan_id=original.plan_id,
            tags=original.tags,
            notes=original.notes,
        )
        db.add(copie)
        db.flush()

        # Dupliquer les scénarios
        for scenario in original.scenarios:
            copie_scenario = ScenarioSimulation(
                simulation_id=copie.id,
                nom=scenario.nom,
                description=scenario.description,
                est_favori=scenario.est_favori,
                budget_estime_min=scenario.budget_estime_min,
                budget_estime_max=scenario.budget_estime_max,
                budget_materiaux=scenario.budget_materiaux,
                budget_main_oeuvre=scenario.budget_main_oeuvre,
                duree_estimee_jours=scenario.duree_estimee_jours,
                score_faisabilite=scenario.score_faisabilite,
                analyse_faisabilite=scenario.analyse_faisabilite,
                contraintes_techniques=scenario.contraintes_techniques,
                recommandations=scenario.recommandations,
                impact_dpe=scenario.impact_dpe,
                gain_energetique_pct=scenario.gain_energetique_pct,
                plus_value_estimee=scenario.plus_value_estimee,
                postes_travaux=scenario.postes_travaux,
                artisans_necessaires=scenario.artisans_necessaires,
                notes=scenario.notes,
            )
            db.add(copie_scenario)

        db.commit()
        logger.info(f"Simulation {simulation_id} dupliquée → {copie.id}")
        return self._simulation_to_dict(copie, db)

    # ─────────────────────────────────────────────────────────
    # SCÉNARIOS — CRUD
    # ─────────────────────────────────────────────────────────

    @avec_session_db
    def lister_scenarios(
        self, simulation_id: int, db: Session | None = None
    ) -> list[dict[str, Any]]:
        """Liste les scénarios d'une simulation."""
        from src.core.models.maison_extensions import ScenarioSimulation

        assert db is not None
        scenarios = (
            db.query(ScenarioSimulation)
            .filter_by(simulation_id=simulation_id)
            .order_by(ScenarioSimulation.est_favori.desc(), ScenarioSimulation.cree_le)
            .all()
        )
        return [self._scenario_to_dict(s) for s in scenarios]

    @avec_session_db
    def obtenir_scenario(self, scenario_id: int, db: Session | None = None) -> dict[str, Any]:
        """Récupère un scénario par ID."""
        from src.core.models.maison_extensions import ScenarioSimulation

        assert db is not None
        scenario = db.query(ScenarioSimulation).filter_by(id=scenario_id).first()
        if not scenario:
            raise ValueError(f"Scénario {scenario_id} introuvable")
        return self._scenario_to_dict(scenario)

    @avec_session_db
    def creer_scenario(
        self, simulation_id: int, data: dict[str, Any], db: Session | None = None
    ) -> dict[str, Any]:
        """Crée un scénario dans une simulation."""
        from src.core.models.maison_extensions import ScenarioSimulation, SimulationRenovation

        assert db is not None
        sim = db.query(SimulationRenovation).filter_by(id=simulation_id).first()
        if not sim:
            raise ValueError(f"Simulation {simulation_id} introuvable")

        scenario = ScenarioSimulation(simulation_id=simulation_id, **data)
        db.add(scenario)
        db.flush()
        result = self._scenario_to_dict(scenario)
        db.commit()
        logger.info(f"Scénario créé: {scenario.id} dans simulation {simulation_id}")
        return result

    @avec_session_db
    def modifier_scenario(
        self, scenario_id: int, data: dict[str, Any], db: Session | None = None
    ) -> dict[str, Any]:
        """Modifie un scénario existant."""
        from src.core.models.maison_extensions import ScenarioSimulation

        assert db is not None
        scenario = db.query(ScenarioSimulation).filter_by(id=scenario_id).first()
        if not scenario:
            raise ValueError(f"Scénario {scenario_id} introuvable")

        for key, value in data.items():
            if hasattr(scenario, key) and value is not None:
                setattr(scenario, key, value)

        db.flush()
        result = self._scenario_to_dict(scenario)
        db.commit()
        return result

    @avec_session_db
    def supprimer_scenario(self, scenario_id: int, db: Session | None = None) -> bool:
        """Supprime un scénario."""
        from src.core.models.maison_extensions import ScenarioSimulation

        assert db is not None
        scenario = db.query(ScenarioSimulation).filter_by(id=scenario_id).first()
        if not scenario:
            raise ValueError(f"Scénario {scenario_id} introuvable")

        db.delete(scenario)
        db.commit()
        logger.info(f"Scénario supprimé: {scenario_id}")
        return True

    # ─────────────────────────────────────────────────────────
    # COMPARAISON
    # ─────────────────────────────────────────────────────────

    @avec_session_db
    def comparer_scenarios(
        self, simulation_id: int, db: Session | None = None
    ) -> dict[str, Any]:
        """Compare tous les scénarios d'une simulation."""
        from src.core.models.maison_extensions import ScenarioSimulation, SimulationRenovation

        assert db is not None
        sim = db.query(SimulationRenovation).filter_by(id=simulation_id).first()
        if not sim:
            raise ValueError(f"Simulation {simulation_id} introuvable")

        scenarios = (
            db.query(ScenarioSimulation)
            .filter_by(simulation_id=simulation_id)
            .all()
        )

        scenarios_dicts = [self._scenario_to_dict(s) for s in scenarios]

        # Déterminer les meilleurs scénarios
        meilleur_budget = None
        meilleur_faisabilite = None
        meilleur_rapport = None

        if scenarios:
            # Scénario le moins cher (budget_estime_min)
            with_budget = [s for s in scenarios if s.budget_estime_min is not None]
            if with_budget:
                meilleur_budget = min(with_budget, key=lambda s: float(s.budget_estime_min)).id

            # Scénario le plus faisable
            with_score = [s for s in scenarios if s.score_faisabilite is not None]
            if with_score:
                meilleur_faisabilite = max(with_score, key=lambda s: s.score_faisabilite).id

            # Meilleur rapport (score / budget moyen)
            with_both = [
                s for s in scenarios
                if s.score_faisabilite is not None and s.budget_estime_min is not None
            ]
            if with_both:
                meilleur_rapport = max(
                    with_both,
                    key=lambda s: (
                        s.score_faisabilite
                        / max(float(s.budget_estime_min), 1)
                    ),
                ).id

        return {
            "simulation": self._simulation_to_dict(sim, db),
            "scenarios": scenarios_dicts,
            "meilleur_budget": meilleur_budget,
            "meilleur_faisabilite": meilleur_faisabilite,
            "meilleur_rapport": meilleur_rapport,
        }

    # ─────────────────────────────────────────────────────────
    # HELPERS
    # ─────────────────────────────────────────────────────────

    @staticmethod
    def _simulation_to_dict(sim: Any, db: Session | None = None) -> dict[str, Any]:
        """Convertit une SimulationRenovation en dict."""
        return {
            "id": sim.id,
            "nom": sim.nom,
            "description": sim.description,
            "type_projet": sim.type_projet,
            "statut": sim.statut,
            "pieces_concernees": sim.pieces_concernees,
            "zones_terrain": sim.zones_terrain,
            "projet_id": sim.projet_id,
            "plan_id": sim.plan_id,
            "tags": sim.tags,
            "notes": sim.notes,
            "scenarios_count": len(sim.scenarios) if sim.scenarios else 0,
            "created_at": sim.cree_le.isoformat() if sim.cree_le else None,
            "updated_at": sim.modifie_le.isoformat() if sim.modifie_le else None,
        }

    @staticmethod
    def _scenario_to_dict(s: Any) -> dict[str, Any]:
        """Convertit un ScenarioSimulation en dict."""
        return {
            "id": s.id,
            "simulation_id": s.simulation_id,
            "nom": s.nom,
            "description": s.description,
            "est_favori": s.est_favori,
            "budget_estime_min": float(s.budget_estime_min) if s.budget_estime_min else None,
            "budget_estime_max": float(s.budget_estime_max) if s.budget_estime_max else None,
            "budget_materiaux": float(s.budget_materiaux) if s.budget_materiaux else None,
            "budget_main_oeuvre": float(s.budget_main_oeuvre) if s.budget_main_oeuvre else None,
            "duree_estimee_jours": s.duree_estimee_jours,
            "score_faisabilite": s.score_faisabilite,
            "analyse_faisabilite": s.analyse_faisabilite,
            "contraintes_techniques": s.contraintes_techniques,
            "recommandations": s.recommandations,
            "impact_dpe": s.impact_dpe,
            "gain_energetique_pct": s.gain_energetique_pct,
            "plus_value_estimee": float(s.plus_value_estimee) if s.plus_value_estimee else None,
            "postes_travaux": s.postes_travaux,
            "artisans_necessaires": s.artisans_necessaires,
            "plan_avant_id": s.plan_avant_id,
            "plan_apres_id": s.plan_apres_id,
            "notes": s.notes,
            "created_at": s.cree_le.isoformat() if s.cree_le else None,
            "updated_at": s.modifie_le.isoformat() if s.modifie_le else None,
        }


@service_factory("simulation_renovation", tags={"maison", "simulation"})
def get_simulation_service() -> SimulationService:
    """Factory singleton pour SimulationService."""
    return SimulationService()
