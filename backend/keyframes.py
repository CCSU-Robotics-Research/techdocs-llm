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
PLACEHOLDER_RE = re.compile(r'<img\b[^>]*\bsrc=["\']frame_(\d+)\.jpg["\']', re.IGNORECASE)
PROJECT_ROOT = Path(__file__).resolve().parent.parent
JOBS_DIR = PROJECT_ROOT / "temp" / "jobs"

class KeyframeError(Exception):
    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail

#Sync Endpoints run in a thread pool 
#Locks needed to ensure that only one thread is ever accessing the code
_LOCKS: dict[str, threading.RLock] = {}
_LOCKS_GUARD = threading.Lock()

def _lock_for(upload_id: str) -> threading.RLock:
    with _LOCKS_GUARD:
        return _LOCKS.setdefault(upload_id, threading.RLock())

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
        raise KeyframeError(502, "Generator returned duplicate frame numbers.")

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
    try:
        metadata = _load_metadata(job)
    except KeyframeError:
        return False
    return all(_list_frame_images(job, iv["frame"]) for iv in metadata["intervals"])

#Gets the candidate images for a frame 
def _list_frame_images(job: Path, frame: int) -> list[Path]:
    frame_dir = _frame_dir(job, frame)
    if not frame_dir.is_dir():
        return[]

    #Extraction only produces numbered files (1.jpg, 2.jpg, ...) so anything else is ignored
    images = [
        path for path in frame_dir.iterdir()
        if path.is_file()
        and path.suffix.lower() in IMAGE_EXTENSIONS
        and path.stem.isdigit()
    ]

    return sorted(images, key=lambda path: int(path.stem))

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
    output_dir = _output_dir(job)
    if not output_dir.is_dir():
        return
    for path in output_dir.glob("frame_*.jpg"):
        if path.is_file():
            path.unlink()

def _clear_all_frame_dirs(job: Path) -> None:
    for path in job.glob("input_frame_*_jpg_frames"):
        if path.is_dir():
            shutil.rmtree(path)


def _clear_frame_dir(job: Path, frame: int) -> None:
    frame_dir = _frame_dir(job, frame)
    if not frame_dir.exists():
        return
    if not frame_dir.is_dir():
        raise KeyframeError(500, f"Frame path is not a directory: {frame_dir.name}")
    try:
        shutil.rmtree(frame_dir)
    except OSError as exc:
        raise KeyframeError(500, f"Could not clear frames for frame {frame}: {exc}") from exc
    
#Builds the per-interval response object shared by state/select/refine
def _interval_state(job: Path, interval: dict) -> dict:
    frame = interval["frame"]
    fps = interval.get("fps", DEFAULT_FPS)
    selected_path = _output_dir(job) / f"frame_{frame}.jpg"
    selected = selected_path.name if selected_path.is_file() else None

    return {
        "frame": frame,
        "alt_text": interval["alt"],
        "start": interval["start"],
        "end": interval["end"],
        "fps": fps,
        "selected": selected,
        "images": [
            {
                "name": path.name,
                "index": int(path.stem),
                "timestamp": round(
                    interval["start"] + (int(path.stem) - 1) / fps,
                    2,
                ),
                "url": f"/api/keyframes/{job.name}/frames/{frame}/{path.name}",
            }
            for path in _list_frame_images(job, frame)
        ],
    }

#Copies a file so readers never see a half written destination
def _atomic_copy(source: Path, destination: Path) -> None:
    tmp = destination.with_name(destination.name + ".tmp")
    try:
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, tmp)
        os.replace(tmp, destination)
    except OSError as exc:
        try:
            tmp.unlink(missing_ok=True)
        except OSError:
            pass
        raise KeyframeError(500, f"Could not copy {source.name}: {exc}") from exc

#Keeps the legacy interval file in sync so legacyGUI.py can still parse it
def _update_interval_txt(job: Path, frame: int, start: float, end: float, alt: str) -> None:
    path = job / "input_keyframe_time_intervals.txt"
    new_line = f'[frame_{frame}] {start:.2f}-{end:.2f} | "{alt}"'
    line_re = re.compile(rf"^\s*\[frame_{frame}\]")

    lines = path.read_text(encoding="utf-8").splitlines() if path.is_file() else []

    for i, line in enumerate(lines):
        if line_re.match(line):
            lines[i] = new_line
            break
    else:
        lines.append(new_line)

    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text("\n".join(lines) + "\n", encoding="utf-8")
    os.replace(tmp, path)

#Shared input checks for client provided image names
def _validate_image_name(name: str) -> None:
    if not isinstance(name, str) or not name or Path(name).name != name:
        raise KeyframeError(400, "Invalid image name")
    if Path(name).suffix.lower() not in IMAGE_EXTENSIONS:
        raise KeyframeError(400, "Invalid image type")

def _find_interval(metadata: dict, frame: int) -> dict:
    interval = next((iv for iv in metadata["intervals"] if iv["frame"] == frame), None)
    if interval is None:
        raise KeyframeError(400, f"Frame {frame} is not part of this extraction")
    return interval

