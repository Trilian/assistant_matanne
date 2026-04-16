// ═══════════════════════════════════════════════════════════
// Client API typé — Instance axios avec intercepteurs JWT
// ═══════════════════════════════════════════════════════════

import axios, { type AxiosError, type InternalAxiosRequestConfig } from "axios";
import { URL_API, PREFIXE_API } from "@/bibliotheque/constantes";
import type { ErreurAPI } from "@/types/api";

/** Instance axios configurée pour le backend FastAPI */
export const clientApi = axios.create({
  baseURL: `${URL_API}${PREFIXE_API}`,
  timeout: 30_000,
  headers: {
    "Content-Type": "application/json",
  },
});

// ─── Intercepteur requête : injection du token JWT ───
clientApi.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    // Le token est géré par cookie httpOnly côté serveur
    // Pour le fallback localStorage (dev uniquement) :
    if (typeof window !== "undefined") {
      const token = localStorage.getItem("access_token");
      if (token && config.headers) {
        config.headers.Authorization = `Bearer ${token}`;
      }
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// ─── Intercepteur réponse : gestion erreurs + refresh token ───
// Sérialiser les refreshs pour éviter les race conditions.
let isRefreshing = false;
let refreshSubscribers: ((token: string) => void)[] = [];

function onRefreshed(token: string) {
  refreshSubscribers.forEach((cb) => cb(token));
  refreshSubscribers = [];
}

function addRefreshSubscriber(cb: (token: string) => void) {
  refreshSubscribers.push(cb);
}

clientApi.interceptors.response.use(
  (response) => response,
  async (error: AxiosError<ErreurAPI>) => {
    const requeteOriginale = error.config;

    // Si 401 et pas déjà un retry → tenter refresh
    if (
      error.response?.status === 401 &&
      requeteOriginale &&
      !(requeteOriginale as ReturnType<typeof Object.assign> & { _retry?: boolean })._retry
    ) {
      (requeteOriginale as ReturnType<typeof Object.assign> & { _retry?: boolean })._retry = true;

      // Si un refresh est déjà en cours, attendre son résultat.
      if (isRefreshing) {
        return new Promise((resolve) => {
          addRefreshSubscriber((newToken: string) => {
            if (requeteOriginale.headers) {
              requeteOriginale.headers.Authorization = `Bearer ${newToken}`;
            }
            resolve(clientApi(requeteOriginale));
          });
        });
      }

      isRefreshing = true;

      try {
        const currentToken = typeof window !== "undefined" ? localStorage.getItem("access_token") : null;
        const { data } = await axios.post(
          `${URL_API}${PREFIXE_API}/auth/refresh`,
          {},
          {
            withCredentials: true,
            timeout: 10_000,
            headers: currentToken ? { Authorization: `Bearer ${currentToken}` } : undefined,
          }
        );

        if (data.access_token) {
          localStorage.setItem("access_token", data.access_token);
          if (requeteOriginale.headers) {
            requeteOriginale.headers.Authorization = `Bearer ${data.access_token}`;
          }
          onRefreshed(data.access_token);
          isRefreshing = false;
          return clientApi(requeteOriginale);
        }
      } catch {
        // Refresh échoué → déconnexion propre
        isRefreshing = false;
        refreshSubscribers = [];
        localStorage.removeItem("access_token");
        if (typeof window !== "undefined") {
          window.location.href = "/connexion";
        }
        return Promise.reject(error);
      }

      isRefreshing = false;
    }

    return Promise.reject(error);
  }
);
