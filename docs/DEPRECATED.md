# Deprecated Features

> Inventaire des fonctionnalités retirées, refusées ou remplacées.
>
> Ce document centralise les références historiques pour éviter qu'elles réapparaissent dans la documentation active.

---

## Canal de messagerie

| Fonctionnalité retirée | Statut | Remplacement | Raison |
| --- | --- | --- | --- |
| Intégration WhatsApp Meta | retiré | Telegram Bot | coût, contraintes de templates, limite 24h, complexité de maintenance |
| Documentation active WhatsApp | retiré | guides Telegram | le projet est Telegram-only |

---

## OCR et scan de tickets

| Fonctionnalité retirée | Statut | Remplacement | Raison |
| --- | --- | --- | --- |
| OCR documents générique | retiré | saisie guidée, import structuré quand disponible | trop fragile pour une app familiale privée |
| OCR tickets jeux | retiré | saisie manuelle ou flux FDJ/API quand disponible | faible valeur, maintenance forte |
| scan de tickets de caisse | retiré | veille prix automatique ultérieure si nécessaire | trop contraignant au quotidien |
| catégorisation OCR de dépenses | retiré | saisie ciblée et automatisations métier | précision insuffisante et expérience médiocre |

---

## Suivi Jules — croissance physique

| Fonctionnalité retirée | Statut | Remplacement | Raison |
| --- | --- | --- | --- |
| courbe de croissance Jules (poids, taille, périmètre, percentiles OMS) | retiré | jalons de développement, alimentation, activités, vaccins | hors besoin produit, ne plus reproposer |
| références OMS de poids/taille/IMC dans la doc active | retiré | repères d'âge simplifiés si nécessaire | éviter de réintroduire un suivi non souhaité |

---

## Partage, social et exports non prioritaires

| Fonctionnalité retirée | Statut | Remplacement | Raison |
| --- | --- | --- | --- |
| marketplace recettes | refusé | aucun | pas de volet social/public |
| partage public / communautaire | refusé | partage privé limité | hors scope du hub familial |
| partage par QR code | refusé | lien classique | peu utile dans le contexte réel |
| export Notion / Obsidian | refusé | export backup personnel | pas de besoin produit |

---

## Budget et gamification

| Fonctionnalité retirée | Statut | Remplacement | Raison |
| --- | --- | --- | --- |
| fusion budget jeux vers budget famille | refusé | budgets séparés | décision architecture explicite |
| mode budget serré alimentaire | refusé | aucun | le projet ne pousse pas d'économies alimentaires forcées |
| suggestions recettes anti-inflation automatiques | refusé | suggestions qualité/plaisir | même raison |
| gamification familiale étendue | retiré | sport/Garmin uniquement | le projet limite la gamification au sport |
| module jeu responsable | retiré du codebase | aucun | scope supprimé |

---

## Maison et gestion personnelle

| Fonctionnalité retirée | Statut | Remplacement | Raison |
| --- | --- | --- | --- |
| CRUD garanties dédié | retiré | badge "sous garantie" sur la fiche équipement | besoin couvert sans module dédié |
| alertes renouvellement contrats | retiré | comparateur d'abonnements ciblé | priorité produit plus utile |
| géolocalisation supermarché et push proximité | retiré | aucun | usage non pertinent |

---

## Règle projet

- toute nouvelle doc active doit éviter de réintroduire ces fonctionnalités comme si elles étaient supportées
- si une référence historique est nécessaire, elle doit pointer vers ce document
- toute proposition produit doit respecter : Telegram-only, pas d'OCR, pas de social public, budgets jeux/famille séparés, pas de courbe de croissance/percentiles OMS pour Jules
