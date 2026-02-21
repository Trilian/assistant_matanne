"""
UI Feedback - Progress tracking avec st.status().

Utilise st.status() natif (Streamlit 1.25+) pour un tracking
de progression moderne avec états visuels intégrés.
"""

from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Callable, Generator, TypeVar

import streamlit as st

T = TypeVar("T")


class EtatProgression(Enum):
    """États possibles d'une progression."""

    EN_COURS = "running"
    TERMINE = "complete"
    ERREUR = "error"


@dataclass
class EtapeProgression:
    """Représente une étape dans une progression multi-étapes."""

    nom: str
    statut: EtatProgression = EtatProgression.EN_COURS
    debut: datetime = field(default_factory=datetime.now)
    fin: datetime | None = None
    message: str = ""

    @property
    def duree_secondes(self) -> float:
        """Durée de l'étape en secondes."""
        end = self.fin or datetime.now()
        return (end - self.debut).total_seconds()


class SuiviProgression:
    """Tracker de progression avec st.status().

    Usage moderne:
        with SuiviProgression("Import recettes", total=100) as progression:
            for i, item in enumerate(items):
                process_item(item)
                progression.update(i + 1, f"Traitement: {item.name}")
        # Automatiquement marqué comme terminé

    Usage classique:
        progression = SuiviProgression("Import recettes", total=100)
        for i, item in enumerate(items):
            process_item(item)
            progression.mettre_a_jour(i + 1, f"Traitement: {item.name}")
        progression.terminer()
    """

    def __init__(
        self,
        operation: str,
        total: int,
        afficher_pourcentage: bool = True,
        expanded: bool = True,
    ):
        """Initialise le tracker de progression.

        Args:
            operation: Nom de l'opération
            total: Nombre total d'éléments
            afficher_pourcentage: Afficher % vs x/y
            expanded: Status étendu par défaut
        """
        self.operation = operation
        self.total = total
        self.afficher_pourcentage = afficher_pourcentage
        self.courant = 0
        self.debut = datetime.now()
        self._etat = EtatProgression.EN_COURS

        # Créer le status container
        self._status = st.status(operation, expanded=expanded)
        self._status_text = self._status.empty()
        self._progress_bar = self._status.progress(0.0)

    def __enter__(self) -> SuiviProgression:
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        """Context manager exit - termine automatiquement."""
        if exc_type is not None:
            self.erreur(str(exc_val) if exc_val else "Erreur inattendue")
            return False
        if self._etat == EtatProgression.EN_COURS:
            self.terminer()
        return False

    def mettre_a_jour(self, courant: int, statut: str = "") -> None:
        """Met à jour la progression.

        Args:
            courant: Valeur actuelle (0 à total)
            statut: Message de statut optionnel
        """
        self.courant = min(courant, self.total)
        pct = self.courant / self.total if self.total > 0 else 0

        # Update progress bar
        self._progress_bar.progress(pct)

        # Build status text
        if self.afficher_pourcentage:
            progress_text = f"{pct * 100:.0f}%"
        else:
            progress_text = f"{self.courant}/{self.total}"

        # Time estimation
        if 0 < self.courant < self.total:
            elapsed = (datetime.now() - self.debut).total_seconds()
            estimated_total = elapsed / self.courant * self.total
            remaining = estimated_total - elapsed
            time_text = f"~{remaining:.0f}s restant"
        else:
            time_text = ""

        # Compose message
        parts = [progress_text]
        if statut:
            parts.append(statut)
        if time_text:
            parts.append(time_text)

        self._status_text.markdown(f"**{' • '.join(parts)}**")

    # Alias
    update = mettre_a_jour

    def incrementer(self, pas: int = 1, statut: str = "") -> None:
        """Incrémente la progression."""
        self.mettre_a_jour(self.courant + pas, statut)

    def terminer(self, message: str = "") -> None:
        """Marque comme terminé avec succès."""
        self.courant = self.total
        self._etat = EtatProgression.TERMINE

        elapsed = (datetime.now() - self.debut).total_seconds()
        final_msg = message or f"Terminé en {elapsed:.1f}s"

        self._progress_bar.progress(1.0)
        self._status_text.markdown(f"✅ **{final_msg}**")
        self._status.update(label=f"✅ {self.operation}", state="complete", expanded=False)

    def erreur(self, message: str) -> None:
        """Marque en erreur."""
        self._etat = EtatProgression.ERREUR
        self._status_text.markdown(f"❌ **{message}**")
        self._status.update(label=f"❌ {self.operation}", state="error", expanded=True)


