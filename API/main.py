from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from scrapers import *
from scraper_parent import ScraperParent
from card import Card

app = FastAPI()

origins = ["http://localhost:8888"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

scraper: ScraperParent = ScraperParent()

scrapers = [StrongholdScraper, F2FScraper, ConnectionScraper, 
            SequenceScraper, TCGPlayerScraper, LegendaryScraper, 
            UntouchablesScraper]

[scraper.add_scraper(scraperClass(scraper.save)) for scraperClass in scrapers]

app.add_middleware(
CORSMiddleware, 
allow_origins=["*"], 
allow_credentials=True, 
allow_methods=["*"], 
allow_headers=["*"], 
)

# Commented out for now as it would take ~5 days to complete scraping
# scraper.scrape_all_cards()

@app.get("/card/{card_name}")
def find_card(card_name: str) -> list[Card]:
    return scraper.get_card(card_name)

@app.get("/cardlist")
def get_card_list() -> list[str]:
    return scraper.card_list

app.add_event_handler("shutdown", scraper.quit)