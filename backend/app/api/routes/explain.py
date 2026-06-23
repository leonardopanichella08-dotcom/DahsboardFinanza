from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import get_api_key
from app.services.explain_service import explain_cell

router = APIRouter(prefix="/explain", tags=["explain"])


@router.get("/{session_id}/{cell_id:path}")
async def explain(
    session_id: str,
    cell_id: str,
    api_key: str = Depends(get_api_key),
):
    try:
        result = await explain_cell(session_id, cell_id, api_key)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e
    return result
