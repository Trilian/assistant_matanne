"use client";

import Link from "next/link";
import { useMemo, useRef, useState } from "react";
import { Camera, Upload, Loader2, Ticket, Sparkles } from "lucide-react";
import { toast } from "sonner";
import { Card, CardContent, CardHeader, CardTitle } from "@/composants/ui/card";
import { Button } from "@/composants/ui/button";
import { Badge } from "@/composants/ui/badge";
import { analyserTicketJeuxOCR } from "@/bibliotheque/api/jeux";
import type { ResultatTicketOCRJeux } from "@/types/jeux";

interface GrilleOCR {
  type: "euromillions" | "loto";
  numeros: number[];
  etoiles?: number[];
  chance?: number;
  source: string;
  confiance: number;
}

interface PariOCR {
  typePari: string;
  prediction: string;
  cote?: number;
  mise?: number;
  source: string;
  confiance: number;
}

function extraireEntiers(texte: string): number[] {
  const matches = texte.match(/\b\d{1,2}\b/g) ?? [];
  return matches.map((v) => Number(v));
}

function uniqSorted(nums: number[]): number[] {
  return Array.from(new Set(nums)).sort((a, b) => a - b);
}

function normaliserTexte(texte: string): string {
  return texte.replace(/\s+/g, " ").trim();
}

function detecterCote(texte: string): number | undefined {
  const match = texte.match(/(?:cote|@)\s*[:=]?\s*(\d+[\.,]\d{1,2})/i);
  if (!match) return undefined;
  const cote = Number(match[1].replace(",", "."));
  if (Number.isFinite(cote) && cote >= 1.01 && cote <= 100) return cote;
  return undefined;
}

function scoreGrilleEuromillions(desc: string, nbNums: number, nbEtoiles: number): number {
  let score = 0;
  if (desc.includes("euro") || desc.includes("million")) score += 45;
  if (nbNums >= 5) score += 35;
  if (nbEtoiles >= 2) score += 20;
  return Math.min(100, score);
}

function scoreGrilleLoto(desc: string, nbNums: number, chance: number | undefined): number {
  let score = 0;
  if (desc.includes("loto") || desc.includes("fdj")) score += 50;
  if (nbNums >= 5) score += 40;
  if (chance != null) score += 10;
  return Math.min(100, score);
}

function scorePari(desc: string, cote: number | undefined, mise: number | undefined): number {
  let score = 0;
  if (/(pari|1n2|over|under|btts|double chance|handicap)/i.test(desc)) score += 50;
  if (cote != null) score += 30;
  if (mise != null && mise > 0) score += 20;
  return Math.min(100, score);
}

function detecterGrillesDepuisOCR(res: ResultatTicketOCRJeux | null): GrilleOCR[] {
  if (!res?.donnees?.lignes?.length) return [];
  const candidates: GrilleOCR[] = [];

  for (const ligne of res.donnees.lignes) {
    const desc = ligne.description.toLowerCase();
    const nums = extraireEntiers(ligne.description);

    const euNums = uniqSorted(nums.filter((n) => n >= 1 && n <= 50));
    const euStars = uniqSorted(nums.filter((n) => n >= 1 && n <= 12));
    const estEuromillions =
      euNums.length >= 5 && euStars.length >= 2 && ((desc.includes("euro") || desc.includes("million")) || nums.length >= 7);
    if (estEuromillions) {
      const confiance = scoreGrilleEuromillions(desc, euNums.length, euStars.length);
      candidates.push({
        type: "euromillions",
        numeros: euNums.slice(0, 5),
        etoiles: euStars.slice(0, 2),
        source: ligne.description,
        confiance,
      });
    }

    const lotoNums = uniqSorted(nums.filter((n) => n >= 1 && n <= 49));
    const chance = nums.find((n) => n >= 1 && n <= 10);
    const estLoto =
      lotoNums.length >= 5 && ((desc.includes("loto") || desc.includes("fdj")) || nums.length >= 5);
    if (estLoto) {
      const confiance = scoreGrilleLoto(desc, lotoNums.length, chance);
      candidates.push({
        type: "loto",
        numeros: lotoNums.slice(0, 5),
        chance,
        source: ligne.description,
        confiance,
      });
    }
  }

  return candidates;
}

