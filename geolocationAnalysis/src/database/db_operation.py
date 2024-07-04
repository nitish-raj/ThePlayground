import duckdb
import pandas as pd


class DuckDBHandler:
    def __init__(self, db_path='../data/places.db', recreate: bool = False):
        self.con = duckdb.connect(db_path)
        self.recreate = recreate
        self._create_table(self.recreate)

    def _create_table(self, recreate):
        if recreate:
            self.con.execute('''
            DROP TABLE IF EXISTS places CASCADE;
            DROP TABLE IF EXISTS placeDetail;         
            ''')
            
        self.con.execute('''
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
            ''')

    def insert_places(self, places):
        data = [[place.place_id, place.name, place.vicinity, place.latitude, place.longitude] for place in places]
        df = pd.DataFrame(data, columns=['place_id', 'name', 'vicinity', 'latitude', 'longitude'])
        self.con.execute('BEGIN TRANSACTION')
        self.con.execute('INSERT INTO places SELECT * FROM df where place_id not in (select place_id from places group by 1)')
        self.con.execute('COMMIT')
    
    def insert_place_details(self, placedetail):
        data = [[detail.place_id, detail.name, detail.address, detail.phoneNumber, detail.website] for detail in placedetail]
        df = pd.DataFrame(data, columns= ['place_id','name','address','phoneNumber', 'website'])
        self.con.execute('BEGIN TRANSACTION')
        self.con.execute('INSERT INTO placeDetail SELECT * FROM df where place_id not in (select place_id from placeDetail group by 1)')
        self.con.execute('COMMIT')

    def _insert_data(self, data, table_name):
        self.con.execute(f'INSERT INTO {table_name} VALUES (?)', data)
