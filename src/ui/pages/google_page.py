"""Behaviour shared by all Google pages: consent dialog, bot-detection and language checks."""
from typing import Optional

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

from config.settings import settings
from src.ui.pages.base_page import BasePage, Locator
from src.utils.logger import get_logger

log = get_logger("google")


class BlockedByGoogleError(RuntimeError):
    """Google served a CAPTCHA / 'unusual traffic' page instead of the expected content."""


class GooglePage(BasePage):
    # Selectors live here, in one place, because Google's markup changes without notice.
    CONSENT_FRAME: Locator = (By.CSS_SELECTOR, "iframe[src*='consent.google.com']")
    CONSENT_BUTTONS = (
        (By.ID, "W0wltc"),  # "Reject all"
        (By.XPATH, "//button[normalize-space()='Reject all' or .//*[normalize-space()='Reject all']]"),
        (By.ID, "L2AGLb"),  # "Accept all" as a last resort
    )
    CAPTCHA_FRAME: Locator = (By.CSS_SELECTOR, "iframe[src*='recaptcha']")

    def __init__(self, driver, timeout: Optional[float] = None, captcha_wait: Optional[float] = None):
        super().__init__(driver, timeout)
        self.captcha_wait = settings.captcha_wait if captcha_wait is None else captcha_wait

    def is_blocked(self) -> bool:
        return "/sorry/" in self.driver.current_url or bool(self.driver.find_elements(*self.CAPTCHA_FRAME))

    def ensure_not_blocked(self) -> None:
        """Raise if Google shows a CAPTCHA. With RM_CAPTCHA_WAIT > 0, give a human time to solve it."""
        if not self.is_blocked():
            return
        if self.captcha_wait > 0:
            log.warning("Google is asking for a CAPTCHA. Solve it in the browser window; waiting up to %ss",
                        self.captcha_wait)
            try:
                WebDriverWait(self.driver, self.captcha_wait).until(lambda _: not self.is_blocked())
                log.info("CAPTCHA solved, continuing")
                return
            except TimeoutException:
                pass
        message = f"Google is showing a CAPTCHA / unusual-traffic page ({self.driver.current_url})."
        if self.captcha_wait == 0:
            message += " Automated tests do not attempt to solve CAPTCHAs."
        else:
            message += (
                " Run non-headless with RM_CAPTCHA_WAIT set to give a human time to solve it, "
                "or retry later.")
        raise BlockedByGoogleError(message)

    def on_timeout(self, description: str) -> None:
        self.ensure_not_blocked()  # a timeout caused by a CAPTCHA deserves a clear message

    def page_language(self) -> str:
        """Value of <html lang>, used to verify the page is rendered in English."""
        return self.driver.find_element(By.TAG_NAME, "html").get_attribute("lang") or ""

    def dismiss_consent_if_present(self, timeout: float = 3) -> bool:
        """Close the EU cookie-consent dialog if shown (it is, e.g., in Bulgaria). Returns True if it was."""
        frames = self.driver.find_elements(*self.CONSENT_FRAME)
        if frames:
            self.driver.switch_to.frame(frames[0])
        try:
            button = self._find_consent_button(timeout)
            if button is None:
                return False
            button.click()
            log.info("Consent dialog dismissed")
        finally:
            self.driver.switch_to.default_content()
        self.wait_until(
            lambda d: (
                not d.find_elements(*self.CONSENT_FRAME)
                and "consent." not in d.current_url
                and not any(
                    element.is_displayed()
                    for locator in self.CONSENT_BUTTONS
                    for element in d.find_elements(*locator)
                )
            ),
            "the consent dialog to close",
            timeout,
        )
        return True

    def _find_consent_button(self, timeout: float) -> Optional[object]:
        def first_displayed(driver):
            for locator in self.CONSENT_BUTTONS:
                for element in driver.find_elements(*locator):
                    if element.is_displayed():
                        return element
            return False
        try:
            return WebDriverWait(self.driver, timeout).until(first_displayed)
        except TimeoutException:
            return None