import requests
import time
from ..models.locations import Place, PlaceDetail, PlaceV2
from typing import List, Tuple
import logging


# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class GoogleMapsClient:
    """
    A client for interacting with the Google Maps API.

    This class provides methods for geocoding addresses, fetching nearby places,
    and retrieving details of specific places using the Google Maps API.

    Attributes:
        api_key (str): The API key required for making requests to the Google Maps API.
    """

    def __init__(self, api_key, base_url, place_types:str|List = [], max_results:int = 20 ):
        self.api_key = api_key
        self.base_url = base_url
        self.place_types = place_types
        self.max_results = max_results

    def get_coordinates_google(self, address: str) -> Tuple[float, float]:
        """
        Geocode an address and return its latitude and longitude coordinates.

        Args:
            address (str): The address to be geocoded.

        Returns:
            Tuple[float, float]: A tuple containing the latitude and longitude coordinates of the address.

        Raises:
            ValueError: If the geocoding request fails or returns an error status.
            requests.exceptions.RequestException: If there's an error with the HTTP request.
        """

        url = f"{self.base_url}/geocode/json?address={address}&key={self.api_key}"

        response = requests.get(url)
        response.raise_for_status()

        data = response.json()
        if data["status"] != "OK":
            raise ValueError(f"Error in response: {data['status']}")

        location = data["results"][0]["geometry"]["location"]
        return location["lat"], location["lng"]

    def get_all_places(self, location: str, radius: int) -> List[Place]:
        """
        Fetch all places within a given radius of a location.

        Args:
            location (str): The location to search around, in the format "latitude,longitude".
            radius (int): The radius in meters to search within.

        Returns:
            List[Place]: A list of Place objects representing the nearby places.
        """
        all_places = []
        url = f"{self.base_url}/place/nearbysearch/json?location={location}&radius={radius}&key={self.api_key}"
         
        while url:
            try:
                response = requests.get(url)
                response.raise_for_status()
            except requests.exceptions.RequestException as e:
                logging.error(f"Error in nearby search request: {e}")
                break

            places = response.json()
            all_places.extend(places["results"])
            next_page_token = places.get("next_page_token")
            if next_page_token:
                time.sleep(2)  # Add a delay before making the next request
                url = f"{self.base_url}/place/nearbysearch/json?pagetoken={next_page_token}&key={self.api_key}"
            else:
                url = None 

        return [self._convert_to_place(result) for result in all_places]

    def get_all_places_v2(self, latitude: float|int, longitude: float|int, radius: int) -> List[Place]:
        """
        Fetch all places within a given radius of a location using the Place Search API.

        Args:
            location (str): The location to search around, in the format "latitude,longitude".
            radius (int): The radius in meters to search within.

        Returns:
            List[Place]: A list of Place objects representing the nearby places.
        """
        all_places = []
        for place_type in self.place_types:
            for preference in ["DISTANCE", "RATING"]:

                # Prepare the request payload
                payload = {
                "includedTypes": [place_type],
                "locationRestriction": {
                    "circle": {
                        "center": {
                            "latitude": latitude,
                            "longitude": longitude
                        },
                        "radius": radius
                    }
                },
                "maxResultCount": self.max_results,
                "rankPreference": preference
                }

                # Prepare the headers
                headers = {
                "Content-Type": "application/json",
                "X-Goog-Api-Key": self.api_key,
                "X-Goog-FieldMask": (
                        "places.businessStatus,places.displayName,places.formattedAddress,"
                        "places.googleMapsUri,places.id,places.location,places.plusCode,"
                        "places.primaryType,places.types,places.internationalPhoneNumber,"
                        "places.nationalPhoneNumber,places.priceLevel,places.rating,"
                        "places.userRatingCount,places.websiteUri,places.delivery,"
                        "places.parkingOptions,places.paymentOptions,places.outdoorSeating,"
                        "places.reservable"
                        )
                }

                response = requests.post(f'{self.base_url}:searchNearby', json=payload, headers=headers)

                places = response.json()

                all_places.extend(places['places'])

        return [self._convert_to_place(result) for result in all_places]

    def get_places_details(self, place_ids: List[str]) -> List[PlaceDetail]:
        """
        Fetch details for a list of place IDs.

        Args:
            place_ids (List[str]): A list of place IDs to fetch details for.

        Returns:
            List[PlaceDetail]: A list of PlaceDetail objects representing the place details.
        """
        all_place_details = []

        for place_id in place_ids:
            details_url = f"{self.base_url}/place/details/json?place_id={place_id}&key={self.api_key}"
            details_response = requests.get(details_url)
            place_details = details_response.json()

            if place_details["status"] != "OK":
                # print(f"Error in response: {place_details['status']}")
                continue

            all_place_details.append(place_details["result"])

        return [self._convert_to_placedetail(result) for result in all_place_details]

    @staticmethod
    def _convert_to_place(result: dict) -> Place:
        """
        Convert a Google Maps API result to a Place object.

        Args:
            result (dict): The result dictionary from the Google Maps API.

        Returns:
            Place: A Place object representing the place.
        """
        place_id = result["place_id"]
        name = result["name"]
        vicinity = result.get("vicinity", "N/A")
        latitude = result["geometry"]["location"]["lat"]
        longitude = result["geometry"]["location"]["lng"]
        return Place(place_id, name, vicinity, latitude, longitude)
    
    @staticmethod
    def _convert_to_place_v2(result: dict) -> PlaceV2:
        """
        Convert a Google Maps API result to a PlaceV2 object.

        Args:
            result (dict): The result dictionary from the Google Maps API.

        Returns:
            PlaceV2: A PlaceV2 object representing the place.
        """
        place_id = result["id"]
        types = result["types"]
        phoneNumber = result.get("international_phone_number", "N/A")
        internationalPhoneNumber = result.get("international_phone_number", "N/A")
        formattedAddress = result.get("formatted_address", "N/A")
        globalCode = result.get("plus_code", {}).get("global_code", "N/A")
        compoundCode = result.get("plus_code", {}).get("compound_code", "N/A")
        latitude = result.get("location",{}).get("latitude", 0.0)
        longitude = result.get("location", {}).get("longitude", 0.0)
        rating = result.get("rating", 0.0)
        googleMapsUri = result.get("google_maps_uri", "N/A")
        websiteUri = result.get("website_uri", "N/A")
        businessStatus = result.get("business_status", "N/A")
        userRatingCount = result.get("user_ratings_total", 0)
        displayName = result.get("name", "N/A")
        delivery = result.get("delivery", False)
        primaryType = result.get("primary_type", "N/A")
        acceptsCreditCards = result.get("payment_options", {}).get("accepts_credit_cards", False)
        acceptsDebitCards = result.get("payment_options", {}).get("accepts_debit_cards", False)
        acceptsCashOnly = result.get("payment_options", {}).get("accepts_cash_only", False)
        acceptsNfc = result.get("payment_options", {}).get("accepts_nfc", False)
        return PlaceV2(place_id, types, phoneNumber, internationalPhoneNumber, formattedAddress, 
                       globalCode, compoundCode, latitude, longitude, rating, googleMapsUri, websiteUri, 
                       businessStatus, userRatingCount, displayName, delivery, primaryType, acceptsCreditCards, 
                       acceptsDebitCards, acceptsCashOnly, acceptsNfc)
    
    @staticmethod
    def _convert_to_placedetail(result: dict) -> PlaceDetail:
        """
        Convert a Google Maps API result to a PlaceDetail object.

        Args:
            result (dict): The result dictionary from the Google Maps API.

        Returns:
            PlaceDetail: A PlaceDetail object representing the place details.
        """
        place_id = result["place_id"]
        name = result["name"]
        address = result["formatted_address"]
        phoneNumber = result.get("formatted_phone_number", "N/A")
        website = result.get("website", "N/A")
        return PlaceDetail(place_id, name, address, phoneNumber, website)
