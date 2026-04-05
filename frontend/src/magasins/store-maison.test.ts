// Tests store maison — timers appareils, tâches jour

import { describe, it, expect, beforeEach } from "vitest";
import { utiliserStoreMaison } from "@/magasins/store-maison";
import { act } from "@testing-library/react";

describe("utiliserStoreMaison", () => {
  beforeEach(() => {
    // Reset store state
    act(() => {
      const store = utiliserStoreMaison.getState();
      store.reinitialiserTachesJour();
      // Clear all timers
      Object.keys(store.timers).forEach((k) => store.arreterTimer(k));
    });
  });

  describe("timers appareils", () => {
    it("lance un timer", () => {
      act(() => {
        utiliserStoreMaison.getState().lancerTimer("lave-linge", 90, "Étendre le linge");
      });

      const state = utiliserStoreMaison.getState();
      expect(state.timers["lave-linge"]).toBeDefined();
      expect(state.timers["lave-linge"].dureeTotalMs).toBe(90 * 60 * 1000);
      expect(state.timers["lave-linge"].actionPost).toBe("Étendre le linge");
      expect(state.timers["lave-linge"].termine).toBe(false);
    });

    it("arrête un timer", () => {
      act(() => {
        utiliserStoreMaison.getState().lancerTimer("four", 30, "Sortir le plat");
        utiliserStoreMaison.getState().arreterTimer("four");
      });

      expect(utiliserStoreMaison.getState().timers["four"]).toBeUndefined();
    });

    it("marque un timer comme terminé", () => {
      act(() => {
        utiliserStoreMaison.getState().lancerTimer("lave-vaisselle", 120, "Ranger");
        utiliserStoreMaison.getState().marquerTimerTermine("lave-vaisselle");
      });

      expect(utiliserStoreMaison.getState().timers["lave-vaisselle"].termine).toBe(true);
    });

    it("timersActifs exclut les terminés", () => {
      act(() => {
        const store = utiliserStoreMaison.getState();
        store.lancerTimer("a", 10, "x");
        store.lancerTimer("b", 20, "y");
        store.marquerTimerTermine("b");
      });

      const actifs = utiliserStoreMaison.getState().timersActifs();
      expect(actifs).toHaveLength(1);
      expect(actifs[0].appareil).toBe("a");
    });
  });

  describe("tâches du jour", () => {
    it("bascule une tâche", () => {
      act(() => {
        utiliserStoreMaison.getState().basculerTache("tache-1");
      });

      expect(utiliserStoreMaison.getState().tachesTerminees).toContain("tache-1");
    });

    it("bascule une tâche deux fois la retire", () => {
      act(() => {
        const store = utiliserStoreMaison.getState();
        store.basculerTache("tache-2");
        store.basculerTache("tache-2");
      });

      expect(utiliserStoreMaison.getState().tachesTerminees).not.toContain("tache-2");
    });

    it("réinitialise les tâches du jour", () => {
      act(() => {
        const store = utiliserStoreMaison.getState();
        store.basculerTache("a");
        store.basculerTache("b");
        store.reinitialiserTachesJour();
      });

      expect(utiliserStoreMaison.getState().tachesTerminees).toEqual([]);
    });
  });
});
