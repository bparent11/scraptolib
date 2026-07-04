from abc import ABC, abstractmethod
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

from scraptolib.utils.helpers import init_logger, human_delay

class Scraper(ABC):
    """
    Abstract base class for web scrapers using Selenium.

    Provides:
    - Driver management (start/stop) via Selenium Manager (auto-downloads the correct ChromeDriver)
    - Cookie banner handling
    - Retry handling for temporary website errors
    - Logging via `init_logger`

    Subclasses must implement the abstract method `run_scraping`.

    Methods
    -------
    __init__()
        Initializes the scraper with a logger. No driver path needed — Selenium Manager
        automatically resolves the correct ChromeDriver for your installed Chrome.

    start_driver()
        Starts a Selenium Chrome WebDriver if not already started.

    stop_driver()
        Stops the WebDriver, ignoring any exceptions if driver is already closed.

    handle_cookies()
        Attempts to click the "Refuser" button on cookie consent banners if present.

    is_retry_later() -> bool
        Detects "Retry later" or temporary error messages on the page.
        Returns True if such messages are found, False otherwise.

    handle_retry_later(current_page: str)
        Waits and retries loading the page if a temporary error ("Retry later") is detected.
        Clears cookies, localStorage, sessionStorage, reloads the page, and waits before retrying.

    run_scraping()
        Abstract method. Subclasses must implement this to define the scraping workflow.
    """

    def __init__(self, headless: bool = False):
        self.lg = init_logger()
        self.headless = headless
        self.driver = None

    def start_driver(self):
        if self.driver:
            pass
        else:
            options = Options()
            options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0 Safari/537.36")
            options.add_argument("--disable-blink-features=AutomationControlled")

            if self.headless:
                options.add_argument("--headless=new")
                options.add_argument("--no-sandbox")
                options.add_argument("--disable-dev-shm-usage")
                options.add_argument("--disable-gpu")
                options.add_argument("--window-size=1920,1080")

            self.driver = webdriver.Chrome(options=options)

    def stop_driver(self):
        try:
            self.driver.quit()
            self.driver = None
        except:
            pass
    
    def handle_cookies(self):
        try:
            refuse_cookies_btn = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[.//span[text()='Refuser']]"))
            )
            refuse_cookies_btn.click()

        except TimeoutException:
            self.lg.info("No cookies banner, scraping still going on ...")

    def is_retry_later(self):
        try:        
            elem = WebDriverWait(self.driver, 0.1).until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        "//pre[contains(., 'Retry later')]"
                        " | "
                        "//span[contains(., \"Désolé, une erreur s'est produite.\")]"
                    )
                )
            )

            text = elem.text

            if "Retry later" in text:
                self.lg.warning("Retry later détecté")
            elif "Désolé" in text:
                self.lg.warning("Erreur Doctolib détectée")

            return True

        except TimeoutException:
            return False
        
    def handle_retry_later(self, current_page): # fully reset the driver could work better
        while self.is_retry_later():
            # self.lg.warning(f"Retry Later page detected -> waiting for {backoff}s")
            human_delay(alpha=15)

            self.stop_driver()
            self.start_driver()
            self.driver.get(current_page)

            human_delay(alpha=20)
        
        self.lg.info("Retry Later went away -> Scraper get back to work")
        time.sleep(5)
        self.handle_cookies()

    @abstractmethod
    def run_scraping(self):
        pass