import { Download, Loader2 } from "lucide-react";

import { Button } from "@/composants/ui/button";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/composants/ui/dialog";

type DialogueQrCoursesProps = {
  ouvert: boolean;
  qrUrl: string | null;
  chargementQr: boolean;
  onOpenChange: (ouvert: boolean) => void;
  onTelecharger: () => void;
};

export function DialogueQrCourses({
  ouvert,
  qrUrl,
  chargementQr,
  onOpenChange,
  onTelecharger,
}: DialogueQrCoursesProps) {
  return (
    <Dialog open={ouvert} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>QR de partage</DialogTitle>
        </DialogHeader>
        <div className="space-y-4">
          <p className="text-sm text-muted-foreground">
            Scannez ce QR pour ouvrir la version texte de votre liste de courses.
          </p>
          <div className="flex min-h-48 items-center justify-center rounded-lg border p-4">
            {chargementQr ? (
              <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
            ) : qrUrl ? (
              <img src={qrUrl} alt="QR liste de courses" className="h-52 w-52" />
            ) : (
              <p className="text-sm text-muted-foreground">QR indisponible</p>
            )}
          </div>
          <div className="flex justify-end">
            <Button variant="outline" onClick={onTelecharger} disabled={!qrUrl}>
              <Download className="mr-1 h-4 w-4" />
              Télécharger
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
