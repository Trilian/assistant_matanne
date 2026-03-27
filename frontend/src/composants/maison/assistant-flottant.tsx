// ─── AssistantFlottant ─────────────────────────────────────
// Bouton flottant 🤖 en bas à droite, ouvre une Sheet latérale
// pour un chat IA contextuel Maison.
"use client";

import { useState, useRef, useEffect } from "react";
import { Bot, X, Send, Loader2, Sparkles } from "lucide-react";
import { Button } from "@/composants/ui/button";
import { Input } from "@/composants/ui/input";
import { ScrollArea } from "@/composants/ui/scroll-area";

interface Message {
  role: "user" | "assistant";
  contenu: string;
}

const SUGGESTIONS = [
  "Que dois-je faire cette semaine dans la maison ?",
  "Quels travaux prévoir avant l'hiver ?",
  "Analyse mes dépenses du mois",
  "Rappelle-moi les contrats qui expirent bientôt",
];

export function AssistantFlottant() {
  const [ouvert, setOuvert] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [saisie, setSaisie] = useState("");
  const [enAttente, setEnAttente] = useState(false);
  const finRef = useRef<HTMLDivElement>(null);

  // Scroll auto vers le bas à chaque nouveau message
  useEffect(() => {
    finRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, enAttente]);

  const envoyer = async (texte?: string) => {
    const question = texte ?? saisie.trim();
    if (!question) return;

    setSaisie("");
    setMessages((m) => [...m, { role: "user", contenu: question }]);
    setEnAttente(true);

    try {
      const res = await fetch("/api/v1/maison/assistant/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: question, contexte: "maison" }),
      });

      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const json = await res.json();
      const reponse: string = json.reponse ?? json.message ?? "Désolé, je n'ai pas compris.";
      setMessages((m) => [...m, { role: "assistant", contenu: reponse }]);
    } catch {
      setMessages((m) => [...m, { role: "assistant", contenu: "Une erreur est survenue. Veuillez réessayer." }]);
    } finally {
      setEnAttente(false);
    }
  };

  return (
    <>
      {/* Bouton flottant */}
      <button
        type="button"
        onClick={() => setOuvert((o) => !o)}
        className="fixed bottom-6 right-6 z-50 h-12 w-12 rounded-full bg-violet-600 hover:bg-violet-700 shadow-lg flex items-center justify-center text-white transition-all hover:scale-105 active:scale-95"
        aria-label="Assistant IA Maison"
      >
        {ouvert ? <X className="h-5 w-5" /> : <Bot className="h-5 w-5" />}
      </button>

      {/* Panel chat */}
      {ouvert && (
        <div className="fixed bottom-20 right-6 z-50 w-80 max-h-[70vh] bg-background border rounded-xl shadow-2xl flex flex-col overflow-hidden">
          {/* En-tête */}
          <div className="flex items-center gap-2 px-4 py-3 bg-violet-600 text-white">
            <Sparkles className="h-4 w-4" />
            <span className="text-sm font-semibold">Assistant Maison</span>
            <Button
              variant="ghost"
              size="icon"
              className="h-6 w-6 ml-auto text-white hover:bg-violet-700"
              onClick={() => setOuvert(false)}
            >
              <X className="h-4 w-4" />
            </Button>
          </div>

          {/* Messages */}
          <ScrollArea className="flex-1 p-3">
            {messages.length === 0 ? (
              <div className="space-y-2">
                <p className="text-xs text-muted-foreground text-center mb-3">
                  Bonjour ! Je suis votre assistant maison. Posez-moi vos questions.
                </p>
                {SUGGESTIONS.map((s) => (
                  <button
                    key={s}
                    type="button"
                    className="w-full text-left text-xs px-3 py-2 rounded-lg bg-muted hover:bg-muted/80 transition-colors"
                    onClick={() => envoyer(s)}
                  >
                    {s}
                  </button>
                ))}
              </div>
            ) : (
              <div className="space-y-3">
                {messages.map((m, i) => (
                  <div
                    key={i}
                    className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}
                  >
                    <div
                      className={`max-w-[85%] rounded-xl px-3 py-2 text-xs ${
                        m.role === "user"
                          ? "bg-violet-600 text-white rounded-br-none"
                          : "bg-muted rounded-bl-none"
                      }`}
                    >
                      {m.contenu}
                    </div>
                  </div>
                ))}
                {enAttente && (
                  <div className="flex justify-start">
                    <div className="bg-muted rounded-xl rounded-bl-none px-3 py-2">
                      <Loader2 className="h-3.5 w-3.5 animate-spin text-muted-foreground" />
                    </div>
                  </div>
                )}
                <div ref={finRef} />
              </div>
            )}
          </ScrollArea>

          {/* Saisie */}
          <div className="flex gap-2 p-3 border-t">
            <Input
              value={saisie}
              onChange={(e) => setSaisie(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && envoyer()}
              placeholder="Posez votre question…"
              className="text-xs h-8"
              disabled={enAttente}
            />
            <Button
              size="icon"
              className="h-8 w-8 shrink-0 bg-violet-600 hover:bg-violet-700"
              onClick={() => envoyer()}
              disabled={enAttente || !saisie.trim()}
            >
              {enAttente ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <Send className="h-3.5 w-3.5" />}
            </Button>
          </div>
        </div>
      )}
    </>
  );
}
