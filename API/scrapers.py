from card import Card
from selenium.webdriver.common.by import By
from typing import Union, Callable, Any
from selenium.webdriver import FirefoxOptions, Firefox
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.remote.webelement import WebElement
from time import time, sleep
import jsonpickle

class WebScraper:
    def __init__(
            self, 
            save_data: Callable[..., None],
        ) -> None:
        options = FirefoxOptions()
        options.add_argument("--headless")
        self.driver: Firefox = Firefox(options=options)
        self.driver.minimize_window()
        self.save_data = save_data

        self.class_name: str
        self.card_name_class: str
        self.site: str
        self.main_site: str

        self.in_stock: Callable[..., bool]
        self.price: Callable[..., Union[float, tuple[float, ...]]]

    def scrape(
                self,
                card_name: str
            ) -> list[Card]:
        init_time = time()
        self.cards = []
        card_data: list[str] = []
        site = self.site.replace("{card_name}", card_name)
        self.driver.get(site)
        self.driver.execute_script("document.body.style.zoom = '0.1'")
        try:
            WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located((By.CLASS_NAME, self.class_name)))
        except TimeoutException:
            return []
        page_cards = self.driver.find_elements(By.CLASS_NAME, self.class_name)
        for page_card in page_cards:
            try:
                page_card_name = page_card.find_element(By.CLASS_NAME, self.card_name_class).text
                if self.in_stock(page_card):
                    img_element = page_card.find_element(By.CSS_SELECTOR, "img")
                    img_src = img_element.get_dom_attribute("src")

                    link_element = page_card.find_element(By.CSS_SELECTOR, "a")
                    link = self.main_site + link_element.get_dom_attribute("href")
                    
                    card = Card(img=img_src, site=self.main_site, link=link, price=self.price(page_card), name=page_card_name)
                    card_data.append(str(jsonpickle.encode(card)))
                    self.cards.append(card)
            except NoSuchElementException:
                pass
        self.save_data(card_data, card_name)
        print(f"{self.main_site}: {round(time() - init_time, 2)} seconds")
        return self.cards
    
class StrongholdScraper(WebScraper):
    def __init__(self, save_data: Callable) -> None:
        super().__init__(save_data)
        self.class_name = "searchResult"
        self.site = "https://magicstronghold.com/store/search/{card_name}"
        self.main_site = "magicstronghold.com"
        self.card_name_class = "prodName"
        sleep(3)
        self.driver.get(self.site)

    def in_stock(self, page_card: WebElement) -> bool:
        shop_btn_classes = page_card.find_element(By.CLASS_NAME, "quickAddBtn").get_dom_attribute("class")
        return "fa-shopping-cart" in shop_btn_classes
    
    def price(self, page_card: WebElement) -> float:
        return float(page_card.find_element(By.CLASS_NAME, "prodPrice").text.strip("$"))
    
class F2FScraper(WebScraper):
    def __init__(self, save_data: Callable) -> None:
        super().__init__(save_data)
        self.class_name = "bb-card-wrapper"
        self.site = "https://facetofacegames.com/en-us/search?q={card_name}&filter__Availability=In+Stock"
        self.main_site = "facetofacegames.com"
        self.card_name_class = "bb-card-title"
        sleep(3)
        self.driver.get(self.site)

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
    
class ConnectionBackend(WebScraper):
    def __init__(self, save_data: Callable) -> None:
        super().__init__(save_data)
        self.card_name_class = "name"
        self.class_name = "product"

    def in_stock(self, page_card: WebElement) -> bool:
        return True
    
    def price(self, page_card: WebElement) -> Union[float, tuple[float, float]]:
        price = []
        prices = page_card.find_elements(By.CLASS_NAME, "add-to-cart-form")

        if len(prices) > 1:
            for price_text in prices:
                new_price = price_text.get_dom_attribute("data-price").strip().lstrip("CAD$ ").replace(",", "")
                price.append(float(new_price))
            price = tuple(price)
        else:
            price = float(prices[0].get_dom_attribute("data-price").strip().lstrip("CAD$ "))
        return price

class ConnectionScraper(ConnectionBackend):
    def __init__(self, save_data: Callable[..., Any]) -> None:
        super().__init__(save_data)
        self.site = "https://www.theconnectiongames.com/advanced_search?utf8=%E2%9C%93&search[fuzzy_search]={card_name}&search[tags_name_eq]=&search[in_stock]=0&search[in_stock]=1"
        self.main_site = "theconnectiongames.com"
        sleep(3)
        self.driver.get(self.site)

class SequenceScraper(ConnectionBackend):
    def __init__(self, save_data: Callable) -> None:
        super().__init__(save_data)
        self.site = "https://www.sequencecomics.ca/advanced_search?utf8=✓&search[fuzzy_search]={card_name}&search[in_stock]=0&search[in_stock]=1"
        self.main_site = "sequencecomics.ca"
        sleep(3)
        self.driver.get(self.site)

class TCGPlayerScraper(WebScraper):
    def __init__(self, save_data: Callable) -> None:
        super().__init__(save_data)
        self.class_name = "search-result"
        self.site = "https://www.tcgplayer.com/search/magic/product?productLineName=magic&q={card_name}&view=grid&ProductTypeName=Cards&page=1&inStock=true"
        self.main_site = "tcgplayer.com"
        self.card_name_class = "product-card__title"
        sleep(3)
        self.driver.get(self.site)

    def in_stock(self, page_card: WebElement) -> bool:
        return True
    
    def price(self, page_card: WebElement) -> float:
        price_text = page_card.find_element(By.CLASS_NAME, "inventory__price-with-shipping").text
        try:
            return float(price_text.strip("$").replace(",", ""))
        except ValueError:
            return 0
        
class LegendaryScraper(WebScraper):
    def __init__(self, save_data: Callable[..., Any]) -> None:
        super().__init__(save_data)
        self.class_name = "productitem"
        self.site = "https://legendarycollectables.com/search?filter.v.availability=1&q=product_type%3AMTG+Single+AND+{card_name}"
        self.main_site = "legendarycollectables.com"
        self.card_name_class = "productitem--title"
        sleep(3)
        self.driver.get(self.site)

    def in_stock(self, page_card: WebElement) -> bool:
        return True
    
    def price(self, page_card: WebElement) -> float:
        price_text = page_card.find_element(By.CLASS_NAME, "price__current--min").text
        return float(price_text.strip("$").replace(",", ""))
    
class UntouchablesScraper(WebScraper):
    def __init__(self, save_data: Callable[..., Any]) -> None:
        super().__init__(save_data)
        self.class_name = "productCard__card"
        self.site = "https://untouchables.ca/pages/advanced-search?q={card_name}&game=mtg&availabilty=true&setNames=&colors=&rarities=&types=&pricemin=&pricemax=&page=1&order=price-ascending"
        self.main_site = "untouchables.ca"
        self.card_name_class = "productCard__title"
        sleep(3)
        self.driver.get(self.site)

    def in_stock(self, page_card: WebElement) -> bool:
        return True
    
    def price(self, page_card: WebElement) -> float:
        price_text = page_card.find_element(By.CLASS_NAME, "productCard__price").text
        return float(price_text.lstrip("$").rstrip(" CAD").replace(",", ""))