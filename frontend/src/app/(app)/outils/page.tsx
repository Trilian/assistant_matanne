// ═══════════════════════════════════════════════════════════
// Hub Outils
// ═══════════════════════════════════════════════════════════

import Link from "next/link";
import {
  Sparkles,
  StickyNote,
  CloudSun,
  Timer,
  ArrowRightLeft,
  Mic,
} from "lucide-react";
import {
  Card,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/composants/ui/card";

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
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">🔧 Outils</h1>
        <p className="text-muted-foreground">
          Chat IA, notes, météo et utilitaires
        </p>
      </div>

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
