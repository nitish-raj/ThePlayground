from dataclasses import dataclass
from typing import List, Optional


@dataclass
class GeoName:
    """
    A dataclass representing a geographical location.

    Attributes:
        adminCode (Optional[str]): The administrative code of the location.
        longitude (float): The longitude coordinate of the location.
        geonameId (int): The unique identifier of the location.
        toponymName (str): The toponym name of the location.
        countryId (Optional[int]): The identifier of the country the location belongs to.
        fcl (str): The feature class of the location.
        population (Optional[int]): The population of the location.
        countryCode (Optional[str]): The code of the country the location belongs to.
        name (str): The name of the location.
        fclName (Optional[str]): The name of the feature class of the location.
        adminCodes (Optional[str]): The administrative codes of the location.
        countryName (Optional[str]): The name of the country the location belongs to.
        fcodeName (str): The name of the feature code of the location.
        adminName (str): The name of the administrative area the location belongs to.
        latitude (float): The latitude coordinate of the location.
        fcode (str): The feature code of the location.
    """

    adminCode: Optional[str] = None
    longitude: float = 0.0
    geonameId: int = 0
    toponymName: str = ""
    countryId: Optional[int] = None
    fcl: str = ""
    population: Optional[int] = None
    countryCode: Optional[str] = None
    name: str = ""
    fclName: Optional[str] = None
    adminCodes: Optional[str] = None
    countryName: Optional[str] = None
    fcodeName: str = ""
    adminName: str = ""
    latitude: float = 0.0
    fcode: str = ""
