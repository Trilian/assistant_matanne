// ═══════════════════════════════════════════════════════════
// Page Achats Famille — Phase P
// ═══════════════════════════════════════════════════════════

"use client";

import { useState } from "react";
import { Plus, Trash2, Check, Sparkles, ShoppingCart } from "lucide-react";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from "@/composants/ui/card";
import { Button } from "@/composants/ui/button";
import { Badge } from "@/composants/ui/badge";
import { Input } from "@/composants/ui/input";
import { Textarea } from "@/composants/ui/textarea";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/composants/ui/dialog";
import { Label } from "@/composants/ui/label";
import { utiliserRequete, utiliserMutation } from "@/crochets/utiliser-api";
import {
  listerAchats,
  creerAchat,
  marquerAchatAchete,
  supprimerAchat,
} from "@/bibliotheque/api/famille";
import { toast } from "sonner";
import type { AchatFamille, SuggestionAchat } from "@/types/famille";

export default function PageAchats() {
  const [openDialogue, setOpenDialogue] = useState(false);
  const [nouveauAchat, setNouveauAchat] = useState({ nom: "", categorie: "autre", priorite: "moyenne", description: "" });

  const { data: achats = [], refetch } = utiliserRequete<AchatFamille[]>(
    ["famille", "achats"],
    () => listerAchats()
  );

  const { mutateAsync: creer } = utiliserMutation(creerAchat, {
    onSuccess: () => {
      refetch();
      toast.success("Achat ajouté");
      setOpenDialogue(false);
      setNouveauAchat({ nom: "", categorie: "autre", priorite: "moyenne", description: "" });
    },
  });

  const { mutateAsync: marquer } = utiliserMutation(
    ({ id, prix_reel }: { id: number; prix_reel?: number }) =>
      marquerAchatAchete(id, prix_reel),
    { onSuccess: () => { refetch(); toast.success("Achat marqué acheté"); } }
  );

  const { mutateAsync: supprimer } = utiliserMutation(supprimerAchat, {
    onSuccess: () => { refetch(); toast.success("Achat supprimé"); },
  });

  // Grouper par catégorie
  const achatsNonAchetes = achats.filter((a) => !a.achete);
  const achatsParCategorie = achatsNonAchetes.reduce(
    (acc, achat) => {
      const cat = achat.categorie ?? "autre";
      if (!acc[cat]) acc[cat] = [];
      acc[cat].push(achat);
      return acc;
    },
    {} as Record<string, AchatFamille[]>
  );

  const categories = Object.keys(achatsParCategorie).sort();

  const handleCreerAchat = async () => {
    if (!nouveauAchat.nom.trim()) {
      toast.error("Le nom est requis");
      return;
    }
    await creer({
      nom: nouveauAchat.nom,
      categorie: nouveauAchat.categorie,
      priorite: nouveauAchat.priorite,
      description: nouveauAchat.description || undefined,
    });
  };

  return (
    <div className="space-y-6">
      {/* En-tête */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight flex items-center gap-2">
            <ShoppingCart className="h-6 w-6" />
            Achats Famille
          </h1>
          <p className="text-muted-foreground">
            Suggestions IA et liste d'achats à prévoir
          </p>
        </div>
        <Dialog open={openDialogue} onOpenChange={setOpenDialogue}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="h-4 w-4 mr-2" />
              Ajouter un achat
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Nouvel achat</DialogTitle>
            </DialogHeader>
            <div className="space-y-4 pt-2">
              <div>
                <Label htmlFor="nom">Nom *</Label>
                <Input
                  id="nom"
                  value={nouveauAchat.nom}
                  onChange={(e) => setNouveauAchat({ ...nouveauAchat, nom: e.target.value })}
                  placeholder="Ex: Livre d'éveil pour Jules"
                />
              </div>
              <div>
                <Label htmlFor="categorie">Catégorie</Label>
                <select
                  id="categorie"
                  value={nouveauAchat.categorie}
                  onChange={(e) => setNouveauAchat({ ...nouveauAchat, categorie: e.target.value })}
                  className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                >
                  <option value="cadeau">Cadeau</option>
                  <option value="vetement">Vêtement</option>
                  <option value="jouet">Jouet</option>
                  <option value="livre">Livre</option>
                  <option value="equipement">Équipement</option>
                  <option value="autre">Autre</option>
                </select>
              </div>
              <div>
                <Label htmlFor="priorite">Priorité</Label>
                <select
                  id="priorite"
                  value={nouveauAchat.priorite}
                  onChange={(e) => setNouveauAchat({ ...nouveauAchat, priorite: e.target.value })}
                  className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                >
                  <option value="haute">Haute</option>
                  <option value="moyenne">Moyenne</option>
                  <option value="basse">Basse</option>
                </select>
              </div>
              <div>
              <Label htmlFor="description">Description</Label>
              <Textarea
                  id="description"
                  value={nouveauAchat.description}
                  onChange={(e) => setNouveauAchat({ ...nouveauAchat, description: e.target.value })}
                  placeholder="Description supplémentaire..."
                  rows={3}
                />
              </div>
              <Button onClick={handleCreerAchat} className="w-full">
                Créer
              </Button>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      {/* Section suggestions IA (placeholder pour phase P backend) */}
      <Card className="bg-gradient-to-br from-purple-50/50 to-pink-50/50 dark:from-purple-950/20 dark:to-pink-950/20">
        <CardHeader>
          <div className="flex items-center gap-2">
            <Sparkles className="h-5 w-5 text-purple-500" />
            <CardTitle className="text-base">Suggestions IA</CardTitle>
          </div>
          <CardDescription>
            L'IA suggère des achats selon les événements (anniversaires, saison, jalons)
          </CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground text-center py-4">
            Fonctionnalité IA à venir — suggestions automatiques de cadeaux et achats pertinents
          </p>
          {/* TODO Phase P: afficher suggestions_cadeaux, suggestions_saison, suggestions_jalons */}
        </CardContent>
      </Card>

      {/* Liste des achats groupés par catégorie */}
      {categories.length === 0 ? (
        <Card>
          <CardContent className="pt-6 pb-6 text-center">
            <p className="text-muted-foreground text-sm">
              Aucun achat en attente. Ajoutez-en un avec le bouton "Ajouter".
            </p>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-4">
          {categories.map((cat) => (
            <Card key={cat}>
              <CardHeader className="pb-3">
                <CardTitle className="text-sm capitalize flex items-center justify-between">
                  <span>{cat}</span>
                  <Badge variant="outline">{achatsParCategorie[cat].length}</Badge>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                {achatsParCategorie[cat].map((achat) => (
                  <div
                    key={achat.id}
                    className="flex items-center gap-3 p-3 rounded-lg border bg-card hover:shadow-sm transition-shadow"
                  >
                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={() => marquer({ id: achat.id })}
                      className="shrink-0"
                    >
                      <Check className="h-4 w-4" />
                    </Button>
                    <div className="flex-1 min-w-0">
                      <p className="font-medium text-sm">{achat.nom}</p>
                      {achat.description && (
                        <p className="text-xs text-muted-foreground truncate">{achat.description}</p>
                      )}
                      {achat.prix_estime && (
                        <p className="text-xs text-muted-foreground">Prix estimé : {achat.prix_estime} €</p>
                      )}
                    </div>
                    {achat.priorite && (
                      <Badge
                        variant={
                          achat.priorite === "haute"
                            ? "destructive"
                            : achat.priorite === "moyenne"
                              ? "default"
                              : "outline"
                        }
                      >
                        {achat.priorite}
                      </Badge>
                    )}
                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={() => supprimer(achat.id)}
                      className="shrink-0"
                    >
                      <Trash2 className="h-4 w-4 text-destructive" />
                    </Button>
                  </div>
                ))}
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Historique achats achetés */}
      {achats.filter((a) => a.achete).length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-sm">Achats effectués récemment</CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="space-y-1 text-sm text-muted-foreground">
              {achats
                .filter((a) => a.achete)
                .slice(0, 5)
                .map((a) => (
                  <li key={a.id} className="flex items-center gap-2">
                    <Check className="h-3 w-3 text-green-500" />
                    <span className="line-through">{a.nom}</span>
                    {a.prix_reel && <span className="text-xs">({a.prix_reel} €)</span>}
                  </li>
                ))}
            </ul>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
