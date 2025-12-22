import time, datetime

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

            return summary.text
        except TimeoutException:
            return ""

    def get_languages(self):
        try:
            languages = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//h3[contains(text(), 'Langues parlées')]/parent::div")
                )
            )
            
            return languages.text.split('\n')[-1].replace(",", "").replace("et ", "").split()
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
                EC.presence_of_all_elements_located(
                    (By.XPATH, "//h2[contains(text(), 'Tarifs')]/parent::div/ul/li")
                )
            )

            extraction = [elem.text.split("\n") for elem in prices]
            return {
                elem[0]:elem[1]
                for elem in extraction
            }
        except TimeoutException:
            return ""
        
    def get_history(self):
        try:
            history = WebDriverWait(self.driver, 5).until(
                EC.presence_of_all_elements_located(
                    (By.XPATH, "//div[contains(@class, 'dl-profile-history')]")
                )
            )
            extraction = [elem.text.split('\n') for elem in history]
            
            output = {}
            for elem in extraction:
                key = elem[0]
                if key != "Associations":
                    value = [(elem[i+1], elem[i+2]) for i in range(0, len(elem)-1, 2)]
                    output[key] = value
                else:
                    output[key] = elem[1:]
            return output
        
        except TimeoutException:
            return ""
        
    def run_scraping(self, profile_href:str):
        self.driver.get(profile_href) # assert href format
        self.driver.execute_script("document.body.style.zoom='1%'")

        time.sleep(3)

        locations = self.get_locations()

        # avoid sending another useless request to doctolib
        for i, location in enumerate(locations):
            if location[1]==profile_href:
                del locations[i]
                locations.insert(0, location)
                break

        output = []
        for i, location in enumerate(locations):
            if i == 0: # avoid sending another useless request to doctolib
                pass
            else:
                human_delay(alpha=5)
                self.driver.get(location[1])
                self.driver.execute_script("document.body.style.zoom='1%'")
            
            time.sleep(3)

            name = self.get_name()
            speciality = self.get_specialty()
            address = self.get_address()
            skills = self.get_skills()
            languages = self.get_languages()
            summary = self.get_summary()
            website = self.get_website()
            contact_details = self.get_contact_details()
            prices = self.get_prices()
            history = self.get_history()

            output.append(
                {
                    "location": location,
                    "name": name,
                    "speciality": speciality,
                    "address": address,
                    "skills": skills,
                    "languages": languages,
                    "summary": summary,
                    "website": website,
                    "contact_details": contact_details,
                    "prices": prices,
                    "history": history,
                    "scrap_timestamp":datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
            )
        return output

if __name__ == '__main__':
    print("test")