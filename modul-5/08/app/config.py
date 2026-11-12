"""Central configuration. Values come from environment variables (see .env.example)."""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
RUNTIME_DIR = Path(os.getenv("RUNTIME_DIR", BASE_DIR / "runtime"))
DB_PATH = RUNTIME_DIR / "acme.db"
OUTBOX_PATH = RUNTIME_DIR / "outbox.jsonl"
UPLOAD_DIR = RUNTIME_DIR / "uploads"

# "openai" = real model (needs OPENAI_API_KEY). "fake" = scripted, gullible stand-in model
# for checking the plumbing and your guards offline. Fake mode is NOT a real LLM.
LLM_MODE = os.getenv("LLM_MODE", "openai")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-5-mini")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
OPENAI_REASONING_EFFORT = os.getenv("OPENAI_REASONING_EFFORT", "low")  # only used for gpt-5* models

INTERNAL_EMAIL_DOMAIN = "acme-store.example"
LAB_MODE = os.getenv("LAB_MODE", "1") == "1"  # enables /admin/reset for the lab
