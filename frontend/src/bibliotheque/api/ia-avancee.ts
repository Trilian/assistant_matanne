import { clientApi } from './client'
import type { ObjetDonnees } from '@/types/commun'
import type {
  AdaptationPlanningMeteoResponse,
  AnalyseDocumentPhotoResponse,
  AnalysePhotoMultiResponse,
  AnomaliesJardinResponse,
  AutoTagsResponse,
  DiagnosticPlantResponse,
  EconomiesEnergieResponse,
  EstimationTravauxResponse,
  InsightsAnalyticsResponse,
  MemoVocalResponse,
  OptimisationRoutinesResponse,
  PiloteAutoStatus,
  ActionPiloteAutoRecente,
  PlanningAdaptatifResponse,
  PlanningVoyageResponse,
  PredictionPannesResponse,
  PrevisionsDepensesResponse,
  ScoreEcologiqueResponse,
  SuggestionsAchatsResponse,
  SuggestionsIdeasResponse,
  SuggestionsProactivesResponse,
} from '@/types/ia-avancee'

const API_PREFIX = '/api/v1/ia-avancee'

export interface IdeesCadeauxPayload {
  nom: string
  age: number
  relation?: string
  budget_max?: number
  occasion?: string
}

export interface PlanningAdaptatifPayload {
  meteo?: ObjetDonnees | null
  budget_restant?: number | null
}

export interface PlanningVoyagePayload {
  destination: string
  duree_jours?: number
  budget_total?: number | null
  avec_enfant?: boolean
}

export async function obtenirSuggestionsAchats(jours = 90): Promise<SuggestionsAchatsResponse> {
  const { data } = await clientApi.get<SuggestionsAchatsResponse>(`${API_PREFIX}/suggestions-achats`, {
    params: { jours },
  })
  return data
}

export async function genererPlanningAdaptatif(
  body: PlanningAdaptatifPayload
): Promise<PlanningAdaptatifResponse> {
  const { data } = await clientApi.post<PlanningAdaptatifResponse>(`${API_PREFIX}/planning-adaptatif`, body)
  return data
}

