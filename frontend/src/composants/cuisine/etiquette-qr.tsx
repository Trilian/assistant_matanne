// ═══════════════════════════════════════════════════════════
// EtiquetteQR — Dialogue d'étiquette QR code pour inventaire
// ═══════════════════════════════════════════════════════════

"use client";

import { useRef } from "react";
import { QrCode, Printer } from "lucide-react";
import { Button } from "@/composants/ui/button";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from "@/composants/ui/dialog";

interface EtiquetteQRProps {
  ouvert: boolean;
  onFermer: () => void;
  articleId: number;
  articleNom: string;
  emplacement?: string;
  datePeremption?: string;
}

export function EtiquetteQR({
  ouvert,
  onFermer,
  articleId,
  articleNom,
  emplacement,
  datePeremption,
}: EtiquetteQRProps) {
  const imageRef = useRef<HTMLImageElement>(null);
  const qrUrl = `/api/v1/inventaire/articles/${articleId}/qr`;

  function imprimer() {
    const printWindow = window.open("", "_blank", "width=400,height=500");
    if (!printWindow) return;

    const peremptionFormatee = datePeremption
      ? new Date(datePeremption).toLocaleDateString("fr-FR")
      : null;

    printWindow.document.write(`
      <!DOCTYPE html>
      <html>
        <head>
          <title>QR - ${articleNom}</title>
          <style>
            body { font-family: sans-serif; text-align: center; padding: 20px; }
            img { width: 200px; height: 200px; }
            h2 { margin: 10px 0 4px; font-size: 18px; }
            p { margin: 2px 0; font-size: 13px; color: #555; }
            @media print { body { padding: 10px; } }
          </style>
        </head>
        <body>
          <img src="${qrUrl}" alt="QR Code" />
          <h2>${articleNom}</h2>
          ${emplacement ? `<p>${emplacement}</p>` : ""}
          ${peremptionFormatee ? `<p>Péremption: ${peremptionFormatee}</p>` : ""}
          <script>window.onload = () => { window.print(); window.close(); }</script>
        </body>
      </html>
    `);
    printWindow.document.close();
  }

  return (
    <Dialog open={ouvert} onOpenChange={(v) => !v && onFermer()}>
      <DialogContent className="max-w-sm">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <QrCode className="h-5 w-5" />
            Étiquette QR
          </DialogTitle>
          <DialogDescription>
            Scannez ou imprimez cette étiquette pour identifier l'article.
          </DialogDescription>
        </DialogHeader>

        <div className="flex flex-col items-center gap-4 py-4">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img
            ref={imageRef}
            src={qrUrl}
            alt={`QR code pour ${articleNom}`}
            className="w-48 h-48 border rounded-lg"
          />
          <div className="text-center">
            <p className="font-semibold">{articleNom}</p>
            {emplacement && (
              <p className="text-sm text-muted-foreground">{emplacement}</p>
            )}
            {datePeremption && (
              <p className="text-sm text-muted-foreground">
                Péremption:{" "}
                {new Date(datePeremption).toLocaleDateString("fr-FR")}
              </p>
            )}
          </div>
        </div>

        <div className="flex gap-2 justify-end">
          <Button variant="outline" onClick={onFermer}>
            Fermer
          </Button>
          <Button onClick={imprimer}>
            <Printer className="mr-2 h-4 w-4" />
            Imprimer
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}
