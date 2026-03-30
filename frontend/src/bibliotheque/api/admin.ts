// ═══════════════════════════════════════════════════════════
// Client API — Administration
// Endpoints : /api/v1/admin/*
// Rôle requis : admin
// ═══════════════════════════════════════════════════════════

import { clientApi } from './client'

// ─── Types ─────────────────────────────────────────────────

export interface JobInfo {
  id: string
  nom: string
  schedule: string
  prochain_run: string | null
  dernier_run: string | null
  statut: 'actif' | 'inactif'
}

export interface JobLog {
  timestamp: string
  status: 'succes' | 'erreur'
  message: string
}

export interface JobLogsResponse {
  job_id: string
  nom: string
  logs: JobLog[]
  total: number
}

export interface AuditLogEntry {
  id: number | string
  timestamp: string
  action: string
  source: string
  utilisateur_id: string | null
  entite_type: string
  entite_id: number | string | null
  details: Record<string, unknown>
}

export interface AuditLogsResponse {
  items: AuditLogEntry[]
  total: number
  page: number
  par_page: number
  pages_totales: number
}

export interface AuditStatsResponse {
  [key: string]: unknown
}

export interface SecurityLogEntry {
  id: number
  created_at: string | null
  event_type: string
  user_id: string | null
  ip: string | null
  user_agent: string | null
  source: string
  details: Record<string, unknown>
}

export interface SecurityLogsResponse {
  items: SecurityLogEntry[]
  total: number
  page: number
  par_page: number
  pages_totales: number
}

export interface ServiceHealthResponse {
  global_status: string
  total_services: number
  instantiated: number
  healthy: number
  erreurs: string[]
  services: Record<string, unknown>
  metriques?: Record<string, unknown>
}

export interface AdminDashboardResponse {
  generated_at: string
  jobs: {
    total: number
    actifs: number
    inactifs: number
  }
  services: ServiceHealthResponse
  metriques_services: Record<string, unknown>
  cache: Record<string, unknown>
  security: {
    events_24h: number
  }
  feature_flags: Record<string, boolean>
}

export interface ServiceActionInfo {
  id: string
  service: string
  description: string
  dry_run: boolean
}

export interface ServiceActionsResponse {
  items: ServiceActionInfo[]
  total: number
  enabled: boolean
}

export interface FeatureFlagsResponse {
  flags: Record<string, boolean>
  total: number
}

export interface RuntimeConfigResponse {
  values: Record<string, unknown>
  readonly: Record<string, unknown>
}

export interface ResyncTarget {
  id: string
  job_id: string
  description: string
}

export interface ResyncTargetsResponse {
  items: ResyncTarget[]
  total: number
  enabled: boolean
}

export interface CacheStatsResponse {
  [key: string]: unknown
}

export interface UtilisateurAdmin {
  id: string
  email: string
  nom: string | null
  role: string
  actif: boolean
  cree_le: string | null
}

export interface NotificationTestPayload {
  canal: 'ntfy' | 'push' | 'email' | 'whatsapp'
  message: string
  email?: string
  titre?: string
}

export interface DbCoherenceResponse {
  [key: string]: unknown
}

export interface VueSqlExposee {
  nom: string
  endpoint: string
}

export interface VuesSqlResponse {
  items: VueSqlExposee[]
  total: number
}

export interface VueSqlDataResponse {
  view: string
  items: Record<string, unknown>[]
  total: number
  page: number
  page_size: number
  pages_totales: number
}

// ─── Audit Logs ────────────────────────────────────────────

export async function listerAuditLogs(params?: {
  page?: number
  par_page?: number
  action?: string
  entite_type?: string
  depuis?: string
  jusqu_a?: string
}): Promise<AuditLogsResponse> {
  const { data } = await clientApi.get('/api/v1/admin/audit-logs', { params })
  return data
}

export async function obtenirStatsAudit(): Promise<AuditStatsResponse> {
  const { data } = await clientApi.get('/api/v1/admin/audit-stats')
  return data
}

export function urlExportAuditCSV(params?: {
  action?: string
  entite_type?: string
  depuis?: string
  jusqu_a?: string
}): string {
  const query = new URLSearchParams()
  if (params?.action) query.set('action', params.action)
  if (params?.entite_type) query.set('entite_type', params.entite_type)
  if (params?.depuis) query.set('depuis', params.depuis)
  if (params?.jusqu_a) query.set('jusqu_a', params.jusqu_a)
  const qs = query.toString()
  return `/api/v1/admin/audit-export${qs ? `?${qs}` : ''}`
}

// ─── Security Logs ─────────────────────────────────────────

export async function listerLogsSecurite(params?: {
  page?: number
  par_page?: number
  event_type?: string
  depuis?: string
  jusqu_a?: string
}): Promise<SecurityLogsResponse> {
  const { data } = await clientApi.get('/api/v1/admin/security-logs', { params })
  return data
}

// ─── Jobs Cron ─────────────────────────────────────────────

export async function listerJobs(): Promise<JobInfo[]> {
  const { data } = await clientApi.get('/api/v1/admin/jobs')
  return data
}

