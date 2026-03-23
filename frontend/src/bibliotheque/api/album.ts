// ═══════════════════════════════════════════════════════════
// API Album — Photos famille
// ═══════════════════════════════════════════════════════════

import { clientApi } from "./client";

export interface PhotoAlbum {
  id: string;
  nom: string;
  url: string;
  path: string;
  taille: number;
  date_upload: string;
}

/** Lister les photos de l'album (optionnel: filtrer par catégorie) */
export async function listerPhotos(
  categorie?: string
): Promise<PhotoAlbum[]> {
  const params = categorie ? `?categorie=${encodeURIComponent(categorie)}` : "";
  const { data } = await clientApi.get(`/upload/photos${params}`);
  return data.items ?? data;
}

/** Uploader une photo dans le bucket photos */
export async function uploaderPhoto(file: File): Promise<PhotoAlbum> {
  const formData = new FormData();
  formData.append("file", file);
  const { data } = await clientApi.post("/upload?bucket=photos", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return {
    id: data.path,
    nom: data.filename,
    url: data.url,
    path: data.path,
    taille: data.size,
    date_upload: new Date().toISOString(),
  };
}

/** Supprimer une photo par son path */
export async function supprimerPhoto(path: string): Promise<void> {
  await clientApi.delete(`/upload/photos/${path}`);
}
