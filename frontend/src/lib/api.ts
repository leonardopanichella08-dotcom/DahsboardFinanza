import type { ExplainResponse, ParsedSession, SimulationResult } from "./types";

const BASE = "/api";

export async function uploadExcel(file: File): Promise<ParsedSession> {
  const form = new FormData();
  form.append("file", file);
  const res = await fetch(`${BASE}/upload`, { method: "POST", body: form });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail ?? "Upload failed");
  }
  return res.json();
}

export async function runSimulation(
  sessionId: string,
  overrides: Record<string, number | string>
): Promise<SimulationResult> {
  const res = await fetch(`${BASE}/simulate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ session_id: sessionId, overrides }),
  });
  if (!res.ok) throw new Error("Simulation failed");
  return res.json();
}

export async function explainCell(
  sessionId: string,
  cellId: string
): Promise<ExplainResponse> {
  const encoded = encodeURIComponent(cellId);
  const res = await fetch(`${BASE}/explain/${sessionId}/${encoded}`);
  if (!res.ok) throw new Error("Explanation failed");
  return res.json();
}
