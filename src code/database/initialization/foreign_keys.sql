ALTER TABLE
    feature_code
ADD
    FOREIGN KEY (feature_class) REFERENCES feature_class(id);

ALTER TABLE
    location
ADD
    FOREIGN KEY (feature_code) REFERENCES feature_code(id);

ALTER TABLE
    location
ADD
    FOREIGN KEY (country_code) REFERENCES country(id);

ALTER TABLE
    review
ADD
    FOREIGN KEY (user_id) REFERENCES user(id);

ALTER TABLE
    review
ADD
    FOREIGN KEY (place_id) REFERENCES location(id);

ALTER TABLE
    review
ADD
    FOREIGN KEY (trip_type) REFERENCES trip_type(id);

ALTER TABLE
    review
ADD
    FOREIGN KEY (trip_season) REFERENCES trip_season(id);