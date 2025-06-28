from fastapi import FastAPI
from scraper import Scraper
from card import Card

app = FastAPI()
scraper: Scraper = Scraper()

@app.get("/stronghold/{card_name}")
def get_stronghold_card(card_name: str) -> list[Card]:
    return scraper.scrape(f"https://magicstronghold.com/store/search/{card_name}")

@app.get("/f2f/{card_name}")
def get_f2f_card(card_name: str) -> list[Card]:
    return scraper.scrape(f"https://facetofacegames.com/en-us/search?q={card_name}&filter__Availability=In+Stock")

app.add_event_handler("shutdown", scraper.driver.quit)