class EtatChargement:
    """Gestion d'états de chargement multi-étapes avec st.status().

    Usage moderne:
        with EtatChargement("Initialisation système") as chargement:
            with chargement.etape("Connexion DB"):
                connect_db()
            with chargement.etape("Chargement cache"):
                load_cache()
            with chargement.etape("Validation config"):
                validate_config()
        # Automatiquement finalisé

    Usage classique:
        chargement = EtatChargement("Chargement données")
        chargement.ajouter_etape("Connexion DB")
        connect_db()
        chargement.terminer_etape("Connexion DB")
        chargement.finaliser()
    """

    def __init__(self, titre: str, expanded: bool = True):
        """Initialise le tracker multi-étapes.

        Args:
            titre: Titre global de l'opération
            expanded: Status étendu par défaut
        """
        self.titre = titre
        self.etapes: list[EtapeProgression] = []
        self._etape_courante: int | None = None
        self.debut = datetime.now()
        self._etat = EtatProgression.EN_COURS

        # Créer le status container
        self._status = st.status(titre, expanded=expanded)
        self._content = self._status.container()

    def __enter__(self) -> EtatChargement:
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        """Context manager exit - finalise automatiquement."""
        if exc_type is not None:
            if self._etape_courante is not None:
                self.erreur_etape(msg_erreur=str(exc_val) if exc_val else "Erreur")
            self._status.update(label=f"❌ {self.titre}", state="error", expanded=True)
            return False
        if self._etat == EtatProgression.EN_COURS:
            self.finaliser()
        return False

    @contextmanager
    def etape(self, nom: str) -> Generator[None, None, None]:
        """Context manager pour une étape.

        Usage:
            with chargement.etape("Connexion DB"):
                connect_db()
            # Automatiquement marqué comme terminé
        """
        self.ajouter_etape(nom)
        try:
            yield
            self.terminer_etape(nom)
        except Exception as e:
            self.erreur_etape(nom, str(e))
            raise

    def ajouter_etape(self, nom_etape: str) -> None:
        """Ajoute une étape en cours."""
        etape = EtapeProgression(nom=nom_etape)
        self.etapes.append(etape)
        self._etape_courante = len(self.etapes) - 1
        self._rafraichir_affichage()

    def terminer_etape(self, nom_etape: str | None = None, succes: bool = True) -> None:
        """Marque une étape comme terminée."""
        idx = self._trouver_etape(nom_etape)
        if idx is None:
            return

        etape = self.etapes[idx]
        etape.fin = datetime.now()
        etape.statut = EtatProgression.TERMINE if succes else EtatProgression.ERREUR
        self._rafraichir_affichage()

    def erreur_etape(self, nom_etape: str | None = None, msg_erreur: str = "") -> None:
        """Marque une étape en erreur."""
        idx = self._trouver_etape(nom_etape)
        if idx is None:
            return

        etape = self.etapes[idx]
        etape.fin = datetime.now()
        etape.statut = EtatProgression.ERREUR
        etape.message = msg_erreur
        self._rafraichir_affichage()

    def finaliser(self, message_succes: str = "") -> None:
        """Termine le chargement avec succès."""
        self._etat = EtatProgression.TERMINE
        elapsed = (datetime.now() - self.debut).total_seconds()

        final_msg = message_succes or f"Terminé en {elapsed:.1f}s"
        label = f"✅ {self.titre}"

        self._status.update(label=label, state="complete", expanded=False)
        self._content.success(final_msg)

    def _trouver_etape(self, nom: str | None) -> int | None:
        """Trouve l'index d'une étape par nom ou retourne la courante."""
        if nom:
            for i, e in enumerate(self.etapes):
                if e.nom == nom:
                    return i
            return None
        return self._etape_courante

    def _rafraichir_affichage(self) -> None:
        """Met à jour l'affichage des étapes."""
        terminees = sum(1 for e in self.etapes if e.statut == EtatProgression.TERMINE)
        total = len(self.etapes)

        self._status.update(
            label=f"{self.titre} ({terminees}/{total})",
            state="running",
        )

        # Clear and rebuild content
        self._content.empty()

        for etape in self.etapes:
            if etape.statut == EtatProgression.TERMINE:
                icon = "✅"
                duree = f"({etape.duree_secondes:.1f}s)"
            elif etape.statut == EtatProgression.ERREUR:
                icon = "❌"
                duree = etape.message or "Erreur"
            else:
                icon = "⏳"
                duree = "en cours..."

            self._content.markdown(f"{icon} **{etape.nom}** {duree}")


# ═══════════════════════════════════════════════════════════
# Helpers de haut niveau
# ═══════════════════════════════════════════════════════════


@contextmanager
def suivi_operation(
    operation: str,
    total: int | None = None,
    afficher_pourcentage: bool = True,
) -> Generator[SuiviProgression | EtatChargement, None, None]:
    """Context manager unifié pour le suivi d'opérations.

    Args:
        operation: Nom de l'opération
        total: Nombre d'éléments (si None, utilise EtatChargement)
        afficher_pourcentage: Afficher % vs x/y

    Yields:
        SuiviProgression si total fourni, sinon EtatChargement
    """
    if total is not None:
        with SuiviProgression(operation, total, afficher_pourcentage) as tracker:
            yield tracker
    else:
        with EtatChargement(operation) as tracker:
            yield tracker


def avec_progression(
    items: list[T],
    operation: str = "Traitement",
    callback: Callable[[T], None] | None = None,
) -> Generator[tuple[int, T], None, None]:
    """Itérateur avec progression automatique.

    Args:
        items: Liste d'éléments à traiter
        operation: Nom de l'opération
        callback: Callback optionnel appelé pour chaque item

    Yields:
        Tuples (index, item)

    Example:
        for i, item in avec_progression(items, "Import"):
            process(item)
    """
    total = len(items)
    with SuiviProgression(operation, total) as progression:
        for i, item in enumerate(items):
            if callback:
                callback(item)
            yield i, item
            progression.mettre_a_jour(i + 1, f"Traité: {i + 1}/{total}")


__all__ = [
    "EtatProgression",
    "EtapeProgression",
    "SuiviProgression",
    "EtatChargement",
    "suivi_operation",
    "avec_progression",
]
