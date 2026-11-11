import re
import threading
from pathlib import Path


#Constants can change frame count to increase or decrease
REFINE_FRAME_COUNT = 9
DEFAULT_FPS = 1.0
VIDEO_EXTENSIONS = {".mp4", ".mov", ".avi", ".mkv"}
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png"}
UPLOAD_ID_RE = re.compile(r"^[0-9a-f]{32}$")
JOBS_DIR = Path(__file__).resolve().parent / "jobs"

class KeyframeError(Exception):
    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail

#Sync Endpoints run in a thread pool 
#Locks to ensure that only one thread is ever accesses the code
_LOCKS: dict[str, threading.lock] = {}
_LOCKS_GUARD = threading.Lock()

def _lock_for(upload_id: str) -> threading.Lock:
    with _LOCKS_GUARD:
        return _LOCKS.setdefault(upload_id, threading.Lock())


def _job_dir(upload_id: str) -> Path:
    if not UPLOAD_ID_RE.fullmatch(upload_id):
        raise KeyframeError(400, "Invalid upload_id")
    job = JOBS_DIR / upload_id
    if not job.is_dir():
        raise KeyframeError(400, "Upload not found")
    return job

#Finds the original uploaded video for FFmpeg extraction
def _find_video(job: Path) -> Path:
    #Sorting used to find one that matches the video type of extension instead of sorting through anything with input.* aka avoiding audio files or transcription text files.
    matches = sorted(
        p for p in job.iterdir()
        if p.is_file() and p.suffix.lower() in VIDEO_EXTENSIONS
    )
    if not matches:
        raise KeyframeError(404, "Video not found for this upload")
    return matches[0]

#Loads the timestamped transcription which obtain_time_intervals() requires
def _find_transcription(job: Path) -> Path:
    #Checks the exact file which should be produced by the API job
    #Its possible that it may use the base name of the video I.E. myvide_transcription.txt
    preferred = job / "input_transcription.txt"
    if preferred.is_file():
        return preferred
    #DOES NOT RETRANSCRIBE if the file is missing << cost saving method 
    matches = sorted(job.glob("*_transcription.txt"))
    if not matches:
        raise KeyframeError(404, "Transcription not found for this upload")
    return matches[0]

#Locates the generated document containing the img tag placeholders
def _find_html(job: Path) -> Path:
    #The API job should desposit input_workdocs.html into output/ directory
    output_dir = job / "output"
    matches = sorted(output_dir.glob("*html")) if output_dir.is_dir() else []

    if not matches:
        matches = sorted(job.rglob("html"))

    if not matches:
        raise KeyframeError(404, "Generated HTML doc not found for this upload")
    return matches[0]

def _frame_dir(job: Path, frame: int) -> Path:
    return job / f"input_frame_{frame}_jpg_frames"

def _output_dir(job: Path) -> Path:
    return job / "output"

#Used in client provided frame or filepath component 
def _safe_child(base: Path, *parts: str) -> Path:
    candidate = base.joinpath(*parts).resolve()
    base_res = base.resolve()
    if base_res != candidate and base_res not in candidate.parents:
        raise KeyframeError(400, "Invalid path")
    return candidate

def extract_keyframes(upload_id: str, force: bool = False) -> dict:
        with _LOCKS:
            job = _job_dir