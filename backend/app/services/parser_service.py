"""
Orchestrates: parse → resolve values → synthesize metrics → return full session data.
"""
import uuid
from pathlib import Path
from typing import Any

from app.core.excel_parser import parse_excel
from app.core.formula_engine import resolve_values
from app.core.metric_synthesizer import synthesize_metrics
from app.models.cell import ParsedSheet


# In-memory session store (replace with Redis in production)
_sessions: dict[str, dict[str, Any]] = {}


def create_session(file_path: Path) -> dict[str, Any]:
    sheet = parse_excel(file_path)
    resolved = resolve_values(sheet)

    # Patch resolved values back into cells
    cell_map = {c.id: c for c in sheet.cells}
    for cid, val in resolved.items():
        if cid in cell_map and cell_map[cid].value is None:
            cell_map[cid].value = val

    # Build label_values for metric synthesis
    label_values: dict[str, tuple[str, Any]] = {
        c.id: (c.label, resolved.get(c.id, c.value))
        for c in sheet.cells
    }
    synthetic = synthesize_metrics(label_values)

    session_id = str(uuid.uuid4())
    _sessions[session_id] = {
        "sheet": sheet,
        "resolved": resolved,
        "synthetic_metrics": synthetic,
    }

    return {
        "session_id": session_id,
        "filename": sheet.filename,
        "sheets": sheet.sheets,
        "cells": [c.model_dump() for c in sheet.cells],
        "static_cells": sheet.static_cells,
        "calculated_cells": sheet.calculated_cells,
        "resolved_values": resolved,
        "dependency_graph": sheet.dependency_graph,
        "synthetic_metrics": [m.model_dump() for m in synthetic],
    }


def get_session(session_id: str) -> dict[str, Any] | None:
    return _sessions.get(session_id)
