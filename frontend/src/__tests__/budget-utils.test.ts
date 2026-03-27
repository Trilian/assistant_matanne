import { describe, expect, it } from "vitest";

import { couleurBarreBudget } from "@/bibliotheque/utils";

describe("couleurBarreBudget", () => {
  it("retourne la couleur verte sous 50%", () => {
    expect(couleurBarreBudget(0)).toBe("bg-green-500");
    expect(couleurBarreBudget(49)).toBe("bg-green-500");
  });

  it("retourne la couleur jaune entre 50% et 74%", () => {
    expect(couleurBarreBudget(50)).toBe("bg-yellow-400");
    expect(couleurBarreBudget(74)).toBe("bg-yellow-400");
  });

  it("retourne la couleur orange entre 75% et 89%", () => {
    expect(couleurBarreBudget(75)).toBe("bg-orange-400");
    expect(couleurBarreBudget(89)).toBe("bg-orange-400");
  });

  it("retourne la couleur rouge a partir de 90%", () => {
    expect(couleurBarreBudget(90)).toBe("bg-red-500");
    expect(couleurBarreBudget(99)).toBe("bg-red-500");
  });

  it("retourne la couleur bloquante a 100% si le seuil est active", () => {
    expect(couleurBarreBudget(100, true)).toBe("bg-red-600");
    expect(couleurBarreBudget(120, true)).toBe("bg-red-600");
  });
});
