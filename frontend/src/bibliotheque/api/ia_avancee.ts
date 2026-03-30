import { clientApi } from './client'
import type {
  AdaptationPlanningMeteoResponse,
  AnalyseDocumentPhotoResponse,
  AnalysePhotoMultiResponse,
  DiagnosticPlantResponse,
  EconomiesEnergieResponse,
  EstimationTravauxResponse,
  OptimisationRoutinesResponse,
  PlanningAdaptatifResponse,
  PlanningVoyageResponse,
  PredictionPannesResponse,
  PrevisionsDepensesResponse,
  SuggestionsAchatsResponse,
  SuggestionsIdeasResponse,
  SuggestionsProactivesResponse,
} from '@/types/ia_avancee'

const API_PREFIX = '/api/v1/ia-avancee'

export interface IdeesCadeauxPayload {
  nom: string
  age: number
  relation?: string
  budget_max?: number
  occasion?: string
}

export interface PlanningAdaptatifPayload {
  meteo?: Record<string, unknown> | null
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
  previsions_meteo: Record<string, unknown>
): Promise<AdaptationPlanningMeteoResponse> {
  const { data } = await clientApi.post<AdaptationPlanningMeteoResponse>(`${API_PREFIX}/adaptations-meteo`, {
    previsions_meteo,
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
}
