import { BarChart3, FileSpreadsheet, RotateCcw } from "lucide-react";
import { FileUpload } from "./FileUpload";
import { AIAssistant } from "./AIAssistant";
import { useSimulationStore } from "@/store/simulationStore";

export function Sidebar() {
  const { session, reset } = useSimulationStore();

  return (
    <aside className="flex h-full w-64 shrink-0 flex-col gap-5 border-r border-surface-700 bg-surface-900 p-4">
      {/* Logo */}
      <div className="flex items-center gap-2.5 px-1 py-2">
        <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-brand-indigo">
          <BarChart3 className="h-4 w-4 text-white" />
        </div>
        <span className="text-sm font-bold text-surface-200 tracking-tight">FinSim</span>
      </div>

      <div className="h-px bg-surface-700" />

      {/* File section */}
      <div className="space-y-2">
        <p className="px-1 text-[10px] font-semibold uppercase tracking-widest text-surface-600">
          Data Source
        </p>
        {session ? (
          <div className="space-y-2">
            <div className="flex items-center gap-2 rounded-lg bg-surface-800 px-3 py-2.5">
              <FileSpreadsheet className="h-4 w-4 shrink-0 text-brand-emerald" />
              <span className="truncate text-xs text-surface-400">{session.filename}</span>
            </div>
            <button
              onClick={reset}
              className="flex w-full items-center gap-2 rounded-lg px-3 py-2 text-xs text-surface-600 hover:bg-surface-800 hover:text-surface-400 transition-colors"
            >
              <RotateCcw className="h-3.5 w-3.5" />
              Load new file
            </button>
          </div>
        ) : (
          <FileUpload />
        )}
      </div>

      <div className="h-px bg-surface-700" />

      {/* AI Assistant */}
      <div className="space-y-2 flex-1">
        <p className="px-1 text-[10px] font-semibold uppercase tracking-widest text-surface-600">
          AI Assistant
        </p>
        <AIAssistant />
      </div>

      {/* Footer */}
      <div className="px-1">
        <p className="text-[10px] text-surface-700">
          Powered by Claude · All calculations client-side
        </p>
      </div>
    </aside>
  );
}
