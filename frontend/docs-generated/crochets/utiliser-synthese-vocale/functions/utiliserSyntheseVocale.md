[**Assistant Matanne — Frontend**](../../../README.md)

***

[Assistant Matanne — Frontend](../../../README.md) / [crochets/utiliser-synthese-vocale](../README.md) / utiliserSyntheseVocale

# Function: utiliserSyntheseVocale()

> **utiliserSyntheseVocale**(`options?`): `object`

Defined in: [crochets/utiliser-synthese-vocale.ts:17](https://github.com/Trilian/assistant_matanne/blob/363b51de0e987de2bff6b0f6d8a68f1492dc8d71/frontend/src/crochets/utiliser-synthese-vocale.ts#L17)

Hook d'interface avec l'API Web Speech Synthesis pour la lecture vocale.

## Parameters

### options?

`OptionsSynthese` = `{}`

Langue (défaut fr-FR), débit, hauteur, volume

## Returns

`object`

### arreter

> **arreter**: () => `void`

#### Returns

`void`

### enLecture

> **enLecture**: `boolean`

### estSupporte

> **estSupporte**: `boolean`

### lire

> **lire**: (`texte`) => `void`

#### Parameters

##### texte

`string`

#### Returns

`void`
