# AI Services

> Référence des services IA, de leurs usages actuels et des garde-fous communs.

---

## Fondations communes

La brique IA du projet repose sur:

- client IA: `src/core/ai/`
- base commune: `src/services/core/base/`
- limitation de débit et cache sémantique intégrés
- parsing structuré des réponses via Pydantic

Capacités transverses fournies par `BaseAIService`:

- appels synchrones et structurés
- cache sémantique
- parsing JSON / liste / modèle Pydantic
- gestion d'erreur et fallback
- pilotage uniforme des prompts système

---

## Services IA identifiés

| Domaine | Service | Rôle principal |
| --------- | --------- | ---------------- |
| Cuisine | `ServiceSuggestions` | suggestions recettes et planning |
| Cuisine | `ServicePredictionCourses` | prédiction d'achats |
| Cuisine | `ServicePredictionPeremption` | prédiction / priorisation péremption |
| Famille | `JulesAIService` | développement enfant |
| Famille | `WeekendAIService` | idées weekend |
| Famille | `SoireeAIService` | suggestions de soirée |
| Famille | `AchatsIAService` | suggestions d'achats famille |
| Dashboard | `ResumeFamilleIAService` | résumé hebdomadaire |
| Dashboard | `ServiceAnomaliesFinancieres` | anomalies budgétaires |
| Jeux | `JeuxAIService` | analyses paris et opportunités |
| Maison | services projets / jardin / conseiller | conseils et enrichissement ciblé |
| Outils | `ChatAIService` | chat conversationnel multi-contexte |
| Intégrations | `MultiModalAIService` | OCR, analyse image, multimodal |

---

## Chat IA multi-contexte

Le chat IA de `src/services/utilitaires/chat_ai.py` gère actuellement les contextes:

- `cuisine`
- `famille`
- `maison`
- `budget`
- `general`
- `nutrition`

Objectif actuel du service:

- réponses contextualisées par domaine
- mémoire courte de conversation
- actions rapides et ton adapté au contexte

---

## Bonnes pratiques projet

- toujours utiliser les abstractions du package `src/core/ai`
- préférer les sorties structurées Pydantic quand la réponse nourrit une logique métier
- limiter les appels coûteux via cache et rate limiting
- éviter les prompts non bornés côté route API
- journaliser les dégradations sans faire échouer tout le flux utilisateur si l'IA est un enrichissement non bloquant

---

## Limites et points à surveiller

- certaines fonctionnalités restent encore rule-based et non enrichies par IA
- le chat multi-module peut encore être enrichi avec plus de contexte inter-modules
- certains services métier utilisent l'IA comme enrichissement, pas comme source de vérité

---

## Références associées

- `docs/ARCHITECTURE.md`
- `docs/INTER_MODULES.md`
- `docs/TROUBLESHOOTING.md`
