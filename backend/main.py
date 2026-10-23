# main.py is the entry point of the program. The frontend GUI is launched from here, which then drives backend processes logged in the Terminal.
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from pathlib import Path
from uuid import uuid4

PROJECT_ROOT = Path(__file__).resolve().parent.parent
JOBS_DIR = PROJECT_ROOT / "temp" / "jobs"

ALLOWED_EXTENSIONS = {".mp4", ".mov", ".avi", ".mkv",}


#Initialize FastAPI app and add health check endpoint for monitoring the backend service.
app = FastAPI()

@app.get("/api/health")
def health_check():
    return {"status": "healthy"}

#Add an endpoint to handle video uploads. The endpoint accepts a video file and returns its filename and content type.
@app.post("/api/upload")
async def upload_video(video: UploadFile):
    return {"filename": video.filename, "content_type": video.content_type}