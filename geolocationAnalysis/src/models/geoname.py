from dataclasses import dataclass
from typing import Optional

@dataclass
class GeoName:
    adminCode: int
    longitude: float
    geonameId: float
    toponymName: float
    countryId: str
    fcl:str
    population: int
    countryCode: str
    name: str
    fclName: str
    adminCodes: str
    countryName: str
    fcodeName: str
    adminName: str
    latitude: float
    fcode: str