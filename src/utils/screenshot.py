"""Screenshot helpers: file naming and saving a single element as JPG."""
import io
import re
from datetime import datetime
from pathlib import Path
from typing import Optional

from PIL import Image

from src.utils.logger import get_logger

log = get_logger("screenshot")

# Human-readable date and time; no ':' so the name is valid on Windows too.
TIMESTAMP_FORMAT = "%Y-%m-%d_%H-%M-%S"


def build_screenshot_filename(name: str, character_id: int, now: Optional[datetime] = None) -> str:
    """'Rick Sanchez', 1 -> 'Rick_Sanchez-1-2026-11-03_17-02-11.jpg' (name made filesystem-safe)."""
    safe_name = re.sub(r"[^\w.-]+", "_", name).strip("_") or "character"
    timestamp = (now or datetime.now()).strftime(TIMESTAMP_FORMAT)
    return f"{safe_name}-{character_id}-{timestamp}.jpg"


def png_to_jpg(png_bytes: bytes, target: Path, quality: int = 90) -> Path:
    """Selenium only produces PNG; convert (dropping any alpha channel) to JPG."""
    with Image.open(io.BytesIO(png_bytes)) as image:
        image.convert("RGB").save(target, format="JPEG", quality=quality)
    return target


def save_element_screenshot(element, directory: Path, name: str, character_id: int,
                            now: Optional[datetime] = None) -> Path:
    """Capture ONLY the given WebElement and save it as NAME-ID-TIMESTAMP.jpg in `directory`."""
    directory.mkdir(parents=True, exist_ok=True)
    target = directory / build_screenshot_filename(name, character_id, now)
    png_to_jpg(element.screenshot_as_png, target)
    log.info("Saved screenshot %s", target)
    return target