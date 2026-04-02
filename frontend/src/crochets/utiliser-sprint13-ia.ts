"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";
import { utiliserStoreNotifications } from "@/magasins/store-notifications";
import {
  analyserHabitudeFamille,
  analyserImpactsMeteo,
  analyserNutritionPersonne,
  analyserVarietePlanningRepas,
  estimerProjetMaison,
  predireConsommationInventaire,
  type AnalyseHabitudeRequest,
  type AnalyseHabitudeResponse,
  type AnalyseImpactsMeteoRequest,
  type AnalyseVarietePlanningRequest,
  type AnalyseVarieteResponse,
  type DonneesNutritionPersonneRequest,
  type DonneesNutritionnellesResponse,
  type EstimationProjetMaisonRequest,
  type EstimationProjetResponse,
  type MeteoContexte,
  type PredictionConsommationRequest,
  type PredictionConsommationResponse,
} from "@/bibliotheque/api/ia-sprint13";

function notifier(type: "succes" | "erreur", message: string): void {
  utiliserStoreNotifications.getState().ajouter({ type, message });
}

export function utilisePredictionConsommation() {
  const queryClient = useQueryClient();

  return useMutation<PredictionConsommationResponse, Error, PredictionConsommationRequest>({
    mutationFn: predireConsommationInventaire,
    onSuccess: (data) => {
      notifier("succes", `Consommation estimée: ${data.prochaine_consommation_estimee_j}j`);
      queryClient.invalidateQueries({ queryKey: ["inventaire"] });
    },
    onError: (error) => {
      notifier("erreur", error.message || "Impossible de générer la prédiction");
    },
  });
}

export function utiliseAnalyseVarietePlanning() {
  const queryClient = useQueryClient();

  return useMutation<AnalyseVarieteResponse, Error, AnalyseVarietePlanningRequest>({
    mutationFn: analyserVarietePlanningRepas,
    onSuccess: (data) => {
      notifier("succes", `Score variété: ${data.variete_score}/100`);
      queryClient.invalidateQueries({ queryKey: ["planning"] });
    },
    onError: (error) => {
      notifier("erreur", error.message || "Impossible d'analyser la variété");
    },
  });
}

export function utiliseAnalyseImpactsMeteo() {
  const queryClient = useQueryClient();

  return useMutation<MeteoContexte[], Error, AnalyseImpactsMeteoRequest>({
    mutationFn: analyserImpactsMeteo,
    onSuccess: (data) => {
      notifier("succes", `${data.length} jours météo analysés`);
      queryClient.invalidateQueries({ queryKey: ["meteo"] });
    },
    onError: (error) => {
      notifier("erreur", error.message || "Impossible d'analyser les impacts météo");
    },
  });
}

export function utiliseAnalyseHabitudes() {
  const queryClient = useQueryClient();

  return useMutation<AnalyseHabitudeResponse, Error, AnalyseHabitudeRequest>({
    mutationFn: analyserHabitudeFamille,
    onSuccess: (data) => {
      notifier("succes", `Compliance: ${Math.round(data.compliance_rate * 100)}%`);
      queryClient.invalidateQueries({ queryKey: ["famille"] });
    },
    onError: (error) => {
      notifier("erreur", error.message || "Impossible d'analyser l'habitude");
    },
  });
}

export function utiliseEstimationProjet() {
  const queryClient = useQueryClient();

  return useMutation<EstimationProjetResponse, Error, EstimationProjetMaisonRequest>({
    mutationFn: estimerProjetMaison,
    onSuccess: (data) => {
      notifier("succes", `Coût estimé: EUR ${data.cout_estime_min}-${data.cout_estime_max}`);
      queryClient.invalidateQueries({ queryKey: ["maison"] });
    },
    onError: (error) => {
      notifier("erreur", error.message || "Impossible d'estimer le projet");
    },
  });
}

export function utiliseAnalyseNutrition() {
  const queryClient = useQueryClient();

  return useMutation<DonneesNutritionnellesResponse, Error, DonneesNutritionPersonneRequest>({
    mutationFn: analyserNutritionPersonne,
    onSuccess: (data) => {
      notifier("succes", `Calories: ${Math.round(data.calories_journalieres_recommandees)} kcal/j`);
      queryClient.invalidateQueries({ queryKey: ["famille", "nutrition"] });
    },
    onError: (error) => {
      notifier("erreur", error.message || "Impossible d'analyser la nutrition");
    },
  });
}
