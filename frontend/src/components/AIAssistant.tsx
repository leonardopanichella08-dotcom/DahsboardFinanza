import { Bot, TrendingUp, TrendingDown, HelpCircle, X } from "lucide-react";
import { useSimulationStore } from "@/store/simulationStore";
import { cn } from "@/lib/utils";

export function AIAssistant() {
  const { selectedCell, explanation, isExplaining, selectCell } =
    useSimulationStore();

  if (!selectedCell && !isExplaining) {
    return (
      <div className="flex flex-col items-center gap-3 rounded-lg bg-surface-800 p-5 text-center">
        <div className="flex h-10 w-10 items-center justify-center rounded-full bg-brand-indigo/20">
          <Bot className="h-5 w-5 text-brand-indigo" />
        </div>
        <p className="text-sm font-medium text-surface-200">Ask the Assistant</p>
        <p className="text-xs text-surface-600">
          Click any metric or KPI card to get a plain-English explanation.
        </p>
      </div>
    );
  }

  return (
    <div className="rounded-lg border border-surface-700 bg-surface-800 overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-surface-700 px-4 py-3">
        <div className="flex items-center gap-2">
          <Bot className="h-4 w-4 text-brand-indigo" />
          <span className="text-sm font-semibold text-surface-200">
            {selectedCell?.label ?? "…"}
          </span>
        </div>
        <button
          onClick={() => selectCell(null)}
          className="rounded p-1 text-surface-600 hover:text-surface-400"
        >
          <X className="h-3.5 w-3.5" />
        </button>
      </div>

      {/* Body */}
      <div className="p-4 space-y-4">
        {isExplaining ? (
          <div className="space-y-2.5">
            {[80, 60, 90].map((w, i) => (
              <div
                key={i}
                className="h-3 rounded animate-shimmer bg-gradient-to-r from-surface-700 via-surface-600 to-surface-700 bg-[length:200%_100%]"
                style={{ width: `${w}%` }}
              />
            ))}
          </div>
        ) : explanation ? (
          <>
            <Section icon={<HelpCircle className="h-3.5 w-3.5" />} title="What it means">
              {explanation.what_it_means}
            </Section>
            <Section icon={<TrendingUp className="h-3.5 w-3.5" />} title="Business impact">
              {explanation.business_impact}
            </Section>
            <Section icon={<TrendingDown className="h-3.5 w-3.5" />} title="Sensitivity">
              {explanation.sensitivity}
            </Section>
          </>
        ) : null}
      </div>
    </div>
  );
}

function Section({
  icon,
  title,
  children,
}: {
  icon: React.ReactNode;
  title: string;
  children: React.ReactNode;
}) {
  return (
    <div className="space-y-1.5">
      <div className="flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wider text-surface-600">
        {icon}
        {title}
      </div>
      <p className="text-xs leading-relaxed text-surface-400">{children}</p>
    </div>
  );
}
