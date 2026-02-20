"""
Tests de régression visuelle pour composants UI.

Permet de détecter les changements non-intentionnels dans le rendu HTML
des composants en comparant avec des snapshots de référence.

Usage:
    # Dans un test
    from src.ui.testing import SnapshotTester

    def test_badge_success():
        tester = SnapshotTester("badge")
        html = badge_html("Active", variant="success")
        tester.assert_matches(html, {"variant": "success"})

    # Mise à jour des snapshots (CLI)
    # UPDATE_SNAPSHOTS=1 pytest tests/test_ui_snapshots.py
"""

from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ComponentSnapshot:
    """Snapshot d'un composant pour comparaison.

    Attributes:
        name: Nom du composant.
        html: HTML rendu.
        props: Props utilisées pour le rendu.
        hash: Hash du contenu pour comparaison rapide.
    """

    name: str
    html: str
    props: dict
    hash: str

    @classmethod
    def create(cls, name: str, html: str, props: dict) -> ComponentSnapshot:
        """Crée un snapshot avec hash calculé.

        Args:
            name: Nom du composant.
            html: HTML rendu.
            props: Props du composant.

        Returns:
            ComponentSnapshot avec hash.
        """
        # Normaliser le HTML (enlever espaces superflus)
        normalized_html = " ".join(html.split())

        # Créer le contenu pour hash
        content = f"{normalized_html}{json.dumps(props, sort_keys=True)}"
        hash_value = hashlib.sha256(content.encode()).hexdigest()[:16]

        return cls(name=name, html=normalized_html, props=props, hash=hash_value)

    def to_dict(self) -> dict:
        """Convertit en dict pour sérialisation."""
        return {
            "name": self.name,
            "html": self.html,
            "props": self.props,
            "hash": self.hash,
        }

    @classmethod
    def from_dict(cls, data: dict) -> ComponentSnapshot:
        """Crée depuis un dict."""
        return cls(
            name=data["name"],
            html=data["html"],
            props=data["props"],
            hash=data["hash"],
        )


