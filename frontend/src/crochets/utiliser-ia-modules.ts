"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";
import { utiliserStoreNotifications } from "@/magasins/store-notifications";
import {
  analyserHabitudeFamille,
  analyserImpactsMeteo,
  analyserNutritionPersonne,
  analyserVarietePlanningRepas,
  estimerProjetMaison,
  optimiserNutritionPlanningRepas,
  predireConsommationInventaire,
  suggererSimplificationPlanningRepas,
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
  type OptimisationNutritionPlanningRequest,
  type OptimisationNutritionPlanningResponse,
  type PredictionConsommationRequest,
  type PredictionConsommationResponse,
  type SimplificationPlanningRequest,
  type SimplificationPlanningResponse,
} from "@/bibliotheque/api/ia-modules";

function notifier(type: "succes" | "erreur", message: string): void {
  utiliserStoreNotifications.getState().ajouter({ type, message });
}

/** Hook mutation IA — prédiction de consommation inventaire. */
export function utilisePredictionConsommation() {
  const queryClient = useQueryClient();

  return useMutation<PredictionConsommationResponse, Error, PredictionConsommationRequest>({
    mutationFn: predireConsommationInventaire,
    onSuccess: (data) => {
      notifier("succes", `Autonomie estimée: ${data.jours_autonomie}j`);
      queryClient.invalidateQueries({ queryKey: ["inventaire"] });
    },
    onError: (error) => {
      notifier("erreur", error.message || "Impossible de générer la prédiction");
    },
  });
}

/** Hook mutation IA — analyse de variété du planning repas. */
export function utiliseAnalyseVarietePlanning() {
  const queryClient = useQueryClient();

  return useMutation<AnalyseVarieteResponse, Error, AnalyseVarietePlanningRequest>({
    mutationFn: analyserVarietePlanningRepas,
    onSuccess: (data) => {
      notifier("succes", `Score variété: ${data.score_variete}/100`);
      queryClient.invalidateQueries({ queryKey: ["planning"] });
    },
    onError: (error) => {
      notifier("erreur", error.message || "Impossible d'analyser la variété");
    },
  });
}

/** Hook mutation IA — optimisation nutritionnelle du planning. */
export function utiliseOptimisationNutritionPlanning() {
  const queryClient = useQueryClient();

  return useMutation<
    OptimisationNutritionPlanningResponse,
    Error,
    OptimisationNutritionPlanningRequest
  >({
    mutationFn: optimiserNutritionPlanningRepas,
    onSuccess: (data) => {
      notifier(
        "succes",
        `Fruits & légumes: ${Math.round(data.fruits_legumes_quota * 100)}% de l'objectif`
      );
      queryClient.invalidateQueries({ queryKey: ["planning", "nutrition"] });
    },
    onError: (error) => {
      notifier("erreur", error.message || "Impossible d'optimiser la nutrition du planning");
    },
  });
}

/** Hook mutation IA — simplification du planning repas. */
export function utiliseSimplificationPlanning() {
  const queryClient = useQueryClient();

  return useMutation<SimplificationPlanningResponse, Error, SimplificationPlanningRequest>({
    mutationFn: suggererSimplificationPlanningRepas,
    onSuccess: (data) => {
      notifier("succes", `Gain estimé: ${data.gain_temps_minutes} min`);
      queryClient.invalidateQueries({ queryKey: ["planning"] });
    },
    onError: (error) => {
      notifier("erreur", error.message || "Impossible de simplifier la semaine");
    },
  });
}

/** Hook mutation IA — analyse des impacts météo sur les activités. */
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

/** Hook mutation IA — analyse des habitudes familiales. */
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

/** Hook mutation IA — estimation coût/durée d'un projet maison. */
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

/** Hook mutation IA — analyse nutritionnelle personnalisée. */
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
