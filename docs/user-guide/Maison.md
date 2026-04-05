# 🏠 Guide Module Maison

> Gérez vos projets, l'entretien, le jardin, l'énergie, les équipements et les finances de votre maison.

---

## Vue d'ensemble

Le module **Maison** couvre tout ce qui concerne la gestion de l'habitat :

| Sous-module | Accès | Description |
|-------------|-------|-------------|
| Visualisation | Maison → Visualisation | Plan de la maison et vue des espaces |
| Ménage | Maison → Ménage | Planning de ménage et tâches ménagères |
| Jardin | Maison → Jardin | Planification du jardin, plantes, semis |
| Travaux | Maison → Travaux | Projets de travaux et rénovation |
| Équipements | Maison → Équipements | Inventaire des équipements avec garanties |
| Artisans | Maison → Artisans | Carnet d'artisans avec historique |
| Diagnostics | Maison → Diagnostics | Diagnostics immobiliers |
| Finances | Maison → Finances | Charges, dépenses, abonnements |
| Abonnements | Maison → Abonnements | Comparateur d'abonnements |
| Provisions | Maison → Provisions | Stocks de produits ménagers |
| Documents | Maison → Documents | Documents maison (factures, contrats) |

---

## Ménage & Entretien

### Créer une tâche d'entretien

1. Allez dans **Maison → Ménage**
2. Cliquez sur **Nouvelle tâche**
3. Renseignez :
   - **Nom** de la tâche (ex : « Nettoyer les filtres hotte »)
   - **Fréquence** (hebdomadaire, mensuelle, trimestrielle, annuelle)
   - **Prochaine date** prévue
   - **Pièce** concernée (optionnel)
4. La tâche apparaît dans le planning d'entretien

### Marquer une tâche comme faite

1. Dans la liste des tâches, cliquez sur **Fait**
2. La prochaine date est **automatiquement recalculée** selon la fréquence
3. L'historique est conservé

<!-- Screenshot: Planning d'entretien avec tâches à venir -->

### Suggestions basées sur l'âge des équipements

L'IA analyse l'âge de vos équipements et suggère des opérations d'entretien préventif :
- Détartrage ballon d'eau chaude (> 2 ans)
- Changement filtre VMC (> 6 mois)
- Ramonage cheminée (> 1 an)

### Alertes météo → entretien

Le bridge **météo-entretien** analyse les prévisions et déclenche des alertes :
- Gel annoncé → protéger les canalisations extérieures
- Canicule → vérifier la climatisation
- Tempête → sécuriser le jardin

---

## Jardin

### Gérer les plantes

1. Allez dans **Maison → Jardin**
2. Ajoutez vos plantes avec : **nom**, **variété**, **date de plantation**, **emplacement**
3. Suivez les récoltes et les soins

### Calendrier de semis personnalisé

L'IA génère un **calendrier de semis/récolte** personnalisé selon :
- Votre **région** et **climat**
- La **latitude** et **longitude**
- Le **mois** en cours

Accessible via **IA → Calendrier semis personnalisé**.

### Diagnostic plante IA

Prenez une photo d'une plante malade et l'IA diagnostique :
- Le **problème** détecté (maladie, carence, parasite)
- Les **traitements** recommandés
- Les **mesures préventives**

### Bridge récolte → recettes

Quand vous enregistrez une récolte de jardin, le bridge **récolte-recettes** propose automatiquement des recettes utilisant cet ingrédient pour la semaine planifiée suivante.

<!-- Screenshot: Page jardin avec plantes et calendrier de semis -->

---

## Travaux & Projets

### Créer un projet

1. Allez dans **Maison → Travaux**
2. Cliquez sur **Nouveau projet**
3. Renseignez :
   - **Nom** et **description** du projet
   - **Budget** estimé
   - **Priorité** (haute, moyenne, basse)
   - **Statut** (planifié, en cours, terminé)
   - **Pièce** concernée

### Estimation IA de travaux

L'IA peut estimer un projet via :
- **Description textuelle** → estimation budget + durée
- **Photo** → analyse visuelle + estimation (Pixtral)

### Comparaison de devis artisans

