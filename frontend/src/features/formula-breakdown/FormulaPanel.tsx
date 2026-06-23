import { Code2 } from "lucide-react";
import { useSimulationStore } from "@/store/simulationStore";
import { formatValue } from "@/lib/utils";
import { cn } from "@/lib/utils";
import { useExplain } from "@/hooks/useExplain";

export function FormulaPanel() {
  const { session, resolvedValues } = useSimulationStore();
  const { explain } = useExplain();

  if (!session) return null;

  const formulaCells = session.cells.filter(
    (c) => c.type === "calculated" && c.formula
  );

  if (formulaCells.length === 0) return null;

  return (
    <section className="space-y-3">
      <div className="flex items-center gap-2">
        <Code2 className="h-4 w-4 text-brand-amber" />
        <h2 className="text-sm font-semibold text-surface-200">Formula Breakdown</h2>
        <span className="ml-auto rounded-full bg-surface-700 px-2 py-0.5 text-xs text-surface-400">
          {formulaCells.length} formulas
        </span>
      </div>

      <div className="rounded-xl border border-surface-700 bg-surface-800 overflow-hidden">
        <table className="w-full text-xs">
          <thead>
            <tr className="border-b border-surface-700">
              <th className="px-4 py-2.5 text-left font-semibold text-surface-600">Cell</th>
              <th className="px-4 py-2.5 text-left font-semibold text-surface-600">Label</th>
              <th className="px-4 py-2.5 text-left font-mono font-semibold text-surface-600">Formula</th>
              <th className="px-4 py-2.5 text-right font-semibold text-surface-600">Value</th>
            </tr>
          </thead>
          <tbody>
            {formulaCells.map((cell, i) => {
              const val = resolvedValues[cell.id] ?? cell.value;
              return (
                <tr
                  key={cell.id}
                  onClick={() => explain(cell)}
                  className={cn(
                    "cursor-pointer border-b border-surface-700/50 transition-colors hover:bg-surface-700/40",
                    i % 2 === 0 ? "bg-transparent" : "bg-surface-800/50"
                  )}
                >
                  <td className="px-4 py-2.5 font-mono text-surface-600">{cell.id.split("!")[1]}</td>
                  <td className="px-4 py-2.5 text-surface-400 max-w-[140px] truncate">{cell.label}</td>
                  <td className="px-4 py-2.5 font-mono text-brand-amber truncate max-w-[200px]">
                    {cell.formula?.raw}
                  </td>
                  <td className={cn(
                    "px-4 py-2.5 text-right font-mono font-semibold",
                    Number(val) > 0 ? "text-brand-emerald" : Number(val) < 0 ? "text-brand-rose" : "text-surface-400"
                  )}>
                    {formatValue(val as number | string | null, cell.data_type, cell.format_string)}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </section>
  );
}
