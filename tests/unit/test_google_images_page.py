"""Page-object logic against a fake driver: position indexing, timeouts and CAPTCHA detection."""
import pytest
from selenium.common.exceptions import TimeoutException

from src.ui.pages.google_home_page import GoogleHomePage
from src.ui.pages.google_images_page import GoogleImagesPage
from src.ui.pages.google_page import BlockedByGoogleError

pytestmark = pytest.mark.unit


class FakeDriver:
    def __init__(self, images, url="https://www.google.com/search?q=x&udm=2"):
        self.images, self.current_url, self.scrolled = images, url, []

    def execute_script(self, script, *args):
        if "scrollIntoView" in script:
            self.scrolled.append(args[0])
            return None
        return self.images

    def find_elements(self, *locator):
        return []


def test_returns_nth_image_one_based_and_scrolls_to_it():
    driver = FakeDriver(images=["img1", "img2", "img3", "img4", "img5"])
    assert GoogleImagesPage(driver, timeout=0.2).get_result_image(4) == "img4"
    assert driver.scrolled == ["img4"]


def test_times_out_with_descriptive_message_when_too_few_images():
    page = GoogleImagesPage(FakeDriver(images=["img1"]), timeout=0.2)
    with pytest.raises(TimeoutException, match=r"result image #3 under 'div\[data-q\] img'"):
        page.get_result_image(3)


def test_captcha_page_is_reported_as_blocked_not_as_a_generic_timeout():
    page = GoogleImagesPage(
        FakeDriver(images=[], url="https://www.google.com/sorry/index?continue=x"),
        timeout=0.2,
        captcha_wait=0,
    )
    with pytest.raises(BlockedByGoogleError, match="CAPTCHA"):
        page.get_result_image(1)


def test_home_page_propagates_unattended_captcha_setting(monkeypatch):
    class Driver:
        current_url = "https://www.google.com/"

        def get(self, url):
            self.current_url = url

    monkeypatch.setattr(GoogleHomePage, "click", lambda self, locator, timeout=None: None)
    monkeypatch.setattr(GoogleImagesPage, "wait_until_ready", lambda self: self)

    images_page = GoogleHomePage(Driver(), captcha_wait=0).open_images()

    assert images_page.captcha_wait == 0


def test_position_must_be_positive():
    with pytest.raises(ValueError):
        GoogleImagesPage(FakeDriver(images=[]), timeout=0.2).get_result_image(0)


class SolvedAfterDriver(FakeDriver):
    """Shows a CAPTCHA URL for the first few reads, then the results page (a human solved it)."""
    def __init__(self, blocked_reads):
        super().__init__(images=[])
        self._reads, self._blocked_reads = 0, blocked_reads

    @property
    def current_url(self):
        self._reads += 1
        if self._reads <= self._blocked_reads:
            return "https://www.google.com/sorry/index?continue=https://www.google.com/search%3Fq%3Dx"
        return "https://www.google.com/search?q=x&udm=2"

    @current_url.setter
    def current_url(self, value):  # FakeDriver.__init__ assigns it
        pass


def test_blocked_without_wait_fails_immediately():
    page = GoogleImagesPage(SolvedAfterDriver(blocked_reads=99), timeout=0.2, captcha_wait=0)
    with pytest.raises(BlockedByGoogleError):
        page.ensure_not_blocked()


def test_blocked_with_wait_continues_once_a_human_solves_it():
    GoogleImagesPage(SolvedAfterDriver(blocked_reads=2), timeout=0.2, captcha_wait=5).ensure_not_blocked()


def test_blocked_with_wait_still_fails_if_never_solved():
    page = GoogleImagesPage(SolvedAfterDriver(blocked_reads=999), timeout=0.2, captcha_wait=1)
    with pytest.raises(BlockedByGoogleError, match="RM_CAPTCHA_WAIT"):
        page.ensure_not_blocked()


def test_captcha_url_is_not_mistaken_for_results_page():
    """Regression: the /sorry/ URL contains 'q=' (inside continue=) but is NOT the results page."""
    page = GoogleImagesPage(SolvedAfterDriver(blocked_reads=99), timeout=0.2)
    assert page._on_results_page() is False
    assert GoogleImagesPage(FakeDriver(images=[]), timeout=0.2)._on_results_page() is True