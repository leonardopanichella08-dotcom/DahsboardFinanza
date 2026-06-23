import { Sidebar } from "@/components/Sidebar";
import { ControlCenter } from "@/features/control-center/ControlCenter";
import { KPICard } from "@/features/dashboard/KPICard";
import { CashflowChart } from "@/features/dashboard/CashflowChart";
import { RevenueChart } from "@/features/dashboard/RevenueChart";
import { BudgetPieChart } from "@/features/dashboard/BudgetPieChart";
import { FormulaPanel } from "@/features/formula-breakdown/FormulaPanel";
import { useSimulationStore } from "@/store/simulationStore";
import { BarChart3, Sparkles } from "lucide-react";

export default function App() {
  const { session } = useSimulationStore();

  return (
    <div className="flex h-screen bg-surface-900 text-surface-200 overflow-hidden font-sans">
      <Sidebar />

      <main className="flex-1 overflow-y-auto">
        {!session ? (
          <EmptyState />
        ) : (
          <Dashboard />
        )}
      </main>
    </div>
  );
}

function EmptyState() {
  return (
    <div className="flex h-full flex-col items-center justify-center gap-5 p-8 text-center">
      <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-surface-800 border border-surface-700">
        <BarChart3 className="h-8 w-8 text-surface-600" />
      </div>
      <div className="space-y-2 max-w-sm">
        <h1 className="text-xl font-bold text-surface-200">Financial Simulation Dashboard</h1>
        <p className="text-sm text-surface-600 leading-relaxed">
          Upload an Excel financial model to get interactive sliders, real-time KPI recalculation,
          AI-generated metrics, and plain-English explanations.
        </p>
      </div>
      <div className="flex gap-4 text-xs text-surface-700">
        <span>What-If Analysis</span>
        <span>·</span>
        <span>Formula Breakdown</span>
        <span>·</span>
        <span>AI Glossary</span>
      </div>
    </div>
  );
}

function Dashboard() {
  const { session } = useSimulationStore();
  if (!session) return null;

  // Top KPI cells: calculated cells or high-value static cells
  const kpiCells = session.cells
    .filter(
      (c) =>
        (c.type === "calculated" || c.type === "static") &&
        c.data_type !== "text"
    )
    .slice(0, 8);

  return (
    <div className="p-6 space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-lg font-bold text-surface-200">{session.filename}</h1>
          <p className="text-xs text-surface-600 mt-0.5">
            {session.static_cells.length} inputs · {session.calculated_cells.length} formulas · {session.sheets.join(", ")}
          </p>
        </div>
        {session.synthetic_metrics.length > 0 && (
          <span className="flex items-center gap-1.5 rounded-full bg-brand-indigo/20 px-3 py-1 text-xs font-medium text-brand-indigo">
            <Sparkles className="h-3 w-3" />
            {session.synthetic_metrics.length} AI metrics generated
          </span>
        )}
      </div>

      {/* KPI Cards */}
      {kpiCells.length > 0 && (
        <section className="space-y-3">
          <h2 className="text-xs font-semibold uppercase tracking-wider text-surface-600">
            Financial Performance
          </h2>
          <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-4">
            {kpiCells.map((cell) => (
              <KPICard key={cell.id} cell={cell} />
            ))}
            {session.synthetic_metrics.map((m) => (
              <KPICard key={m.id} synthetic={m} />
            ))}
          </div>
        </section>
      )}

      {/* Charts */}
      <section className="space-y-3">
        <h2 className="text-xs font-semibold uppercase tracking-wider text-surface-600">
          Visualizations
        </h2>
        <div className="grid gap-4 lg:grid-cols-2">
          <CashflowChart />
          <RevenueChart />
          <BudgetPieChart />
        </div>
      </section>

      {/* Control Center */}
      <ControlCenter />

      {/* Formula Breakdown */}
      <FormulaPanel />
    </div>
  );
}
