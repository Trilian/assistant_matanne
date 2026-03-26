// ═══════════════════════════════════════════════════════════
// Album — Galerie photos famille
// ═══════════════════════════════════════════════════════════

"use client";

import { useState, useRef } from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { Camera, Upload, Trash2, Image as ImageIcon, X } from "lucide-react";
import { Button } from "@/composants/ui/button";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/composants/ui/card";
import { Skeleton } from "@/composants/ui/skeleton";
import { utiliserRequete, utiliserMutation } from "@/crochets/utiliser-api";
import { useQueryClient } from "@tanstack/react-query";
import {
  listerPhotos,
  uploaderPhoto,
  supprimerPhoto,
} from "@/bibliotheque/api/album";
import { listerJalons } from "@/bibliotheque/api/famille";
import type { PhotoAlbum } from "@/bibliotheque/api/album";
import { toast } from "sonner";

export default function PageAlbum() {
  const searchParams = useSearchParams();
  const jalonDepuisUrl = searchParams.get("jalon_id");
  const [photoSelectionnee, setPhotoSelectionnee] = useState<PhotoAlbum | null>(null);
  const [jalonLie, setJalonLie] = useState<string>(jalonDepuisUrl ?? "");
  const fileInputRef = useRef<HTMLInputElement>(null);
  const queryClient = useQueryClient();

  const { data: photos, isLoading } = utiliserRequete(
    ["famille", "album"],
    () => listerPhotos()
  );

  const { data: jalons = [] } = utiliserRequete(
    ["famille", "jules", "jalons", "album-lien"],
    () => listerJalons()
  );

  const invalider = () =>
    queryClient.invalidateQueries({ queryKey: ["famille", "album"] });

  const { mutate: uploader, isPending: enUpload } = utiliserMutation(
    (file: File) => uploaderPhoto(file),
    {
      onSuccess: () => { invalider(); toast.success("Photo uploadée"); },
      onError: () => toast.error("Erreur lors de l'upload"),
    }
  );

  const { mutate: supprimer } = utiliserMutation(
    (path: string) => supprimerPhoto(path),
    {
      onSuccess: () => {
        invalider();
        setPhotoSelectionnee(null);
        toast.success("Photo supprimée");
      },
      onError: () => toast.error("Erreur lors de la suppression"),
    }
  );

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (!files) return;
    Array.from(files).forEach((file) => {
      const nomAvecJalon = jalonLie
        ? `jalon-${jalonLie}_${file.name}`
        : file.name;
      const fichierLie = new File([file], nomAvecJalon, { type: file.type });
      uploader(fichierLie);
    });
    e.target.value = "";
  };

  const extraireJalonId = (nom: string) => {
    const match = /^jalon-(\d+)_/.exec(nom);
    return match ? match[1] : null;
  };

  const photosFiltrees = jalonLie
    ? (photos ?? []).filter((p) => extraireJalonId(p.nom) === jalonLie)
    : (photos ?? []);

  const formatTaille = (bytes: number) => {
    if (bytes < 1024) return `${bytes} o`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(0)} Ko`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} Mo`;
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">📸 Album</h1>
          <p className="text-muted-foreground">
            Galerie photos familiale — {photosFiltrees.length} photo(s)
          </p>
        </div>
        <div className="flex items-center gap-2">
          <select
            title="Lier les uploads à un jalon"
            value={jalonLie}
            onChange={(e) => setJalonLie(e.target.value)}
            className="h-9 rounded-md border border-input bg-background px-3 text-sm"
          >
            <option value="">Aucun jalon</option>
            {jalons.map((j) => (
              <option key={j.id} value={String(j.id)}>
                #{j.id} - {j.titre}
              </option>
            ))}
          </select>
          <input
            ref={fileInputRef}
            type="file"
            title="Sélectionner des photos à uploader"
            accept="image/jpeg,image/png,image/webp,image/gif"
            multiple
            className="hidden"
            onChange={handleFileChange}
          />
          <Button
            size="sm"
            onClick={() => fileInputRef.current?.click()}
            disabled={enUpload}
          >
            <Upload className="mr-2 h-4 w-4" />
            {enUpload ? "Upload…" : "Ajouter des photos"}
          </Button>
        </div>
      </div>

      {/* Galerie */}
      {isLoading ? (
        <div className="grid gap-3 grid-cols-2 sm:grid-cols-3 lg:grid-cols-4">
          {[1, 2, 3, 4, 5, 6].map((i) => (
            <Skeleton key={i} className="aspect-square rounded-lg" />
          ))}
        </div>
      ) : !photosFiltrees.length ? (
        <Card>
          <CardContent className="flex flex-col items-center gap-4 py-16">
            <Camera className="h-16 w-16 text-muted-foreground" />
            <div className="text-center">
              <p className="text-lg font-medium">Aucune photo</p>
              <p className="text-sm text-muted-foreground mt-1">
                Cliquez sur &quot;Ajouter des photos&quot; pour commencer votre
                album famille.
              </p>
            </div>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-3 grid-cols-2 sm:grid-cols-3 lg:grid-cols-4">
          {photosFiltrees.map((photo) => (
            <div
              key={photo.id}
              role="button"
              tabIndex={0}
              aria-label={`Voir la photo ${photo.nom}`}
              className="group relative aspect-square rounded-lg overflow-hidden border cursor-pointer hover:ring-2 hover:ring-primary focus-visible:ring-2 focus-visible:ring-primary transition-all outline-none"
              onClick={() => setPhotoSelectionnee(photo)}
              onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); setPhotoSelectionnee(photo); } }}
            >
              <img
                src={photo.url}
                alt={photo.nom}
                className="w-full h-full object-cover"
                loading="lazy"
              />
              <div className="absolute inset-0 bg-black/0 group-hover:bg-black/20 transition-colors" />
              {extraireJalonId(photo.nom) && (
                <div className="absolute left-2 top-2 rounded bg-black/70 px-2 py-0.5 text-[10px] text-white">
                  Jalon #{extraireJalonId(photo.nom)}
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Lightbox */}
      {photoSelectionnee && (
        <div
          role="dialog"
          aria-modal="true"
          aria-label={`Photo : ${photoSelectionnee.nom}`}
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 p-4"
          onClick={() => setPhotoSelectionnee(null)}
          onKeyDown={(e) => { if (e.key === 'Escape') setPhotoSelectionnee(null); }}
        >
          <div
            className="relative max-w-4xl w-full max-h-[90vh] flex flex-col items-center"
            onClick={(e) => e.stopPropagation()}
          >
            <img
              src={photoSelectionnee.url}
              alt={photoSelectionnee.nom}
              className="max-h-[80vh] rounded-lg object-contain"
            />
            <div className="flex items-center gap-3 mt-3">
              <span className="text-white text-sm">
                {photoSelectionnee.nom} · {formatTaille(photoSelectionnee.taille)}
              </span>
              {extraireJalonId(photoSelectionnee.nom) && (
                <Link
                  href={`/famille/jules?jalon_id=${extraireJalonId(photoSelectionnee.nom)}`}
                  className="text-xs text-white underline"
                >
                  Voir le jalon lié
                </Link>
              )}
              <Button
                variant="destructive"
                size="sm"
                onClick={() => supprimer(photoSelectionnee.path)}
              >
                <Trash2 className="mr-1 h-3 w-3" />
                Supprimer
              </Button>
            </div>
            <Button
              variant="ghost"
              size="icon"
              aria-label="Fermer la photo"
              className="absolute top-0 right-0 text-white hover:bg-white/20"
              onClick={() => setPhotoSelectionnee(null)}
            >
              <X className="h-5 w-5" />
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}
