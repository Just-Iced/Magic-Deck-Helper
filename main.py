from fastapi import FastAPI
from typing import Union
from pydantic import BaseModel

from scraper import Scraper

app = FastAPI()
scraper = Scraper()

class Item(BaseModel):
    name: str
    price: float
    is_offer: Union[bool, None] = None


@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/stronghold/{card_name}")
def get_stronghold_card(card_name: str):
    return scraper.scrape(f"https://magicstronghold.com/store/search/{card_name}")