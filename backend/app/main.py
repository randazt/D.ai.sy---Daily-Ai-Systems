import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import router as api_router

app = FastAPI(
    title="D.AI.SY Backend",
    version="0.1.0"
)

allowed_origins = [
    origin.strip()
    for origin in os.getenv(
        "DAISY_CORS_ORIGINS",
        "http://localhost:5173,http://localhost:5175",
    ).split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=False,
    allow_methods=["POST", "OPTIONS"],
    allow_headers=["Content-Type"],
)

app.include_router(api_router)


@app.get("/")
def root():
    return {
        "system": "D.AI.SY",
        "status": "running",
        "version": "0.1.0"
    }
