"""
api.py — Local dev server for the Website Chatbot (static version).

Serves the static frontend files so you can test at localhost:8000/chat
without needing a separate HTTP server.

NOT required in production — deploy the 4 frontend files directly to cPanel.

Endpoints:
  GET /health       — liveness check
  GET /chat         — standalone chat page
  GET /widget.js    — embeddable widget script
  GET /widget.css   — widget styles
  GET /qa-data.js   — Q&A content (loaded by widget.js and chat-page.html)
"""

import logging
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-7s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

FRONTEND_DIR = Path(__file__).parent.parent / "frontend"


@asynccontextmanager
async def lifespan(app: FastAPI):
    log.info("Static chatbot server ready")
    yield


app = FastAPI(title="Pradeep Nair — Website Chatbot (local dev)", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok", "mode": "static"}


@app.get("/chat", include_in_schema=False)
async def chat_page():
    return FileResponse(FRONTEND_DIR / "chat-page.html")


@app.get("/widget.js", include_in_schema=False)
async def widget_js():
    return FileResponse(FRONTEND_DIR / "widget.js", media_type="application/javascript")


@app.get("/widget.css", include_in_schema=False)
async def widget_css():
    return FileResponse(FRONTEND_DIR / "widget.css", media_type="text/css")


@app.get("/qa-data.js", include_in_schema=False)
async def qa_data():
    return FileResponse(FRONTEND_DIR / "qa-data.js", media_type="application/javascript")
