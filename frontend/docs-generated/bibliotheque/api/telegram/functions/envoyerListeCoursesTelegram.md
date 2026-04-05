[**Assistant Matanne — Frontend**](../../../../README.md)

***

[Assistant Matanne — Frontend](../../../../README.md) / [bibliotheque/api/telegram](../README.md) / envoyerListeCoursesTelegram

# Function: envoyerListeCoursesTelegram()

> **envoyerListeCoursesTelegram**(`listeId`, `nomListe?`): `Promise`\<\{ `id?`: `number` \| `null`; `message`: `string`; \}\>

Defined in: [bibliotheque/api/telegram.ts:39](https://github.com/Trilian/assistant_matanne/blob/363b51de0e987de2bff6b0f6d8a68f1492dc8d71/frontend/src/bibliotheque/api/telegram.ts#L39)

Envoyer la liste de courses via Telegram avec boutons interactifs
Appelé après confirmerCourses() pour notifier les utilisateurs via Telegram

Le callback_data sera formaté comme:
- courses_confirmer:ID (confirme la liste)
- courses_ajouter:ID (lien web pour ajouter des articles)
- courses_refaire:ID (crée une nouvelle liste)

## Parameters

### listeId

`number`

### nomListe?

`string`

## Returns

`Promise`\<\{ `id?`: `number` \| `null`; `message`: `string`; \}\>
