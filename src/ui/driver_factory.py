"""Chrome WebDriver creation. Options are built separately so they can be unit-tested without a browser."""
from pathlib import Path
from typing import Iterable, Optional

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from config.settings import settings
from src.utils.logger import get_logger

log = get_logger("driver")


def build_chrome_options(headless: bool, language: str = "en", extra_args: Iterable[str] = (),
                         profile_dir: Optional[Path] = None) -> Options:
    options = Options()
    options.add_argument(f"--lang={language}")                     # browser UI language
    options.add_experimental_option(                               # Accept-Language header
        "prefs", {"intl.accept_languages": f"{language},{language}-US"})
    options.add_argument("--disable-notifications")
    if headless:
        options.add_argument("--headless=new")
        options.add_argument("--window-size=1920,1080")            # no real window to maximize
    else:
        options.add_argument("--start-maximized")
    if profile_dir:                                                # keep cookies between runs
        options.add_argument(f"--user-data-dir={profile_dir}")
    for arg in extra_args:
        options.add_argument(arg)
    return options


def create_chrome_driver(headless: Optional[bool] = None, language: Optional[str] = None) -> webdriver.Chrome:
    """Start Chrome (Selenium Manager resolves the matching chromedriver) and maximize the window."""
    headless = settings.headless if headless is None else headless
    language = language or settings.browser_language
    log.info("Starting Chrome: headless=%s, language=%s, profile=%s, extra_args=%s",
             headless, language, settings.chrome_profile_dir, list(settings.chrome_args))
    options = build_chrome_options(headless, language, settings.chrome_args, settings.chrome_profile_dir)
    driver = webdriver.Chrome(options=options)
    if not headless:
        driver.maximize_window()
    return driver