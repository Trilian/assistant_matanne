# 🗺️ ROADMAP — Assistant Matanne

> **Dernière mise à jour** : 28 mars 2026

🔍 **Audit complet** : [`ANALYSE_COMPLETE.md`](ANALYSE_COMPLETE.md) — état réel, bugs, dette technique, plan long terme  
📅 **Plan d'implémentation** : [`PLANNING_IMPLEMENTATION.md`](PLANNING_IMPLEMENTATION.md) — sprints 1-9, tâches détaillées

---

## 🟠 Sprint 2 en cours — Bugs hauts + Nettoyage documentation

> Semaine 2 | 28 mars → 4 avril 2026 | Priorité : HIGH

| # | Tâche | Item | Statut |
|---|-------|------|--------|
| 1 | `url_source` absent du modèle ORM Recette | B-06 | ✅ Done |
| 2 | `verifier_saison` silencieusement ignoré → warning | B-07 | ✅ Done |
| 3 | Lien sidebar "Calendriers" → 404 | B-11 | ✅ Done |
| 4 | `RetourRecette.est_favori` vs `feedback` mismatch | B-12 | ✅ Done |
| 5 | Supprimer `STATUS_PHASES.md` (1004 lignes redondantes) | CT-15 | ✅ Done |
| 6 | Nettoyer `ROADMAP.md` (ce fichier) | CT-16 | ✅ Done |
| 7 | Nettoyer `docs/` (4 fichiers obsolètes) | CT-17 | ✅ Done |
| 8 | Mettre à jour `docs/MIGRATION_GUIDE.md` — workflow DB | CT-11 | ✅ Done |

---

## 📅 Prochains sprints

| Sprint | Thème | Items clés |
|--------|-------|-----------|
| **Sprint 3** (Sem 3) | Tests manquants | CT-07, CT-12, CT-13, CT-14 |
| **Sprint 4** (Sem 4) | Features cuisine/famille/Jules | CT-05, CT-06, CT-09 |
| **Sprint 5** (Sem 5-6) | Notifications email + Admin étendu | CT-01, CT-02 |
| **Sprint 6** (Sem 7-8) | Cron jobs + SQL avancé | CT-03, CT-04, CT-08, CT-10 |
| **Sprint 7** (Mois 2) | Inter-modules + Dashboard | MT-01, MT-03, MT-06 |
| **Sprint 8** (Mois 3) | Canal WhatsApp + IA avancée | MT-02, MT-04~07 |
| **Sprint 9** (Mois 3+) | Innovations & Long terme | LT-01~04 |

→ Détail complet dans [`PLANNING_IMPLEMENTATION.md`](PLANNING_IMPLEMENTATION.md)

---

## Moyen terme

### Fonctionnalités

- [ ] **Notifications push complètes** — logique d'envoi des rappels (Famille/Jeux/Maison)
  → Sprints 5-6 — infrastructure déjà en place (endpoints + APScheduler)

- [ ] **Collaboration temps réel courses** — tester multi-utilisateur, stabiliser WebSocket
  → Sprint 6 — `src/api/websocket_courses.py` déjà implémenté

- [ ] **Planning IA amélioré** — suggestions nutritionnelles + prise en compte historique complet
  → Sprint 6 — base existante dans `src/services/planning/`

- [ ] **Dashboard widgets configurables** — drag & drop, choix des métriques
  → Sprint 7 — hubs famille/maison/jeux déjà réordonnables (localStorage)

- [ ] **Canal WhatsApp** — notifications famille via WhatsApp Business API
  → Sprint 8 — `src/services/integrations/` à créer

### Technique

- [ ] **Tests de couverture** — atteindre 80 %+ sur les modules critiques (cuisine, famille)
  → Sprint 3 — `pytest --cov=src` actuellement < 50 %

- [ ] **Upgrade httpx → 0.29+** — attendre support mistralai
  → Surveiller [mistralai releases](https://github.com/mistralai/client-python/releases)

---

## Principes

- **Pas de feature creep** : chaque ajout doit résoudre un besoin réel de la famille
- **Stabilité d'abord** : corriger les bugs et tests avant d'ajouter des fonctionnalités
- **Documentation à jour** : toute nouvelle feature = mise à jour du guide et de l'API reference
- **Sécurité** : RLS Supabase, JWT, rate limiting, sanitization — non négociables
