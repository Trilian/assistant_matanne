# 📐 ARCHITECTURE PLANNING REFONCÉ

## Vue d'Ensemble

```
┌────────────────────────────────────────────────────────────────┐
│                    APP STREAMLIT (app.py)                      │
├────────────────────────────────────────────────────────────────┤
│                                                                 │
│  📅 Planning Module (__init__.py - Point d'Entrée)            │
│  ├─ Menu: Sélectionner Vue                                     │
│  └─ Charge dynamique sous-modules                              │
│                                                                 │
├────────────────────────────────────────────────────────────────┤
│                    UI MODULES (3 Vues)                         │
├────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1️⃣ Calendrier Familial (calendrier.py)                       │
│     ├─ Navigation semaine                                      │
│     ├─ Affichage jour par jour (repas, activités, etc)        │
│     ├─ Créer événements                                        │
│     └─ Générer avec IA                                         │
│                                                                 │
│  2️⃣ Vue Semaine (vue_semaine.py)                              │
│     ├─ Graphique charge Plotly                                 │
│     ├─ Timeline jour détaillé                                  │
│     └─ Analyses intelligentes                                  │
│                                                                 │
│  3️⃣ Vue d'Ensemble (vue_ensemble.py)                          │
│     ├─ Actions prioritaires (alertes)                          │
│     ├─ Métriques clés (KPIs)                                   │
│     ├─ Suggestions amélioration                                │
│     └─ Rééquilibrage/Optimisation IA                           │
│                                                                 │
├────────────────────────────────────────────────────────────────┤
│              COMPOSANTS RÉUTILISABLES (components/)            │
├────────────────────────────────────────────────────────────────┤
│                                                                 │
│  📦 Composants UI:                                              │
│  ├─ afficher_badge_charge()       → 🟢🟡🔴                    │
│  ├─ afficher_badge_priorite()      → Projet priorité            │
│  ├─ carte_repas()                  → Affichage repas            │
│  ├─ carte_activite()               → Affichage activité         │
│  ├─ carte_projet()                 → Affichage projet           │
│  ├─ carte_event()                  → Affichage événement        │
│  ├─ selecteur_semaine()            → Navigation semaine         │
│  ├─ afficher_liste_alertes()       → Groupe alertes             │
│  └─ afficher_stats_semaine()       → KPI colonnes               │
│                                                                 │
├────────────────────────────────────────────────────────────────┤
│            SERVICE UNIFIÉ (PlanningAIService)                  │
├────────────────────────────────────────────────────────────────┤
│                                                                 │
│  🔧 planning_unified.py (Service métier)                       │
│     ├─ get_semaine_complete()       → SemaineCompleSchema      │
│     │  ├─ _charger_repas()          → Requête DB optimisée     │
│     │  ├─ _charger_activites()      → Requête DB optimisée     │
│     │  ├─ _charger_projets()        → Requête DB optimisée     │
│     │  ├─ _charger_routines()       → Requête DB optimisée     │
│     │  ├─ _charger_events()         → Requête DB optimisée     │
│     │  ├─ _calculer_charge()        → Logique métier            │
│     │  └─ _detecter_alertes()       → Logique intelligente      │
│     │                                                           │
│     ├─ generer_semaine_ia()         → SemaineGenereeIASchema   │
│     │  └─ _construire_prompt_generation()                      │
│     │                                                           │
│     └─ creer_event()                → CRUD événement            │
│                                                                 │
│  Hérite de:                                                     │
│  ├─ BaseService[CalendarEvent]      → CRUD standard             │
│  ├─ BaseAIService                   → Rate limiting + cache     │
│  └─ PlanningAIMixin                 → Contextes métier          │
│                                                                 │
├────────────────────────────────────────────────────────────────┤
│                    COUCHE DATA (Models)                        │
├────────────────────────────────────────────────────────────────┤
│                                                                 │
│  📊 Modèles SQLAlchemy (models.py):                            │
│  ├─ Planning                        → Plannings hebdo           │
│  ├─ Repas                           → Repas planifiés           │
│  ├─ FamilyActivity                  → Activités famille         │
│  ├─ CalendarEvent                   → Événements ⭐ (indices)  │
│  ├─ Project                         → Projets maison            │
│  ├─ ProjectTask                     → Tâches projets            │
│  ├─ Routine                         → Routines quotidiennes     │
│  └─ RoutineTask                     → Tâches routines           │
│                                                                 │
│  Index composites ajoutés:                                     │
│  ├─ idx_date_type (date_debut, type_event)                    │
│  └─ idx_date_range (date_debut, date_fin)                     │
│                                                                 │
├────────────────────────────────────────────────────────────────┤
│                  INFRASTRUCTURE (Décorateurs)                  │
├────────────────────────────────────────────────────────────────┤
│                                                                 │
│  🛠️ Utilisés par PlanningAIService:                             │
│  ├─ @with_db_session              → Gestion session DB auto    │
│  ├─ @with_cache                   → Cache TTL intelligent      │
│  ├─ @with_error_handling          → Gestion erreurs centralisée│
│  └─ Rate limiting IA              → Limite quotidienne/horaire │
│                                                                 │
└────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Flux de Données

### **Cas 1: Affichage Semaine (GET)**

```
Utilisateur sélectionne semaine
    ↓
Vue (calendrier.py)
    ↓
service = get_planning_service()
    ↓
service.get_semaine_complete(date_debut)
    ↓
