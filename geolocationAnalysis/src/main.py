#%%
from configparser import ConfigParser
import sys
import os
from dataclasses import asdict
import pandas as pd

from .dataclient.geonames_api import GeoMapClient
from .dataclient.googlemaps_api import GoogleMapsClient
from .database.duckdb_operation import DuckDBHandler


def format_coordinates(latitude: float, longitude: float) -> str:
    return f"{latitude},{longitude}"

def main():
    # Load configuration from file
    config = ConfigParser()
    config_file = os.path.join(os.path.dirname(__file__), "..", ".config")
    config.read(config_file)

    # Get API keys and credentials from environment variables or config file
    api_key = os.environ.get("GOOGLE_MAPS_API_KEY") or config.get(
        "GoogleMaps", "API_key", fallback=None
    )
    geoname_username = os.environ.get("GEONAME_USERNAME") or config.get(
        "GEONAME", "username", fallback=None
    )

    gmaps_base_url = os.environ.get("GOOGLE_MAPS_BASE_URL") or config.get(
                        'GoogleMaps', 'base_url', fallback=None
                        )

    gnames_base_url = os.environ.get("GOEONAME_BASE_URL") or config.get(
                        'GEONAME', 'base_url', fallback=None
                        )

    # Check if API keys are provided
    if not api_key:
        print("Error: Google Maps API key not found in environment or config file.")
        sys.exit(1)

    if not geoname_username:
        print("Error: GeoNames username not found in environment or config file.")
        sys.exit(1)

    # Accept address as input from the user
    country_code = input("Enter the country code: ")

    # Not required with Geonames API
    # address = input("Enter the address: ")
 
    while True:
        try:
            radius = int(input("Enter the radius in meters for Google Maps [default:50000]: "))
            break
        except ValueError:
            print("Invalid input. Please enter an integer.")

    while True:
        try:
            max_rows = int(input("Enter the maximum number of rows to fetch from GeoNames [default:1000]: "))
            break
        except ValueError:
            print("Invalid input. Please enter an integer.")


    # Create clients and database handler
    google_maps_client = GoogleMapsClient(api_key,gmaps_base_url)
    geoname_client = GeoMapClient(geoname_username, gnames_base_url)
    duckdb_handler = DuckDBHandler()

    # Fetch and insert GeoName data
    geoname_df = geoname_client.get_geonames_data(country_code, max_rows)
    duckdb_handler.insert_data("geonames", geoname_df)

    # Process GeoNames data
    for _, row in geoname_df.iterrows():
        location = format_coordinates(row["latitude"], row["longitude"])

        # Fetch places and insert into DuckDB
        places = google_maps_client.get_all_places(location, radius)
        if places:
            places_df = pd.DataFrame([asdict(gn) for gn in places])
            duckdb_handler.insert_data("places", places_df)
            PlaceDetails = google_maps_client.get_places_details(
                [place.place_id for place in places]
            )
            if PlaceDetails:
                place_details_df = pd.DataFrame([asdict(gn) for gn in PlaceDetails])
                duckdb_handler.insert_data("place_details", place_details_df)

    print("Data processing completed successfully.")

if __name__ == "__main__":
    main()