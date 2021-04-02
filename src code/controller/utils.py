def generateErrorMessage(error_number):
    if error_number == 1062:
        return "You already wrote review for such trip"
    if error_number == 1048:
        return "Incorrect query arguments"
    if error_number == 1045:
        return "Access denied for current client credentials"
    if error_number == 2013:
        return "Lost connection with server"
    if error_number == 2002:
        return "Cannot conect with server"
    if error_number == 2008 or error_number == 1114:
        return "Server ran out of memory"
    if error_number == 1292:
        return "User entered invalid data"
    else:
        return f"Raised Mysql error:{error_number}" 