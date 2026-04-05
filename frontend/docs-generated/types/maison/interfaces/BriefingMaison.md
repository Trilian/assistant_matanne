[**Assistant Matanne — Frontend**](../../../README.md)

***

[Assistant Matanne — Frontend](../../../README.md) / [types/maison](../README.md) / BriefingMaison

# Interface: BriefingMaison

Defined in: [types/maison.ts:434](https://github.com/Trilian/assistant_matanne/blob/363b51de0e987de2bff6b0f6d8a68f1492dc8d71/frontend/src/types/maison.ts#L434)

## Properties

### alertes

> **alertes**: [`AlerteMaison`](AlerteMaison.md)[]

Defined in: [types/maison.ts:440](https://github.com/Trilian/assistant_matanne/blob/363b51de0e987de2bff6b0f6d8a68f1492dc8d71/frontend/src/types/maison.ts#L440)

***

### cellier\_alertes

> **cellier\_alertes**: `object`[]

Defined in: [types/maison.ts:444](https://github.com/Trilian/assistant_matanne/blob/363b51de0e987de2bff6b0f6d8a68f1492dc8d71/frontend/src/types/maison.ts#L444)

#### jours\_restants

> **jours\_restants**: `number`

#### nom

> **nom**: `string`

#### quantite?

> `optional` **quantite?**: `number`

***

### date

> **date**: `string`

Defined in: [types/maison.ts:435](https://github.com/Trilian/assistant_matanne/blob/363b51de0e987de2bff6b0f6d8a68f1492dc8d71/frontend/src/types/maison.ts#L435)

***

### eco\_score\_jour?

> `optional` **eco\_score\_jour?**: `number`

Defined in: [types/maison.ts:446](https://github.com/Trilian/assistant_matanne/blob/363b51de0e987de2bff6b0f6d8a68f1492dc8d71/frontend/src/types/maison.ts#L446)

***

### energie\_anomalies

> **energie\_anomalies**: `object`[]

Defined in: [types/maison.ts:445](https://github.com/Trilian/assistant_matanne/blob/363b51de0e987de2bff6b0f6d8a68f1492dc8d71/frontend/src/types/maison.ts#L445)

#### message

> **message**: `string`

#### type

> **type**: `string`

***

### entretiens\_saisonniers

> **entretiens\_saisonniers**: `object`[]

Defined in: [types/maison.ts:442](https://github.com/Trilian/assistant_matanne/blob/363b51de0e987de2bff6b0f6d8a68f1492dc8d71/frontend/src/types/maison.ts#L442)

#### description?

> `optional` **description?**: `string`

#### mois

> **mois**: `number`[]

#### nom

> **nom**: `string`

***

### jardin

> **jardin**: `object`[]

Defined in: [types/maison.ts:443](https://github.com/Trilian/assistant_matanne/blob/363b51de0e987de2bff6b0f6d8a68f1492dc8d71/frontend/src/types/maison.ts#L443)

#### action?

> `optional` **action?**: `string`

#### nom

> **nom**: `string`

#### type

> **type**: `string`

#### urgence?

> `optional` **urgence?**: `string`

***

### meteo?

> `optional` **meteo?**: [`MeteoResumeMaison`](MeteoResumeMaison.md)

Defined in: [types/maison.ts:439](https://github.com/Trilian/assistant_matanne/blob/363b51de0e987de2bff6b0f6d8a68f1492dc8d71/frontend/src/types/maison.ts#L439)

***

### projets\_actifs

> **projets\_actifs**: `object`[]

Defined in: [types/maison.ts:441](https://github.com/Trilian/assistant_matanne/blob/363b51de0e987de2bff6b0f6d8a68f1492dc8d71/frontend/src/types/maison.ts#L441)

#### avancement?

> `optional` **avancement?**: `number`

#### id

> **id**: `number`

#### nom

> **nom**: `string`

#### priorite?

> `optional` **priorite?**: `string`

***

### resume

> **resume**: `string`

Defined in: [types/maison.ts:436](https://github.com/Trilian/assistant_matanne/blob/363b51de0e987de2bff6b0f6d8a68f1492dc8d71/frontend/src/types/maison.ts#L436)

***

### taches\_jour

> **taches\_jour**: `string`[]

Defined in: [types/maison.ts:437](https://github.com/Trilian/assistant_matanne/blob/363b51de0e987de2bff6b0f6d8a68f1492dc8d71/frontend/src/types/maison.ts#L437)

***

### taches\_jour\_detail

> **taches\_jour\_detail**: [`TacheJourMaison`](TacheJourMaison.md)[]

Defined in: [types/maison.ts:438](https://github.com/Trilian/assistant_matanne/blob/363b51de0e987de2bff6b0f6d8a68f1492dc8d71/frontend/src/types/maison.ts#L438)
