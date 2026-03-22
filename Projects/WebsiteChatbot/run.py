#!/usr/bin/env python3
"""
Local dev server for the Website Chatbot (static / no-LLM version).

Serves the 4 frontend files so you can test the chat UI at localhost:8000/chat.
NOT required in production — just upload the frontend/ files to cPanel.

Usage:
  cd Projects/WebsiteChatbot
  python run.py
"""

import os
import sys
from pathlib import Path

SRC_DIR = Path(__file__).parent / "src"
sys.path.insert(0, str(SRC_DIR))

import uvicorn

if __name__ == "__main__":
    os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
    print("\n  Pradeep Nair Website Chatbot (static mode)")
    print("  Chat → http://localhost:8000/chat\n")
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True, reload_dirs=[str(SRC_DIR)])
