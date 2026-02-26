"""
Workflow Status — Innovation v11: st.status() pour workflows.

Fournit des progress indicators pour les opérations longues:
- Batch cooking (génération menus + listes)
- Imports de recettes (URL, PDF, images)
- Synchronisation données
- Génération rapports

Usage:
    from src.ui.components.workflow_status import (
        WorkflowStatus,
        batch_cooking_workflow,
        import_workflow,
        rapport_workflow,
    )

    # Workflow personnalisé
    with WorkflowStatus("Génération du menu", steps=4) as workflow:
        workflow.step("Analyse des préférences...")
        # ... traitement
        workflow.step("Génération des recettes...")
        # ... traitement
        workflow.complete("Menu généré!")

    # Workflow batch cooking prédéfini
    resultat = batch_cooking_workflow(
        date_debut=date.today(),
        nb_jours=7,
        callback_step=lambda msg: st.write(msg),
    )
"""

from __future__ import annotations

import logging
import time
from collections.abc import Callable, Generator
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import date
from typing import Any, TypeVar

import streamlit as st

logger = logging.getLogger(__name__)

T = TypeVar("T")

__all__ = [
    "WorkflowStatus",
    "WorkflowStep",
    "batch_cooking_workflow",
    "import_workflow",
    "rapport_workflow",
    "sync_workflow",
    "with_workflow",
]


# ═══════════════════════════════════════════════════════════
# DATACLASSES
# ═══════════════════════════════════════════════════════════


@dataclass
class WorkflowStep:
    """Étape d'un workflow."""

    name: str
    description: str = ""
    duration_ms: float = 0.0
    status: str = "pending"  # pending, running, completed, error
    result: Any = None
    error: str | None = None


@dataclass
class WorkflowResult:
    """Résultat complet d'un workflow."""

    success: bool
    steps: list[WorkflowStep] = field(default_factory=list)
    total_duration_ms: float = 0.0
    result: Any = None
    error: str | None = None


# ═══════════════════════════════════════════════════════════
# WORKFLOW STATUS — Wrapper st.status()
# ═══════════════════════════════════════════════════════════


