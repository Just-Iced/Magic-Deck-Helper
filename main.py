from fastapi import FastAPI
from scrapers import *
from scraper_parent import ScraperParent
from card import Card

app = FastAPI()
scraper: ScraperParent = ScraperParent()

scraper.add_scraper(StrongholdScraper(scraper.save))
scraper.add_scraper(F2FScraper(scraper.save))
scraper.add_scraper(ConnectionScraper(scraper.save))
scraper.add_scraper(SequenceScraper(scraper.save))
scraper.add_scraper(TCGPlayerScraper(scraper.save))
scraper.add_scraper(LegendaryScraper(scraper.save))
scraper.add_scraper(UntouchablesScraper(scraper.save))

scraper.scrape_all_cards()

@app.get("/card/{card_name}")
def find_card(card_name: str) -> list[Card]:
    return scraper.get_card(card_name)
    
app.add_event_handler("shutdown", scraper.quit)