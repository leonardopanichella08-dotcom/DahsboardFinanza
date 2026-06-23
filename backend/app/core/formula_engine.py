"""
Server-side formula engine: topological sort + safe evaluation of Excel formulas
translated to Python expressions. Used for the initial parse-time value resolution.
The frontend replicates this logic in TypeScript for real-time what-if updates.
"""
import math
import re
from typing import Any

from app.models.cell import Cell, CellType, ParsedSheet


def _topological_sort(dep_graph: dict[str, list[str]]) -> list[str]:
    """Kahn's algorithm — returns cells in evaluation order."""
    in_degree: dict[str, int] = {n: 0 for n in dep_graph}
    for deps in dep_graph.values():
        for d in deps:
            in_degree.setdefault(d, 0)

    # Cells with no deps go first
    queue = [n for n, deg in in_degree.items() if deg == 0]
    order = []
    while queue:
        node = queue.pop(0)
        order.append(node)
        for n, deps in dep_graph.items():
            if node in deps:
                in_degree[n] -= 1
                if in_degree[n] == 0:
                    queue.append(n)

    return order


# Safe builtins for eval
_SAFE_GLOBALS = {
    "__builtins__": {},
    "sum": sum,
    "max": max,
    "min": min,
    "abs": abs,
    "round": round,
    "int": int,
    "float": float,
    "math": math,
}


def _if(condition: Any, true_val: Any, false_val: Any) -> Any:
    return true_val if condition else false_val


def _and(*args: Any) -> bool:
    return all(bool(a) for a in args)


def _or(*args: Any) -> bool:
    return any(bool(a) for a in args)


def resolve_values(sheet: ParsedSheet) -> dict[str, Any]:
    """
    Evaluate all formula cells in dependency order.
    Returns a dict {cell_id: resolved_value}.
    """
    # Seed with static values
    values: dict[str, Any] = {}
    cell_map = {c.id: c for c in sheet.cells}

    for cell in sheet.cells:
        if cell.type == CellType.STATIC:
            values[cell.id] = cell.value
        elif cell.type == CellType.LABEL:
            values[cell.id] = cell.value

    eval_order = _topological_sort(sheet.dependency_graph)

    # Also ensure cells not in dep_graph are included
    remaining = [
        cid for cid in sheet.calculated_cells if cid not in eval_order
    ]
    eval_order = eval_order + remaining

    for cid in eval_order:
        cell = cell_map.get(cid)
        if cell is None or cell.formula is None:
            continue

        py_expr = cell.formula.python_expr
        if not py_expr:
            continue

        # Build local namespace from already-resolved values
        local_ns = {
            _id_to_var(dep): values.get(dep, 0)
            for dep in cell.formula.dependencies
        }
        local_ns.update({"_if": _if, "_and": _and, "_or": _or})

        try:
            result = eval(py_expr, _SAFE_GLOBALS, local_ns)  # noqa: S307
        except Exception:
            result = None

        values[cid] = result

    return values


def recalculate(
    sheet: ParsedSheet,
    overrides: dict[str, Any],
) -> dict[str, Any]:
    """Apply user overrides to static cells, then re-resolve all formulas."""
    # Patch static values
    cell_map = {c.id: c for c in sheet.cells}
    for cid, new_val in overrides.items():
        if cid in cell_map:
            cell_map[cid].value = new_val

    return resolve_values(sheet)


def _id_to_var(cell_id: str) -> str:
    """Convert 'Sheet1!B3' to 'Sheet1__B3' (Python-safe variable name)."""
    return cell_id.replace("!", "__").replace(" ", "_")
