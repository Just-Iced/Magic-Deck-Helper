from card import Card
from typing import Union
from selenium.webdriver import Firefox
from time import time
import json, jsonpickle
from scrapers import WebScraper

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

    def save(self, data: list[str]) -> None:
        self.card_data["last_scrape"] = time()
        self.card_data["cards"] = data
        json.dump(self.card_data, open(self.data_file, "w"), indent=4)

    def scrape(self, card_name: str) -> list[Card]:
        cards: list[Card] = []
        for scraper in self.scrapers:
            for card in scraper.scrape(card_name):
                cards.append(card)
        return cards
    
    def add_scraper(self, scraper: WebScraper) -> None:
        self.scrapers.append(scraper)