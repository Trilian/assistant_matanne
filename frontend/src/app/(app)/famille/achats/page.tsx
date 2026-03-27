// ═══════════════════════════════════════════════════════════
// Page Achats Famille — Phase Refonte
// ═══════════════════════════════════════════════════════════

"use client";

import { useState } from "react";
import Link from "next/link";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  Plus,
  Trash2,
  Check,
  Sparkles,
  ShoppingCart,
  Tag,
  Copy,
  ChevronDown,
  ChevronUp,
  Repeat,
} from "lucide-react";
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
import {
  listerAchats,
  creerAchat,
  marquerAchatAchete,
  supprimerAchat,
  marquerAchatVendu,
  genererAnnonceLBC,
  genererAnnonceVinted,
  obtenirSuggestionsAchatsEnrichies,
} from "@/bibliotheque/api/famille";
import { toast } from "sonner";
import type { AchatFamille } from "@/types/famille";

const ONGLETS_POUR_QUI = [
  { id: "tout", label: "Tout" },
  { id: "jules", label: "Jules" },
  { id: "anne", label: "Anne" },
  { id: "mathieu", label: "Mathieu" },
  { id: "famille", label: "Famille" },
] as const;

const CHIPS_CATEGORIES = [
  "vetements", "jouets", "livres", "equipement", "gaming", "maison", "cadeau", "autre",
];

const LABELS_PRIORITE: Record<string, string> = {
  urgent: "Urgent", haute: "Haute", moyenne: "Moyenne", basse: "Basse", optionnel: "Optionnel",
};

const TRIGGERS_IA = [
  { id: "vetements_qualite", label: "Vetements" },
  { id: "sejour", label: "Sejour" },
  { id: "culture", label: "Culture" },
  { id: "gaming", label: "Gaming" },
  { id: "anniversaire", label: "Anniversaire" },
  { id: "maison", label: "Maison" },
] as const;

