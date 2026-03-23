// ═══════════════════════════════════════════════════════════
// API Auth — Authentification
// ═══════════════════════════════════════════════════════════

import { clientApi } from "./client";
import type { Utilisateur, ReponseToken } from "@/types/api";

export interface DonneesConnexion {
  email: string;
  mot_de_passe: string;
}

export interface DonneesInscription {
  email: string;
  mot_de_passe: string;
  nom: string;
}

/** Connexion → retourne JWT */
export async function connecter(donnees: DonneesConnexion): Promise<ReponseToken> {
  const { data } = await clientApi.post<ReponseToken>("/auth/login", donnees);
  localStorage.setItem("access_token", data.access_token);
  return data;
}

/** Inscription */
export async function inscrire(donnees: DonneesInscription): Promise<ReponseToken> {
  const { data } = await clientApi.post<ReponseToken>("/auth/register", donnees);
  localStorage.setItem("access_token", data.access_token);
  return data;
}

/** Récupérer le profil utilisateur courant */
export async function obtenirProfil(): Promise<Utilisateur> {
  const { data } = await clientApi.get<Utilisateur>("/auth/me");
  return data;
}

/** Déconnexion */
export function deconnecter(): void {
  localStorage.removeItem("access_token");
  window.location.href = "/connexion";
}

/** Rafraîchir le token */
export async function rafraichirToken(): Promise<ReponseToken> {
  const { data } = await clientApi.post<ReponseToken>("/auth/refresh");
  localStorage.setItem("access_token", data.access_token);
  return data;
}
