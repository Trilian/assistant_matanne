# 🗺️ ROADMAP — Assistant Matanne

> **Dernière mise à jour** : 28 mars 2026 (Sprint 10 MVP)

🔍 **Audit complet** : [`ANALYSE_COMPLETE.md`](ANALYSE_COMPLETE.md) — état réel, bugs, dette technique, plan long terme  
📅 **Plan d'implémentation** : [`PLANNING_IMPLEMENTATION.md`](PLANNING_IMPLEMENTATION.md) — sprints 1-10, tâches détaillées

---

## ✅ Sprints 1–7 terminés

**Sprint 1 — Bugs critiques push** : P-01/P-02/P-03/B-05 ✅  
**Sprint 4 — Features Jules + Cuisine** : CT-05/CT-06/CT-09/QW-02 ✅  
**Sprint 5 — Notifications + Admin + 2FA** : CT-01/CT-02/WhatsApp webhook/RouteurIA/Redis L2 ✅  
**Sprint 6 — Cron jobs** : CT-03/CT-04 (10 jobs APScheduler actifs) ✅  
**Sprint 7 — SQL consolidation + Bugs + Tests + Doc** ✅

- P-04/P-05/P-06 : migrations SQL absorbées dans INIT_COMPLET (Sprint 1)
- P-07 : alembic archivé (`alembic.ini.bak`)
- B-06/B-07/B-11/B-12 : bugs corrigés
- CT-08 : index SQL manquants ajoutés
- CT-10 : audit orphelines ORM ↔ SQL + test de non-régression
- CT-12/CT-13/CT-14/CT-07 : tests push, admin, famille créés
- CT-02-FE : page Admin Jobs (`/admin/jobs`) créée
- CT-11/CT-15/CT-16/CT-17 : documentation nettoyée

---

## 🔜 Sprint 8 — Inter-modules + Dashboard avancé

| # | Tâche | Item | Effort |
| --- | ------- | ------ | -------- |
| 1 | Cellier ↔ Inventaire cuisine consolidé | MT-01 | M |
| 2 | Score bien-être global (IA-09) | MT-03 | M |
| 3 | Alertes météo contextuelles cross-modules | MT-04 | M |
| 4 | Widgets dashboard configurables (drag & drop) | MT-06 | L |
| 5 | Timeline vie familiale | MT-08 | M |
| 6 | OCR photo-frigo → auto-sync inventaire | MT-09 | S |
| 7 | Widget météo sur dashboard | QW-01 | XS |
| 8 | "Aujourd'hui dans l'histoire de la famille" | QW-06 | S |

→ Détail dans [`PLANNING_IMPLEMENTATION.md`](PLANNING_IMPLEMENTATION.md#sprint-8)

---

## 🔜 Sprint 9 — WhatsApp sortant + IA avancée

- MT-02 : WhatsApp sortant proactif (messages préemptifs Meta Cloud API)
- MT-07 : Assistant vocal (Web Speech API → commandes Mistral)
- J-03 à J-11 : cron jobs restants (péremptions, planning dimanche, budget mensuel…)
- IA-04/IA-05/IA-07/IA-08 : planificateur vacances, anomalies financières, optimisation budget, diagnostic photo maison

Note : plusieurs items de Sprint 9 sont désormais partiellement ou totalement implémentés côté backend, notamment la refonte notifications, l'extension CRON (68 jobs) et le moteur d'automations enrichi. Le détail opérationnel à jour se trouve dans `PLANNING_IMPLEMENTATION.md` et les guides de documentation spécialisés.

---

## 🔜 Sprint 10 — Innovations & Long terme

- ✅ LT-01 : Intégration Garmin santé/sport (sync matinale + recommandations dîner)
- ✅ LT-02 : Gamification sport + alimentation (points/badges persistés + page dédiée)
- ✅ LT-03 : Mode Voyage avec checklists intelligentes (scaling participants + génération courses)
- ✅ LT-04 : Automations "Si → Alors" (table DB + moteur + cron + exécution manuelle)

État réel du moteur LT-04 au 1er avril 2026 :

- 9 déclencheurs supportés
- 10 actions supportées
- dry-run global et par règle
- génération IA de règle structurée

→ Détail dans [`PLANNING_IMPLEMENTATION.md`](PLANNING_IMPLEMENTATION.md#sprint-10)

---

## Principes

- **Pas de feature creep** : chaque ajout doit résoudre un besoin réel de la famille
- **Stabilité d'abord** : corriger les bugs et tests avant d'ajouter des fonctionnalités
- **Documentation à jour** : toute nouvelle feature = mise à jour du guide et de l'API reference
- **Sécurité** : RLS Supabase, JWT, rate limiting, sanitization — non négociables

