'use client'

import { type ReactNode } from "react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/composants/ui/dialog";
import { Sheet, SheetContent, SheetHeader, SheetTitle } from "@/composants/ui/sheet";
import { useIsMobile } from "@/crochets/use-mobile";

interface ResponsiveOverlayProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  title: string;
  children: ReactNode;
  contentClassName?: string;
}

export function ResponsiveOverlay({
  open,
  onOpenChange,
  title,
  children,
  contentClassName,
}: ResponsiveOverlayProps) {
  const isMobile = useIsMobile();

  if (isMobile) {
    return (
      <Sheet open={open} onOpenChange={onOpenChange}>
        <SheetContent
          side="bottom"
          className={`max-h-[92vh] overflow-y-auto rounded-t-3xl border-x-0 border-b-0 px-0 ${contentClassName ?? ""}`}
        >
          <SheetHeader className="pb-2">
            <SheetTitle>{title}</SheetTitle>
          </SheetHeader>
          <div className="px-4 pb-4">{children}</div>
        </SheetContent>
      </Sheet>
    );
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className={contentClassName}>
        <DialogHeader>
          <DialogTitle>{title}</DialogTitle>
        </DialogHeader>
        {children}
      </DialogContent>
    </Dialog>
  );
}
