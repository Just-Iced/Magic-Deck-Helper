from card import Card
from typing import Union
from time import time
from scrapers import WebScraper
import json, jsonpickle, os.path, threading
class ScraperParent:
    def __init__(self, 
                 sites_formats: Union[dict[str, str], None] = None,
                 data_file: str = "data/card_data.json") -> None:
        
        self.site: str = ""
        self.sites_formats = sites_formats

        self.card_data: dict = {"last_scrape": 0, "cards": {}}
        self.data_file = data_file
        if os.path.exists(self.data_file):
            self.card_data = json.load(open(self.data_file))

        self.card_list = self.get_card_list()
        self.scrapers: list[WebScraper] = []

    def save(self, data: list[str], card_name: str) -> None:
        self.card_data["cards"][card_name] = data
        with open(self.data_file, "w") as data_file:
            json.dump(self.card_data, data_file, indent=4)

    def scrape(self, card_name: str) -> None:
        if card_name not in self.card_list:
            return
        threads = []
        card_index = self.card_list.index(card_name) + 1
        print(f"{card_index}/{len(self.card_list)} ({round(float(card_index) / len(self.card_list), 4)}%). {card_name}")
        for scraper in self.scrapers:
            x = threading.Thread(target=scraper.scrape, args=[card_name])
            x.start()
            threads.append(x)
            
        [thread.join() for thread in threads]
    
    def scrape_all_cards(self) -> None:
        if time() - self.card_data["last_scrape"] >= 86_400:
            [self.scrape(card) for card in self.card_list]
        self.card_data["last_scrape"] = time()
        with open(self.data_file, "w") as data_file:
            json.dump(self.card_data, data_file, indent=4)
    
    def get_card(self, card_name: str) -> list[Card]:
        if card_name not in self.card_data["cards"]:
            self.scrape(card_name)
        cards = [jsonpickle.decode(card) for card in self.card_data["cards"][card_name]]
        return cards

    def add_scraper(self, scraper: WebScraper) -> None:
        self.scrapers.append(scraper)

    def convert_scryfall_data_to_list(self) -> None:
        all_cards: dict = json.load(open("data/all_cards.json", encoding="utf-8"))
        cards_list = [card["name"] for card in all_cards]
        cards_list.sort()
        json.dump(cards_list, open("data/card_list.json", "w"), indent=4)

    def get_card_list(self) -> list[str]:
        if not os.path.exists("data/card_list.json"):
            self.convert_scryfall_data_to_list()
        return json.load(open("data/card_list.json"))
    
    def quit(self):
        [scraper.driver.quit() for scraper in self.scrapers]