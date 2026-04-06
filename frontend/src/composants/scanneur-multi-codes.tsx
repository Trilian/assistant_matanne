// ═══════════════════════════════════════════════════════════
// Scanneur Multi-Codes — Scan simultané de plusieurs codes-barres
// ═══════════════════════════════════════════════════════════

"use client";

import { useEffect, useRef, useState, useCallback } from "react";
import { BrowserMultiFormatReader } from "@zxing/browser";
import { ScanLine, X, Check, Camera, CameraOff, Minus, Plus } from "lucide-react";
import { Button } from "@/composants/ui/button";
import { Badge } from "@/composants/ui/badge";
import { Input } from "@/composants/ui/input";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/composants/ui/dialog";
import { scannerCodesBatch, type ArticleBarcode } from "@/bibliotheque/api/inventaire";
import { toast } from "sonner";

export interface CodeScanné {
  code: string;
  article?: ArticleBarcode["article"];
  inconnu?: boolean;
}

interface ScanneurMultiCodesProps {
  ouvert: boolean;
  onFermer: () => void;
  /** Callback avec les articles résolus et les codes inconnus, avec quantités */
  onImporter: (trouves: ArticleBarcode[], inconnus: string[], quantites: Record<string, number>) => void;
  /** Label personnalisé pour le bouton "Importer" */
  labelImporter?: string;
}

/**
 * Modal de scan multi-codes-barres.
 *
 * - Flux caméra live via @zxing/browser (EAN-8, EAN-13, QR, UPC-A, UPC-E…)
 * - Filtre les doublons automatiquement
 * - Résout tous les codes en un seul appel batch vers l'API
 * - Callback onImporter avec articles trouvés + codes inconnus
 */
