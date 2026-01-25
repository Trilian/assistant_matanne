# 🚀 PROCHAINES ÉTAPES - Planning Refoncé

## ✅ Ce qui est Terminé

La **refonte complète du module planning** est finie :

- ✅ Service unifié `PlanningAIService` créé
- ✅ Calendrier refactorisé avec nouvelle archi
- ✅ Vue semaine crée (nouveau)
- ✅ Vue d'ensemble refactorisée
- ✅ Module __init__.py avec menu
- ✅ Composants réutilisables créés
- ✅ Modèles optimisés (indices)

**~1800 lignes de code neuf/refactorisé** 🎁

---

## 📋 Avant de Lancer l'App

### **1. Vérifier les Imports**

L'app utilise maintenant:
```python
from src.services.planning_unified import get_planning_service
```

Vérifiez que ce module est importable:

```bash
python -c "from src.services.planning_unified import get_planning_service; print('✅ OK')"
```

### **2. Tests Rapides**

Si vous avez des repas/activités/projets en base, testez:

```bash
# Via test
pytest tests/test_planning.py -v

# Ou direct Python
python -c "
from src.services.planning_unified import get_planning_service
from datetime import date
service = get_planning_service()
semaine = service.get_semaine_complete(date.today())
print(f'✅ Semaine chargée: {len(semaine.jours)} jours')
print(f'📊 Stats: {semaine.stats_semaine}')
"
```

### **3. Vérifier la BD**

Le service utilise les modèles existants:
```python
- Planning, Repas (cuisine)
- FamilyActivity (famille)
- CalendarEvent (planning)
- Project, ProjectTask (maison)
- Routine, RoutineTask (famille)
```

Assurez-vous que vos tables existent et ont des données pour tester.

---

## 🎯 Premier Lancement

### **Étape 1: Accéder au Planning**
```
streamlit run src/app.py
  ↓
Menu latéral: 📅 Planning
  ↓
Sélectionner vue (Calendrier, Vue Semaine, ou Vue d'Ensemble)
```

### **Étape 2: Tester Chaque Vue**

**📅 Calendrier Familial**
- [ ] Voir la semaine complète
- [ ] Vérifier charge par jour (badges 🟢🟡🔴)
- [ ] Créer un événement test
- [ ] Essayer générer avec IA

**📊 Vue Semaine**
- [ ] Voir graphique charge
- [ ] Voir pie chart répartition
- [ ] Voir timeline jour par jour
- [ ] Vérifier statistiques

**🎯 Vue d'Ensemble**
- [ ] Voir actions prioritaires
- [ ] Voir alertes détectées
- [ ] Essayer rééquilibrer
- [ ] Essayer optimisation IA

---

## 🔧 Configuration Recommandée

### **Budget Familia (Adapter à Vos Données)**

Dans `vue_ensemble.py` ligne ~230:
```python
budget_limite = 500  # ← À adapter à votre budget famille réel
```

### **Objectifs Santé (Jules & Co)**

Dans `calendrier.py` et `vue_ensemble.py`:
```python
contexte={
    "jules_age_mois": 19,  # À jour avec réalité
    "objectifs_sante": [...],  # Vos objectifs
}
```

### **Seuils d'Alertes**

Dans `src/services/planning_unified.py` méthode `_detecter_alertes()`:
- Surcharge: `>= 80` (adapter si besoin)
- Activités Jules: `< 3` recommandé
- Repas complexes: `> 3` par jour

---

## 🐛 Dépannage

### **Erreur: Module planning_unified not found**
```bash
# Solution: Vérifier import dans __init__.py
cat src/modules/planning/__init__.py
# Doit avoir: from src.modules.planning import calendrier, vue_semaine, vue_ensemble
```

### **Erreur: Models not found (FamilyActivity, etc)**
```python
# Vérifier que tous les modèles existent dans src/core/models.py:
grep -n "class FamilyActivity\|class CalendarEvent\|class Routine" src/core/models.py
```

### **Cache non invalidé après création événement**
```python
# Le service invalide automatiquement, mais si soucis:
from src.core.cache import Cache
Cache().nettoyer("planning")
```

### **IA ne génère rien**
```python
# Vérifier limite de débit:
from src.core.ai import RateLimitIA
ok, msg = RateLimitIA.peut_appeler()
print(f"IA disponible: {ok}, Msg: {msg}")
```

---

## 📊 Cas d'Usage de Test

### **Test 1: Semaine avec Beaucoup d'Activités**
```
Créer:
- 3 repas planifiés
- 2-3 activités Jules
- 2 projets urgents
- 1-2 événements sociaux

Attendre que ça charge → Vérifier charge > 70 et alertes
```

### **Test 2: Générer une Semaine IA**
```
Planning → Calendrier ou Vue d'Ensemble
→ Onglet "🤖 Générer avec IA"
→ Budget: 400€, Énergie: normal, Objectifs: Cardio + Temps famille
→ Cliquer "🚀 Générer"
→ Voir propositions
```

### **Test 3: Rééquilibrer**
```
Créer une semaine très déséquilibrée (tout mercredi)
→ Vue d'Ensemble → Onglet "🔄 Rééquilibrer"
→ Voir suggestions de déplacement
```

---

## 📈 Prochaines Améliorations (Optionnelles)

### **Phase 2: Intégration Plus Poussée**
- [ ] Drag & drop calendrier (déplacer événements)
- [ ] Intégration Google Calendar / Outlook
- [ ] Export PDF semaine
- [ ] Notifications rappels
- [ ] Templates de semaines (famille, travail, etc)

### **Phase 3: IA Avancée**
- [ ] Prédiction charge (ML basé sur histoire)
- [ ] Recommandations personnalisées Jules
- [ ] Optimisation budget automatique
- [ ] Détection patterns (semaines chargées)

### **Phase 4: Mobile**
- [ ] Vue mobile optimisée
- [ ] Sync multi-devices
- [ ] Offline support

---

## 💾 Important: Migrations BD

Si vous aviez une ancienne structure planning:

```bash
# Créer migration:
python manage.py create_migration "Update planning schema with new indices"

# Vérifier migration:
alembic current

# Appliquer:
python manage.py migrate
```

Le service utilise les modèles existants (Planning, Repas, CalendarEvent, etc) donc pas de breaking changes.

---

## 📞 Support/Questions

Si problèmes:

1. **Vérifier logs**: `streamlit run src/app.py --logger.level=debug`
2. **Tester imports**: `python -c "from src.services.planning_unified import ..."`
3. **Vérifier BD**: `SELECT COUNT(*) FROM planning; FROM repas; FROM calendar_events;`
4. **Cache**: Forcer nettoyage: `from src.core.cache import Cache; Cache().nettoyer_tout()`

---

## ✨ Félicitations !

Vous avez un module planning **vraiment intelligent** maintenant ! 🎉

Le planning familial est maintenant le **centre de coordination** de votre app, avec:

✅ Vision complète (tous événements)
✅ Intelligence (charge, alertes, suggestions)
✅ Aide IA (génération semaines équilibrées)
✅ Performance (cache, requêtes optimisées)
✅ UX moderne (graphiques, interfaces intuitives)

Enjoy ! 🚀
