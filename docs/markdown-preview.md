# Configuration: ouverture automatique des fichiers Markdown en preview

Ce dépôt contient une configuration VS Code pour ouvrir automatiquement les fichiers `*.md` en mode preview (onglet unique).

Fichiers ajoutés:
- `.vscode/settings.json` — association `*.md` → preview intégré
- `.vscode/extensions.json` — recommandations d'extensions Markdown utiles

Si la preview ne s'ouvre pas automatiquement:
1. Ouvrir la palette de commandes (Ctrl+Shift+P) → `Open With...` → choisir **Markdown Preview** → cocher _Remember my choice_.
2. Redémarrer VS Code ou recharger la fenêtre (`Developer: Reload Window`).

Commandes utiles:
- `Markdown: Open Preview` — ouvrir la preview
- `Markdown: Open Preview to the Side` — ouvrir en side-by-side

Pour revenir à l'éditeur par défaut, supprimer/éditer la clé `workbench.editorAssociations` dans `.vscode/settings.json`.
