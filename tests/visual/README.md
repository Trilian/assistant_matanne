# Tests Visuels avec Playwright

Ce dossier contient les tests de régression visuelle pour l'UI de l'application
Assistant Matanne. Les tests utilisent Playwright pour capturer des screenshots
et les comparer aux références.

## Installation

```bash
# Installer Playwright
pip install playwright pytest-playwright

# Installer les navigateurs
playwright install chromium
```

## Exécution des tests

```bash
# Lancer tous les tests visuels
pytest tests/visual/ -m visual

# Mode visible (pour debug)
pytest tests/visual/ -m visual --headed

# Uniquement les tests responsive
pytest tests/visual/test_visual_regression.py::TestResponsive

# Tests d'accessibilité
pytest tests/visual/ -m a11y
```

## Mise à jour des snapshots

Quand un changement d'UI est intentionnel :

```bash
# Mettre à jour tous les snapshots
UPDATE_SNAPSHOTS=1 pytest tests/visual/ -m visual

# Ou en PowerShell
$env:UPDATE_SNAPSHOTS="1"; pytest tests/visual/ -m visual
```

## Structure des fichiers

```
tests/visual/
├── conftest.py                 # Configuration Playwright
├── test_visual_regression.py   # Tests principaux
└── README.md                   # Ce fichier

tests/snapshots/visual/         # Screenshots de référence (générés)
├── accueil.png
├── design_system.png
├── accueil-mobile.png
└── ...

tests/test-results/visual/      # Screenshots d'échec (gitignored)
├── accueil-actual.png
├── accueil-diff.png
└── ...
```

## Bonnes pratiques

1. **Premier run** : Les snapshots sont créés automatiquement
2. **CI/CD** : Commit les snapshots dans `tests/snapshots/`
3. **Review** : Vérifier visuellement les diffs avant UPDATE
4. **Isolation** : Utiliser un port dédié (8502) pour les tests

## Ajouter un nouveau test

```python
@pytest.mark.visual
def test_ma_page(
    self,
    page: "Page",
    streamlit_server: str,
    snapshot_dir: Path,
    output_dir: Path,
) -> None:
    """Test visuel de ma page."""
    self._test_page(
        page,
        f"{streamlit_server}/ma_page",
        "ma_page",
        snapshot_dir,
        output_dir,
    )
```
