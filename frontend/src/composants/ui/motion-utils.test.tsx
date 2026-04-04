import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { SectionReveal } from "./motion-utils";

describe("SectionReveal", () => {
  it("rend son contenu et la classe passée", () => {
    render(
      <SectionReveal className="zone-test" data-testid="section-reveal-test">
        <span>Contenu animé</span>
      </SectionReveal>
    );

    const section = screen.getByTestId("section-reveal-test");
    expect(section).toBeInTheDocument();
    expect(section).toHaveClass("zone-test");
    expect(screen.getByText("Contenu animé")).toBeInTheDocument();
  });
});
