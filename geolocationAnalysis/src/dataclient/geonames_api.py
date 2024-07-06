import requests
import time

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
                "startRow": start_row
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
                print("Error retrieving data:", data.get("status", {}).get("message", "Unknown error"))
                return None