# main.py is the entry point of the program. The frontend GUI is launched from here, which then drives backend processes logged in the Terminal.
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse, HTMLResponse
from pathlib import Path
from uuid import uuid4
from backend.processVideo import preliminary_video_processing
import shutil
import re
from pydantic import BaseModel, Field
from backend.transcribe import transcribe
from backend.generatePage import generate_page
from backend.keyframes import (
    KeyframeError,
    extract_keyframes,
    get_keyframe_state,
    select_keyframe,
    refine_keyframe,
    finalize_keyframes,
    resolve_frame_image,
    resolve_document_asset,
)

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

#Serve the generated HTML page for an upload so the frontend can display it.
@app.get("/api/documents/{upload_id}")
def get_document(upload_id: str):
    if not re.fullmatch(r"[0-9a-f]{32}", upload_id):
        raise HTTPException(status_code=400, detail="Invalid upload_id.")
    html_path = next((JOBS_DIR / upload_id / "output").glob("*.html"), None)
    if html_path is None:
        raise HTTPException(status_code=404, detail="Document not found.")

    #generatePage.py writes <img src="frame_N.jpg">
    html = html_path.read_text(encoding="utf-8")
    base = f'<base href="/api/documents/{upload_id}/assets/">'
    html, count = re.subn(r"<head\b[^>]*>", lambda m: f"{m.group(0)}\n{base}", html, count=1, flags=re.IGNORECASE)
    if count == 0:
        html = base + html

    return HTMLResponse(content=html, media_type="text/html")

#Serve the final selected keyframe images that the base tag points at
@app.get("/api/documents/{upload_id}/assets/{filename}")
def get_document_asset(upload_id: str, filename: str):
    path = _keyframe_call(resolve_document_asset, upload_id, filename)
    return FileResponse(path)

#Keyframe selection endpoints
class SelectFrameRequest(BaseModel):
    frame: int = Field(..., ge=1)
    image: str = Field(..., min_length=1, max_length=255)


class RefineIntervalRequest(BaseModel):
    frame: int = Field(..., ge=1)
    images: list[str] = Field(..., min_length=2, max_length=2)

#Converts the service's KeyframeError into an HTTPException, keeping the status code and detail (str or dict).
def _keyframe_call(func, *args, **kwargs):
    try:
        return func(*args, **kwargs)
    except KeyframeError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.detail) from exc
    
#Current extraction/selection state
@app.get("/api/keyframes/{upload_id}")
def get_keyframes(upload_id: str):
    return _keyframe_call(get_keyframe_state, upload_id)

#Runs interval discovery returns the cached state unless force=true
@app.post("/api/keyframes/{upload_id}/extract")
def extract_keyframes_route(upload_id: str, force: bool = False):
    return _keyframe_call(extract_keyframes, upload_id, force)

#Saves one candidate as frame_N.jpg overwriting any previous selection for that frame
@app.post("/api/keyframes/{upload_id}/select")
def select_keyframe_route(upload_id: str, req: SelectFrameRequest):
    return _keyframe_call(select_keyframe, upload_id, req.frame, req.image)

#Re-extracts REFINE_FRAME_COUNT candidates between two chosen candidates
@app.post("/api/keyframes/{upload_id}/refine")
def refine_keyframe_route(upload_id: str, req: RefineIntervalRequest):
    return _keyframe_call(refine_keyframe, upload_id, req.frame, req.images)

#Confirms every placeholder has a selected image 409 with missing_frames if not
@app.post("/api/keyframes/{upload_id}/finalize")
def finalize_keyframes_route(upload_id: str):
    return _keyframe_call(finalize_keyframes, upload_id)

#Serves candidate images for the selection grid
@app.get("/api/keyframes/{upload_id}/frames/{frame}/{filename}")
def get_keyframe_frame(upload_id: str, frame: int, filename: str):
    path = _keyframe_call(resolve_frame_image, upload_id, frame, filename)
    return FileResponse(path)