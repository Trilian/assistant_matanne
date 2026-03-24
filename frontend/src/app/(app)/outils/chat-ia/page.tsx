"use client";

import { useState, useRef, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Skeleton } from "@/components/ui/skeleton";
import { utiliserMutation } from "@/crochets/utiliser-api";
import { obtenirSuggestionsRecettes } from "@/bibliotheque/api/outils";
import type { MessageChat } from "@/types/outils";
import { toast } from "sonner";

export default function ChatIAPage() {
  const [messages, setMessages] = useState<MessageChat[]>([]);
  const [saisie, setSaisie] = useState("");
  const refScroll = useRef<HTMLDivElement>(null);

  const { mutate: envoyer, isPending } = utiliserMutation(
    async (question: string) => {
      const suggestions = await obtenirSuggestionsRecettes(question, 3);
      return suggestions;
    },
    {
      onSuccess: (suggestions: string[]) => {
        const reponse = suggestions.length > 0
          ? `Voici mes suggestions :\n\n${suggestions.map((s, i) => `${i + 1}. ${s}`).join("\n")}`
          : "Je n'ai pas de suggestion pour le moment.";

        setMessages((prev) => [
          ...prev,
          {
            role: "assistant",
            contenu: reponse,
            horodatage: new Date().toISOString(),
          },
        ]);
      },
      onError: () => toast.error("Erreur lors de l'envoi"),
    }
  );

  useEffect(() => {
    refScroll.current?.scrollTo({ top: refScroll.current.scrollHeight, behavior: "smooth" });
  }, [messages]);

  function gererEnvoi(e: React.FormEvent) {
    e.preventDefault();
    const texte = saisie.trim();
    if (!texte || isPending) return;

    setMessages((prev) => [
      ...prev,
      { role: "user", contenu: texte, horodatage: new Date().toISOString() },
    ]);
    setSaisie("");
    envoyer(texte);
  }

  return (
    <div className="flex flex-col h-[calc(100vh-12rem)]">
      <h1 className="text-3xl font-bold mb-4">🤖 Chat IA</h1>

      <Card className="flex-1 flex flex-col overflow-hidden">
        <CardHeader className="pb-2">
          <CardTitle className="text-base">
            Assistant culinaire — posez vos questions !
          </CardTitle>
        </CardHeader>
        <CardContent className="flex-1 flex flex-col overflow-hidden p-0">
          <ScrollArea ref={refScroll} className="flex-1 px-4">
            {messages.length === 0 ? (
              <div className="flex items-center justify-center h-full py-16">
                <p className="text-muted-foreground text-center">
                  Demandez des suggestions de recettes, des idées de menus…
                </p>
              </div>
            ) : (
              <div className="space-y-4 py-4">
                {messages.map((m, i) => (
                  <div
                    key={i}
                    className={`flex ${
                      m.role === "user" ? "justify-end" : "justify-start"
                    }`}
                  >
                    <div
                      className={`max-w-[80%] rounded-xl px-4 py-2 whitespace-pre-wrap ${
                        m.role === "user"
                          ? "bg-primary text-primary-foreground"
                          : "bg-muted"
                      }`}
                    >
                      {m.contenu}
                    </div>
                  </div>
                ))}
                {isPending && (
                  <div className="flex justify-start">
                    <Skeleton className="h-10 w-48 rounded-xl" />
                  </div>
                )}
              </div>
            )}
          </ScrollArea>

          <form onSubmit={gererEnvoi} className="flex gap-2 p-4 border-t">
            <Input
              value={saisie}
              onChange={(e) => setSaisie(e.target.value)}
              placeholder="Ex: Que faire avec du poulet et des courgettes ?"
              disabled={isPending}
            />
            <Button type="submit" disabled={isPending || !saisie.trim()}>
              Envoyer
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
