# 👋 START HERE - Commencez par ici

Vous venez de terminer une intégration API complète pour le module 🎲 Jeux!

Voici **EXACTEMENT** ce que vous devez faire maintenant:

---

## ⏰ 5 Minutes pour démarrer

### Étape 1: Clé API (2 min)

```bash
# 1. Aller sur: https://www.football-data.org/client/register
# 2. S'inscrire (gratuit, pas de CB)
# 3. Confirmer l'email
# 4. Copier le token API
```

### Étape 2: Configuration (.env.local)

À la racine du projet (`d:\Projet_streamlit\assistant_matanne\`), créer/modifier `.env.local`:

```env
FOOTBALL_DATA_API_KEY=votre_token_ici
```

### Étape 3: Lancer l'app

```bash
cd d:\Projet_streamlit\assistant_matanne
streamlit run src/app.py
```

### Étape 4: Naviguer vers 🎲 Jeux

Dans le menu sidebar, cliquer sur **🎲 Jeux**

---

## ✅ Vérifier que tout marche (1 min)

```bash
python tests/test_jeux_apis.py
```

Vous verrez:

```
✅ PASS - Football-Data API
✅ PASS - FDJ Loto Scraper
✅ PASS - UI Helpers
3/3 tests passed ✅
```

Si tous les tests passent = **tout est prêt!** 🎉

---

## 📚 Documentation (Dans l'ordre recommandé)

### 1️⃣ QUICKSTART.md (5 min)

```
→ Lire: src/domains/jeux/QUICKSTART.md
- Démarrage ultra-rapide
- Copy-paste ready code
```

### 2️⃣ README.md (30 min - optionnel)

```
→ Lire: src/domains/jeux/README.md
- Guide complet du module
- Workflows détaillés
- Architecture complète
```

### 3️⃣ APIS_CONFIGURATION.md (15 min - si besoin)

```
→ Lire: APIS_CONFIGURATION.md
- Setup détaillé des APIs
- Limitations et alternatives
- Troubleshooting
```

---

## 🎯 Utiliser le module

### ⚽ Paris Sportifs

```
1. Menu → 🎲 Jeux → ⚽ Paris Sportifs
2. Cliquer "🔄 Actualiser"
3. Voir les matchs de la semaine
4. Analyser les prédictions
5. Enregistrer vos paris (Virtual mode!)
6. Voir le dashboard de performance
```

### 🎰 Loto

```
1. Menu → 🎲 Jeux → 🎰 Loto
2. Tab "Statistiques" → Voir fréquences
3. Tab "Générateur" → Créer grilles
4. Tab "Simulation" → Tester stratégies
5. Tab "Espérance" → Comprendre les math
```

---

## 🐛 Si quelque chose ne marche pas

### Erreur: "Clé API non trouvée"

```bash
# Vérifier que .env.local existe
ls -la .env.local

# Vérifier le contenu
cat .env.local | grep FOOTBALL_DATA_API_KEY
```

### Erreur: "Aucun match n'apparaît"

```bash
# Tester la connexion API
python -c "
from src.domains.jeux.logic.api_football import charger_matchs_a_venir
matchs = charger_matchs_a_venir('Ligue 1', 7)
print(f'Trouvé {len(matchs)} matchs')
"
```

### Erreur: "Les tests échouent"

```bash
# Vérifier les imports
python -c "from src.domains.jeux.logic import paris_logic, loto_logic, api_football"

# Vérifier la BD
python manage.py migrate
```

### Pas d'erreur mais données vides

→ C'est OK! Le fallback BD s'active. Les données apparaîtront quand vous synchroniserez.

---

## 💡 Tips & Tricks

### Tip 1: Utiliser Virtual mode d'abord

Ne pariez pas d'argent réel tout de suite!

- Cocher "Virtual" quand vous enregistrez un pari
- Tester votre stratégie
- Vérifier le ROI
- Puis passer au réel si confiant

### Tip 2: Lire le guide complet

```
Pour Paris Sportifs:
→ Lire la section "Stratégie suggérée" dans README.md

Pour Loto:
→ Lire "Important: Réclamation d'équité" dans README.md
→ Comprendre pourquoi on perd -51% toujours
```

### Tip 3: Forcer un refresh des données

```bash
# Dans l'app:
1. Cliquer "🔄 Actualiser depuis API"
2. Cliquer "C" en haut du navigateur (cache clear)
3. Rafraîchir la page (F5)
```

### Tip 4: Vérifier la source des données

```
Au bas de chaque section, voir:
🌐 Données depuis: API   (données live)
💾 Données depuis: BD     (cache local)
🕷️ Données depuis: Scraper FDJ (web)
```

---

## 🚀 Ce qui est déjà inclus

Vous n'avez rien à faire pour:

✅ Fallback automatique (API → BD)  
✅ Cache Streamlit (30 min TTL)  
✅ Rate limiting (géré automatiquement)  
✅ Web scraper FDJ (fonctionne seul)  
✅ Création auto d'équipes manquantes  
✅ Gestion des erreurs (partout)  
✅ Logging détaillé  
✅ Tests automatiques

**Tout marche out-of-the-box!** 🎉

---

## 📞 Besoin d'aide?

| Besoin         | Faire                                                   |
| -------------- | ------------------------------------------------------- |
| Setup rapide   | Lire: QUICKSTART.md                                     |
| Guide complet  | Lire: README.md                                         |
| Config APIs    | Lire: APIS_CONFIGURATION.md                             |
| Tests          | Lancer: `python tests/test_jeux_apis.py`                |
| Logs détaillés | Lancer: `streamlit run --logger.level=debug src/app.py` |

---

## ✅ Checklist pour vous

- [ ] Clé API Football-Data obtenue
- [ ] `.env.local` configuré
- [ ] App lancée: `streamlit run src/app.py`
- [ ] Tests passent: `python tests/test_jeux_apis.py`
- [ ] Menu 🎲 Jeux visible
- [ ] ⚽ Paris Sportifs chargé
- [ ] 🎰 Loto chargé
- [ ] Documentation lue (QUICKSTART)

**Tous les checkboxes cochés?**
→ **Vous êtes prêt à utiliser le module!** 🚀

---

## 🎓 Prochaines étapes

1. **Cette semaine**: Tester Virtual mode (Paris)
2. **Semaine 2**: Lire le README complet
3. **Semaine 3**: Analyser vos données
4. **Semaine 4**: Optimiser votre stratégie

---

## 🎉 Résumé

Vous avez maintenant un module 🎲 Jeux **complet et prêt** avec:

✨ **Données live** depuis Football-Data.org  
✨ **Historiques Loto** depuis FDJ  
✨ **Fallback BD** si APIs down  
✨ **Tests validés** et documentation complète  
✨ **Virtual betting** pour apprendre sans risque

**Everything is ready! Lancez l'app et explorez! 🚀**

---

**Questions? Consultez les docs. Bugs? Lancez les tests.**

**Bon jeu! 🍀⚽🎰**
