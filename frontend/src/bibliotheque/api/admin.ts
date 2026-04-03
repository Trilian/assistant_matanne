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
  status: 'succes' | 'erreur' | 'success' | 'failure' | 'dry_run'
  message: string
  ended_at?: string | null
  duration_ms?: number
  source?: string
}

export interface JobLogsResponse {
  job_id: string
  nom: string
  logs: JobLog[]
  total: number
}

export interface JobHistoryEntry {
  id: number
  job_id: string
  job_name: string
  started_at: string | null
  ended_at: string | null
  duration_ms: number
  status: string
  error_message: string | null
  output_logs: string | null
  triggered_by_user_id: string | null
  triggered_by_user_role: string | null
}

export interface JobHistoryResponse {
  items: JobHistoryEntry[]
  total: number
  page: number
  par_page: number
  pages_totales: number
}

export interface JobBatchItem {
  job_id: string
  status: string
  duration_ms: number
  message: string
}

export interface JobBatchResponse {
  mode: 'dry_run' | 'run'
  jobs_cibles?: string[]
  total: number
  succes: number
  echecs: number
  items: JobBatchItem[]
}

export interface JobCompareItem {
  job_id: string
  job_name: string
  dry_run: {
    status: string
    started_at: string | null
    duration_ms: number
    error_message: string | null
  } | null
  run: {
    status: string
    started_at: string | null
    duration_ms: number
    error_message: string | null
  } | null
  comparaison: {
    delta_duration_ms: number | null
    status_coherent: boolean | null
  }
}

export interface JobCompareResponse {
  generated_at: string
  fenetre_heures: number
  total: number
  items: JobCompareItem[]
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
  numero_destinataire?: string
  titre?: string
}

export interface NotificationTestAllPayload {
  message: string
  email?: string
  titre?: string
  inclure_whatsapp?: boolean
}

export interface NotificationTemplateInfo {
  id: string
  label: string
  trigger: string
}

export interface NotificationTemplatesResponse {
  status: string
  templates: {
    whatsapp: NotificationTemplateInfo[]
    email: NotificationTemplateInfo[]
  }
  total: number
}

export interface NotificationTestAllResponse {
  resultats: Record<string, boolean>
  canaux_testes: string[]
  succes: string[]
  echecs: string[]
  message: string
}

export interface NotificationQueueItem {
  user_id: string
  taille_queue: number
  dernier_message?: string
  dernier_evenement?: string
  last_updated?: string
}

export interface NotificationQueueResponse {
  items: NotificationQueueItem[]
  total: number
  total_users_pending: number
}

export interface ConfigAdminExport {
  exported_at: string
  feature_flags: Record<string, boolean>
  runtime_config: Record<string, unknown>
}

export interface ConfigAdminImportPayload {
  feature_flags?: Record<string, boolean>
  runtime_config?: Record<string, unknown>
  merge?: boolean
}

export interface FlowSimulationPayload {
  scenario: 'peremption_j2' | 'document_expirant' | 'echec_cron_job' | 'rappel_courses' | 'resume_hebdo'
  user_id?: string
  message?: string
  dry_run?: boolean
  payload?: Record<string, unknown>
}

export interface FlowSimulationResponse {
  scenario: string
  user_id: string
  dry_run: boolean
  actions: Array<Record<string, unknown>>
  payload: Record<string, unknown>
}

export interface EventBusItem {
  event_id: string
  type: string
  source: string
  timestamp: string | null
  data: Record<string, unknown>
}

export interface EventBusResponse {
  metriques: Record<string, unknown>
  items: EventBusItem[]
  total: number
}

export interface EventBusTriggerPayload {
  type_evenement: string
  source?: string
  payload?: Record<string, unknown>
}

export interface EventBusTriggerResponse {
  status: string
  type_evenement: string
  handlers_notifies: number
}

export interface EventBusReplayPayload {
  event_id?: string
  type_evenement?: string
  limite?: number
  source?: string
}

export interface EventBusReplayResponse {
  status: string
  replayes: Array<{
    event_id: string
    type: string
    handlers_notifies: number
  }>
  total: number
  handlers_notifies: number
}

export interface OneClickE2EAdminResponse {
  status: string
  workflow: string
  user_id: string
  mode: string
  etapes: Array<{
    etape: string
    action: string
    status: string
  }>
  total_etapes: number
}

export interface AiMetricsResponse {
  generated_at: string
  api: Record<string, unknown>
  rate_limit: Record<string, unknown>
  cache: Record<string, unknown>
  monitoring: Record<string, unknown>
  cout_estime_eur: number
  cout_eur_1k_tokens: number
}

