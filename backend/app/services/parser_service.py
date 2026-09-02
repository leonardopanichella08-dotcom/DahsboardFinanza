"""
Orchestrates: parse → resolve values → synthesize metrics → return full session data.
Falls back to pandas reader if openpyxl cannot load the file.
"""
import io
import uuid
from pathlib import Path
from typing import Any

import pandas as pd

from app.core.excel_parser import parse_excel
from app.core.formula_engine import resolve_values
from app.core.metric_synthesizer import synthesize_metrics
from app.core.smart_extractor import (
    extract_business_metrics,
    extract_time_series,
    extract_scenario_params,
)
from app.models.cell import Cell, CellType, ParsedSheet


# In-memory session store (replace with Redis in production)
_sessions: dict[str, dict[str, Any]] = {}


def _pandas_fallback(file_path: Path) -> dict[str, Any]:
    """
    When openpyxl cannot parse the file, fall back to pandas using the
    stripped (definedNames-free) version of the xlsx.
    """
    from app.core.excel_parser import _strip_defined_names
    cleaned = _strip_defined_names(file_path)
    xl = pd.ExcelFile(cleaned, engine="openpyxl")
    cells: list[Cell] = []
    static_ids: list[str] = []

    for sheet_name in xl.sheet_names:
        df = xl.parse(sheet_name, header=None)
        df = df.where(pd.notnull(df), None)
        for row_idx, row in df.iterrows():
            for col_idx, val in enumerate(row):
                if val is None:
                    continue
                r = int(row_idx) + 1
                c = int(col_idx) + 1
                from openpyxl.utils import get_column_letter
                cid = f"{sheet_name}!{get_column_letter(c)}{r}"
                if isinstance(val, str) and val.strip():
                    ctype = CellType.LABEL
                elif isinstance(val, (int, float)):
                    ctype = CellType.STATIC
                    static_ids.append(cid)
                else:
                    ctype = CellType.STATIC
                    static_ids.append(cid)
                cells.append(Cell(
                    id=cid, label=str(val)[:60], value=val,
                    type=ctype, formula=None,
                    row=r, col=c, sheet=sheet_name,
                    data_type="number" if isinstance(val, (int, float)) else "text",
                    format_string="General",
                ))

    sheet = ParsedSheet(
        filename=file_path.name,
        sheets=xl.sheet_names,
        cells=cells,
        static_cells=static_ids,
        calculated_cells=[],
        dependency_graph={},
    )
    label_values = {c.id: (c.label, c.value) for c in cells}
    synthetic = synthesize_metrics(label_values)
    resolved = {c.id: c.value for c in cells if c.value is not None}

    session_id = str(uuid.uuid4())
    _sessions[session_id] = {"sheet": sheet, "resolved": resolved, "synthetic_metrics": synthetic}
    return {
        "session_id": session_id,
        "filename": sheet.filename,
        "sheets": sheet.sheets,
        "cells": [c.model_dump() for c in sheet.cells],
        "static_cells": sheet.static_cells,
        "calculated_cells": sheet.calculated_cells,
        "resolved_values": resolved,
        "dependency_graph": {},
        "synthetic_metrics": [m.model_dump() for m in synthetic],
    }


def create_session(file_path: Path) -> dict[str, Any]:
    try:
        sheet = parse_excel(file_path)
        resolved = resolve_values(sheet)

        # Patch resolved values back into cells
        cell_map = {c.id: c for c in sheet.cells}
        for cid, val in resolved.items():
            if cid in cell_map and cell_map[cid].value is None:
                cell_map[cid].value = val

        label_values: dict[str, tuple[str, Any]] = {
            c.id: (c.label, resolved.get(c.id, c.value))
            for c in sheet.cells
        }
        synthetic = synthesize_metrics(label_values)

        session_id = str(uuid.uuid4())
        _sessions[session_id] = {"sheet": sheet, "resolved": resolved, "synthetic_metrics": synthetic}

        cells_dicts = [c.model_dump() for c in sheet.cells]

        # Smart business intelligence layer
        business_kpis    = extract_business_metrics(cells_dicts, resolved)
        time_series      = extract_time_series(cells_dicts, resolved)
        scenario_params  = extract_scenario_params(cells_dicts, resolved, sheet.dependency_graph)

        return {
            "session_id":      session_id,
            "filename":        sheet.filename,
            "sheets":          sheet.sheets,
            "cells":           cells_dicts,
            "static_cells":    sheet.static_cells,
            "calculated_cells":sheet.calculated_cells,
            "resolved_values": resolved,
            "dependency_graph":sheet.dependency_graph,
            "synthetic_metrics": [m.model_dump() for m in synthetic],
            # New investor-grade data
            "business_kpis":   business_kpis,
            "time_series":     time_series,
            "scenario_params": scenario_params,
        }
    except Exception:
        # openpyxl failed (e.g. named ranges with invalid column names) → pandas fallback
        return _pandas_fallback(file_path)


def get_session(session_id: str) -> dict[str, Any] | None:
    return _sessions.get(session_id)
