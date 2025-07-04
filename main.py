from fastapi import FastAPI
from scrapers import *
from scraper_parent import ScraperParent
from card import Card

app = FastAPI()
scraper: ScraperParent = ScraperParent()
scraper.add_scraper(StrongholdScraper(scraper.driver, scraper.save))
scraper.add_scraper(F2FScraper(scraper.driver, scraper.save))
scraper.add_scraper(ConnectionScraper(scraper.driver, scraper.save))
scraper.add_scraper(SequenceScraper(scraper.driver, scraper.save))
scraper.add_scraper(TCGPlayerScraper(scraper.driver, scraper.save))
scraper.add_scraper(LegendaryScraper(scraper.driver, scraper.save))
scraper.add_scraper(UntouchablesScraper(scraper.driver, scraper.save))

@app.get("/card/{card_name}")
def find_card(card_name: str) -> list[Card]:
    return scraper.scrape(card_name)
    
app.add_event_handler("shutdown", scraper.driver.quit)