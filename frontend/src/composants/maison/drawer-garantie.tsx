// ═══════════════════════════════════════════════════════════
// DrawerGarantie — Fiche garantie avec actions SAV
// ═══════════════════════════════════════════════════════════

"use client";

import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetDescription,
} from "@/composants/ui/sheet";
import { Badge } from "@/composants/ui/badge";
import { Button } from "@/composants/ui/button";
import { utiliserRequete } from "@/crochets/utiliser-api";
import { obtenirGarantie } from "@/bibliotheque/api/maison";

interface DrawerGarantieProps {
  garantieId: number | null;
  ouvert: boolean;
  onFermer: () => void;
}

const STATUT_COULEUR: Record<string, string> = {
  active: "bg-green-100 text-green-800",
  expiree: "bg-red-100 text-red-800",
  en_cours_sav: "bg-yellow-100 text-yellow-800",
};

function formaterDate(dateStr?: string): string {
  if (!dateStr) return "—";
  return new Date(dateStr).toLocaleDateString("fr-FR", {
    day: "numeric",
    month: "long",
    year: "numeric",
  });
}

function joursRestants(dateFin: string): number {
  return Math.ceil(
    (new Date(dateFin).getTime() - Date.now()) / (1000 * 86400)
  );
}

export function DrawerGarantie({ garantieId, ouvert, onFermer }: DrawerGarantieProps) {
  const { data: garantie, isLoading } = utiliserRequete(
    ["garantie", String(garantieId)],
    () => obtenirGarantie(garantieId!),
    { enabled: !!garantieId }
  );

  const jours = garantie ? joursRestants(garantie.date_fin_garantie) : null;

  return (
    <Sheet open={ouvert} onOpenChange={(o) => !o && onFermer()}>
      <SheetContent side="right" className="w-full sm:w-[440px] overflow-y-auto">
        <SheetHeader>
          <SheetTitle>{garantie?.appareil ?? "Garantie"}</SheetTitle>
          <SheetDescription>Informations et actions</SheetDescription>
        </SheetHeader>

        <div className="mt-6 space-y-5">
          {isLoading && (
            <div className="flex items-center justify-center py-12">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary" />
            </div>
          )}

          {garantie && !isLoading && (
            <>
              {/* Statut */}
              <div className="flex items-center gap-3">
                <span
                  className={`text-xs font-medium px-2 py-0.5 rounded-full ${
                    STATUT_COULEUR[garantie.statut] ?? "bg-muted"
                  }`}
                >
                  {garantie.statut}
                </span>
                {jours !== null && (
                  <span
                    className={`text-sm ${
                      jours < 0 ? "text-red-600" : jours < 30 ? "text-orange-600" : "text-muted-foreground"
                    }`}
                  >
                    {jours < 0
                      ? `Expirée depuis ${Math.abs(jours)} jours`
                      : `Expire dans ${jours} jours`}
                  </span>
                )}
              </div>

              {/* Détails */}
              <div className="space-y-3 rounded-lg border p-4 text-sm">
                <div className="grid grid-cols-2 gap-2">
                  <span className="text-muted-foreground">Marque</span>
                  <span className="font-medium">{garantie.marque ?? "—"}</span>

                  <span className="text-muted-foreground">N° série</span>
                  <span className="font-mono text-xs">{garantie.numero_serie ?? "—"}</span>

                  <span className="text-muted-foreground">Achat</span>
                  <span>{formaterDate(garantie.date_achat)}</span>

                  <span className="text-muted-foreground">Fin garantie</span>
                  <span className={jours !== null && jours < 30 ? "font-bold text-orange-600" : ""}>
                    {formaterDate(garantie.date_fin_garantie)}
                  </span>

                  {garantie.magasin && (
                    <>
                      <span className="text-muted-foreground">Magasin</span>
                      <span>{garantie.magasin}</span>
                    </>
                  )}

                  {garantie.prix_achat && (
                    <>
                      <span className="text-muted-foreground">Prix</span>
                      <span>{garantie.prix_achat.toLocaleString("fr-FR")} €</span>
                    </>
                  )}
                </div>
              </div>

              {/* Notes */}
              {garantie.notes && (
                <div className="rounded-lg bg-muted/50 p-3">
                  <p className="text-xs font-semibold text-muted-foreground mb-1">Notes</p>
                  <p className="text-sm">{garantie.notes}</p>
                </div>
              )}

              {/* Actions */}
              <div className="space-y-2">
                <p className="text-xs font-semibold text-muted-foreground uppercase">Actions</p>
                <div className="grid gap-2">
                  {garantie.document_url && (
                    <Button variant="outline" size="sm" asChild>
                      <a href={garantie.document_url} target="_blank" rel="noreferrer">
                        📄 Voir le justificatif
                      </a>
                    </Button>
                  )}
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() =>
                      window.open(
                        `mailto:sav@${garantie.marque?.toLowerCase().replace(/\s+/g, "") ?? "fabricant"}.com?subject=SAV - ${garantie.appareil} (N° ${garantie.numero_serie})`,
                        "_blank"
                      )
                    }
                  >
                    📧 Contacter le SAV
                  </Button>
                  <Button variant="outline" size="sm" asChild>
                    <a href="/maison/garanties" onClick={onFermer}>
                      ✏️ Modifier la fiche
                    </a>
                  </Button>
                </div>
              </div>

              {/* Alertes et recommandations */}
              {jours !== null && jours > 0 && jours <= 30 && (
                <div className="rounded-lg bg-orange-50 dark:bg-orange-950/30 p-4">
                  <p className="text-sm font-medium text-orange-700 dark:text-orange-300">
                    ⚠️ Garantie expirant bientôt
                  </p>
                  <p className="text-sm text-orange-600 dark:text-orange-400 mt-1">
                    Pensez à rédiger un avis en ligne avant expiration — cela peut vous aider à obtenir
                    un geste commercial en cas de panne.
                  </p>
                </div>
              )}
            </>
          )}
        </div>
      </SheetContent>
    </Sheet>
  );
}
