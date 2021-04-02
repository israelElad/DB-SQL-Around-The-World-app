-- expermination file, ignore it


UPDATE trip_type 
SET 
    name = CONCAT(UPPER(LEFT(name, 1)),
            LOWER(SUBSTRING(name, 2, LENGTH(name))));

UPDATE trip_season 
SET 
    name = CONCAT(UPPER(LEFT(name, 1)),
            LOWER(SUBSTRING(name, 2, LENGTH(name))));

ALTER TABLE location add column lat DECIMAL( 10, 8 ) NOT NULL;
ALTER TABLE location add column lng DECIMAL( 11, 8 ) NOT NULL;
update location set lat=ST_X(coordinates); -- invert in elad anton
update location set lng=ST_Y(coordinates);
ALTER TABLE location ADD INDEX(lat);
ALTER TABLE location ADD INDEX(lng);
-------------

SET @R=100; 
set @earth_radius=6378;
set @lat = 31.4117;
set @lng = 35.0818;
set @km_per_lat_degree = @earth_radius * PI() / 180;
set @lat_delta = @R /@km_per_lat_degree;
set @lng_delta = @lat_delta / COS(@lat * PI() / 180);
SET @lat_min = @lat - @lat_delta;
SET @lat_max = @lat + @lat_delta;
SET @lng_min = @lng - @lng_delta;
SET @lng_max = @lng + @lng_delta;





SELECT 
    (SELECT 
            name
        FROM
            trip_season tseason
        WHERE
            id = trip_season) trip_season,
    COUNT(*) num_reviews
FROM
    review
WHERE
    place_id = 8542111
GROUP BY trip_season;
SELECT 
    (SELECT 
            name
        FROM
            trip_type ttype
        WHERE
            id = trip_type) trip_type,
    COUNT(*) num_reviews
FROM
    review
WHERE
    place_id = 8542111
GROUP BY trip_type;


SELECT 
	l.id,
    l.name,
    lat latitude,
    lng longitude,
    (SELECT 
            fclass.name
        FROM
            feature_code fcode
                JOIN
            feature_class fclass ON fcode.feature_class = fclass.id
        WHERE
            fcode.id = l.feature_code) category,
    (SELECT 
            fcode.name
        FROM
            feature_code fcode
        WHERE
            fcode.id = l.feature_code) subcategory,
    (SELECT 
            c.name
        FROM
            country c
        WHERE
            c.id = l.country_code) country,
    temp.average_rating average_rating
FROM
    location l
        JOIN
    (SELECT 
        place_id, AVG(rating) average_rating
    FROM
        review
    GROUP BY place_id
    ORDER BY average_rating DESC
    LIMIT 20) temp ON l.id = temp.place_id
;

SELECT 
    trip_season,
    trip_type,
    FLOOR(YEAR(CURRENT_TIMESTAMP) - AVG(year_of_birth)) average_age
FROM
    (SELECT 
        YEAR(date_of_birth) year_of_birth,
            ttype.name trip_type,
            tseason.name trip_season
    FROM
        trip_type ttype
    JOIN review r ON ttype.id = r.trip_type
    JOIN trip_season tseason ON tseason.id = r.trip_season
    JOIN user u ON r.user_id = u.id
    GROUP BY u.id , ttype.id , tseason.id) temp
GROUP BY trip_type , trip_season
ORDER BY trip_season , trip_type;


SELECT 
    (SELECT 
            name
        FROM
            trip_type
        WHERE
            id = ttype) trip_type,
    FLOOR(YEAR(CURRENT_TIMESTAMP) - AVG(year_of_birth)) average_age
FROM
    (SELECT DISTINCT
        u.id, YEAR(date_of_birth) year_of_birth, r.trip_type ttype
    FROM
        trip_type ttype
    JOIN review r ON ttype.id = r.trip_type
    JOIN user u ON r.user_id = u.id) temp
GROUP BY ttype
ORDER BY average_age;




 SELECT DISTINCT
    l.name,
    lat latitude,
    lng longitude,
    (SELECT 
            fclass.name
        FROM
            feature_code fcode
                JOIN
            feature_class fclass ON fcode.feature_class = fclass.id
        WHERE
            fcode.id = l.feature_code) category,
    (SELECT 
            fcode.name
        FROM
            feature_code fcode
        WHERE
            fcode.id = l.feature_code) subcategory,
    (SELECT 
            c.name
        FROM
            country c
        WHERE
            c.id = l.country_code) country
             ,
     (SELECT 
             AVG(rating)
         FROM
             review r
         WHERE
             r.place_id = l.id
             AND r.trip_season = (select id from trip_season where name = 'spring')
	 		AND r.trip_type = (select id from trip_type where name = 'nightlife')
             ) avg_rating
