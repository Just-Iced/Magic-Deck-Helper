import selenium
from selenium.webdriver.common.by import By
from typing import Union
from selenium.webdriver import Firefox
from pydantic import BaseModel
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from time import sleep

class Card(BaseModel):
    img: str
    link: str
    price: float
    in_stock: bool = True

class Scraper:
    def __init__(self, sites_formats: Union[dict[str, str], None] = None) -> None:
        self.site: Union[str, None] = None
        self.cards = []
        self.driver: Firefox = Firefox()
        self.sites_formats = sites_formats
        
    def scrape(self, site: str) -> list[Card]:
        self.cards = []
        self.site = site.lstrip("http").lstrip("s").lstrip("://").lstrip("www.").split("/")[0]
        self.driver.get(site)
        self.driver.execute_script("document.body.style.zoom = '0.1'")
        match self.site:
            case "magicstronghold.com":
                self.stronghold_scrape()
            case _:
                print("Invalid website")
        print(len(self.cards))
        return self.cards
    
    def stronghold_scrape(self) -> None:
        WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.CLASS_NAME, "prodImage")))
        sleep(7)
        page_cards = self.driver.find_elements(By.CLASS_NAME, "searchResult")
        for page_card in page_cards:
            try:
                img = page_card.find_element(By.CLASS_NAME, "prodImage").get_dom_attribute("src")
                link = "https://magicstronghold.com" + page_card.find_element(By.CLASS_NAME, "searchResultLeftTop").get_dom_attribute("href")
                price = page_card.find_element(By.CLASS_NAME, "prodPrice").text.strip("$")
                in_stock = "fa-shopping-cart" in page_card.find_element(By.CLASS_NAME, "quickAddBtn").get_dom_attribute("class")
                card = Card(img=img, link=link, price=float(price), in_stock=in_stock)
                self.cards.append(card)
            except NoSuchElementException:
                pass