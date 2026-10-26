"""Give OpenCV a temporary path and remove it after every operation."""
from contextlib import contextmanager
from pathlib import Path
import tempfile

import cv2

from signal_processing.video_pipeline import analyze_live_video, video_metadata


@contextmanager
def recording_path(upload):
    path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(upload.name).suffix or '.mp4') as file:
            path = Path(file.name)
            file.write(upload.getbuffer())
        yield path
    finally:
        if path is not None:
            path.unlink(missing_ok=True)


def inspect_recording(upload):
    try:
        with recording_path(upload) as path:
            return video_metadata(path)
    except cv2.error as error:
        raise ValueError('The video decoder could not read this recording. Try an original H.264 MP4.') from error


def analyze_recording(upload, allow_short=False, height_m=1.75):
    with recording_path(upload) as path:
        return analyze_live_video(path, allow_short=allow_short, height_m=height_m)