#Shared by both resolvers: validate the name, confine it to base, require it to exist
def _resolve_image(base: Path, filename: str, label: str) -> Path:
    _validate_image_name(filename)
    path = _safe_child(base, filename)
    if not path.is_file():
        raise KeyframeError(404, f"{label} not found")
    return path

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
            state = _interval_state(job, iv)
            if state["selected"] is None:
                missing.append(iv["frame"])
            intervals.append(state)

        return {
            "upload_id": job.name,
            "status": "complete" if not missing else "ready",
            "intervals": intervals,
            "missing_frames": missing,
        }

def select_keyframe(upload_id: str, frame: int, image: str) -> dict:
    with _lock_for(upload_id):
        job = _job_dir(upload_id)
        metadata = _load_metadata(job)
        interval = _find_interval(metadata, frame)

        _validate_image_name(image)
        if image not in {p.name for p in _list_frame_images(job, frame)}:
            raise KeyframeError(400, f"{image} is not a candidate for frame {frame}")

        source = _safe_child(_frame_dir(job, frame), image)
        if not source.is_file():
            raise KeyframeError(404, "Candidate image not found")

        _atomic_copy(source, _output_dir(job) / f"frame_{frame}.jpg")

        return {
            "interval": _interval_state(job, interval),
            "state": get_keyframe_state(upload_id),
        }


def refine_keyframe(upload_id: str, frame: int, images: list[str]) -> dict:
    with _lock_for(upload_id):
        job = _job_dir(upload_id)
        metadata = _load_metadata(job)
        interval = _find_interval(metadata, frame)

        if not isinstance(images, list) or len(images) != 2:
            raise KeyframeError(400, "Exactly two images are required")
        if images[0] == images[1]:
            raise KeyframeError(400, "The two images must be different")

        candidates = {p.name for p in _list_frame_images(job, frame)}
        for name in images:
            _validate_image_name(name)
            if name not in candidates:
                raise KeyframeError(400, f"{name} is not a candidate for frame {frame}")

        current_fps = float(interval.get("fps", DEFAULT_FPS))
        if current_fps <= 0:
            current_fps = DEFAULT_FPS

        idx_a = int(Path(images[0]).stem)
        idx_b = int(Path(images[1]).stem)
        t_a = interval["start"] + (idx_a - 1) / current_fps
        t_b = interval["start"] + (idx_b - 1) / current_fps
        t1, t2 = sorted((t_a, t_b))

        if t2 <= t1:
            raise KeyframeError(400, "Chosen frames do not span a valid interval")

        new_fps = REFINE_FRAME_COUNT / (t2 - t1)

        _clear_frame_dir(job, frame)
        video = _find_video(job)

        interval_frame_extraction(
            str(video),
            str(job),
            "input",
            [(f"frame_{frame}", interval["alt"], t1, t2)],
            new_fps,
        )

        new_images = _list_frame_images(job, frame)
        if not new_images:
            raise KeyframeError(500, f"Refinement produced no frames for frame {frame}")

        #Derive FPS from what FFmpeg actually produced so timestamps stay accurate
        actual_fps = len(new_images) / (t2 - t1)

        interval["start"] = t1
        interval["end"] = t2
        interval["fps"] = actual_fps

        _write_metadata(job, metadata)
        _update_interval_txt(job, frame, t1, t2, interval["alt"])

        #The old selection no longer matches any candidate
        stale = _output_dir(job) / f"frame_{frame}.jpg"
        if stale.is_file():
            stale.unlink()

        return {
            "interval": _interval_state(job, interval),
            "state": get_keyframe_state(upload_id),
        }


def finalize_keyframes(upload_id: str) -> dict:
    with _lock_for(upload_id):
        job = _job_dir(upload_id)
        state = get_keyframe_state(upload_id)

        if state["status"] == "not_extracted":
            raise KeyframeError(409, "Keyframes have not been extracted for this upload")

        if state["missing_frames"]:
            raise KeyframeError(
                409,
                {
                    "message": "Not all keyframes have been selected",
                    "missing_frames": state["missing_frames"],
                },
            )

        _find_html(job)

        return {
            "upload_id": upload_id,
            "status": "complete",
            "document_url": f"/api/documents/{upload_id}",
            "assets_url": f"/api/documents/{upload_id}/assets/",
        }


#Serves candidate images from input_frame_N_jpg_frames/
def resolve_frame_image(upload_id: str, frame: int, filename: str) -> Path:
    job = _job_dir(upload_id)
    if frame < 1:
        raise KeyframeError(400, "Invalid frame number")
    return _resolve_image(_frame_dir(job, frame), filename, "Image")


#Serves final selected images from output/
def resolve_document_asset(upload_id: str, filename: str) -> Path:
    job = _job_dir(upload_id)
    return _resolve_image(_output_dir(job), filename, "Asset")