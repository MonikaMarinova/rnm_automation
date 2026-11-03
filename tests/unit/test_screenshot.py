import io
import re
from datetime import datetime

import pytest
from PIL import Image

from src.utils.screenshot import build_screenshot_filename, png_to_jpg, save_element_screenshot

pytestmark = pytest.mark.unit
NOW = datetime(2026, 11, 3, 17, 2, 11)


def fake_png(size=(20, 10), mode="RGBA") -> bytes:
    buffer = io.BytesIO()
    Image.new(mode, size, (255, 0, 0, 128) if mode == "RGBA" else (255, 0, 0)).save(buffer, format="PNG")
    return buffer.getvalue()


class FakeElement:
    screenshot_as_png = fake_png()


@pytest.mark.parametrize("name, expected", [
    ("Rick Sanchez", "Rick_Sanchez-1-2026-11-03_17-02-11.jpg"),
    ("Mr. Poopybutthole", "Mr._Poopybutthole-1-2026-11-03_17-02-11.jpg"),
    ("A/B: <Morty>?", "A_B_Morty-1-2026-11-03_17-02-11.jpg"),   # unsafe characters removed
])
def test_filename(name, expected):
    assert build_screenshot_filename(name, 1, NOW) == expected


def test_filename_defaults_to_current_time_in_readable_format():
    assert re.fullmatch(r"Rick-1-\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}\.jpg", build_screenshot_filename("Rick", 1))


def test_png_to_jpg_produces_real_jpeg_even_with_alpha(tmp_path):
    target = png_to_jpg(fake_png(mode="RGBA"), tmp_path / "x.jpg")
    with Image.open(target) as image:
        assert image.format == "JPEG" and image.size == (20, 10)


def test_save_element_screenshot_creates_directory_and_file(tmp_path):
    path = save_element_screenshot(FakeElement(), tmp_path / "nested" / "shots", "Morty Smith", 2, NOW)
    assert path.name == "Morty_Smith-2-2026-11-03_17-02-11.jpg"
    assert path.exists() and path.stat().st_size > 0