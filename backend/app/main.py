from fastapi import FastAPI
from app.api.router import router as api_router

app = FastAPI(
    title="D.AI.SY Backend",
    version="0.1.0"
)

app.include_router(api_router)


@app.get("/")
def root():
    return {
        "system": "D.AI.SY",
        "status": "running",
        "version": "0.1.0"
    }