export interface UserImpersonationPayload {
  duree_heures?: number
  raison?: string
}

export interface UserImpersonationResponse {
  status: string
  token_type: string
  access_token: string
  expires_in: number
  utilisateur: {
    id: string
    email: string
    role: string
  }
}

export interface LiveSnapshotResponse {
  generated_at: string
  api: {
    uptime_seconds: number
    requests_total: number
    top_endpoints: Array<{ endpoint: string; count: number }>
    latency: {
      avg_ms: number
      p95_ms: number
      tracked_endpoints: number
    }
    rate_limiting: Record<string, unknown>
    ai: Record<string, unknown>
  }
  cache: Record<string, unknown>
  jobs: {
    last_24h: Record<string, number>
  }
  security: {
    events_1h: number
  }
}

export interface MaintenanceModeResponse {
  maintenance_mode: boolean
}

export interface AiConsolePayload {
  prompt: string
  prompt_systeme?: string
  temperature?: number
  max_tokens?: number
  utiliser_cache?: boolean
}

export interface AiConsoleResponse {
  status: string
  duration_ms: number
  model: string
  response: string
}

export interface DbExportResponse {
  format: 'json'
  exported_at: string
  tables: Record<string, Array<Record<string, unknown>>>
  total_tables: number
}

export interface DbImportResponse {
  status: string
  imported_tables: number
  resultats: Record<string, { imported: number; merge: boolean }>
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

export interface StatutBridgePhase5Item {
  id: string
  bridge: string
  intitule: string
  verification: string
  statut: string
  latence_ms: number
  details: string
}

export interface StatutBridgesPhase5Response {
  phase: string
  generated_at: string
  execution_ms: number
  statut_global: string
  resume: {
    total_actions: number
    operationnelles: number
    indisponibles: number
    taux_operationnel_pct: number
    mode_verification: string
  }
  items: StatutBridgePhase5Item[]
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

export function urlExportAuditPDF(params?: {
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
  return `/api/v1/admin/audit-export/pdf${qs ? `?${qs}` : ''}`
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

export async function listerHistoriqueJobs(params?: {
  page?: number
  par_page?: number
  job_id?: string
  status?: string
  depuis?: string
  jusqu_a?: string
}): Promise<JobHistoryResponse> {
  const { data } = await clientApi.get('/api/v1/admin/jobs/history', { params })
  return data
}

export async function executerJobsDuMatin(options?: {
  dry_run?: boolean
  continuer_sur_erreur?: boolean
}): Promise<JobBatchResponse> {
  const { data } = await clientApi.post('/api/v1/admin/jobs/run-morning-batch', {
    dry_run: options?.dry_run ?? false,
    continuer_sur_erreur: options?.continuer_sur_erreur ?? true,
  })
  return data
}

export async function simulerJourneeJobs(options?: {
  dry_run?: boolean
  continuer_sur_erreur?: boolean
  inclure_jobs_inactifs?: boolean
}): Promise<JobBatchResponse> {
  const { data } = await clientApi.post('/api/v1/admin/jobs/simulate-day', {
    dry_run: options?.dry_run ?? true,
    continuer_sur_erreur: options?.continuer_sur_erreur ?? true,
    inclure_jobs_inactifs: options?.inclure_jobs_inactifs ?? false,
  })
  return data
}

export async function comparerDryRunVsRun(params?: {
  limite?: number
  depuis_heures?: number
}): Promise<JobCompareResponse> {
  const { data } = await clientApi.get('/api/v1/admin/jobs/compare-dry-run', { params })
  return data
}

// ─── Services & Santé ──────────────────────────────────────

export async function obtenirSanteServices(): Promise<ServiceHealthResponse> {
  const { data } = await clientApi.get('/api/v1/admin/services/health')
  return data
}

export async function obtenirStatutBridgesPhase5(params?: {
  inclure_smoke?: boolean
}): Promise<StatutBridgesPhase5Response> {
  const { data } = await clientApi.get('/api/v1/admin/bridges/status', { params })
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

export async function envoyerNotificationTestTousCanaux(
  payload: NotificationTestAllPayload,
): Promise<NotificationTestAllResponse> {
  const { data } = await clientApi.post('/api/v1/admin/notifications/test-all', payload)
  return data
}

export async function listerTemplatesNotifications(): Promise<NotificationTemplatesResponse> {
  const { data } = await clientApi.get('/api/v1/admin/notifications/templates')
  return data
}

export async function listerQueueNotifications(params?: {
  user_id?: string
  limit?: number
}): Promise<NotificationQueueResponse> {
  const { data } = await clientApi.get('/api/v1/admin/notifications/queue', { params })
  return data
}

export async function relancerQueueNotifications(userId: string): Promise<{ status: string; user_id: string }> {
  const { data } = await clientApi.post(`/api/v1/admin/notifications/queue/${userId}/retry`)
  return data
}

export async function supprimerQueueNotifications(userId: string): Promise<{ status: string; user_id: string; deleted: number }> {
  const { data } = await clientApi.delete(`/api/v1/admin/notifications/queue/${userId}`)
  return data
}

// ─── Console Commande Rapide (D1) ──────────────────────────

export interface QuickCommandResponse {
  status: string
  type: string
  message: string
  commandes?: Record<string, string>
  jobs?: string[]
  total?: number
  result?: Record<string, unknown>
  pattern?: string
  nb_invalidees?: number
  enabled?: boolean
}

export async function executerCommandeRapide(commande: string): Promise<QuickCommandResponse> {
  const { data } = await clientApi.post('/api/v1/admin/quick-command', { commande })
  return data
}

// ─── Scheduler visuel CRON (D2) ────────────────────────────

export interface JobScheduleInfo extends JobInfo {
  next_run_in_seconds?: number
  categorie?: string
}

export async function listerJobsAvecSchedule(): Promise<JobScheduleInfo[]> {
  const { data } = await clientApi.get('/api/v1/admin/jobs')
  return data
}

export async function exporterConfigAdmin(): Promise<ConfigAdminExport> {
  const { data } = await clientApi.get('/api/v1/admin/config/export')
  return data
}

export async function importerConfigAdmin(
  payload: ConfigAdminImportPayload,
): Promise<{ status: string; feature_flags: Record<string, boolean>; runtime_config: Record<string, unknown> }> {
  const { data } = await clientApi.post('/api/v1/admin/config/import', payload)
  return data
}

export async function simulerFluxAdmin(
  payload: FlowSimulationPayload,
): Promise<FlowSimulationResponse> {
  const { data } = await clientApi.post('/api/v1/admin/flow-simulator', payload)
  return data
}

export async function lireEvenementsAdmin(params?: {
  limite?: number
  type_evenement?: string
}): Promise<EventBusResponse> {
  const { data } = await clientApi.get('/api/v1/admin/events', { params })
  return data
}

export async function declencherEvenementAdmin(
  payload: EventBusTriggerPayload,
): Promise<EventBusTriggerResponse> {
  const { data } = await clientApi.post('/api/v1/admin/events/trigger', payload)
  return data
}

export async function rejouerEvenementAdmin(
  payload: EventBusReplayPayload,
): Promise<EventBusReplayResponse> {
  const { data } = await clientApi.post('/api/v1/admin/events/replay', payload)
  return data
}

export async function lancerTestE2EOneClickAdmin(): Promise<OneClickE2EAdminResponse> {
  const { data } = await clientApi.post('/api/v1/admin/tests/e2e-one-click')
  return data
}

export async function lireMetriquesIAAdmin(): Promise<AiMetricsResponse> {
  const { data } = await clientApi.get('/api/v1/admin/ia/metrics')
  return data
}

export async function obtenirLiveSnapshotAdmin(): Promise<LiveSnapshotResponse> {
  const { data } = await clientApi.get('/api/v1/admin/live-snapshot')
  return data
}

export async function testerConsoleIA(payload: AiConsolePayload): Promise<AiConsoleResponse> {
  const { data } = await clientApi.post('/api/v1/admin/ai/console', payload)
  return data
}

export async function lireModeMaintenance(): Promise<MaintenanceModeResponse> {
  const { data } = await clientApi.get('/api/v1/admin/maintenance')
  return data
}

export async function basculerModeMaintenance(enabled: boolean): Promise<MaintenanceModeResponse & { status: string }> {
  const { data } = await clientApi.put('/api/v1/admin/maintenance', { enabled })
  return data
}

export async function simulerUtilisateur(
  userId: string,
  payload?: UserImpersonationPayload,
): Promise<UserImpersonationResponse> {
  const { data } = await clientApi.post(`/api/v1/admin/users/${userId}/impersonate`, payload ?? {})
  return data
}

export async function lireModeMaintenancePublic(): Promise<MaintenanceModeResponse> {
  const { data } = await clientApi.get('/api/v1/admin/public/maintenance')
  return data
}

export async function exporterDbJson(): Promise<DbExportResponse> {
  const { data } = await clientApi.get('/api/v1/admin/db/export', { params: { format: 'json' } })
  return data
}

export async function importerDbJson(
  tables: Record<string, Array<Record<string, unknown>>>,
  merge = false,
): Promise<DbImportResponse> {
  const { data } = await clientApi.post('/api/v1/admin/db/import', { tables, merge })
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
