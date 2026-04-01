# Gamification â€” Sport + Nutrition

> **PÃ©rimÃ¨tre volontairement limitÃ©** : La gamification sert uniquement Ã  inciter Ã  **faire du sport** et **bien manger**. Aucun badge/point pour d'autres modules.

---

## Architecture

```
Backend
â”œâ”€â”€ src/core/models/gamification.py        # ModÃ¨les ORM (PointsUtilisateur, BadgeUtilisateur)
â”œâ”€â”€ src/services/dashboard/points_famille.py  # Calcul des points hebdo
â”œâ”€â”€ src/services/dashboard/badges_triggers.py # Triggers badges sport + nutrition
â”œâ”€â”€ src/services/core/cron/jobs.py         # Job CRON hebdo (dim 20h)
â””â”€â”€ src/api/routes/dashboard.py            # Endpoints API gamification

Frontend
â”œâ”€â”€ frontend/src/app/(app)/famille/gamification/page.tsx  # Page dÃ©tail
â””â”€â”€ frontend/src/bibliotheque/api/tableau-bord.ts         # Client API
```

---

## Points hebdomadaires

Les points sont calculÃ©s chaque dimanche Ã  20h via le job CRON `points_famille_hebdo`.

### Calcul

| CatÃ©gorie | Formule | Max |
| ----------- | --------- | ----- |
| **Sport** | `min(300, nb_activitÃ©s Ã— 40 + calories_actives Ã· 20 + total_pas Ã· 1000)` | 300 |
| **Alimentation** | `min(300, score_bien_Ãªtre Ã— 3)` | 300 |
| **Anti-gaspi** | `max(0, 200 - articles_Ã _risque Ã— 15)` | 200 |

**Total max** : 800 points/semaine

### Sources de donnÃ©es

- **Garmin** : `ActiviteGarmin` (sessions sport) + `ResumeQuotidienGarmin` (pas, calories)
- **Score bien-Ãªtre** : Score composite alimentation (diversitÃ© + nutri-score + activitÃ©s)
- **Inventaire** : Articles proches de la date de pÃ©remption (Â±3 jours)

### Persistance

Snapshot hebdomadaire dans `points_utilisateurs` (unique par `user_id + semaine_debut`).

---

## Badges

### Catalogue complet

#### Badges Sport

| Badge | Emoji | Type | Condition | Seuil |
| ------- | ------- | ------ | ----------- | ------- |
| **Marcheur rÃ©gulier** | ðŸš¶ | `marcheur_regulier` | â‰¥ 8 000 pas/jour pendant 7 jours consÃ©cutifs | 7 jours |
| **Marathonien** | ðŸƒ | `marathonien` | â‰¥ 12 000 pas/jour pendant 7 jours consÃ©cutifs | 7 jours |
| **Sportif assidu** | ðŸ’ª | `sportif_hebdo` | â‰¥ 4 sessions sport dans la semaine | 4 sessions |
| **BrÃ»leur de calories** | ðŸ”¥ | `bruleur_calories` | â‰¥ 2 500 calories actives dans la semaine | 2 500 kcal |
| **AthlÃ¨te complet** | ðŸ… | `athlete_complet` | â‰¥ 3 types d'activitÃ©s diffÃ©rentes | 3 types |
| **Bougeotte** | âš¡ | `bougeotte` | â‰¥ 180 points sport dans la semaine | 180 pts |

#### Badges Nutrition

| Badge | Emoji | Type | Condition | Seuil |
| ------- | ------- | ------ | ----------- | ------- |
| **Planning Ã©quilibrÃ©** | ðŸ¥— | `planning_equilibre` | â‰¥ 5 jours avec repas planifiÃ©s | 5 jours |
| **Nutritionniste** | ðŸŽ | `nutritionniste` | Score bien-Ãªtre â‰¥ 75 | 75 |
| **Assiette futÃ©e** | ðŸ§  | `assiette_futee` | â‰¥ 220 points alimentation | 220 pts |
| **ZÃ©ro gaspi** | â™»ï¸ | `zero_gaspi` | 0 article expirÃ© dans la semaine | 0 articles |
| **DiversitÃ© alimentaire** | ðŸŒˆ | `diversite_alimentaire` | â‰¥ 5 catÃ©gories d'aliments | 5 catÃ©gories |
| **Champion anti-gaspi** | ðŸ† | `anti_gaspi_champion` | â‰¥ 170 points anti-gaspi | 170 pts |