export async function declencherJob(jobId: string): Promise<{ status: string; job_id: string; message: string }> {
  const { data } = await clientApi.post(`/api/v1/admin/jobs/${jobId}/run`)
  return data
}

export async function obtenirLogsJob(jobId: string): Promise<JobLogsResponse> {
  const { data } = await clientApi.get(`/api/v1/admin/jobs/${jobId}/logs`)
  return data
}

// ─── Services & Santé ──────────────────────────────────────

export async function obtenirSanteServices(): Promise<ServiceHealthResponse> {
  const { data } = await clientApi.get('/api/v1/admin/services/health')
  return data
}

export async function obtenirDashboardAdmin(): Promise<AdminDashboardResponse> {
  const { data } = await clientApi.get('/api/v1/admin/dashboard')
  return data
}

export async function listerActionsServices(): Promise<ServiceActionsResponse> {
  const { data } = await clientApi.get('/api/v1/admin/services/actions')
  return data
}

export async function executerActionService(
  actionId: string,
  options?: { dry_run?: boolean; params?: Record<string, unknown> },
): Promise<{ status: string; action_id: string; dry_run?: boolean; result: unknown }> {
  const { data } = await clientApi.post(
    `/api/v1/admin/services/actions/${actionId}/run`,
    { params: options?.params ?? {} },
    { params: { dry_run: options?.dry_run ?? false } },
  )
  return data
}

// ─── Cache ─────────────────────────────────────────────────

export async function obtenirStatsCache(): Promise<CacheStatsResponse> {
  const { data } = await clientApi.get('/api/v1/admin/cache/stats')
  return data
}

export async function purgerCache(pattern = '*'): Promise<{ status: string; nb_invalidees: number; message: string }> {
  const { data } = await clientApi.post('/api/v1/admin/cache/purge', { pattern })
  return data
}

export async function viderCache(): Promise<{ status: string; message: string }> {
  const { data } = await clientApi.post('/api/v1/admin/cache/clear')
  return data
}

export async function lireFeatureFlags(): Promise<FeatureFlagsResponse> {
  const { data } = await clientApi.get('/api/v1/admin/feature-flags')
  return data
}

export async function sauvegarderFeatureFlags(
  flags: Record<string, boolean>,
): Promise<{ status: string; flags: Record<string, boolean>; total: number }> {
  const { data } = await clientApi.put('/api/v1/admin/feature-flags', { flags })
  return data
}

export async function lireRuntimeConfig(): Promise<RuntimeConfigResponse> {
  const { data } = await clientApi.get('/api/v1/admin/runtime-config')
  return data
}

export async function sauvegarderRuntimeConfig(
  values: Record<string, unknown>,
): Promise<{ status: string; values: Record<string, unknown> }> {
  const { data } = await clientApi.put('/api/v1/admin/runtime-config', { values })
  return data
}

export async function listerResyncTargets(): Promise<ResyncTargetsResponse> {
  const { data } = await clientApi.get('/api/v1/admin/resync/targets')
  return data
}

export async function forcerResync(
  targetId: string,
  dryRun = false,
): Promise<Record<string, unknown>> {
  const { data } = await clientApi.post(
    `/api/v1/admin/resync/${targetId}`,
    null,
    { params: { dry_run: dryRun } },
  )
  return data
}

export async function lancerSeedDev(
  scope: 'recettes_standard' = 'recettes_standard',
  dryRun = false,
): Promise<Record<string, unknown>> {
  const { data } = await clientApi.post(
    '/api/v1/admin/seed/dev',
    { scope },
    { params: { dry_run: dryRun } },
  )
  return data
}

// ─── Utilisateurs ──────────────────────────────────────────

export async function listerUtilisateurs(params?: {
  page?: number
  par_page?: number
}): Promise<UtilisateurAdmin[]> {
  const { data } = await clientApi.get('/api/v1/admin/users', { params })
  return data
}

export async function desactiverUtilisateur(
  userId: string,
  raison?: string,
): Promise<{ status: string; user_id: string; message: string }> {
  const { data } = await clientApi.post(`/api/v1/admin/users/${userId}/disable`, { raison })
  return data
}

// ─── Notifications ─────────────────────────────────────────

export async function envoyerNotificationTest(
  payload: NotificationTestPayload,
): Promise<{ resultats: Record<string, unknown>; message: string }> {
  const { data } = await clientApi.post('/api/v1/admin/notifications/test', payload)
  return data
}

// ─── Base de données ───────────────────────────────────────

export async function verifierCoherenceDb(): Promise<DbCoherenceResponse> {
  const { data } = await clientApi.get('/api/v1/admin/db/coherence')
  return data
}

export async function listerVuesSql(): Promise<VuesSqlResponse> {
  const { data } = await clientApi.get('/api/v1/admin/sql-views')
  return data
}

export async function lireVueSql(
  viewName: string,
  params?: { page?: number; page_size?: number },
): Promise<VueSqlDataResponse> {
  const { data } = await clientApi.get(`/api/v1/admin/sql-views/${viewName}`, { params })
  return data
}
