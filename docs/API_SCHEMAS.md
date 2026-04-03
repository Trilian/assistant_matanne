# API Schemas

Documentation auto-generee depuis `src/api/schemas/*.py`.

- Genere le: 2026-04-01 06:48:57 UTC
- Nombre total de classes BaseModel: 282
- Nombre de modules schemas: 25

## anti_gaspillage

| Classe | Champs annotes |
| --- | ---: |
| ArticlePerissable | 6 |
| RecetteRescue | 5 |
| ReponseAntiGaspillage | 3 |
| ScoreAntiGaspillage | 4 |

## auth

| Classe | Champs annotes |
| --- | ---: |
| LoginRequest | 2 |
| LoginResponse | 5 |
| RegisterRequest | 3 |
| TwoFactorEnableResponse | 3 |
| TwoFactorLoginRequest | 2 |
| TwoFactorStatusResponse | 2 |
| TwoFactorVerifyRequest | 1 |
| UserInfoResponse | 3 |

## base

| Classe | Champs annotes |
| --- | ---: |
| TimestampedResponse | 2 |

## batch_cooking

| Classe | Champs annotes |
| --- | ---: |
| ConfigBatchResponse | 6 |
| EtapeBatchResponse | 8 |
| GenererSessionDepuisPlanningRequest | 4 |
| GenererSessionDepuisPlanningResponse | 6 |
| PreparationBatchResponse | 11 |
| SessionBatchBase | 6 |
| SessionBatchPatch | 5 |
| SessionBatchResponse | 15 |

## calendriers

| Classe | Champs annotes |
| --- | ---: |
| CalendrierResponse | 8 |
| EvenementJourResponse | 6 |
| EvenementResponse | 11 |
| EvenementsAujourdhuiResponse | 2 |
| EvenementsSemaineResponse | 4 |

## common

| Classe | Champs annotes |
| --- | ---: |
| ErrorResponse | 1 |
| MessageResponse | 3 |
| ReponsePaginee | 5 |

## courses

| Classe | Champs annotes |
| --- | ---: |
| ArticleGenereResume | 5 |
| ArticleResponse | 5 |
| CheckoutArticleRequest | 2 |
| CheckoutArticleResult | 6 |
| CheckoutCoursesRequest | 3 |
| CheckoutCoursesResponse | 5 |
| CourseItemBase | 5 |
| CourseListCreate | 1 |
| GenererCoursesRequest | 5 |
| GenererCoursesResponse | 7 |
| ListeCoursesResponse | 5 |
| ListeCoursesResume | 4 |
| ScanBarcodeCheckoutRequest | 3 |
| ScanBarcodeCheckoutResponse | 7 |

## dashboard

| Classe | Champs annotes |
| --- | ---: |
| DonneesTableauBord | 4 |
| ResumeBudget | 2 |
| StatistiquesRapides | 6 |

## documents

| Classe | Champs annotes |
| --- | ---: |
| DocumentBase | 10 |
| DocumentPatch | 6 |
| DocumentResponse | 13 |

## export

| Classe | Champs annotes |
| --- | ---: |
| ExportPDFRequest | 2 |
| ExportPDFResponse | 2 |

## famille

| Classe | Champs annotes |
| --- | ---: |
| AchatCreate | 13 |
| AchatPatch | 12 |
| AchatResponse | 18 |
| AchatUrgent | 6 |
| ActiviteContexte | 5 |
| AnniversaireBase | 6 |
| AnniversaireContexte | 6 |
| AnniversairePatch | 7 |
| AnniversaireResponse | 12 |
| AnnonceIBCRequest | 4 |
| AnnonceIBCResponse | 1 |
| AnnonceVintedRequest | 7 |
| AnnonceVintedResponse | 1 |
| ChecklistAnniversaireItemCreate | 8 |
| ChecklistAnniversaireItemPatch | 9 |
| ChecklistAnniversaireSyncRequest | 1 |
| ConfigGardeRequest | 3 |
| ConfigGardeResponse | 4 |
| ContexteFamilialResponse | 8 |
| CroissanceResponse | 2 |
| DocumentExpirant | 3 |
| EvenementFamilialBase | 7 |
| EvenementFamilialPatch | 8 |
| EvenementFamilialResponse | 10 |
| JourSansCrecheResponse | 3 |
| JourSpecialResponse | 4 |
| JulesContexte | 3 |
| MarquerAchetePayload | 1 |
| MeteoActuelle | 7 |
| PercentilesOMS | 5 |
| PreferencesFamilleRequest | 7 |
| PrefillReventeResponse | 8 |
| RappelFamilleResponse | 6 |
| ResumeBudgetMoisResponse | 5 |
| ResumeSemaineRequest | 3 |
| RetrospectiveRequest | 4 |
| RoutineContexte | 3 |
| SemainesFermetureCreche | 3 |
| SuggestionAchatResponse | 5 |
| SuggestionsAchatsEnrichiesRequest | 6 |
| SuggestionsActivitesSimpleRequest | 3 |
| SuggestionsSejourRequest | 4 |
| SuggestionsSoireeRequest | 4 |
| SuggestionsWeekendRequest | 3 |

