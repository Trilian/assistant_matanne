# Guide Utilisateur — Assistant Matanne

Bienvenue dans la documentation utilisateur d'**Assistant Matanne**, votre hub familial tout-en-un pour gérer le quotidien avec simplicité et intelligence.

## 📚 Table des matières

- [Premiers pas](./getting-started.md) — Installation, inscription et tour rapide
- [FAQ — Questions fréquentes](./FAQ.md) — Réponses aux questions courantes
- [Modules](#modules) — Vue d'ensemble des fonctionnalités

---

## 🎯 Qu'est-ce qu'Assistant Matanne ?

Assistant Matanne est une application web moderne qui centralise la gestion familiale :

### 🍽️ **Cuisine**
- **Recettes** : Bibliothèque de recettes avec recherche avancée, tags et notes
- **Planning repas** : Planification hebdomadaire avec suggestions IA
- **Courses** : Listes de courses intelligentes générées depuis les recettes
- **Inventaire** : Suivi des stocks avec dates de péremption
- **Batch Cooking** : Organisation des sessions de préparation
- **Anti-Gaspillage** : Suggestions pour utiliser les restes

### 👨‍👩‍👦 **Famille**
- **Jules** : Suivi du développement de l'enfant (jalons, vaccins, croissance)
- **Activités** : Gestion des activités familiales et emploi du temps
- **Routines** : Routines quotidiennes et habitudes
- **Budget** : Suivi des dépenses familiales
- **Weekend** : Suggestions d'activités pour le weekend
- **Anniversaires** : Rappels et organisation
- **Contacts** : Carnet d'adresses familial
- **Journal** : Journal familial avec suivi d'humeur
- **Documents** : Stockage et organisation des documents importants

### 🏡 **Maison**
- **Projets** : Gestion des travaux et projets maison
- **Jardin** : Planification et suivi du jardin
- **Entretien** : Calendrier d'entretien avec rappels
- **Charges** : Suivi des charges fixes
- **Dépenses** : Historique des dépenses maison
- **Énergie** : Relevés et suivi de consommation
- **Stocks** : Inventaire général (produits ménagers, etc.)
- **Cellier** : Gestion de la cave à vin
- **Artisans** : Coordonnées et historique des interventions
- **Contrats** : Gestion des contrats (assurance, abonnements)
- **Garanties** : Suivi des garanties et factures
- **Diagnostics** : Stockage des diagnostics immobiliers
- **Visualisation** : Plan de la maison et visualisation des espaces
- **Éco-Tips** : Conseils écologiques et économies d'énergie

### 📅 **Planning**
- Vue calendrier unifiée
- Timeline interactive
- Synchronisation avec les événements famille

### 🎮 **Jeux**
- **Paris sportifs** : Suivi et statistiques (mode virtuel ou réel)
- **Loto** : Gestion des grilles et tirages
- **EuroMillions** : Gestion des grilles

### 🛠️ **Outils**
- **Chat IA** : Assistant conversationnel pour suggestions cuisine
- **Convertisseur** : Conversion d'unités (masse, volume, température)
- **Météo** : Prévisions météo intégrées
- **Minuteur** : Minuteurs de cuisine multiples
- **Notes** : Prise de notes rapide

---

## ✨ Fonctionnalités clés

### Intelligence Artificielle
- **Suggestions de recettes** basées sur inventaire et préférences
- **Génération de planning** hebdomadaire équilibré
- **Suggestions d'activités weekend** adaptées à l'âge de l'enfant
- **Analyse nutritionnelle** automatique
- **Optimisation anti-gaspillage**

### Navigation rapide
- **`Ctrl+K` (ou `Cmd+K`)** : Palette de commandes — recherchez et accédez instantanément à n'importe quelle page sans cliquer dans les menus. Affiche aussi les 5 dernières pages visitées.
- **★ Favoris** : Épingle tes pages les plus utilisées via le bouton ★ dans le fil d'ariane. Elles apparaîssent en haut de la sidebar.
- **Ma Semaine** (`/ma-semaine`) : Vue trans-modules de la semaine en cours — repas planifiés, activités famille, matchs du jour et tâches ménage sur un seul écran.
- **Chat IA flottant** (bouton 🤖 en bas à droite) : Mini-chat accessible depuis n'importe quelle page sans quitter son contexte. Sur mobile, redirige vers la page Chat IA complète.
- **Minuteur flottant** : Lance un minuteur depuis la page Outils → Minuteur — une barre discrète reste visible dans toute l'application tant que le minuteur tourne.

### Collaboration
- **Partage en temps réel** des listes de courses (WebSocket)
- **Export PDF** (planning, courses, recettes, budget)
- **Export iCal** pour synchronisation avec calendriers externes

### Mobile-First
- Interface responsive optimisée mobile
- Navigation bottom bar sur petits écrans (Accueil, Cuisine, Famille, Maison, Ma Semaine)
- Gestes tactiles intuitifs

### Sécurité
- Authentification JWT sécurisée
- Row Level Security (RLS) Supabase
- Chiffrement des données sensibles (mots de passe)
- Rate limiting API (protection DDoS)

---

## 🚀 Démarrage rapide

1. **[Créer un compte](./getting-started.md#inscription)** — Inscription rapide en 2 minutes
2. **[Explorer le dashboard](./getting-started.md#dashboard)** — Vue d'ensemble de vos données
3. **[Ouvrir “Ma Semaine”](./FAQ.md#navigation)** — Vue unifiée de toute la semaine
4. **[Ajouter votre première recette](./getting-started.md#recettes)** — Commencez à construire votre bibliothèque
5. **[Générer un planning IA](./getting-started.md#planning-ia)** — Laissez l'IA planifier vos repas

---

## 📸 Screenshots

Voir le dossier [`screenshots/`](./screenshots/) pour des captures d'écran de tous les modules.

---

## 🆘 Besoin d'aide ?

- **[FAQ](./FAQ.md)** — Questions fréquentes et solutions
- **Support** — Contactez-nous via [contact@assistant-matanne.fr](mailto:contact@assistant-matanne.fr)
- **GitHub Issues** — Signalez un bug ou proposez une fonctionnalité

---

## 📱 Accès

- **URL Production** : https://assistant-matanne.vercel.app
- **Compatibilité** : Chrome, Firefox, Safari, Edge (dernières versions)
- **Mobile** : iOS 14+, Android 10+

---

**Version** : 1.0.0  
**Dernière mise à jour** : Mars 2026
