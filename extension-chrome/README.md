# Extension Chrome — Assistant Matanne

Mini extension utilitaire pour relier le navigateur à l'écosystème Assistant Matanne.

## Contenu

- `manifest.json` — manifeste de l'extension
- `background.js` — logique de fond
- `content.js` — injection sur les pages ciblées
- `bridge.js` — pont de communication avec l'application
- `popup.html` / `popup.js` / `popup.css` — interface popup

## Installation locale

1. Ouvrir `chrome://extensions`
2. Activer **Mode développeur**
3. Cliquer sur **Charger l’extension non empaquetée**
4. Sélectionner le dossier `extension-chrome/`

## Remarques

- Usage local / expérimental
- Vérifier les permissions déclarées dans `manifest.json` avant toute publication
- Toute évolution fonctionnelle doit être documentée dans `docs/CHANGELOG.md`
