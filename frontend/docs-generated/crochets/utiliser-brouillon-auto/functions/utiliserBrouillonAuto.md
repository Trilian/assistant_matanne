[**Assistant Matanne — Frontend**](../../../README.md)

***

[Assistant Matanne — Frontend](../../../README.md) / [crochets/utiliser-brouillon-auto](../README.md) / utiliserBrouillonAuto

# Function: utiliserBrouillonAuto()

> **utiliserBrouillonAuto**\<`T`\>(`options`): `ResultatBrouillonAuto`\<`T`\>

Defined in: [crochets/utiliser-brouillon-auto.ts:30](https://github.com/Trilian/assistant_matanne/blob/363b51de0e987de2bff6b0f6d8a68f1492dc8d71/frontend/src/crochets/utiliser-brouillon-auto.ts#L30)

Hook de sauvegarde automatique de brouillon dans localStorage.
Persiste la valeur après un délai configurable et restaure au montage.

## Type Parameters

### T

`T`

## Parameters

### options

`OptionsBrouillonAuto`\<`T`\>

Clé localStorage, valeur à sauvegarder, délai debounce

## Returns

`ResultatBrouillonAuto`\<`T`\>

Valeur initiale restaurée et fonction d'effacement
