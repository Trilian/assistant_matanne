// ═══════════════════════════════════════════════════════════
// Bouton Export PDF — Composant réutilisable
// ═══════════════════════════════════════════════════════════

"use client";

import { useState } from "react";
import { Download, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { exporterPdf, type TypeExport } from "@/bibliotheque/api/export";

interface PropsBoutonExportPdf {
  typeExport: TypeExport;
  idRessource?: number;
  label?: string;
  variant?: "default" | "outline" | "ghost" | "secondary";
  size?: "default" | "sm" | "lg" | "icon";
}

export function BoutonExportPdf({
  typeExport,
  idRessource,
  label = "Exporter PDF",
  variant = "outline",
  size = "sm",
}: PropsBoutonExportPdf) {
  const [enCours, setEnCours] = useState(false);

  const handleExport = async () => {
    setEnCours(true);
    try {
      await exporterPdf(typeExport, idRessource);
    } catch {
      // Silently handle — user sees no download
    } finally {
      setEnCours(false);
    }
  };

  return (
    <Button
      variant={variant}
      size={size}
      onClick={handleExport}
      disabled={enCours}
    >
      {enCours ? (
        <Loader2 className="h-4 w-4 animate-spin mr-2" />
      ) : (
        <Download className="h-4 w-4 mr-2" />
      )}
      {label}
    </Button>
  );
}
