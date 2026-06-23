import { useRef, useState } from "react";
import { Upload, FileSpreadsheet, AlertCircle } from "lucide-react";
import { cn } from "@/lib/utils";
import { useSimulation } from "@/hooks/useSimulation";
import { useSimulationStore } from "@/store/simulationStore";

export function FileUpload() {
  const { upload } = useSimulation();
  const { isLoading, uploadError } = useSimulationStore();
  const [dragging, setDragging] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleFile = (file: File) => {
    if (!file.name.endsWith(".xlsx")) return;
    upload(file);
  };

  return (
    <div className="space-y-3">
      <button
        onClick={() => inputRef.current?.click()}
        onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
        onDragLeave={() => setDragging(false)}
        onDrop={(e) => {
          e.preventDefault();
          setDragging(false);
          const file = e.dataTransfer.files[0];
          if (file) handleFile(file);
        }}
        disabled={isLoading}
        className={cn(
          "w-full rounded-lg border-2 border-dashed p-6 text-center transition-all",
          dragging
            ? "border-brand-indigo bg-brand-indigo/10"
            : "border-surface-700 hover:border-surface-600 hover:bg-surface-700/30",
          isLoading && "opacity-50 cursor-not-allowed"
        )}
      >
        <div className="flex flex-col items-center gap-2">
          {isLoading ? (
            <div className="h-8 w-8 rounded-full border-2 border-brand-indigo border-t-transparent animate-spin" />
          ) : (
            <Upload className="h-8 w-8 text-surface-400" />
          )}
          <p className="text-sm font-medium text-surface-200">
            {isLoading ? "Parsing…" : "Drop your Excel file"}
          </p>
          <p className="text-xs text-surface-600">.xlsx · max 10 MB</p>
        </div>
      </button>

      <input
        ref={inputRef}
        type="file"
        accept=".xlsx"
        className="hidden"
        onChange={(e) => {
          const file = e.target.files?.[0];
          if (file) handleFile(file);
          e.target.value = "";
        }}
      />

      {uploadError && (
        <div className="flex items-start gap-2 rounded-md bg-brand-rose/10 p-3 text-xs text-brand-rose">
          <AlertCircle className="mt-0.5 h-3.5 w-3.5 shrink-0" />
          <span>{uploadError}</span>
        </div>
      )}
    </div>
  );
}
