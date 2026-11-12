import re
import shutil
import threading
import os
import datetime
import json
from pathlib import Path
from backend.transcribe import obtain_time_intervals
from backend.processVideo import interval_frame_extraction

#Constants can change frame count to increase or decrease
REFINE_FRAME_COUNT = 9
DEFAULT_FPS = 1.0
VIDEO_EXTENSIONS = {".mp4", ".mov", ".avi", ".mkv"}
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png"}
UPLOAD_ID_RE = re.compile(r"^[0-9a-f]{32}$")
PLACEHOLDER_RE = re.compile(r'<img>\b[^>]*\bsrc=["\']frame_(\d+)\.jpg["\']', re.IGNORECASE)
PROJECT_ROOT = Path(__file__).resolve().parent.parent
JOBS_DIR = PROJECT_ROOT / "temp" / "jobs"

class KeyframeError(Exception):
    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail

#Sync Endpoints run in a thread pool 
#Locks to ensure that only one thread is ever accesses the code
_LOCKS: dict[str, threading.lock] = {}
_LOCKS_GUARD = threading.Lock()

def _lock_for(upload_id: str) -> threading.RLock:
    with _LOCKS_GUARD:
        return _LOCKS.setdefault(upload_id, threading.Lock())

#Helper functions
def _job_dir(upload_id: str) -> Path:
    if not UPLOAD_ID_RE.fullmatch(upload_id):
        raise KeyframeError(400, "Invalid upload_id")
    job = JOBS_DIR / upload_id
    if not job.is_dir():
        raise KeyframeError(404, "Upload not found")
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
    matches = sorted(output_dir.glob("*.html")) if output_dir.is_dir() else []

    if not matches:
        matches = sorted(job.rglob("*.html"))

    if not matches:
        raise KeyframeError(404, "Generated HTML doc not found for this upload")
    return matches[0]

def _frame_dir(job: Path, frame: int) -> Path:
    return job / f"input_frame_{frame}_jpg_frames"

def _output_dir(job: Path) -> Path:
    return job / "output"

#Reject malformed/corrupted LLM output before running FFmpeg
def _validate_intervals(metadata_intervals: list[dict], html_text: str) -> None:
    if not metadata_intervals:
        raise KeyframeError(502, "Generator returned no keyframe intervals")

    frames = [iv["frame"] for iv in metadata_intervals]

    if len(frames) != len(set(frames)):
        raise KeyframeError(502, "Generator returned dupe frmae numbers.")

    expected = set(range(1, len(frames) + 1))
    if set(frames) != expected:
        raise KeyframeError(502, f"Generator returned non-contiguous frames: {sorted(frames)}")

    for iv in metadata_intervals:
        if iv["start"] >= iv ["end"]:
            raise KeyframeError(502, f"Invalid interval for frame {iv['frame']}: " f"{iv['start']} >= {iv['end']}")

    placeholders = PLACEHOLDER_RE.findall(html_text)
    if len(placeholders) != len(metadata_intervals):
        raise KeyframeError(502, f"Generator returned {len(metadata_intervals)} intervals " f"but the HTML contains {len(placeholders)} image placeholders")

#Decides whether extraction can be skipped without re-running OpenAI/FFmpeg
def _cache_is_valid(job: Path) -> bool:
    metadata_path = job / "keyframes.json"
    if not metadata_path.is_file():
        return False
    try:
        data = json.loads(metadata_path.read_text(encoding="utf-8"))
        intervals = data.get("intervals", [])

    except (OSError, json.JSONDecodeError):
        return False

    if not intervals:
        return False

    for interval in intervals:
        frames = _list_frame_images(job, interval["frame"])
        if not frames:
            return False

    return True

#Gets the candidate images for a frame 
def _list_frame_images(job: Path, frame: int) -> list[Path]:
    frame_dir = _frame_dir(job, frame)
    if not frame_dir.is_dir():
        return[]

    images = [
        path for path in frame_dir.iterdir()
        if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS
    ]

    def sort_key(path: Path):
        stem = path.stem
        return(0, int(stem)) if stem.isdigit() else(1, path.name)

    return sorted(images, key=sort_key)

