"use client";

import { useEffect } from "react";

interface RaccourcisPage {
  touche: string;
  action: () => void;
  actif?: boolean;
  description?: string;
}

function cibleEditable(target: EventTarget | null): boolean {
  if (!(target instanceof HTMLElement)) {
    return false;
  }

  const tag = target.tagName.toLowerCase();
  return tag === "input" || tag === "textarea" || target.isContentEditable || tag === "select";
}

export function utiliserRaccourcisPage(raccourcis: RaccourcisPage[]) {
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.metaKey || event.ctrlKey || event.altKey || cibleEditable(event.target)) {
        return;
      }

      const raccourci = raccourcis.find(
        (item) => (item.actif ?? true) && item.touche.toLowerCase() === event.key.toLowerCase()
      );

      if (!raccourci) {
        return;
      }

      event.preventDefault();
      raccourci.action();
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [raccourcis]);
}