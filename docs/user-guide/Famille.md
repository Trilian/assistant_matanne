# 👨‍👩‍👧 Guide Module Famille

> Suivez le développement de Jules, organisez les activités familiales, gérez le budget et les routines du quotidien.

---

## Vue d'ensemble

Le module **Famille** regroupe tout ce qui concerne la vie familiale :

| Sous-module | Accès | Description |
|-------------|-------|-------------|
| Jules | Famille → Jules | Suivi développement enfant (jalons, alimentation, vaccins, activités) |
| Activités | Famille → Activités | Gestion des activités familiales |
| Routines | Famille → Routines | Routines quotidiennes avec streaks |
| Budget | Famille → Budget | Suivi des dépenses familiales |
| Achats | Famille → Achats | Suivi des achats importants |
| Weekend | — | Suggestions d'activités weekend |
| Anniversaires | Famille → Anniversaires | Rappels et organisation |
| Voyages | Famille → Voyages | Planification de voyages avec checklists IA |
| Contacts | Famille → Contacts | Carnet d'adresses familial |
| Documents | Famille → Documents | Stockage et organisation des documents |
| Garmin | Famille → Garmin | Intégration sportive Garmin |

---

## Jules — Suivi enfant

### Consulter le profil de Jules

1. Depuis la sidebar, cliquez sur **Famille → Jules**
2. Vous voyez le résumé :
   - **Jalons** de développement atteints
   - **Prochains jalons** attendus
   - **Alimentation** adaptée
   - **Activités** récentes
   - **Suivi vaccinal**

<!-- Screenshot: Page Jules avec résumé développement -->

### Ajouter un jalon

1. Sur la page Jules, rubrique **Jalons**
2. Cliquez sur **Ajouter un jalon**
3. Indiquez la **date**, le **type** (moteur, langage, social...) et une **description**
4. Le jalon s'affiche dans la timeline

### Alimentation de Jules

