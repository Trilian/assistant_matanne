// ═══════════════════════════════════════════════════════════
// Client API — Administration
// Endpoints : /api/v1/admin/*
// Rôle requis : admin
// ═══════════════════════════════════════════════════════════

import { apiClient } from './client'

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

// ─── Audit Logs ────────────────────────────────────────────

export async function listerAuditLogs(params?: {
  page?: number
  par_page?: number
  action?: string
  entite_type?: string
  depuis?: string
  jusqu_a?: string
}): Promise<AuditLogsResponse> {
  const { data } = await apiClient.get('/api/v1/admin/audit-logs', { params })
  return data
}

export async function obtenirStatsAudit(): Promise<AuditStatsResponse> {
  const { data } = await apiClient.get('/api/v1/admin/audit-stats')
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
  const { data } = await apiClient.get('/api/v1/admin/security-logs', { params })
  return data
}

// ─── Jobs Cron ─────────────────────────────────────────────

export async function listerJobs(): Promise<JobInfo[]> {
  const { data } = await apiClient.get('/api/v1/admin/jobs')
  return data
}

export async function declencherJob(jobId: string): Promise<{ status: string; job_id: string; message: string }> {
  const { data } = await apiClient.post(`/api/v1/admin/jobs/${jobId}/run`)
  return data
}

export async function obtenirLogsJob(jobId: string): Promise<JobLogsResponse> {
  const { data } = await apiClient.get(`/api/v1/admin/jobs/${jobId}/logs`)
  return data
}

// ─── Services & Santé ──────────────────────────────────────

export async function obtenirSanteServices(): Promise<ServiceHealthResponse> {
  const { data } = await apiClient.get('/api/v1/admin/services/health')
  return data
}

// ─── Cache ─────────────────────────────────────────────────

export async function obtenirStatsCache(): Promise<CacheStatsResponse> {
  const { data } = await apiClient.get('/api/v1/admin/cache/stats')
  return data
}

export async function purgerCache(pattern = '*'): Promise<{ status: string; nb_invalidees: number; message: string }> {
  const { data } = await apiClient.post('/api/v1/admin/cache/purge', { pattern })
  return data
}

export async function viderCache(): Promise<{ status: string; message: string }> {
  const { data } = await apiClient.post('/api/v1/admin/cache/clear')
  return data
}

// ─── Utilisateurs ──────────────────────────────────────────

export async function listerUtilisateurs(params?: {
  page?: number
  par_page?: number
}): Promise<UtilisateurAdmin[]> {
  const { data } = await apiClient.get('/api/v1/admin/users', { params })
  return data
}

export async function desactiverUtilisateur(
  userId: string,
  raison?: string,
): Promise<{ status: string; user_id: string; message: string }> {
  const { data } = await apiClient.post(`/api/v1/admin/users/${userId}/disable`, { raison })
  return data
}

// ─── Notifications ─────────────────────────────────────────

export async function envoyerNotificationTest(
  payload: NotificationTestPayload,
): Promise<{ resultats: Record<string, unknown>; message: string }> {
  const { data } = await apiClient.post('/api/v1/admin/notifications/test', payload)
  return data
}

// ─── Base de données ───────────────────────────────────────

export async function verifierCoherenceDb(): Promise<DbCoherenceResponse> {
  const { data } = await apiClient.get('/api/v1/admin/db/coherence')
  return data
}
