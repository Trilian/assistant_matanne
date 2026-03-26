// ═══════════════════════════════════════════════════════════
// Weekend — Suggestions IA méteo-intelligentes (Phase O2)
// ═══════════════════════════════════════════════════════════

"use client";

import { useState } from "react";
import {
  Palmtree,
  Sparkles,
  Loader2,
  CloudRain,
  Sun,
  Cloud,
  Calendar,
} from "lucide-react";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from "@/composants/ui/card";
import { Button } from "@/composants/ui/button";
import { Badge } from "@/composants/ui/badge";
import { obtenirSuggestionsWeekend } from "@/bibliotheque/api/famille";
import { toast } from "sonner";

export default function PageWeekend() {
  const [suggestions, setSuggestions] = useState<string>("");
  const [meteoInfo, setMeteoInfo] = useState<string>("");
  const [enChargement, setEnChargement] = useState(false);

  const isWeekendApproaching = new Date().getDay() >= 4; // Jeudi ou plus

  const genererSuggestions = async () => {
    setEnChargement(true);
    try {
      const resultat = await obtenirSuggestionsWeekend();
      setSuggestions(resultat.suggestions);
      setMeteoInfo(resultat.meteo);
      toast.success("Suggestions générées avec la météo du weekend !");
    } catch {
      toast.error("Erreur lors de la génération des suggestions");
    } finally {
      setEnChargement(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight flex items-center gap-2">
          <Palmtree className="h-6 w-6" />
          Weekend
        </h1>
        <p className="text-muted-foreground">
          Suggestions d'activités adaptées à Jules et à la météo du weekend
        </p>
      </div>

      {/* Section génération IA */}
      <Card className="bg-gradient-to-br from-purple-50/50 to-indigo-50/50 dark:from-purple-950/20 dark:to-indigo-950/20">
        <CardHeader>
          <div className="flex items-center gap-2">
            <Sparkles className="h-5 w-5 text-purple-500" />
            <CardTitle className="text-base">Suggestions IA</CardTitle>
          </div>
          <CardDescription>
            L'IA analyse la météo du weekend et l'âge de Jules pour générer 3-5 suggestions
            personnalisées
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {!isWeekendApproaching && !suggestions && (
            <div className="flex items-center gap-2 p-3 rounded-lg bg-amber-100/50 dark:bg-amber-900/20 text-amber-800 dark:text-amber-300 text-sm">
              <Calendar className="h-4 w-4 shrink-0" />
              <span>
                Les suggestions weekend sont optimales à partir du jeudi. Revenez plus tard !
              </span>
            </div>
          )}

          <Button
            onClick={genererSuggestions}
            disabled={enChargement}
            className="w-full"
            size="lg"
          >
            {enChargement ? (
              <>
                <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                Génération en cours...
              </>
            ) : (
              <>
                <Sparkles className="mr-2 h-5 w-5" />
                Générer les suggestions du weekend
              </>
            )}
          </Button>

          {meteoInfo && (
            <div className="flex items-center gap-2 p-3 rounded-lg bg-blue-100/50 dark:bg-blue-900/20 text-blue-800 dark:text-blue-300 text-sm">
              <Cloud className="h-4 w-4 shrink-0" />
              <span>{meteoInfo}</span>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Résultats suggestions */}
      {suggestions && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Suggestions générées</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="prose prose-sm dark:prose-invert max-w-none whitespace-pre-wrap">
              {suggestions}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Infos supplémentaires */}
      {!suggestions && (
        <Card>
          <CardHeader>
            <CardTitle className="text-sm">Comment ça marche ?</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2 text-sm text-muted-foreground">
            <p>
              Le générateur de suggestions weekend utilise l'IA pour proposer des activités
              adaptées à votre situation :
            </p>
            <ul className="list-disc list-inside space-y-1 pl-2">
              <li>Météo du samedi et dimanche (récupération automatique)</li>
              <li>Âge de Jules en mois</li>
              <li>Détection de longs weekends (férié lundi, crèche fermée vendredi)</li>
              <li>Suggestions raisonnables selon le budget et la durée</li>
            </ul>
            <p className="pt-2">
              Les suggestions sont optimales à partir du jeudi, lorsque la météo du weekend
              devient plus fiable.
            </p>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
