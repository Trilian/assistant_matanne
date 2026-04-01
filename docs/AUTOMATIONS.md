# Automations

> Documentation du moteur d'automatisation Si?Alors.
>
> **Derni�re mise � jour** : 1er avril 2026

---

## Vue d'ensemble

Le moteur d'automations ex�cute des r�gles stock�es en base � fr�quence r�guli�re.

Composants :

- routes API : `src/api/routes/automations.py`
- moteur : `src/services/utilitaires/automations_engine.py`
- ex�cution planifi�e : job CRON `automations_runner` (toutes les 5 minutes)
- mod�le ORM : `AutomationRegle`

---

## D�clencheurs support�s (9)

| Type | Description |
| ------ | ------------- |
| `stock_bas` | Articles inventaire sous un seuil |
| `peremption_proche` | Articles arrivant � p�remption proche |
| `budget_depassement` | D�penses du mois au-dessus d'un seuil |
| `meteo_alerte` | Pr�vision m�t�o contenant un mot-cl� (pluie, orage, neige, vent) |
| `anniversaire_proche` | Anniversaires dans une fen�tre de jours |
| `tache_en_retard` | T�ches d'entretien en retard |
| `garmin_inactivite` | Inactivit� Garmin au-del� d'un seuil |
| `document_expiration` | Documents arrivant � expiration |
| `recette_sans_photo` | Recettes sans image |

---

## Actions support�es (10)

| Type | Description |
| ------ | ------------- |
| `ajouter_courses` | Ajoute articles � une liste de courses active |
| `generer_liste_courses` | Alias de `ajouter_courses` |
| `suggerer_recette` | Envoie une notification de suggestion recette |
| `creer_tache_maison` | Cr�e une t�che d'entretien |
| `ajouter_au_planning` | Cr�e un �v�nement planning |
| `mettre_a_jour_budget` | Ajoute une d�pense d'ajustement budget |
| `generer_rapport_pdf` | Notifie qu'un rapport PDF est pr�t |
| `archiver` | D�sactive la r�gle apr�s ex�cution |
| `notifier` | Notification ntfy + push |
| `envoyer_whatsapp` | Notification WhatsApp |
| `envoyer_email` | Notification email |

---

## Ex�cution

- le job `automations_runner` passe toutes les 5 minutes
- seules les r�gles actives sont �valu�es
- le moteur met � jour `derniere_execution` et incr�mente `execution_count`
- support du **dry-run** global et par r�gle

M�thodes principales :

- `executer_automations_actives()`
- `executer_automations_actives_dry_run()`
- `executer_automation_par_id()`

---

## API disponible

| M�thode | Route | Usage |
| --------- | ------- | ------- |
| `GET` | `/api/v1/automations` | Lister les automations de l'utilisateur |
| `POST` | `/api/v1/automations/init` | Initialiser depuis les pr�f�rences legacy |
| `POST` | `/api/v1/automations` | Cr�er une automation |
| `PUT` | `/api/v1/automations/{automation_id}` | Modifier une automation |
| `POST` | `/api/v1/automations/{automation_id}/simuler` | Simuler une automation |
| `POST` | `/api/v1/automations/{automation_id}/executer-maintenant` | Ex�cuter imm�diatement (`dry_run` optionnel) |
| `POST` | `/api/v1/automations/generer-ia` | G�n�rer une r�gle depuis un prompt IA |

Le module expose aussi un format structur� `RegleAutomationIA` pour les r�ponses IA.

---

## Exemple conceptuel

```json
{
  "nom": "Stock bas produits de base",
  "condition": {"type": "stock_bas", "seuil": 2},
  "action": {"type": "ajouter_courses", "quantite": 1},
  "parametres": {}
}
```

---

## Limitations actuelles

- pas d'historique d�taill� persistant par ex�cution d'automation
- pas de rollback m�tier avanc�
- d�clencheurs �valu�s en polling via CRON, pas en temps r�el �v�nementiel

---

## Statut CRON et ex�cution

Le moteur d'automations est orchestr� par le scheduler global de l'application via `automations_runner`.

Statut actuel : **op�rationnel en production**

- jobs planifi�s: 38+ au niveau plateforme
- job automation d�di�: `automations_runner`
- fr�quence recommand�e: 5 minutes

Points de contr�le op�rationnels:

- visibilit� des ex�cutions via routes admin jobs
- logs de derni�re ex�cution consultables
- relance manuelle possible pour diagnostic

---

## Extension pr�vue

D�clencheurs suppl�mentaires cibl�s:

- `document_expirant`
- `peremption_proche`
- `routine_en_retard`
- `seuil_budget_depasse`

Actions suppl�mentaires cibl�es:

- `creer_tache_planning`
- `envoyer_email`
- `envoyer_whatsapp`
- `declencher_webhook`

Am�liorations structurelles pr�vues:

- historique persistant des ex�cutions
- mode dry-run
- meilleure observabilit� des erreurs par r�gle
