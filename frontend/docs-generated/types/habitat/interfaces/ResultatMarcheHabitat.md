[**Assistant Matanne — Frontend**](../../../README.md)

***

[Assistant Matanne — Frontend](../../../README.md) / [types/habitat](../README.md) / ResultatMarcheHabitat

# Interface: ResultatMarcheHabitat

Defined in: [types/habitat.ts:240](https://github.com/Trilian/assistant_matanne/blob/363b51de0e987de2bff6b0f6d8a68f1492dc8d71/frontend/src/types/habitat.ts#L240)

## Properties

### historique

> **historique**: [`HistoriqueMarcheHabitatPoint`](HistoriqueMarcheHabitatPoint.md)[]

Defined in: [types/habitat.ts:262](https://github.com/Trilian/assistant_matanne/blob/363b51de0e987de2bff6b0f6d8a68f1492dc8d71/frontend/src/types/habitat.ts#L262)

***

### query

> **query**: `object`

Defined in: [types/habitat.ts:246](https://github.com/Trilian/assistant_matanne/blob/363b51de0e987de2bff6b0f6d8a68f1492dc8d71/frontend/src/types/habitat.ts#L246)

#### code\_postal?

> `optional` **code\_postal?**: `string` \| `null`

#### commune?

> `optional` **commune?**: `string` \| `null`

#### departement?

> `optional` **departement?**: `string` \| `null`

#### nb\_pieces\_min?

> `optional` **nb\_pieces\_min?**: `number` \| `null`

#### surface\_min\_m2?

> `optional` **surface\_min\_m2?**: `number` \| `null`

#### type\_local?

> `optional` **type\_local?**: `string` \| `null`

***

### repartition\_types

> **repartition\_types**: [`RepartitionTypeMarcheHabitat`](RepartitionTypeMarcheHabitat.md)[]

Defined in: [types/habitat.ts:263](https://github.com/Trilian/assistant_matanne/blob/363b51de0e987de2bff6b0f6d8a68f1492dc8d71/frontend/src/types/habitat.ts#L263)

***

### resume

> **resume**: `object`

Defined in: [types/habitat.ts:254](https://github.com/Trilian/assistant_matanne/blob/363b51de0e987de2bff6b0f6d8a68f1492dc8d71/frontend/src/types/habitat.ts#L254)

#### dernier\_mois?

> `optional` **dernier\_mois?**: [`HistoriqueMarcheHabitatPoint`](HistoriqueMarcheHabitatPoint.md) \| `null`

#### nb\_transactions

> **nb\_transactions**: `number`

#### prix\_m2\_median?

> `optional` **prix\_m2\_median?**: `number` \| `null`

#### prix\_m2\_moyen?

> `optional` **prix\_m2\_moyen?**: `number` \| `null`

#### surface\_mediane?

> `optional` **surface\_mediane?**: `number` \| `null`

#### valeur\_mediane?

> `optional` **valeur\_mediane?**: `number` \| `null`

***

### source

> **source**: `object`

Defined in: [types/habitat.ts:241](https://github.com/Trilian/assistant_matanne/blob/363b51de0e987de2bff6b0f6d8a68f1492dc8d71/frontend/src/types/habitat.ts#L241)

#### dataset\_id

> **dataset\_id**: `string`

#### resource\_id?

> `optional` **resource\_id?**: `string` \| `null`

#### resource\_title?

> `optional` **resource\_title?**: `string` \| `null`

***

### transactions

> **transactions**: [`TransactionMarcheHabitat`](TransactionMarcheHabitat.md)[]

Defined in: [types/habitat.ts:264](https://github.com/Trilian/assistant_matanne/blob/363b51de0e987de2bff6b0f6d8a68f1492dc8d71/frontend/src/types/habitat.ts#L264)
