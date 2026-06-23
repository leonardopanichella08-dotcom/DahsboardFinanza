from fastapi import APIRouter, HTTPException

from app.models.simulation import SimulationInput
from app.services.simulation_service import run_simulation

router = APIRouter(prefix="/simulate", tags=["simulate"])


@router.post("")
def simulate(body: SimulationInput):
    try:
        result = run_simulation(body.session_id, body.overrides)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    return result
