import { Skeleton } from "@/composants/ui/skeleton";

export default function MaSemaineLoading() {
  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      <Skeleton className="h-8 w-56" />
      <Skeleton className="h-4 w-44" />
      <div className="grid gap-4 grid-cols-1 md:grid-cols-3">
        <Skeleton className="h-40 rounded-xl" />
        <Skeleton className="h-40 rounded-xl" />
        <Skeleton className="h-40 rounded-xl" />
      </div>
      <Skeleton className="h-56 rounded-xl" />
    </div>
  );
}