export default function PageAchats() {
  const queryClient = useQueryClient();
  const [ongletActif, setOngletActif] = useState<string>("tout");
  const [filtreCategorie, setFiltreCategorie] = useState<string | null>(null);
  const [accordeonIAOuvert, setAccordeonIAOuvert] = useState(false);
  const [openDialogue, setOpenDialogue] = useState(false);
  const [nouveauAchat, setNouveauAchat] = useState({
    nom: "", categorie: "autre", priorite: "moyenne", description: "",
    pour_qui: "famille", a_revendre: false, prix_estime: "",
  });
  const [annonceItem, setAnnonceItem] = useState<AchatFamille | null>(null);
  const [annonceTexte, setAnnonceTexte] = useState<string | null>(null);
  const [annonceChargement, setAnnonceChargement] = useState(false);
  const [plateformeAnnonce, setPlateformeAnnonce] = useState<"lbc" | "vinted">("lbc");

  const { data: achats = [] } = useQuery({
    queryKey: ["famille", "achats", "page"],
    queryFn: () => listerAchats(),
  });

  const [suggestions, setSuggestions] = useState<Array<{
    titre: string; description: string;
    fourchette_prix?: string | null; ou_acheter?: string | null;
    pertinence?: string | null; source?: string;
  }>>([]);
  const [chargementSuggestions, setChargementSuggestions] = useState(false);
  const [triggerActif, setTriggerActif] = useState<string | null>(null);

  const mutCreer = useMutation({
    mutationFn: creerAchat,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["famille", "achats"] });
      toast.success("Achat ajoute");
      setOpenDialogue(false);
      setNouveauAchat({ nom: "", categorie: "autre", priorite: "moyenne", description: "", pour_qui: "famille", a_revendre: false, prix_estime: "" });
    },
    onError: () => toast.error("Erreur lors de la creation"),
  });

  const mutMarquer = useMutation({
    mutationFn: ({ id, prix_reel }: { id: number; prix_reel?: number }) => marquerAchatAchete(id, prix_reel),
    onSuccess: () => { queryClient.invalidateQueries({ queryKey: ["famille", "achats"] }); toast.success("Achete !"); },
  });

  const mutSupprimer = useMutation({
    mutationFn: supprimerAchat,
    onSuccess: () => { queryClient.invalidateQueries({ queryKey: ["famille", "achats"] }); toast.success("Supprime"); },
  });

  const mutVendu = useMutation({
    mutationFn: marquerAchatVendu,
    onSuccess: () => { queryClient.invalidateQueries({ queryKey: ["famille", "achats"] }); toast.success("Marque comme vendu"); },
  });

  const achatsNonAchetes = achats.filter((a) => !a.achete);
  const achatsFiltres = achatsNonAchetes.filter((a) => {
    const matchPourQui = ongletActif === "tout" || a.pour_qui === ongletActif;
    const matchCat = !filtreCategorie || a.categorie === filtreCategorie;
    return matchPourQui && matchCat;
  });
  const achatsARevendre = achats.filter((a) => a.a_revendre && !a.vendu_le);
  const achatsParCategorie = achatsFiltres.reduce((acc, a) => {
    const cat = a.categorie ?? "autre";
    acc[cat] = acc[cat] ?? [];
    acc[cat].push(a);
    return acc;
  }, {} as Record<string, AchatFamille[]>);
  const categories = Object.keys(achatsParCategorie).sort();

  const handleCreerAchat = () => {
    if (!nouveauAchat.nom.trim()) { toast.error("Le nom est requis"); return; }
    mutCreer.mutate({
      nom: nouveauAchat.nom, categorie: nouveauAchat.categorie, priorite: nouveauAchat.priorite,
      description: nouveauAchat.description || undefined, pour_qui: nouveauAchat.pour_qui,
      a_revendre: nouveauAchat.a_revendre,
      prix_estime: nouveauAchat.prix_estime ? parseFloat(nouveauAchat.prix_estime) : undefined,
      suggere_par: "manuel",
    });
  };

  const chargerSuggestionsIA = async (trigger: string) => {
    setTriggerActif(trigger);
    setChargementSuggestions(true);
    try {
      const resultat = await obtenirSuggestionsAchatsEnrichies({
        triggers: [trigger],
        pour_qui: ongletActif !== "tout" ? ongletActif : "famille",
      });
      setSuggestions(resultat.items);
      toast.success(resultat.total + " suggestion(s) generee(s)");
    } catch { toast.error("Erreur IA"); } finally { setChargementSuggestions(false); }
  };

  const ajouterSuggestion = (s: { titre: string; description: string; source?: string }) => {
    mutCreer.mutate({
      nom: s.titre, categorie: s.source ?? "autre", priorite: "moyenne",
      description: s.description, suggere_par: "ia",
      pour_qui: ongletActif !== "tout" ? ongletActif : "famille", a_revendre: false,
    });
  };

  const plateformeRecommandee = (item: AchatFamille): "lbc" | "vinted" => {
    const categorie = (item.categorie ?? "").toLowerCase();
    if (["vetements", "jouets", "livres"].includes(categorie)) {
      return "vinted";
    }
    return "lbc";
  };

  const ouvrirDialogueAnnonce = async (item: AchatFamille, plateforme: "lbc" | "vinted") => {
    setPlateformeAnnonce(plateforme);
    setAnnonceItem(item);
    setAnnonceTexte(null);
    setAnnonceChargement(true);
    try {
      if (plateforme === "vinted") {
        const result = await genererAnnonceVinted(item.id, {
          nom: item.nom,
          description: item.description ?? "",
          etat_usage: "bon",
          prix_cible: item.prix_revente_estime ?? item.prix_reel ?? undefined,
          taille: item.taille,
          categorie_vinted: item.categorie,
        });
        setAnnonceTexte(result.annonce);
      } else {
        const result = await genererAnnonceLBC(item.id, {
          nom: item.nom,
          description: item.description ?? "",
          etat_usage: "bon",
          prix_cible: item.prix_revente_estime ?? item.prix_reel ?? undefined,
        });
        setAnnonceTexte(result.annonce);
      }
    } catch { toast.error("Impossible de generer l annonce"); } finally { setAnnonceChargement(false); }
  };

  const copierAnnonce = () => { if (annonceTexte) { navigator.clipboard.writeText(annonceTexte); toast.success("Copie !"); } };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight flex items-center gap-2">
            <ShoppingCart className="h-6 w-6" />Achats Famille
          </h1>
          <p className="text-muted-foreground">Suggestions IA et liste d achats</p>
        </div>
        <div className="flex items-center gap-2">
          <Link href="/famille/budget">
            <Button variant="outline" size="sm">Budget</Button>
          </Link>
          <Link href="/famille/activites">
            <Button variant="outline" size="sm">Activités</Button>
          </Link>
          <Dialog open={openDialogue} onOpenChange={setOpenDialogue}>
            <DialogTrigger asChild>
              <Button><Plus className="h-4 w-4 mr-2" />Ajouter</Button>
            </DialogTrigger>
          <DialogContent>
            <DialogHeader><DialogTitle>Nouvel achat</DialogTitle></DialogHeader>
            <div className="space-y-4 pt-2">
              <div>
                <Label htmlFor="nom">Nom *</Label>
                <Input id="nom" value={nouveauAchat.nom}
                  onChange={(e) => setNouveauAchat({ ...nouveauAchat, nom: e.target.value })}
                  placeholder="Ex: Livre pour Jules" />
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <Label htmlFor="pour_qui">Pour qui</Label>
                  <select id="pour_qui" title="Pour qui" value={nouveauAchat.pour_qui}
                    onChange={(e) => setNouveauAchat({ ...nouveauAchat, pour_qui: e.target.value })}
                    className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm">
                    <option value="famille">Famille</option>
                    <option value="jules">Jules</option>
                    <option value="anne">Anne</option>
                    <option value="mathieu">Mathieu</option>
                  </select>
                </div>
                <div>
                  <Label htmlFor="categorie">Categorie</Label>
                  <select id="categorie" title="Categorie" value={nouveauAchat.categorie}
                    onChange={(e) => setNouveauAchat({ ...nouveauAchat, categorie: e.target.value })}
                    className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm">
                    {CHIPS_CATEGORIES.map((c) => <option key={c} value={c}>{c}</option>)}
                  </select>
                </div>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <Label htmlFor="priorite">Priorite</Label>
                  <select id="priorite" title="Priorite" value={nouveauAchat.priorite}
                    onChange={(e) => setNouveauAchat({ ...nouveauAchat, priorite: e.target.value })}
                    className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm">
                    <option value="urgent">Urgent</option>
                    <option value="haute">Haute</option>
                    <option value="moyenne">Moyenne</option>
                    <option value="basse">Basse</option>
                    <option value="optionnel">Optionnel</option>
                  </select>
                </div>
                <div>
                  <Label htmlFor="prix">Prix (euros)</Label>
                  <Input id="prix" type="number" min="0" step="0.5" value={nouveauAchat.prix_estime}
                    onChange={(e) => setNouveauAchat({ ...nouveauAchat, prix_estime: e.target.value })}
                    placeholder="0.00" />
                </div>
              </div>
              <div>
                <Label htmlFor="description">Description</Label>
                <Textarea id="description" value={nouveauAchat.description}
                  onChange={(e) => setNouveauAchat({ ...nouveauAchat, description: e.target.value })}
                  placeholder="Taille, couleur, lien..." rows={2} />
              </div>
              <div className="flex items-center gap-2">
                <input id="a_revendre" type="checkbox" title="A revendre ensuite" checked={nouveauAchat.a_revendre}
                  onChange={(e) => setNouveauAchat({ ...nouveauAchat, a_revendre: e.target.checked })}
                  className="rounded" />
                <Label htmlFor="a_revendre" className="cursor-pointer">
                  <Repeat className="h-3.5 w-3.5 inline mr-1" />A revendre ensuite
                </Label>
              </div>
              <Button onClick={handleCreerAchat} className="w-full" disabled={mutCreer.isPending}>Creer</Button>
            </div>
          </DialogContent>
          </Dialog>
        </div>
      </div>

      <div className="flex gap-2 flex-wrap">
        {ONGLETS_POUR_QUI.map((o) => (
          <Button key={o.id} variant={ongletActif === o.id ? "default" : "outline"} size="sm" onClick={() => setOngletActif(o.id)}>
            {o.label}
            {o.id !== "tout" && (
              <Badge variant="secondary" className="ml-1.5 text-xs">
                {achatsNonAchetes.filter((a) => a.pour_qui === o.id).length}
              </Badge>
            )}
          </Button>
        ))}
      </div>

      <div className="flex gap-2 flex-wrap">
        <Button variant={filtreCategorie === null ? "secondary" : "ghost"} size="sm" onClick={() => setFiltreCategorie(null)}>
          <Tag className="h-3.5 w-3.5 mr-1" />Toutes
        </Button>
        {CHIPS_CATEGORIES.map((cat) => (
          <Button key={cat} variant={filtreCategorie === cat ? "secondary" : "ghost"} size="sm"
            onClick={() => setFiltreCategorie(filtreCategorie === cat ? null : cat)}>
            {cat}
          </Button>
        ))}
      </div>

      <Card className="border-purple-200/50">
        <CardHeader className="pb-2 cursor-pointer select-none" onClick={() => setAccordeonIAOuvert((o) => !o)}>
          <CardTitle className="text-sm flex items-center gap-2">
            <Sparkles className="h-4 w-4 text-purple-500" />
            Suggestions IA contextuelles
            {accordeonIAOuvert ? <ChevronUp className="h-4 w-4 ml-auto text-muted-foreground" /> : <ChevronDown className="h-4 w-4 ml-auto text-muted-foreground" />}
          </CardTitle>
          <CardDescription className="text-xs">Anniversaires, saison, jalons, sejour, gaming, culture</CardDescription>
        </CardHeader>
        {accordeonIAOuvert && (
          <CardContent className="space-y-4">
            <div className="grid grid-cols-3 gap-2">
              {TRIGGERS_IA.map((t) => (
                <Button key={t.id} variant={triggerActif === t.id ? "default" : "outline"} size="sm"
                  className="text-xs h-9" onClick={() => chargerSuggestionsIA(t.id)} disabled={chargementSuggestions}>
                  {chargementSuggestions && triggerActif === t.id ? <span className="animate-pulse">...</span> : t.label}
                </Button>
              ))}
            </div>
            {suggestions.length === 0 ? (
              <p className="text-sm text-muted-foreground text-center py-2">Choisissez un theme pour obtenir des idees.</p>
            ) : (
              <div className="space-y-2">
                {suggestions.slice(0, 8).map((s, idx) => (
                  <div key={s.titre + idx} className="rounded-lg border bg-card p-3">
                    <div className="flex items-start justify-between gap-3">
                      <div className="min-w-0">
                        <div className="flex items-center gap-1.5 flex-wrap">
                          <p className="text-sm font-medium">{s.titre}</p>
                          {(s as { score_pertinence?: number }).score_pertinence !== undefined &&
                            (s as { score_pertinence?: number }).score_pertinence! > 0.7 && (
                              <Badge variant="secondary" className="text-[10px]">✨ Très pertinent</Badge>
                            )}
                        </div>
                        {(s as { raison_suggestion?: string }).raison_suggestion && (
                          <p className="text-xs text-muted-foreground mt-0.5">
                            {(s as { raison_suggestion?: string }).raison_suggestion}
                          </p>
                        )}
                        <p className="text-xs text-muted-foreground mt-1">{s.description}</p>
                        <div className="flex flex-wrap gap-1 mt-2">
                          {s.source && <Badge variant="outline" className="text-xs">{s.source}</Badge>}
                          {s.fourchette_prix && <Badge variant="secondary" className="text-xs">{s.fourchette_prix}</Badge>}
                          {s.ou_acheter && <Badge variant="outline" className="text-xs text-muted-foreground">{s.ou_acheter}</Badge>}
                        </div>
                      </div>
                      <Button size="sm" onClick={() => ajouterSuggestion(s)}>Ajouter</Button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        )}
      </Card>

      {categories.length === 0 ? (
        <Card>
          <CardContent className="pt-6 pb-6 text-center">
            <p className="text-muted-foreground text-sm">
              {ongletActif === "tout" ? "Aucun achat en attente." : "Aucun achat en attente pour ce filtre."}
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
                  <div key={achat.id} className="flex items-center gap-3 p-3 rounded-lg border bg-card">
                    <Button size="sm" variant="ghost" onClick={() => mutMarquer.mutate({ id: achat.id })} className="shrink-0" title="Marquer achete">
                      <Check className="h-4 w-4" />
                    </Button>
                    <div className="flex-1 min-w-0">
                      <p className="font-medium text-sm">{achat.nom}</p>
                      {achat.description && <p className="text-xs text-muted-foreground truncate">{achat.description}</p>}
                      <div className="flex flex-wrap gap-1 mt-1">
                        {achat.pour_qui && achat.pour_qui !== "famille" && <Badge variant="outline" className="text-xs">{achat.pour_qui}</Badge>}
                        {achat.prix_estime && <span className="text-xs text-muted-foreground">~{achat.prix_estime} euros</span>}
                        {achat.a_revendre && (
                          <Badge variant="secondary" className="text-xs">
                            <Repeat className="h-3 w-3 mr-1" />a revendre
                          </Badge>
                        )}
                      </div>
                    </div>
                    {achat.priorite && (
                      <Badge variant={achat.priorite === "urgent" || achat.priorite === "haute" ? "destructive" : achat.priorite === "moyenne" ? "default" : "outline"} className="shrink-0 text-xs">
                        {LABELS_PRIORITE[achat.priorite] ?? achat.priorite}
                      </Badge>
                    )}
                    <Button size="sm" variant="ghost" onClick={() => mutSupprimer.mutate(achat.id)} className="shrink-0" title="Supprimer">
                      <Trash2 className="h-4 w-4 text-destructive" />
                    </Button>
                  </div>
                ))}
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {achatsARevendre.length > 0 && (
        <Card className="border-green-200/50">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm flex items-center gap-2">
              <Repeat className="h-4 w-4 text-green-500" />A revendre ({achatsARevendre.length})
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            {achatsARevendre.map((a) => (
              <div key={a.id} className="flex items-center gap-3 p-2 rounded border bg-card text-sm">
                <span className="flex-1 font-medium">{a.nom}</span>
                {a.prix_revente_estime && <span className="text-xs text-muted-foreground">~{a.prix_revente_estime} euros</span>}
                <Badge variant="outline" className="text-xs">
                  Reco: {plateformeRecommandee(a) === "vinted" ? "Vinted" : "LBC"}
                </Badge>
                <Button size="sm" variant="outline" onClick={() => ouvrirDialogueAnnonce(a, "lbc")} className="text-xs h-7">Annonce LBC</Button>
                <Button size="sm" variant="outline" onClick={() => ouvrirDialogueAnnonce(a, "vinted")} className="text-xs h-7">Annonce Vinted</Button>
                <Button size="sm" variant="ghost" onClick={() => mutVendu.mutate(a.id)} title="Marquer vendu">
                  <Check className="h-4 w-4 text-green-600" />
                </Button>
              </div>
            ))}
          </CardContent>
        </Card>
      )}

      <Dialog open={!!annonceItem} onOpenChange={(o) => { if (!o) { setAnnonceItem(null); setAnnonceTexte(null); } }}>
        <DialogContent className="max-w-lg">
          <DialogHeader><DialogTitle>Annonce {plateformeAnnonce === "vinted" ? "Vinted" : "LeBonCoin"} - {annonceItem?.nom}</DialogTitle></DialogHeader>
          {annonceChargement ? (
            <p className="text-sm text-muted-foreground py-4 text-center">Generation en cours...</p>
          ) : annonceTexte ? (
            <div className="space-y-3">
              <Textarea value={annonceTexte} readOnly rows={10} className="font-mono text-xs resize-none" />
              <Button onClick={copierAnnonce} className="w-full">
                <Copy className="h-4 w-4 mr-2" />Copier l annonce
              </Button>
            </div>
          ) : (
            <p className="text-sm text-muted-foreground py-4 text-center">Annonce non disponible</p>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}