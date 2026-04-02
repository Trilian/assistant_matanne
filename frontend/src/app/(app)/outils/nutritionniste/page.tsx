"use client";

import { useState, useRef, useEffect } from "react";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/composants/ui/card";
import { Button } from "@/composants/ui/button";
import { Input } from "@/composants/ui/input";
import { ScrollArea } from "@/composants/ui/scroll-area";
import { Skeleton } from "@/composants/ui/skeleton";
import {
  Apple,
  Bot,
  Send,
  Loader2,
  AlertCircle,
  TrendingUp,
  Flame,
  Beef,
  Droplets,
  Wheat,
} from "lucide-react";
import { utiliserMutation, utiliserRequete } from "@/crochets/utiliser-api";
import {
  envoyerMessageChat,
} from "@/bibliotheque/api/outils";
import { obtenirNutritionHebdo } from "@/bibliotheque/api/planning";
import type { MessageChat } from "@/types/outils";
import { toast } from "sonner";
import { BoutonVocal } from "@/composants/ui/bouton-vocal";

const ACTIONS_RAPIDES_NUTRITION = [
  { label: "Analyser mon repas", message: "Analyse la valeur nutritionnelle de ce repas pour moi" },
  { label: "Équilibre de la semaine", message: "Comment équilibrer mon planning repas cette semaine ?" },
  { label: "Astuces pour Jules", message: "Conseils nutrition pour un enfant de 3 ans qui refuse les légumes" },
  { label: "Réduire sucre ajouté", message: "Comment réduire le sucre dans mes recettes familiales ?" },
];

