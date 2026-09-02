import io

import pandas as pd
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes import explain, simulate, upload

app = FastAPI(
    title="Architetto Gestionale API",
    version="2.0.0",
    description="Parser Excel avanzato con simulazione what-if, metriche AI e spiegazioni.",
)

# CORS aperto per sviluppo locale
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Rotte principali (parser completo + simulazione + AI) ──────────────────
app.include_router(upload.router, prefix="/api")
app.include_router(simulate.router, prefix="/api")
app.include_router(explain.router, prefix="/api")


# ── Rotta di compatibilità: /upload senza prefisso (versione pandas semplice)
@app.post("/upload")
async def upload_simple(file: UploadFile = File(...)):
    """Endpoint di fallback – restituisce anteprima grezza via pandas."""
    try:
        contents = await file.read()
        df = pd.read_excel(io.BytesIO(contents))
        df = df.fillna("")

        def safe(v):
            if isinstance(v, float) and v != v:
                return ""
            try:
                return v.item()
            except AttributeError:
                return v

        preview = [[safe(v) for v in row] for row in df.head(20).values.tolist()]
        return JSONResponse(content={
            "filename": file.filename,
            "columns": [str(c) for c in df.columns.tolist()],
            "rows_count": int(len(df)),
            "preview": preview,
        })
    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": str(e)})


@app.get("/")
def read_root():
    return {"status": "online", "message": "Backend Architetto Gestionale pronto"}


@app.get("/health")
def health():
    return {"status": "ok"}
