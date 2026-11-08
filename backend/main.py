# main.py is the entry point of the program. The frontend GUI is launched from here, which then drives backend processes logged in the Terminal.
from fastapi import BackgroundTasks, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
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

#Percent complete at the start of each processing stage, used by the frontend progress bar.
JOB_STAGES = {
    "uploaded": 10,
    "extracting_audio": 25,
    "transcribing": 50,
    "generating_page": 75,
    "done": 100,
}

#Current stage of each documentation job, keyed by upload ID. Jobs are lost if the server restarts.
jobs = {}

#Initialize FastAPI app and add health check endpoint for monitoring the backend service.
app = FastAPI()

#First API endpoint: Health check to ensure the backend service is running and responsive. 
@app.get("/api/health")
def health_check():
    return {"status": "healthy"}

#Save an uploaded video to a new job directory and return the path to the saved video.
#It also checks if the uploaded file is empty and raises an HTTPException if so for error handling.
def save_upload(video: UploadFile) -> Path:
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

    return video_path

#Add an endpoint to handle video uploads. The endpoint accepts a video file and returns its filename and content type.
@app.post("/api/upload")

#Function to handle video uploads. It saves the uploaded video to a temporary directory and returns metadata about the upload.
def upload_video(video: UploadFile):
    video_path = save_upload(video)
    upload_dir = video_path.parent
    upload_id = upload_dir.name

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

#Record the stage a documentation job is in so the status endpoint can report it.
def set_job_stage(upload_id: str, stage: str, **details):
    jobs[upload_id] = {"upload_id": upload_id, "stage": stage, "progress": JOB_STAGES[stage], **details}

#Run each processing stage for a saved upload, recording the stage before it starts.
#Runs as a background task after the response is sent, so errors are recorded on the job instead of raised.
def run_documentation_job(upload_id: str, video_path: Path, context: str):
    job_dir = video_path.parent
    try:
        set_job_stage(upload_id, "extracting_audio")
        audio_path = preliminary_video_processing(
            input_video_path=str(video_path),
            base_filename=video_path.stem,
            output_directory=str(job_dir), )

        set_job_stage(upload_id, "transcribing")
        markdown_path, _ = transcribe(audio_path, context)

        set_job_stage(upload_id, "generating_page")
        html_path, _ = generate_page(markdown_path, output_dir=job_dir / "output")

        set_job_stage(upload_id, "done", html_file=Path(html_path).name)
    except Exception as error:
        print(f"ERROR: Documentation job {upload_id} failed: {error}")
        jobs[upload_id] = {**jobs[upload_id], "failed": True, "detail": "Processing failed."}

#Start generating documentation from a video and return right away with 202 Accepted.
#The video is saved before responding, then processing continues in the background. Poll /api/jobs/{upload_id} for progress.
#The context is a form field because a request that includes a file cannot also have a JSON body.
@app.post("/api/generate-documentation", status_code=202)
def generate_documentation(video: UploadFile, background_tasks: BackgroundTasks, context: str = Form("")):
    video_path = save_upload(video)
    upload_id = video_path.parent.name

    set_job_stage(upload_id, "uploaded")
    background_tasks.add_task(run_documentation_job, upload_id, video_path, context)

    return {"filename": video.filename,
            "content_type": video.content_type,
            "upload_id": upload_id,
            "status": "processing",
            }

#Report the current stage and progress of a documentation job.
@app.get("/api/jobs/{upload_id}")
def get_job_status(upload_id: str):
    if not re.fullmatch(r"[0-9a-f]{32}", upload_id):
        raise HTTPException(status_code=400, detail="Invalid upload_id.")
    job = jobs.get(upload_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found.")

    return job

#Serve the generated HTML page for an upload so the frontend can display it.
@app.get("/api/documents/{upload_id}")
def get_document(upload_id: str):
    if not re.fullmatch(r"[0-9a-f]{32}", upload_id):
        raise HTTPException(status_code=400, detail="Invalid upload_id.")
    html_path = next((JOBS_DIR / upload_id / "output").glob("*.html"), None)
    if html_path is None:
        raise HTTPException(status_code=404, detail="Document not found.")

    return FileResponse(html_path, media_type="text/html")
