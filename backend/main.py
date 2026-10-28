# main.py is the entry point of the program. The frontend GUI is launched from here, which then drives backend processes logged in the Terminal.
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from pathlib import Path
from uuid import uuid4
from backend.processVideo import preliminary_video_processing
import shutil

PROJECT_ROOT = Path(__file__).resolve().parent.parent
JOBS_DIR = PROJECT_ROOT / "temp" / "jobs"

#Initialize FastAPI app and add health check endpoint for monitoring the backend service.
app = FastAPI()

#First API endpoint: Health check to ensure the backend service is running and responsive. 
@app.get("/api/health")
def health_check():
    return {"status": "healthy"}

#Add an endpoint to handle video uploads. The endpoint accepts a video file and returns its filename and content type.
@app.post("/api/upload")

#Function to handle video uploads. It saves the uploaded video to a temporary directory and returns metadata about the upload.
#It also checks if the uploaded file is empty and raises an HTTPException if so for error handling.
def upload_video(video: UploadFile):
    extension = Path(video.filename or "").suffix.lower()
    
    upload_id = uuid4().hex 
    upload_dir = JOBS_DIR / upload_id 
    upload_dir.mkdir(parents=True, exist_ok=True) 
    video_path = upload_dir / f"input{extension}"

    try:
        with video_path.open("wb") as destination:
            shutil.copyfileobj(video.file, destination)

    finally:
        video.file.close()

    if video_path.stat().st_size == 0:
        video_path.unlink() # Remove the empty file
        upload_dir.rmdir() # Removes the empty directory
        raise HTTPException(status_code=400,                             
                            detail="Uploaded file is empty.")   

    audio_path = preliminary_video_processing(
        input_video_path=str(video_path),
        base_filename=video_path.stem,
        output_directory=str(upload_dir), )
    

    return {"filename": video.filename, 
            "content_type": video.content_type,
            "upload_id": upload_id,
            "status": "audio ready",
            "audio_path": Path(audio_path).name,
            }