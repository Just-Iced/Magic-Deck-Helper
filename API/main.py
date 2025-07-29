from fastapi import FastAPI
from scrapers import *
from scraper_parent import ScraperParent
from card import Card

app = FastAPI()
scraper: ScraperParent = ScraperParent()

scrapers = [StrongholdScraper, F2FScraper, ConnectionScraper, 
            SequenceScraper, TCGPlayerScraper, LegendaryScraper, 
            UntouchablesScraper]

[scraper.add_scraper(scraperClass(scraper.save)) for scraperClass in scrapers]

# Commented out for now as it would take ~5 days to complete scraping
# scraper.scrape_all_cards()

@app.get("/card/{card_name}")
def find_card(card_name: str) -> list[Card]:
    return scraper.get_card(card_name)
    
app.add_event_handler("shutdown", scraper.quit)