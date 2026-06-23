import { useCallback } from "react";
import { explainCell } from "@/lib/api";
import { useSimulationStore } from "@/store/simulationStore";
import type { Cell } from "@/lib/types";

export function useExplain() {
  const { session, setExplanation, setExplaining, selectCell } =
    useSimulationStore();

  const explain = useCallback(
    async (cell: Cell) => {
      if (!session) return;
      selectCell(cell);
      setExplaining(true);
      try {
        const exp = await explainCell(session.session_id, cell.id);
        setExplanation(exp);
      } catch {
        setExplanation({
          cell_id: cell.id,
          what_it_means: "Could not fetch explanation — check your API key.",
          business_impact: "",
          sensitivity: "",
        });
      } finally {
        setExplaining(false);
      }
    },
    [session, selectCell, setExplaining, setExplanation]
  );

  return { explain };
}
