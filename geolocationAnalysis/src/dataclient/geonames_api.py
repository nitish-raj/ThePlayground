import requests
import time
from ..models.geoname import GeoName
from dataclasses import asdict
import pandas as pd

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
                all_data.extend(
                    [
                        GeoName(
                            adminCode=item["adminCode1"],
                            longitude=float(item["lng"]),
                            geonameId=int(item["geonameId"]),
                            toponymName=item["toponymName"],
                            countryId=int(item["countryId"]),
                            fcl=item["fcl"],
                            population=(
                                int(item["population"])
                                if item.get("population")
                                else None
                            ),
                            countryCode=item["countryCode"],
                            name=item["name"],
                            fclName=item["fclName"],
                            adminCodes=item["adminCodes1"],
                            countryName=item["countryName"],
                            fcodeName=item["fcodeName"],
                            adminName=item["adminName1"],
                            latitude=float(item["lat"]),
                            fcode=item["fcode"],
                        )
                        for item in geonames
                    ]
                )

                if len(geonames) < max_rows:
                    break

                start_row += max_rows
                time.sleep(1)
            else:
                print(
                    "Error retrieving data:",
                    data.get("status", {}).get("message", "Unknown error"),
                )
                return []

        df_geoname = pd.DataFrame([asdict(gn) for gn in all_data])

        return df_geoname
