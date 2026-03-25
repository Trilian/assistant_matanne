# 🗺️ ROADMAP — Assistant Matanne

> Dernière mise à jour : 25 mars 2026

---

## En cours

### Réorganisation docs & SQL

- [x] Suppression docs obsolètes (MIGRATION_CORE_PACKAGES, GUIDE_UTILISATEUR, batch_cooking.md)
- [x] Réécriture MODULES.md, SERVICES_REFERENCE.md, INDEX.md
- [x] Guides complets par module (cuisine, famille, maison, jeux, outils, planning, dashboard, utilitaires)
- [x] Correction RLS Supabase (USING(true) → filtrage par user_id)
- [x] Tables SQL manquantes (webhooks_abonnements, etats_persistants)
- [x] Migrations SQL incrémentales (V001 RLS fix, V002 user_id standardization)
- [x] Nettoyage ROADMAP (suppression historique sprints 1-16)
- [ ] Standardiser user_id VARCHAR → UUID dans les tables existantes (migration V002, application manuelle)

---

## Court terme

### Qualité & stabilité

- [ ] Atteindre 100 % des tests passing (8 tests restants = routes manquantes)
- [ ] Ajouter les 5 routes maison manquantes (DELETE projets, POST routine-repetitions, CRUD cellier-produit)
- [ ] Ajouter les 3 routes dépenses/énergie (prévisions IA, consommation historique)
- [ ] CI/CD : valider les workflows GitHub Actions (deploy.yml, tests.yml)
- [ ] Audit sécurité : valider les headers CORS, rate limiting, et sanitization en production

### Frontend

- [ ] PWA : offline mode fonctionnel (service worker + cache stratégique)
- [ ] Tests E2E Playwright : couverture des parcours critiques (auth, CRUD recettes, courses)
- [ ] Responsive : audit mobile (sidebar, formulaires, tableaux)
- [ ] Accessibilité : rôles ARIA, navigation clavier, contrastes

---

## Moyen terme

### Fonctionnalités

- [ ] Notifications push (abonnements push déjà câblés, logique d'envoi à compléter)
- [ ] Collaboration temps réel courses (WebSocket déjà implémenté, à tester multi-utilisateur)
- [ ] Planning IA amélioré (suggestions nutritionnelles, prise en compte historique)
- [ ] Import recettes par URL ou PDF (service `importer.py` existant, route à exposer)
- [ ] Dashboard widgets configurables (drag & drop, choix des métriques)

### Technique

- [ ] Cache Redis L2 (actuellement L1 mémoire + L3 fichier, Redis optionnel)
- [ ] Observabilité Sentry (DSN déjà en config, intégration à activer)
- [ ] Prometheus / Grafana (métriques déjà collectées, dashboard à créer)
- [ ] Tests de charge (k6 ou locust sur les endpoints critiques)
- [ ] Migration Alembic (remplacer le système SQL-file maison)

---

## Backlog

- [ ] Multi-famille (plusieurs foyers dans la même instance)
- [ ] Scan multi-codes simultané (amélioration scanner codes-barres)
- [ ] Reconnaissance de tickets de caisse (OCR → import courses automatique)
- [ ] Export/import données complet (backup JSON)
- [ ] Intégration calendrier externe (Google Calendar sync bidirectionnelle)
- [ ] Mode hors-ligne complet avec synchronisation au retour en ligne
- [ ] Application mobile native (React Native ou Capacitor)

---

## Principes

- **Pas de feature creep** : chaque ajout doit résoudre un besoin réel de la famille
- **Stabilité d'abord** : corriger les bugs et tests avant d'ajouter des fonctionnalités
- **Documentation à jour** : toute nouvelle feature = mise à jour du guide et de l'API reference
- **Sécurité** : RLS Supabase, JWT, rate limiting, sanitization — non négociables