FROM
    location l
        JOIN
    review r ON l.id = r.place_id
WHERE
    lat BETWEEN @lat_min AND @lat_max
        AND lng BETWEEN @lng_min AND @lng_max
        AND (((ACOS(SIN(@lat * PI() / 180) * SIN(lat * PI() / 180) + COS(@lat * PI() / 180) * COS(lat * PI() / 180) * COS((@lng - lng) * PI() / 180)) * 180 / PI()) * 60 * 1.1515) * 1.609344) < @R
      AND r.trip_season = (select id from trip_season where name = 'spring')
      AND r.trip_type = (select id from trip_type where name = 'nightlife')
      order by id
		;




SET GLOBAL innodb_buffer_pool_size=268435456;
ALTER TABLE location MODIFY COLUMN coordinates POINT;
update location set coordinates=ST_GeomFromText(ST_AsText(Point(lat, lng)), 4326);
ALTER TABLE location MODIFY COLUMN coordinates POINT SRID 4326 not null;
ALTER TABLE location ADD INDEX(coordinates);

SET @R=230; -- km
set @earth_radius=6378;
set @lat = 50.000000;
set @lng = -72.935242; -- new york coordinates
set @km_per_lat_degree = @earth_radius * PI() / 180;
set @lat_delta = @R /@km_per_lat_degree;
set @lng_delta = @lat_delta / COS(@lat * PI() / 180);
SET @lat_min = @lat - @lat_delta;
SET @lat_max = @lat + @lat_delta;
SET @lng_min = @lng - @lng_delta;
SET @lng_max = @lng + @lng_delta;

SELECT 
     *,
     (((ACOS(SIN(@lat * PI() / 180) * SIN(lat * PI() / 180) + COS(@lat * PI() / 180) * COS(lat * PI() / 180) * COS((@lng - lng) * PI() / 180)) * 180 / PI()) * 60 * 1.1515) * 1.609344) AS distance
FROM
    location l
WHERE feature_code = 'PPL' and
	lat between @lat_min and @lat_max and lng between @lng_min and @lng_max 
	and (((ACOS(SIN(@lat * PI() / 180) * SIN(lat * PI() / 180) + COS(@lat * PI() / 180) * COS(lat * PI() / 180) * COS((@lng - lng) * PI() / 180)) * 180 / PI()) * 60 * 1.1515) * 1.609344) < @R
;    
    
SET @g1 = ST_SRID(POINT(34.65365, 69.04978), 4326);
SET @R=1.4;
SET @lat_min = ST_Latitude(@g1) - (0.009*R); -- 34.64105
SET @lat_max = ST_Latitude(@g1) + (0.009*R); -- 34.66625
SET @lng_min = ST_Longitude(@g1) - (0.009*R); -- 69.03718
SET @lng_max = ST_Longitude(@g1) + (0.009*R); -- 69.06238
-- SET @rectangle = POLYGON((@lat_min @lng_min, @lat_min @lng_max, @lat_max @lng_max, @lat_max @lng_min));
SET @rectangle = 'POLYGON((34.64105 69.03718, 34.64105 69.06238, 34.66625 69.06238, 34.66625 69.03718, 34.64105 69.03718))';
SET @bounding_box = ST_GeomFromText(@rectangle, 4326);
set @a = (select coordinates from location where id='1349943' limit 0, 1);
select @a;
select st_within(coordinates, @bounding_box), coordinates, @bounding_box from location WHERE st_within(coordinates, @bounding_box) and id='1349943'; 

set @coordinates = ST_GeomFromText(ST_AsText(Point(34.65365, 69.04978)), 4326);
select @coordinates;
SELECT st_contains(@bounding_box, @coordinates), @bounding_box;

update location set coordinates=ST_SRID(coordinates, 4326);
update location set coordinates=ST_GeomFromText(ST_AsText(coordinates), 4326);
ALTER TABLE location MODIFY COLUMN coordinates POINT SRID 4326 not null;
ALTER TABLE location ADD INDEX(coordinates);
alter table location drop index coordinates;
ALTER TABLE location add column lat DECIMAL( 10, 8 ) NOT NULL;
ALTER TABLE location add column lng DECIMAL( 11, 8 ) NOT NULL;
ALTER TABLE location ADD INDEX(lat);
ALTER TABLE location ADD INDEX(lng);
update location set lat=ST_X(coordinates); -- invert in elad anton
update location set lng=ST_Y(coordinates);

SET @lat = 34.65365, @lng = 69.04978;

