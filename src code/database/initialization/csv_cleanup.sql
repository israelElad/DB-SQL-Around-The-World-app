SELECT distinct country_code FROM location where country_code not in(SELECT id from country);
SET SQL_SAFE_UPDATES = 0;
DELETE FROM location where country_code like "";
DELETE FROM location where country_code like "XK";
DELETE FROM location where country_code like "YU";
DELETE FROM location where country_code like "CS";
DELETE FROM location where country_code like "AN";

SELECT distinct feature_code FROM location where feature_code not in(SELECT id from feature_code);
DELETE FROM location where feature_code like "";

SELECT *
FROM location
INTO OUTFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/geonames_updated_final.csv'
FIELDS TERMINATED BY ','
LINES TERMINATED BY '\n';