# 📚 Index de Documentation - Module Maison

## 🚨 URGENT : Erreur `calendar_events` does not exist

**Commencez par :** [ACTION_IMMEDIATE_ERREUR_CALENDAR.md](ACTION_IMMEDIATE_ERREUR_CALENDAR.md)

3 étapes pour relancer l'app sans erreur ! ⚡

---

## 📖 Guides de Configuration

### Pour configurer Supabase (5 min)
👉 [CONFIG_SUPABASE_RAPIDE.md](CONFIG_SUPABASE_RAPIDE.md)
- Comment obtenir DATABASE_URL
- Remplir .env.local
- Créer les tables
- Dépannage

### Pour comprendre l'erreur
👉 [SOLUTION_CALENDAR_EVENTS_ERROR.md](SOLUTION_CALENDAR_EVENTS_ERROR.md)
- Cause de l'erreur
- Pourquoi elle survient
- Comment la fixer
- FAQ

---

## ✅ Guides de Vérification

### Checklist complète du module Maison
👉 [CHECKLIST_FINALE_MAISON.md](CHECKLIST_FINALE_MAISON.md)
- Vérifier que tout fonctionne
- Tester les 3 sous-modules
- Dépannage complet

### Guide de test détaillé
👉 [MAISON_TEST_GUIDE.md](MAISON_TEST_GUIDE.md)
- Scénarios de test
- Cas d'usage
- Validation

---

## 🔧 Guides Techniques

### Documentation du script de création de tables
👉 [GUIDE_CREATION_TABLES_COMPLETES.md](GUIDE_CREATION_TABLES_COMPLETES.md)
- Ce que crée le script
- Options d'exécution
- Vérification des résultats

### Récapitulatif des corrections appliquées
👉 [RECAP_CORRECTIONS_25_JAN.md](RECAP_CORRECTIONS_25_JAN.md)
- Fichiers modifiés
- Fichiers créés
- Résumé des changements

### Suivi détaillé des correctifs
👉 [CORRECTIFS_25_JAN_2026.md](CORRECTIFS_25_JAN_2026.md)
- Problèmes identifiés
- Solutions appliquées
- Détails techniques

---

## 📚 Documentation Module Maison

### Documentation complète du module
👉 [MAISON_MODULE_DOCUMENTATION.md](MAISON_MODULE_DOCUMENTATION.md)
- Architecture
- Services IA
- Composants UI
- API

### Résumé de la refonte
👉 [MAISON_REFONTE_RESUME.md](MAISON_REFONTE_RESUME.md)
- Objectifs
- Fonctionnalités
- Métriques
- Timeline

---

## 🔨 Scripts et Configuration

### Fichier de configuration
📄 `.env.local`
- Configuration BD (DATABASE_URL)
- Paramètres application
- API keys

### Script de création de tables
📄 `scripts/create_maison_tables.py`
- Crée 24 tables
- Vérifie la création
- Affiche résumé

### Migration Alembic
📄 `alembic/versions/008_add_planning_and_missing_tables.py`
- Alternative au script Python
- Utile pour les CI/CD

---

## 🎯 Workflow Recommandé

### 1️⃣ Premier lancement (Configuration)
```
1. Lire: ACTION_IMMEDIATE_ERREUR_CALENDAR.md
2. Lire: CONFIG_SUPABASE_RAPIDE.md
3. Exécuter: python scripts/create_maison_tables.py
4. Lancer: streamlit run src/app.py
```

### 2️⃣ Vérification (Tests)
```
1. Lire: CHECKLIST_FINALE_MAISON.md
2. Tester chaque sous-module
3. Ajouter quelques données de test
```

### 3️⃣ Compréhension (Approfondissement)
```
1. Lire: MAISON_MODULE_DOCUMENTATION.md
2. Lire: MAISON_TEST_GUIDE.md
3. Explorer le code source
```

### 4️⃣ Maintenance (Futur)
```
1. Consulter: RECAP_CORRECTIONS_25_JAN.md
2. Consulter: CORRECTIFS_25_JAN_2026.md
3. Pour nouvelles tables: alembic/versions/008_...
```

---

## 📍 Structure des fichiers

```
assistant_matanne/
├── .env.local ← Configuration BD
├── scripts/
│   └── create_maison_tables.py ← Créer les tables
├── src/
│   ├── core/
│   │   └── models.py ← Modèles ORM
│   └── modules/
│       └── maison/ ← Module Maison
│           ├── __init__.py (hub)
│           ├── helpers.py (fonctions partagées)
│           ├── jardin.py (sous-module)
│           ├── projets.py (sous-module)
│           └── entretien.py (sous-module)
└── Documentation/
    ├── ACTION_IMMEDIATE_ERREUR_CALENDAR.md ← À lire en premier!
    ├── CONFIG_SUPABASE_RAPIDE.md
    ├── SOLUTION_CALENDAR_EVENTS_ERROR.md
    ├── CHECKLIST_FINALE_MAISON.md
    ├── GUIDE_CREATION_TABLES_COMPLETES.md
    ├── RECAP_CORRECTIONS_25_JAN.md
    ├── CORRECTIFS_25_JAN_2026.md
    ├── MAISON_MODULE_DOCUMENTATION.md
    ├── MAISON_REFONTE_RESUME.md
    └── MAISON_TEST_GUIDE.md
```

---

## 🚀 Commandes Rapides

```bash
# 1. Créer les tables
python scripts/create_maison_tables.py

# 2. Lancer l'application
streamlit run src/app.py

# 3. Lancer les tests
pytest tests/test_maison*.py -v

# 4. Voir les migrations
alembic current
alembic history
```

---

## 💡 Tips

- **Première fois ?** → Lire `ACTION_IMMEDIATE_ERREUR_CALENDAR.md` (2 min)
- **Besoin de DATABASE_URL ?** → Lire `CONFIG_SUPABASE_RAPIDE.md` (5 min)
- **Erreur persiste ?** → Lire `SOLUTION_CALENDAR_EVENTS_ERROR.md` (10 min)
- **Tout fonctionne ?** → Lire `CHECKLIST_FINALE_MAISON.md` (15 min pour tester)

---

## ✨ Status Actuel

| Élément | Status |
|---------|--------|
| Code Python | ✅ Corrigé |
| Scripts | ✅ Améliorés |
| Configuration | ✅ Documentée |
| Documentation | ✅ Complète |
| Tables | ⏳ À créer (par l'utilisateur) |
| Application | ⏳ À relancer |

---

## 🎉 Prochaine Étape

👉 **Ouvrir** [ACTION_IMMEDIATE_ERREUR_CALENDAR.md](ACTION_IMMEDIATE_ERREUR_CALENDAR.md)

3 étapes et vous y êtes ! ⚡
