from fastapi import FastAPI
from .routers.research import router as research_router

app = FastAPI()

app.include_router(research_router, prefix="/api")