export default function NutritionistePage() {
  const [messages, setMessages] = useState<MessageChat[]>([]);
  const [saisie, setSaisie] = useState("");
  const scrollRef = useRef<HTMLDivElement>(null);

  const { data: nutrition, isLoading: chargementNutri } = utiliserRequete(
    ["planning", "nutrition-hebdo"],
    () => obtenirNutritionHebdo()
  );

  const { mutate: envoyer, isPending } = utiliserMutation(
    (message: string) =>
      envoyerMessageChat({
        message,
        contexte: "cuisine",
        historique: messages,
      }),
    {
      onSuccess: (data: { reponse: string }) => {
        setMessages((prev) => [
          ...prev,
          { role: "assistant", contenu: data.reponse, horodatage: new Date().toISOString() },
        ]);
      },
      onError: () => toast.error("Erreur lors de la communication avec le nutritionniste IA"),
    }
  );

  useEffect(() => {
    if (scrollRef.current && typeof scrollRef.current.scrollIntoView === "function") {
      scrollRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages]);

  function gererEnvoi(e: React.FormEvent) {
    e.preventDefault();
    if (!saisie.trim() || isPending) return;
    const message = saisie.trim();
    setMessages((prev) => [...prev, { role: "user", contenu: message, horodatage: new Date().toISOString() }]);
    setSaisie("");
    envoyer(message);
  }

  function gererActionRapide(msg: string) {
    setMessages((prev) => [...prev, { role: "user", contenu: msg, horodatage: new Date().toISOString() }]);
    envoyer(msg);
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">
          🥗 Nutritionniste IA
        </h1>
        <p className="text-muted-foreground">
          Conseils personnalisés en nutrition pour votre famille
        </p>
      </div>

      <div className="rounded-lg border bg-amber-50 dark:bg-amber-950 border-amber-200 dark:border-amber-800 p-3 flex gap-2 text-sm">
        <AlertCircle className="h-4 w-4 text-amber-600 mt-0.5 shrink-0" />
        <span className="text-amber-800 dark:text-amber-200">
          Cet assistant fournit des informations générales. Pour un suivi médical personnalisé, consultez un diététicien-nutritionniste.
        </span>
      </div>

      {/* Dashboard nutrition semaine en cours */}
      {chargementNutri ? (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          {[1, 2, 3, 4].map((i) => (
            <Card key={i}><CardContent className="pt-4"><Skeleton className="h-12 w-full" /></CardContent></Card>
          ))}
        </div>
      ) : nutrition ? (
        <div className="space-y-3">
          <h2 className="text-base font-semibold flex items-center gap-2">
            <TrendingUp className="h-4 w-4 text-green-500" />
            Semaine en cours — moyennes journalières
          </h2>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            <Card>
              <CardContent className="pt-4">
                <div className="flex items-center gap-2">
                  <Flame className="h-4 w-4 text-orange-500" />
                  <p className="text-xs text-muted-foreground">Calories</p>
                </div>
                <p className="text-2xl font-bold mt-1">
                  {Math.round(nutrition.moyenne_calories_par_jour ?? 0)}
                </p>
                <p className="text-xs text-muted-foreground">kcal/jour</p>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="pt-4">
                <div className="flex items-center gap-2">
                  <Beef className="h-4 w-4 text-red-500" />
                  <p className="text-xs text-muted-foreground">Protéines</p>
                </div>
                <p className="text-2xl font-bold mt-1">
                  {Math.round((nutrition.totaux?.proteines ?? 0) / 7)}
                </p>
                <p className="text-xs text-muted-foreground">g/jour</p>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="pt-4">
                <div className="flex items-center gap-2">
                  <Droplets className="h-4 w-4 text-yellow-500" />
                  <p className="text-xs text-muted-foreground">Lipides</p>
                </div>
                <p className="text-2xl font-bold mt-1">
                  {Math.round((nutrition.totaux?.lipides ?? 0) / 7)}
                </p>
                <p className="text-xs text-muted-foreground">g/jour</p>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="pt-4">
                <div className="flex items-center gap-2">
                  <Wheat className="h-4 w-4 text-amber-500" />
                  <p className="text-xs text-muted-foreground">Glucides</p>
                </div>
                <p className="text-2xl font-bold mt-1">
                  {Math.round((nutrition.totaux?.glucides ?? 0) / 7)}
                </p>
                <p className="text-xs text-muted-foreground">g/jour</p>
              </CardContent>
            </Card>
          </div>
          {nutrition.nb_repas_sans_donnees != null && nutrition.nb_repas_sans_donnees > 0 && (
            <p className="text-xs text-muted-foreground">
              ⚠️ {nutrition.nb_repas_sans_donnees} repas sans données nutritionnelles cette semaine.
            </p>
          )}
          {/* Répartition par jour */}
          {nutrition.par_jour && Object.keys(nutrition.par_jour).length > 0 && (
            <div className="grid grid-cols-7 gap-1">
              {["lun", "mar", "mer", "jeu", "ven", "sam", "dim"].map((jour, idx) => {
                const jours = Object.entries(nutrition.par_jour);
                const entry = jours[idx];
                const cal = entry ? Math.round((entry[1] as { calories?: number }).calories ?? 0) : 0;
                const maxCal = 2500;
                const pct = Math.min(100, Math.round((cal / maxCal) * 100));
                return (
                  <div key={jour} className="flex flex-col items-center gap-1">
                    <div className="w-full bg-muted rounded-full overflow-hidden h-16 flex items-end">
                      <div
                        className="w-full bg-orange-400 rounded-t"
                        style={{ height: `${pct}%` }}
                      />
                    </div>
                    <span className="text-xs text-muted-foreground">{jour}</span>
                    <span className="text-xs font-medium">{cal > 0 ? cal : "—"}</span>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      ) : null}

      <Card className="flex flex-col" style={{ height: "65vh" }}>
        <CardHeader className="pb-2">
          <CardTitle className="flex items-center gap-2 text-base">
            <Apple className="h-5 w-5 text-green-500" />
            Chat Nutritionniste
          </CardTitle>
        </CardHeader>

        <CardContent className="flex-1 overflow-hidden flex flex-col gap-3 p-4">
          {/* Actions rapides */}
          {messages.length === 0 && (
            <div className="flex flex-wrap gap-2">
              {ACTIONS_RAPIDES_NUTRITION.map((a) => (
                <Button
                  key={a.label}
                  variant="outline"
                  size="sm"
                  className="text-xs h-8"
                  onClick={() => gererActionRapide(a.message)}
                  disabled={isPending}
                >
                  {a.label}
                </Button>
              ))}
            </div>
          )}

          {/* Messages */}
          <ScrollArea className="flex-1">
            <div className="space-y-4 pr-3">
              {messages.length === 0 && (
                <div className="flex items-center gap-3 text-muted-foreground text-sm py-8 justify-center">
                  <Bot className="h-6 w-6" />
                  Bonjour ! Je suis votre nutritionniste IA. Comment puis-je vous aider ?
                </div>
              )}
              {messages.map((msg, i) => (
                <div
                  key={i}
                  className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
                >
                  <div
                    className={`max-w-[80%] rounded-lg px-4 py-2 text-sm ${
                      msg.role === "user"
                        ? "bg-primary text-primary-foreground"
                        : "bg-muted"
                    }`}
                  >
                    {msg.contenu}
                  </div>
                </div>
              ))}
              {isPending && (
                <div className="flex justify-start">
                  <div className="bg-muted rounded-lg px-4 py-2">
                    <Skeleton className="h-4 w-32" />
                  </div>
                </div>
              )}
              <div ref={scrollRef} />
            </div>
          </ScrollArea>

          {/* Input */}
          <form onSubmit={gererEnvoi} className="flex gap-2">
            <BoutonVocal
              onResultat={(texte) =>
                setSaisie((prev) => (prev ? `${prev} ${texte}` : texte))
              }
              placeholder="Dicter votre question"
            />
            <Input
              value={saisie}
              onChange={(e) => setSaisie(e.target.value)}
              placeholder="Posez votre question sur la nutrition..."
              disabled={isPending}
            />
            <Button
              type="submit"
              disabled={isPending || !saisie.trim()}
              size="icon"
              aria-label="Envoyer"
            >
              {isPending ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Send className="h-4 w-4" />
              )}
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
