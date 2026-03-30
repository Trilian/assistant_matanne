"use client";

import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/composants/ui/card";
import { Button } from "@/composants/ui/button";
import { Badge } from "@/composants/ui/badge";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/composants/ui/select";
import { Loader2, Sparkles, TrendingUp, Zap, BarChart3 } from "lucide-react";
import { toast } from "sonner";

interface GrilleIAGenereeProps {
  onGenerer: (mode: "chauds" | "froids" | "equilibre") => Promise<{
    numeros: number[];
    numero_chance: number;
    mode: string;
    analyse: string;
    confiance: number;
  }>;
  onAnalyser: (numeros: number[], numeroChance: number) => Promise<{
    note: number;
    points_forts: string[];
    points_faibles: string[];
    recommandations: string[];
    appreciation: string;
  }>;
}

export function GrilleIAPonderee({ onGenerer, onAnalyser }: GrilleIAGenereeProps) {
  const [mode, setMode] = useState<"chauds" | "froids" | "equilibre">("equilibre");
  const [loading, setLoading] = useState(false);
  const [grille, setGrille] = useState<{
    numeros: number[];
    numero_chance: number;
    analyse: string;
    confiance: number;
  } | null>(null);
  const [analyse, setAnalyse] = useState<{
    note: number;
    points_forts: string[];
    points_faibles: string[];
    recommandations: string[];
    appreciation: string;
  } | null>(null);

  const handleGenerer = async () => {
    setLoading(true);
    setGrille(null);
    setAnalyse(null);

    try {
      const result = await onGenerer(mode);
      setGrille({
        numeros: result.numeros,
        numero_chance: result.numero_chance,
        analyse: result.analyse,
        confiance: result.confiance,
      });
      toast.success("Grille IA générée avec succès");
    } catch (err) {
      toast.error("Erreur lors de la génération de la grille");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleAnalyser = async () => {
    if (!grille) return;

    setLoading(true);
    try {
      const result = await onAnalyser(grille.numeros, grille.numero_chance);
      setAnalyse(result);
      toast.success("Analyse complétée");
    } catch (err) {
      toast.error("Erreur lors de l'analyse");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card className="border-purple-200 dark:border-purple-800">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Sparkles className="h-5 w-5 text-purple-600" />
          Générateur IA Pondéré
        </CardTitle>
        <CardDescription>
          Grille intelligente basée sur statistiques et Mistral AI
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Sélecteur mode */}
        <div className="flex items-center gap-3">
          <Select value={mode} onValueChange={(v) => setMode(v as "chauds" | "froids" | "equilibre")}>
            <SelectTrigger className="w-48">
              <SelectValue placeholder="Stratégie" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="chauds">
                <div className="flex items-center gap-2">
                  <TrendingUp className="h-4 w-4 text-red-500" />
                  <span>Numéros chauds</span>
                </div>
              </SelectItem>
              <SelectItem value="froids">
                <div className="flex items-center gap-2">
                  <Zap className="h-4 w-4 text-blue-500" />
                  <span>Numéros en retard</span>
                </div>
              </SelectItem>
              <SelectItem value="equilibre">
                <div className="flex items-center gap-2">
                  <BarChart3 className="h-4 w-4 text-emerald-500" />
                  <span>Équilibre (recommandé)</span>
                </div>
              </SelectItem>
            </SelectContent>
          </Select>

          <Button onClick={handleGenerer} disabled={loading} className="gap-2">
            {loading ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                Génération...
              </>
            ) : (
              <>
                <Sparkles className="h-4 w-4" />
                Générer
              </>
            )}
          </Button>
        </div>

        {/* Grille générée */}
        {grille && (
          <div className="space-y-3 p-4 bg-muted/30 rounded-lg">
            <div className="flex flex-wrap gap-2 items-center">
              {grille.numeros.map((n) => (
                <div
                  key={n}
                  className="flex h-10 w-10 items-center justify-center rounded-full bg-purple-600 text-white font-bold text-sm shadow-md"
                >
                  {n}
                </div>
              ))}
              <span className="mx-2 text-muted-foreground">+</span>
              <div className="flex h-10 w-10 items-center justify-center rounded-full bg-yellow-500 text-white font-bold text-sm shadow-md">
                {grille.numero_chance}
              </div>
            </div>

            <div className="text-sm text-muted-foreground">
              <p className="font-medium mb-1">Analyse IA:</p>
              <p>{grille.analyse}</p>
              <Badge variant="outline" className="mt-2">
                Confiance: {Math.round(grille.confiance * 100)}%
              </Badge>
            </div>

            <Button onClick={handleAnalyser} variant="outline" size="sm" disabled={loading}>
              {loading ? "Analyse en cours..." : "Analyser cette grille"}
            </Button>
          </div>
        )}

        {/* Résultat analyse */}
        {analyse && (
          <div className="space-y-2 p-4 bg-emerald-50 dark:bg-emerald-950/20 rounded-lg border border-emerald-200 dark:border-emerald-800">
            <div className="flex items-center justify-between">
              <h4 className="font-semibold text-sm">Critique IA Mistral</h4>
              <Badge variant={analyse.note >= 7 ? "default" : "secondary"}>
                Note: {analyse.note}/10
              </Badge>
            </div>

            <p className="text-sm italic">{analyse.appreciation}</p>

            {analyse.points_forts.length > 0 && (
              <div>
                <p className="text-xs font-medium text-emerald-700 dark:text-emerald-400">
                  ✅ Points forts:
                </p>
                <ul className="text-xs list-disc list-inside pl-2 space-y-1">
                  {analyse.points_forts.map((p, i) => (
                    <li key={i}>{p}</li>
                  ))}
                </ul>
              </div>
            )}

            {analyse.points_faibles.length > 0 && (
              <div>
                <p className="text-xs font-medium text-orange-700 dark:text-orange-400">
                  ⚠️ Points faibles:
                </p>
                <ul className="text-xs list-disc list-inside pl-2 space-y-1">
                  {analyse.points_faibles.map((p, i) => (
                    <li key={i}>{p}</li>
                  ))}
                </ul>
              </div>
            )}

            {analyse.recommandations.length > 0 && (
              <div>
                <p className="text-xs font-medium text-blue-700 dark:text-blue-400">
                  💡 Recommandations:
                </p>
                <ul className="text-xs list-disc list-inside pl-2 space-y-1">
                  {analyse.recommandations.map((r, i) => (
                    <li key={i}>{r}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}

        <p className="text-xs text-muted-foreground">
          ⚠️ Les grilles IA sont basées sur des statistiques historiques. Le Loto reste un jeu de
          hasard pur.
        </p>
      </CardContent>
    </Card>
  );
}
