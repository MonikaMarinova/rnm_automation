import pytest

from src.ui.driver_factory import build_chrome_options

pytestmark = pytest.mark.unit


def test_headed_options_are_english_and_maximized():
    options = build_chrome_options(headless=False, language="en")
    assert "--lang=en" in options.arguments
    assert "--start-maximized" in options.arguments
    assert not any(arg.startswith("--headless") for arg in options.arguments)
    assert options.experimental_options["prefs"]["intl.accept_languages"] == "en,en-US"


def test_headless_options_set_window_size():
    options = build_chrome_options(headless=True)
    assert "--headless=new" in options.arguments
    assert "--window-size=1920,1080" in options.arguments
    assert "--start-maximized" not in options.arguments


def test_extra_args_are_appended():
    assert "--no-sandbox" in build_chrome_options(headless=True, extra_args=["--no-sandbox"]).arguments


def test_profile_dir_is_passed_to_chrome(tmp_path):
    options = build_chrome_options(headless=False, profile_dir=tmp_path)
    assert f"--user-data-dir={tmp_path}" in options.arguments


def test_no_profile_dir_by_default():
    assert not any(a.startswith("--user-data-dir") for a in build_chrome_options(headless=False).arguments)