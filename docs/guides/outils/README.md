# ??? Guide Module Outils

> Ce guide couvre les outils pratiques dans MaTanne : chat IA, m�t�o, convertisseur d'unit�s, minuteur, et prise de notes.

## Table des mati�res

1. [Vue d'ensemble](#vue-densemble)
2. [Chat IA](#chat-ia)
3. [M�t�o](#m�t�o)
4. [Convertisseur d'unit�s](#convertisseur-dunit�s)
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

### Fonctionnalit�s

- Interface de conversation libre avec l'IA Mistral
- Contexte familial inject� automatiquement (profil Jules, recettes r�centes, planning)
- Historique de conversation persist� en session
- Suggestions de questions rapides (raccourcis)
- Mode streaming pour les r�ponses longues

### Usage

```
/outils/chat-ia
```

### Exemples de questions

- *"Qu'est-ce qu'on peut cuisiner ce soir avec ce qu'on a dans le frigo ?"*
- *"Donne-moi des activit�s pour un enfant de 18 mois par temps de pluie"*
- *"Rappelle-moi les t�ches d'entretien � faire ce mois-ci"*

### Architecture

```
Frontend ? POST /api/v1/utilitaires/chat
         ? src/services/utilitaires/service.py
         ? src/core/ai/client.py (Mistral)
         ? R�ponse streaming (Server-Sent Events)
```

### Backend

```python
from src.services.utilitaires.service import UtilitairesService
service = UtilitairesService()
reponse = service.chat_ia(message="Id�es repas rapides", contexte_famille=True)
```

---

## M�t�o

### Fonctionnalit�s

- M�t�o actuelle et pr�visions 7 jours
- Bas� sur la localisation configur�e dans les param�tres
- Alertes m�t�o (orage, canicule, gel)
- Conseils jardin adapt�s � la m�t�o
- Donn�es utilis�es par d'autres modules (planning arrosage, suggestions week-end)

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

### Sources de donn�es

Le service m�t�o (`src/services/integrations/weather/`) agr�ge plusieurs APIs m�t�o avec fallback automatique.

---

## Convertisseur d'unit�s

### Fonctionnalit�s

- Conversion entre unit�s de mesure courantes en cuisine :
  - **Volumes** : ml, cl, dl, L, cuill�re � caf�, cuill�re � soupe, tasse
  - **Poids** : g, kg, oz, lb
  - **Temp�ratures** : Celsius, Fahrenheit, Gas
- Conversion rapide de devises (taux de change temps r�el)
- Interface intuitive avec saisie d'une valeur et s�lection des unit�s

### Usage

```
/outils/convertisseur
```

### Exemple

```
500 ml ? 2.11 tasses (US)
180�C ? 350�F ? Thermostat 6
250g flour ? 2 cups
```

---

## Minuteur

### Fonctionnalit�s

- Minuteur compte � rebours avec notifications push � l'expiration
- Chronom�tre
- Minuteurs nomm�s simultan�s (ex: "P�tes", "Sauce")
- Pr�r�glages rapides (3 min, 5 min, 10 min, 15 min)
- Fonctionne en arri�re-plan (Service Worker)

### Usage

```
/outils/minuteur
```

### PWA

Le minuteur utilise le Service Worker (`public/sw.js`) pour continuer � fonctionner m�me quand l'onglet est en arri�re-plan. La notification arrive via l'API Web Notifications.

---

## Notes

### Fonctionnalit�s

- Prise de notes rapide en texte libre
- Organisation par cat�gorie ou tag
- Recherche full-text dans les notes
- Notes �pingl�es en haut de liste
- Persistance locale + synchronisation avec le backend

### Usage

```
/outils/notes
```

### Mod�le de donn�es

```python
# Persist� en DB via src/core/models/utilitaires.py
class Note(Base):
    titre: str
    contenu: str         # Markdown support�
    tags: list[str]
    epinglee: bool
    user_id: int
    created_at: datetime
    updated_at: datetime
```

---

## API Reference

### Endpoints principaux

| M�thode | URL                          | Description                        |
| -------- | ------------------------------ | ------------------------------------ |
| POST   | `/api/v1/utilitaires/chat`   | Chat IA (streaming SSE)            |
| GET    | `/api/v1/utilitaires/meteo`  | M�t�o actuelle + pr�visions        |
| GET    | `/api/v1/utilitaires/convertir` | Conversion d'unit�s             |
| GET    | `/api/v1/utilitaires/notes`  | Lister les notes                   |
| POST   | `/api/v1/utilitaires/notes`  | Cr�er une note                     |
| PUT    | `/api/v1/utilitaires/notes/{id}` | Modifier une note              |
| DELETE | `/api/v1/utilitaires/notes/{id}` | Supprimer une note             |

Voir [API_REFERENCE.md](../API_REFERENCE.md) pour la documentation compl�te.
