[**Assistant Matanne — Frontend**](../../../../README.md)

***

[Assistant Matanne — Frontend](../../../../README.md) / [bibliotheque/api/inventaire](../README.md) / detecterPhotoFrigoSansImport

# Function: detecterPhotoFrigoSansImport()

> **detecterPhotoFrigoSansImport**(`file`, `_emplacement?`): `Promise`\<[`ResultatOCRFrigo`](../interfaces/ResultatOCRFrigo.md)\>

Defined in: [bibliotheque/api/inventaire.ts:102](https://github.com/Trilian/assistant_matanne/blob/363b51de0e987de2bff6b0f6d8a68f1492dc8d71/frontend/src/bibliotheque/api/inventaire.ts#L102)

Détecte les aliments dans une photo de frigo via le endpoint unifié photo-frigo (mode preview pour checkboxes)

## Parameters

### file

`File`

### \_emplacement?

`string` = `"frigo"`

## Returns

`Promise`\<[`ResultatOCRFrigo`](../interfaces/ResultatOCRFrigo.md)\>
