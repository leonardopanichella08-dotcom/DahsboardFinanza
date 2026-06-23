import { useState } from "react";
import { cn, formatValue } from "@/lib/utils";
import type { Cell } from "@/lib/types";
import { useSimulation } from "@/hooks/useSimulation";
import { useSimulationStore } from "@/store/simulationStore";
import { useExplain } from "@/hooks/useExplain";

interface InputSliderProps {
  cell: Cell;
}

export function InputSlider({ cell }: InputSliderProps) {
  const { updateInput } = useSimulation();
  const { overrides, resolvedValues } = useSimulationStore();
  const { explain } = useExplain();

  const currentValue = Number(overrides[cell.id] ?? resolvedValues[cell.id] ?? cell.value ?? 0);
  const [inputStr, setInputStr] = useState(String(currentValue));

  const isPercentage = cell.data_type === "percentage" || cell.format_string?.includes("%");
  const displayVal = formatValue(currentValue, cell.data_type, cell.format_string);

  // Derive a sensible slider range: ±300% of the base value
  const base = Number(cell.value) || 1;
  const min = base < 0 ? base * 4 : 0;
  const max = base < 0 ? 0 : base * 4;
  const step = isPercentage ? 0.001 : Math.max(1, Math.abs(base) / 1000);

  const commit = (raw: string) => {
    const n = parseFloat(raw);
    if (!isNaN(n)) updateInput(cell.id, n);
  };

  return (
    <div className="group rounded-lg border border-surface-700 bg-surface-800 p-3.5 space-y-2.5 hover:border-surface-600 transition-colors">
      <div className="flex items-center justify-between">
        <button
          onClick={() => explain(cell)}
          className="text-xs font-medium text-surface-400 hover:text-surface-200 text-left transition-colors"
        >
          {cell.label}
        </button>
        <span
          className={cn(
            "font-mono text-sm font-semibold",
            currentValue > 0 ? "text-brand-emerald" : currentValue < 0 ? "text-brand-rose" : "text-surface-200"
          )}
        >
          {displayVal}
        </span>
      </div>

      {/* Inline number input */}
      <input
        type="number"
        value={inputStr}
        onChange={(e) => setInputStr(e.target.value)}
        onBlur={() => commit(inputStr)}
        onKeyDown={(e) => e.key === "Enter" && commit(inputStr)}
        className="w-full rounded bg-surface-900 border border-surface-700 px-2.5 py-1.5 font-mono text-xs text-surface-200 focus:border-brand-indigo focus:outline-none"
      />

      {/* Slider */}
      <input
        type="range"
        min={min}
        max={max}
        step={step}
        value={currentValue}
        onChange={(e) => {
          const v = parseFloat(e.target.value);
          setInputStr(String(v));
          updateInput(cell.id, v);
        }}
        className="w-full accent-brand-indigo cursor-pointer"
      />
    </div>
  );
}