#Allows readers to never see a half written file
def _write_metadata(job: Path, data: dict) -> None:
    data["updated_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    tmp = job/"keyframes.json.tmp"
    tmp.write_text(json.dumps(data, indent=2), encoding="utf-8")
    os.replace(tmp, job / "keyframes.json")

def _load_metadata(job: Path) -> dict:
    path = job / "keyframes.json"
    if not path.is_file():
        raise KeyframeError(409, "Keyframes have not been extracted for this upload")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise KeyframeError(500, "Keyframe metadata is corrupted") from exc
    if not data.get("intervals"):
        raise KeyframeError(409, "Keyframes have not been extracted for this upload")
    return data

def _clear_selections(job: Path) -> None:

def _clear_all_frame_dirs(job: Path) -> None:

def _clear_frame_dir(job: Path) -> None:
    



#Used in client provided frame or filepath component 
def _safe_child(base: Path, *parts: str) -> Path:
    candidate = base.joinpath(*parts).resolve()
    base_res = base.resolve()
    if base_res != candidate and base_res not in candidate.parents:
        raise KeyframeError(400, "Invalid path")
    return candidate

#Service functions
def extract_keyframes(upload_id: str, force: bool = False) -> dict:
    with _lock_for(upload_id):
        job = _job_dir(upload_id)
        if not force and _cache_is_valid(job):
            return get_keyframe_state(upload_id)

        html = _find_html(job)
        video = _find_video(job)
        transcription = _find_transcription(job)

        transcript_text = transcription.read_text(encoding="utf-8")
        intervals, _txt_path = obtain_time_intervals(
            str(html), transcript_text, "input", str(job)
        )

        try:
            metadata_intervals = [
                {
                    "frame": int(name.removeprefix("frame_")),
                    "alt": alt,
                    "start": float(start),
                    "end": float(end),
                    "fps": DEFAULT_FPS,
                }
                for name, alt, start, end in intervals
            ]
        except (ValueError, TypeError) as exc:
            raise KeyframeError(502, f"Malformed interval from generator: {exc}") from exc

        _validate_intervals(metadata_intervals, html.read_text(encoding="utf-8"))

        if force:
            _clear_selections(job)
            _clear_all_frame_dirs(job)

        for interval in metadata_intervals:
            _clear_frame_dir(job, interval["frame"])

        interval_frame_extraction(
            str(video), str(job),"input",
            [(f"frame_{iv['frame']}", iv["alt"], iv["start"], iv["end"]) 
            for iv in metadata_intervals],DEFAULT_FPS,
        )

        for interval in metadata_intervals:
            if not _list_frame_images(job, interval["frame"]):
                raise KeyframeError(
                    500, f"No frames extracted for frame {interval['frame']}."
                )

        _write_metadata(job, {
            "version": 1,
            "base_filename": "input",
            "video_file": video.name,
            "intervals": metadata_intervals,
        })

        return get_keyframe_state(upload_id)


def get_keyframe_state(upload_id: str) -> dict:
    job = _job_dir(upload_id)
    with _lock_for(upload_id):
        try:
            metadata = _load_metadata(job)
        except KeyframeError as exc:
            if exc.status_code == 409:
                return {
                    "upload_id": job.name,
                    "status": "not_extracted",
                    "intervals": [],
                    "missing_frames": [],
                }
            raise

        intervals = []
        missing = []

        for iv in metadata["intervals"]:
            frame = iv["frame"]
            images = _list_frame_images(job, frame)
            selected_path = _output_dir(job) / f"frame_{frame}.jpg"
            selected = selected_path.name if selected_path.is_file() else None

            if selected is None:
                missing.append(frame)

            intervals.append({
                "frame": frame,
                "alt_text": iv["alt"],
                "start": iv["start"],
                "end": iv["end"],
                "fps": iv.get("fps", DEFAULT_FPS),
                "selected": selected,
                "images": [
                    {
                        "name": path.name,
                        "index": int(path.stem),
                        "timestamp": round(
                            iv["start"] + (int(path.stem) - 1) / iv.get("fps", DEFAULT_FPS),
                            2,
                        ),
                        "url": f"/api/keyframes/{job.name}/frames/{frame}/{path.name}",
                    }
                    for path in images
                ],
            })

        return {
            "upload_id": job.name,
            "status": "complete" if not missing else "ready",
            "intervals": intervals,
            "missing_frames": missing,
        }

def select_keyframe(upload_id, frame, image) -> dict:
    with _lock_for(upload_id):
        job = _job_dir(upload_id)