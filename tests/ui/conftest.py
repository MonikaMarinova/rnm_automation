"""UI fixtures: a Chrome driver that is ALWAYS closed, plus a screenshot of the page on failure."""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import re
from threading import Thread
from urllib.parse import parse_qs, quote, urlsplit

import pytest
from selenium.common.exceptions import WebDriverException

from config.settings import settings
from src.ui.driver_factory import create_chrome_driver
from src.utils.logger import get_logger

log = get_logger("ui-conftest")


@pytest.fixture
def google_test_site():
    """Local Google-shaped pages for deterministic browser tests without external CAPTCHA."""
    searches = []
    image = quote(
        "<svg xmlns='http://www.w3.org/2000/svg' width='160' height='120'>"
        "<rect width='160' height='120' fill='#5c9ead'/></svg>"
    )

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            parsed_url = urlsplit(self.path)
            query = parse_qs(parsed_url.query).get("q", [""])[0]
            if parsed_url.path == "/":
                body = "<html lang='en'><a href='/imghp?hl=en'>Images</a></html>"
            elif parsed_url.path == "/imghp":
                body = (
                    "<html lang='en'><form action='/search' method='get'>"
                    "<input name='q'><button type='submit'>Search</button></form></html>"
                )
            elif parsed_url.path == "/search":
                searches.append(query)
                results = "".join(
                    f"<div data-q='{query} result {index}'>"
                    f"<img alt='Result {index}' width='160' height='120' "
                    f"src='data:image/svg+xml,{image}'></div>"
                    for index in range(1, 13)
                )
                body = (
                    "<html lang='en'><form action='/search' method='get'>"
                    f"<input name='q' value='{query}'><button type='submit'>Search</button></form>"
                    f"{results}</html>"
                )
            else:
                self.send_error(404)
                return

            content = body.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)

        def log_message(self, format, *args):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}/", searches
    finally:
        server.shutdown()
        server.server_close()
        thread.join()


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