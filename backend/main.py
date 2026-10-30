# main.py is the entry point of the program. The frontend GUI is launched from here, which then drives backend processes logged in the Terminal.
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from pathlib import Path
from uuid import uuid4
from backend.processVideo import preliminary_video_processing
import shutil
import re
from pydantic import BaseModel
from backend.transcribe import transcribe
from backend.generatePage import generate_page

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

class GenerateRequest(BaseModel):
    upload_id: str
    context: str = ""

#Generate a page from a completed upload.
#Validates the upload ID, ensures the audio is ready, and returns the generated HTML file.
@app.post("/api/generate")
def generate(req: GenerateRequest):
    #Check that the upload ID exists before looking for the job.
    if not re.fullmatch(r"[0-9a-f]{32}", req.upload_id):
        raise HTTPException(status_code=400, detail="Invaild upload_id.")
    job_dir = JOBS_DIR / req.upload_id
    if not job_dir.is_dir():
        raise HTTPException(status_code=404, detail="Upload not found.")
    audio = next(job_dir.glob("*_audio.mp3"), None)
    if audio is None:
        raise HTTPException(status_code  =409, detail="Audio not ready for this upload.")

    #Transcribe the audio, then generate the page from the transcript.
    markdown_path, _ = transcribe(str(audio), req.context)
    html_path, out_dir = generate_page(markdown_path, output_dir=job_dir / "output")

    return {"upload_id": req.upload_id, "status":"page ready", "html_file": Path(html_path).name}

#Generate documentation from a video in one request by running the upload and generate steps back to back.
#The context is a form field because a request that includes a file cannot also have a JSON body.
@app.post("/api/generate-documentation")
def generate_documentation(video: UploadFile, context: str = Form("")):
    upload = upload_video(video)
    page = generate(GenerateRequest(upload_id=upload["upload_id"], context=context))

    return {"filename": upload["filename"],
            "content_type": upload["content_type"],
            "upload_id": page["upload_id"],
            "status": page["status"],
            "html_file": page["html_file"],
            }
