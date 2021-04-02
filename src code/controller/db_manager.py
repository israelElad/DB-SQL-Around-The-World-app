from database.database import Database
from controller.utils import generateErrorMessage

class DataBaseManager:

    def __init__(self, database):
        self.database = database
        self.user_logged_in = False
        self.user_data = None
        self.last_locations_id = 0
        self.last_locations_query_data = None
        self.last_location_reviews_id = 0
        self.last_review_data = None



    # Next six functions only call for relevant functions from model layer. Also it slightly 
    # modifies returned data (deleting unrelevant parts of it), and catches exceptions, from
    # witch it generated error messages, that (ideally - all of them) we will show to user.
    # All functions in this object return two values - 1) value that user wants to receive;
    # 2) string that contains some error message, that gui will show to user.
    def fetchCountries(self):
        try:
            countries = self.database.fetchCountries()
            result = [i[1] for i in countries]
            return result, None
        except Exception as err:
                return None, generateErrorMessage(err.args[0])

    def fetchFeatureClasses(self):
        try:
            classes = self.database.fetchFeatureClasses()
            result = [i[1] for i in classes]
            return result, None
        except Exception as err:
                return None, generateErrorMessage(err.args[0])

    def fetchFeatureCodes(self, feature_class_name):
        try:
            codes = self.database.fetchFeatureCodes(feature_class_name)
            result = [i[2] for i in codes]
            return result, None
        except Exception as err:
                return None, generateErrorMessage(err.args[0])

    def fetchTripSeasons(self):
        try:
            seasons = self.database.fetchTripSeasons()
            result = [i[1] for i in seasons]
            return result, None
        except Exception as err:
                return None, generateErrorMessage(err.args[0])

    def fetchTripTypes(self):
        try:
            types = self.database.fetchTripTypes()
            result = [i[1] for i in types]
            return result, None
        except Exception as err:
                return None, generateErrorMessage(err.args[0])


    def fetchLocationReviews(self, location_id, limit=-1):
        try:
            result = self.database.fetchLocationReviews(location_id, limit=limit)
            return result, None
        except Exception as err:
                return None, generateErrorMessage(err.args[0])


    # Current function firstly checks whether user is already inside of system. In this case, function returns
    # negative result, with relevant error message.Then runs function of model layer, that checks whether exist
    # user in system with entered credentials. In positive outcome, function returns - "true".
    def logInUser(self, email, password):
        try:
            if self.user_logged_in:
                return False, "User already logged in"

            query_result = self.database.checkUserExistence(email, password)
            if(len(query_result) > 0):
                self.user_data = query_result[0]
                self.user_logged_in = True
                return True, None
            else:
                return False, "Such user not exist"
        except Exception as err:
                return False, generateErrorMessage(err.args[0])


    def logOutUser(self):
        if self.user_logged_in:
            self.user_logged_in = False
            return True, None
        else:
            return False, "User was not logged in"


    def _validateUserEnryData(self, email):
        query_result = self.database.checkEmailExistence(email)
        if query_result > 0:
            return True
        else:
            return False

    # First function checks whether in system already exists user with entered email. In such case function
    # returns - "false". Otherwise we enter user data to system, and make log in of newly created user.
    def registerUser(self, full_name, email, password, birth_date):
        try:
            if self._validateUserEnryData(email):
                return False, "Such email already taken"
            else:
                self.database.enterNewUser(full_name, email, password, birth_date)
                self.logInUser(email, password)
                return True, None
        except Exception as err:
                return False, generateErrorMessage(err.args[0])

    
    def isUserLoggedIn(self):
        return self.user_logged_in
    
    # Current function returns all reviews that where written by user, firstly checking whether client
    # made log in into system.
    def getCurrentUserReviews(self, limit=-1):
        try:
            if self.user_logged_in:
                result = self.database.fetchUserReviews(self.user_data[0], limit=limit)
                return result, None
            else:
                return None, "You had not logged in"
        except Exception as err:
                return None, generateErrorMessage(err.args[0])

    # Current function checks whether user made review on entered trip. This function is private and used
    # in next function.
    def _isReviewBelongsToUser(self, place_id, trip_season):
        if self.isUserLoggedIn():
            if self.database.countSpecificUserReviews(self.user_data[0], place_id, trip_season) > 0:
                return True
            else:
                return False
        else:
            return False
    
    # Current function takes data of review that user wants to delete. Firstly it checks whether user
    # is logged in, and whether user have review that matches entered trip data. Then it runs function
    # of model layer.
    def deleteCurrentUserReview(self, place_id, trip_season):
        try:
            if self.isUserLoggedIn() and self._isReviewBelongsToUser(place_id, trip_season):
                self.database.deleteUserReview(self.user_data[0], place_id, trip_season)
                return True, None
            elif not self.isUserLoggedIn():
                return False, "You had not logged in"
            else:
                return False, "Review was not written by user"
        except Exception as err:
                return False, generateErrorMessage(err.args[0])
    
    # Current function takes all data, that concerns review that will be created. Firslty it checks whether
    # user is logged in, and it checks that entered values are valid review values. Then, if data passes
    # all checks, it runs relevant function from model layer.
    def addCurrentUserReview(self, place_id, rating, trip_type, trip_season, anon_rew, text_rew):
        try:
            if self.isUserLoggedIn() and (rating <= 10 and rating >= 1) and ((type(text_rew) == type('')) and (len(text_rew) < 300)):
                self.database.addUserReview(self.user_data[0], place_id, rating, trip_type, trip_season, anon_rew, text_rew)
                return True, None
            elif not self.isUserLoggedIn():
                return False, "You had not logged in"
            elif not (rating <= 10 and rating >= 1):
                return False, "Rating must be value between 1 and 10"
            elif not ((type(text_rew) == type('')) and (len(text_rew) < 300)):
                return False, "Text review must be less that 300 characters"
        except Exception as err:
                return False, generateErrorMessage(err.args[0])
    
    
    # def isLocationReviewedByUser(self, place_id):
    #     try:
    #         if self.isUserLoggedIn():
    #             self.cursor.execute(f"SELECT COUNT(*) FROM review WHERE user_id = {self.user_data[0]} AND place_id = {place_id};")
    #             result_list = self.cursor.fetchall()
    #             if result_list[0][0] > 0:
    #                 return True, None
    #             else:
    #                 return False, "User not viewed current location"
    #         else:
    #             return False, "You had not logged in"
    #     except Exception as err:
    #             return False, generateErrorMessage(err.args[0])



    # Basically, this function wraps function from model layer, that performs locations search operation. Also it meant to 
    # save data of last made search attributes, and id of last received location data. It made for pagination functionality.
    def searchLocations(self, country_name, radius, lat, lng, fclass, fcode, trip_type, trip_season, limit_size):
        # try:
        result = self.database.find_locations(country_name, radius, lat, lng, fclass, fcode, trip_type, trip_season, limit_size)
        if len(result) == 0:
            return [], None

        self.last_locations_query_data = [country_name, radius, lat, lng, fclass, fcode, trip_type, trip_season]
        self.last_locations_id = result[len(result)-1][0]
        return result, None
        # except Exception as err:
        #         return None, generateErrorMessage(err.args[0])


    # Current function is similar to preceding one, with only one change - it takes search query data not from gui layer,
    # but from internal list, that conatins search attributes data from last performed search.
    def proceedLastSearchQuery(self, limit_size):
        if self.last_locations_query_data == None:
            return None, "You haven't searched anything yet"
        
        # try:
        result = self.database.find_locations(self.last_locations_query_data[0], self.last_locations_query_data[1], self.last_locations_query_data[2], 
                        self.last_locations_query_data[3], self.last_locations_query_data[4], self.last_locations_query_data[5], 
                        self.last_locations_query_data[6], self.last_locations_query_data[7], limit_size, last_id=self.last_locations_id)
        if len(result) == 0:
            return [], "No more results"
        self.last_locations_id = result[len(result)-1][0]
        return result, None
        # except Exception as err:
        #         return False, generateErrorMessage(err.args[0])


    def getGlobalStatistics(self):
        try:
            result = self.database.global_statistics()
            return result, None
        except Exception as err:
            return False, generateErrorMessage(err.args[0])

    def getHighestRatedLocations(self):
        try:
            result = self.database.highest_rated_locations()
            return result, None
        except Exception as err:
            return False, generateErrorMessage(err.args[0])

    def getLocationSeasonStatistics(self, location_id):
        try:
            result = self.database.trip_season_statistics_per_location(location_id)
            return result, None
        except Exception as err:
            return False, generateErrorMessage(err.args[0])

    def getLocationTripTypeStatistics(self, location_id):
        try:
            result = self.database.trip_type_statistics_per_location(location_id)
            return result, None
        except Exception as err:
            return False, generateErrorMessage(err.args[0])

