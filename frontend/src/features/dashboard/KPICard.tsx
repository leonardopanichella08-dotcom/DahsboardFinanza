import { Sparkles } from "lucide-react";
import { cn, formatValue, getValueColor } from "@/lib/utils";
import type { Cell, SyntheticMetric } from "@/lib/types";
import { useExplain } from "@/hooks/useExplain";
import { useSimulationStore } from "@/store/simulationStore";

interface KPICardProps {
  cell?: Cell;
  synthetic?: SyntheticMetric;
}

export function KPICard({ cell, synthetic }: KPICardProps) {
  const { explain } = useExplain();
  const { resolvedValues } = useSimulationStore();

  const label = cell?.label ?? synthetic?.label ?? "";
  const rawValue = cell
    ? (resolvedValues[cell.id] ?? cell.value)
    : synthetic?.value;
  const dataType = cell?.data_type ?? null;
  const formatStr = cell?.format_string ?? null;
  const isAI = synthetic?.is_ai_generated ?? false;

  const displayVal = formatValue(rawValue as number | string | null, dataType, formatStr);
  const valueColor = getValueColor(rawValue as number | null);

  const handleClick = () => {
    if (cell) explain(cell);
  };

  return (
    <button
      onClick={handleClick}
      disabled={!cell}
      className={cn(
        "group relative rounded-xl border bg-surface-800 p-4 text-left transition-all",
        cell
          ? "border-surface-700 hover:border-brand-indigo/60 hover:bg-surface-700/50 cursor-pointer"
          : "border-surface-700/50 cursor-default"
      )}
    >
      {isAI && (
        <span className="absolute right-3 top-3 flex items-center gap-1 rounded-full bg-brand-indigo/20 px-2 py-0.5 text-[10px] font-medium text-brand-indigo">
          <Sparkles className="h-2.5 w-2.5" />
          AI
        </span>
      )}

      <p className="text-xs text-surface-600 truncate pr-8">{label}</p>
      <p className={cn("mt-1.5 font-mono text-xl font-bold tracking-tight", valueColor)}>
        {displayVal}
      </p>

      {synthetic && (
        <p className="mt-2 text-[10px] leading-relaxed text-surface-600 line-clamp-2">
          {synthetic.formula_used}
        </p>
      )}
    </button>
  );
}