export function ScanneurMultiCodes({
  ouvert,
  onFermer,
  onImporter,
  labelImporter = "Importer",
}: ScanneurMultiCodesProps) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const readerRef = useRef<BrowserMultiFormatReader | null>(null);
  const vusRef = useRef<Set<string>>(new Set());

  const [codesScannés, setCodesScannés] = useState<string[]>([]);
  const [quantitésCodes, setQuantitésCodes] = useState<Record<string, number>>({});
  const [cameraActive, setCameraActive] = useState(false);
  const [erreurCamera, setErreurCamera] = useState<string | null>(null);
  const [enResolution, setEnResolution] = useState(false);

  const ajouterCode = useCallback((code: string) => {
    if (vusRef.current.has(code)) return;
    vusRef.current.add(code);
    setCodesScannés((prev) => [...prev, code]);
    setQuantitésCodes((prev) => ({ ...prev, [code]: 1 }));
    // Feedback haptic si disponible
    if (typeof navigator !== "undefined" && "vibrate" in navigator) {
      navigator.vibrate(60);
    }
  }, []);

  const démarrerCamera = useCallback(async () => {
    if (!videoRef.current) return;
    try {
      const reader = new BrowserMultiFormatReader();
      readerRef.current = reader;
      setErreurCamera(null);
      setCameraActive(true);

      await reader.decodeFromVideoDevice(
        undefined, // utilise la caméra arrière par défaut
        videoRef.current,
        (result, error) => {
          if (result) {
            ajouterCode(result.getText());
          }
          if (error && (error as { name?: string }).name !== "NotFoundException") {
            // NotFoundException est normale (pas de code trouvé dans le frame)
          }
        }
      );
    } catch (err) {
      const msg =
        err instanceof DOMException && err.name === "NotAllowedError"
          ? "Permission caméra refusée. Autorisez l'accès dans les paramètres du navigateur."
          : "Impossible d'accéder à la caméra.";
      setErreurCamera(msg);
      setCameraActive(false);
    }
  }, [ajouterCode]);

  const arrêterCamera = useCallback(() => {
    if (readerRef.current) {
      BrowserMultiFormatReader.releaseAllStreams();
      readerRef.current = null;
    }
    setCameraActive(false);
  }, []);

  // Démarrer/arrêter caméra selon l'état d'ouverture du modal
  useEffect(() => {
    if (ouvert) {
      démarrerCamera();
    } else {
      arrêterCamera();
      // Reset à la fermeture
      vusRef.current = new Set();
      setCodesScannés([]);
      setQuantitésCodes({});
      setErreurCamera(null);
    }
    return arrêterCamera;
  }, [ouvert, démarrerCamera, arrêterCamera]);

  const supprimerCode = (code: string) => {
    vusRef.current.delete(code);
    setCodesScannés((prev) => prev.filter((c) => c !== code));
    setQuantitésCodes((prev) => {
      const next = { ...prev };
      delete next[code];
      return next;
    });
  };

  const importer = async () => {
    if (codesScannés.length === 0) return;
    setEnResolution(true);
    try {
      const resultat = await scannerCodesBatch(codesScannés);
      onImporter(resultat.trouves, resultat.inconnus, quantitésCodes);
      if (resultat.inconnus.length > 0) {
        toast.info(
          `${resultat.trouves.length} article(s) trouv\u00e9(s), ${resultat.inconnus.length} code(s) non reconnu(s)`
        );
      }
      onFermer();
    } catch {
      toast.error("Erreur lors de la r\u00e9solution des codes-barres");
    } finally {
      setEnResolution(false);
    }
  };

  return (
    <Dialog open={ouvert} onOpenChange={(open) => !open && onFermer()}>
      <DialogContent className="max-w-md p-0 overflow-hidden">
        <DialogHeader className="px-4 pt-4 pb-2">
          <DialogTitle className="flex items-center gap-2">
            <ScanLine className="h-4 w-4" />
            Scanner plusieurs codes-barres
          </DialogTitle>
        </DialogHeader>

        {/* Vue caméra */}
        <div className="relative bg-black aspect-[4/3] mx-4 rounded-lg overflow-hidden">
          <video
            ref={videoRef}
            className="w-full h-full object-cover"
            muted
            playsInline
            autoPlay
            aria-label="Flux caméra"
          />
          {/* Réticule */}
          {cameraActive && (
            <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
              <div className="border-2 border-white/70 rounded w-48 h-32 relative">
                <span className="absolute -top-1 -left-1 border-t-2 border-l-2 border-primary rounded-tl w-4 h-4" />
                <span className="absolute -top-1 -right-1 border-t-2 border-r-2 border-primary rounded-tr w-4 h-4" />
                <span className="absolute -bottom-1 -left-1 border-b-2 border-l-2 border-primary rounded-bl w-4 h-4" />
                <span className="absolute -bottom-1 -right-1 border-b-2 border-r-2 border-primary rounded-br w-4 h-4" />
                <ScanLine className="absolute inset-0 m-auto h-4 w-4 text-white/70" />
              </div>
            </div>
          )}
          {/* Overlay erreur */}
          {erreurCamera && (
            <div className="absolute inset-0 flex flex-col items-center justify-center bg-black/80 text-white p-4 text-center">
              <CameraOff className="h-8 w-8 mb-2 text-muted-foreground" />
              <p className="text-sm">{erreurCamera}</p>
              <Button
                variant="secondary"
                size="sm"
                className="mt-3"
                onClick={démarrerCamera}
              >
                <Camera className="mr-1 h-4 w-4" />
                Réessayer
              </Button>
            </div>
          )}
          {/* Indicateur actif */}
          {cameraActive && (
            <div className="absolute top-2 right-2">
              <span className="flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75" />
                <span className="relative inline-flex rounded-full h-2 w-2 bg-green-500" />
              </span>
            </div>
          )}
        </div>

        {/* Codes scannés */}
        <div className="px-4 py-3 space-y-2">
          <div className="flex items-center justify-between">
            <p className="text-sm font-medium">
              Codes détectés{" "}
              <Badge variant="secondary" className="ml-1">
                {codesScannés.length}
              </Badge>
            </p>
            {codesScannés.length > 0 && (
              <Button
                variant="ghost"
                size="sm"
                className="text-xs"
                onClick={() => {
                  vusRef.current = new Set();
                  setCodesScannés([]);
                  setQuantitésCodes({});
                }}
              >
                Tout effacer
              </Button>
            )}
          </div>

          {codesScannés.length === 0 ? (
            <p className="text-xs text-muted-foreground py-2 text-center">
              Dirigez la caméra vers un code-barres
            </p>
          ) : (
            <div className="space-y-1 max-h-32 overflow-y-auto">
              {codesScannés.map((code) => (
                <div
                  key={code}
                  className="flex items-center gap-2 rounded-md border px-2 py-1"
                >
                  <span className="font-mono text-xs flex-1 truncate">
                    {code.length > 13 ? `${code.slice(0, 13)}…` : code}
                  </span>
                  <div className="flex items-center gap-1">
                    <button
                      onClick={() =>
                        setQuantitésCodes((prev) => ({
                          ...prev,
                          [code]: Math.max(1, (prev[code] ?? 1) - 1),
                        }))
                      }
                      className="p-0.5 rounded hover:bg-muted"
                      aria-label="Réduire quantité"
                    >
                      <Minus className="h-3 w-3" />
                    </button>
                    <Input
                      type="number"
                      min={1}
                      max={99}
                      value={quantitésCodes[code] ?? 1}
                      onChange={(e) =>
                        setQuantitésCodes((prev) => ({
                          ...prev,
                          [code]: Math.max(1, Math.min(99, Number(e.target.value) || 1)),
                        }))
                      }
                      className="h-6 w-12 text-center text-xs px-1"
                    />
                    <button
                      onClick={() =>
                        setQuantitésCodes((prev) => ({
                          ...prev,
                          [code]: Math.min(99, (prev[code] ?? 1) + 1),
                        }))
                      }
                      className="p-0.5 rounded hover:bg-muted"
                      aria-label="Augmenter quantité"
                    >
                      <Plus className="h-3 w-3" />
                    </button>
                  </div>
                  <button
                    onClick={() => supprimerCode(code)}
                    className="hover:text-destructive transition-colors p-0.5"
                    aria-label={`Retirer le code ${code}`}
                  >
                    <X className="h-3 w-3" />
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Actions */}
        <div className="px-4 pb-4 flex gap-2">
          <Button
            className="flex-1"
            disabled={codesScannés.length === 0 || enResolution}
            onClick={importer}
          >
            {enResolution ? (
              <span className="mr-2 h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent" />
            ) : (
              <Check className="mr-2 h-4 w-4" />
            )}
            {labelImporter} ({codesScannés.length})
          </Button>
          <Button variant="outline" onClick={onFermer}>
            Annuler
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}