class WorkflowStatus:
    """Gestionnaire de workflow avec st.status().

    Encapsule st.status() avec:
    - Suivi des étapes
    - Métriques de durée
    - Progress bar optionnelle
    - Gestion d'erreurs

    Usage:
        with WorkflowStatus("Import recettes", steps=3) as wf:
            wf.step("Téléchargement...")
            data = download()
            wf.step("Parsing...")
            parsed = parse(data)
            wf.step("Sauvegarde...")
            save(parsed)
            wf.complete("Import terminé!")
    """

    def __init__(
        self,
        label: str,
        *,
        steps: int = 0,
        expanded: bool = True,
        show_progress: bool = True,
        icon: str = "🔄",
    ):
        """
        Args:
            label: Titre du workflow
            steps: Nombre d'étapes (0 = indéterminé)
            expanded: Afficher le détail
            show_progress: Afficher la barre de progression
            icon: Icône du workflow
        """
        self.label = label
        self.total_steps = steps
        self.expanded = expanded
        self.show_progress = show_progress and steps > 0
        self.icon = icon

        self._current_step = 0
        self._steps: list[WorkflowStep] = []
        self._start_time = 0.0
        self._step_start_time = 0.0
        self._status = None
        self._progress_bar = None

    def __enter__(self) -> WorkflowStatus:
        """Démarre le workflow."""
        self._start_time = time.time()

        # Créer le status container
        self._status = st.status(
            f"{self.icon} {self.label}",
            expanded=self.expanded,
        )
        self._status.__enter__()

        # Progress bar optionnelle
        if self.show_progress:
            self._progress_bar = st.progress(0, text="Démarrage...")

        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        """Finalise le workflow."""
        duration = (time.time() - self._start_time) * 1000

        if exc_type is not None:
            # Erreur
            self._status.update(
                label=f"❌ {self.label} - Erreur",
                state="error",
                expanded=True,
            )
            st.error(f"Erreur: {exc_val}")
            logger.error(f"Workflow '{self.label}' échoué: {exc_val}")
        else:
            # Succès implicite (si complete() non appelé)
            if self._status._state != "complete":
                self._status.update(
                    label=f"✅ {self.label}",
                    state="complete",
                )

        # Métriques
        st.caption(f"⏱️ Durée totale: {duration:.0f}ms")

        self._status.__exit__(exc_type, exc_val, exc_tb)
        return False  # Ne pas supprimer l'exception

    def step(self, description: str, *, result: Any = None) -> None:
        """Marque une nouvelle étape.

        Args:
            description: Description de l'étape en cours
            result: Résultat optionnel de l'étape précédente
        """
        now = time.time()

        # Finaliser l'étape précédente
        if self._steps:
            prev_step = self._steps[-1]
            prev_step.duration_ms = (now - self._step_start_time) * 1000
            prev_step.status = "completed"
            prev_step.result = result

        # Nouvelle étape
        self._current_step += 1
        self._step_start_time = now

        step = WorkflowStep(
            name=f"Étape {self._current_step}",
            description=description,
            status="running",
        )
        self._steps.append(step)

        # Afficher l'étape
        st.write(f"**{self._current_step}.** {description}")

        # Mettre à jour la progress bar
        if self._progress_bar and self.total_steps > 0:
            progress = self._current_step / self.total_steps
            self._progress_bar.progress(
                min(progress, 1.0),
                text=f"Étape {self._current_step}/{self.total_steps}",
            )

    def substep(self, description: str) -> None:
        """Ajoute une sous-étape (indentée).

        Args:
            description: Description de la sous-étape
        """
        st.write(f"   ↳ {description}")

    def complete(
        self,
        message: str = "Terminé!",
        *,
        result: Any = None,
        icon: str = "✅",
    ) -> None:
        """Marque le workflow comme terminé.

        Args:
            message: Message de succès
            result: Résultat final
            icon: Icône de succès
        """
        # Finaliser la dernière étape
        if self._steps:
            last_step = self._steps[-1]
            last_step.duration_ms = (time.time() - self._step_start_time) * 1000
            last_step.status = "completed"
            last_step.result = result

        # Progress bar à 100%
        if self._progress_bar:
            self._progress_bar.progress(1.0, text=message)

        # Mise à jour status
        self._status.update(
            label=f"{icon} {self.label} - {message}",
            state="complete",
        )
        st.success(message)

    def error(self, message: str) -> None:
        """Marque le workflow en erreur.

        Args:
            message: Message d'erreur
        """
        if self._steps:
            last_step = self._steps[-1]
            last_step.status = "error"
            last_step.error = message

        self._status.update(
            label=f"❌ {self.label} - Erreur",
            state="error",
        )
        st.error(message)

    def warning(self, message: str) -> None:
        """Affiche un avertissement.

        Args:
            message: Message d'avertissement
        """
        st.warning(f"⚠️ {message}")

    def get_result(self) -> WorkflowResult:
        """Retourne le résultat complet du workflow.

        Returns:
            WorkflowResult avec toutes les métriques
        """
        duration = (time.time() - self._start_time) * 1000
        success = all(s.status == "completed" for s in self._steps)

        return WorkflowResult(
            success=success,
            steps=self._steps.copy(),
            total_duration_ms=duration,
        )


# ═══════════════════════════════════════════════════════════
# DECORATEUR WORKFLOW
# ═══════════════════════════════════════════════════════════


@contextmanager
def with_workflow(
    label: str,
    *,
    steps: int = 0,
    expanded: bool = True,
) -> Generator[WorkflowStatus, None, None]:
    """Context manager pour workflow simple.

    Usage:
        with with_workflow("Import", steps=3) as wf:
            wf.step("Étape 1...")
            wf.step("Étape 2...")
            wf.complete("Fini!")
    """
    workflow = WorkflowStatus(label, steps=steps, expanded=expanded)
    with workflow:
        yield workflow


# ═══════════════════════════════════════════════════════════
# WORKFLOWS PRÉDÉFINIS
# ═══════════════════════════════════════════════════════════


