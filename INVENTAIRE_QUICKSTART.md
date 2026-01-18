# 🚀 Inventaire - Démarrage Rapide

## ⚡ 5 minutes pour commencer

### 1️⃣ Démarrer l'application
```bash
streamlit run src/app.py
```

### 2️⃣ Accéder au module inventaire
```
Barre latérale → Cuisine → Inventaire
```

### 3️⃣ Voir les 5 onglets

| Onglet | Fonction | Icône |
|--------|----------|-------|
| 📊 Stock | Vue complète + filtres | 📊 |
| ⚠️ Alertes | Articles problématiques | ⚠️ |
| 🏷️ Catégories | Organisé par catégorie | 🏷️ |
| 🛒 Suggestions IA | Listes de courses auto | 🛒 |
| 🔧 Outils | Export + statistiques | 🔧 |

---

## 📦 Cas d'usage courants

### 👉 Je veux voir mon stock

**Onglet:** 📊 Stock

1. Voir **4 statistiques** en haut
2. Voir **tableau complet** avec tous articles
3. Utiliser **filtres** pour affiner
4. Voir **détails** (seuil, emplacement, péremption)

### 👉 Je veux lister ce qui est urgent

**Onglet:** ⚠️ Alertes

1. Voir **articles critiques** (🔴 < 50% seuil)
2. Voir **stock bas** (🟠 < seuil)
3. Voir **proche péremption** (🔔 < 7 jours)

### 👉 Je veux générer une liste de courses

**Onglet:** 🛒 Suggestions IA

