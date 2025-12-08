import time, random, logging

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

def human_delay(a=1.2, b=1.9):
    time.sleep(random.uniform(a, b))

def init_logger():
    lg = logging.getLogger(__name__)
    lg.setLevel(logging.INFO)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    # Format optionnel
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)

    # Ajouter le handler au logger
    lg.addHandler(console_handler)

    return lg

def check_retry_later(service, driver, page_link):
    while True:
        try:
            # Si le texte "Retry later" est présent, on attend et on rafraîchit
            WebDriverWait(driver, 0.5).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//pre[contains(text(), 'Retry later')]")
                )
            )
            print("Page en mode 'Retry later', redémarrage ... ")
            print(f"Lien actuel : {page_link}")

            # restart
            driver.quit()
            driver.delete_all_cookies()
            driver.execute_script("window.localStorage.clear();")
            driver.execute_script("window.sessionStorage.clear();")
            driver.get("https://www.doctolib.fr/")
            time.sleep(3)
            driver = webdriver.Chrome(service=service)
            time.sleep(3)
            driver.get(page_link)
            first = True

            print("test")

        except:
            # Si l'élément n'est plus là, on sort de la boucle
            break