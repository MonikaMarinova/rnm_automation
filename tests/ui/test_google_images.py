"""Browser flow against a local Google-shaped site, independent of external services."""
import re
from types import SimpleNamespace

import pytest
from PIL import Image

from config.settings import settings
from src.ui.pages import google_home_page
from src.ui.pages.google_home_page import GoogleHomePage
from src.utils.image_position import image_position
from src.utils.screenshot import save_element_screenshot

pytestmark = pytest.mark.ui


@pytest.mark.parametrize(
    "character_id, character_name",
    [(2, "Morty Smith"), (123, "Rick Sanchez")],
    ids=["first_character", "second_character"],
)
def test_capture_character_image_from_google(
    driver, monkeypatch, google_test_site, character_id, character_name
):
    base_url, searches = google_test_site
    monkeypatch.setattr(google_home_page, "settings", SimpleNamespace(google_url=base_url))
    position = image_position(character_id)

    images_page = GoogleHomePage(driver, captcha_wait=0).open().open_images()
    images_page.search(f"Rick and Morty {character_name}")

    assert images_page.page_language().lower().startswith("en"), \
        f"Google test page is not in English (<html lang='{images_page.page_language()}'>)"

    image = images_page.get_result_image(position)
    screenshot = save_element_screenshot(image, settings.screenshots_dir, character_name, character_id)

    assert searches == [f"Rick and Morty {character_name}"]
    assert screenshot.exists() and screenshot.stat().st_size > 0, f"Empty screenshot: {screenshot}"
    assert re.fullmatch(rf".+-{character_id}-\d{{4}}-\d{{2}}-\d{{2}}_\d{{2}}-\d{{2}}-\d{{2}}\.jpg", screenshot.name), \
        f"Unexpected file name: {screenshot.name}"
    with Image.open(screenshot) as saved:
        assert saved.format == "JPEG", f"Expected a JPEG, got {saved.format}"
        assert saved.width > 0 and saved.height > 0