Jules mange les mêmes repas que la famille, mais **adaptés** :
- Pas de sel ajouté
- Pas d'alcool dans les sauces
- Pas de morceaux durs (version mixée/simplifiée selon l'âge)

L'IA adapte automatiquement les recettes du planning quand Jules est inclus.

### Conseils IA pour Jules

L'IA peut générer des conseils de développement proactifs pour Jules basés sur son âge et ses jalons. Accessible via **IA → Conseil Jules**.

<!-- Screenshot: Conseils IA personnalisés pour Jules -->

---

## Activités

### Ajouter une activité

1. Allez dans **Famille → Activités**
2. Cliquez sur **Nouvelle activité**
3. Renseignez :
   - **Nom** de l'activité
   - **Date et heure**
   - **Lieu** (optionnel)
   - **Participants**
   - **Notes**
4. L'activité apparaît dans le calendrier unifié

### Suggestions weekend

L'IA propose des idées d'activités pour le weekend adaptées à :
- L'**âge de Jules**
- La **météo** prévue
- L'**historique** des activités récentes (pour varier)

---

## Routines

### Créer une routine

1. Allez dans **Famille → Routines**
2. Cliquez sur **Nouvelle routine**
3. Définissez :
   - **Nom** (ex : « Routine du matin »)
   - **Fréquence** (quotidienne, hebdomadaire...)
   - **Étapes** de la routine
   - **Heure** de rappel (optionnel)

### Suivi des streaks

Chaque routine suivie au quotidien accumule un **streak** (série consécutive). Le suivi est visible :
- Sur la page Routines (compteur de jours)
- Via l'endpoint `GET /intra/routines-streak`

### Coach IA routines

L'IA analyse vos routines et suggère des **optimisations** :
- Regroupement de tâches
- Ajustement des horaires
- Identification des routines abandonnées

---

## Budget famille

### Consulter le budget

1. Allez dans **Famille → Budget**
2. Visualisez :
   - **Dépenses du mois** par catégorie
   - **Tendances** par rapport au mois précédent
   - **Prévision** de fin de mois (IA)

<!-- Screenshot: Vue budget avec graphiques par catégorie -->

> **Note** : Le budget jeux est volontairement séparé du budget famille.

### Ajouter une dépense

1. Sur la page Budget, cliquez sur **Ajouter**
2. Renseignez le **montant**, la **catégorie**, la **date** et une **description**
3. L'IA peut **catégoriser automatiquement** une dépense à partir de sa description

### Détection d'anomalies

L'IA surveille les catégories budgétaires et alerte si une catégorie dépasse **80 %** de son seuil habituel.

---

## Voyages

### Planifier un voyage

1. Allez dans **Famille → Voyages**
2. Cliquez sur **Nouveau voyage**
3. Renseignez la **destination**, les **dates**, le **type** de séjour
4. L'IA peut **générer automatiquement** :
   - Des **checklists** par catégorie (vêtements, documents, Jules, pharmacie...)
   - Un **planning** jour par jour
   - Un **budget** estimé

### Générer les courses depuis un voyage

1. Ouvrez un voyage existant
2. Cliquez sur **Générer les courses**
3. Les articles des checklists sont ajoutés à votre liste de courses

### Cocher les articles

- Dans la vue détail du voyage, cochez les articles préparés dans chaque checklist
- Le pourcentage de complétion s'affiche en temps réel

---

## Garmin

### Connecter Garmin

1. Allez dans **Famille → Garmin**
2. Cliquez sur **Connecter**
3. Autorisez l'accès via la page OAuth Garmin
4. Les données de sport sont synchronisées automatiquement

### Données disponibles

| Donnée | Description |
|--------|-------------|
| **Activités sportives** | Type d'activité, durée, distance, calories |
| **Fréquence cardiaque** | Moyenne, repos, zones HR |
| **Pas quotidiens** | Compteur de pas |
| **Calories brûlées** | Total journalier |

### Recommandation dîner

Après une activité sportive intense, l'IA propose un **dîner adapté** à la dépense énergétique du jour : plus de protéines et glucides après un effort important, repas léger après une journée calme.

---

## Contacts

### Gérer le carnet d'adresses

1. Allez dans **Famille → Contacts**
2. Ajoutez des contacts avec : **nom**, **téléphone**, **email**, **adresse**, **catégorie** (famille, amis, professionnels)
3. L'IA peut **enrichir** automatiquement les contacts

---

## Documents

### Stocker un document

1. Allez dans **Famille → Documents**
2. Cliquez sur **Uploader**
3. Sélectionnez le fichier (PDF, image — max 10 Mo)
4. L'IA peut **analyser** et **classer** automatiquement le document

### Alertes d'expiration

Les documents avec date d'expiration (carte d'identité, passeport, etc.) déclenchent une alerte **30 jours** avant l'échéance.

---

## Anniversaires

1. Allez dans **Famille → Anniversaires**
2. Ajoutez les dates d'anniversaire des proches
3. L'application :
   - Envoie un **rappel** avant la date
   - Propose un **menu festif** adapté (via le bridge anniversaire → menu)
   - Peut suggérer des **idées cadeaux** personnalisées (IA)

---

## Intégrations IA

| Fonctionnalité | Description |
|----------------|-------------|
| **Conseils Jules** | Conseils de développement adaptés à l'âge |
| **Planning Jules adaptatif** | Planning d'activités personnalisé pour Jules |
| **Weekend IA** | Suggestions d'activités pour le weekend |
| **Prévision budget** | Prédiction de dépenses fin de mois |
| **Anomalies budget** | Détection de dépassements par catégorie |
| **Score famille hebdo** | Score de bien-être familial composite |
| **Journal familial** | Journal automatique avec résumé IA |
| **Idées cadeaux** | Suggestions personnalisées pour les proches |
| **Checklist voyage** | Génération IA de checklists de voyage |
