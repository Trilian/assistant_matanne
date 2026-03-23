// ═══════════════════════════════════════════════════════════
// Layout App — Avec sidebar et navigation (routes protégées)
// ═══════════════════════════════════════════════════════════

import { CoquilleApp } from "@/composants/disposition/coquille-app";

export default function LayoutApp({
  children,
}: {
  children: React.ReactNode;
}) {
  return <CoquilleApp>{children}</CoquilleApp>;
}