Pour un projet avec plusieurs devis d'artisans, l'IA compare :
- Les **tarifs** (main d'œuvre + matériaux)
- Les **délais** proposés
- Le rapport **qualité/prix**

<!-- Screenshot: Projet avec estimation IA et comparaison devis -->

---

## Équipements

### Inventaire des équipements

1. Allez dans **Maison → Équipements**
2. Ajoutez un équipement : **nom**, **marque**, **date d'achat**, **durée de garantie**, **pièce**
3. Un badge **« sous garantie »** s'affiche si l'équipement est encore couvert

### Prédiction de pannes

L'IA analyse l'âge et l'état de vos équipements pour prédire les risques de panne :
- Niveau de risque (faible, moyen, élevé)
- Actions préventives recommandées
- Estimation de la durée de vie restante

---

## Artisans

1. Allez dans **Maison → Artisans**
2. Ajoutez un artisan : **nom**, **spécialité**, **téléphone**, **email**, **notes**
3. Reliez les artisans aux projets pour garder l'historique des interventions

---

## Finances maison

### Charges fixes

1. Allez dans **Maison → Finances**
2. Consultez les charges mensuelles : loyer/crédit, électricité, eau, gaz, assurances, etc.
3. Ajoutez ou modifiez une charge

### Dépenses

- Historique des dépenses maison par catégorie
- Graphiques de tendances mensuelles
- Prévision de fin de mois (IA)

### Abonnements — Comparateur

1. Allez dans **Maison → Abonnements**
2. Le comparateur analyse vos abonnements actuels (eau, électricité, gaz, assurances, chaudière, téléphone, internet)
3. Identifiez les **économies possibles** en changeant de fournisseur

---

## Énergie

### Relevés de consommation

1. Allez dans **Maison → Finances** → section Énergie
2. Saisissez vos relevés (électricité, eau, gaz)
3. Visualisez les **tendances** et **comparaisons** N/N-1

### Anomalies énergie

L'IA détecte les anomalies de consommation :
- Pic soudain d'électricité ou d'eau
- Consommation anormalement haute par rapport à la période

### Recommandations énergie

L'IA recommande des **économies d'énergie** basées sur votre consommation :
- Créneaux heures creuses/pleines pour les machines
- Température optimale par pièce
- Estimation de la prochaine facture

### Comparateur fournisseurs

Compare les offres des fournisseurs d'énergie selon votre profil de consommation.

---

## Provisions (Stocks ménagers)

1. Allez dans **Maison → Provisions**
2. Gérez les stocks de produits ménagers (lessive, savon, papier toilette, etc.)
3. Quand un stock est bas, un article est automatiquement suggéré pour la liste de courses

---

## Habitat (module avancé)

Le sous-module **Habitat** gère les projets immobiliers :

| Fonction | Description |
|----------|-------------|
| **Scénarios** | Comparer des scénarios d'achat immobilier |
| **Veille immo** | Alertes sur les nouvelles annonces |
| **Marché DVF** | Historique des prix via les données DVF publiques |
| **Plans** | Plans de maison avec analyse IA |
| **Déco** | Projets de décoration avec suggestions IA |
| **Jardin paysager** | Aménagement paysager avec canvas |

### Estimation ROI immobilier

L'IA estime le prix d'un bien et calcule le ROI d'une rénovation en se basant sur les données DVF de la zone.

---

## Diagnostic photo maison

Prenez une photo d'un problème dans la maison (fuite, fissure, moisissure...) et l'IA :
- **Diagnostique** le problème
- Propose des **solutions** (DIY ou professionnel)
- Estime le **coût** de réparation

---

## Intégrations IA

| Fonctionnalité | Description |
|----------------|-------------|
| **Diagnostic photo** | Analyse visuelle de problèmes maison |
| **Estimation travaux** | Budget + durée depuis photo/description |
| **Prédiction pannes** | Risques de panne par équipement |
| **Anomalies énergie** | Détection de consommation anormale |
| **Comparateur énergie** | Comparaison fournisseurs |
| **Recommandations énergie** | Économies d'énergie personnalisées |
| **Calendrier semis** | Semis/récolte personnalisé par région |
| **Diagnostic plante** | Analyse photo de plantes malades |
| **Suggestions entretien** | Entretien préventif basé sur l'âge |
| **Estimation ROI** | Prix immobilier + ROI rénovation |
| **Comparaison devis** | Analyse comparative de devis artisans |
