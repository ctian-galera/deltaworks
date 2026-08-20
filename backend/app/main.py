from fastapi import FastAPI

app = FastAPI(
    title="DeltaWorks",
    description="Industrial Engineering Change & Decision Automation Platform",
    version="0.1.0",
)


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "deltaworks-api",
        "version": "0.1.0",
    }