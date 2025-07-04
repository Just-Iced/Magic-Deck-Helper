from card import Card
from selenium.webdriver.common.by import By
from typing import Union, Callable, Any
from selenium.webdriver import Firefox
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.remote.webelement import WebElement
from time import sleep, time
import json, jsonpickle

class ScraperParent:
    def __init__(self, 
                 sites_formats: Union[dict[str, str], None] = None,
                 data_file: str = "data/card_data.json") -> None:
        
        self.site: str = ""
        self.driver: Firefox = Firefox()
        self.driver.minimize_window()
        self.sites_formats = sites_formats

        self.card_data: dict = {"last_scrape": 0, "cards": []}
        self.data_file = data_file
        self.cards: list[Card] = []
        try:
            self.card_data = json.load(open(self.data_file))
            for card_json in self.card_data["cards"]:
                card: Card = jsonpickle.decode(card_json)
                self.cards.append(card)
        except FileNotFoundError:
            pass

        self.scrapers: list[WebScraper] = []

    def save(self, data: list[str]):
        self.card_data["last_scrape"] = time()
        self.card_data["cards"] = data
        json.dump(self.card_data, open(self.data_file, "w"), indent=4)

    def scrape(self, card_name: str):
        cards: list[Card] = []
        for scraper in self.scrapers:
            for card in scraper.scrape(card_name):
                cards.append(card)
        return cards

class WebScraper:
    def __init__(
            self, 
            driver: Firefox,
            save_data: Callable,
        ) -> None:
        
        self.driver: Firefox = driver
        self.save_data = save_data
        self.card_data: list[str] = []

        self.class_name: str
        self.card_name_class: str
        self.site: str
        self.main_site: str

        self.in_stock: Callable[[Any, WebElement], bool]
        self.price: Callable[[Any, WebElement], Union[float, tuple[float, float]]]

    def scrape(
                self,
                card_name: str
            ) -> list[Card]:
        
        self.cards = []
        site = self.site.replace("{card_name}", card_name)
        self.driver.get(site)
        self.driver.execute_script("document.body.style.zoom = '0.1'")
        try:
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, self.class_name)))
        except TimeoutException:
            return []
        sleep(5)
        page_cards = self.driver.find_elements(By.CLASS_NAME, self.class_name)
        for page_card in page_cards:
            try:
                page_card_name = page_card.find_element(By.CLASS_NAME, self.card_name_class).text
                if self.in_stock(page_card) and card_name.lower() in page_card_name.lower().strip():
                    img_element = page_card.find_element(By.CSS_SELECTOR, "img")
                    img_src = img_element.get_dom_attribute("src")

                    link_element = page_card.find_element(By.CSS_SELECTOR, "a")
                    link = self.main_site + link_element.get_dom_attribute("href")
                    
                    card = Card(img=img_src, site=self.main_site, link=link, price=self.price(page_card))
                    self.card_data.append(str(jsonpickle.encode(card)))
                    self.cards.append(card)
            except NoSuchElementException:
                pass
        self.save_data(self.card_data)
        return self.cards
    
class StrongholdScraper(WebScraper):
    def __init__(self, driver: Firefox, save_data: Callable) -> None:
        super().__init__(driver, save_data)
        self.class_name = "searchResult"
        self.site = "https://magicstronghold.com/store/search/{card_name}"
        self.main_site = "magicstronghold.com"
        self.card_name_class = "prodName"

    def in_stock(self, page_card: WebElement) -> bool:
        shop_btn_classes = page_card.find_element(By.CLASS_NAME, "quickAddBtn").get_dom_attribute("class")
        return "fa-shopping-cart" in shop_btn_classes
    
    def price(self, page_card: WebElement) -> float:
        return float(page_card.find_element(By.CLASS_NAME, "prodPrice").text.strip("$"))

class F2FScraper(WebScraper):
    def __init__(self, driver: Firefox, save_data: Callable) -> None:
        super().__init__(driver, save_data)
        self.class_name = "bb-card-wrapper"
        self.site = "https://facetofacegames.com/en-us/search?q={card_name}&filter__Availability=In+Stock"
        self.main_site = "facetofacegames.com"
        self.card_name_class = "bb-card-title"

    def in_stock(self, page_card: WebElement) -> bool:
        return True
    
    def price(self, page_card: WebElement) -> Union[float, tuple[float, float]]:
        price = []
        price_divs = page_card.find_elements(By.CLASS_NAME, "f2f-featured-variant")
        if len(price_divs) == 2:
            for price_div in price_divs:
                new_price = price_div.find_element(By.CSS_SELECTOR, ".price-item span + span").text
                price.append(float(new_price))
            price = tuple(price)
        else:
            price = float(price_divs[0].find_element(By.CSS_SELECTOR, ".price-item span + span").text)
        return price
    
class ConnectionScraper(WebScraper):
    def __init__(self, driver: Firefox, save_data: Callable) -> None:
        super().__init__(driver, save_data)
        self.class_name = "product"
        self.site = "https://www.theconnectiongames.com/advanced_search?utf8=%E2%9C%93&search[fuzzy_search]={card_name}&search[tags_name_eq]=&search[in_stock]=0&search[in_stock]=1"
        self.main_site = "theconnectiongames.com"
        self.card_name_class = "name"

    def in_stock(self, page_card: WebElement) -> bool:
        return True
    
    def price(self, page_card: WebElement) -> Union[float, tuple[float, float]]:
        price = []
        prices = page_card.find_elements(By.CLASS_NAME, "add-to-cart-form")

        if len(prices) > 1:
            for price_text in prices:
                new_price = price_text.get_dom_attribute("data-price").strip().lstrip("CAD$ ")
                price.append(float(new_price))
            price = tuple(price)
        else:
            price = float(prices[0].get_dom_attribute("data-price").strip().lstrip("CAD$ "))
        return price

class SequenceScraper(ConnectionScraper):
    def __init__(self, driver: Firefox, save_data: Callable) -> None:
        super().__init__(driver, save_data)
        self.site = "https://www.sequencecomics.ca/advanced_search?utf8=✓&search[fuzzy_search]={card_name}&search[in_stock]=0&search[in_stock]=1"
        self.main_site = "sequencecomics.ca"