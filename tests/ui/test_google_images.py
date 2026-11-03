"""Google Images flow for each API-selected character."""
import re

import pytest
from PIL import Image

from config.settings import settings
from src.ui.pages.google_home_page import GoogleHomePage
from src.utils.image_position import image_position
from src.utils.screenshot import save_element_screenshot

pytestmark = pytest.mark.ui


# The characters are only known at run time (random API selection), so we parametrize by index.
@pytest.mark.parametrize("index", [0, 1], ids=["first_character", "second_character"])
def test_capture_character_image_from_google(driver, selected_characters, index):
    character = selected_characters[index]
    position = image_position(character.id)

    images_page = GoogleHomePage(driver).open().open_images()
    images_page.search(f"Rick and Morty {character.name}")

    assert images_page.page_language().lower().startswith("en"), \
        f"Google is not in English (<html lang='{images_page.page_language()}'>)"

    image = images_page.get_result_image(position)
    screenshot = save_element_screenshot(image, settings.screenshots_dir, character.name, character.id)

    assert screenshot.exists() and screenshot.stat().st_size > 0, f"Empty screenshot: {screenshot}"
    assert re.fullmatch(rf".+-{character.id}-\d{{4}}-\d{{2}}-\d{{2}}_\d{{2}}-\d{{2}}-\d{{2}}\.jpg", screenshot.name), \
        f"Unexpected file name: {screenshot.name}"
    with Image.open(screenshot) as saved:
        assert saved.format == "JPEG", f"Expected a JPEG, got {saved.format}"
        assert saved.width > 0 and saved.height > 0
