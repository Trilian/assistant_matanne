// ═══════════════════════════════════════════════════════════
// CarteConseil — Carte conseil IA actionnable pour le hub Maison
// Phase 0B
// ═══════════════════════════════════════════════════════════

"use client";

import { ArrowRight, Calendar, X } from "lucide-react";
import { useRouter } from "next/navigation";
import { Card, CardContent } from "@/composants/ui/card";
import { Badge } from "@/composants/ui/badge";
import { Button } from "@/composants/ui/button";
import { utiliserMutation } from "@/crochets/utiliser-api";
import { creerTacheEntretien } from "@/bibliotheque/api/maison";
import { BoutonAchat } from "@/composants/bouton-achat";
import type { ConseilMaisonHub } from "@/types/maison";
import { toast } from "sonner";

const COULEURS_NIVEAU: Record<string, string> = {
  urgent: "border-l-4 border-l-destructive bg-destructive/5",
  warning: "border-l-4 border-l-amber-400 bg-amber-50/50 dark:bg-amber-950/20",
  info: "border-l-4 border-l-muted-foreground/30",
};

const BADGE_VARIANT: Record<string, "destructive" | "secondary" | "outline"> = {
  urgent: "destructive",
  warning: "secondary",
  info: "outline",
};

const LABELS_MODULE: Record<string, string> = {
  travaux: "Travaux",
  finances: "Finances",
  provisions: "Provisions",
  jardin: "Jardin",
  documents: "Documents",
  equipements: "Équipements",
  menage: "Ménage",
  general: "Maison",
};

interface CarteConseilProps {
  conseil: ConseilMaisonHub;
  onDismiss: () => void;
}

const SNOOZE_MS = 7 * 24 * 60 * 60 * 1000; // 7 jours

function hashConseil(conseil: ConseilMaisonHub): string {
  return btoa(encodeURIComponent(conseil.titre)).replace(/[^a-zA-Z0-9]/g, "").slice(0, 20);
}

export function estDismissed(conseil: ConseilMaisonHub): boolean {
  if (typeof window === "undefined") return false;
  const key = `conseil_dismiss_${hashConseil(conseil)}`;
  const val = localStorage.getItem(key);
  if (!val) return false;
  return Date.now() < Number(val);
}

export function CarteConseil({ conseil, onDismiss }: CarteConseilProps) {
  const router = useRouter();

  const { mutate: planifierEntretien, isPending: planification } = utiliserMutation(
    () =>
      creerTacheEntretien({
        nom: conseil.action_payload.nom ?? conseil.titre,
        categorie: conseil.action_payload.categorie ?? conseil.module_source,
        fait: false,
      }),
    {
      onSuccess: () => toast.success("Tâche ajoutée à l'entretien"),
    }
  );

  const handleDismiss = () => {
    if (typeof window !== "undefined") {
      const key = `conseil_dismiss_${hashConseil(conseil)}`;
      localStorage.setItem(key, String(Date.now() + SNOOZE_MS));
    }
    onDismiss();
  };

  return (
    <Card className={`relative ${COULEURS_NIVEAU[conseil.niveau] ?? ""}`}>
      <CardContent className="py-3 pr-8">
        <div className="flex items-start gap-2">
          <span className="text-base shrink-0">{conseil.icone || "💡"}</span>
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 flex-wrap">
              <p className="text-sm font-medium leading-tight">{conseil.titre}</p>
              <Badge variant={BADGE_VARIANT[conseil.niveau] ?? "outline"} className="text-xs">
                {LABELS_MODULE[conseil.module_source] ?? conseil.module_source}
              </Badge>
            </div>
            {conseil.description && (
              <p className="text-xs text-muted-foreground mt-1">{conseil.description}</p>
            )}
            <div className="flex items-center gap-2 mt-2 flex-wrap">
              {conseil.action_type === "voir" && conseil.action_payload.chemin && (
                <Button
                  variant="outline"
                  size="sm"
                  className="h-6 px-2 text-xs"
                  onClick={() => router.push(conseil.action_payload.chemin!)}
                >
                  <ArrowRight className="h-3 w-3 mr-1" />
                  Voir
                </Button>
              )}
              {conseil.action_type === "planifier_entretien" && (
                <Button
                  variant="outline"
                  size="sm"
                  className="h-6 px-2 text-xs"
                  disabled={planification}
                  onClick={() => planifierEntretien()}
                >
                  <Calendar className="h-3 w-3 mr-1" />
                  Planifier
                </Button>
              )}
              {conseil.action_type === "acheter" && conseil.action_payload.nom && (
                <BoutonAchat
                  article={{ nom: conseil.action_payload.nom }}
                  taille="xs"
                />
              )}
            </div>
          </div>
        </div>
      </CardContent>
      <button
        onClick={handleDismiss}
        className="absolute top-2 right-2 h-5 w-5 rounded-sm flex items-center justify-center text-muted-foreground hover:text-foreground transition-colors"
        aria-label="Ignorer ce conseil"
      >
        <X className="h-3 w-3" />
      </button>
    </Card>
  );
}
