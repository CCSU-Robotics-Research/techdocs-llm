# main.py is the entry point of the program. The frontend GUI is launched from here, which then drives backend processes logged in the Terminal.
from fastapi import BackgroundTasks, FastAPI, File, Form, HTTPException, UploadFile, Request
from fastapi.responses import FileResponse, HTMLResponse
from pathlib import Path
from uuid import uuid4
from backend.processVideo import preliminary_video_processing
import os
import shutil
import re
import nh3
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

#The user's edits are saved in the job folder instead of over the generated page in output/, so the original is never lost.
#Keyframe selection keeps reading the original from output/.
EDITED_DOCUMENT_NAME = "edited_document.html"

#Largest document that can be saved, in bytes. Generated documents are a few kilobytes, so this leaves plenty of room.
MAX_DOCUMENT_BYTES = 5_000_000

#Attributes allowed in saved edits on top of the nh3 defaults: the page's own classes and the inline styles on images.
DOCUMENT_ATTRIBUTES = {tag: set(attributes) for tag, attributes in nh3.ALLOWED_ATTRIBUTES.items()}
for tag, attribute in (("div", "class"), ("h1", "class"), ("code", "class"), ("img", "style"), ("span", "style")):
    DOCUMENT_ATTRIBUTES.setdefault(tag, set()).add(attribute)

#Style properties kept inside those style attributes. Anything else, such as position, is removed.
DOCUMENT_STYLES = {
    "max-height", "width", "border", "border-radius", "margin", "display",
    "font-weight", "font-style", "text-decoration", "text-decoration-line",
}

#Scripts are never needed in a document, so the browser is told not to run any, even when the page is opened directly.
DOCUMENT_SECURITY_HEADERS = {"Content-Security-Policy": "script-src 'none'; object-src 'none'"}

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
    #Edits made to the previous page no longer match the newly generated one.
    (job_dir / EDITED_DOCUMENT_NAME).unlink(missing_ok=True)

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

#Find the generated HTML page for an upload, raising an HTTPException if it does not exist.
#Sorted the same way as keyframes.py so every route uses the same file.
def find_document(upload_id: str) -> Path:
    if not re.fullmatch(r"[0-9a-f]{32}", upload_id):
        raise HTTPException(status_code=400, detail="Invalid upload_id.")
    html_path = next(iter(sorted((JOBS_DIR / upload_id / "output").glob("*.html"))), None)
    if html_path is None:
        raise HTTPException(status_code=404, detail="Document not found.")

    return html_path

#Serve the HTML page for an upload so the frontend can display it, showing the user's saved edits if there are any.
@app.get("/api/documents/{upload_id}")
def get_document(upload_id: str):
    html_path = find_document(upload_id)
    edited_path = JOBS_DIR / upload_id / EDITED_DOCUMENT_NAME
    if edited_path.is_file():
        html_path = edited_path

    #generatePage.py writes <img src="frame_N.jpg">
    html = html_path.read_text(encoding="utf-8")
    base = f'<base href="/api/documents/{upload_id}/assets/">'
    html, count = re.subn(r"<head\b[^>]*>", lambda m: f"{m.group(0)}\n{base}", html, count=1, flags=re.IGNORECASE)
    if count == 0:
        html = base + html

    return HTMLResponse(content=html, media_type="text/html", headers=DOCUMENT_SECURITY_HEADERS)

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


#Return where the contents of an HTML page's body start and end, or None if it has no body.
def find_body(html: str):
    body = re.search(r"<body\b[^>]*>", html, flags=re.IGNORECASE)
    end = html.lower().rfind("</body>")
    if body is None or end < body.end():
        return None

    return body.end(), end

#Save the user's edits to the document and return the saved page, so the editor shows exactly what was kept.
#Only the edited body is kept, with anything that could run code removed. It is placed inside the generated page,
#so the head, styles, and body tag always come from the original and cannot be changed by the request.
@app.put("/api/documents/{upload_id}")
async def save_document(upload_id: str, request: Request):
    html_path = find_document(upload_id)

    #Error Handling: Reject documents that are too large or not valid text
    if int(request.headers.get("content-length") or 0) > MAX_DOCUMENT_BYTES:
        raise HTTPException(status_code=413, detail="Document is too large.")
    raw = await request.body()
    if len(raw) > MAX_DOCUMENT_BYTES:
        raise HTTPException(status_code=413, detail="Document is too large.")
    try:
        html = raw.decode("utf-8")
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="Document must be UTF-8 text.")

    #Keep only the edited body. The base tag added for displaying images is in the head, so it is left behind too.
    edited_body = find_body(html)
    body = html[edited_body[0]:edited_body[1]] if edited_body else html
    body = nh3.clean(body, attributes=DOCUMENT_ATTRIBUTES, filter_style_properties=DOCUMENT_STYLES).strip()
    if not body:
        raise HTTPException(status_code=400, detail="Document cannot be empty.")

    #Put the cleaned body inside the generated page in place of its original body
    original = html_path.read_text(encoding="utf-8")
    original_body = find_body(original)
    page = body
    if original_body:
        page = original[:original_body[0]] + "\n" + body + "\n" + original[original_body[1]:]

    #Save beside the generated page so the original in output/ is kept
    #Write to a temporary file first, then swap it in, so a failed save never leaves a half written document
    edited_path = JOBS_DIR / upload_id / EDITED_DOCUMENT_NAME
    tmp = edited_path.with_name(f"{EDITED_DOCUMENT_NAME}.{uuid4().hex}.tmp")
    try:
        tmp.write_text(page, encoding="utf-8")
        os.replace(tmp, edited_path)
    finally:
        tmp.unlink(missing_ok=True)

    return get_document(upload_id)