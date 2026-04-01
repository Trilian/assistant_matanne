# ðŸ› ï¸ Module Utilitaires

Outils transversaux : scanner codes-barres, commandes vocales, et fonctions helpers partagÃ©es.

## FonctionnalitÃ©s

| Outil | Description | Page frontend |
| --- | --- | --- |
| ðŸ“· Scanner codes-barres | Scan WebRTC / photo / saisie manuelle â†’ inventaire & courses | `/outils/scanner` |
| ðŸŽ¤ Commandes vocales | Pilotage vocal (Web Speech API) â€” courses, inventaire, recettes, navigation | `/outils/vocal` |

## API Backend

| MÃ©thode | Endpoint | Description |
| --- | --- | --- |
| `POST` | `/api/v1/utilitaires/barcode-lookup` | Recherche produit par code EAN (OpenFoodFacts) |
| `POST` | `/api/v1/utilitaires/voice-command` | Parse et exÃ©cute une commande vocale |
| `GET`  | `/api/v1/utilitaires/search` | Recherche globale multi-domaines |

## Guides dÃ©taillÃ©s

- [Scanner Codes-barres](barcode.md) â€” Modes de scan, formats supportÃ©s, OpenFoodFacts, dÃ©pannage
- [Commandes Vocales](vocal.md) â€” Commandes reconnues, configuration micro, exemples
- [Google Assistant](../../GOOGLE_ASSISTANT_SETUP.md) â€” Intents disponibles, webhook fulfillment, sÃ©curitÃ©, tests curl

## Architecture

```
src/api/routes/utilitaires.py       # Router FastAPI
src/api/schemas/utilitaires.py      # SchÃ©mas Pydantic
frontend/src/app/(app)/outils/      # Pages Next.js (scanner, vocal, etc.)
```
