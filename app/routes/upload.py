from fastapi import APIRouter, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from app.pipeline.summarizer import run_pipeline

router = APIRouter(tags=["upload"])


@router.post("/upload")
async def upload_transcript(file: UploadFile):
    if not file.filename.lower().endswith((".txt", ".vtt", ".srt")):
        raise HTTPException(status_code=400, detail="Only .txt, .vtt, or .srt files are supported for now.")

    raw_bytes = await file.read()
    try:
        text = raw_bytes.decode("utf-8", errors="ignore")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to decode file as UTF-8: {e}")

    result = run_pipeline(text, source_name=file.filename)
    return JSONResponse(result)
