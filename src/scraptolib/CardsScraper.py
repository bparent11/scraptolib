# import undetected_chromedriver as uc
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException

import logging
lg = logging.getLogger(__name__)

from scraptolib.utils.helpers import human_delay

class CardsScraper:
    """
    Scraper designed to scrap pages similar to : https://www.doctolib.fr/search?location=xxx&speciality=xxx
    
    """

    def __init__(self, driver_path:str, waiting_time:float=3.0):
        self.service = Service(executable_path=driver_path)
        self.options = Options()
        self.options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0 Safari/537.36")
        self.options.add_argument("--disable-blink-features=AutomationControlled")
        self.driver = webdriver.Chrome(service=self.service, options=self.options)

        self.waiting_time = waiting_time

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
        
        # def check_retry_later(self):
        #     while True:
        #         try:
        #             # Si le texte "Retry later" est présent, on attend et on rafraîchit
        #             WebDriverWait(driver, 0.5).until(
        #                 EC.presence_of_element_located(
        #                     (By.XPATH, "//pre[contains(text(), 'Retry later')]")
        #                 )
        #             )
        #             print("Page en mode 'Retry later', redémarrage ... ")
        #             print(f"Lien actuel : {page_link}")

        #             # restart
        #             driver.quit()
        #             driver.delete_all_cookies()
        #             driver.execute_script("window.localStorage.clear();")
        #             driver.execute_script("window.sessionStorage.clear();")
        #             driver.get("https://www.doctolib.fr/")
        #             time.sleep(3)
        #             driver = webdriver.Chrome(service=service)
        #             time.sleep(3)
        #             driver.get(page_link)
        #             first = True

        #             print("test")
        #         except:
        #             # Si l'élément n'est plus là, on sort de la boucle
        #             break

    def run_scraping(self, place_input:str, query_input:str):
        query_input = query_input.lower().replace(" ", "-")
        place_input = place_input.lower().replace(" ", "-")

        page_link = f"https://www.doctolib.fr/search?location={place_input}&speciality={query_input}"

        print(page_link)
        lg.info(page_link)

        self.driver.get(page_link)

        human_delay()

        self.handle_cookies()

        human_delay()

        next_page_btn = self.driver.find_elements(By.XPATH, '//a[@rel="next"]')

        if next_page_btn:
            lg.info("Next page does exist")
            next_page_exists = True
            next_page_href = next_page_btn[0].get_attribute("href")
        else:
            lg.info("Next page doesn't exist")
            next_page_exists = False

        human_delay()

        try:
            """Fetching CARDS"""
            cards = self.driver.find_elements(By.CSS_SELECTOR, "div.dl-card-variant-default")
            for card in cards:
                try:
                    # physician's data
                    content = card.find_element(By.CSS_SELECTOR, "div.p-16").text

                    human_delay()

                    # physician's page link
                    href = card.find_elements(By.TAG_NAME, "a")[0].get_attribute("href")

                    human_delay()

                    results = content.split("\n") + [href]

                    lg.info(str(results))

                except NoSuchElementException:
                    print('Issue with a card')
                    continue
                break
        except:
            print('Issue with the cards')
            raise Exception

        if not next_page_exists:
            return "Scraping done"
        else:
            self.driver.get(next_page_href)
            human_delay()
            human_delay()
            human_delay()
            return "Test done"