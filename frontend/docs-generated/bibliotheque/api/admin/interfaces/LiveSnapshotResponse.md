[**Assistant Matanne — Frontend**](../../../../README.md)

***

[Assistant Matanne — Frontend](../../../../README.md) / [bibliotheque/api/admin](../README.md) / LiveSnapshotResponse

# Interface: LiveSnapshotResponse

Defined in: [bibliotheque/api/admin.ts:448](https://github.com/Trilian/assistant_matanne/blob/363b51de0e987de2bff6b0f6d8a68f1492dc8d71/frontend/src/bibliotheque/api/admin.ts#L448)

## Properties

### api

> **api**: `object`

Defined in: [bibliotheque/api/admin.ts:450](https://github.com/Trilian/assistant_matanne/blob/363b51de0e987de2bff6b0f6d8a68f1492dc8d71/frontend/src/bibliotheque/api/admin.ts#L450)

#### ai

> **ai**: [`ObjetDonnees`](../../../../types/commun/type-aliases/ObjetDonnees.md)

#### latency

> **latency**: `object`

##### latency.avg\_ms

> **avg\_ms**: `number`

##### latency.p95\_ms

> **p95\_ms**: `number`

##### latency.tracked\_endpoints

> **tracked\_endpoints**: `number`

#### rate\_limiting

> **rate\_limiting**: [`ObjetDonnees`](../../../../types/commun/type-aliases/ObjetDonnees.md)

#### requests\_total

> **requests\_total**: `number`

#### top\_endpoints

> **top\_endpoints**: `object`[]

#### uptime\_seconds

> **uptime\_seconds**: `number`

***

### cache

> **cache**: [`ObjetDonnees`](../../../../types/commun/type-aliases/ObjetDonnees.md)

Defined in: [bibliotheque/api/admin.ts:462](https://github.com/Trilian/assistant_matanne/blob/363b51de0e987de2bff6b0f6d8a68f1492dc8d71/frontend/src/bibliotheque/api/admin.ts#L462)

***

### generated\_at

> **generated\_at**: `string`

Defined in: [bibliotheque/api/admin.ts:449](https://github.com/Trilian/assistant_matanne/blob/363b51de0e987de2bff6b0f6d8a68f1492dc8d71/frontend/src/bibliotheque/api/admin.ts#L449)

***

### jobs

> **jobs**: `object`

Defined in: [bibliotheque/api/admin.ts:463](https://github.com/Trilian/assistant_matanne/blob/363b51de0e987de2bff6b0f6d8a68f1492dc8d71/frontend/src/bibliotheque/api/admin.ts#L463)

#### last\_24h

> **last\_24h**: `Record`\<`string`, `number`\>

***

### security

> **security**: `object`

Defined in: [bibliotheque/api/admin.ts:466](https://github.com/Trilian/assistant_matanne/blob/363b51de0e987de2bff6b0f6d8a68f1492dc8d71/frontend/src/bibliotheque/api/admin.ts#L466)

#### events\_1h

> **events\_1h**: `number`
