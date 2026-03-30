# Gamification — Sport + Nutrition

> **Périmètre volontairement limité** : La gamification sert uniquement à inciter à **faire du sport** et **bien manger**. Aucun badge/point pour d'autres modules.

---

## Architecture

```
Backend
├── src/core/models/gamification.py        # Modèles ORM (PointsUtilisateur, BadgeUtilisateur)
├── src/services/dashboard/points_famille.py  # Calcul des points hebdo
├── src/services/dashboard/badges_triggers.py # Triggers badges sport + nutrition
├── src/services/core/cron/jobs.py         # Job CRON hebdo (dim 20h)
└── src/api/routes/dashboard.py            # Endpoints API gamification

Frontend
├── frontend/src/app/(app)/famille/gamification/page.tsx  # Page détail
└── frontend/src/bibliotheque/api/tableau-bord.ts         # Client API
```

---

## Points hebdomadaires

Les points sont calculés chaque dimanche à 20h via le job CRON `points_famille_hebdo`.

### Calcul

| Catégorie | Formule | Max |
|-----------|---------|-----|
| **Sport** | `min(300, nb_activités × 40 + calories_actives ÷ 20 + total_pas ÷ 1000)` | 300 |
| **Alimentation** | `min(300, score_bien_être × 3)` | 300 |
| **Anti-gaspi** | `max(0, 200 - articles_à_risque × 15)` | 200 |

**Total max** : 800 points/semaine

### Sources de données

- **Garmin** : `ActiviteGarmin` (sessions sport) + `ResumeQuotidienGarmin` (pas, calories)
- **Score bien-être** : Score composite alimentation (diversité + nutri-score + activités)
- **Inventaire** : Articles proches de la date de péremption (±3 jours)

### Persistance

Snapshot hebdomadaire dans `points_utilisateurs` (unique par `user_id + semaine_debut`).

---

## Badges

### Catalogue complet

#### Badges Sport

| Badge | Emoji | Type | Condition | Seuil |
|-------|-------|------|-----------|-------|
| **Marcheur régulier** | 🚶 | `marcheur_regulier` | ≥ 8 000 pas/jour pendant 7 jours consécutifs | 7 jours |
| **Marathonien** | 🏃 | `marathonien` | ≥ 12 000 pas/jour pendant 7 jours consécutifs | 7 jours |
| **Sportif assidu** | 💪 | `sportif_hebdo` | ≥ 4 sessions sport dans la semaine | 4 sessions |
| **Brûleur de calories** | 🔥 | `bruleur_calories` | ≥ 2 500 calories actives dans la semaine | 2 500 kcal |
| **Athlète complet** | 🏅 | `athlete_complet` | ≥ 3 types d'activités différentes | 3 types |
| **Bougeotte** | ⚡ | `bougeotte` | ≥ 180 points sport dans la semaine | 180 pts |

#### Badges Nutrition

| Badge | Emoji | Type | Condition | Seuil |
|-------|-------|------|-----------|-------|
| **Planning équilibré** | 🥗 | `planning_equilibre` | ≥ 5 jours avec repas planifiés | 5 jours |
| **Nutritionniste** | 🍎 | `nutritionniste` | Score bien-être ≥ 75 | 75 |
| **Assiette futée** | 🧠 | `assiette_futee` | ≥ 220 points alimentation | 220 pts |
| **Zéro gaspi** | ♻️ | `zero_gaspi` | 0 article expiré dans la semaine | 0 articles |
| **Diversité alimentaire** | 🌈 | `diversite_alimentaire` | ≥ 5 catégories d'aliments | 5 catégories |
| **Champion anti-gaspi** | 🏆 | `anti_gaspi_champion` | ≥ 170 points anti-gaspi | 170 pts |

### Mécanisme d'attribution

1. Le job CRON hebdo appelle `BadgesTriggersService.evaluer_et_attribuer()`
2. Les métriques sont collectées sur les 7 derniers jours
3. Chaque badge est évalué contre son seuil
4. Un badge peut être obtenu plusieurs fois (un par jour max — contrainte unique `user_id + badge_type + acquis_le`)
5. Les badges nouvellement attribués déclenchent une notification push/ntfy

