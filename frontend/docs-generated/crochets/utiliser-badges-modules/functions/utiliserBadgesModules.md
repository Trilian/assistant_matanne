[**Assistant Matanne — Frontend**](../../../README.md)

***

[Assistant Matanne — Frontend](../../../README.md) / [crochets/utiliser-badges-modules](../README.md) / utiliserBadgesModules

# Function: utiliserBadgesModules()

> **utiliserBadgesModules**(): `object`

Defined in: [crochets/utiliser-badges-modules.ts:17](https://github.com/Trilian/assistant_matanne/blob/363b51de0e987de2bff6b0f6d8a68f1492dc8d71/frontend/src/crochets/utiliser-badges-modules.ts#L17)

Hook de compteurs badge par module (cuisine, famille, maison, jeux).
Interroge les alertes/rappels de chaque domaine et retourne les compteurs à afficher dans la sidebar.

## Returns

`object`

Objet avec compteurs par module et total global

### badgePlus

> **badgePlus**: `number` = `badges.jeux`

### badges

> **badges**: `object`

#### badges.cuisine

> **cuisine**: `number`

#### badges.famille

> **famille**: `number`

#### badges.jeux

> **jeux**: `number`

#### badges.maison

> **maison**: `number`
