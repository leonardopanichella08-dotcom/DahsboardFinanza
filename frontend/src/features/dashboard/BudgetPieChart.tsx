import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from "recharts";
import { useSimulationStore } from "@/store/simulationStore";
import { formatValue } from "@/lib/utils";

const COLORS = ["#6366f1", "#10b981", "#f59e0b", "#f43f5e", "#06b6d4", "#8b5cf6"];

export function BudgetPieChart() {
  const { session, resolvedValues } = useSimulationStore();
  if (!session) return null;

  // Take the top positive numeric static cells as budget slices
  const slices = session.cells
    .filter(
      (c) =>
        c.type === "static" &&
        typeof (resolvedValues[c.id] ?? c.value) === "number" &&
        Number(resolvedValues[c.id] ?? c.value) > 0
    )
    .map((c) => ({
      name: c.label.length > 16 ? c.label.slice(0, 16) + "…" : c.label,
      value: Number(resolvedValues[c.id] ?? c.value ?? 0),
    }))
    .sort((a, b) => b.value - a.value)
    .slice(0, 6);

  if (slices.length < 2) return null;

  return (
    <div className="rounded-xl border border-surface-700 bg-surface-800 p-4 space-y-3">
      <p className="text-xs font-semibold text-surface-400 uppercase tracking-wider">
        Budget Allocation
      </p>
      <div className="flex items-center gap-4">
        <ResponsiveContainer width="50%" height={140}>
          <PieChart>
            <Pie
              data={slices}
              cx="50%"
              cy="50%"
              innerRadius={38}
              outerRadius={60}
              dataKey="value"
              strokeWidth={0}
            >
              {slices.map((_, i) => (
                <Cell key={i} fill={COLORS[i % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip
              contentStyle={{ background: "#1e293b", border: "1px solid #334155", borderRadius: 8, fontSize: 12 }}
              formatter={(v: number) => [formatValue(v, "number"), ""]}
            />
          </PieChart>
        </ResponsiveContainer>
        <ul className="space-y-1.5 flex-1">
          {slices.map((s, i) => (
            <li key={i} className="flex items-center gap-2 text-xs text-surface-400">
              <span
                className="inline-block h-2 w-2 rounded-full shrink-0"
                style={{ background: COLORS[i % COLORS.length] }}
              />
              <span className="truncate">{s.name}</span>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
