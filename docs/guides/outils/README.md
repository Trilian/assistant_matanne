# 🛠️ Guide Module Outils

> Ce guide couvre les outils pratiques dans MaTanne : chat IA, météo, convertisseur d'unités, minuteur, et prise de notes.

## Table des matières

1. [Vue d'ensemble](#vue-densemble)
2. [Chat IA](#chat-ia)
3. [Météo](#météo)
4. [Convertisseur d'unités](#convertisseur-dunités)
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

### Fonctionnalités

- Interface de conversation libre avec l'IA Mistral
- Contexte familial injecté automatiquement (profil Jules, recettes récentes, planning)
- Historique de conversation persisté en session
- Suggestions de questions rapides (raccourcis)
- Mode streaming pour les réponses longues

### Usage

```
/outils/chat-ia
```

### Exemples de questions

- *"Qu'est-ce qu'on peut cuisiner ce soir avec ce qu'on a dans le frigo ?"*
- *"Donne-moi des activités pour un enfant de 18 mois par temps de pluie"*
- *"Rappelle-moi les tâches d'entretien à faire ce mois-ci"*

### Architecture

```
Frontend → POST /api/v1/utilitaires/chat
         → src/services/utilitaires/service.py
         → src/core/ai/client.py (Mistral)
         → Réponse streaming (Server-Sent Events)
```

### Backend

```python
from src.services.utilitaires.service import UtilitairesService
service = UtilitairesService()
reponse = service.chat_ia(message="Idées repas rapides", contexte_famille=True)
```

---

## Météo

### Fonctionnalités

- Météo actuelle et prévisions 7 jours
- Basé sur la localisation configurée dans les paramètres
- Alertes météo (orage, canicule, gel)
- Conseils jardin adaptés à la météo
- Données utilisées par d'autres modules (planning arrosage, suggestions week-end)

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

### Sources de données

Le service météo (`src/services/integrations/weather/`) agrège plusieurs APIs météo avec fallback automatique.

---

## Convertisseur d'unités

### Fonctionnalités

- Conversion entre unités de mesure courantes en cuisine :
  - **Volumes** : ml, cl, dl, L, cuillère à café, cuillère à soupe, tasse
  - **Poids** : g, kg, oz, lb
  - **Températures** : Celsius, Fahrenheit, Gas
- Conversion rapide de devises (taux de change temps réel)
- Interface intuitive avec saisie d'une valeur et sélection des unités

### Usage

```
/outils/convertisseur
```

### Exemple

```
500 ml → 2.11 tasses (US)
180°C → 350°F → Thermostat 6
250g flour → 2 cups
```

---

## Minuteur

### Fonctionnalités

- Minuteur compte à rebours avec notifications push à l'expiration
- Chronomètre
- Minuteurs nommés simultanés (ex: "Pâtes", "Sauce")
- Préréglages rapides (3 min, 5 min, 10 min, 15 min)
- Fonctionne en arrière-plan (Service Worker)

### Usage

```
/outils/minuteur
```

### PWA

Le minuteur utilise le Service Worker (`public/sw.js`) pour continuer à fonctionner même quand l'onglet est en arrière-plan. La notification arrive via l'API Web Notifications.

---

## Notes

### Fonctionnalités

- Prise de notes rapide en texte libre
- Organisation par catégorie ou tag
- Recherche full-text dans les notes
- Notes épinglées en haut de liste
- Persistance locale + synchronisation avec le backend

### Usage

```
/outils/notes
```

### Modèle de données

```python
# Persisté en DB via src/core/models/utilitaires.py
class Note(Base):
    titre: str
    contenu: str         # Markdown supporté
    tags: list[str]
    epinglee: bool
    user_id: int
    created_at: datetime
    updated_at: datetime
```

---

## API Reference

### Endpoints principaux

| Méthode | URL                          | Description                        |
|--------|------------------------------|------------------------------------|
| POST   | `/api/v1/utilitaires/chat`   | Chat IA (streaming SSE)            |
| GET    | `/api/v1/utilitaires/meteo`  | Météo actuelle + prévisions        |
| GET    | `/api/v1/utilitaires/convertir` | Conversion d'unités             |
| GET    | `/api/v1/utilitaires/notes`  | Lister les notes                   |
| POST   | `/api/v1/utilitaires/notes`  | Créer une note                     |
| PUT    | `/api/v1/utilitaires/notes/{id}` | Modifier une note              |
| DELETE | `/api/v1/utilitaires/notes/{id}` | Supprimer une note             |

Voir [API_REFERENCE.md](../API_REFERENCE.md) pour la documentation complète.
