from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

from scraptolib.utils.helpers import human_delay, store_json_data
from scraptolib.scrapers.Scraper import Scraper

class CardsScraper(Scraper):
    """
    Scraper designed to scrap pages similar to : https://www.doctolib.fr/search?location=xxx&speciality=xxx
    
    """

    def __init__(self, driver_path:str):
        super().__init__(
            driver_path=driver_path
        )

    def look_for_next_page(self):
        try:
            next_page_btn = WebDriverWait(self.driver, 15.0).until(
                EC.presence_of_element_located(
                    (By.XPATH, '//a[@rel="next"]')
                )
            )
            next_page_href = next_page_btn.get_attribute("href")

        except TimeoutException:
            self.lg.info("Next page button not found")
            next_page_href = None

        return next_page_href
        
    def run_scraping(self, place_input:str, query_input:str, only_href:bool=False, target_path:str="results_cards.json"):
        self.start_driver()
        
        retrieved_data = []
        query_input = query_input.lower().replace(" ", "-")
        place_input = place_input.lower().replace(" ", "-")

        page_link = f"https://www.doctolib.fr/search?location={place_input}&speciality={query_input}"

        self.lg.info(page_link)

        self.driver.get(page_link)

        if self.driver.current_url == "https://www.doctolib.fr/":
            self.lg.warning(
                f"place: {place_input} and query: {query_input} didn't return any results."
            )
            return None

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
                store_json_data(
                    data=retrieved_data,
                    target_path=target_path
                )
                self.lg.info(f"{len(retrieved_data)} profile(s) retrieved")
                self.stop_driver()
                self.lg.info("Successful job.")
                break
            else:
                human_delay(alpha=20)

                self.driver.get(next_page_href)
                current_page = next_page_href
                current_page_nb = current_page.split("page=")[-1]
                self.lg.info(f"Scraping page {current_page_nb} -- {(int(current_page_nb)-1)*20} cards scraped")

if __name__ == '__main__':
    print("test")