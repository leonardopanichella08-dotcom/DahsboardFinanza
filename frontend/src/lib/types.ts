export type CellType = "static" | "calculated" | "label";
export type DataType = "number" | "currency" | "percentage" | "text";

export interface FormulaNode {
  raw: string;
  dependencies: string[];
  python_expr: string | null;
}

export interface Cell {
  id: string;
  label: string;
  value: number | string | null;
  type: CellType;
  formula: FormulaNode | null;
  row: number;
  col: number;
  sheet: string;
  data_type: DataType | null;
  format_string: string | null;
}

export interface SyntheticMetric {
  id: string;
  label: string;
  value: number | string;
  formula_used: string;
  explanation: string;
  why_it_matters: string;
  source_cells: string[];
  is_ai_generated: boolean;
}

export interface ParsedSession {
  session_id: string;
  filename: string;
  sheets: string[];
  cells: Cell[];
  static_cells: string[];
  calculated_cells: string[];
  resolved_values: Record<string, number | string | null>;
  dependency_graph: Record<string, string[]>;
  synthetic_metrics: SyntheticMetric[];
}

export interface SimulationResult {
  session_id: string;
  values: Record<string, number | string | null>;
  changed_cells: string[];
}

export interface ExplainResponse {
  cell_id: string;
  what_it_means: string;
  business_impact: string;
  sensitivity: string;
}
