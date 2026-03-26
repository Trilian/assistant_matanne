// ═══════════════════════════════════════════════════════════
// Client API — Export PDF
// ═══════════════════════════════════════════════════════════

import { clientApi } from "./client";

export type TypeExport = "courses" | "planning" | "recette" | "budget";

/**
 * Exporte une ressource en PDF et déclenche le téléchargement côté navigateur.
 */
export async function exporterPdf(
  typeExport: TypeExport,
  idRessource?: number
): Promise<void> {
  const params = new URLSearchParams({ type_export: typeExport });
  if (idRessource !== undefined) {
    params.set("id_ressource", String(idRessource));
  }

  const response = await clientApi.post(`/export/pdf?${params.toString()}`, null, {
    responseType: "blob",
  });

  const blob = new Blob([response.data], { type: "application/pdf" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = `${typeExport}${idRessource ? `_${idRessource}` : ""}.pdf`;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}

// ─── Export / Import données (backup) ─────────────────────

export const DOMAINES_DEFAUT = [
  "recettes",
  "courses",
  "inventaire",
  "planning",
  "notes",
] as const;

export interface DomaineExport {
  id: string;
  label: string;
}

export async function listerDomaines(): Promise<DomaineExport[]> {
  const { data } = await clientApi.get<{ domaines: DomaineExport[] }>(
    "/export/domaines"
  );
  return data.domaines;
}

/**
 * Télécharge un backup JSON des domaines sélectionnés.
 * Si motDePasse est fourni, le fichier est chiffré (.json.enc).
 */
export async function telechargerBackupJson(
  domaines: string[] = [...DOMAINES_DEFAUT],
  motDePasse?: string
): Promise<void> {
  const params = new URLSearchParams({ domaines: domaines.join(",") });
  if (motDePasse) params.set("mot_de_passe", motDePasse);

  const response = await clientApi.get(`/export/json?${params.toString()}`, {
    responseType: "blob",
  });

  const timestamp = new Date().toISOString().slice(0, 10);
  const ext = motDePasse ? ".json.enc" : ".json";
  const mime = motDePasse ? "application/octet-stream" : "application/json";
  const blob = new Blob([response.data], { type: mime });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = `matanne_backup_${timestamp}${ext}`;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}

export interface ResultatRestauration {
  success: boolean;
  message: string;
  tables_restaurees: string[];
  total_enregistrements: number;
}

/**
 * Restaure des données depuis un fichier JSON exporté (clair ou chiffré).
 */
export async function restaurerDepuisJson(
  file: File,
  options?: { domaines?: string[]; effacerExistant?: boolean; motDePasse?: string }
): Promise<ResultatRestauration> {
  const formData = new FormData();
  formData.append("file", file);

  const params = new URLSearchParams();
  if (options?.domaines?.length) {
    params.set("domaines", options.domaines.join(","));
  }
  if (options?.effacerExistant) {
    params.set("effacer_existant", "true");
  }
  if (options?.motDePasse) {
    params.set("mot_de_passe", options.motDePasse);
  }

  const { data } = await clientApi.post<ResultatRestauration>(
    `/export/restaurer?${params.toString()}`,
    formData,
    { headers: { "Content-Type": "multipart/form-data" } }
  );
  return data;
}
