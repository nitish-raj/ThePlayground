from dataclasses import dataclass


@dataclass
class Place:
    place_id: str
    name: str
    vicinity: str
    latitude: float
    longitude: float

class PlaceV2:
    place_id: str
    types: list[str]
    phoneNumber: str
    internationalPhoneNumber: str
    formattedAddress: str
    globalCode: str
    compoundCode: str
    latitude: float
    longitude: float
    rating: float
    googleMapsUri: str
    websiteUri: str
    businessStatus: str
    userRatingCount: int
    displayName: str
    delivery: bool
    primaryType: str
    acceptsCreditCards: bool
    acceptsDebitCards: bool
    acceptsCashOnly: bool
    acceptsNfc: bool


@dataclass
class PlaceDetail:
    place_id: str
    name: str
    address: str
    phoneNumber: str
    website: str
