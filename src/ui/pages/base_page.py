"""Generic page-object helpers built on explicit waits (no sleeps, no implicit waits)."""
from typing import Callable, Optional, Tuple

from selenium.common.exceptions import ElementClickInterceptedException, TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from config.settings import settings

Locator = Tuple[str, str]


class BasePage:
    def __init__(self, driver: WebDriver, timeout: Optional[float] = None):
        self.driver = driver
        self.timeout = settings.ui_timeout if timeout is None else timeout

    def wait_until(self, condition: Callable, description: str, timeout: Optional[float] = None,
                   ignored_exceptions=()):
        """Explicit wait with a descriptive failure message and a hook for page-specific diagnosis."""
        wait = WebDriverWait(self.driver, self.timeout if timeout is None else timeout,
                             ignored_exceptions=ignored_exceptions)
        try:
            return wait.until(condition)
        except TimeoutException as exc:
            self.on_timeout(description)
            raise TimeoutException(
                f"Timed out waiting for {description} (url: {self.driver.current_url})") from exc

    def on_timeout(self, description: str) -> None:
        """Hook: subclasses can inspect the page and raise a clearer error than a bare timeout."""

    def find_visible(self, locator: Locator):
        return self.wait_until(EC.visibility_of_element_located(locator), f"{locator} to be visible")

    def click(self, locator: Locator, timeout: Optional[float] = None) -> None:
        def click_when_ready(driver):
            element = EC.element_to_be_clickable(locator)(driver)
            if not element:
                return False
            try:
                element.click()
                return True
            except ElementClickInterceptedException:
                return False

        self.wait_until(click_when_ready, f"{locator} to be clickable", timeout)

    def type_text(self, locator: Locator, text: str, submit: bool = False) -> None:
        field = self.find_visible(locator)
        field.clear()
        field.send_keys(text)
        if submit:
            field.send_keys(Keys.ENTER)

    def is_visible(self, locator: Locator, timeout: float = 2) -> bool:
        try:
            WebDriverWait(self.driver, timeout).until(EC.visibility_of_element_located(locator))
            return True
        except TimeoutException:
            return False