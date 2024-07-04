from dataclasses import dataclass
from typing import Optional

@dataclass
class Place:
    place_id: str
    name: str
    vicinity: str
    latitude: float
    longitude: float

@dataclass
class PlaceDetail:
    place_id: str
    name: str
    address: str
    phoneNumber: str
    website: str