1. Cliquer "🛒 Générer les suggestions"
2. Attendre 3-5 secondes
3. Voir **15 articles suggérés**
4. Articles groupés par **priorité** (haute/moyenne/basse)
5. Voir **rayon magasin** (où l'acheter?)

### 👉 Je veux organiser par catégorie

**Onglet:** 🏷️ Catégories

1. Voir **onglets par catégorie**
2. Chaque catégorie montre:
   - Nombre articles
   - Quantité totale
   - Nombre d'alertes
3. Tableau détaillé pour chaque

### 👉 Je veux exporter mes données

**Onglet:** 🔧 Outils

**Export:**
1. Cliquer "Télécharger en CSV"
2. Fichier "inventaire.csv" arrive
3. Ouvrir dans Excel/Sheets

**Statistiques:**
1. Voir 4 métriques clés
2. Voir 2 graphiques
3. Analyser votre inventaire

---

## 🔑 Clés de succès

### ✅ Pour commencer
1. Au moins **1 article** dans l'inventaire
2. Quelques articles avec **quantité_min**
3. Quelques articles avec **date_peremption**

### ✅ Pour les alertes
- Articles avec `quantite < quantite_min` (stock bas)
- Articles avec `quantite < quantite_min * 0.5` (critique)
- Articles avec `date_peremption <= aujourd'hui + 7 jours` (péremption)

### ✅ Pour les suggestions IA
- Avoir **alertes actives** (sinon rien à suggérer)
- Clé IA configurée (MISTRAL_API_KEY)
- Au moins **3-4 articles** en alerte

---

## 💡 Conseils utiles

### 🎯 Bien remplir son inventaire
```
Article             Quantité   Seuil   Emplacement   Péremption
─────────────────────────────────────────────────────────────
Tomates             3 kg       2 kg    Frigo         2026-02-15
Lait                1.5 L      1 L     Frigo         2026-01-25
Pâtes               500 g      200 g   Placard       2027-12-31
Oeufs               6          4       Frigo         2026-02-10
Poulet congelé      1.2 kg     0.5 kg  Congélateur   2026-06-01
```

### 📍 Emplacements standards
- 🧊 Frigo (0-4°C)
- ❄️ Congélateur (-18°C)
- 📦 Placard (ambiant)
- 🕳️ Cave (frais, sombre)
- 🥕 Garde-manger (sec)

### 🏷️ Catégories standard
- Légumes
- Fruits
- Féculents
- Protéines
- Laitier
- Épices & Condiments
- Conserves
- Surgelés
- Autre

### ⏰ Dates d'expiration
- **Courte terme:** Fruits, légumes → 1-2 semaines
- **Moyen terme:** Lait, yaourt → 2-3 semaines
- **Long terme:** Pâtes, riz → 6-12 mois

---

## 🔧 Utilisation avancée

### Via Python (pour intégrations)

```python
from src.services.inventaire import get_inventaire_service
from datetime import date

service = get_inventaire_service()

# 📖 Récupérer
inventaire = service.get_inventaire_complet()
alertes = service.get_alertes()

# ✏️ Créer/modifier/supprimer
service.ajouter_article(
    ingredient_nom="Tomate",
    quantite=5.0,
    quantite_min=2.0,
    emplacement="Frigo",
    date_peremption=date(2026, 2, 15)
)

service.mettre_a_jour_article(article_id=1, quantite=3.0)
service.supprimer_article(article_id=1)

# 📊 Analyser
stats = service.get_statistiques()
cat_stats = service.get_stats_par_categorie()
a_prelever = service.get_articles_a_prelever()

# 🤖 Suggestions IA
suggestions = service.suggerer_courses_ia()
```

### Via filtres UI

```
Stock:
├─ Filtrer par emplacement (Frigo, Placard, etc)
├─ Filtrer par catégorie (Légumes, Fruits, etc)
├─ Filtrer par statut (critique, stock_bas, peremption_proche, ok)
└─ Combiner multiple filtres

Alertes:
└─ Voir automatiquement tous les articles problématiques

Catégories:
└─ Cliquer l'onglet de votre catégorie

Suggestions:
└─ Cliquer "Générer" pour IA
```

---

## ❓ FAQ

### Q: Où trouver mon article dans l'inventaire?
**R:** Onglet Stock → Utiliser Filtres pour chercher

### Q: Comment modifier la quantité d'un article?
**R:** Service: `mettre_a_jour_article()` ou via UI future

### Q: Pourquoi article marqué critique?
**R:** Stock < 50% du seuil minimum

### Q: Comment ajouter un nouvel article?
**R:** Service: `ajouter_article()` ou UI future (onglet Stock)

### Q: Les suggestions IA sont vides?
**R:** 
1. Vérifier que vous avez des alertes
2. Vérifier MISTRAL_API_KEY configurée
3. Attendre 3-5 secondes après clic

### Q: Exporter prend du temps?
**R:** Non, instant! Si lent = vérifier navigateur

### Q: Puis-je importer un CSV?
**R:** En développement - actuellement export seulement

### Q: Les statistiques se mettent à jour?
**R:** Cache 30 min (cliquer Rafraîchir pour forcer)

---

## 🧪 Tests rapides

```bash
# Vérifier que module charge
python -c "from src.services.inventaire import get_inventaire_service; print('✅ OK')"

# Exécuter tests
pytest tests/test_inventaire.py -v

# Voir couverture
pytest tests/test_inventaire.py --cov=src/services/inventaire --cov-report=term-missing
```

---

## 📚 Ressources

| Ressource | Lien |
|-----------|------|
| Guide complet | [INVENTAIRE_GUIDE.md](INVENTAIRE_GUIDE.md) |
| Changements | [INVENTAIRE_CHANGES.md](INVENTAIRE_CHANGES.md) |
| Code UI | [src/modules/cuisine/inventaire.py](src/modules/cuisine/inventaire.py) |
| Code Service | [src/services/inventaire.py](src/services/inventaire.py) |
| Tests | [tests/test_inventaire.py](tests/test_inventaire.py) |

---

## 🎯 Checklist de démarrage

- [ ] Application Streamlit lancée
- [ ] Navigué vers Cuisine → Inventaire
- [ ] Vu les 5 onglets
- [ ] Vérifié le stock (onglet Stock)
- [ ] Checké les alertes (onglet Alertes)
- [ ] Essayé les suggestions IA
- [ ] Téléchargé le CSV
- [ ] Ran les tests
- [ ] Lire le guide complet

---

**Prêt à l'emploi! Bon usage! 🚀**

*Dernière mise à jour: 18 janvier 2026*
