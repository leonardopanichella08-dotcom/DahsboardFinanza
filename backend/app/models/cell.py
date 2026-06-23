from enum import Enum
from typing import Any, Optional
from pydantic import BaseModel


class CellType(str, Enum):
    STATIC = "static"
    CALCULATED = "calculated"
    LABEL = "label"


class FormulaNode(BaseModel):
    raw: str
    dependencies: list[str] = []
    python_expr: Optional[str] = None


class Cell(BaseModel):
    id: str                          # e.g. "Sheet1!B3"
    label: str                       # nearest left/top label text
    value: Any                       # current resolved value
    type: CellType
    formula: Optional[FormulaNode] = None
    row: int
    col: int
    sheet: str
    data_type: Optional[str] = None  # number, currency, percentage, text
    format_string: Optional[str] = None


class ParsedSheet(BaseModel):
    filename: str
    sheets: list[str]
    cells: list[Cell]
    static_cells: list[str]          # ids of static input cells
    calculated_cells: list[str]      # ids of formula cells
    dependency_graph: dict[str, list[str]]  # cell_id -> list of cell_ids it depends on
