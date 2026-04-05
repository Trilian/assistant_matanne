[**Assistant Matanne — Frontend**](../../../../README.md)

***

[Assistant Matanne — Frontend](../../../../README.md) / [bibliotheque/api/recherche](../README.md) / rechercheGlobale

# Function: rechercheGlobale()

> **rechercheGlobale**(`query`, `limit?`, `types?`): `Promise`\<[`ResultatRecherche`](../interfaces/ResultatRecherche.md)[]\>

Defined in: [bibliotheque/api/recherche.ts:49](https://github.com/Trilian/assistant_matanne/blob/363b51de0e987de2bff6b0f6d8a68f1492dc8d71/frontend/src/bibliotheque/api/recherche.ts#L49)

Effectue une recherche globale multi-entités

## Parameters

### query

`string`

Terme de recherche (min 2 caractères)

### limit?

`number` = `20`

Nombre maximum de résultats (défaut: 20, max: 100)

### types?

[`TypeResultatRecherche`](../type-aliases/TypeResultatRecherche.md)[]

## Returns

`Promise`\<[`ResultatRecherche`](../interfaces/ResultatRecherche.md)[]\>

Liste de résultats unifiés

## Throws

Error si le terme est trop court ou si l'API retourne une erreur
