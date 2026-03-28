"use client";

import * as React from "react";

type CollapsibleContextValue = {
  open: boolean;
  setOpen: (open: boolean) => void;
};

const CollapsibleContext = React.createContext<CollapsibleContextValue | null>(null);

function useCollapsibleContext(): CollapsibleContextValue {
  const context = React.useContext(CollapsibleContext);
  if (!context) {
    throw new Error("Collapsible components must be used within <Collapsible>.");
  }
  return context;
}

type CollapsibleProps = React.HTMLAttributes<HTMLDivElement> & {
  open?: boolean;
  defaultOpen?: boolean;
  onOpenChange?: (open: boolean) => void;
};

export function Collapsible({
  open,
  defaultOpen = false,
  onOpenChange,
  children,
  ...props
}: CollapsibleProps) {
  const [internalOpen, setInternalOpen] = React.useState(defaultOpen);
  const isControlled = open !== undefined;
  const currentOpen = isControlled ? open : internalOpen;

  const setOpen = React.useCallback(
    (nextOpen: boolean) => {
      if (!isControlled) {
        setInternalOpen(nextOpen);
      }
      onOpenChange?.(nextOpen);
    },
    [isControlled, onOpenChange],
  );

  return (
    <CollapsibleContext.Provider value={{ open: currentOpen, setOpen }}>
      <div data-state={currentOpen ? "open" : "closed"} {...props}>
        {children}
      </div>
    </CollapsibleContext.Provider>
  );
}

export const CollapsibleTrigger = React.forwardRef<
  HTMLButtonElement,
  React.ButtonHTMLAttributes<HTMLButtonElement>
>(({ onClick, children, ...props }, ref) => {
  const { open, setOpen } = useCollapsibleContext();
  return (
    <button
      ref={ref}
      type="button"
      data-state={open ? "open" : "closed"}
      onClick={(event) => {
        onClick?.(event);
        if (!event.defaultPrevented) {
          setOpen(!open);
        }
      }}
      {...props}
    >
      {children}
    </button>
  );
});

CollapsibleTrigger.displayName = "CollapsibleTrigger";

export const CollapsibleContent = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ children, ...props }, ref) => {
  const { open } = useCollapsibleContext();
  if (!open) {
    return null;
  }
  return (
    <div ref={ref} data-state="open" {...props}>
      {children}
    </div>
  );
});

CollapsibleContent.displayName = "CollapsibleContent";
