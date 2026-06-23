import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import { useSimulationStore } from "@/store/simulationStore";
import { formatValue } from "@/lib/utils";

export function RevenueChart() {
  const { session, resolvedValues } = useSimulationStore();
  if (!session) return null;

  // Find revenue-ish and cost-ish cells heuristically
  const revKeywords = ["revenue", "sales", "income", "ricavi", "fatturato"];
  const costKeywords = ["cost", "expense", "spesa", "costo", "burn"];

  const revCells = session.cells.filter(
    (c) =>
      c.type !== "label" &&
      revKeywords.some((k) => c.label.toLowerCase().includes(k)) &&
      typeof (resolvedValues[c.id] ?? c.value) === "number"
  );
  const costCells = session.cells.filter(
    (c) =>
      c.type !== "label" &&
      costKeywords.some((k) => c.label.toLowerCase().includes(k)) &&
      typeof (resolvedValues[c.id] ?? c.value) === "number"
  );

  if (revCells.length === 0 && costCells.length === 0) return null;

  const allLabels = [
    ...new Set([...revCells.map((c) => c.label), ...costCells.map((c) => c.label)]),
  ].slice(0, 8);

  const data = allLabels.map((lbl) => {
    const rc = revCells.find((c) => c.label === lbl);
    const cc = costCells.find((c) => c.label === lbl);
    return {
      name: lbl.length > 12 ? lbl.slice(0, 12) + "…" : lbl,
      Revenue: rc ? Number(resolvedValues[rc.id] ?? rc.value ?? 0) : 0,
      Costs: cc ? Math.abs(Number(resolvedValues[cc.id] ?? cc.value ?? 0)) : 0,
    };
  });

  return (
    <div className="rounded-xl border border-surface-700 bg-surface-800 p-4 space-y-3">
      <p className="text-xs font-semibold text-surface-400 uppercase tracking-wider">
        Revenue vs Costs
      </p>
      <ResponsiveContainer width="100%" height={180}>
        <BarChart data={data} margin={{ top: 4, right: 8, left: 0, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
          <XAxis dataKey="name" tick={{ fill: "#475569", fontSize: 10 }} tickLine={false} axisLine={false} />
          <YAxis
            tick={{ fill: "#475569", fontSize: 10 }}
            tickLine={false}
            axisLine={false}
            tickFormatter={(v) => formatValue(v, "number")}
          />
          <Tooltip
            contentStyle={{ background: "#1e293b", border: "1px solid #334155", borderRadius: 8, fontSize: 12 }}
            labelStyle={{ color: "#94a3b8" }}
          />
          <Legend wrapperStyle={{ fontSize: 11, color: "#94a3b8" }} />
          <Bar dataKey="Revenue" fill="#10b981" radius={[4, 4, 0, 0]} />
          <Bar dataKey="Costs" fill="#f43f5e" radius={[4, 4, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
