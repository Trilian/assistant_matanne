[**Assistant Matanne — Frontend**](../../../../README.md)

***

[Assistant Matanne — Frontend](../../../../README.md) / [bibliotheque/api/batch-cooking](../README.md) / listerSessionsBatch

# Function: listerSessionsBatch()

> **listerSessionsBatch**(`page?`, `pageSize?`, `statut?`): `Promise`\<\{ `items`: [`SessionBatchCooking`](../../../../types/batch-cooking/interfaces/SessionBatchCooking.md)[]; `pages`: `number`; `total`: `number`; \}\>

Defined in: [bibliotheque/api/batch-cooking.ts:19](https://github.com/Trilian/assistant_matanne/blob/363b51de0e987de2bff6b0f6d8a68f1492dc8d71/frontend/src/bibliotheque/api/batch-cooking.ts#L19)

Lister les sessions de batch cooking

## Parameters

### page?

`number` = `1`

### pageSize?

`number` = `20`

### statut?

`string`

## Returns

`Promise`\<\{ `items`: [`SessionBatchCooking`](../../../../types/batch-cooking/interfaces/SessionBatchCooking.md)[]; `pages`: `number`; `total`: `number`; \}\>
