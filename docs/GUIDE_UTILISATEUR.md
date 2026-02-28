# 📖 Guide Utilisateur — MaTanne

> Hub de gestion familial pour Anne & Mathieu (et le petit Jules !)
> Application Streamlit accessible depuis le navigateur.

---

## Table des matières

1. [Premiers pas](#premiers-pas)
2. [Accueil — Tableau de bord](#accueil--tableau-de-bord)
3. [Planning](#-planning)
4. [Cuisine](#-cuisine)
5. [Famille](#-famille)
6. [Maison](#-maison)
7. [Jeux](#-jeux)
8. [Outils](#-outils)
9. [Données](#-données)
10. [Cuisine+ (Outils)](#-cuisine-outils)
11. [Productivité](#-productivité)
12. [Outils Maison](#-outils-maison)
13. [Configuration](#%EF%B8%8F-configuration)
14. [FAQ & Dépannage](#faq--dépannage)

---

## Premiers pas

### Lancer l'application

```bash
streamlit run src/app.py
```

L'application s'ouvre dans votre navigateur (par défaut `http://localhost:8501`).

### Navigation

La barre latérale gauche organise toutes les fonctionnalités par **sections**. Cliquez sur un module pour y accéder. La page d'accueil est le tableau de bord par défaut.

### Prérequis

- Base de données PostgreSQL (Supabase) initialisée avec le script `sql/INIT_COMPLET.sql`
- Fichier `.env.local` à la racine du projet avec `DATABASE_URL` et éventuellement `MISTRAL_API_KEY`

---

## Accueil — Tableau de bord

🏠 **Page d'accueil** avec un aperçu global de votre vie familiale :

- **Métriques rapides** : repas planifiés, courses en attente, alertes stocks, prochains événements
- **Alertes critiques** : dates de péremption, rappels vaccins, entretien en retard
- **Raccourcis rapides** vers les modules les plus utilisés

---

## 📅 Planning

### 🎯 Cockpit Familial

Vue d'ensemble de la semaine : repas, activités, routines, tâches maison. Tout en un coup d'œil pour orchestrer votre quotidien.

### 📅 Calendrier

Calendrier interactif avec tous les événements familiaux, médicaux, scolaires. Supporte les calendriers externes (Google, Apple, Outlook) via import iCal.

### 📋 Templates

Créez et réutilisez des **templates de semaine type** : semaine scolaire, vacances, semaine de télétravail… Appliquez-les en un clic pour pré-remplir votre planning.

### 📊 Timeline

Visualisation chronologique des événements et activités sur une frise temporelle. Idéal pour voir la charge de la semaine.

---

## 🍳 Cuisine

### 🍽️ Planifier Repas

Planification hebdomadaire des repas. L'**IA Mistral** peut suggérer des menus équilibrés en tenant compte de :

- Vos préférences alimentaires (exclusions, favoris)
- L'âge de Jules et ses besoins
- Les saisons, le budget, le temps disponible
- L'équilibre nutritionnel (poisson, végétarien, viande rouge…)

Générez automatiquement la liste de courses depuis le planning validé.

### 🍳 Batch Cooking

Organisez vos sessions de **cuisine en lot** le weekend :

- Sélectionnez les recettes à préparer
- L'app génère un planning d'étapes optimisé (en parallèle si possible)
- Suivi des portions préparées, stockage (frigo/congélateur), dates de péremption
- Timer intégré pour chaque étape
- Mode "avec Jules" pour les recettes adaptées bébé

### 🛒 Courses

Gestion complète des listes de courses :

- Génération automatique depuis le planning des repas
- Organisation par rayon de magasin
- Cochez les articles au fur et à mesure des achats
- Estimation du budget
- Modèles de courses réutilisables (courses hebdo, mensuelle…)

### 📋 Recettes

Votre bibliothèque de recettes personnelle :

- **Import** depuis URL (Marmiton, CuisineAZ…), PDF ou saisie manuelle
- **Catégories** : entrée, plat, dessert, goûter…
- **Tags** : saison, type de cuisine, batch-cooking, adaptée bébé
- **Historique** : nombre de préparations, notes, avis
- **Versions** : version bébé, version batch cooking

### 🥫 Inventaire

Suivi de votre stock alimentaire :

- **Scan code-barres** (EAN-13, EAN-8, UPC, QR) via la caméra
- **OpenFoodFacts** : enrichissement automatique (nom, marque, Nutriscore, allergènes…)
- **Alertes péremption** : notification avant la date limite
- **Seuils minimum** : alerte quand le stock descend sous le seuil
- Lieu de stockage (frigo, placard, congélateur…)

### 🌾 Bio & Local

Trouvez des producteurs locaux et produits bio. Conseils pour une alimentation responsable.

---

## 👨‍👩‍👧‍👦 Famille

### 🏠 Hub Famille

Centre névralgique de la vie familiale : événements à venir, tâches en cours, budget du mois.

### 👶 Jules

**Suivi du développement** de Jules :

- **Courbes de croissance** (poids, taille, périmètre crânien) comparées aux normes OMS
- **Jalons de développement** (premiers mots, premiers pas…) avec photos et récits
- **Bien-être** : humeur, sommeil, activités quotidiennes

### 📅 Planning Jules

Planning hebdomadaire spécifique à Jules : crèche, activités, routines, rendez-vous médicaux.

### 💪 Mon Suivi

Suivi personnel de santé et fitness :

- **Objectifs** : pas quotidiens, calories, minutes actives
- **Routines santé** : sport, méditation, alimentation
- **Intégration Garmin** (optionnelle) : synchronisation automatique des données fitness
- **Journal alimentaire** avec suivi nutritionnel

### 🎉 Weekend

Planification des **sorties et activités du weekend** :

- Suggestions adaptées à l'âge de Jules
- Filtrage par météo, coût, distance
- Notes et évaluations des lieux visités
- Historique et « à refaire »

### 🛍️ Achats

Liste d'achats famille (hors alimentaire) :

- Catégorisation (jouets, vêtements, puériculture…)
- Priorités et suivi des prix
- Suggestions par âge recommandé

### 🎭 Activités

Planification d'**activités familiales** : sorties, loisirs, événements.
Suivi des coûts et participation.

### ⏰ Routines

Gestion des **routines quotidiennes** familiales :

- Routine du matin, du soir, du bain…
- Tâches assignées par personne
- Suivi de complétion

### 🏥 Carnet Santé

**Carnet de santé numérique** complet :

- **Vaccinations** : calendrier vaccinal, rappels automatiques, numéros de lot
- **Rendez-vous médicaux** : historique par spécialité, ordonnances, comptes rendus
- **Mesures de croissance** : percentiles OMS en temps réel

### 📅 Calendrier Famille

Calendrier partagé avec événements familiaux, médicaux, scolaires, anniversaires.

### 🎂 Anniversaires

Dates importantes et rappels automatiques (7 jours et 1 jour avant).
Historique des cadeaux offerts.

### 📞 Contacts

Répertoire familial organisé par catégorie : médical, garde, éducation, administration, famille, urgence.
Contacts d'urgence en accès rapide.

### ❤️ Soirée Couple

Suggestions d'activités en couple, planification de soirées.

### 📸 Album Souvenirs

Albums photo familiaux numériques. Associez des souvenirs aux jalons de développement de Jules.

### 💪 Santé Globale

Vue d'ensemble de la santé de toute la famille : objectifs, routines, derniers rendez-vous.

### 📝 Journal IA

Journal familial enrichi par l'**IA** : résumés automatiques, suggestions d'activités basées sur l'historique.

### 📁 Documents

**Coffre-fort numérique** pour les documents importants :

- Identité, médical, scolaire, administratif, assurance
- Alertes d'expiration
- Recherche par membre de famille, type, tags

### ✈️ Mode Voyage

Planification de voyages familiaux :

- Budget prévisionnel et suivi des dépenses
- **Checklists personnalisées** par type de voyage (plage, montagne, ville…)
- Templates de checklists réutilisables
- Suivi des réservations

### 🖨️ Routines PDF

Export et impression des routines au format PDF pour les afficher (porte du frigo, chambre de Jules…).

---

## 🏠 Maison

### 🏠 Maison

Tableau de bord maison : tâches du jour, charge de la semaine, score journalier, alertes entretien.

### 🌱 Jardin

Gestion de votre jardin :

- **Plantes** : catalogue complet avec calendrier de semis/récolte, compagnonnage
- **Historique des actions** : arrosage, traitement, taille…
- **Objectifs d'autonomie alimentaire** : suivi production vs besoins annuels

### 🌿 Zones Jardin

Plan visuel du jardin avec zones (potager, verger, pelouse…) et plantes positionnées.
Suivi des récoltes par zone.

### 🏡 Entretien

Gestion des **tâches d'entretien** récurrentes :

- Fréquence paramétrable (hebdo, mensuel, annuel…)
- Responsable assigné
- Alertes de retard

### 💡 Charges

Suivi des **charges mensuelles** : électricité, gaz, eau, internet…
Graphiques d'évolution et comparaison année/année.

### 💰 Dépenses

Suivi de toutes les dépenses de la maison par catégorie (jardin, entretien, énergie, travaux, équipement…).
Budgets par catégorie avec alertes de dépassement.

### 🌿 Éco-Tips

Actions écologiques mises en place, économies mensuelles réalisées, suivi de la transition.

### ⚡ Énergie

Suivi détaillé de la consommation énergétique. Graphiques et tendances.

### 🪑 Meubles

Inventaire du mobilier par pièce : état, prix, priorité d'achat/remplacement. Suivi des souhaits.

### 🏗️ Projets

Gestion de **projets maison** (rénovation, aménagement…) avec tâches, budget, timeline.

### 📄 Contrats

Suivi de tous les **contrats et abonnements** :

- Type (énergie, internet, assurance…)
- Dates de renouvellement et résiliation
- Montants mensuels/annuels
- Alertes avant tacite reconduction

### 👷 Artisans

Carnet d'adresses des **artisans** et professionnels :

- Métier, spécialité, zone d'intervention
- Notes et recommandations
- Historique des interventions avec coûts

### 🍷 Cellier

Inventaire du cellier/garde-manger non alimentaire (ou cave à vin) :

- Suivi des quantités et dates limites (DLC/DLUO)
- Alertes de seuil

### 📋 Diagnostics

Suivi des **diagnostics immobiliers** : DPE, amiante, électricité…
Alertes de renouvellement. Suivi de l'estimation immobilière.

### 🛡️ Garanties

Gestion des **garanties et SAV** :

- Appareils, dates d'achat, fin de garantie
- Garanties étendues
- Historique des incidents et réparations

### ✅ Checklists

Checklists vacances/départ : préparez tout avant de partir. Templates réutilisables par type de voyage.

### 🐛 Nuisibles

Suivi des **traitements nuisibles** : type, zone, produit, efficacité, date du prochain traitement.

### 📑 Devis

**Comparatif de devis** pour vos projets travaux :

- Plusieurs artisans par projet
- Lignes de devis détaillées
- Notes et choix final

### 📊 Relevés

Relevés de compteurs (eau, gaz, électricité) avec calcul automatique de consommation journalière et détection d'anomalies.

### 🗓️ Entretien Saisonnier

Calendrier des **entretiens saisonniers** prédéfinis (chaudière, gouttières, ramonage, toiture…) avec rappels automatiques et indication si professionnel requis.

---

## 🎲 Jeux

> Module de suivi et simulation — **Jeu responsable** avec limites de mises intégrées.

### ⚽ Paris Sportifs

Suivi des paris (réels ou virtuels) :

- Saisie des matchs avec cotes et prédictions
- Historique des résultats, ROI
- Modèle de prédiction avec taux de confiance

### 🎰 Loto

Suivi des tirages Loto :

- Historique des tirages officiels
- Grilles jouées (réelles ou virtuelles)
- Statistiques de fréquence : numéros chauds/froids, retards, paires

### ⭐ Euromillions

Même principe que le Loto, adapté à l'Euromillions (5 numéros + 2 étoiles).

### 📊 Bilan Global

Vue consolidée des résultats tous jeux confondus : mises vs gains, tendances.

### 📈 Comparatif ROI

Comparaison du retour sur investissement entre les différents types de jeux.

### 🔔 Alertes Pronostics

Alertes automatiques quand une **série statistique** atteint un seuil significatif (value bet).

### 🧠 Biais Cognitifs

Module éducatif sur les biais psychologiques liés aux jeux (gambler's fallacy, etc.).

### 📅 Calendrier Jeux

Calendrier des prochains tirages et matchs à suivre.

### 🎓 Module Éducatif

Contenus pédagogiques sur les probabilités et la gestion responsable des jeux.

### 💰 Jeu Responsable

Limites de mises mensuelles avec alertes progressives (50%, 75%, 90%, 100%), cooldown et auto-exclusion.

---

## 🔧 Outils

### 📱 Code-barres

Scannez les codes-barres via la caméra pour identifier un produit (OpenFoodFacts) et l'ajouter à l'inventaire.

### 🧾 Scan Factures

Numérisez vos factures pour extraction automatique des données (montant, date, fournisseur).

### 🔍 Produits

Recherche de produits dans la base OpenFoodFacts par nom ou code-barres.

### 📊 Rapports

Génération de rapports PDF : résumé hebdomadaire, bilan mensuel, export de données.

### 🔔 Notifications

Configuration des notifications push : catégories activées, heures silencieuses, canal préféré.

### 💬 Chat IA

**Chat libre avec l'IA Mistral** pour poser des questions sur vos données, obtenir des conseils cuisine/famille/maison.

---

## 📦 Données

### 📤 Export Global

Exportez toutes vos données en un seul fichier (CSV, JSON) pour sauvegarde ou migration.

### 📥 Import Masse

Importez des données en masse depuis des fichiers CSV (template fourni dans `data/TEMPLATE_IMPORT.csv`).

---

## 🍳 Cuisine+ (Outils)

### ⚖️ Convertisseur

Conversion d'unités culinaires : grammes ↔ tasses, ml ↔ cuillères, Celsius ↔ Fahrenheit…

### 🔢 Portions

Calculatrice de mise à l'échelle des recettes : doublez ou réduisez les quantités automatiquement.

### 🔄 Substitutions

Suggestions de **substitutions d'ingrédients** : sans gluten, sans lactose, végan…

### 💰 Coût Repas

Estimation du coût d'un repas basé sur les prix inventaire.

### 🥕 Saisons

Calendrier des **fruits et légumes de saison** pour cuisiner responsable.

### ⏱️ Minuteur

Minuteur de cuisine avec alarme, utilisable en parallèle de la navigation.

---

## 📝 Productivité

### 📝 Notes

Bloc-notes avec catégories, couleurs, épinglage et archivage. Votre post-it numérique.

### 📓 Journal

Journal de bord quotidien : humeur, énergie, gratitudes, tags personnalisés.

### 📋 Presse-papiers

Presse-papiers partagé entre membres de la famille pour s'échanger textes et infos.

### 🔗 Favoris

Liens utiles classés par catégorie (recettes en ligne, sites admin, shopping…).

### 📇 Contacts

Annuaire de contacts utiles (dentiste, plombier, école, nounou…) avec catégories.

### ⏳ Compte à rebours

Comptes à rebours pour événements importants (anniversaires, vacances, fin de contrats…).

---

## 🏠 Outils Maison

### 🌤️ Météo

Prévisions météo locales avec alertes jardin (gel, canicule, pluie).

### ⚡ Suivi Énergie

Relevés d'énergie (électricité, gaz, eau) avec graphiques d'évolution et comparaisons.

### 🔐 Mots de passe

Gestionnaire de mots de passe maison (WiFi, alarme, codes…). Stockage chiffré.

### 📱 QR Codes

Générateur de QR codes pour partager rapidement un lien, un texte ou un contact.

---

## ⚙️ Configuration

### ⚙️ Paramètres

Configuration globale de l'application :

- **Foyer** : profils utilisateurs (Anne, Mathieu), informations santé, objectifs fitness
- **Affichage** : thème (clair/sombre/auto)
- **Budget** : seuils d'alerte par catégorie
- **IA** : clé API Mistral, limites de requêtes quotidiennes/horaires
- **Cache** : gestion du cache multi-niveaux (mémoire, session, fichier)
- **Base de données** : statut de connexion, health check
- **Sécurité** : PIN de protection par section
- **À propos** : version, statistiques de l'application

### 🎨 Design System

Aperçu de tous les composants UI disponibles dans l'application (pour les développeurs).

---

## FAQ & Dépannage

### L'application ne démarre pas

1. Vérifiez que l'environnement virtuel est activé : `.venv\Scripts\Activate.ps1`
2. Installez les dépendances : `pip install -r requirements.txt`
3. Lancez : `streamlit run src/app.py`

### La base de données ne se connecte pas

1. Vérifiez `DATABASE_URL` dans `.env.local` (format : `postgresql://user:pass@host:5432/db`)
2. Testez : `python -c "from src.core.db import obtenir_moteur; obtenir_moteur().connect()"`
3. Si première utilisation, exécutez `sql/INIT_COMPLET.sql` dans Supabase SQL Editor

### Les suggestions IA ne fonctionnent pas

1. Vérifiez `MISTRAL_API_KEY` dans `.env.local`
2. Vérifiez les limites de requêtes (quotidiennes/horaires) dans Paramètres > IA
3. L'IA fonctionne sans connexion en mode dégradé (pas de suggestions)

### Le scan code-barres ne marche pas

- Autorisez l'accès caméra dans votre navigateur
- Utilisez Chrome ou Firefox (meilleur support WebRTC)
- Essayez avec un bon éclairage et un code-barres bien lisible

### Comment sauvegarder mes données ?

- **Export** : allez dans 📦 Données > Export Global
- **Base de données** : faites un backup depuis Supabase Dashboard
- Les backups automatiques sont traçés dans la table `sauvegardes`

### Comment réinitialiser la base de données ?

⚠️ **Attention : cela supprime TOUTES vos données !**

1. Exécutez `sql/INIT_COMPLET.sql` dans Supabase SQL Editor
2. Le script supprime toutes les tables existantes puis les recrée
3. Les profils Anne & Mathieu et les données de référence sont réinsérés

---

_Dernière mise à jour : Février 2026_
