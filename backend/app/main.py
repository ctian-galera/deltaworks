from fastapi import FastAPI

from app.api.engineering_changes import router as engineering_changes_router
from app.api.context import router as context_router


app = FastAPI(
    title="DeltaWorks",
    version="0.1.0",
)


app.include_router(
    engineering_changes_router,
    prefix="/api/v1",
)

app.include_router(
    context_router,
    prefix="/api/v1",
)


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "deltaworks-api",
        "version": "0.1.0",
    }