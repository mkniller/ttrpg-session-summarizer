from fastapi import FastAPI
from app.routes.upload import router as upload_router

app = FastAPI(
    title="TTRPG Session Summarizer",
    description="Multi-pass GM & player-facing summarizer for TTRPG voice transcripts.",
    version="0.1.0",
)

app.include_router(upload_router, prefix="/api")

@app.get("/health")
async def health_check():
    return {"status": "ok"}
