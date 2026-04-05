[**Assistant Matanne — Frontend**](../../../README.md)

***

[Assistant Matanne — Frontend](../../../README.md) / [bibliotheque/validateurs](../README.md) / schemaAnniversaire

# Variable: schemaAnniversaire

> `const` **schemaAnniversaire**: `ZodObject`\<\{ `date_naissance`: `ZodString`; `idees_cadeaux`: `ZodOptional`\<`ZodNullable`\<`ZodString`\>\>; `nom_personne`: `ZodString`; `notes`: `ZodOptional`\<`ZodNullable`\<`ZodString`\>\>; `rappel_jours_avant`: `ZodDefault`\<`ZodArray`\<`ZodNumber`\>\>; `relation`: `ZodEnum`\<\{ `ami`: `"ami"`; `collegue`: `"collegue"`; `cousin`: `"cousin"`; `enfant`: `"enfant"`; `grand_parent`: `"grand_parent"`; `oncle_tante`: `"oncle_tante"`; `parent`: `"parent"`; \}\>; \}, `$strip`\>

Defined in: [bibliotheque/validateurs-famille.ts:4](https://github.com/Trilian/assistant_matanne/blob/363b51de0e987de2bff6b0f6d8a68f1492dc8d71/frontend/src/bibliotheque/validateurs-famille.ts#L4)

Schémas famille
