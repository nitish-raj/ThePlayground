#%%
from dataclasses import dataclass
import requests
import time
import duckdb
import pandas as pd
from configparser import ConfigParser

@dataclass
class Place:
    place_id: str
    name: str
    address: str
    latitude: float
    longitude: float
    website: str

def format_coordinates(latitude, longitude):
    return f"{latitude},{longitude}"

class GoogleMapsClient:
    def __init__(self, api_key):
        self.api_key = api_key

    def get_coordinates(self, address):
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
                all_places.extend(places)
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
        place_id = result['results']['place_id']
        name = result['results']['name']
        address = result['results'].get('vicinity', 'N/A')
        latitude = result['results']['geometry']['location']['lat']
        longitude = result['results']['geometry']['location']['lng']
        website = result['results'].get('website', 'N/A')
        return Place(place_id, name, address, latitude, longitude, website)

class DuckDBHandler:
    def __init__(self, db_path='places.db'):
        self.con = duckdb.connect(db_path)
        self._create_table()

    def _create_table(self):
        self.con.execute('''
        CREATE TABLE IF NOT EXISTS places (
            place_id VARCHAR,
            name VARCHAR,
            address VARCHAR,
            latitude DOUBLE,
            longitude DOUBLE,
            website varchar
        )
        ''')

    def insert_places(self, places):
        data = [[place.place_id, place.name, place.address, place.latitude, place.longitude, place.website] for place in places]
        df = pd.DataFrame(data, columns=['place_id', 'name', 'address', 'latitude', 'longitude','website'])
        self.con.execute('BEGIN TRANSACTION')
        self.con.execute('INSERT INTO places SELECT * FROM df')
        self.con.execute('COMMIT')

#%%
if __name__ == "__main__":
    config = ConfigParser()
    config.read("../.config")
    API_KEY = config['GCP']['API_KEY']
    address = 'Luxembourg'  # The location name

    # Create an instance of the Google Maps client
    google_maps_client = GoogleMapsClient(API_KEY)

    # Fetch coordinates for the given address
    latitude, longitude = google_maps_client.get_coordinates(address)
    if latitude and longitude:
        location = format_coordinates(latitude, longitude)
        radius = 15000  # in meters

        # Fetch places and insert into DuckDB
        places = google_maps_client.get_all_places(location, radius)
        if places:
            duckdb_handler = DuckDBHandler()
            duckdb_handler.insert_places(places)
        else:
            print("No places found.")
    else:
        print("Could not retrieve coordinates.")
