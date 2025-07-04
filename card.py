from pydantic import BaseModel
from typing import Union

class Card(BaseModel):
    img: str
    link: str
    site: str
    price: Union[float, tuple[float, ...]]
    name: str