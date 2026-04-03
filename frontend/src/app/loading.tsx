// ═══════════════════════════════════════════════════════════
// Loading global — Skeleton pendant le chargement
// ═══════════════════════════════════════════════════════════

import { Skeleton } from "@/composants/ui/skeleton";

export default function Loading() {
  return (
    <div className="flex h-screen items-center justify-center">
      <div className="space-y-4 w-full max-w-md px-4">
        <Skeleton className="h-8 w-48 animate-in fade-in slide-in-from-bottom-1 duration-500" />
        <Skeleton className="h-4 w-full animate-in fade-in slide-in-from-bottom-1 duration-500 delay-75" />
        <Skeleton className="h-4 w-3/4 animate-in fade-in slide-in-from-bottom-1 duration-500 delay-150" />
        <div className="grid grid-cols-2 gap-4 mt-6">
          <Skeleton className="h-24 animate-in fade-in slide-in-from-bottom-1 duration-500 delay-200" />
          <Skeleton className="h-24 animate-in fade-in slide-in-from-bottom-1 duration-500 delay-300" />
          <Skeleton className="h-24 animate-in fade-in slide-in-from-bottom-1 duration-500 delay-500" />
          <Skeleton className="h-24 animate-in fade-in slide-in-from-bottom-1 duration-500 delay-700" />
        </div>
      </div>
    </div>
  );
}
