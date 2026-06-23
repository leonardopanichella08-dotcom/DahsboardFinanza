import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import { useSimulationStore } from "@/store/simulationStore";
import { formatValue } from "@/lib/utils";

export function CashflowChart() {
  const { session, resolvedValues } = useSimulationStore();

  if (!session) return null;

  // Collect cells that look like periodic cash-flow rows (monthly/quarterly)
  // Group by row, picking numeric calculated or static cells
  const numericCells = session.cells.filter(
    (c) =>
      c.type !== "label" &&
      typeof (resolvedValues[c.id] ?? c.value) === "number"
  );

  // Use column index as period proxy — group by column, sum values per column
  const byCol: Record<number, number> = {};
  numericCells.forEach((c) => {
    const val = Number(resolvedValues[c.id] ?? c.value ?? 0);
    byCol[c.col] = (byCol[c.col] ?? 0) + val;
  });

  const data = Object.entries(byCol)
    .sort(([a], [b]) => Number(a) - Number(b))
    .slice(0, 24)
    .map(([col, total], i) => ({
      period: `P${i + 1}`,
      value: total,
    }));

  if (data.length < 2) return null;

  const hasNegative = data.some((d) => d.value < 0);

  return (
    <div className="rounded-xl border border-surface-700 bg-surface-800 p-4 space-y-3">
      <p className="text-xs font-semibold text-surface-400 uppercase tracking-wider">
        Cumulative Value by Period
      </p>
      <ResponsiveContainer width="100%" height={180}>
        <AreaChart data={data} margin={{ top: 4, right: 8, left: 0, bottom: 0 }}>
          <defs>
            <linearGradient id="grad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#6366f1" stopOpacity={0.3} />
              <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
          <XAxis dataKey="period" tick={{ fill: "#475569", fontSize: 10 }} tickLine={false} axisLine={false} />
          <YAxis
            tick={{ fill: "#475569", fontSize: 10 }}
            tickLine={false}
            axisLine={false}
            tickFormatter={(v) => formatValue(v, "number")}
          />
          <Tooltip
            contentStyle={{ background: "#1e293b", border: "1px solid #334155", borderRadius: 8, fontSize: 12 }}
            labelStyle={{ color: "#94a3b8" }}
            itemStyle={{ color: "#6366f1" }}
            formatter={(v: number) => [formatValue(v, "number"), "Value"]}
          />
          <Area
            type="monotone"
            dataKey="value"
            stroke="#6366f1"
            strokeWidth={2}
            fill="url(#grad)"
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
