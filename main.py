from fastapi import FastAPI
from scraper import StrongholdScraper, ScraperParent, F2FScraper
from card import Card

app = FastAPI()
scraper: ScraperParent = ScraperParent()
stronghold_scraper = StrongholdScraper(scraper.driver, save_data=scraper.save)
f2f_scraper = F2FScraper(scraper.driver, scraper.save)

@app.get("/stronghold/{card_name}")
def get_stronghold_card(card_name: str) -> list[Card]:
    return stronghold_scraper.scrape(card_name)

@app.get("/f2f/{card_name}")
def get_f2f_card(card_name: str) -> list[Card]:
    return f2f_scraper.scrape(card_name)
    
app.add_event_handler("shutdown", scraper.driver.quit)