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
  obtenirSuggestionsAchatsAuto,
} from "@/bibliotheque/api/famille";
import { toast } from "sonner";
import type { AchatFamille } from "@/types/famille";

export default function PageAchats() {
  const [openDialogue, setOpenDialogue] = useState(false);
  const [nouveauAchat, setNouveauAchat] = useState({ nom: "", categorie: "autre", priorite: "moyenne", description: "" });
  const [chargementSuggestions, setChargementSuggestions] = useState(false);
  const [suggestions, setSuggestions] = useState<Array<{
    titre: string;
    description: string;
    fourchette_prix?: string | null;
    ou_acheter?: string | null;
    pertinence?: string | null;
    source: "anniversaire" | "jalon" | "saison";
  }>>([]);

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

  const chargerSuggestionsIA = async () => {
    setChargementSuggestions(true);
    try {
      const resultat = await obtenirSuggestionsAchatsAuto({});
      setSuggestions(resultat.suggestions);
      toast.success(`${resultat.total} suggestion(s) IA générée(s)`);
    } catch {
      toast.error("Erreur lors du chargement des suggestions IA");
    } finally {
      setChargementSuggestions(false);
    }
  };

  const ajouterSuggestion = async (suggestion: {
    titre: string;
    description: string;
    source: "anniversaire" | "jalon" | "saison";
  }) => {
    await creer({
      nom: suggestion.titre,
      categorie: suggestion.source === "anniversaire" ? "cadeau" : suggestion.source,
      priorite: suggestion.source === "anniversaire" ? "haute" : "moyenne",
      description: suggestion.description,
      suggere_par: "ia",
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
                  title="Catégorie"
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
                  title="Priorité"
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

      {/* Section suggestions IA (Phase P) */}
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
          <div className="space-y-3">
            <Button
              variant="outline"
              className="w-full"
              onClick={chargerSuggestionsIA}
              disabled={chargementSuggestions}
            >
              <Sparkles className="h-4 w-4 mr-2" />
              {chargementSuggestions ? "Génération en cours..." : "Générer des suggestions proactives"}
            </Button>

            {suggestions.length === 0 ? (
              <p className="text-sm text-muted-foreground text-center py-2">
                Lancez la génération pour obtenir des idées cadeaux/achats basées sur anniversaire, jalons et saison.
              </p>
            ) : (
              <div className="space-y-2">
                {suggestions.slice(0, 6).map((s, idx) => (
                  <div key={`${s.titre}-${idx}`} className="rounded-lg border bg-card p-3">
                    <div className="flex items-start justify-between gap-3">
                      <div className="min-w-0">
                        <p className="text-sm font-medium">{s.titre}</p>
                        <p className="text-xs text-muted-foreground mt-1">{s.description}</p>
                        <div className="flex flex-wrap gap-1 mt-2">
                          <Badge variant="outline" className="text-xs">{s.source}</Badge>
                          {s.fourchette_prix && <Badge variant="secondary" className="text-xs">{s.fourchette_prix}</Badge>}
                        </div>
                      </div>
                      <Button size="sm" onClick={() => ajouterSuggestion(s)}>
                        Ajouter
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
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