## habitat

| Classe | Champs annotes |
| --- | ---: |
| AnnonceHabitatCreate | 19 |
| CritereImmoCreate | 14 |
| CritereScenarioCreate | 4 |
| GenerationImageHabitatCreate | 2 |
| PieceHabitatCreate | 12 |
| PlanHabitatAnalyseCreate | 2 |
| PlanHabitatCreate | 9 |
| ProjetDecoDepenseCreate | 4 |
| ProjetDecoHabitatCreate | 7 |
| ProjetDecoSuggestionCreate | 2 |
| ScenarioHabitatCreate | 9 |
| ScenarioHabitatPatch | 9 |
| SynchronisationVeilleHabitatCreate | 4 |
| ZoneJardinHabitatCreate | 14 |
| ZoneJardinHabitatPatch | 13 |

## ia_avancee

| Classe | Champs annotes |
| --- | ---: |
| AdaptationsMeteoRequest | 1 |
| EstimationTravauxRequest | 1 |
| IdeesCadeauxRequest | 5 |
| PlanningAdaptatifRequest | 2 |
| PlanningVoyageRequest | 4 |

## innovations

| Classe | Champs annotes |
| --- | ---: |
| BilanAnnuelRequest | 1 |
| ComparateurEnergieRequest | 2 |
| IdeesCadeauxRequest | 0 |
| LienInviteRequest | 3 |
| MangeCeSoirRequest | 2 |
| ParcoursOptimiseRequest | 1 |
| VeilleEmploiRequest | 6 |

## inventaire

| Classe | Champs annotes |
| --- | ---: |
| ArticleBatchTrouve | 2 |
| ArticleConsolideResponse | 8 |
| InventaireItemBase | 2 |
| InventaireItemCreate | 7 |
| InventaireItemResponse | 15 |
| InventaireItemUpdate | 7 |
| ScanBatchRequest | 1 |
| ScanBatchResponse | 2 |

## jeux

| Classe | Champs annotes |
| --- | ---: |
| AlerteJeuxResponse | 10 |
| AnalyseIARequest | 2 |
| AnalyseIAResponse | 6 |
| BacktestResponse | 7 |
| BudgetResponsableResponse | 6 |
| CotesMatch | 3 |
| DashboardJeuxResponse | 7 |
| EquipeResponse | 12 |
| GenererGrilleRequest | 2 |
| GrilleEuromillionsResponse | 9 |
| GrilleGenereeResponse | 4 |
| GrilleLotoResponse | 6 |
| KPIsJeuxResponse | 4 |
| MatchDetailResponse | 14 |
| MatchEquipeRef | 2 |
| MatchResponse | 14 |
| NotificationJeuxResponse | 8 |
| NumeroRetardResponse | 6 |
| PariCreate | 7 |
| PariPatch | 3 |
| PariResponse | 10 |
| PariResume | 7 |
| PerformanceMoisResponse | 4 |
| PerformanceResponse | 11 |
| PredictionMatch | 6 |
| PredictionMatchResponse | 9 |
| ResumeMensuelResponse | 6 |
| SerieJeuxResponse | 8 |
| StatistiquesParis | 6 |
| StatsEuromillionsResponse | 8 |
| StatsLotoResponse | 5 |
| TirageEuromillionsResponse | 6 |
| TirageLotoResponse | 7 |
| ValueBetResponse | 10 |

## maison

