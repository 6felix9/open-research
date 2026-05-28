import logging
import os

from dotenv import load_dotenv
from fastapi import FastAPI

# Load environment files: .env and .env.local (checks both local and root directories)
for path in [".env", ".env.local", "../.env", "../.env.local"]:
    if os.path.exists(path):
        load_dotenv(dotenv_path=path)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)

os.environ.setdefault("OPENAI_AGENTS_DISABLE_TRACING", "1")

from .routers.research import router as research_router

app = FastAPI()

app.include_router(research_router, prefix="/api")