### Progression

L'endpoint `/api/v1/dashboard/badges/utilisateur` retourne tous les badges avec :
- État obtenu/non obtenu
- Nombre de fois obtenu (`nb_obtenu`)
- Date de dernière obtention (`derniere_date`)

---

## API Endpoints

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `GET` | `/api/v1/dashboard/points-famille` | Points consolidés de la semaine |
| `GET` | `/api/v1/dashboard/badges/catalogue` | Catalogue complet des badges |
| `GET` | `/api/v1/dashboard/badges/utilisateur` | Badges d'un utilisateur + progression |
| `POST` | `/api/v1/dashboard/badges/evaluer` | Évaluer et attribuer les badges mérités |
| `GET` | `/api/v1/dashboard/historique-points` | Historique des points (N semaines) |

### Exemples de réponses

**GET /api/v1/dashboard/badges/utilisateur**
```json
{
  "items": [
    {
      "badge_type": "sportif_hebdo",
      "badge_label": "Sportif assidu",
      "categorie": "sport",
      "emoji": "💪",
      "description": "Réaliser au moins 4 sessions de sport dans la semaine",
      "seuil": 4,
      "unite": "sessions/semaine",
      "obtenu": true,
      "nb_obtenu": 3,
      "derniere_date": "2026-03-29"
    }
  ],
  "total": 12,
  "obtenus": 5
}
```

**GET /api/v1/dashboard/historique-points?nb_semaines=4**
```json
{
  "items": [
    {
      "semaine_debut": "2026-03-02",
      "points_sport": 220,
      "points_alimentation": 180,
      "points_anti_gaspi": 185,
      "total_points": 585,
      "details": {}
    }
  ],
  "total": 4
}
```

---

## Notifications

Quand de nouveaux badges sont débloqués, une notification est envoyée via le dispatcher multi-canal :

- **Type d'événement** : `badge_debloque`
- **Canaux** : `push` + `ntfy`
- **Message** : `Nouveau(x) badge(s) débloqué(s) : 🏅 Sportif assidu, 🥗 Planning équilibré`

---

## Frontend

La page `/famille/gamification` affiche :

1. **4 cartes métriques** : Total points, Score bien-être, Pas Garmin, Badges débloqués
2. **3 barres de progression** : Sport (/300), Alimentation (/300), Anti-gaspi (/200)
3. **Grille Badges Sport** : 6 badges avec état obtenu/non obtenu, emoji, description, compteur
4. **Grille Badges Nutrition** : 6 badges avec état obtenu/non obtenu, emoji, description, compteur
5. **Graphique historique** : Barres empilées (sport/alimentation/anti-gaspi) sur 8 semaines

---

## Modèle de données

### Table `points_utilisateurs`

| Colonne | Type | Description |
|---------|------|-------------|
| `id` | SERIAL PK | |
| `user_id` | INT FK | → profils_utilisateurs |
| `semaine_debut` | DATE | Début de la semaine |
| `points_sport` | INT | Points sport (0-300) |
| `points_alimentation` | INT | Points alimentation (0-300) |
| `points_anti_gaspi` | INT | Points anti-gaspi (0-200) |
| `total_points` | INT | Total calculé |
| `details` | JSONB | Métriques détaillées |
| UNIQUE | | `(user_id, semaine_debut)` |

### Table `badges_utilisateurs`

| Colonne | Type | Description |
|---------|------|-------------|
| `id` | SERIAL PK | |
| `user_id` | INT FK | → profils_utilisateurs |
| `badge_type` | VARCHAR(100) | Identifiant du badge |
| `badge_label` | VARCHAR(150) | Nom affiché |
| `acquis_le` | DATE | Date d'obtention |
| `meta` | JSONB | Métadonnées (valeur, seuil, emoji, catégorie) |
| UNIQUE | | `(user_id, badge_type, acquis_le)` |
