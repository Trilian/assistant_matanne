"use client";

import { useState } from "react";
import { Loader2, MessageSquare, Send } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/composants/ui/card";
import { Button } from "@/composants/ui/button";
import { Input } from "@/composants/ui/input";
import { Label } from "@/composants/ui/label";
import { envoyerNotificationTest } from "@/bibliotheque/api/admin";

export default function PageAdminTelegramTest() {
  const [numero, setNumero] = useState("");
  const [message, setMessage] = useState("Test Telegram depuis l'admin Matanne.");
  const [envoiEnCours, setEnvoiEnCours] = useState(false);
  const [retour, setRetour] = useState<{ ok: boolean; message: string } | null>(null);

  const envoyer = async () => {
    setEnvoiEnCours(true);
    setRetour(null);
    try {
      const data = await envoyerNotificationTest({
        canal: "telegram",
        message,
        titre: "Test Telegram",
        numero_destinataire: numero || undefined,
      });
      setRetour({ ok: true, message: data.message });
    } catch (err: unknown) {
      const detail =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ??
        "Echec envoi Telegram";
      setRetour({ ok: false, message: detail });
    } finally {
      setEnvoiEnCours(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight flex items-center gap-2">
          <MessageSquare className="h-6 w-6" />
          Telegram Test
        </h1>
        <p className="text-muted-foreground">Envoi d'un message test vers un chat Telegram specifique.</p>
      </div>

      <Card className="max-w-xl">
        <CardHeader>
          <CardTitle>Message de test</CardTitle>
          <CardDescription>Si le destinataire est vide, le backend utilise TELEGRAM_CHAT_ID.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="space-y-1">
            <Label htmlFor="numero-telegram">Chat destinataire</Label>
            <Input
              id="numero-telegram"
              value={numero}
              onChange={(e) => setNumero(e.target.value)}
              placeholder="123456789"
            />
          </div>
          <div className="space-y-1">
            <Label htmlFor="message-telegram">Message</Label>
            <Input id="message-telegram" value={message} onChange={(e) => setMessage(e.target.value)} />
          </div>
          <Button onClick={envoyer} disabled={envoiEnCours || !message.trim()}>
            {envoiEnCours ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Send className="mr-2 h-4 w-4" />}
            Envoyer
          </Button>
          {retour && (
            <p className={`text-sm ${retour.ok ? "text-green-600" : "text-red-600"}`}>{retour.message}</p>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
