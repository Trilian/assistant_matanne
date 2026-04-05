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
  Brain,
  BarChart3,
} from "lucide-react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/composants/ui/card";
import { Badge } from "@/composants/ui/badge";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/composants/ui/select";
import { toast } from "sonner";
import { ItemAnime, SectionReveal } from "@/composants/ui/motion-utils";
import { utiliserMutation, utiliserRequete } from "@/crochets/utiliser-api";
import { configurerModePiloteAuto, obtenirModePiloteAuto } from "@/bibliotheque/api/avance";

const SECTIONS = [
  { titre: "Chat IA", description: "Assistant intelligent", chemin: "/outils/chat-ia", Icone: Sparkles },
  { titre: "Préférences IA", description: "Ce que l'IA a appris des goûts famille", chemin: "/outils/preferences-apprises", Icone: Brain },
  { titre: "Assistant vocal", description: "Commandes à la voix", chemin: "/outils/assistant-vocal", Icone: Mic },
  { titre: "Google Assistant", description: "Tester intents/actions", chemin: "/outils/google-assistant", Icone: Sparkles },
  { titre: "Notes", description: "Bloc-notes rapide", chemin: "/outils/notes", Icone: StickyNote },
  { titre: "Météo", description: "Prévisions locales", chemin: "/outils/meteo", Icone: CloudSun },
  { titre: "Minuteur", description: "Chronomètre cuisine", chemin: "/outils/minuteur", Icone: Timer },
  { titre: "Convertisseur", description: "Unités de mesure", chemin: "/outils/convertisseur", Icone: ArrowRightLeft },
  { titre: "Insights IA", description: "Ma famille en chiffres", chemin: "/outils/insights", Icone: BarChart3 },
];

export default function PageOutils() {
  const { data: modePilote, refetch: rechargerModePilote } = utiliserRequete(
    ["avance", "mode-pilote", "outils"],
    obtenirModePiloteAuto,
    { staleTime: 60 * 1000 }
  );

  const { mutate: changerNiveau, isPending: changementEnCours } = utiliserMutation(
    (niveau: string) =>
      configurerModePiloteAuto({
        actif: niveau !== "off",
        niveau_autonomie: niveau,
      }),
    {
      onSuccess: (data) => {
        const labels: Record<string, string> = {
          off: "Mode pilote désactivé",
          proposee: "Mode propositions activé",
          validation_requise: "Mode validation activé",
          semi_auto: "Mode semi-auto activé",
          auto: "Mode automatique activé",
        };
        toast.success(labels[data.niveau_autonomie] ?? "Mode pilote mis à jour");
        void rechargerModePilote();
      },
      onError: () => {
        toast.error("Impossible de mettre à jour le mode pilote");
      },
    }
  );

  return (
    <div className="space-y-6">
      <SectionReveal>
        <div>
          <h1 className="text-2xl font-bold tracking-tight">🔧 Outils</h1>
          <p className="text-muted-foreground">
            Chat IA, notes, météo et utilitaires
          </p>
        </div>
      </SectionReveal>

      <SectionReveal delay={0.04}>
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
          <CardContent className="space-y-3">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <Select
                value={modePilote?.niveau_autonomie ?? "validation_requise"}
                disabled={changementEnCours}
                onValueChange={(v) => changerNiveau(v)}
              >
                <SelectTrigger className="w-[220px]">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="off">⏹️ Désactivé</SelectItem>
                  <SelectItem value="proposee">💡 Propositions seules</SelectItem>
                  <SelectItem value="validation_requise">✅ Validation requise</SelectItem>
                  <SelectItem value="semi_auto">⚡ Semi-auto (faible risque)</SelectItem>
                  <SelectItem value="auto">🤖 Tout automatique</SelectItem>
                </SelectContent>
              </Select>
              <span className="text-xs text-muted-foreground">
                {modePilote?.actions?.length ?? 0} action(s) en attente
              </span>
            </div>
            {(modePilote?.actions?.length ?? 0) > 0 && (
              <div className="space-y-1.5">
                {modePilote!.actions.map((a, i) => (
                  <div key={i} className="flex items-center gap-2 text-xs">
                    <Badge
                      variant={a.statut === "auto" ? "default" : "outline"}
                      className="text-[10px] px-1.5"
                    >
                      {a.statut}
                    </Badge>
                    <span className="text-muted-foreground">{a.details}</span>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </SectionReveal>

      <SectionReveal delay={0.08} className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {SECTIONS.map(({ titre, description, chemin, Icone }, index) => (
          <ItemAnime key={chemin} index={index}>
            <Link href={chemin}>
              <Card className="h-full transition-all hover:-translate-y-0.5 hover:bg-accent/50 hover:shadow-md">
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
          </ItemAnime>
        ))}
      </SectionReveal>
    </div>
  );
}
