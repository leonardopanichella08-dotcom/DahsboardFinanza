import shutil
import tempfile
from pathlib import Path

from fastapi import APIRouter, HTTPException, UploadFile

from app.services.parser_service import create_session

router = APIRouter(prefix="/upload", tags=["upload"])

_MAX_BYTES = 10 * 1024 * 1024  # 10 MB


@router.post("")
async def upload_excel(file: UploadFile):
    if not file.filename or not file.filename.endswith((".xlsx", ".xls")):
        raise HTTPException(status_code=400, detail="Il file deve essere un Excel (.xlsx o .xls)")

    suffix = ".xls" if file.filename.endswith(".xls") else ".xlsx"
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp_path = Path(tmp.name)
        content = await file.read()
        if len(content) > _MAX_BYTES:
            raise HTTPException(status_code=413, detail="File exceeds 10 MB limit")
        tmp.write(content)

    try:
        session_data = create_session(tmp_path)
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Failed to parse Excel file: {e}") from e
    finally:
        tmp_path.unlink(missing_ok=True)

    return session_data
