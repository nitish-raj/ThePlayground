import requests
import time
from ..models.locations import Place, PlaceDetail

class GoogleMapsClient:
    def __init__(self, api_key):
        self.api_key = api_key

    def get_coordinates_google(self, address):
        url = f"https://maps.googleapis.com/maps/api/geocode/json?address={address}&key={self.api_key}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if data['status'] == 'OK':
                location = data['results'][0]['geometry']['location']
                return location['lat'], location['lng']
            else:
                print(f"Error in response: {data['status']}")
                return None, None
        else:
            print(f"HTTP error: {response.status_code}")
            return None, None

    def get_all_places(self, location, radius):
        all_places = []
        url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={location}&radius={radius}&key={self.api_key}"
        
        while url:
            response = requests.get(url)
            if response.status_code == 200:
                places = response.json()
                all_places.extend(places['results'])
                next_page_token = places.get('next_page_token')
                if next_page_token:
                    time.sleep(2)  # Add a delay before making the next request
                    url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?pagetoken={next_page_token}&key={self.api_key}"
                else:
                    url = None
            else:
                print(f"HTTP error: {response.status_code}")
                break
        
        return [self._convert_to_place(result) for result in all_places]

    def _convert_to_place(self, result):
        place_id = result['place_id']
        name = result['name']
        vicinity = result.get('vicinity', 'N/A')
        latitude = result['geometry']['location']['lat']
        longitude = result['geometry']['location']['lng']
        return Place(place_id, name, vicinity, latitude, longitude)

    def get_places_details(self, place_ids):
        all_place_details = []

        for place_id in place_ids:
            details_url = f"https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&key={self.api_key}"
            details_response = requests.get(details_url)
            place_details = details_response.json()
            
            if place_details['status'] != 'OK':
                # print(f"Error in response: {place_details['status']}")
                continue
            
            all_place_details.append(place_details['result'])

        return [self._convert_to_placedetail(result) for result in all_place_details] 

    def _convert_to_placedetail(self, result):
        place_id = result['place_id']
        name = result['name']
        address = result['formatted_address']
        phoneNumber = result.get('formatted_phone_number', 'N/A')
        website = result.get('website', 'N/A')
        return PlaceDetail(place_id, name, address, phoneNumber, website)