SELECT (((ACOS(SIN(@lat * PI() / 180) * SIN(lat * PI() / 180) 
    + COS(@lat * PI() / 180) * COS(lat * PI() / 180) 
    * COS((@lng - lng) * PI() / 180)) * 180 / PI()) 
    * 60 * 1.1515)* 1.609344) AS distance FROM location where lat between @lat-0.3 and @lat+0.3 and lng between @lng-0.3 and @lng+0.3 ORDER BY distance DESC;


-----------------------------

-- file for temporary queries while working on them from workbench
SET SQL_SAFE_UPDATES = 0;
ALTER TABLE location ADD SPATIAL INDEX(coordinates);
ALTER TABLE location add column lat DECIMAL( 10, 8 ) NOT NULL;
ALTER TABLE location add column lng DECIMAL( 11, 8 ) NOT NULL;
ALTER TABLE location ADD INDEX(lat);
ALTER TABLE location ADD INDEX(lng);
update location set lat=ST_Y(coordinates);
update location set lng=ST_X(coordinates);
select * from location where coordinates = POINT (34.65365, 69.04978);

select * from location where id='1349943';

SELECT *,
    id, (
      6371 * acos (
      cos ( radians(@lat) )
      * cos( radians( lat ) )
      * cos( radians( lng ) - radians(@lng) )
      + sin ( radians(@lat) )
      * sin( radians( lat ) )
    )
) AS distance
FROM location
HAVING distance < 30
ORDER BY distance
LIMIT 0 , 20;

SET @lat = 34.65365, @lng = 69.04978;
ALTER TABLE location ADD INDEX(lat);
ALTER TABLE location ADD INDEX(lng);
SELECT *,(((ACOS(SIN(@lat * PI() / 180) * SIN(lat * PI() / 180) 
    + COS(@lat * PI() / 180) * COS(lat * PI() / 180) 
    * COS((@lng - lng) * PI() / 180)) * 180 / PI()) 
    * 60 * 1.1515)* 1.609344) AS distance FROM location HAVING distance<=30 ORDER BY distance ASC LIMIT 0 , 20;

SELECT ST_SRID( coordinates, 4326) from location;

SET GLOBAL innodb_buffer_pool_size=268435456;
UPDATE location 
SET 
    coordinates = POINT(ST_X(coordinates),
        ST_Y(coordinates));


SELECT 
    l.name,
    lat latitude,
    lng longitude,
    (SELECT 
            fclass.name
        FROM
            feature_code fcode
                JOIN
            feature_class fclass ON fcode.feature_class = fclass.id
        WHERE
            fcode.id = l.feature_code) category,
    (SELECT 
            fcode.name
        FROM
            feature_code fcode
        WHERE
            fcode.id = l.feature_code) subcategory,
    c.name AS country,
    (SELECT 
            AVG(rating)
        FROM
            review r
        WHERE
            r.place_id = l.id) avg_rating
FROM
    location l
        JOIN
    country c ON l.country_code = c.id
WHERE
    c.name = 'israel'
        AND l.feature_code = (SELECT 
            id
        FROM
            feature_code
        WHERE
            name = 'populated place')
;
SELECT 
    l.name,
    ST_X(coordinates) latitude,
    ST_Y(coordinates) longitude,
    (SELECT 
            fclass.name
        FROM
            feature_code fcode
                JOIN
            feature_class fclass ON fcode.feature_class = fclass.id
        WHERE
            fcode.id = l.feature_code) category,
    (SELECT 
            fcode.name
        FROM
            feature_code fcode
        WHERE
            fcode.id = l.feature_code) subcategory,
    c.name as country,
     (SELECT 
            AVG(rating)
        FROM
            review r
        WHERE
            r.place_id = l.id) avg_rating
FROM
    location l
        JOIN
    country c ON l.country_code = c.id
WHERE
    c.name like 'isra__'
        AND feature_code = 'PPL';

SELECT 
    l.name,
    ST_X(coordinates) latitude,
    ST_Y(coordinates) longitude,
    (SELECT 
            fclass.name
        FROM
            feature_code fcode
                JOIN
            feature_class fclass ON fcode.feature_class = fclass.id
        WHERE
            fcode.id = l.feature_code) category,
    (SELECT 
            fcode.name
        FROM
            feature_code fcode
        WHERE
            fcode.id = l.feature_code) subcategory,
    c.name AS country
FROM
    location l
        JOIN
    country c ON l.country_code = c.id
WHERE
    c.name = 'armenia'
        AND feature_code IN (SELECT 
            fcode.id
        FROM
            feature_code fcode
                JOIN
            feature_class fclass ON fcode.feature_class = fclass.id
        WHERE
            fclass.name = 'city, village');
        

-- SELECT * FROM location, country, feature_class where country.name = 'armenia' 
-- and feature_class.name='undersea';