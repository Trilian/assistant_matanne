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

/** Réponse login (avec ou sans 2FA) */
export interface ReponseLogin {
  access_token?: string;
  token_type?: string;
  expires_in?: number;
  requires_2fa?: boolean;
  temp_token?: string;
}

/** Connexion → retourne JWT ou demande 2FA */
export async function connecter(donnees: DonneesConnexion): Promise<ReponseLogin> {
  const { data } = await clientApi.post<ReponseLogin>("/auth/login", {
    email: donnees.email,
    password: donnees.mot_de_passe,
  });
  if (data.access_token) {
    localStorage.setItem("access_token", data.access_token);
  }
  return data;
}

/** Inscription */
export async function inscrire(donnees: DonneesInscription): Promise<ReponseToken> {
  const { data } = await clientApi.post<ReponseToken>("/auth/register", {
    email: donnees.email,
    password: donnees.mot_de_passe,
    nom: donnees.nom,
  });
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

// ─── 2FA ──────────────────────────────────────────────────

export interface Reponse2FAEnable {
  secret: string;
  qr_code: string;
  backup_codes: string[];
}

export interface Statut2FA {
  enabled: boolean;
  backup_codes_remaining: number;
}

/** Initier l'activation 2FA → QR code + backup codes */
export async function activer2FA(): Promise<Reponse2FAEnable> {
  const { data } = await clientApi.post<Reponse2FAEnable>("/auth/2fa/enable");
  return data;
}

/** Confirmer l'activation 2FA avec un code TOTP */
export async function verifierSetup2FA(code: string): Promise<void> {
  await clientApi.post("/auth/2fa/verify-setup", { code });
}

/** Désactiver le 2FA (nécessite un code valide) */
export async function desactiver2FA(code: string): Promise<void> {
  await clientApi.post("/auth/2fa/disable", { code });
}

/** Statut 2FA */
export async function statut2FA(): Promise<Statut2FA> {
  const { data } = await clientApi.get<Statut2FA>("/auth/2fa/status");
  return data;
}

/** Login 2FA (étape 2 après connexion) */
export async function login2FA(tempToken: string, code: string): Promise<ReponseToken> {
  const { data } = await clientApi.post<ReponseToken>("/auth/2fa/login", {
    temp_token: tempToken,
    code,
  });
  localStorage.setItem("access_token", data.access_token);
  return data;
}
