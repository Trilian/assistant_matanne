// ═══════════════════════════════════════════════════════════
// Page Sauvegarde — Export JSON + Restauration
// ═══════════════════════════════════════════════════════════

"use client";

import { useRef, useState } from "react";
import {
  Download,
  Upload,
  Loader2,
  Check,
  AlertTriangle,
  Database,
  RotateCcw,
} from "lucide-react";
import { toast } from "sonner";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/composants/ui/card";
import { Button } from "@/composants/ui/button";
import { Badge } from "@/composants/ui/badge";
import { Label } from "@/composants/ui/label";
import {
  listerDomaines,
  telechargerBackupJson,
  restaurerDepuisJson,
  DOMAINES_DEFAUT,
  type DomaineExport,
  type ResultatRestauration,
} from "@/bibliotheque/api/export";
import { utiliserRequete } from "@/crochets/utiliser-api";

export default function PageSauvegarde() {
  const [domainesSelectionnes, setDomainesSelectionnes] = useState<Set<string>>(
    new Set(DOMAINES_DEFAUT)
  );
  const [exportEnCours, setExportEnCours] = useState(false);
  const [importEnCours, setImportEnCours] = useState(false);
  const [resultatRestauration, setResultatRestauration] =
    useState<ResultatRestauration | null>(null);
  const [fichierImport, setFichierImport] = useState<File | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const { data: domaines = [] } = utiliserRequete<DomaineExport[]>(
    ["domaines-export"],
    listerDomaines
  );

  function toggleDomaine(id: string) {
    setDomainesSelectionnes((prev) => {
      const next = new Set(prev);
      if (next.has(id)) {
        next.delete(id);
      } else {
        next.add(id);
      }
      return next;
    });
  }

  function toutSelectionner() {
    setDomainesSelectionnes(new Set(domaines.map((d) => d.id)));
  }

  function toutDeselectionner() {
    setDomainesSelectionnes(new Set());
  }

  async function handleExport() {
    if (domainesSelectionnes.size === 0) {
      toast.error("Sélectionnez au moins un domaine à exporter");
      return;
    }
    setExportEnCours(true);
    try {
      await telechargerBackupJson(Array.from(domainesSelectionnes));
      toast.success("Backup téléchargé");
    } catch {
      toast.error("Erreur lors de l'export");
    } finally {
      setExportEnCours(false);
    }
  }

  async function handleImport() {
    if (!fichierImport) {
      toast.error("Sélectionnez un fichier JSON");
      return;
    }

    setImportEnCours(true);
    setResultatRestauration(null);
    try {
      const result = await restaurerDepuisJson(fichierImport);
      setResultatRestauration(result);
      if (result.success) {
        toast.success(result.message);
      } else {
        toast.error(result.message);
      }
    } catch {
      toast.error("Erreur lors de la restauration");
    } finally {
      setImportEnCours(false);
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold flex items-center gap-2">
          <Database className="h-6 w-6" />
          Sauvegarde &amp; Restauration
        </h1>
        <p className="text-sm text-muted-foreground mt-1">
          Exportez vos données en JSON ou restaurez depuis un backup.
        </p>
      </div>

      {/* Export */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Download className="h-5 w-5" />
            Exporter les données
          </CardTitle>
          <CardDescription>
            Téléchargez un fichier JSON contenant vos données sélectionnées.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center gap-3 flex-wrap">
            <Button
              variant="outline"
              size="sm"
              onClick={toutSelectionner}
            >
              Tout sélectionner
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={toutDeselectionner}
            >
              Tout décocher
            </Button>
            <Badge variant="secondary">
              {domainesSelectionnes.size} / {domaines.length || DOMAINES_DEFAUT.length} sélectionné(s)
            </Badge>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
            {(domaines.length > 0 ? domaines : DOMAINES_DEFAUT.map((id) => ({ id, label: id }))).map(
              (d) => (
                <label key={d.id} className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    id={`domaine-${d.id}`}
                    checked={domainesSelectionnes.has(d.id)}
                    onChange={() => toggleDomaine(d.id)}
                    className="h-4 w-4 rounded border-gray-300 accent-primary cursor-pointer"
                  />
                  <Label htmlFor={`domaine-${d.id}`} className="cursor-pointer font-normal">
                    {d.label}
                  </Label>
                </label>
              )
            )}
          </div>

          <Button
            onClick={handleExport}
            disabled={exportEnCours || domainesSelectionnes.size === 0}
            className="w-full sm:w-auto"
          >
            {exportEnCours ? (
              <>
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                Export en cours…
              </>
            ) : (
              <>
                <Download className="h-4 w-4 mr-2" />
                Télécharger le backup JSON
              </>
            )}
          </Button>
        </CardContent>
      </Card>

      {/* Restauration */}
      <Card className="border-amber-200 dark:border-amber-800">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <RotateCcw className="h-5 w-5 text-amber-600" />
            Restaurer depuis un backup
          </CardTitle>
          <CardDescription>
            Importez un fichier JSON précédemment exporté.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="rounded-lg bg-amber-50 dark:bg-amber-950 border border-amber-200 dark:border-amber-800 p-3 flex gap-2 text-sm text-amber-700 dark:text-amber-300">
            <AlertTriangle className="h-4 w-4 flex-shrink-0 mt-0.5" />
            <span>
              La restauration ajoute les données existantes sans supprimer celles
              présentes. Les doublons seront ignorés.
            </span>
          </div>

          <input
            ref={inputRef}
            type="file"
            accept=".json,.json.gz"
            className="hidden"
            onChange={(e) => {
              const f = e.target.files?.[0];
              setFichierImport(f ?? null);
              setResultatRestauration(null);
            }}
          />

          <div
            className="rounded-lg border-2 border-dashed p-6 text-center cursor-pointer hover:bg-accent/30 transition-colors"
            onClick={() => inputRef.current?.click()}
          >
            <Upload className="h-8 w-8 mx-auto mb-2 text-muted-foreground" />
            {fichierImport ? (
              <p className="text-sm font-medium">{fichierImport.name}</p>
            ) : (
              <>
                <p className="text-sm font-medium">
                  Choisir un fichier JSON
                </p>
                <p className="text-xs text-muted-foreground mt-1">
                  .json ou .json.gz
                </p>
              </>
            )}
          </div>

          <Button
            onClick={handleImport}
            disabled={!fichierImport || importEnCours}
            variant="outline"
            className="w-full sm:w-auto"
          >
            {importEnCours ? (
              <>
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                Restauration en cours…
              </>
            ) : (
              <>
                <RotateCcw className="h-4 w-4 mr-2" />
                Restaurer
              </>
            )}
          </Button>

          {/* Résultat restauration */}
          {resultatRestauration && (
            <div
              className={`rounded-lg border p-4 space-y-2 text-sm ${
                resultatRestauration.success
                  ? "bg-green-50 dark:bg-green-950 border-green-200 dark:border-green-800"
                  : "bg-red-50 dark:bg-red-950 border-red-200 dark:border-red-800"
              }`}
            >
              <div className="flex items-center gap-2 font-medium">
                {resultatRestauration.success ? (
                  <Check className="h-4 w-4 text-green-600" />
                ) : (
                  <AlertTriangle className="h-4 w-4 text-red-600" />
                )}
                {resultatRestauration.message}
              </div>
              {resultatRestauration.total_enregistrements > 0 && (
                <p className="text-xs text-muted-foreground">
                  {resultatRestauration.total_enregistrements} enregistrement(s) restauré(s)
                </p>
              )}
              {resultatRestauration.tables_restaurees?.length > 0 && (
                <div className="flex flex-wrap gap-1">
                  {resultatRestauration.tables_restaurees.map((t) => (
                    <Badge key={t} variant="secondary" className="text-xs">
                      {t}
                    </Badge>
                  ))}
                </div>
              )}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
