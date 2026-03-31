# 🛠️ Module Utilitaires

Outils transversaux : scanner codes-barres, commandes vocales, et fonctions helpers partagées.

## Fonctionnalités

| Outil | Description | Page frontend |
|---|---|---|
| 📷 Scanner codes-barres | Scan WebRTC / photo / saisie manuelle → inventaire & courses | `/outils/scanner` |
| 🎤 Commandes vocales | Pilotage vocal (Web Speech API) — courses, inventaire, recettes, navigation | `/outils/vocal` |

## API Backend

| Méthode | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/utilitaires/barcode-lookup` | Recherche produit par code EAN (OpenFoodFacts) |
| `POST` | `/api/v1/utilitaires/voice-command` | Parse et exécute une commande vocale |
| `GET`  | `/api/v1/utilitaires/search` | Recherche globale multi-domaines |

## Guides détaillés

- [Scanner Codes-barres](barcode.md) — Modes de scan, formats supportés, OpenFoodFacts, dépannage
- [Commandes Vocales](vocal.md) — Commandes reconnues, configuration micro, exemples
- [Google Assistant](../../GOOGLE_ASSISTANT_SETUP.md) — Intents disponibles, webhook fulfillment, sécurité, tests curl

## Architecture

```
src/api/routes/utilitaires.py       # Router FastAPI
src/api/schemas/utilitaires.py      # Schémas Pydantic
frontend/src/app/(app)/outils/      # Pages Next.js (scanner, vocal, etc.)
```
