from typing import Any

from app.core.formula_engine import recalculate
from app.models.simulation import SimulationResult
from app.services.parser_service import get_session


def run_simulation(session_id: str, overrides: dict[str, Any]) -> SimulationResult:
    session = get_session(session_id)
    if session is None:
        raise KeyError(f"Session {session_id!r} not found")

    sheet = session["sheet"]
    new_values = recalculate(sheet, overrides)

    # Track which cells changed
    old_values = session["resolved"]
    changed = [cid for cid, val in new_values.items() if val != old_values.get(cid)]

    # Persist updated resolved values in session
    session["resolved"] = new_values

    return SimulationResult(
        session_id=session_id,
        values=new_values,
        changed_cells=changed,
    )
