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
    foreign key (place_id) references places(place_id);  