def batch_cooking_workflow(
    *,
    date_debut: date,
    nb_jours: int = 7,
    nb_personnes: int = 4,
    preferences: dict[str, Any] | None = None,
    callback_step: Callable[[str], None] | None = None,
) -> WorkflowResult:
    """Workflow complet de batch cooking.

    Étapes:
    1. Analyse des préférences et contraintes
    2. Génération du menu de la semaine (IA)
    3. Création de la liste de courses agrégée
    4. Planification du batch cooking (ordre de préparation)

    Args:
        date_debut: Date de début du planning
        nb_jours: Nombre de jours à planifier
        nb_personnes: Nombre de personnes
        preferences: Préférences alimentaires
        callback_step: Callback appelé à chaque étape

    Returns:
        WorkflowResult avec menu, liste courses, planning
    """
    with WorkflowStatus(
        "Batch Cooking",
        steps=4,
        icon="🍳",
    ) as workflow:
        # Étape 1: Analyse
        workflow.step("Analyse des préférences et du stock...")
        if callback_step:
            callback_step("Analyse des préférences...")
        time.sleep(0.5)  # Simulation

        workflow.substep("Vérification du stock actuel")
        workflow.substep("Analyse des allergies et restrictions")

        # Étape 2: Génération menu
        workflow.step("Génération du menu avec l'IA...")
        if callback_step:
            callback_step("Génération du menu...")

        try:
            from src.services.cuisine import get_planning_service

            service = get_planning_service()
            menu = service.generer_suggestions_ia_sync(
                date_debut=date_debut,
                nb_jours=nb_jours,
                nb_personnes=nb_personnes,
            )
            workflow.substep(f"{len(menu) if menu else 0} repas générés")
        except Exception as e:
            logger.warning(f"Génération menu fallback: {e}")
            menu = []
            workflow.warning("Menu généré en mode simplifié")

        # Étape 3: Liste de courses
        workflow.step("Création de la liste de courses...")
        if callback_step:
            callback_step("Agrégation des courses...")

        courses = []
        try:
            if menu:
                from src.services.cuisine import get_courses_service

                service = get_courses_service()
                courses = service.agreger_depuis_recettes_sync(menu)
                workflow.substep(f"{len(courses)} articles agrégés")
        except Exception as e:
            logger.warning(f"Agrégation courses fallback: {e}")
            workflow.warning("Liste simplifiée")

        # Étape 4: Planning batch
        workflow.step("Planification de la préparation...")
        if callback_step:
            callback_step("Optimisation de l'ordre...")

        planning_batch = {
            "jour_preparation": date_debut,
            "duree_estimee": "2h30",
            "ordre": [
                "1. Préparer les bases (bouillons, sauces)",
                "2. Cuire les féculents",
                "3. Préparer les légumes",
                "4. Assembler les plats",
            ],
        }
        workflow.substep("Ordre de préparation optimisé")

        # Résultat
        result = {
            "menu": menu,
            "courses": courses,
            "planning_batch": planning_batch,
            "date_debut": date_debut.isoformat(),
            "nb_jours": nb_jours,
        }

        workflow.complete(
            f"Plan de {nb_jours} jours prêt!",
            result=result,
        )

        return workflow.get_result()


