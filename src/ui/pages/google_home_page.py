"""Google home page: entry point of the UI flow."""
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By

from config.settings import settings
from src.ui.pages.base_page import Locator
from src.ui.pages.google_images_page import GoogleImagesPage
from src.ui.pages.google_page import GooglePage
from src.utils.logger import get_logger

log = get_logger("home-page")


class GoogleHomePage(GooglePage):
    IMAGES_LINK: Locator = (By.CSS_SELECTOR, "a[href*='/imghp']")
    IMAGES_FALLBACK_URL = "https://www.google.com/imghp?hl=en"

    def open(self) -> "GoogleHomePage":
        self.driver.get(settings.google_url)
        self.ensure_not_blocked()
        self.dismiss_consent_if_present()
        return self

    def open_images(self) -> GoogleImagesPage:
        """Go to Google Images through the UI link; fall back to the URL if the link is not available."""
        try:
            self.click(self.IMAGES_LINK, timeout=5)
        except TimeoutException:
            log.warning("'Images' link not found on the home page; navigating by URL instead")
            self.driver.get(self.IMAGES_FALLBACK_URL)
        return GoogleImagesPage(self.driver, self.timeout, self.captcha_wait).wait_until_ready()