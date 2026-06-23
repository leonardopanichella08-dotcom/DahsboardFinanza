"""Basic smoke tests for the Excel parser."""
import tempfile
from pathlib import Path

import openpyxl
import pytest

from app.core.excel_parser import parse_excel
from app.models.cell import CellType


def _make_simple_workbook() -> Path:
    wb = openpyxl.Workbook()
    ws = wb.active
    ws["A1"] = "Revenue"
    ws["B1"] = 100_000
    ws["A2"] = "Cost"
    ws["B2"] = 40_000
    ws["A3"] = "Profit"
    ws["B3"] = "=B1-B2"

    tmp = tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False)
    wb.save(tmp.name)
    return Path(tmp.name)


def test_parse_detects_static_and_formula():
    path = _make_simple_workbook()
    try:
        sheet = parse_excel(path)
        types = {c.id.split("!")[1]: c.type for c in sheet.cells}
        assert types.get("B1") == CellType.STATIC
        assert types.get("B2") == CellType.STATIC
        assert types.get("B3") == CellType.CALCULATED
    finally:
        path.unlink(missing_ok=True)


def test_formula_dependencies():
    path = _make_simple_workbook()
    try:
        sheet = parse_excel(path)
        cell_map = {c.id.split("!")[1]: c for c in sheet.cells}
        b3 = cell_map["B3"]
        assert b3.formula is not None
        assert any("B1" in dep for dep in b3.formula.dependencies)
        assert any("B2" in dep for dep in b3.formula.dependencies)
    finally:
        path.unlink(missing_ok=True)


def test_resolve_formula_value():
    from app.core.formula_engine import resolve_values
    path = _make_simple_workbook()
    try:
        sheet = parse_excel(path)
        values = resolve_values(sheet)
        # Sheet1!B3 = B1 - B2 = 100_000 - 40_000 = 60_000
        b3_key = next(k for k in values if k.endswith("!B3"))
        assert values[b3_key] == 60_000
    finally:
        path.unlink(missing_ok=True)