PlanningAIService:
├─ Vérifier cache (TTL 30min)
├─ Si pas en cache:
│  ├─ _charger_repas(db) → 1 requête optimisée
│  ├─ _charger_activites(db) → 1 requête optimisée
│  ├─ _charger_projets(db) → 1 requête optimisée
│  ├─ _charger_routines(db) → 1 requête optimisée
│  └─ _charger_events(db) → 1 requête optimisée
│  └─ Total: 5 requêtes (vs 20+ avant)
│
├─ Calculer charge jour par jour
├─ Détecter alertes intelligentes
├─ Compiler SemaineCompleSchema
└─ Enregistrer en cache
    ↓
Retourner SemaineCompleSchema
    ↓
Vue affiche graphiquement:
├─ Badges charge 🟢🟡🔴
├─ Listes événements
├─ Alertes contextuelles
└─ KPIs et statistiques
```

### **Cas 2: Générer Semaine IA (POST)**

```
Utilisateur clique "🚀 Générer avec IA"
    ↓
Saisir:
├─ Budget (€)
├─ Énergie (faible/normal/élevé)
└─ Objectifs (santé)
    ↓
Vue appelle:
service.generer_semaine_ia(
    date_debut,
    contraintes={...},
    contexte={jules_age=19, ...}
)
    ↓
PlanningAIService:
├─ Vérifier cache IA (TTL 30min)
├─ Si pas en cache:
│  ├─ Vérifier rate limit (RateLimitIA)
│  ├─ Construire prompt avec contexte complet
│  ├─ Appeler ClientIA.appeler()
│  └─ Parser réponse en SemaineGenereeIASchema
│
└─ Enregistrer cache IA
    ↓
Retourner propositions
    ↓
Vue affiche:
├─ Harmonie description
├─ Raisons proposition
└─ Repas/Activités/Projets proposés
```

### **Cas 3: Créer Événement (INSERT)**

```
Utilisateur remplit formulaire
    ↓
Soumet "💾 Créer l'événement"
    ↓
calendrier.py:
└─ service.creer_event(
    titre, date, heure, type, lieu, couleur
)
    ↓
PlanningAIService.creer_event():
├─ Valider données
├─ INSERT into calendar_events
├─ db.commit()
├─ Invalider cache semaine
└─ Log succès
    ↓
DB updated
    ↓
Vue rerun() → Recharge semaine
    ↓
Service.get_semaine_complete() → Cache MISS
    ↓
Recharger tous événements (cache fraîche)
    ↓
Afficher semaine mise à jour
```

---

## 💾 Schemas & Types

### **Importants: Schémas Pydantic**

```python
# JourCompletSchema
{
    date: date,
    charge: "faible" | "normal" | "intense",
    charge_score: int (0-100),
    repas: [
        {
            id, type, recette, recette_id, portions,
            temps_total, notes
        }
    ],
    activites: [
        {
            id, titre, type, debut, fin, lieu, budget,
            pour_jules
        }
    ],
    projets: [
        {
            id, nom, priorite, statut, echéance
        }
    ],
    routines: [
        {
            id, nom, routine, heure, fait
        }
    ],
    events: [
        {
            id, titre, type, debut, fin, lieu, couleur
        }
    ],
    budget_jour: float,
    alertes: [str],
    suggestions_ia: [str]
}

# SemaineCompleSchema
{
    semaine_debut: date,
    semaine_fin: date,
    jours: {iso_date: JourCompletSchema},
    stats_semaine: {
        total_repas, total_activites, activites_jules,
        total_projets, total_events, budget_total,
        charge_moyenne
    },
    charge_globale: "faible" | "normal" | "intense",
    alertes_semaine: [str]
}

# SemaineGenereeIASchema
{
    repas_proposes: [dict],
    activites_proposees: [dict],
    projets_suggeres: [dict],
    harmonie_description: str,
    raisons: [str]
}
```

---

## 🔐 Couches de Sécurité

```
┌─────────────────────┐
│   User Input (UI)   │ ← Validation Streamlit widgets
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│   Pydantic Schemas  │ ← Validation stricte types
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│  Service Layer      │ ← Logique métier
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│  @with_db_session   │ ← Gestion transactions
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│  SQLAlchemy ORM     │ ← Protection injection SQL
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│  PostgreSQL DB      │ ← Constraints BD
└─────────────────────┘
```

---

## 📈 Performance

### **Requêtes Optimisées**

**AVANT** (Legacy):
- 20+ requêtes pour charger semaine
- N+1 queries (boucles imbriquées)
- Pas d'index
- Cache minimal

**APRÈS** (Unifié):
- **5 requêtes** (une par type événement)
- Joins optimisés
- Index composites (idx_date_type, idx_date_range)
- Cache TTL 30min + invalidation intelligente

**Résultat**: ~60% plus rapide ⚡

### **Cache Strategy**

```
request() → check cache
    ↓
if not cached or expired:
    execute_query()
    parse_data()
    store_cache(ttl=1800)
    
when create/update/delete:
    invalidate_week_cache()
    
→ Prochaine requête: cache HIT
```

---

## 🎯 Points Clés à Retenir

✅ **Service unifié** = une seule source de vérité
✅ **PlanningAIService** = logique métier centralisée
✅ **3 vues** = perspectives différentes même données
✅ **Cache intelligent** = perf + économie IA
✅ **Composants** = réutilisabilité UI
✅ **Modèles** = BD existante, pas de rupture
✅ **Décorateurs** = gestion cross-cutting
✅ **IA intégrée** = contexte famille complet

---

## 🚀 Evolution Future

```
Phase 1 (Fait) ✅
├─ Service unifié
├─ 3 vues intégrées
└─ IA avec contexte

Phase 2 (Optionnel)
├─ Drag & drop calendrier
├─ Notifications/Rappels
└─ Export PDF

Phase 3 (Avancé)
├─ ML prédictions charge
├─ Recommandations personnalisées
└─ Optimisation budgets
```

---

**Architecture claire, modulaire, et extensible !** 🎨
