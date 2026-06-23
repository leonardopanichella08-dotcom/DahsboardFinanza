from typing import Any, Optional
from pydantic import BaseModel


class SimulationInput(BaseModel):
    session_id: str
    overrides: dict[str, Any]  # cell_id -> new value


class SimulationResult(BaseModel):
    session_id: str
    values: dict[str, Any]       # cell_id -> recalculated value
    changed_cells: list[str]


class SyntheticMetric(BaseModel):
    id: str
    label: str
    value: Any
    formula_used: str
    explanation: str
    why_it_matters: str
    source_cells: list[str]
    is_ai_generated: bool = True


class ExplainRequest(BaseModel):
    cell_id: str
    label: str
    value: Any
    context_cells: Optional[dict[str, Any]] = None


class ExplainResponse(BaseModel):
    cell_id: str
    what_it_means: str
    business_impact: str
    sensitivity: str             # "what happens if it goes up/down"
