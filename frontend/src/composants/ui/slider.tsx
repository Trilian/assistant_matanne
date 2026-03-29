"use client";

import * as React from "react";
import { cn } from "@/bibliotheque/utils";

export interface SliderProps {
  className?: string;
  id?: string;
  value?: number[];
  defaultValue?: number[];
  min?: number;
  max?: number;
  step?: number;
  onValueChange?: (value: number[]) => void;
  disabled?: boolean;
}

const Slider = React.forwardRef<HTMLDivElement, SliderProps>(
  (
    {
      className,
      value,
      defaultValue = [0],
      min = 0,
      max = 100,
      step = 1,
      onValueChange,
      disabled,
      ...props
    },
    ref
  ) => {
    const [internalValue, setInternalValue] = React.useState<number[]>(defaultValue);
    const current = value ?? internalValue;

    function handleChange(e: React.ChangeEvent<HTMLInputElement>, index: number) {
      const next = current.map((v, i) => (i === index ? Number(e.target.value) : v));
      setInternalValue(next);
      onValueChange?.(next);
    }

    const pct = ((current[0] - min) / (max - min)) * 100;

    return (
      <div
        ref={ref}
        className={cn("relative flex w-full touch-none select-none items-center", className)}
        {...props}
      >
        <div className="relative h-1.5 w-full grow overflow-hidden rounded-full bg-secondary">
          <div
            aria-hidden="true"
            className="absolute h-full bg-primary"
            style={{ width: `${pct}%` }}
          />
        </div>
        <input
          type="range"
          min={min}
          max={max}
          step={step}
          value={current[0]}
          disabled={disabled}
          onChange={(e) => handleChange(e, 0)}
          className="absolute w-full opacity-0 cursor-pointer h-1.5 disabled:cursor-not-allowed"
          aria-valuenow={current[0]}
          aria-valuemin={min}
          aria-valuemax={max}
        />
        <div
          aria-hidden="true"
          className="absolute h-4 w-4 rounded-full border border-primary/50 bg-background shadow transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50"
          style={{ left: `calc(${pct}% - 8px)` }}
        />
      </div>
    );
  }
);
Slider.displayName = "Slider";

export { Slider };
