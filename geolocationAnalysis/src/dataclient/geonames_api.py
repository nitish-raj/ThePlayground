import requests
import time
from ..models.geoname import GeoName
from dataclasses import asdict
import pandas as pd
from configparser import ConfigParser

# Configuration
config = ConfigParser()
config.read(".config")


class GeoMapClient:
    """
    A client for interacting with the GeoNames API.

    Attributes:
        username (str): The username required for making requests to the GeoNames API.
    """

    def __init__(self, username):
        self.username = username
        self.base_url = f"{config.get('GEONAME', 'base_url')}"

    def get_geonames_data(self, country_code, max_rows = None):
        """
        Retrieve geographical location data from the GeoNames API for a given country code.

        Args:
            country_code (str): The code of the country to retrieve location data for.
            max_rows (int, optional): The maximum number of rows to retrieve. Defaults to 1000.

        Returns:
            List[GeoName]: A list of GeoName objects representing the retrieved locations.

        Raises:
            ValueError: If there is an error in the HTTP request or the API response.
        """
        all_data = []
        start_row = 0
        
        while True:
            params = {
                "country": country_code,
                "maxRows": int(max_rows) if max_rows and max_rows != '' else 1000,
                "username": self.username,
                "startRow": start_row,
            }

            try:
                response = requests.get(self.base_url, params=params)
                response.raise_for_status()
                data = response.json()
            except requests.exceptions.RequestException as e:
                raise ValueError(f"Error in HTTP request: {e}")

            if "geonames" in data:
                geonames = data["geonames"]
                all_data.extend([self._convert_to_geoname(item) for item in geonames])

                if max_rows is not None and len(geonames) < max_rows:
                    break

                start_row += max_rows
                time.sleep(1)

            else:
                error_message = data.get("status", {}).get("message", "Unknown error")
                raise ValueError(f"Error retrieving data: {error_message}")

        df_geoname = pd.DataFrame([asdict(gn) for gn in all_data])

        return df_geoname

    @staticmethod
    def _convert_to_geoname(item):
        """
        Convert a dictionary representing a geographical location to a GeoName object.

        Args:
            item (dict): A dictionary containing the location data.

        Returns:
            GeoName: A GeoName object representing the location.
        """

        return GeoName(
            adminCode=item["adminCode1"] if item.get("adminCode1") else None,
            longitude=float(item["lng"]),
            geonameId=int(item["geonameId"]),
            toponymName=item["toponymName"],
            countryId=int(item["countryId"]) if item.get("countryId") else None,
            fcl=item["fcl"],
            population=int(item["population"]) if item.get("population") else None,
            countryCode=item["countryCode"] if item.get("countryCode") else None,
            name=item["name"],
            fclName=item["fclName"] if item.get("fclName") else None,
            adminCodes=item["adminCodes1"] if item.get("adminCodes1") else None,
            countryName=item["countryName"] if item.get("countryName") else None,
            fcodeName=item["fcodeName"],
            adminName=item["adminName1"],
            latitude=float(item["lat"]),
            fcode=item["fcode"],
        )
