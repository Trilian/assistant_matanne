[**Assistant Matanne — Frontend**](../../../../README.md)

***

[Assistant Matanne — Frontend](../../../../README.md) / [bibliotheque/api/documents](../README.md) / extraireDocumentOCR

# Function: extraireDocumentOCR()

> **extraireDocumentOCR**(`file`, `typeDocument?`): `Promise`\<[`ResultatOCR`](../interfaces/ResultatOCR.md)\>

Defined in: [bibliotheque/api/documents.ts:115](https://github.com/Trilian/assistant_matanne/blob/363b51de0e987de2bff6b0f6d8a68f1492dc8d71/frontend/src/bibliotheque/api/documents.ts#L115)

Envoie une image au backend pour extraction OCR.

## Parameters

### file

`File`

Fichier image (JPEG/PNG/WebP)

### typeDocument?

`string` = `"facture"`

"facture" (défaut) ou "generique"

## Returns

`Promise`\<[`ResultatOCR`](../interfaces/ResultatOCR.md)\>
