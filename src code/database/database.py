import mysql.connector
# from database.utils import execute_sql_file
from database.config import *
# import random
# import csv


class Database:
    """A class for communication with db, execution of statements and queries
    """
    def initialize(self):
        self.mydb = mysql.connector.connect(
            option_files='my.conf', 
            autocommit=True
        )
        self.cursor = self.mydb.cursor()

        # self.cursor.execute(f"""CREATE DATABASE {db_name}""")
        self.cursor.execute(f"USE {db_name}")
        # execute_sql_file(self.cursor, "models/initialization/tables_creation.sql")
        # execute_sql_file(self.cursor, "models/initialization/foreign_keys.sql")
        # self.populate_tables()
        # self.populate_users()
        # self.generate_reviews()
        self.cursor.execute(f"USE {db_name}")

    def close(self):
        self.cursor.close()
        self.mydb.close()

    #query for the 2 tabs in location screen - whether by country or by lat, lng
    def find_locations(self, country_name, radius, lat, lng, fclass, fcode, trip_type, trip_season, limit_size, last_id=0):
        """
        Query for the 2 tabs in location screen - whether by country or by radius, lat, lng.
        Either country_name should be the empty string, or radius, lat and lng should be 0.
        fclass and fcode are feature class and feature code, respectively.
        limit_size - number of rows fetched. Combined with last_id it's the mechanism implemented for pagination.
        """
        query = ""
        args = []
        if country_name == "":
            self.execute_single_query(
                "SET @R= %s;", args=[radius], is_expecting_result=False)
            self.execute_single_query(
                "SET @lat = %s;", args=[lat], is_expecting_result=False)
            self.execute_single_query(
                "SET @lng = %s;", args=[lng], is_expecting_result=False)
            # using the bounding box technique to quickly filter out entries 
            self.execute_multiple_queries(""" 
                SET @earth_radius = 6378;
                SET @km_per_lat_degree = @earth_radius * PI() / 180;
                SET @lat_delta = @R /@km_per_lat_degree;
                SET @lng_delta = @lat_delta / COS(@lat * PI() / 180);
                SET @lat_min = @lat - @lat_delta;
                SET @lat_max = @lat + @lat_delta;
                SET @lng_min = @lng - @lng_delta;
                SET @lng_max = @lng + @lng_delta;
                """)
        # the values that if passed as trip_type/trip_season, indicate that we should ignore it
        review_ignored_values = ["", "All", "Trip type", "Trip season"]
        review_conditions = ""
        review_args = []
        if trip_season not in review_ignored_values:
            review_conditions += """
                    AND r.trip_season = (select id from trip_season where name = %s)
                    """
            review_args.extend([trip_season])
        if trip_type not in review_ignored_values:
            review_conditions += """
                    AND r.trip_type = (select id from trip_type where name = %s)
                    """
            review_args.extend([trip_type])
        query += f"""
                SELECT DISTINCT
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
                    (SELECT 
                            AVG(rating)
                        FROM
                            review r
                        WHERE
                            r.place_id = l.id
                            {review_conditions}
                            ) average_rating
                """
        args.extend(review_args)
        if country_name != "":
            query += """
                    FROM
                        location l
                            JOIN
                        country c ON l.country_code = c.id
                    """
        else:
            query += """
            FROM location l
            """
        if review_conditions != "":
            query += """
                        JOIN
                    review r ON l.id = r.place_id
                    """
        if country_name != "":
            query += """WHERE c.id = (select id from country where name = %s) 
            """
            args.extend([country_name])
        else:
            query += """
                    WHERE
                    lat between @lat_min and @lat_max and lng between @lng_min and @lng_max 
                    and (((ACOS(SIN(@lat * PI() / 180) * SIN(lat * PI() / 180) + COS(@lat * PI() / 180) * COS(lat * PI() / 180) * COS((@lng - lng) * PI() / 180)) * 180 / PI()) * 60 * 1.1515) * 1.609344) < @R
                    """
        if fclass not in ["", "All"]:
            if fcode not in ["", "Please choose category first!", "All"]:
                query += """AND l.feature_code = (SELECT 
                                id
                            FROM
                                feature_code
                            WHERE
                                name =%s)
                        """
                args.extend([fcode])
            else:
                query += """AND feature_code IN (SELECT 
                                fcode.id
                            FROM
                                feature_code fcode
                                    JOIN
                                feature_class fclass ON fcode.feature_class = fclass.id
                            WHERE
                                fclass.name = %s)
                """
                args.extend([fclass])

        query += review_conditions
        args.extend(review_args)
        query += """
                AND l.id > %s
                ORDER BY l.id limit %s
                ;
                """
        args.extend([last_id, limit_size])
        return self.execute_single_query(query, args)

    def highest_rated_locations(self):
        query = """
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
                    LIMIT 20) temp ON l.id = temp.place_id;
            """
        return self.execute_single_query(query)

    def global_statistics(self):
        query = """
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
                """
        return self.execute_single_query(query)

    def trip_season_statistics_per_location(self, location_id):
        query = """
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
                    place_id = %s
                GROUP BY trip_season;
            """
        return self.execute_single_query(query, [location_id])

    def trip_type_statistics_per_location(self, location_id):
        query = """
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
                    place_id = %s
                GROUP BY trip_type;
            """
        return self.execute_single_query(query, [location_id])

    def execute_single_query(self, query, args=[], is_expecting_result=True):
        if args:
            self.cursor.execute(query, tuple(args))
        else:
            self.cursor.execute(query)
        # print(self.cursor.statement)
        if is_expecting_result:
            return self.cursor.fetchall()
        return []

    def execute_multiple_queries(self, query):
        # print(query)  
        for stmt in query.split(';'):
            if stmt.strip():
                self.cursor.execute(stmt)


    # Next five functions just fetch all data from number of small tables
    def fetchCountries(self):
        self.cursor.execute("SELECT * FROM country;")
        return self.cursor.fetchall()

    def fetchFeatureClasses(self):
        self.cursor.execute("SELECT * FROM feature_class;")
        return self.cursor.fetchall()

    # Function gets name of feature class, and uses it to fetch relevant feature codes from
    # table "feature_code". First we run query to get id of entered feature class name, and then
    # run query to get relevant data from "feature_code" table.
    def fetchFeatureCodes(self, feature_class_name):
        self.cursor.execute(
            "SELECT id FROM feature_class WHERE name = %s;", tuple([feature_class_name]))
        feature_class_id = self.cursor.fetchall()[0][0]
        self.cursor.execute(
            "SELECT * FROM feature_code WHERE feature_class = %s;", tuple([feature_class_id]))
        return self.cursor.fetchall()

    def fetchTripSeasons(self):
        self.cursor.execute("SELECT * FROM trip_season;")
        return self.cursor.fetchall()

    def fetchTripTypes(self):
        self.cursor.execute("SELECT * FROM trip_type;")
        return self.cursor.fetchall()

    # Next function takes location_id and user_id as arguments, which are set to "-1" by default.
    # In general current function builds SQL query depending on which of these two arguments where
    # entered by caller.
    # def fetchReviews(self, limit=50, location_id=-1, user_id=-1):
    #     command = "SELECT * FROM review WHERE "

    #     if (location_id == -1 and user_id == -1):
    #         raise Exception("Have to provide user id or location id")
    #     elif (location_id != -1 and user_id == -1):
    #         command += f"place_id = {location_id} LIMIT {limit}"
    #     elif (location_id == -1 and user_id != -1):
    #         command += f"user_id = {user_id} LIMIT {limit}"
    #     else:
    #         raise Exception("Cannot provide specific user and specific location for the same time")
    #         # command += f"user_id = {user_id} AND place_id = {location_id} LIMIT {limit}"

    #     command = f"""SELECT l.user_id, l.place_id, l.rating, l.trip_type, r.name as trip_season, l.anonymous_review, l.review 
    #                             FROM ({command}) as l INNER JOIN trip_season as r ON l.trip_season = r.id"""
    #     command = f"""SELECT l.user_id, l.place_id, l.rating, r.name as trip_type, l.trip_season, l.anonymous_review, l.review
    #                             FROM ({command}) as l INNER JOIN trip_type as r ON l.trip_type = r.id"""
    #     if user_id == -1:
    #         command = f""" SELECT r.full_name, FLOOR(YEAR(CURRENT_TIMESTAMP) - YEAR(r.date_of_birth)),
    #                                 l.place_id, l.rating, l.trip_type, l.trip_season, l.anonymous_review, l.review 
    #                                 FROM ({command}) as l INNER JOIN user as r ON l.user_id = r.id"""
    #     if location_id == -1:
    #         command = f""" SELECT r.name as place_name, l.place_id, l.rating, l.trip_type, l.trip_season, l.anonymous_review, l.review
    #                                 FROM ({command}) as l INNER JOIN location as r ON l.place_id = r.id"""

    #     command = f"{command};"
    #     self.cursor.execute(command)
    #     return self.cursor.fetchall()

    # Current function returns list of all reviews, that were made on provided location. Table "review" itself returns us
    # id's of different data (like trip season, trip type, or user id). So we to make JOIN with relevant 3 tables, to fetch
    # names of that data (trip type name, season, name of user and age of user).
    def fetchLocationReviews(self, location_id, limit=-1):
        args = [location_id]
        command = "SELECT * FROM review WHERE place_id = %s "
        if limit > 0:
            args.append(limit)
            command += "LIMIT %s "
        command = f"""SELECT l.user_id, l.place_id, l.rating, l.trip_type, r.name as trip_season, l.anonymous_review, l.review 
                                FROM ({command}) as l INNER JOIN trip_season as r ON l.trip_season = r.id"""
        command = f"""SELECT l.user_id, l.place_id, l.rating, r.name as trip_type, l.trip_season, l.anonymous_review, l.review
                                FROM ({command}) as l INNER JOIN trip_type as r ON l.trip_type = r.id"""
        command = f""" SELECT r.full_name, FLOOR(YEAR(CURRENT_TIMESTAMP) - YEAR(r.date_of_birth)),
                                l.place_id, l.rating, l.trip_type, l.trip_season, l.anonymous_review, l.review 
                                FROM ({command}) as l INNER JOIN user as r ON l.user_id = r.id"""
        command = f"{command};"
        return self.execute_single_query(command, args=args)

    # Current function returns list of all reviews that were made by logged in user. Likewise preceding function, here we have
    # to swap between id's of different data, and actual textual names of that data. Also, unlike preceding function, we make
    # JOIN with "location" table, to provide textual names of locations of reviews.
    def fetchUserReviews(self, user_id, limit=-1):
        args = [user_id]
        command = "SELECT * FROM review WHERE user_id = %s "
        if limit > 0:
            args.append(limit)
            command += "LIMIT %s "
        command = f"""SELECT l.user_id, l.place_id, l.rating, l.trip_type, r.name as trip_season, l.anonymous_review, l.review 
                                FROM ({command}) as l INNER JOIN trip_season as r ON l.trip_season = r.id"""
        command = f"""SELECT l.user_id, l.place_id, l.rating, r.name as trip_type, l.trip_season, l.anonymous_review, l.review
                                FROM ({command}) as l INNER JOIN trip_type as r ON l.trip_type = r.id"""
        command = f""" SELECT r.name as place_name, l.place_id, l.rating, l.trip_type, l.trip_season, l.anonymous_review, l.review
                                FROM ({command}) as l INNER JOIN location as r ON l.place_id = r.id"""
        command = f"{command};"
        return self.execute_single_query(command, args=args)


    # Next bunch of functions made to administrate all things related to authentication. 
    # Current function takes user credentials as arguments, and makes SELECT query to check whether there
    # exist user with those credentials
    def checkUserExistence(self, email, password):
        args = [email, password]
        command = "SELECT * FROM user WHERE email = %s AND password = %s;"

        return self.execute_single_query(command, args=args)

    # Current function takes email as argument, and makes SELECT query to check whether exist in system 
    # user with this email. User mainly to check whether user can register into system with given email.
    def checkEmailExistence(self, email):
        args = [email]
        command = "SELECT COUNT(*) FROM user WHERE email = %s;"

        return self.execute_single_query(command, args=args)[0][0]

    # Current function enters new user to "user" table.
    def enterNewUser(self, full_name, email, password, birth_date):
        args = [full_name, email, password, birth_date]
        command = "INSERT INTO user(full_name, email, password, date_of_birth) VALUES(%s, %s, %s, %s);"

        self.cursor.execute(command, tuple(args))


    # Current function counts number of reviews that were made by specific user, on specific
    # location and season. Mainly used to check whether user can add new review on some location,
    # and to forbid adding multiple reviews on one trip. Also in this (and next) functions, we take
    # as argument names of possible search attributes (like trip season, or trip type). But to add
    # new line to table we have to provide id of such things, so we make sub-commands, that we 
    # eventually ember in main queries.
    def countSpecificUserReviews(self, user_id, place_id, trip_season):
        args = [user_id, place_id, trip_season]
        trip_season_command = "SELECT id FROM trip_season WHERE name=%s"
        command = "SELECT COUNT(*) FROM review WHERE user_id = %s AND place_id = %s AND"
        command += f" trip_season = ({trip_season_command});"

        return self.execute_single_query(command, args=args)[0][0]

    def deleteUserReview(self, user_id, place_id, trip_season):
        args = [user_id, place_id, trip_season]
        trip_season_command = "SELECT id FROM trip_season WHERE name=%s"
        command = "DELETE FROM review WHERE user_id = %s AND place_id = %s AND"
        command += f" trip_season = ({trip_season_command});"

        self.cursor.execute(command, tuple(args))

    def addUserReview(self, user_id, place_id, rating, trip_type, trip_season, anon_rew, text_rew):
        args = [user_id, place_id, rating, trip_type, trip_season, anon_rew, text_rew]
        trip_season_command = "SELECT id FROM trip_season WHERE name=%s"
        trip_type_command = "SELECT id FROM trip_type WHERE name=%s"

        command = "INSERT INTO review VALUES (%s,  %s, %s,"
        command += f" ({trip_type_command}), ({trip_season_command}),"
        command += " %s, %s);"

        self.cursor.execute(command, tuple(args))
