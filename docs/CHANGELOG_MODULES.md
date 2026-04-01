# Changelog Modules

Historique transversal par module, au-delà des sprints, avec consolidation fonctionnelle au 1er avril 2026.

## Cuisine

- Ajout de la persistance `batch_cooking_congelation`.
- Renforcement du flux planning → courses → inventaire.
- Déduction automatique des ingrédients après session batch cooking.
- Suggestions IA contextuelles enrichies selon stock, saisonnalité et retours utilisateur.
- Ponts actifs : inventaire → planning, saisonnalité → planning IA, péremption → anti-gaspillage, jardin → recettes.

## Famille

- Consolidation des flux Jules / activités / routines.
- Renforcement des achats famille et des suggestions IA associées.
- Intégration des documents expirants, anniversaires et budget prévisionnel.
- Suggestions activités enrichies via météo et contexte weekend.
- Meilleure articulation entre jalons, notifications et invalidation des caches de suggestions.

## Maison

- Enrichissement du CRUD maison : contrats, garanties, diagnostics, devis, cellier, dépenses.
- Interactions énergie / entretien / courses / dashboard renforcées.
- Diagnostic IA photo → projet maison / artisan documenté et actif.
- Génération de tâches saisonnières jardin/entretien automatisée.

## Habitat

- Extension du module habitat : veille, scénarios, plans, déco, jardin.
- Endpoints dédiés habitat sur API v1.
- Synchronisation veille habitat par job planifié.
- Intégration avec le dashboard et les flux budget/maison.

## Jeux

- Consolidation des services paris / loto / euromillions.
- Jobs de synchronisation des tirages et alertes résultats.
- Sync jeux → budget automatisée quotidiennement.
- Archivage mensuel de l'historique ancien des paris sportifs.

## Outils & Intégrations

- WhatsApp conversationnel et webhooks Meta Cloud API.
- Intégration Google Calendar planifiée.
- Intégration Garmin santé/sport consolidée avec sync matinale et détection d'inactivité.
- Moteur d'automations Si→Alors étendu : 9 déclencheurs, 10 actions, dry-run, exécution manuelle.

## Admin & Observabilité

- Runbook admin étendu à 51 endpoints.
- Cockpit admin, audit logs, sécurité, cache, jobs, feature flags et simulations documentés.
- Historique d'exécution des jobs persisté via `job_executions`.
- Event bus enrichi : 32 événements typés, 51 subscribers.

## Notifications

- Refonte multi-canal unifiée via `DispatcherNotifications`.
- Support ntfy, push web, email et WhatsApp avec failover configurable.
- Historisation des notifications dans `historique_notifications`.
- Throttling utilisateur + digest périodique.

## Documentation

- Création / mise à jour : `EVENT_BUS`, `SECURITY`, `DATA_MODEL`, `WHATSAPP_COMMANDS`, `MONITORING`, `PERFORMANCE`.
- Mise à jour complète au 1er avril 2026 : `CRON_JOBS`, `NOTIFICATIONS`, `ADMIN_RUNBOOK`, `INTER_MODULES`, `AUTOMATIONS`.
- Nouveau guide unifié : `TESTING.md`.
- Schémas API documentés et génération automatisée consolidée.