class SnapshotTester:
    """Testeur de snapshots pour régression visuelle.

    Utilisation typique dans les tests:
        1. Premier run: crée le snapshot de référence
        2. Runs suivants: compare avec le snapshot existant
        3. Si changement intentionnel: UPDATE_SNAPSHOTS=1 pytest ...

    Example:
        def test_badge_variants():
            tester = SnapshotTester("badge")

            # Test chaque variante
            for variant in ["success", "warning", "danger"]:
                html = badge_html("Test", variant=variant)
                tester.assert_matches(html, {"variant": variant}, test_name=variant)
    """

    # Dossier des snapshots
    SNAPSHOT_DIR = Path(__file__).parent.parent.parent.parent / "tests" / "snapshots" / "ui"

    def __init__(self, component_name: str):
        """Initialise le testeur.

        Args:
            component_name: Nom du composant à tester.
        """
        self.component_name = component_name
        self.SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)

    def snapshot_path(self, test_name: str) -> Path:
        """Retourne le chemin du fichier snapshot.

        Args:
            test_name: Nom du test.

        Returns:
            Path du fichier JSON.
        """
        safe_name = test_name.replace("/", "_").replace("\\", "_")
        return self.SNAPSHOT_DIR / f"{self.component_name}_{safe_name}.json"

    def assert_matches(
        self,
        html: str,
        props: dict,
        test_name: str = "default",
    ) -> None:
        """Vérifie que le rendu correspond au snapshot.

        Args:
            html: HTML rendu du composant.
            props: Props utilisées.
            test_name: Nom du test (pour différencier les cas).

        Raises:
            AssertionError: Si le snapshot ne correspond pas.
        """
        snapshot = ComponentSnapshot.create(self.component_name, html, props)
        path = self.snapshot_path(test_name)

        # Mode mise à jour
        if os.environ.get("UPDATE_SNAPSHOTS") == "1":
            self._write_snapshot(path, snapshot)
            return

        # Premier run: créer le snapshot
        if not path.exists():
            self._write_snapshot(path, snapshot)
            print(f"📸 Snapshot créé: {path.name}")
            return

        # Comparer avec l'existant
        existing = self._read_snapshot(path)

        if existing.hash != snapshot.hash:
            diff_msg = self._generate_diff(existing, snapshot)
            raise AssertionError(
                f"Snapshot mismatch pour {self.component_name}/{test_name}\n"
                f"\n{diff_msg}\n"
                f"\nHash attendu: {existing.hash}\n"
                f"Hash actuel:  {snapshot.hash}\n"
                f"\n💡 Run avec UPDATE_SNAPSHOTS=1 pour mettre à jour."
            )

    def _write_snapshot(self, path: Path, snapshot: ComponentSnapshot) -> None:
        """Écrit un snapshot sur disque."""
        path.write_text(
            json.dumps(snapshot.to_dict(), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    def _read_snapshot(self, path: Path) -> ComponentSnapshot:
        """Lit un snapshot depuis le disque."""
        data = json.loads(path.read_text(encoding="utf-8"))
        return ComponentSnapshot.from_dict(data)

    def _generate_diff(
        self,
        expected: ComponentSnapshot,
        actual: ComponentSnapshot,
    ) -> str:
        """Génère un diff lisible entre deux snapshots."""
        lines = ["Différences détectées:", ""]

        # Diff HTML
        if expected.html != actual.html:
            lines.append("📝 HTML:")
            lines.append(f"  Attendu: {expected.html[:100]}...")
            lines.append(f"  Actuel:  {actual.html[:100]}...")
            lines.append("")

        # Diff props
        if expected.props != actual.props:
            lines.append("⚙️ Props:")
            lines.append(f"  Attendu: {expected.props}")
            lines.append(f"  Actuel:  {actual.props}")

        return "\n".join(lines)

    def list_snapshots(self) -> list[str]:
        """Liste tous les snapshots pour ce composant.

        Returns:
            Liste des noms de tests ayant des snapshots.
        """
        prefix = f"{self.component_name}_"
        return [p.stem.replace(prefix, "") for p in self.SNAPSHOT_DIR.glob(f"{prefix}*.json")]

    def delete_snapshot(self, test_name: str) -> bool:
        """Supprime un snapshot.

        Args:
            test_name: Nom du test.

        Returns:
            True si supprimé, False si n'existait pas.
        """
        path = self.snapshot_path(test_name)
        if path.exists():
            path.unlink()
            return True
        return False


# ═══════════════════════════════════════════════════════════
# HELPERS POUR TESTS
# ═══════════════════════════════════════════════════════════


def assert_html_contains(html: str, *expected: str) -> None:
    """Vérifie que le HTML contient toutes les chaînes attendues.

    Args:
        html: HTML à vérifier.
        *expected: Chaînes qui doivent être présentes.

    Raises:
        AssertionError: Si une chaîne est manquante.
    """
    for exp in expected:
        if exp not in html:
            raise AssertionError(f"HTML ne contient pas: {exp!r}\n\nHTML: {html[:500]}...")


def assert_html_not_contains(html: str, *forbidden: str) -> None:
    """Vérifie que le HTML ne contient pas les chaînes interdites.

    Args:
        html: HTML à vérifier.
        *forbidden: Chaînes qui ne doivent pas être présentes.

    Raises:
        AssertionError: Si une chaîne interdite est présente.
    """
    for forb in forbidden:
        if forb in html:
            raise AssertionError(f"HTML contient la chaîne interdite: {forb!r}")


def normalize_html(html: str) -> str:
    """Normalise le HTML pour comparaison.

    - Supprime les espaces multiples
    - Trim les lignes
    - Uniformise les guillemets

    Args:
        html: HTML brut.

    Returns:
        HTML normalisé.
    """
    # Supprimer les espaces multiples
    normalized = " ".join(html.split())

    return normalized


__all__ = [
    "ComponentSnapshot",
    "SnapshotTester",
    "assert_html_contains",
    "assert_html_not_contains",
    "normalize_html",
]
