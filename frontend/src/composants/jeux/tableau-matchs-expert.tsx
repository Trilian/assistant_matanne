"use client";

import { useState, useMemo } from "react";
import { Badge } from "@/composants/ui/badge";
import { Button } from "@/composants/ui/button";
import { Input } from "@/composants/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/composants/ui/select";
import { Slider } from "@/composants/ui/slider";
import { Label } from "@/composants/ui/label";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/composants/ui/dropdown-menu";
import { 
  Download, 
  Filter, 
  AlertTriangle,
  MoreVertical,
  Eye,
  Plus,
} from "lucide-react";
import { utiliserRequete } from "@/crochets/utiliser-api";
import { Skeleton } from "@/composants/ui/skeleton";
import { ZoneTableauResponsive } from "@/composants/ui/zone-tableau-responsive";
import { CSVLink } from "react-csv";

export interface MatchExpert {
  id: number;
  equipe_domicile: string;
  equipe_exterieur: string;
  date_match: string;
  championnat: string;
  cote_domicile: number | null;
  cote_nul: number | null;
  cote_exterieur: number | null;
  ev: number | null; // Expected Value
  prediction_ia: string | null;
  proba_ia: number | null;
  confiance_ia: number | null;
  pattern_detecte: string | null;
  forme_domicile: string | null;
  forme_exterieur: string | null;
}

interface Filtres {
  league: string;
  date_min: string;
  date_max: string;
  ev_min: number;
  confidence_min: number;
  pattern: string;
  search: string;
}

const LEAGUES = [
  { value: "all", label: "Toutes les ligues" },
  { value: "ligue_1", label: "Ligue 1" },
  { value: "premier_league", label: "Premier League" },
  { value: "la_liga", label: "La Liga" },
  { value: "bundesliga", label: "Bundesliga" },
  { value: "serie_a", label: "Serie A" },
];

const PATTERNS = [
  { value: "all", label: "Tous les patterns" },
  { value: "hot_hand", label: "Hot Hand" },
  { value: "regression", label: "Régression moyenne" },
  { value: "value_bet", label: "Value Bet" },
  { value: "high_ev", label: "EV élevé (>10%)" },
];

interface TableauMatchsExpertProps {
  onCreerPari?: (matchId: number, prediction: string, cote: number) => void;
  onVoirDetails?: (matchId: number) => void;
}

