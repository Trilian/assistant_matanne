import { Skeleton } from "@/composants/ui/skeleton";

export default function Loading() {
  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      <Skeleton className="h-8 w-56 animate-in fade-in slide-in-from-bottom-1 duration-500" />
      <Skeleton className="h-4 w-40 animate-in fade-in slide-in-from-bottom-1 duration-500 delay-75" />
      <div className="grid gap-4 grid-cols-2 lg:grid-cols-4">
        <Skeleton className="h-24 rounded-xl animate-in fade-in slide-in-from-bottom-1 duration-500 delay-150" />
        <Skeleton className="h-24 rounded-xl animate-in fade-in slide-in-from-bottom-1 duration-500 delay-300" />
        <Skeleton className="h-24 rounded-xl animate-in fade-in slide-in-from-bottom-1 duration-500 delay-500" />
        <Skeleton className="h-24 rounded-xl animate-in fade-in slide-in-from-bottom-1 duration-500 delay-700" />
      </div>
      <Skeleton className="h-48 rounded-xl animate-in fade-in slide-in-from-bottom-1 duration-500 delay-700" />
    </div>
  );
}
