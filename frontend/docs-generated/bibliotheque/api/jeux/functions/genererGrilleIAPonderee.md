[**Assistant Matanne — Frontend**](../../../../README.md)

***

[Assistant Matanne — Frontend](../../../../README.md) / [bibliotheque/api/jeux](../README.md) / genererGrilleIAPonderee

# Function: genererGrilleIAPonderee()

> **genererGrilleIAPonderee**(`mode?`, `sauvegarder?`): `Promise`\<\{ `analyse`: `string`; `confiance`: `number`; `mode`: `string`; `numero_chance`: `number`; `numeros`: `number`[]; `sauvegardee`: `boolean`; \}\>

Defined in: [bibliotheque/api/jeux.ts:159](https://github.com/Trilian/assistant_matanne/blob/363b51de0e987de2bff6b0f6d8a68f1492dc8d71/frontend/src/bibliotheque/api/jeux.ts#L159)

Générer une grille Loto avec IA pondérée

## Parameters

### mode?

`"chauds"` \| `"froids"` \| `"equilibre"`

### sauvegarder?

`boolean` = `false`

## Returns

`Promise`\<\{ `analyse`: `string`; `confiance`: `number`; `mode`: `string`; `numero_chance`: `number`; `numeros`: `number`[]; `sauvegardee`: `boolean`; \}\>
