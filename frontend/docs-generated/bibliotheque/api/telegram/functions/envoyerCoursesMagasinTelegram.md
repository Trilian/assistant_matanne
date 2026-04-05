[**Assistant Matanne — Frontend**](../../../../README.md)

***

[Assistant Matanne — Frontend](../../../../README.md) / [bibliotheque/api/telegram](../README.md) / envoyerCoursesMagasinTelegram

# Function: envoyerCoursesMagasinTelegram()

> **envoyerCoursesMagasinTelegram**(`listeId`, `magasin`, `nomListe?`): `Promise`\<\{ `id?`: `number` \| `null`; `message`: `string`; \}\>

Defined in: [bibliotheque/api/telegram.ts:57](https://github.com/Trilian/assistant_matanne/blob/363b51de0e987de2bff6b0f6d8a68f1492dc8d71/frontend/src/bibliotheque/api/telegram.ts#L57)

Envoyer une sous-liste de courses filtrée par magasin via Telegram.
Idéal pour Bio Coop / Grand Frais avant de se rendre en magasin physique.

## Parameters

### listeId

`number`

### magasin

`string`

### nomListe?

`string`

## Returns

`Promise`\<\{ `id?`: `number` \| `null`; `message`: `string`; \}\>
