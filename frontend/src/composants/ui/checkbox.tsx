"use client";

import * as React from "react";
import { cn } from "@/bibliotheque/utils";
import { Check } from "lucide-react";

export interface CheckboxProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  checked?: boolean;
  onCheckedChange?: (checked: boolean) => void;
}

const Checkbox = React.forwardRef<HTMLButtonElement, CheckboxProps>(
  ({ className, checked = false, onCheckedChange, disabled, ...props }, ref) => (
    <button
      ref={ref}
      type="button"
      role="checkbox"
      aria-checked={checked}
      disabled={disabled}
      data-state={checked ? "checked" : "unchecked"}
      className={cn(
        "peer h-4 w-4 shrink-0 rounded-sm border border-primary shadow",
        "focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring",
        "disabled:cursor-not-allowed disabled:opacity-50",
        "data-[state=checked]:bg-primary data-[state=checked]:text-primary-foreground",
        className
      )}
      onClick={() => onCheckedChange?.(!checked)}
      {...props}
    >
      {checked && <Check className="h-3.5 w-3.5" aria-hidden="true" />}
    </button>
  )
);
Checkbox.displayName = "Checkbox";

export { Checkbox };
