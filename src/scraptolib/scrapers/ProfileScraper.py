import time

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from scraptolib.utils.helpers import human_delay, store_json_data
from scraptolib.scrapers.Scraper import Scraper

class ProfileScraper(Scraper):
    """
    Scraper designed to scrap pages similar to : "https://www.doctolib.fr/osteopathe/stains/xxx-xxx"
    
    """

    def __init__(self, driver_path:str):
        super().__init__(
            driver_path=driver_path
        )

    def get_locations(self):
        try:
            locations = WebDriverWait(self.driver, 5).until(
                EC.presence_of_all_elements_located(
                    (By.XPATH, "//div[contains(@class, 'dl-pill-list')]//a")
                )
            )
            return [(elem.text, elem.get_attribute("href")) for elem in locations]
        except TimeoutException:
            return [("", self.driver.current_url)]
        
    def get_name(self):
        try:
            name = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//span[@itemprop='name']")
                )
            )
            return name.text
        except TimeoutException:
            return ""

    def get_specialty(self):
        try:
            specialty = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//div[@class='dl-profile-header-speciality']")
                )
            )

            try:
                specialty.find_element(
                    By.XPATH, 
                    "//div[@class='dl-profile-organization-icon']"
                )
                is_establishment = True
            except NoSuchElementException:
                is_establishment = False

            # print(f"Speciality method: {specialty.get_attribute('class')}")
            return (specialty.text, is_establishment)
        except TimeoutException:
            return ""

    def get_address(self):
        try:
            address = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//div[contains(@data-test, 'location')]")
                )
            )
            return address.text
        except TimeoutException:
            return ""
    
    def get_skills(self):
        try:
            skills = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//div[@class='dl-profile-skills']")
                )
            )

            return skills.text.split("\n")
        except TimeoutException:
            return ""
    
    def get_summary(self):
        try:
            summary = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//div[contains(@class, 'dl-profile-bio')]")
                )
            )

            return summary
        except TimeoutException:
            return ""

    def get_languages(self):
        try:
            languages = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//h3[contains(text(), 'Langues parlées')]/parent::div")
                )
            )
            
            return languages.text.split('\n')[-1]
        except TimeoutException:
            return ""

    def get_website(self):
        try:
            website = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//h3[contains(text(), 'Site web')]/parent::div//a")
                )
            )
        except TimeoutException:
            return ""
        
        return website.get_attribute("href")
    
    def get_contact_details(self):
        try:
            contact_details = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//h3[contains(text(), 'Coordonnées')]/parent::div//div")
                )
            )

            return contact_details.text.replace(" ", "")
        except TimeoutException:
            return ""

    
    def get_prices(self):
        try:
            prices = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//h2[contains(text(), 'Tarifs')]/parent::div/ul/li")
                )
            )

            return prices.text
        except TimeoutException:
            return ""
        
    def get_history(self):
        try:
            history = WebDriverWait(self.driver, 5).until(
                EC.presence_of_all_elements_located(
                    (By.XPATH, "//div[contains(@class, 'dl-profile-history')]")
                )
            )

            return [elem.text for elem in history]
        except TimeoutException:
            return ""

    def scrap_full_page():
        pass

if __name__ == '__main__':
    print("test")