from scraptolib.CardsScraper import CardsScraper

scpr = CardsScraper(driver_path="chromedriver.exe")

scpr.run_scraping(place_input='lorraine', query_input='osteopathe du sport')

scpr.close()