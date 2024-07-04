from configparser import ConfigParser
import sys
from .dataclient.geonames_api import GoogleMapsClient
from .database.db_operation import DuckDBHandler

def format_coordinates(latitude, longitude):
    return f"{latitude},{longitude}"

def main():
    if len(sys.argv) < 2:
        print("Please provide a location name as an argument.")
        sys.exit(1)
    
    config = ConfigParser()
    config.read("../.config")
    API_KEY = config['GCP']['API_KEY']
    GEONAME_USERNAME = config['GEONAME']['username']


    address = sys.argv[1]  # The location name

    # Create an instance of the Google Maps client
    google_maps_client = GoogleMapsClient(API_KEY)

    # Fetch coordinates for the given address
    latitude, longitude = google_maps_client.get_coordinates(address)

    # latitude, longitude = 

    if latitude and longitude:
        location = format_coordinates(latitude, longitude)
        radius = sys.argv[2] if len(sys.argv) > 2 else 50000  # in meters

        # Fetch places and insert into DuckDB
        places = google_maps_client.get_all_places(location, radius)
        PlaceDetails = google_maps_client.get_places_details([place.place_id for place in places])

        # pass True to recreate the tables else False
        duckdb_handler = DuckDBHandler(recreate=sys.argv[3] if len(sys.argv) > 3 else False)
        
        if places:
            duckdb_handler.insert_places(places)
        if PlaceDetails:
            duckdb_handler.insert_place_details(PlaceDetails)
        else:
            print("No places found.")
    else:
        print("Could not retrieve coordinates.")

if __name__ == "__main__":
    main()