| Classe | Champs annotes |
| --- | ---: |
| ActionEcoCreate | 6 |
| ActionEcoPatch | 7 |
| AlerteContratResponse | 5 |
| AlerteMaisonResponse | 7 |
| AlertePeremptionResponse | 5 |
| ArticleCellierCreate | 10 |
| ArticleCellierPatch | 10 |
| ArtisanCreate | 7 |
| ArtisanPatch | 7 |
| BriefingMaisonResponse | 14 |
| BudgetMeublesResponse | 4 |
| ContratCreate | 11 |
| ContratPatch | 11 |
| DepenseMaisonCreate | 7 |
| DepenseMaisonPatch | 7 |
| DevisCreate | 10 |
| DevisPatch | 8 |
| DiagnosticCreate | 7 |
| DiagnosticPatch | 7 |
| ElementJardinCreate | 7 |
| ElementJardinPatch | 7 |
| EntretienSaisonnierCreate | 4 |
| EntretienSaisonnierPatch | 6 |
| EstimationCreate | 6 |
| EstimationPatch | 6 |
| FicheTacheResponse | 9 |
| InterventionCreate | 6 |
| InterventionPatch | 5 |
| LigneDevisCreate | 3 |
| LigneDevisResponse | 6 |
| MeteoResumeResponse | 6 |
| MeubleCreate | 8 |
| MeublePatch | 8 |
| ObjetCreate | 9 |
| ObjetPatch | 8 |
| PieceCreate | 8 |
| PiecePatch | 8 |
| PlanningSemaineResponse | 3 |
| PreferencesMenageRequest | 4 |
| ProjetCreate | 6 |
| ProjetPatch | 7 |
| ReleveCompteurCreate | 4 |
| ReleveCompteurPatch | 4 |
| ResumeFinancierContratsResponse | 3 |
| StatsArtisansResponse | 4 |
| StatsCellierResponse | 5 |
| StatsDepensesResponse | 5 |
| StatsHubMaisonResponse | 8 |
| StockCreate | 7 |
| StockPatch | 7 |
| TacheEntretienCreate | 8 |
| TacheEntretienPatch | 9 |
| TacheJourResponse | 7 |
| TraitementNuisibleCreate | 7 |
| TraitementNuisiblePatch | 7 |

## planning

| Classe | Champs annotes |
| --- | ---: |
| GenererPlanningRequest | 3 |
| PlanningSemaineResponse | 3 |
| RepasBase | 4 |
| RepasRapideSuggestion | 5 |

## preferences

| Classe | Champs annotes |
| --- | ---: |
| CanauxParCategorie | 3 |
| PreferencesBase | 12 |
| PreferencesNotificationsBase | 14 |
| PreferencesNotificationsUpdate | 14 |
| PreferencesPatch | 12 |

## push

| Classe | Champs annotes |
| --- | ---: |
| PushStatusResponse | 3 |
| PushSubscriptionKeys | 2 |
| PushSubscriptionRequest | 2 |
| PushSubscriptionResponse | 4 |
| PushUnsubscribeRequest | 1 |

## recettes

| Classe | Champs annotes |
| --- | ---: |
| EtapeResponse | 5 |
| IngredientItem | 3 |
| IngredientResponse | 5 |
| RecetteBase | 7 |
| RecettePatch | 10 |
| VersionRecetteResponse | 9 |

## suggestions

| Classe | Champs annotes |
| --- | ---: |
| IngredientDetecteResponse | 3 |
| PhotoFrigoResponse | 2 |
| RecetteSuggestionResponse | 5 |
| SuggestionRecetteItem | 3 |
| SuggestionsPlanningResponse | 3 |
| SuggestionsRecettesResponse | 3 |

## utilitaires

| Classe | Champs annotes |
| --- | ---: |
| ContactBase | 8 |
| ContactPatch | 8 |
| ContactResponse | 9 |
| EnergieBase | 8 |
| EnergiePatch | 4 |
| EnergieResponse | 9 |
| JournalBase | 6 |
| JournalPatch | 5 |
| JournalResponse | 8 |
| LienBase | 6 |
| LienPatch | 6 |
| LienResponse | 7 |
| MinuteurCreate | 3 |
| MinuteurPatch | 3 |
| MinuteurResponse | 8 |
| MotDePasseBase | 5 |
| MotDePassePatch | 5 |
| MotDePasseResponse | 6 |
| NoteBase | 8 |
| NotePatch | 7 |
| NoteResponse | 11 |

## webhooks

| Classe | Champs annotes |
| --- | ---: |
| WebhookCreate | 3 |
| WebhookListResponse | 2 |
| WebhookResponse | 10 |
| WebhookTestResponse | 4 |
| WebhookUpdate | 4 |

## Regeneration

```bash
python scripts/analysis/generate_api_schemas_doc.py
```
