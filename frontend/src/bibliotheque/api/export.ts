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
