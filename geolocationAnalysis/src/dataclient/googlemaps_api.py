import requests
import time
from ..models.locations import Place, PlaceDetail
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

    def __init__(self, api_key, base_url):
        self.api_key = api_key
        self.base_url = base_url

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

        payload = {
            "location": location,
            
        }

        headers = {
            "Content-Type": "application/json",
        }

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
            details_url = f"{self.base_url}/place/details/{place_id}?key={self.api_key}"
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
