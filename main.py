from fastapi import FastAPI
from scraper import StrongholdScraper, ScraperParent, F2FScraper, ConectionScraper
from card import Card

app = FastAPI()
scraper: ScraperParent = ScraperParent()
scraper.scrapers.append(StrongholdScraper(scraper.driver, scraper.save))
scraper.scrapers.append(F2FScraper(scraper.driver, scraper.save))
scraper.scrapers.append(ConectionScraper(scraper.driver, scraper.save)) 

@app.get("/card/{card_name}")
def find_card(card_name: str) -> list[Card]:
    return scraper.scrape(card_name)
    
app.add_event_handler("shutdown", scraper.driver.quit)