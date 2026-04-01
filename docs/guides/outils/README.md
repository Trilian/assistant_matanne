# ðŸ› ï¸ Guide Module Outils

> Ce guide couvre les outils pratiques dans MaTanne : chat IA, mÃ©tÃ©o, convertisseur d'unitÃ©s, minuteur, et prise de notes.

## Table des matiÃ¨res

1. [Vue d'ensemble](#vue-densemble)
2. [Chat IA](#chat-ia)
3. [MÃ©tÃ©o](#mÃ©tÃ©o)
4. [Convertisseur d'unitÃ©s](#convertisseur-dunitÃ©s)
5. [Minuteur](#minuteur)
6. [Notes](#notes)
7. [API Reference](#api-reference)

---

## Vue d'ensemble

Le module **Outils** regroupe les utilitaires pratiques du quotidien, accessibles rapidement depuis la navigation.

**URL** : `/outils`  
**Service backend** : `src/services/utilitaires/`  
**Route API** : `src/api/routes/utilitaires.py` (`/api/v1/utilitaires`)

---

## Chat IA

### FonctionnalitÃ©s

- Interface de conversation libre avec l'IA Mistral
- Contexte familial injectÃ© automatiquement (profil Jules, recettes rÃ©centes, planning)
- Historique de conversation persistÃ© en session
- Suggestions de questions rapides (raccourcis)
- Mode streaming pour les rÃ©ponses longues

### Usage

```
/outils/chat-ia
```

### Exemples de questions

- *"Qu'est-ce qu'on peut cuisiner ce soir avec ce qu'on a dans le frigo ?"*
- *"Donne-moi des activitÃ©s pour un enfant de 18 mois par temps de pluie"*
- *"Rappelle-moi les tÃ¢ches d'entretien Ã  faire ce mois-ci"*

### Architecture

```
Frontend â†’ POST /api/v1/utilitaires/chat
         â†’ src/services/utilitaires/service.py
         â†’ src/core/ai/client.py (Mistral)
         â†’ RÃ©ponse streaming (Server-Sent Events)
```

### Backend

```python
from src.services.utilitaires.service import UtilitairesService
service = UtilitairesService()
reponse = service.chat_ia(message="IdÃ©es repas rapides", contexte_famille=True)
```

---

## MÃ©tÃ©o

### FonctionnalitÃ©s

- MÃ©tÃ©o actuelle et prÃ©visions 7 jours
- BasÃ© sur la localisation configurÃ©e dans les paramÃ¨tres
- Alertes mÃ©tÃ©o (orage, canicule, gel)
- Conseils jardin adaptÃ©s Ã  la mÃ©tÃ©o
- DonnÃ©es utilisÃ©es par d'autres modules (planning arrosage, suggestions week-end)

### Usage

```
/outils/meteo
```

### Service

```python
from src.services.integrations.weather import ServiceMeteo, obtenir_service_meteo
service = obtenir_service_meteo()
meteo = service.obtenir_meteo_actuelle(ville="Paris")
previsions = service.obtenir_previsions(ville="Paris", jours=7)
```

### Sources de donnÃ©es

Le service mÃ©tÃ©o (`src/services/integrations/weather/`) agrÃ¨ge plusieurs APIs mÃ©tÃ©o avec fallback automatique.

---

## Convertisseur d'unitÃ©s

### FonctionnalitÃ©s

- Conversion entre unitÃ©s de mesure courantes en cuisine :
  - **Volumes** : ml, cl, dl, L, cuillÃ¨re Ã  cafÃ©, cuillÃ¨re Ã  soupe, tasse
  - **Poids** : g, kg, oz, lb
  - **TempÃ©ratures** : Celsius, Fahrenheit, Gas
- Conversion rapide de devises (taux de change temps rÃ©el)
- Interface intuitive avec saisie d'une valeur et sÃ©lection des unitÃ©s

### Usage

```
/outils/convertisseur
```

### Exemple

```
500 ml â†’ 2.11 tasses (US)
180Â°C â†’ 350Â°F â†’ Thermostat 6
250g flour â†’ 2 cups
```

---

## Minuteur

### FonctionnalitÃ©s

- Minuteur compte Ã  rebours avec notifications push Ã  l'expiration
- ChronomÃ¨tre
- Minuteurs nommÃ©s simultanÃ©s (ex: "PÃ¢tes", "Sauce")
- PrÃ©rÃ©glages rapides (3 min, 5 min, 10 min, 15 min)
- Fonctionne en arriÃ¨re-plan (Service Worker)

### Usage

```
/outils/minuteur
```

### PWA

Le minuteur utilise le Service Worker (`public/sw.js`) pour continuer Ã  fonctionner mÃªme quand l'onglet est en arriÃ¨re-plan. La notification arrive via l'API Web Notifications.

---

## Notes

### FonctionnalitÃ©s

- Prise de notes rapide en texte libre
- Organisation par catÃ©gorie ou tag
- Recherche full-text dans les notes
- Notes Ã©pinglÃ©es en haut de liste
- Persistance locale + synchronisation avec le backend

### Usage

```
/outils/notes
```

### ModÃ¨le de donnÃ©es

```python
# PersistÃ© en DB via src/core/models/utilitaires.py
class Note(Base):
    titre: str
    contenu: str         # Markdown supportÃ©
    tags: list[str]
    epinglee: bool
    user_id: int
    created_at: datetime
    updated_at: datetime
```

---

## API Reference

### Endpoints principaux

| MÃ©thode | URL                          | Description                        |
| -------- | ------------------------------ | ------------------------------------ |
| POST   | `/api/v1/utilitaires/chat`   | Chat IA (streaming SSE)            |
| GET    | `/api/v1/utilitaires/meteo`  | MÃ©tÃ©o actuelle + prÃ©visions        |
| GET    | `/api/v1/utilitaires/convertir` | Conversion d'unitÃ©s             |
| GET    | `/api/v1/utilitaires/notes`  | Lister les notes                   |
| POST   | `/api/v1/utilitaires/notes`  | CrÃ©er une note                     |
| PUT    | `/api/v1/utilitaires/notes/{id}` | Modifier une note              |
| DELETE | `/api/v1/utilitaires/notes/{id}` | Supprimer une note             |

Voir [API_REFERENCE.md](../API_REFERENCE.md) pour la documentation complÃ¨te.
