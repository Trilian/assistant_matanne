// ═══════════════════════════════════════════════════════════
// Layout Auth — Pages connexion/inscription (sans sidebar)
// ═══════════════════════════════════════════════════════════

export default function LayoutAuth({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="flex min-h-screen items-center justify-center bg-muted/40 p-4">
      <div className="w-full max-w-md">{children}</div>
    </div>
  );
}
