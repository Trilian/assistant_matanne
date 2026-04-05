[**Assistant Matanne — Frontend**](../../../README.md)

***

[Assistant Matanne — Frontend](../../../README.md) / [bibliotheque/validateurs](../README.md) / schemaRecette

# Variable: schemaRecette

> `const` **schemaRecette**: `ZodObject`\<\{ `categorie`: `ZodOptional`\<`ZodString`\>; `description`: `ZodOptional`\<`ZodString`\>; `difficulte`: `ZodOptional`\<`ZodEnum`\<\{ `difficile`: `"difficile"`; `facile`: `"facile"`; `moyen`: `"moyen"`; \}\>\>; `ingredients`: `ZodArray`\<`ZodObject`\<\{ `nom`: `ZodString`; `quantite`: `ZodOptional`\<`ZodCoercedNumber`\<`unknown`\>\>; `unite`: `ZodOptional`\<`ZodString`\>; \}, `$strip`\>\>; `instructions`: `ZodOptional`\<`ZodString`\>; `nom`: `ZodString`; `portions`: `ZodOptional`\<`ZodCoercedNumber`\<`unknown`\>\>; `temps_cuisson`: `ZodOptional`\<`ZodCoercedNumber`\<`unknown`\>\>; `temps_preparation`: `ZodOptional`\<`ZodCoercedNumber`\<`unknown`\>\>; \}, `$strip`\>

Defined in: [bibliotheque/validateurs-cuisine.ts:4](https://github.com/Trilian/assistant_matanne/blob/363b51de0e987de2bff6b0f6d8a68f1492dc8d71/frontend/src/bibliotheque/validateurs-cuisine.ts#L4)

Schémas cuisine : recettes, courses, inventaire
