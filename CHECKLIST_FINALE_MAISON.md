# ✅ Checklist Finale - Démarrage Module Maison

Suivez cette checklist pour que le module Maison soit **100% fonctionnel** :

## ✅ Étape 1 : Créer les tables manquantes

### Commande
```bash
python scripts/create_maison_tables.py
```

### Résultat attendu
```
🔧 CRÉATION DE TOUTES LES TABLES
═════════════════════════════════════════════════════════════════════════

✅ Connexion BD établie

🌱 RECETTES
  ✅ recettes                        (12 colonnes)
  ✅ ingredients                     ( 5 colonnes)
  
... (toutes les tables) ...

🎉 RÉSUMÉ: 24/24 tables créées
✨ SUCCÈS! Toutes les tables sont créées.
```

### Si ça échoue
1. ✅ Vérifier `.env.local` contient `DATABASE_URL` valide
2. ✅ Vérifier connexion Supabase accessible
3. ✅ Vérifier credentials PostgreSQL

---

## ✅ Étape 2 : Relancer l'application

### Commande
```bash
streamlit run src/app.py
```

### Première exécution - attendez
L'app va prendre du temps (importation des modules) :
```
2026-01-25 16:30:42.123  thread_id=1234
  Main script rerun started

  Compiling Streamlit modules...
  
  Module optimisé: accueil
  Module optimisé: cuisine
  Module optimisé: famille
  Module optimisé: maison       ← Voici!
  Module optimisé: barcode
  Module optimisé: parametres
  
  ✨ Dashboard chargé
```

### L'interface doit montrer
- ✅ Barre latérale avec modules
- ✅ Tab "🏠 Maison" doit être cliquable
- ✅ Pas d'erreur en rouge

---

## ✅ Étape 3 : Tester le module Maison

### 3.1 Accueil du module (🏠 Hub)
Cliquez sur **🏠 Maison** dans la barre latérale

**Vous devez voir :**
- ✅ 3 métriques : Projets | Plantes | Routines (tous à 0)
- ✅ 3 sections d'alertes : Projets urgents | Plantes à arroser | Tâches du jour (vides car aucune donnée)
- ✅ 3 boutons : Créer projet | Ajouter plante | Nouvelle routine
- ✅ Callout ℹ️ "Partenaire IA du ménage"

### 3.2 Sous-module 🌱 Jardin
Cliquez sur **🌱 Jardin**

**5 tabs doivent être présents :**
1. ✅ **🌱 Mes Plantes** - Liste vide (aucune plante ajoutée)
2. ✅ **🤖 Conseils IA** - 3 panneaux IA
3. ✅ **➕ Ajouter** - Formulaire pour ajouter plante
4. ✅ **📊 Stats** - 4 métriques à 0
5. ✅ **📅 Journal** - Tableau vide

**Test :** Cliquez **➕ Ajouter** → Remplissez le formulaire → Cliquez "Ajouter la plante"

Résultat attendu :
- ✅ Message "Plante ajoutée avec succès"
- ✅ La plante apparaît dans le tab **🌱 Mes Plantes**

### 3.3 Sous-module 📋 Projets
Cliquez sur **📋 Projets**

**4 tabs doivent être présents :**
1. ✅ **📋 En cours** - Projets avec progress bars
2. ✅ **🤖 Assistant IA** - 3 panneaux IA
3. ✅ **➕ Nouveau** - Formulaire + 3 templates
4. ✅ **📊 Tableau** - Graphiques et dataframe

**Test :** Cliquez **➕ Nouveau** → Sélectionnez un template ou remplissez le formulaire → Cliquez "Créer projet"

Résultat attendu :
- ✅ Message "Projet créé avec succès"
- ✅ Le projet apparaît dans le tab **📋 En cours**

### 3.4 Sous-module ☑️ Entretien
Cliquez sur **☑️ Entretien**

**4 tabs doivent être présents :**
1. ✅ **☑️ Aujourd'hui** - Checklist du jour
2. ✅ **📅 Routines** - Liste des routines actives
3. ✅ **🤖 Assistant IA** - 4 panneaux IA
4. ✅ **➕ Créer** - Formulaire + 3 templates

**Test :** Cliquez **➕ Créer** → Sélectionnez un template ou remplissez le formulaire → Cliquez "Créer routine"

Résultat attendu :
- ✅ Message "Routine créée avec succès"
- ✅ La routine apparaît dans le tab **📅 Routines**

---

## ❌ Dépannage

### Erreur: "Module 'maison' not found"
- ✅ Vérifier que `src/modules/maison/__init__.py` existe
- ✅ Vérifier que tous les fichiers existent : `jardin.py`, `projets.py`, `entretien.py`, `helpers.py`

### Erreur: "relation 'calendar_events' does not exist"
- 🔧 **SOLUTION :** Relancer le script :
  ```bash
  python scripts/create_maison_tables.py
  ```

### Erreur: "relation 'projects' does not exist"
- 🔧 **SOLUTION :** Même solution - relancer le script

### Erreur: "KeyError: 'a_arroser'"
- ✅ C'est corrigé ! Le code gère maintenant les DataFrames vides
- 🔧 Si ça persiste : redémarrer l'app `Ctrl+C` puis `streamlit run src/app.py`

### Erreur: "Configuration DB manquante"
- ✅ Vérifier que `.env.local` existe
- ✅ Vérifier `DATABASE_URL` est défini
- ✅ Vérifier format : `postgresql://user:password@host:5432/database`

---

## 🎯 Résumé des fichiers modifiés

| Fichier | Modification | Type |
|---------|-------------|------|
| `src/modules/maison/helpers.py` | Check DataFrame vide | Fix |
| `scripts/create_maison_tables.py` | Refactorisé pour TOUTES tables | Amélioration |
| `alembic/versions/008_add_...py` | Migration Alembic | Nouveau |
| `GUIDE_CREATION_TABLES_COMPLETES.md` | Documentation | Nouveau |
| `CORRECTIFS_25_JAN_2026.md` | Suivi corrections | Nouveau |

---

## ✨ À la fin de la checklist

Vous devez avoir :
- ✅ 24/24 tables créées en base
- ✅ App lancée sans erreur
- ✅ 3 sous-modules accessibles et fonctionnels
- ✅ IA intégrée dans chaque sous-module
- ✅ Capacité à créer projets, plantes, routines

**🎉 Le module Maison est maintenant 100% fonctionnel !**

---

## 📞 Questions ?

Consultez les documents de référence :
- [GUIDE_CREATION_TABLES_COMPLETES.md](GUIDE_CREATION_TABLES_COMPLETES.md) - Comment créer les tables
- [CORRECTIFS_25_JAN_2026.md](CORRECTIFS_25_JAN_2026.md) - Détails des corrections
- [MAISON_MODULE_DOCUMENTATION.md](MAISON_MODULE_DOCUMENTATION.md) - Doc technique complète
- [MAISON_TEST_GUIDE.md](MAISON_TEST_GUIDE.md) - Guide de test détaillé
