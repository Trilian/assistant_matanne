// ═══════════════════════════════════════════════════════════
// Layout Maison — Présent sur toutes les pages /maison/*
// Inclut l'assistant IA flottant 
// ═══════════════════════════════════════════════════════════

import { AssistantFlottant } from "@/composants/maison/assistant-flottant";

export default function LayoutMaison({ children }: { children: React.ReactNode }) {
  return (
    <>
      {children}
      <AssistantFlottant />
    </>
  );
}
