"""Google Images: run a search and pick the n-th result image."""
from urllib.parse import urlparse

from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By

from src.ui.pages.base_page import Locator
from src.ui.pages.google_page import GooglePage
from src.utils.logger import get_logger

log = get_logger("images-page")

# Returns result <img> elements that are big enough to be real results and fully loaded.
# One JS round-trip instead of one WebDriver call per image.
_READY_RESULTS_JS = """
const [selector, minSize] = arguments;
return Array.from(document.querySelectorAll(selector)).filter(img =>
    img.offsetWidth >= minSize && img.offsetHeight >= minSize &&
    img.complete && img.naturalWidth > 0);
"""


class GoogleImagesPage(GooglePage):
    SEARCH_BOX: Locator = (By.CSS_SELECTOR, "textarea[name='q'], input[name='q']")
    # The task: result images sit under a div carrying a data-q attribute.
    RESULT_IMAGES_CSS = "div[data-q] img"
    MIN_RESULT_SIZE_PX = 80  # ignores tiny icons that may also live under data-q containers

    def wait_until_ready(self) -> "GoogleImagesPage":
        self.dismiss_consent_if_present()
        self.find_visible(self.SEARCH_BOX)
        return self

    def search(self, query: str) -> "GoogleImagesPage":
        log.info("Searching Google Images for %r", query)
        self.type_text(self.SEARCH_BOX, query, submit=True)
        # NOTE: a CAPTCHA URL (/sorry/...) also contains "q=" inside its continue= parameter,
        # so we compare the URL *path*, and treat "blocked" as a reason to stop waiting.
        self.wait_until(lambda d: self._on_results_page() or self.is_blocked(),
                        "the search results page to load")
        self.ensure_not_blocked()  # may pause for a human to solve the CAPTCHA
        self.wait_until(lambda d: self._on_results_page(), "the search results page to load")
        self.dismiss_consent_if_present()
        return self

    def _on_results_page(self) -> bool:
        return urlparse(self.driver.current_url).path.startswith("/search")

    def get_result_image(self, position: int):
        """Return the `position`-th (1-based) fully loaded result image, scrolled into view."""
        if position < 1:
            raise ValueError(f"Image position is 1-based, got {position}")

        def nth_loaded_image(driver):
            images = driver.execute_script(_READY_RESULTS_JS, self.RESULT_IMAGES_CSS, self.MIN_RESULT_SIZE_PX)
            return images[position - 1] if len(images) >= position else False

        image = self.wait_until(
            nth_loaded_image, f"result image #{position} under '{self.RESULT_IMAGES_CSS}'",
            ignored_exceptions=(StaleElementReferenceException,))  # results re-render while loading
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'instant'});", image)
        return image