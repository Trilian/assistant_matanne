// ═══════════════════════════════════════════════════════════
// Journal — Journal familial
// ═══════════════════════════════════════════════════════════

"use client";

import { useState } from "react";
import { BookOpen, Plus, Calendar, Smile, Meh, Frown } from "lucide-react";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";

interface EntreeJournal {
  id: number;
  titre: string;
  contenu: string;
  date: string;
  humeur: "bien" | "neutre" | "difficile";
}

const HUMEURS = [
  { value: "bien" as const, label: "Bien", icone: Smile, couleur: "text-green-500" },
  { value: "neutre" as const, label: "Neutre", icone: Meh, couleur: "text-yellow-500" },
  { value: "difficile" as const, label: "Difficile", icone: Frown, couleur: "text-red-500" },
];

export default function PageJournal() {
  const [entrees, setEntrees] = useState<EntreeJournal[]>([
    {
      id: 1,
      titre: "Premier jour de crèche",
      contenu:
        "Jules a passé sa première journée complète à la crèche. Il a bien mangé et fait une sieste.",
      date: new Date().toISOString().split("T")[0],
      humeur: "bien",
    },
  ]);
  const [ouvert, setOuvert] = useState(false);
  const [titre, setTitre] = useState("");
  const [contenu, setContenu] = useState("");
  const [humeur, setHumeur] = useState<EntreeJournal["humeur"]>("bien");

  function ajouterEntree() {
    if (!titre.trim() || !contenu.trim()) return;
    setEntrees((prev) => [
      {
        id: Date.now(),
        titre: titre.trim(),
        contenu: contenu.trim(),
        date: new Date().toISOString().split("T")[0],
        humeur,
      },
      ...prev,
    ]);
    setTitre("");
    setContenu("");
    setHumeur("bien");
    setOuvert(false);
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">
            📝 Journal familial
          </h1>
          <p className="text-muted-foreground">
            Souvenirs et moments du quotidien
          </p>
        </div>
        <Dialog open={ouvert} onOpenChange={setOuvert}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="mr-2 h-4 w-4" />
              Nouvelle entrée
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Ajouter une entrée</DialogTitle>
            </DialogHeader>
            <div className="space-y-4 pt-2">
              <Input
                placeholder="Titre"
                value={titre}
                onChange={(e) => setTitre(e.target.value)}
              />
              <Textarea
                placeholder="Racontez votre journée..."
                value={contenu}
                onChange={(e) => setContenu(e.target.value)}
                rows={4}
              />
              <div>
                <p className="text-sm font-medium mb-2">Humeur du jour</p>
                <div className="flex gap-3">
                  {HUMEURS.map((h) => {
                    const Icone = h.icone;
                    return (
                      <button
                        key={h.value}
                        type="button"
                        onClick={() => setHumeur(h.value)}
                        className={`flex flex-col items-center gap-1 rounded-lg border p-3 transition-colors ${
                          humeur === h.value
                            ? "border-primary bg-primary/10"
                            : "border-transparent hover:bg-accent"
                        }`}
                      >
                        <Icone className={`h-6 w-6 ${h.couleur}`} />
                        <span className="text-xs">{h.label}</span>
                      </button>
                    );
                  })}
                </div>
              </div>
              <Button onClick={ajouterEntree} className="w-full">
                Enregistrer
              </Button>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      {/* Timeline */}
      {entrees.length === 0 ? (
        <Card>
          <CardContent className="flex flex-col items-center gap-2 py-10 text-muted-foreground">
            <BookOpen className="h-8 w-8 opacity-50" />
            Commencez à écrire votre journal familial
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-4">
          {entrees.map((entree) => {
            const humeurInfo = HUMEURS.find((h) => h.value === entree.humeur);
            const HumeurIcone = humeurInfo?.icone ?? Smile;
            return (
              <Card key={entree.id}>
                <CardHeader className="pb-2">
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-base">{entree.titre}</CardTitle>
                    <div className="flex items-center gap-2">
                      <HumeurIcone
                        className={`h-4 w-4 ${humeurInfo?.couleur}`}
                      />
                      <Badge variant="secondary" className="text-xs">
                        <Calendar className="mr-1 h-3 w-3" />
                        {new Date(entree.date).toLocaleDateString("fr-FR", {
                          day: "numeric",
                          month: "short",
                        })}
                      </Badge>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-muted-foreground whitespace-pre-line">
                    {entree.contenu}
                  </p>
                </CardContent>
              </Card>
            );
          })}
        </div>
      )}
    </div>
  );
}