### MÃ©canisme d'attribution

1. Le job CRON hebdo appelle `BadgesTriggersService.evaluer_et_attribuer()`
2. Les mÃ©triques sont collectÃ©es sur les 7 derniers jours
3. Chaque badge est Ã©valuÃ© contre son seuil
4. Un badge peut Ãªtre obtenu plusieurs fois (un par jour max â€” contrainte unique `user_id + badge_type + acquis_le`)
5. Les badges nouvellement attribuÃ©s dÃ©clenchent une notification push/ntfy

### Progression

L'endpoint `/api/v1/dashboard/badges/utilisateur` retourne tous les badges avec :
- Ã‰tat obtenu/non obtenu
- Nombre de fois obtenu (`nb_obtenu`)
- Date de derniÃ¨re obtention (`derniere_date`)

---

## API Endpoints

| MÃ©thode | Endpoint | Description |
| --------- | ---------- | ------------- |
| `GET` | `/api/v1/dashboard/points-famille` | Points consolidÃ©s de la semaine |
| `GET` | `/api/v1/dashboard/badges/catalogue` | Catalogue complet des badges |
| `GET` | `/api/v1/dashboard/badges/utilisateur` | Badges d'un utilisateur + progression |
| `POST` | `/api/v1/dashboard/badges/evaluer` | Ã‰valuer et attribuer les badges mÃ©ritÃ©s |
| `GET` | `/api/v1/dashboard/historique-points` | Historique des points (N semaines) |

### Exemples de rÃ©ponses

**GET /api/v1/dashboard/badges/utilisateur**
```json
{
  "items": [
    {
      "badge_type": "sportif_hebdo",
      "badge_label": "Sportif assidu",
      "categorie": "sport",
      "emoji": "ðŸ’ª",
      "description": "RÃ©aliser au moins 4 sessions de sport dans la semaine",
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

Quand de nouveaux badges sont dÃ©bloquÃ©s, une notification est envoyÃ©e via le dispatcher multi-canal :

- **Type d'Ã©vÃ©nement** : `badge_debloque`
- **Canaux** : `push` + `ntfy`
- **Message** : `Nouveau(x) badge(s) dÃ©bloquÃ©(s) : ðŸ… Sportif assidu, ðŸ¥— Planning Ã©quilibrÃ©`

---

## Frontend

La page `/famille/gamification` affiche :

1. **4 cartes mÃ©triques** : Total points, Score bien-Ãªtre, Pas Garmin, Badges dÃ©bloquÃ©s
2. **3 barres de progression** : Sport (/300), Alimentation (/300), Anti-gaspi (/200)
3. **Grille Badges Sport** : 6 badges avec Ã©tat obtenu/non obtenu, emoji, description, compteur
4. **Grille Badges Nutrition** : 6 badges avec Ã©tat obtenu/non obtenu, emoji, description, compteur
5. **Graphique historique** : Barres empilÃ©es (sport/alimentation/anti-gaspi) sur 8 semaines

---

## ModÃ¨le de donnÃ©es

### Table `points_utilisateurs`

| Colonne | Type | Description |
| --------- | ------ | ------------- |
| `id` | SERIAL PK | |
| `user_id` | INT FK | â†’ profils_utilisateurs |
| `semaine_debut` | DATE | DÃ©but de la semaine |
| `points_sport` | INT | Points sport (0-300) |
| `points_alimentation` | INT | Points alimentation (0-300) |
| `points_anti_gaspi` | INT | Points anti-gaspi (0-200) |
| `total_points` | INT | Total calculÃ© |
| `details` | JSONB | MÃ©triques dÃ©taillÃ©es |
| UNIQUE | | `(user_id, semaine_debut)` |

### Table `badges_utilisateurs`

| Colonne | Type | Description |
| --------- | ------ | ------------- |
| `id` | SERIAL PK | |
| `user_id` | INT FK | â†’ profils_utilisateurs |
| `badge_type` | VARCHAR(100) | Identifiant du badge |
| `badge_label` | VARCHAR(150) | Nom affichÃ© |
| `acquis_le` | DATE | Date d'obtention |
| `meta` | JSONB | MÃ©tadonnÃ©es (valeur, seuil, emoji, catÃ©gorie) |
| UNIQUE | | `(user_id, badge_type, acquis_le)` |
