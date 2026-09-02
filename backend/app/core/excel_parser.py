"""
Excel parser: ingests .xlsx and produces a ParsedSheet with full cell metadata.
Distinguishes static values from formula cells and builds a dependency graph.
"""
import io
import re
import zipfile
from pathlib import Path
from typing import Any, Optional
from xml.etree import ElementTree as ET

import openpyxl
from openpyxl.utils import get_column_letter, column_index_from_string
from openpyxl.utils.cell import coordinate_to_tuple

from app.models.cell import Cell, CellType, FormulaNode, ParsedSheet


def _strip_defined_names(file_path: Path) -> io.BytesIO:
    """
    Strip <definedNames> from workbook.xml inside the xlsx zip.
    Prevents openpyxl from raising ValueError on named ranges whose names
    coincidentally look like invalid column references (e.g. 'anno').
    """
    raw = file_path.read_bytes()
    buf_out = io.BytesIO()
    try:
        with zipfile.ZipFile(io.BytesIO(raw)) as zin, \
             zipfile.ZipFile(buf_out, "w", zipfile.ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                data = zin.read(item.filename)
                if item.filename in ("xl/workbook.xml", "xl/workbook.xml/"):
                    try:
                        ET.register_namespace("", "http://schemas.openxmlformats.org/spreadsheetml/2006/main")
                        ET.register_namespace("r", "http://schemas.openxmlformats.org/officeDocument/2006/relationships")
                        tree = ET.fromstring(data)
                        ns = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
                        for dn in tree.findall(f"{{{ns}}}definedNames"):
                            tree.remove(dn)
                        data = b'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n' + \
                               ET.tostring(tree, encoding="unicode").encode("utf-8")
                    except Exception:
                        pass
                zout.writestr(item, data)
        buf_out.seek(0)
        return buf_out
    except Exception:
        return io.BytesIO(raw)


# Excel formula token pattern — captures cell references like A1, $B$3, Sheet2!C4
_CELL_REF_RE = re.compile(
    r"(?:(?P<sheet>[A-Za-z0-9_]+)!)?\$?(?P<col>[A-Za-z]+)\$?(?P<row>\d+)"
)

# Heuristic: labels in adjacent cells (left or top) with text content
_LABEL_DATA_TYPES = {"s", "str", None}


def _cell_id(sheet_name: str, row: int, col: int) -> str:
    return f"{sheet_name}!{get_column_letter(col)}{row}"


def _extract_formula_dependencies(formula: str, current_sheet: str) -> list[str]:
    """Return list of cell ids that this formula references."""
    deps = []
    for match in _CELL_REF_RE.finditer(formula):
        col_letter = match.group("col").upper()
        # Excel columns are A–ZZZ (max 3 letters). Skip anything longer.
        if len(col_letter) > 3:
            continue
        try:
            col_idx = column_index_from_string(col_letter)
        except ValueError:
            continue
        sheet = match.group("sheet") or current_sheet
        row_num = int(match.group("row"))
        deps.append(_cell_id(sheet, row_num, col_idx))
    return list(dict.fromkeys(deps))  # deduplicate preserving order


def _translate_formula_to_python(formula: str, sheet_name: str) -> str:
    """
    Best-effort translation of an Excel formula string into a Python expression.
    The expression uses cell IDs as variable names (with ! replaced by __ and
    letters kept uppercase). Complex functions fall back to a placeholder.
    """
    expr = formula.lstrip("=")

    # Replace cell references with Python-safe variable names
    def _ref_to_var(m: re.Match) -> str:
        col_letter = m.group("col").upper()
        # Skip invalid column names (> 3 chars) — leave the token as-is
        if len(col_letter) > 3:
            return m.group(0)
        sheet = m.group("sheet") or sheet_name
        row_num = m.group("row")
        safe = f"{sheet}__{col_letter}{row_num}".replace(" ", "_")
        return safe

    expr = _CELL_REF_RE.sub(_ref_to_var, expr)

    # Map common Excel functions to Python equivalents
    excel_to_py = {
        r"\bSUM\b": "sum",
        r"\bAVERAGE\b": "sum",        # simplified; real avg needs count
        r"\bIF\b": "_if",
        r"\bAND\b": "_and",
        r"\bOR\b": "_or",
        r"\bNOT\b": "not ",
        r"\bMAX\b": "max",
        r"\bMIN\b": "min",
        r"\bABS\b": "abs",
        r"\bROUND\b": "round",
        r"\bINT\b": "int",
    }
    for pattern, replacement in excel_to_py.items():
        expr = re.sub(pattern, replacement, expr, flags=re.IGNORECASE)

    return expr


def _detect_data_type(cell: openpyxl.cell.Cell) -> str:
    """Infer a human-friendly data type from cell value and number format."""
    fmt = cell.number_format or ""
    if "%" in fmt:
        return "percentage"
    if any(c in fmt for c in ("$", "€", "£", "¥")):
        return "currency"
    if cell.data_type == "n" or isinstance(cell.value, (int, float)):
        return "number"
    return "text"


def _find_label(ws: openpyxl.worksheet.worksheet.Worksheet, row: int, col: int) -> str:
    """
    Look left then up for the nearest non-empty text cell to use as a label.
    Falls back to the cell coordinate string.
    """
    # Look left (same row, previous columns)
    for c in range(col - 1, max(col - 4, 0), -1):
        v = ws.cell(row=row, column=c).value
        if v and isinstance(v, str) and v.strip():
            return v.strip()
    # Look up (same column, previous rows)
    for r in range(row - 1, max(row - 4, 0), -1):
        v = ws.cell(row=r, column=col).value
        if v and isinstance(v, str) and v.strip():
            return v.strip()
    return f"{get_column_letter(col)}{row}"


def parse_excel(file_path: Path) -> ParsedSheet:
    # Strip problematic definedNames before loading (avoids 'not a valid column name' errors)
    cleaned = _strip_defined_names(file_path)

    try:
        wb = openpyxl.load_workbook(cleaned, data_only=False, keep_links=False)
    except Exception:
        cleaned.seek(0)
        wb = openpyxl.load_workbook(cleaned, data_only=True, keep_links=False)

    # Second pass with data_only=True to get pre-computed formula values from Excel
    try:
        cleaned.seek(0)
        wb_values = openpyxl.load_workbook(cleaned, data_only=True, keep_links=False)
        _cached_values: dict[str, Any] = {}
        for sname in wb_values.sheetnames:
            ws2 = wb_values[sname]
            for row2 in ws2.iter_rows():
                for c2 in row2:
                    if c2.value is not None:
                        _cached_values[_cell_id(sname, c2.row, c2.column)] = c2.value
    except Exception:
        _cached_values = {}
    cells: list[Cell] = []
    static_ids: list[str] = []
    calculated_ids: list[str] = []
    dep_graph: dict[str, list[str]] = {}

    for sheet_name in wb.sheetnames:
        ws = wb[sheet_name]
        for row in ws.iter_rows():
            for cell in row:
                if cell.value is None:
                    continue

                try:
                    r, c = cell.row, cell.column
                    cid = _cell_id(sheet_name, r, c)
                    raw_value = cell.value
                    is_formula = isinstance(raw_value, str) and raw_value.startswith("=")

                    if is_formula:
                        try:
                            deps = _extract_formula_dependencies(raw_value, sheet_name)
                        except Exception:
                            deps = []
                        try:
                            py_expr = _translate_formula_to_python(raw_value, sheet_name)
                        except Exception:
                            py_expr = "None"
                        formula_node = FormulaNode(
                            raw=raw_value,
                            dependencies=deps,
                            python_expr=py_expr,
                        )
                        cell_type = CellType.CALCULATED
                        calculated_ids.append(cid)
                        dep_graph[cid] = deps
                        # Use pre-computed value from Excel as initial display value
                        display_value = _cached_values.get(cid)
                    else:
                        formula_node = None
                        if isinstance(raw_value, str) and raw_value.strip():
                            cell_type = CellType.LABEL
                        else:
                            cell_type = CellType.STATIC
                            static_ids.append(cid)
                        display_value = raw_value

                    try:
                        label = _find_label(ws, r, c)
                    except Exception:
                        label = f"{get_column_letter(c)}{r}"
                    try:
                        data_type = _detect_data_type(cell)
                    except Exception:
                        data_type = "text"

                    cells.append(
                        Cell(
                            id=cid,
                            label=label,
                            value=display_value,
                            type=cell_type,
                            formula=formula_node,
                            row=r,
                            col=c,
                            sheet=sheet_name,
                            data_type=data_type,
                            format_string=cell.number_format or "General",
                        )
                    )
                except Exception:
                    # Skip any cell that causes unexpected errors
                    continue

    return ParsedSheet(
        filename=file_path.name,
        sheets=wb.sheetnames,
        cells=cells,
        static_cells=static_ids,
        calculated_cells=calculated_ids,
        dependency_graph=dep_graph,
    )
