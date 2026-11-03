"""Regression tests for the 'element click intercepted' failure seen on the real Google home page."""
import pytest
from selenium.common.exceptions import ElementClickInterceptedException, TimeoutException
from selenium.webdriver.common.by import By

from src.ui.pages.base_page import BasePage
from src.ui.pages.google_page import GooglePage

pytestmark = pytest.mark.unit


class CoveredElement:
    """Visible and enabled, but its click is intercepted `fail_times` times (an overlay is fading out)."""
    def __init__(self, fail_times):
        self.fail_times, self.clicks = fail_times, 0

    def is_displayed(self):
        return True

    def is_enabled(self):
        return True

    def click(self):
        self.clicks += 1
        if self.clicks <= self.fail_times:
            raise ElementClickInterceptedException("Other element would receive the click")


class ElementDriver:
    current_url = "https://www.google.com/?hl=en"

    def __init__(self, element):
        self.element = element

    def find_element(self, *locator):
        return self.element


LINK = (By.CSS_SELECTOR, "a[href*='/imghp']")


def test_click_retries_while_an_overlay_covers_the_element():
    element = CoveredElement(fail_times=2)
    BasePage(ElementDriver(element), timeout=5).click(LINK)
    assert element.clicks == 3  # two intercepted attempts, then success


def test_click_fails_with_a_descriptive_timeout_if_the_element_stays_covered():
    page = BasePage(ElementDriver(CoveredElement(fail_times=999)), timeout=1)
    with pytest.raises(TimeoutException, match="to be clickable"):
        page.click(LINK)


class InlineConsentDriver:
    """Consent dialog rendered inline (no iframe): the button stays on screen for a few reads after the click."""
    current_url = "https://www.google.com/?hl=en"

    def __init__(self, visible_reads_after_click):
        self.clicked, self.reads, self.visible_reads = False, 0, visible_reads_after_click
        self.switch_to = self
        self.button = self._Button(self)

    class _Button:
        def __init__(self, driver):
            self.driver = driver

        def is_displayed(self):
            return True

        def click(self):
            self.driver.clicked = True

    def default_content(self):
        pass

    def find_elements(self, by, value):
        if (by, value) == (By.ID, "W0wltc"):
            if self.clicked:
                self.reads += 1
                if self.reads > self.visible_reads:
                    return []  # dialog finally gone
            return [self.button]
        return []


def test_consent_dismissal_waits_until_the_inline_dialog_is_really_gone():
    """Regression: previously returned right after the click, while the backdrop still covered the page."""
    driver = InlineConsentDriver(visible_reads_after_click=2)
    assert GooglePage(driver, timeout=5, captcha_wait=0).dismiss_consent_if_present() is True
    assert driver.reads > 2  # kept polling until the button disappeared


def test_no_consent_dialog_returns_false_quickly():
    class NoDialog(InlineConsentDriver):
        def find_elements(self, by, value):
            return []
    assert GooglePage(NoDialog(0), timeout=5, captcha_wait=0).dismiss_consent_if_present(timeout=0.5) is False