function detecterParisDepuisOCR(res: ResultatTicketOCRJeux | null): PariOCR[] {
  if (!res?.donnees?.lignes?.length) return [];
  const candidates: PariOCR[] = [];

  for (const ligne of res.donnees.lignes) {
    const descBrut = ligne.description;
    const desc = descBrut.toLowerCase();
    const cote = detecterCote(descBrut);
    const mise = ligne.prix_total && ligne.prix_total > 0 ? ligne.prix_total : undefined;

    if (!/(pari|1n2|over|under|btts|double chance|handicap)/i.test(desc)) continue;

    const confiance = scorePari(desc, cote, mise);
    const prediction = normaliserTexte(descBrut).slice(0, 120);
    candidates.push({
      typePari: "1X2",
      prediction,
      cote,
      mise,
      source: descBrut,
      confiance,
    });
  }

  return candidates;
}

export default function OCRTicketJeuxPage() {
  const inputRef = useRef<HTMLInputElement>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [resultat, setResultat] = useState<ResultatTicketOCRJeux | null>(null);
  const [chargement, setChargement] = useState(false);
  const [seuilConfiance, setSeuilConfiance] = useState(80);

  const grillesDetectees = useMemo(() => detecterGrillesDepuisOCR(resultat), [resultat]);
  const parisDetectes = useMemo(() => detecterParisDepuisOCR(resultat), [resultat]);
  const grillesFiltrees = useMemo(
    () => grillesDetectees.filter((g) => g.confiance >= seuilConfiance),
    [grillesDetectees, seuilConfiance]
  );

  async function onFichier(file: File) {
    if (!file.type.startsWith("image/")) {
      toast.error("Veuillez sélectionner une image");
      return;
    }
    if (file.size > 10 * 1024 * 1024) {
      toast.error("Image trop volumineuse (max 10 Mo)");
      return;
    }

    const reader = new FileReader();
    reader.onload = () => setPreview(reader.result as string);
    reader.readAsDataURL(file);

    setChargement(true);
    try {
      const data = await analyserTicketJeuxOCR(file);
      setResultat(data);
      if (data.success) {
        toast.success("Ticket analysé avec succès");
      } else {
        toast.error(data.message || "Analyse OCR incomplète");
      }
    } catch {
      toast.error("Impossible d'analyser le ticket");
    } finally {
      setChargement(false);
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">🎟️ OCR Ticket Jeux</h1>
        <p className="text-muted-foreground">Scannez un ticket FDJ puis pré-remplissez une grille loto/euromillions.</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Camera className="h-5 w-5" />
            Import du ticket
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <input
            ref={inputRef}
            type="file"
            accept="image/*"
            className="hidden"
            onChange={(e) => {
              const file = e.target.files?.[0];
              if (file) void onFichier(file);
            }}
          />

          <div
            className="rounded-lg border-2 border-dashed p-8 text-center cursor-pointer hover:bg-accent/40"
            onClick={() => inputRef.current?.click()}
          >
            <Upload className="h-10 w-10 mx-auto mb-2 text-muted-foreground" />
            <p className="font-medium">Cliquez pour charger une photo du ticket</p>
            <p className="text-xs text-muted-foreground">JPEG, PNG, WebP — 10 Mo max</p>
          </div>

          {preview && (
            <img src={preview} alt="Ticket" className="max-h-72 w-full rounded-lg object-contain border" />
          )}

          {chargement && (
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <Loader2 className="h-4 w-4 animate-spin" />
              Analyse OCR en cours...
            </div>
          )}
        </CardContent>
      </Card>

      {resultat?.donnees && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Ticket className="h-5 w-5" />
              Résultat OCR
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-sm">
              <div><span className="text-muted-foreground">Point de vente:</span> {resultat.donnees.point_vente ?? "-"}</div>
              <div><span className="text-muted-foreground">Date:</span> {resultat.donnees.date_achat ?? "-"}</div>
              <div><span className="text-muted-foreground">Total:</span> {resultat.donnees.total != null ? `${resultat.donnees.total.toFixed(2)} €` : "-"}</div>
            </div>
            <div className="rounded-lg bg-muted p-3 text-xs overflow-x-auto">
              <pre>{JSON.stringify(resultat.donnees.lignes, null, 2)}</pre>
            </div>
          </CardContent>
        </Card>
      )}

      {grillesDetectees.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Sparkles className="h-5 w-5" />
              Grilles détectées et pré-remplissage
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="space-y-1">
              <div className="flex items-center justify-between text-sm">
                <span>Filtre confiance OCR</span>
                <span className="font-medium">{seuilConfiance}%+</span>
              </div>
              <input
                type="range"
                min={50}
                max={100}
                step={5}
                value={seuilConfiance}
                onChange={(e) => setSeuilConfiance(Number(e.target.value))}
                className="w-full"
              />
              <p className="text-xs text-muted-foreground">
                {grillesFiltrees.length} / {grillesDetectees.length} grilles proposées après filtrage
              </p>
            </div>

            {grillesFiltrees.map((g, idx) => (
              <div key={`${g.type}-${idx}`} className="rounded-lg border p-3 space-y-2">
                <div className="flex items-center gap-2">
                  <Badge>{g.type}</Badge>
                  <Badge variant={g.confiance >= 85 ? "default" : "secondary"}>{g.confiance}%</Badge>
                  <span className="text-xs text-muted-foreground truncate">{g.source}</span>
                </div>
                <p className="text-sm">Numéros: {g.numeros.join(" - ")}</p>
                {g.etoiles && <p className="text-sm">Étoiles: {g.etoiles.join(" - ")}</p>}
                {g.chance != null && <p className="text-sm">Chance: {g.chance}</p>}

                {g.type === "euromillions" ? (
                  <Link
                    href={`/jeux/euromillions?numeros=${g.numeros.join(",")}&etoiles=${(g.etoiles ?? []).join(",")}`}
                    className="inline-flex"
                  >
                    <Button size="sm">Pré-remplir Euromillions</Button>
                  </Link>
                ) : (
                  <Link
                    href={`/jeux/loto?numeros=${g.numeros.join(",")}${g.chance != null ? `&chance=${g.chance}` : ""}`}
                    className="inline-flex"
                  >
                    <Button size="sm">Pré-remplir Loto</Button>
                  </Link>
                )}
              </div>
            ))}
            {grillesFiltrees.length === 0 && (
              <p className="text-sm text-muted-foreground">Aucune grille avec ce niveau de confiance.</p>
            )}
          </CardContent>
        </Card>
      )}

      {parisDetectes.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">🏟️ Paris détectés</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {parisDetectes
              .filter((p) => p.confiance >= seuilConfiance)
              .map((p, idx) => (
                <div key={`pari-${idx}`} className="rounded-lg border p-3 space-y-2">
                  <div className="flex items-center gap-2">
                    <Badge>pari</Badge>
                    <Badge variant={p.confiance >= 85 ? "default" : "secondary"}>{p.confiance}%</Badge>
                    <span className="text-xs text-muted-foreground truncate">{p.source}</span>
                  </div>
                  <p className="text-sm">Prédiction: {p.prediction}</p>
                  <div className="text-sm text-muted-foreground">
                    {p.cote != null && <span className="mr-4">Cote: {p.cote.toFixed(2)}</span>}
                    {p.mise != null && <span>Mise: {p.mise.toFixed(2)} €</span>}
                  </div>
                  <Link
                    href={`/jeux/paris?source_ocr=1&type_pari=${encodeURIComponent(p.typePari)}&prediction=${encodeURIComponent(p.prediction)}${p.cote != null ? `&cote=${p.cote}` : ""}${p.mise != null ? `&mise=${p.mise}` : ""}`}
                    className="inline-flex"
                  >
                    <Button size="sm">Créer un pari pré-rempli</Button>
                  </Link>
                </div>
              ))}
          </CardContent>
        </Card>
      )}
    </div>
  );
}
