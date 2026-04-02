// ═══════════════════════════════════════════════════════════
// Hub Outils
// ═══════════════════════════════════════════════════════════

"use client";

import Link from "next/link";
import {
  Sparkles,
  StickyNote,
  CloudSun,
  Timer,
  ArrowRightLeft,
  Mic,
  Bot,
} from "lucide-react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/composants/ui/card";
import { Switch } from "@/composants/ui/switch";
import { Badge } from "@/composants/ui/badge";
import { toast } from "sonner";
import { utiliserMutation, utiliserRequete } from "@/crochets/utiliser-api";
import { configurerModePiloteAuto, obtenirModePiloteAuto } from "@/bibliotheque/api/avance";

const SECTIONS = [
  { titre: "Chat IA", description: "Assistant intelligent", chemin: "/outils/chat-ia", Icone: Sparkles },
  { titre: "Assistant vocal", description: "Commandes à la voix", chemin: "/outils/assistant-vocal", Icone: Mic },
  { titre: "Google Assistant", description: "Tester intents/actions", chemin: "/outils/google-assistant", Icone: Sparkles },
  { titre: "Notes", description: "Bloc-notes rapide", chemin: "/outils/notes", Icone: StickyNote },
  { titre: "Météo", description: "Prévisions locales", chemin: "/outils/meteo", Icone: CloudSun },
  { titre: "Minuteur", description: "Chronomètre cuisine", chemin: "/outils/minuteur", Icone: Timer },
  { titre: "Convertisseur", description: "Unités de mesure", chemin: "/outils/convertisseur", Icone: ArrowRightLeft },
];

export default function PageOutils() {
  const { data: modePilote, refetch: rechargerModePilote } = utiliserRequete(
    ["avance", "mode-pilote", "outils"],
    obtenirModePiloteAuto,
    { staleTime: 60 * 1000 }
  );

  const { mutate: basculerModePilote, isPending: basculeModePiloteEnCours } = utiliserMutation(
    (actif: boolean) =>
      configurerModePiloteAuto({
        actif,
        niveau_autonomie: actif ? modePilote?.niveau_autonomie ?? "validation_requise" : "off",
      }),
    {
      onSuccess: (data) => {
        toast.success(data.actif ? "Mode pilote activé" : "Mode pilote désactivé");
        void rechargerModePilote();
      },
      onError: () => {
        toast.error("Impossible de mettre à jour le mode pilote");
      },
    }
  );

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">🔧 Outils</h1>
        <p className="text-muted-foreground">
          Chat IA, notes, météo et utilitaires
        </p>
      </div>

      <Card className="border-sky-300/60 bg-sky-50/50 dark:border-sky-900/50 dark:bg-sky-950/20">
        <CardHeader className="pb-2">
          <CardTitle className="text-base flex items-center gap-2">
            <Bot className="h-4 w-4 text-sky-600" />
            Mode Pilote Automatique
          </CardTitle>
          <CardDescription>
            Pilotage IA centralisé côté outils.
          </CardDescription>
        </CardHeader>
        <CardContent className="flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-center gap-2">
            <Badge variant="outline">Niveau: {modePilote?.niveau_autonomie ?? "validation_requise"}</Badge>
            <span className="text-xs text-muted-foreground">Actions: {modePilote?.actions?.length ?? 0}</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-sm">Actif</span>
            <Switch
              checked={Boolean(modePilote?.actif)}
              disabled={basculeModePiloteEnCours}
              onCheckedChange={(actif) => basculerModePilote(actif)}
            />
          </div>
        </CardContent>
      </Card>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {SECTIONS.map(({ titre, description, chemin, Icone }) => (
          <Link key={chemin} href={chemin}>
            <Card className="hover:bg-accent/50 transition-colors h-full">
              <CardHeader>
                <div className="flex items-center gap-3">
                  <div className="rounded-lg bg-primary/10 p-2">
                    <Icone className="h-5 w-5 text-primary" />
                  </div>
                  <div>
                    <CardTitle className="text-base">{titre}</CardTitle>
                    <CardDescription className="text-sm">{description}</CardDescription>
                  </div>
                </div>
              </CardHeader>
            </Card>
          </Link>
        ))}
      </div>
    </div>
  );
}
