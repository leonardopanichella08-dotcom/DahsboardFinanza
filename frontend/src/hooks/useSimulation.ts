import { useCallback } from "react";
import { runSimulation, uploadExcel } from "@/lib/api";
import { useSimulationStore } from "@/store/simulationStore";

export function useSimulation() {
  const {
    session,
    overrides,
    setSession,
    setResolvedValues,
    applyOverride,
    setLoading,
    setUploadError,
  } = useSimulationStore();

  const upload = useCallback(async (file: File) => {
    setLoading(true);
    setUploadError(null);
    try {
      const parsed = await uploadExcel(file);
      setSession(parsed);
    } catch (e) {
      setUploadError(e instanceof Error ? e.message : "Upload failed");
    } finally {
      setLoading(false);
    }
  }, [setLoading, setUploadError, setSession]);

  const updateInput = useCallback(
    async (cellId: string, value: number | string) => {
      if (!session) return;
      applyOverride(cellId, value);
      const newOverrides = { ...overrides, [cellId]: value };
      try {
        const result = await runSimulation(session.session_id, newOverrides);
        setResolvedValues(result.values);
      } catch {
        // Silent — the override is still stored locally
      }
    },
    [session, overrides, applyOverride, setResolvedValues]
  );

  return { upload, updateInput };
}
