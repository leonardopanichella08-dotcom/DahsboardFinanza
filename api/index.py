"""
Vercel serverless entry point — re-exports the FastAPI app from backend/.
Vercel expects a file at api/index.py with an `app` (ASGI) object.
"""
import sys
import os

# Make the backend package importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from main import app  # noqa: F401  — Vercel picks up `app`
