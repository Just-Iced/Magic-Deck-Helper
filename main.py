from fastapi import FastAPI
from scraper import Scraper

app = FastAPI()
scraper: Scraper = Scraper()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/stronghold/{card_name}")
def get_stronghold_card(card_name: str):
    return scraper.scrape(f"https://magicstronghold.com/store/search/{card_name}")

app.add_event_handler("shutdown", scraper.driver.quit)