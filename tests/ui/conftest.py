"""UI fixtures: a Chrome driver that is ALWAYS closed, plus a screenshot of the page on failure."""
import re

import pytest
from selenium.common.exceptions import WebDriverException

from config.settings import settings
from src.ui.driver_factory import create_chrome_driver
from src.utils.logger import get_logger

log = get_logger("ui-conftest")


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Expose each phase's report on the item so fixtures can tell whether the test failed."""
    outcome = yield
    setattr(item, f"rep_{call.when}", outcome.get_result())


@pytest.fixture
def driver(request):
    browser = create_chrome_driver(headless=request.config.getoption("--headless"))
    try:
        yield browser
    finally:  # runs whether the test passed, failed or errored
        report = getattr(request.node, "rep_call", None)
        if report is not None and report.failed:
            _save_failure_screenshot(browser, request.node.name)
        browser.quit()


def _save_failure_screenshot(browser, test_name: str) -> None:
    """Best effort: a diagnostics problem must never hide the real failure."""
    try:
        target = settings.output_dir / "failures" / (re.sub(r"[^\w.-]+", "_", test_name) + ".png")
        target.parent.mkdir(parents=True, exist_ok=True)
        browser.save_screenshot(str(target))
        log.info("Failure screenshot saved to %s", target)
    except WebDriverException as exc:
        log.warning("Could not capture failure screenshot: %s", exc)