export async function diagnostiquerPlante(file: File): Promise<DiagnosticPlantResponse> {
  const formData = new FormData()
  formData.append('file', file)
  const { data } = await clientApi.post<DiagnosticPlantResponse>(`${API_PREFIX}/diagnostic-plante`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return data
}

export async function obtenirPrevisionDepenses(): Promise<PrevisionsDepensesResponse> {
  const { data } = await clientApi.get<PrevisionsDepensesResponse>(`${API_PREFIX}/prevision-depenses`)
  return data
}

export async function obtenirIdeesCadeaux(
  body: IdeesCadeauxPayload
): Promise<SuggestionsIdeasResponse> {
  const { data } = await clientApi.post<SuggestionsIdeasResponse>(`${API_PREFIX}/idees-cadeaux`, body)
  return data
}

export async function analyserPhotoMultiUsage(file: File): Promise<AnalysePhotoMultiResponse> {
  const formData = new FormData()
  formData.append('file', file)
  const { data } = await clientApi.post<AnalysePhotoMultiResponse>(`${API_PREFIX}/analyse-photo`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return data
}

export async function obtenirOptimisationRoutines(): Promise<OptimisationRoutinesResponse> {
  const { data } = await clientApi.get<OptimisationRoutinesResponse>(`${API_PREFIX}/optimisation-routines`)
  return data
}

export async function analyserDocument(file: File): Promise<AnalyseDocumentPhotoResponse> {
  const formData = new FormData()
  formData.append('file', file)
  const { data } = await clientApi.post<AnalyseDocumentPhotoResponse>(`${API_PREFIX}/analyse-document`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return data
}

export async function estimerTravaux(
  file: File,
  description = ''
): Promise<EstimationTravauxResponse> {
  const formData = new FormData()
  formData.append('file', file)
  const { data } = await clientApi.post<EstimationTravauxResponse>(
    `${API_PREFIX}/estimation-travaux`,
    formData,
    {
      params: { description },
      headers: { 'Content-Type': 'multipart/form-data' },
    }
  )
  return data
}

export async function genererPlanningVoyage(
  body: PlanningVoyagePayload
): Promise<PlanningVoyageResponse> {
  const { data } = await clientApi.post<PlanningVoyageResponse>(`${API_PREFIX}/planning-voyage`, body)
  return data
}

export async function obtenirRecommandationsEnergie(): Promise<EconomiesEnergieResponse> {
  const { data } = await clientApi.get<EconomiesEnergieResponse>(`${API_PREFIX}/recommandations-energie`)
  return data
}

export async function obtenirPredictionPannes(): Promise<PredictionPannesResponse> {
  const { data } = await clientApi.get<PredictionPannesResponse>(`${API_PREFIX}/prediction-pannes`)
  return data
}

export async function obtenirSuggestionsProactives(): Promise<SuggestionsProactivesResponse> {
  const { data } = await clientApi.get<SuggestionsProactivesResponse>(`${API_PREFIX}/suggestions-proactives`)
  return data
}

export async function obtenirAdaptationsMeteo(
  previsions_meteo: ObjetDonnees
): Promise<AdaptationPlanningMeteoResponse> {
  const { data } = await clientApi.post<AdaptationPlanningMeteoResponse>(`${API_PREFIX}/adaptations-meteo`, {
    previsions_meteo,
  })
  return data
}

// ═══════════════════════════════════════════════════════════
// P6 — IA Avancée & Intelligence Proactive
// ═══════════════════════════════════════════════════════════

export async function obtenirInsightsAnalytics(periode_mois = 3): Promise<InsightsAnalyticsResponse> {
  const { data } = await clientApi.get<InsightsAnalyticsResponse>('/api/v1/dashboard/insights-analytics', {
    params: { periode_mois },
  })
  return data
}

export async function obtenirPiloteAutoStatus(): Promise<PiloteAutoStatus> {
  const { data } = await clientApi.get<PiloteAutoStatus>(`${API_PREFIX}/pilote-auto/status`)
  return data
}

export async function togglePiloteAuto(actif: boolean): Promise<PiloteAutoStatus> {
  const { data } = await clientApi.post<PiloteAutoStatus>(`${API_PREFIX}/pilote-auto/toggle`, { actif })
  return data
}

export async function obtenirActionsPiloteAuto(): Promise<ActionPiloteAutoRecente[]> {
  const { data } = await clientApi.get<ActionPiloteAutoRecente[]>(`${API_PREFIX}/pilote-auto/actions-recentes`)
  return data
}

export async function autoEtiqueterNote(noteId: number): Promise<AutoTagsResponse> {
  const { data } = await clientApi.post<AutoTagsResponse>(`/api/v1/outils/notes/${noteId}/auto-tags`)
  return data
}

export async function classifierMemoVocal(texte: string): Promise<MemoVocalResponse> {
  const { data } = await clientApi.post<MemoVocalResponse>('/api/v1/outils/memos/vocal', { texte })
  return data
}

export async function obtenirAnomaliesJardin(): Promise<AnomaliesJardinResponse> {
  const { data } = await clientApi.get<AnomaliesJardinResponse>('/api/v1/ia/modules/jardin/anomalies')
  return data
}

export async function obtenirScoreEcologiqueRecette(recetteId: number): Promise<ScoreEcologiqueResponse> {
  const { data } = await clientApi.post<ScoreEcologiqueResponse>('/api/v1/ia/modules/recette/score-ecologique', {
    recette_id: recetteId,
  })
  return data
}

export type {
  SuggestionsAchatsResponse,
  PlanningAdaptatifResponse,
  DiagnosticPlantResponse,
  PrevisionsDepensesResponse,
  SuggestionsIdeasResponse,
  AnalysePhotoMultiResponse,
  OptimisationRoutinesResponse,
  AnalyseDocumentPhotoResponse,
  EstimationTravauxResponse,
  PlanningVoyageResponse,
  EconomiesEnergieResponse,
  PredictionPannesResponse,
  SuggestionsProactivesResponse,
  AdaptationPlanningMeteoResponse,
  InsightsAnalyticsResponse,
  PiloteAutoStatus,
  ActionPiloteAutoRecente,
  AutoTagsResponse,
  MemoVocalResponse,
  AnomaliesJardinResponse,
  ScoreEcologiqueResponse,
}