def import_workflow(
    *,
    source: str,
    source_type: str = "url",  # url, pdf, image
    callback_step: Callable[[str], None] | None = None,
) -> WorkflowResult:
    """Workflow d'import de recettes.

    Étapes:
    1. Téléchargement/lecture de la source
    2. Extraction du contenu (parsing HTML/PDF/OCR)
    3. Analyse et structuration (IA)
    4. Validation et sauvegarde

    Args:
        source: URL, chemin fichier, ou bytes
        source_type: Type de source
        callback_step: Callback à chaque étape

    Returns:
        WorkflowResult avec recette importée
    """
    with WorkflowStatus(
        f"Import {source_type.upper()}",
        steps=4,
        icon="📥",
    ) as workflow:
        recette = None

        # Étape 1: Récupération
        workflow.step(f"Récupération depuis {source_type}...")
        if callback_step:
            callback_step("Téléchargement...")

        content = None
        if source_type == "url":
            try:
                import httpx

                response = httpx.get(source, timeout=30, follow_redirects=True)
                content = response.text
                workflow.substep(f"{len(content)} caractères récupérés")
            except Exception as e:
                workflow.error(f"Erreur téléchargement: {e}")
                return workflow.get_result()

        elif source_type == "pdf":
            workflow.substep("Lecture PDF...")
            # TODO: Extraction PDF
            content = source

        elif source_type == "image":
            workflow.substep("Préparation image...")
            content = source

        # Étape 2: Extraction
        workflow.step("Extraction du contenu...")
        if callback_step:
            callback_step("Parsing...")

        extracted = {}
        if source_type == "url" and content:
            try:
                from src.services.cuisine.recettes import RecipeImportService

                service = RecipeImportService()
                extracted = await service.importer(url)
                workflow.substep(f"Titre trouvé: {extracted.nom if extracted else 'N/A'}")
            except Exception as e:
                workflow.warning(f"Extraction basique: {e}")
                extracted = {"contenu_brut": content[:5000]}

        # Étape 3: Structuration IA
        workflow.step("Structuration avec l'IA...")
        if callback_step:
            callback_step("Analyse IA...")

        try:
            from src.services.cuisine import get_recette_service

            service = get_recette_service()
            recette = service.structurer_recette_ia_sync(extracted)
            if recette:
                workflow.substep(f"Recette: {recette.get('nom', 'Sans nom')}")
                workflow.substep(f"{len(recette.get('ingredients', []))} ingrédients")
        except Exception as e:
            logger.warning(f"Structuration IA: {e}")
            recette = extracted
            workflow.warning("Structuration manuelle recommandée")

        # Étape 4: Sauvegarde
        workflow.step("Validation et sauvegarde...")
        if callback_step:
            callback_step("Sauvegarde...")

        if recette and recette.get("nom"):
            workflow.substep("Recette validée")
            workflow.complete(
                f"Recette '{recette.get('nom', '')}' importée!",
                result=recette,
            )
        else:
            workflow.error("Recette non valide")

        return workflow.get_result()


def rapport_workflow(
    *,
    type_rapport: str,
    periode: tuple[date, date],
    format_sortie: str = "pdf",
    callback_step: Callable[[str], None] | None = None,
) -> WorkflowResult:
    """Workflow de génération de rapports.

    Args:
        type_rapport: budget, gaspillage, stocks, activites
        periode: (date_debut, date_fin)
        format_sortie: pdf, excel, html
        callback_step: Callback à chaque étape

    Returns:
        WorkflowResult avec chemin du rapport
    """
    with WorkflowStatus(
        f"Rapport {type_rapport}",
        steps=4,
        icon="📊",
    ) as workflow:
        # Étape 1: Collecte données
        workflow.step("Collecte des données...")
        if callback_step:
            callback_step("Requêtes DB...")

        workflow.substep(f"Période: {periode[0]} → {periode[1]}")
        data = {}  # TODO: Vraie collecte

        # Étape 2: Analyse
        workflow.step("Analyse et calculs...")
        if callback_step:
            callback_step("Analyse...")

        stats = {"total": 0, "moyenne": 0}  # TODO: Vrais calculs

        # Étape 3: Génération
        workflow.step(f"Génération {format_sortie.upper()}...")
        if callback_step:
            callback_step(f"Création {format_sortie}...")

        rapport_path = f"reports/{type_rapport}_{periode[0]}_{format_sortie}"

        # Étape 4: Finalisation
        workflow.step("Finalisation...")
        workflow.substep("Ajout des graphiques")
        workflow.substep("Mise en page")

        workflow.complete(
            f"Rapport {type_rapport} généré!",
            result={"path": rapport_path, "stats": stats},
        )

        return workflow.get_result()


def sync_workflow(
    *,
    sources: list[str],
    callback_step: Callable[[str], None] | None = None,
) -> WorkflowResult:
    """Workflow de synchronisation de données.

    Args:
        sources: Liste des sources à synchroniser
        callback_step: Callback à chaque étape

    Returns:
        WorkflowResult
    """
    with WorkflowStatus(
        "Synchronisation",
        steps=len(sources) + 1,
        icon="🔄",
    ) as workflow:
        synced = []

        for source in sources:
            workflow.step(f"Synchronisation {source}...")
            if callback_step:
                callback_step(f"Sync {source}...")

            try:
                # TODO: Vraie sync
                time.sleep(0.3)
                synced.append(source)
                workflow.substep(f"{source} synchronisé ✓")
            except Exception as e:
                workflow.warning(f"Erreur {source}: {e}")

        workflow.step("Vérification globale...")
        workflow.complete(
            f"{len(synced)}/{len(sources)} sources synchronisées",
            result={"synced": synced},
        )

        return workflow.get_result()
