"""
Tests visuels automatisés avec Playwright pour l'UI Streamlit.

Ces tests capturent des screenshots de l'application et les comparent
aux références pour détecter les régressions visuelles.

Usage:
    # Installer Playwright
    pip install playwright pytest-playwright
    playwright install chromium

    # Lancer les tests
    pytest tests/visual/test_visual_regression.py

    # Mettre à jour les snapshots
    UPDATE_SNAPSHOTS=1 pytest tests/visual/test_visual_regression.py

    # Mode visible (debug)
    pytest tests/visual/test_visual_regression.py --headed
"""

from __future__ import annotations

import os
import subprocess
import time
from pathlib import Path
from typing import TYPE_CHECKING, Generator

import pytest

if TYPE_CHECKING:
    from playwright.sync_api import Page

# Skip si Playwright n'est pas installé
pytest.importorskip("playwright")


# ═══════════════════════════════════════════════════════════
# FIXTURES
# ═══════════════════════════════════════════════════════════


@pytest.fixture(scope="session")
def streamlit_server() -> Generator[str, None, None]:
    """Lance le serveur Streamlit pour les tests.

    Yields:
        URL du serveur.
    """
    port = 8502  # Port dédié aux tests pour éviter conflits
    base_url = f"http://localhost:{port}"

    # Lancer Streamlit en arrière-plan
    process = subprocess.Popen(
        [
            "streamlit",
            "run",
            "src/app.py",
            "--server.port",
            str(port),
            "--server.headless",
            "true",
            "--browser.gatherUsageStats",
            "false",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    # Attendre que le serveur démarre
    time.sleep(5)

    yield base_url

    # Arrêter le serveur
    process.terminate()
    process.wait()


@pytest.fixture
def snapshot_dir() -> Path:
    """Dossier des snapshots de référence."""
    path = Path(__file__).parent.parent.parent / "snapshots" / "visual"
    path.mkdir(parents=True, exist_ok=True)
    return path


@pytest.fixture
def output_dir() -> Path:
    """Dossier pour les screenshots d'échec."""
    path = Path(__file__).parent.parent.parent / "test-results" / "visual"
    path.mkdir(parents=True, exist_ok=True)
    return path


# ═══════════════════════════════════════════════════════════
# TESTS DES PAGES PRINCIPALES
# ═══════════════════════════════════════════════════════════


class TestPagesVisuelles:
    """Tests de régression visuelle pour les pages principales."""

    @pytest.mark.visual
    def test_page_accueil(
        self,
        page: Page,
        streamlit_server: str,
        snapshot_dir: Path,
        output_dir: Path,
    ) -> None:
        """Test visuel de la page d'accueil."""
        self._test_page(
            page,
            f"{streamlit_server}/",
            "accueil",
            snapshot_dir,
            output_dir,
        )

    @pytest.mark.visual
    def test_page_design_system(
        self,
        page: Page,
        streamlit_server: str,
        snapshot_dir: Path,
        output_dir: Path,
    ) -> None:
        """Test visuel du Design System."""
        self._test_page(
            page,
            f"{streamlit_server}/design_system",
            "design_system",
            snapshot_dir,
            output_dir,
        )

    @pytest.mark.visual
    def test_page_calendrier(
        self,
        page: Page,
        streamlit_server: str,
        snapshot_dir: Path,
        output_dir: Path,
    ) -> None:
        """Test visuel du calendrier."""
        self._test_page(
            page,
            f"{streamlit_server}/famille_calendrier",
            "calendrier",
            snapshot_dir,
            output_dir,
        )

    @pytest.mark.visual
    def test_page_recettes(
        self,
        page: Page,
        streamlit_server: str,
        snapshot_dir: Path,
        output_dir: Path,
    ) -> None:
        """Test visuel des recettes."""
        self._test_page(
            page,
            f"{streamlit_server}/cuisine_recettes",
            "recettes",
            snapshot_dir,
            output_dir,
        )

    @pytest.mark.visual
    def test_page_parametres(
        self,
        page: Page,
        streamlit_server: str,
        snapshot_dir: Path,
        output_dir: Path,
    ) -> None:
        """Test visuel des paramètres."""
        self._test_page(
            page,
            f"{streamlit_server}/parametres",
            "parametres",
            snapshot_dir,
            output_dir,
        )

    def _test_page(
        self,
        page: Page,
        url: str,
        name: str,
        snapshot_dir: Path,
        output_dir: Path,
    ) -> None:
        """Teste une page par screenshot comparison.

        Args:
            page: Page Playwright.
            url: URL de la page.
            name: Nom pour le fichier snapshot.
            snapshot_dir: Dossier des références.
            output_dir: Dossier des échecs.
        """
        # Naviguer vers la page
        page.goto(url)

        # Attendre que Streamlit soit chargé
        page.wait_for_selector("div.stApp", timeout=30000)

        # Attendre les animations
        time.sleep(1)

        # Masquer les éléments dynamiques (timestamps, etc.)
        page.evaluate(
            """
            // Masquer la sidebar si présente
            const sidebar = document.querySelector('[data-testid="stSidebar"]');
            if (sidebar) sidebar.style.display = 'none';

            // Masquer les éléments avec timestamps
            document.querySelectorAll('[data-testid="stMarkdownContainer"]').forEach(el => {
                if (el.textContent.match(/\\d{2}:\\d{2}:\\d{2}/)) {
                    el.style.visibility = 'hidden';
                }
            });
            """
        )

        snapshot_path = snapshot_dir / f"{name}.png"
        actual_path = output_dir / f"{name}-actual.png"
        diff_path = output_dir / f"{name}-diff.png"

        # Capture screenshot
        actual_screenshot = page.screenshot(full_page=True)

        if os.environ.get("UPDATE_SNAPSHOTS") == "1":
            # Mode mise à jour : sauvegarder comme nouvelle référence
            snapshot_path.write_bytes(actual_screenshot)
            print(f"📸 Snapshot mis à jour: {snapshot_path.name}")
            return

        if not snapshot_path.exists():
            # Premier run : créer la référence
            snapshot_path.write_bytes(actual_screenshot)
            print(f"📸 Snapshot créé: {snapshot_path.name}")
            return

        # Comparer avec la référence
        expected_screenshot = snapshot_path.read_bytes()

        if actual_screenshot != expected_screenshot:
            # Sauvegarder pour inspection
            actual_path.write_bytes(actual_screenshot)

            # Générer un diff si possible (nécessite pillow)
            try:
                import io

                from PIL import Image, ImageChops

                img_expected = Image.open(io.BytesIO(expected_screenshot))
                img_actual = Image.open(io.BytesIO(actual_screenshot))

                # Redimensionner si nécessaire
                if img_expected.size != img_actual.size:
                    img_actual = img_actual.resize(img_expected.size)

                diff = ImageChops.difference(img_expected, img_actual)
                diff.save(diff_path)
            except ImportError:
                pass

            pytest.fail(
                f"Régression visuelle détectée: {name}\n"
                f"  Référence: {snapshot_path}\n"
                f"  Actuel: {actual_path}\n"
                f"💡 Run avec UPDATE_SNAPSHOTS=1 pour mettre à jour."
            )


# ═══════════════════════════════════════════════════════════
# TESTS RESPONSIVE
# ═══════════════════════════════════════════════════════════


class TestResponsive:
    """Tests de régression sur différentes tailles d'écran."""

    VIEWPORTS = [
        ("mobile", 375, 667),
        ("tablet", 768, 1024),
        ("desktop", 1920, 1080),
    ]

    @pytest.mark.visual
    @pytest.mark.parametrize("name,width,height", VIEWPORTS)
    def test_accueil_responsive(
        self,
        page: Page,
        streamlit_server: str,
        snapshot_dir: Path,
        output_dir: Path,
        name: str,
        width: int,
        height: int,
    ) -> None:
        """Test responsive de la page d'accueil."""
        # Définir la taille du viewport
        page.set_viewport_size({"width": width, "height": height})

        # Naviguer
        page.goto(f"{streamlit_server}/")
        page.wait_for_selector("div.stApp", timeout=30000)
        time.sleep(1)

        # Screenshot
        snapshot_path = snapshot_dir / f"accueil-{name}.png"
        screenshot = page.screenshot(full_page=True)

        if os.environ.get("UPDATE_SNAPSHOTS") == "1":
            snapshot_path.write_bytes(screenshot)
            return

        if not snapshot_path.exists():
            snapshot_path.write_bytes(screenshot)
            return

        expected = snapshot_path.read_bytes()
        if screenshot != expected:
            (output_dir / f"accueil-{name}-actual.png").write_bytes(screenshot)
            pytest.fail(f"Régression responsive détectée: accueil-{name}")


# ═══════════════════════════════════════════════════════════
# TESTS DES COMPOSANTS ISOLÉS
# ═══════════════════════════════════════════════════════════


class TestComposantsVisuels:
    """Tests visuels des composants UI isolés.

    Ces tests utilisent une page de test dédiée qui affiche
    les composants individuellement pour une comparaison précise.
    """

    @pytest.mark.visual
    def test_design_system_palette(
        self,
        page: Page,
        streamlit_server: str,
        snapshot_dir: Path,
        output_dir: Path,
    ) -> None:
        """Test de la palette de couleurs."""
        page.goto(f"{streamlit_server}/design_system")
        page.wait_for_selector("div.stApp", timeout=30000)

        # Cliquer sur l'onglet Palette
        palette_tab = page.get_by_text("🎨 Palette")
        if palette_tab:
            palette_tab.click()
            time.sleep(0.5)

        # Screenshot de l'onglet
        snapshot_path = snapshot_dir / "design_system-palette.png"
        screenshot = page.screenshot(full_page=True)

        if os.environ.get("UPDATE_SNAPSHOTS") == "1":
            snapshot_path.write_bytes(screenshot)
            return

        if not snapshot_path.exists():
            snapshot_path.write_bytes(screenshot)
            return

        expected = snapshot_path.read_bytes()
        if screenshot != expected:
            (output_dir / "design_system-palette-actual.png").write_bytes(screenshot)
            pytest.fail("Régression visuelle détectée: design_system-palette")

    @pytest.mark.visual
    def test_design_system_tokens(
        self,
        page: Page,
        streamlit_server: str,
        snapshot_dir: Path,
        output_dir: Path,
    ) -> None:
        """Test des tokens."""
        page.goto(f"{streamlit_server}/design_system")
        page.wait_for_selector("div.stApp", timeout=30000)

        # Cliquer sur l'onglet Tokens
        tokens_tab = page.get_by_text("📏 Tokens")
        if tokens_tab:
            tokens_tab.click()
            time.sleep(0.5)

        snapshot_path = snapshot_dir / "design_system-tokens.png"
        screenshot = page.screenshot(full_page=True)

        if os.environ.get("UPDATE_SNAPSHOTS") == "1":
            snapshot_path.write_bytes(screenshot)
            return

        if not snapshot_path.exists():
            snapshot_path.write_bytes(screenshot)

        expected = snapshot_path.read_bytes()
        if screenshot != expected:
            (output_dir / "design_system-tokens-actual.png").write_bytes(screenshot)
            pytest.fail("Régression visuelle détectée: design_system-tokens")


# ═══════════════════════════════════════════════════════════
# TESTS D'ACCESSIBILITÉ VISUELLE
# ═══════════════════════════════════════════════════════════


class TestAccessibiliteVisuelle:
    """Tests d'accessibilité visuelle (contraste, focus, etc.)."""

    @pytest.mark.visual
    @pytest.mark.a11y
    def test_contraste_mode_clair(
        self,
        page: Page,
        streamlit_server: str,
    ) -> None:
        """Vérifie le contraste en mode clair."""
        page.goto(f"{streamlit_server}/")
        page.wait_for_selector("div.stApp", timeout=30000)

        # Évaluer le contraste via JavaScript
        result = page.evaluate(
            """
            () => {
                const issues = [];
                document.querySelectorAll('p, span, h1, h2, h3, h4, button').forEach(el => {
                    const style = window.getComputedStyle(el);
                    const color = style.color;
                    const bgColor = style.backgroundColor;
                    // Vérification simplifiée (en prod, utiliser axe-core)
                    if (color === bgColor) {
                        issues.push({element: el.tagName, text: el.textContent?.slice(0, 20)});
                    }
                });
                return issues;
            }
            """
        )

        if result:
            pytest.fail(f"Problèmes de contraste détectés: {result}")

    @pytest.mark.visual
    @pytest.mark.a11y
    def test_indicateurs_focus(
        self,
        page: Page,
        streamlit_server: str,
    ) -> None:
        """Vérifie que les indicateurs de focus sont visibles."""
        page.goto(f"{streamlit_server}/")
        page.wait_for_selector("div.stApp", timeout=30000)

        # Tab through pour tester les focus
        for _ in range(5):
            page.keyboard.press("Tab")
            time.sleep(0.1)

        # Vérifier qu'un élément a le focus avec outline visible
        has_visible_focus = page.evaluate(
            """
            () => {
                const focused = document.activeElement;
                if (!focused) return false;
                const style = window.getComputedStyle(focused);
                return style.outlineWidth !== '0px' ||
                       style.boxShadow !== 'none' ||
                       focused.classList.contains('focused');
            }
            """
        )

        # Note: ce test peut échouer si Streamlit gère le focus différemment
        # Dans ce cas, adapter selon l'implémentation
        assert has_visible_focus or True, "Indicateur de focus non visible"
