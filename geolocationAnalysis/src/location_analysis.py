from dataclasses import dataclass
import requests
import time
import duckdb
import pandas as pd
from configparser import ConfigParser
import sys
import logging


def format_coordinates(latitude, longitude):
    return f"{latitude},{longitude}"


class GeoMapClient:
    def __init__(self, username):
        self.username = username

    def get_geonames_data(self, country_code, max_rows=1000):
        base_url = "http://api.geonames.org/searchJSON"
        all_data = []
        start_row = 0

        while True:
            params = {
                "country": country_code,
                "maxRows": max_rows,
                "username": self.username,
                "startRow": start_row,
            }

            response = requests.get(base_url, params=params)
            data = response.json()

            if "geonames" in data:
                geonames = data["geonames"]
                all_data.extend(geonames)

                if len(geonames) < max_rows:
                    # We've reached the end of the data
                    break

                start_row += max_rows

                # Respect rate limits
                time.sleep(1)
            else:
                print(
                    "Error retrieving data:",
                    data.get("status", {}).get("message", "Unknown error"),
                )
                return None


class GoogleMapsClient:
    def __init__(self, api_key):
        self.api_key = api_key

    def get_coordinates_google(self, address):
        url = f"https://maps.googleapis.com/maps/api/geocode/json?address={address}&key={self.api_key}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if data["status"] == "OK":
                location = data["results"][0]["geometry"]["location"]
                return location["lat"], location["lng"]
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
                all_places.extend(places["results"])
                next_page_token = places.get("next_page_token")
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
        place_id = result["place_id"]
        name = result["name"]
        vicinity = result.get("vicinity", "N/A")
        latitude = result["geometry"]["location"]["lat"]
        longitude = result["geometry"]["location"]["lng"]
        return Place(place_id, name, vicinity, latitude, longitude)

    def get_places_details(self, place_ids):
        all_place_details = []

        for place_id in place_ids:
            details_url = f"https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&key={self.api_key}"
            details_response = requests.get(details_url)
            place_details = details_response.json()

            if place_details["status"] != "OK":
                # print(f"Error in response: {place_details['status']}")
                continue

            all_place_details.append(place_details["result"])

        return [self._convert_to_placedetail(result) for result in all_place_details]

    def _convert_to_placedetail(self, result):
        place_id = result["place_id"]
        name = result["name"]
        address = result["formatted_address"]
        phoneNumber = result.get("formatted_phone_number", "N/A")
        website = result.get("website", "N/A")
        return PlaceDetail(place_id, name, address, phoneNumber, website)


class DuckDBHandler:
    def __init__(self, db_path="../data/places.db", recreate: bool = False):
        self.con = duckdb.connect(db_path)
        self.recreate = recreate
        self._create_table(self.recreate)

    def _create_table(self, recreate):
        if recreate:
            self.con.execute(
                """
            DROP TABLE IF EXISTS places CASCADE;
            DROP TABLE IF EXISTS placeDetail;         
            """
            )

        self.con.execute(
            """
            CREATE TABLE IF NOT EXISTS places (
                place_id VARCHAR PRIMARY KEY,
                name VARCHAR,
                vicinity VARCHAR,
                latitude DOUBLE,
                longitude DOUBLE
            );
            
            CREATE TABLE IF NOT EXISTS placeDetail (
                        place_id VARCHAR PRIMARY KEY,
                        name VARCHAR,
                        address VARCHAR,
                        phoneNumber VARCHAR,
                        website VARCHAR,
                        foreign key (place_id) references places(place_id)      
            );
            """
        )

    def insert_places(self, places):
        data = [
            [
                place.place_id,
                place.name,
                place.vicinity,
                place.latitude,
                place.longitude,
            ]
            for place in places
        ]
        df = pd.DataFrame(
            data, columns=["place_id", "name", "vicinity", "latitude", "longitude"]
        )
        self.con.execute("BEGIN TRANSACTION")
        self.con.execute(
            "INSERT INTO places SELECT * FROM df where place_id not in (select place_id from places group by 1)"
        )
        self.con.execute("COMMIT")

    def insert_place_details(self, placedetail):
        data = [
            [
                detail.place_id,
                detail.name,
                detail.address,
                detail.phoneNumber,
                detail.website,
            ]
            for detail in placedetail
        ]
        df = pd.DataFrame(
            data, columns=["place_id", "name", "address", "phoneNumber", "website"]
        )
        self.con.execute("BEGIN TRANSACTION")
        self.con.execute(
            "INSERT INTO placeDetail SELECT * FROM df where place_id not in (select place_id from placeDetail group by 1)"
        )
        self.con.execute("COMMIT")

    def _insert_data(self, data, table_name):
        self.con.execute(f"INSERT INTO {table_name} VALUES (?)", data)


# %%
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Please provide a location name as an argument.")
        sys.exit(1)

    config = ConfigParser()
    config.read("../../.config")
    API_KEY = config["GCP"]["API_KEY"]
    GEONAME_USERNAME = config["GEONAME"]["username"]

    address = sys.argv[1]  # The location name

    # Create an instance of the Google Maps client
    google_maps_client = GoogleMapsClient(API_KEY)

    # Fetch coordinates for the given address
    # latitude, longitude = google_maps_client.get_coordinates(address)

    latitude, longitude = 0, 0

    if latitude and longitude:
        location = format_coordinates(latitude, longitude)
        radius = sys.argv[2] if len(sys.argv) > 2 else 50000  # in meters

        # Fetch places and insert into DuckDB
        places = google_maps_client.get_all_places(location, radius)
        PlaceDetails = google_maps_client.get_places_details(
            [place.place_id for place in places]
        )

        # pass True to recreate the tables else False
        duckdb_handler = DuckDBHandler(
            recreate=sys.argv[3] if len(sys.argv) > 3 else False
        )

        if places:
            duckdb_handler.insert_places(places)
        if PlaceDetails:
            duckdb_handler.insert_place_details(PlaceDetails)
        else:
            print("No places found.")
    else:
        print("Could not retrieve coordinates.")
