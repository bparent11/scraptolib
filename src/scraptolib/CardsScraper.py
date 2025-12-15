from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from pathlib import Path
import json
import time

from scraptolib.utils.helpers import human_delay, init_logger

lg = init_logger()

class CardsScraper:
    """
    Scraper designed to scrap pages similar to : https://www.doctolib.fr/search?location=xxx&speciality=xxx
    
    """

    def __init__(self, driver_path:str, waiting_time:float=3.0, target_path:str="results.json"):
        self.service = Service(executable_path=driver_path)
        self.options = Options()
        self.options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0 Safari/537.36")
        self.options.add_argument("--disable-blink-features=AutomationControlled")
        self.driver = webdriver.Chrome(service=self.service, options=self.options)

        self.waiting_time = waiting_time
        self.target_path = target_path

    def close(self):
        try:
            self.driver.quit()
        except:
            pass

    def handle_cookies(self):
        try:
            refuse_cookies_btn = WebDriverWait(self.driver, self.waiting_time).until(
                EC.element_to_be_clickable((By.XPATH, "//button[.//span[text()='Refuser']]"))
            )
            refuse_cookies_btn.click()

        except TimeoutException:
            print("Pas de bannière de cookies affichée, on continue.")

        except Exception as NotFound:
            raise KeyError(
                "Le bouton pour refuser les cookies n'a pas été trouvé"
            ) from NotFound
    
    def store_json_data(self, data:list[dict], target_path:str):
        """
        Store line by line
        """
        path = Path(target_path)

        if not path.exists():
            output = []
        else:
            with open(path, "r", encoding="utf-8") as f:
                output = json.load(f)

        output += data

        with open(path, "w", encoding="utf-8") as f:
            json.dump(output, f, indent=4, ensure_ascii=False)

    def look_for_next_page(self):
        try:
            next_page_btn = WebDriverWait(self.driver, 15.0).until(
                EC.presence_of_element_located(
                    (By.XPATH, '//a[@rel="next"]')
                )
            )
            next_page_href = next_page_btn.get_attribute("href")

        except TimeoutException:
            lg.info("Next page button not found")
            next_page_href = None

        return next_page_href

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
                lg.warning("Retry later détecté")
            elif "Désolé" in text:
                lg.warning("Erreur Doctolib détectée")

            return True

        except TimeoutException:
            lg.info("Retry later page is gone.")
            return False
        
    def handle_retry_later(self, current_page):
        backoff = 900

        while self.is_retry_later():
            lg.warning(f"Retry Later page detected -> waiting for {backoff}s")
            time.sleep(backoff)

            self.driver.delete_all_cookies()
            self.driver.execute_script("window.localStorage.clear();")
            self.driver.execute_script("window.sessionStorage.clear();")
            self.driver.execute_script("location.reload(true);")
            self.driver.get(current_page)

            human_delay(alpha=20)
        
        lg.info("Retry Later went away -> Scraper get back to work")
        time.sleep(5)
        self.handle_cookies()

    def run_scraping(self, place_input:str, query_input:str, only_href:bool=False):
        retrieved_data = []
        query_input = query_input.lower().replace(" ", "-")
        place_input = place_input.lower().replace(" ", "-")

        page_link = f"https://www.doctolib.fr/search?location={place_input}&speciality={query_input}"

        lg.info(page_link)

        self.driver.get(page_link)

        human_delay()

        self.handle_cookies()

        current_page = page_link

        while True:
            next_page_href = self.look_for_next_page()
            
            if (next_page_href is None) and (self.is_retry_later()):
                self.handle_retry_later(current_page)
                next_page_href = self.look_for_next_page()

            try:
                """Fetching CARDS"""
                cards = self.driver.find_elements(By.CSS_SELECTOR, "div.dl-card-variant-default")

                for card in cards:
                    # physician's page link
                    href = card.find_elements(By.TAG_NAME, "a")[0].get_attribute("href")

                    if only_href:
                        retrieved_data.append(
                            {
                                "Page_doctolib":href.split('&')[0],
                                "Nom_Recherche":query_input,
                                "Lieu_Recherche":place_input
                            }
                        )
                    else:
                        # physician's data
                        elements = card.find_elements(By.CSS_SELECTOR, "div.p-16 h2, div.p-16 p")
                        content = [ele.text.strip() for ele in elements if ele.text.strip() != ""]

                        retrieved_data.append(
                            {
                                "Pratiquant":content[0],
                                "Intitulé":content[1],
                                "Adresse":content[2],
                                "Ville":content[3],
                                "Page_doctolib":href.split('&')[0],
                                "Nom_Recherche":query_input,
                                "Lieu_Recherche":place_input
                            }
                        )

            except Exception as e:
                raise e

            if not next_page_href:
                self.store_json_data(
                    data=retrieved_data,
                    target_path=self.target_path
                )
                lg.info(f"{len(retrieved_data)} profile(s) retrieved")
                return "Scraping done"
            
            else:
                human_delay(alpha=20)

                self.driver.get(next_page_href)
                current_page = next_page_href
                current_page_nb = current_page.split("page=")[-1]
                lg.info(f"Scraping page {current_page_nb} -- {(int(current_page_nb)-1)*20} cards scraped")