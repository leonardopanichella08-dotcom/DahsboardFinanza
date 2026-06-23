from typing import Any

from app.llm.claude_client import call_claude
from app.llm.prompts import explain_metric_prompt, formula_explanation_prompt
from app.models.simulation import ExplainResponse
from app.services.parser_service import get_session


async def explain_cell(
    session_id: str,
    cell_id: str,
    api_key: str,
) -> ExplainResponse:
    session = get_session(session_id)
    if session is None:
        raise KeyError(f"Session {session_id!r} not found")

    sheet = session["sheet"]
    resolved = session["resolved"]
    cell_map = {c.id: c for c in sheet.cells}
    cell = cell_map.get(cell_id)

    if cell is None:
        raise ValueError(f"Cell {cell_id!r} not found in session")

    current_value = resolved.get(cell_id, cell.value)

    # Build context from neighbouring cells
    context_snippets = []
    for dep_id in (cell.formula.dependencies if cell.formula else [])[:5]:
        dep = cell_map.get(dep_id)
        if dep:
            context_snippets.append(f"{dep.label}={resolved.get(dep_id, dep.value)}")
    context_str = ", ".join(context_snippets) or "no context available"

    if cell.formula:
        prompt = formula_explanation_prompt(
            formula=cell.formula.raw,
            label=cell.label,
            dependencies=[cell_map[d].label for d in cell.formula.dependencies if d in cell_map],
        )
        raw = await call_claude(prompt, api_key)
        return ExplainResponse(
            cell_id=cell_id,
            what_it_means=raw.get("plain_english", ""),
            business_impact=raw.get("step_by_step", ""),
            sensitivity=raw.get("common_pitfalls", ""),
        )
    else:
        prompt = explain_metric_prompt(
            label=cell.label,
            value=str(current_value),
            data_type=cell.data_type or "number",
            context=context_str,
        )
        raw = await call_claude(prompt, api_key)
        return ExplainResponse(
            cell_id=cell_id,
            what_it_means=raw.get("what_it_means", ""),
            business_impact=raw.get("business_impact", ""),
            sensitivity=raw.get("sensitivity", ""),
        )
