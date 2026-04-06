# 🛠️ Module Utilitaires

Outils transversaux : chat IA, convertisseur, météo, minuteur, notes et fonctions helpers partagées.

## Fonctionnalités

| Outil | Description | Page frontend |
| --- | --- | --- |
| 🤖 Chat IA | Assistant conversationnel Mistral | /outils/chat-ia |
| 🔄 Convertisseur | Conversion d''unités de mesure | /outils/convertisseur |
| 🌤️ Météo | Prévisions météo locales | /outils/meteo |
| ⏱️ Minuteur | Minuteur de cuisine | /outils/minuteur |
| 📝 Notes | Bloc-notes rapide | /outils/notes |

## API Backend

| Méthode | Endpoint | Description |
| --- | --- | --- |
| GET  | /api/v1/utilitaires/search | Recherche globale multi-domaines |

## Guides détaillés

- [Google Assistant](../../GOOGLE_ASSISTANT_SETUP.md) — Intents disponibles, webhook fulfillment, sécurité, tests curl

## Architecture

`
src/api/routes/utilitaires.py       # Router FastAPI
src/api/schemas/utilitaires.py      # Schémas Pydantic
frontend/src/app/(app)/outils/      # Pages Next.js (chat-ia, convertisseur, meteo, minuteur, notes)
`
