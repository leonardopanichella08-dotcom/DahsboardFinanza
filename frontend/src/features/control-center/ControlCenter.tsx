import { SlidersHorizontal } from "lucide-react";
import { useSimulationStore } from "@/store/simulationStore";
import { InputSlider } from "./InputSlider";

export function ControlCenter() {
  const { session, resolvedValues } = useSimulationStore();

  if (!session) return null;

  const staticCells = session.cells.filter(
    (c) =>
      c.type === "static" &&
      session.static_cells.includes(c.id) &&
      typeof (resolvedValues[c.id] ?? c.value) === "number"
  );

  if (staticCells.length === 0) {
    return (
      <div className="rounded-lg border border-surface-700 bg-surface-800 p-5 text-center">
        <p className="text-sm text-surface-600">No numeric input cells detected.</p>
      </div>
    );
  }

  return (
    <section className="space-y-3">
      <div className="flex items-center gap-2">
        <SlidersHorizontal className="h-4 w-4 text-brand-indigo" />
        <h2 className="text-sm font-semibold text-surface-200">Control Center</h2>
        <span className="ml-auto rounded-full bg-surface-700 px-2 py-0.5 text-xs text-surface-400">
          {staticCells.length} inputs
        </span>
      </div>
      <div className="grid gap-2.5 sm:grid-cols-2">
        {staticCells.map((cell) => (
          <InputSlider key={cell.id} cell={cell} />
        ))}
      </div>
    </section>
  );
}
