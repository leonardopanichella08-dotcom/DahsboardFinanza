import { create } from "zustand";
import type { Cell, ExplainResponse, ParsedSession, SyntheticMetric } from "@/lib/types";

interface SimulationStore {
  // Session state
  session: ParsedSession | null;
  resolvedValues: Record<string, number | string | null>;
  overrides: Record<string, number | string>;
  isLoading: boolean;
  uploadError: string | null;

  // AI Assistant state
  selectedCell: Cell | null;
  explanation: ExplainResponse | null;
  isExplaining: boolean;

  // Actions
  setSession: (session: ParsedSession) => void;
  setResolvedValues: (values: Record<string, number | string | null>) => void;
  applyOverride: (cellId: string, value: number | string) => void;
  setLoading: (v: boolean) => void;
  setUploadError: (msg: string | null) => void;
  selectCell: (cell: Cell | null) => void;
  setExplanation: (exp: ExplainResponse | null) => void;
  setExplaining: (v: boolean) => void;
  reset: () => void;
}

const initialState = {
  session: null,
  resolvedValues: {},
  overrides: {},
  isLoading: false,
  uploadError: null,
  selectedCell: null,
  explanation: null,
  isExplaining: false,
};

export const useSimulationStore = create<SimulationStore>((set) => ({
  ...initialState,

  setSession: (session) =>
    set({ session, resolvedValues: session.resolved_values }),

  setResolvedValues: (values) => set({ resolvedValues: values }),

  applyOverride: (cellId, value) =>
    set((s) => ({ overrides: { ...s.overrides, [cellId]: value } })),

  setLoading: (v) => set({ isLoading: v }),
  setUploadError: (msg) => set({ uploadError: msg }),
  selectCell: (cell) => set({ selectedCell: cell, explanation: null }),
  setExplanation: (exp) => set({ explanation: exp }),
  setExplaining: (v) => set({ isExplaining: v }),
  reset: () => set(initialState),
}));