export function TableauMatchsExpert({ 
  onCreerPari,
  onVoirDetails,
}: TableauMatchsExpertProps) {
  const [filtres, setFiltres] = useState<Filtres>({
    league: "all",
    date_min: "",
    date_max: "",
    ev_min: 0,
    confidence_min: 0,
    pattern: "all",
    search: "",
  });

  const [showFilters, setShowFilters] = useState(true);

  // Construire query params
  const queryParams = useMemo(() => {
    const params = new URLSearchParams();
    
    if (filtres.league !== "all") params.append("league", filtres.league);
    if (filtres.date_min) params.append("date_min", filtres.date_min);
    if (filtres.date_max) params.append("date_max", filtres.date_max);
    if (filtres.ev_min > 0) params.append("ev_min", String(filtres.ev_min));
    if (filtres.confidence_min > 0) params.append("confidence_min", String(filtres.confidence_min / 100));
    if (filtres.pattern !== "all") params.append("pattern", filtres.pattern);
    if (filtres.search) params.append("search", filtres.search);
    
    return params.toString();
  }, [filtres]);

  // Fetch matchs experts
  const { data, isLoading, error } = utiliserRequete<{ items: MatchExpert[] }>(
    ["jeux", "matchs-expert", queryParams],
    async () => {
      const response = await fetch(`/api/v1/jeux/paris/matchs?${queryParams}`);
      if (!response.ok) throw new Error("Erreur lors du chargement des matchs");
      return response.json();
    }
  );

  const matchs = useMemo(() => data?.items ?? [], [data?.items]);

  // Données pour export CSV
  const csvData = useMemo(() => {
    return matchs.map((m) => ({
      Match: `${m.equipe_domicile} vs ${m.equipe_exterieur}`,
      Championnat: m.championnat,
      Date: new Date(m.date_match).toLocaleDateString("fr-FR"),
      "Cote 1": m.cote_domicile,
      "Cote N": m.cote_nul,
      "Cote 2": m.cote_exterieur,
      "EV %": m.ev ? (m.ev * 100).toFixed(1) : "N/A",
      "Prédiction IA": m.prediction_ia || "N/A",
      "Proba %": m.proba_ia ? (m.proba_ia * 100).toFixed(0) : "N/A",
      "Confiance %": m.confiance_ia ? (m.confiance_ia * 100).toFixed(0) : "N/A",
      Pattern: m.pattern_detecte || "Aucun",
      "Forme Dom.": m.forme_domicile || "N/A",
      "Forme Ext.": m.forme_exterieur || "N/A",
    }));
  }, [matchs]);

  // Reset filtres
  const reinitialiserFiltres = () => {
    setFiltres({
      league: "all",
      date_min: "",
      date_max: "",
      ev_min: 0,
      confidence_min: 0,
      pattern: "all",
      search: "",
    });
  };

  const couleurEV = (ev: number | null) => {
    if (ev === null || ev < 0) return "text-red-600";
    if (ev > 0.10) return "text-green-600 font-bold";
    if (ev > 0.05) return "text-green-600";
    return "text-muted-foreground";
  };

  const couleurConfiance = (conf: number | null) => {
    if (!conf) return "text-muted-foreground";
    if (conf >= 0.7) return "text-green-600";
    if (conf >= 0.5) return "text-yellow-600";
    return "text-orange-600";
  };

  return (
    <div className="space-y-4">
      {/* Barre d'actions */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Button
            variant={showFilters ? "default" : "outline"}
            size="sm"
            onClick={() => setShowFilters(!showFilters)}
          >
            <Filter className="h-4 w-4 mr-2" />
            Filtres
          </Button>
          
          <Button variant="outline" size="sm" onClick={reinitialiserFiltres}>
            Réinitialiser
          </Button>
        </div>

        <div className="flex items-center gap-2">
          <span className="text-sm text-muted-foreground">
            {matchs.length} match{matchs.length > 1 ? "s" : ""}
          </span>
          
          <CSVLink
            data={csvData}
            filename={`matchs-expert-${new Date().toISOString().split("T")[0]}.csv`}
            className="inline-flex"
          >
            <Button variant="outline" size="sm">
              <Download className="h-4 w-4 mr-2" />
              Export CSV
            </Button>
          </CSVLink>
        </div>
      </div>

      {/* Panneau de filtres */}
      {showFilters && (
        <div className="grid gap-4 p-4 border rounded-lg bg-muted/30">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Ligue */}
            <div className="space-y-2">
              <Label htmlFor="filter-league">Championnat</Label>
              <Select
                value={filtres.league}
                onValueChange={(v) => setFiltres({ ...filtres, league: v })}
              >
                <SelectTrigger id="filter-league">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {LEAGUES.map((l) => (
                    <SelectItem key={l.value} value={l.value}>
                      {l.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* Pattern */}
            <div className="space-y-2">
              <Label htmlFor="filter-pattern">Pattern statistique</Label>
              <Select
                value={filtres.pattern}
                onValueChange={(v) => setFiltres({ ...filtres, pattern: v })}
              >
                <SelectTrigger id="filter-pattern">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {PATTERNS.map((p) => (
                    <SelectItem key={p.value} value={p.value}>
                      {p.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* Recherche */}
            <div className="space-y-2">
              <Label htmlFor="filter-search">Recherche équipe</Label>
              <Input
                id="filter-search"
                placeholder="PSG, Lyon..."
                value={filtres.search}
                onChange={(e) => setFiltres({ ...filtres, search: e.target.value })}
              />
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* EV min */}
            <div className="space-y-2">
              <Label>Expected Value minimum: {filtres.ev_min}%</Label>
              <Slider
                value={[filtres.ev_min]}
                onValueChange={([v]) => setFiltres({ ...filtres, ev_min: v })}
                min={0}
                max={20}
                step={1}
              />
            </div>

            {/* Confiance min */}
            <div className="space-y-2">
              <Label>Confiance IA minimum: {filtres.confidence_min}%</Label>
              <Slider
                value={[filtres.confidence_min]}
                onValueChange={([v]) => setFiltres({ ...filtres, confidence_min: v })}
                min={0}
                max={100}
                step={5}
              />
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Date min */}
            <div className="space-y-2">
              <Label htmlFor="filter-date-min">Date minimum</Label>
              <Input
                id="filter-date-min"
                type="date"
                value={filtres.date_min}
                onChange={(e) => setFiltres({ ...filtres, date_min: e.target.value })}
              />
            </div>

            {/* Date max */}
            <div className="space-y-2">
              <Label htmlFor="filter-date-max">Date maximum</Label>
              <Input
                id="filter-date-max"
                type="date"
                value={filtres.date_max}
                onChange={(e) => setFiltres({ ...filtres, date_max: e.target.value })}
              />
            </div>
          </div>
        </div>
      )}

      {/* Table */}
      {isLoading ? (
        <div className="space-y-2">
          <Skeleton className="h-12 w-full" />
          <Skeleton className="h-12 w-full" />
          <Skeleton className="h-12 w-full" />
        </div>
      ) : error ? (
        <div className="text-center py-8">
          <AlertTriangle className="h-12 w-12 text-destructive mx-auto mb-2" />
          <p className="text-sm text-muted-foreground">Erreur lors du chargement des matchs</p>
        </div>
      ) : matchs.length === 0 ? (
        <div className="text-center py-12 border rounded-lg bg-muted/20">
          <p className="text-muted-foreground">Aucun match trouvé avec ces filtres</p>
          <Button variant="link" onClick={reinitialiserFiltres} className="mt-2">
            Réinitialiser les filtres
          </Button>
        </div>
      ) : (
        <ZoneTableauResponsive containerClassName="border rounded-lg overflow-auto">
          <table className="w-full min-w-[900px]">
            <thead className="bg-muted">
              <tr>
                <th className="px-4 py-3 text-left text-sm font-medium">Match</th>
                <th className="px-4 py-3 text-left text-sm font-medium">Date</th>
                <th className="px-4 py-3 text-center text-sm font-medium">Cotes</th>
                <th className="px-4 py-3 text-center text-sm font-medium">EV</th>
                <th className="px-4 py-3 text-left text-sm font-medium">Prédiction IA</th>
                <th className="px-4 py-3 text-center text-sm font-medium">Confiance</th>
                <th className="px-4 py-3 text-left text-sm font-medium">Pattern</th>
                <th className="px-4 py-3 text-center text-sm font-medium">Forme</th>
                <th className="px-4 py-3 text-center text-sm font-medium">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y">
              {matchs.map((match) => (
                <tr key={match.id} className="hover:bg-muted/50">
                    <td className="px-4 py-3">
                      <div>
                        <p className="font-medium text-sm">{match.equipe_domicile}</p>
                        <p className="text-sm text-muted-foreground">{match.equipe_exterieur}</p>
                      </div>
                      <Badge variant="outline" className="text-xs mt-1">
                        {match.championnat}
                      </Badge>
                    </td>
                    
                    <td className="px-4 py-3 text-sm">
                      {new Date(match.date_match).toLocaleDateString("fr-FR", {
                        day: "numeric",
                        month: "short",
                      })}
                    </td>
                    
                    <td className="px-4 py-3 text-center">
                      <div className="flex gap-2 justify-center text-xs">
                        <span className="font-mono">{match.cote_domicile?.toFixed(2) || "—"}</span>
                        <span className="font-mono text-muted-foreground">{match.cote_nul?.toFixed(2) || "—"}</span>
                        <span className="font-mono">{match.cote_exterieur?.toFixed(2) || "—"}</span>
                      </div>
                    </td>
                    
                    <td className="px-4 py-3 text-center">
                      {match.ev !== null ? (
                        <span className={`text-sm font-medium ${couleurEV(match.ev)}`}>
                          {match.ev > 0 && "+"}
                          {(match.ev * 100).toFixed(1)}%
                        </span>
                      ) : (
                        <span className="text-xs text-muted-foreground">N/A</span>
                      )}
                    </td>
                    
                    <td className="px-4 py-3">
                      {match.prediction_ia ? (
                        <div className="flex items-center gap-1">
                          <span className="text-sm">{match.prediction_ia}</span>
                          {match.proba_ia && (
                            <span className="text-xs text-muted-foreground">
                              ({(match.proba_ia * 100).toFixed(0)}%)
                            </span>
                          )}
                        </div>
                      ) : (
                        <span className="text-xs text-muted-foreground">—</span>
                      )}
                    </td>
                    
                    <td className="px-4 py-3 text-center">
                      {match.confiance_ia !== null ? (
                        <Badge variant="outline" className={couleurConfiance(match.confiance_ia)}>
                          {(match.confiance_ia * 100).toFixed(0)}%
                        </Badge>
                      ) : (
                        <span className="text-xs text-muted-foreground">—</span>
                      )}
                    </td>
                    
                    <td className="px-4 py-3">
                      {match.pattern_detecte ? (
                        <Badge variant="secondary" className="text-xs">
                          {match.pattern_detecte}
                        </Badge>
                      ) : (
                        <span className="text-xs text-muted-foreground">Aucun</span>
                      )}
                    </td>
                    
                    <td className="px-4 py-3 text-center">
                      <div className="flex gap-1 justify-center text-xs">
                        <span className="font-mono">{match.forme_domicile || "—"}</span>
                        <span className="text-muted-foreground">vs</span>
                        <span className="font-mono">{match.forme_exterieur || "—"}</span>
                      </div>
                    </td>
                    
                    <td className="px-4 py-3">
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button variant="ghost" size="sm">
                            <MoreVertical className="h-4 w-4" />
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end">
                          {onVoirDetails && (
                            <DropdownMenuItem onClick={() => onVoirDetails(match.id)}>
                              <Eye className="h-4 w-4 mr-2" />
                              Voir détails
                            </DropdownMenuItem>
                          )}
                          {onCreerPari && match.cote_domicile && (
                            <>
                              <DropdownMenuItem 
                                onClick={() => onCreerPari(match.id, "domicile", match.cote_domicile!)}
                              >
                                <Plus className="h-4 w-4 mr-2" />
                                Parier domicile ({match.cote_domicile.toFixed(2)})
                              </DropdownMenuItem>
                              {match.cote_nul && (
                                <DropdownMenuItem 
                                  onClick={() => onCreerPari(match.id, "nul", match.cote_nul!)}
                                >
                                  <Plus className="h-4 w-4 mr-2" />
                                  Parier nul ({match.cote_nul.toFixed(2)})
                                </DropdownMenuItem>
                              )}
                              {match.cote_exterieur && (
                                <DropdownMenuItem 
                                  onClick={() => onCreerPari(match.id, "exterieur", match.cote_exterieur!)}
                                >
                                  <Plus className="h-4 w-4 mr-2" />
                                  Parier extérieur ({match.cote_exterieur.toFixed(2)})
                                </DropdownMenuItem>
                              )}
                            </>
                          )}
                        </DropdownMenuContent>
                      </DropdownMenu>
                    </td>
                  </tr>
              ))}
            </tbody>
          </table>
        </ZoneTableauResponsive>
      )}
    </div>
  );
}
