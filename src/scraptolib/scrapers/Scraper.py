from abc import ABC, abstractmethod
import time

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
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
    - Driver management (start/stop)
    - Cookie banner handling
    - Retry handling for temporary website errors
    - Logging via `init_logger`

    Subclasses must implement the abstract method `run_scraping`.

    Methods
    -------
    __init__(driver_path: str)
        Initializes the scraper with the path to the Chrome driver and a logger.

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

    def __init__(self, driver_path:str):
        """
        
        """
        self.lg = init_logger()
        self.driver_path = driver_path
        self.driver = None

    def start_driver(self):
        if self.driver:
            pass
        else:
            service = Service(executable_path=self.driver_path)
            options = Options()
            options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0 Safari/537.36")
            options.add_argument("--disable-blink-features=AutomationControlled")
            self.driver = webdriver.Chrome(service=service, options=options)

    def stop_driver(self):
        try:
            self.driver.quit()
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
            elem = WebDriverWait(self.driver, 10.0).until(
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
        
    def handle_retry_later(self, current_page):
        backoff = 1200

        while self.is_retry_later():
            self.lg.warning(f"Retry Later page detected -> waiting for {backoff}s")
            time.sleep(backoff)

            self.driver.delete_all_cookies()
            self.driver.execute_script("window.localStorage.clear();")
            self.driver.execute_script("window.sessionStorage.clear();")
            self.driver.execute_script("location.reload(true);")
            self.driver.get(current_page)

            human_delay(alpha=20)
        
        self.lg.info("Retry Later went away -> Scraper get back to work")
        time.sleep(5)
        self.handle_cookies()

    @abstractmethod
    def run_scraping(self):
        pass