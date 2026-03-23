// ═══════════════════════════════════════════════════════════
// Client API typé — Instance axios avec intercepteurs JWT
// ═══════════════════════════════════════════════════════════

import axios, { type AxiosError, type InternalAxiosRequestConfig } from "axios";
import { URL_API, PREFIXE_API } from "@/lib/constantes";
import type { ErreurAPI } from "@/types/api";

/** Instance axios configurée pour le backend FastAPI */
export const clientApi = axios.create({
  baseURL: `${URL_API}${PREFIXE_API}`,
  timeout: 30_000,
  headers: {
    "Content-Type": "application/json",
  },
  withCredentials: true,
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

      try {
        const { data } = await axios.post(
          `${URL_API}${PREFIXE_API}/auth/refresh`,
          {},
          { withCredentials: true }
        );

        if (data.access_token) {
          localStorage.setItem("access_token", data.access_token);
          if (requeteOriginale.headers) {
            requeteOriginale.headers.Authorization = `Bearer ${data.access_token}`;
          }
          return clientApi(requeteOriginale);
        }
      } catch {
        // Refresh échoué → déconnexion
        localStorage.removeItem("access_token");
        if (typeof window !== "undefined") {
          window.location.href = "/connexion";
        }
      }
    }

    return Promise.reject(error);
  }
);
